"""
Issue classifier.

IMPORTANT, READ THIS FIRST:
This module ships a simple, explainable OpenCV heuristic baseline, not a
trained model. It exists so the whole pipeline (upload -> classify ->
geocode -> email -> dashboard) runs end-to-end out of the box with no
dataset, no GPU, and no internet access to a model hub.

For your actual project submission, replace `classify_image()` with a real
trained CNN (see README.md "Swapping in a real model"). The function
signature below is the only contract the rest of the app depends on, so you
can swap the body for a PyTorch/TensorFlow model call without touching
anything else:

    classify_image(image_bytes) -> ClassificationResult

Heuristic approach (documented so you can explain it in a viva):
- Pothole: dark, roughly-round blobs against a grey/brown road-colored
  background, found via adaptive thresholding + contour shape analysis.
- Garbage: clusters of high color-variance, irregular-shaped contours
  (garbage piles are visually "busy" / high local color entropy).
- Broken streetlight: looked for by brightness pattern (very dark image
  with no bright localized spot, where a working streetlight at night
  would usually create one) -- weak signal by design, flagged low-confidence.
- Water leakage: specular highlight / reflective patch detection (wet
  surfaces reflect more light than dry ones, creating bright elongated
  patches with low color saturation).

None of these are reliable classifiers on their own -- they are intentionally
simple so every decision can be explained, and so confidence is capped low
enough that the human-confirmation step (see main.py) catches most mistakes.
"""
from dataclasses import dataclass
import cv2
import numpy as np

CATEGORIES = ["pothole", "garbage", "broken_streetlight", "water_leakage"]


@dataclass
class ClassificationResult:
    category: str
    confidence: float  # 0.0 - 1.0
    scores: dict        # per-category raw scores, for debugging/dashboarding


def _decode(image_bytes) -> np.ndarray:
    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode image. Is it a valid JPG/PNG?")
    # Normalize size so thresholds behave consistently regardless of
    # the phone's camera resolution.
    h, w = img.shape[:2]
    scale = 800 / max(h, w)
    if scale < 1:
        img = cv2.resize(img, (int(w * scale), int(h * scale)))
    return img


def _pothole_score(img, gray) -> float:
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)
    thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 10
    )
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    img_area = img.shape[0] * img.shape[1]
    score = 0.0
    for c in contours:
        area = cv2.contourArea(c)
        if area < img_area * 0.01 or area > img_area * 0.4:
            continue
        perimeter = cv2.arcLength(c, True)
        if perimeter == 0:
            continue
        circularity = 4 * np.pi * area / (perimeter ** 2)
        # Potholes read as moderately-round dark blobs, not perfect circles.
        if 0.3 < circularity < 0.95:
            score = max(score, circularity * min(area / (img_area * 0.15), 1.0))
    return float(score)


def _garbage_score(img, gray) -> float:
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # Garbage piles tend to have high local variance in hue/saturation --
    # lots of different colored objects jumbled together.
    h_std = np.std(hsv[:, :, 0].astype(np.float32))
    s_std = np.std(hsv[:, :, 1].astype(np.float32))
    edges = cv2.Canny(gray, 60, 160)
    edge_density = np.count_nonzero(edges) / edges.size
    # Normalize into roughly 0-1 ranges empirically.
    score = min(1.0, (h_std / 60.0) * 0.4 + (s_std / 90.0) * 0.3 + (edge_density * 6) * 0.3)
    return float(score)


def _streetlight_score(img, gray) -> float:
    mean_brightness = float(np.mean(gray))
    # Looks for a scene that is dark overall (suggesting night) and checks
    # whether a plausible light fixture (small bright blob) is visible.
    if mean_brightness > 110:
        return 0.0  # daytime photo, not useful for this check
    bright_mask = gray > 200
    bright_fraction = np.count_nonzero(bright_mask) / gray.size
    # Dark scene + *no* meaningfully bright spot => plausible broken light.
    # Dark scene + a bright spot => light is probably working (not this issue).
    if bright_fraction < 0.001:
        darkness = 1.0 - (mean_brightness / 110.0)
        return float(min(1.0, darkness * 0.6))  # capped: weak signal
    return 0.0


def _water_leakage_score(img, gray) -> float:
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    v = hsv[:, :, 2].astype(np.float32)
    s = hsv[:, :, 1].astype(np.float32)
    # Wet patches: locally bright (specular) but low saturation (water
    # reflects sky/light rather than carrying strong color itself).
    wet_mask = (v > 150) & (s < 60)
    wet_fraction = np.count_nonzero(wet_mask) / wet_mask.size
    return float(min(1.0, wet_fraction * 4))


def classify_image(image_bytes) -> ClassificationResult:
    img = _decode(image_bytes)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    scores = {
        "pothole": _pothole_score(img, gray),
        "garbage": _garbage_score(img, gray),
        "broken_streetlight": _streetlight_score(img, gray),
        "water_leakage": _water_leakage_score(img, gray),
    }

    best_category = max(scores, key=scores.get)
    best_score = scores[best_category]

    # Squash into a confidence-ish number; heuristics are noisy, so keep the
    # ceiling well under 1.0 to make "needs review" the common honest outcome.
    confidence = round(min(0.85, best_score), 3)

    return ClassificationResult(category=best_category, confidence=confidence, scores=scores)
