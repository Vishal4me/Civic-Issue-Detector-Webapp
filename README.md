# Civic Issue Reporter

Take a photo of a street problem (pothole, garbage, broken streetlight, water
leakage) → the app detects the issue type and your location → it emails an
alert with the photo → everyone can track progress on a live dashboard.

This is a working end-to-end prototype, not a toy mockup: every report really
gets classified, really gets geocoded, and really gets emailed (once you add
credentials). The one deliberate placeholder is the **classifier**, and the
**email recipient** — see below for why, and how to upgrade both.

## Quick start

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# edit .env — see "Email setup" below
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Then open:
- **Report a photo:** http://localhost:8000/app/report.html
- **Dashboard:** http://localhost:8000/app/dashboard.html
- **API docs (auto-generated):** http://localhost:8000/docs

Open `report.html` on your **phone** (same Wi-Fi, use your laptop's local IP
instead of `localhost`) to use the real camera and real GPS — desktop
browsers can fake both, but it's much more convincing on a phone.

## Why the recipient email is yours, for now

As instructed, `EMAIL_TO` in `.env.example` defaults to `vc810620@gmail.com`
instead of a government address. The blueprint conversation that led to this
project covers why: verified departmental emails for Lucknow Nagar Nigam
were never confirmed publicly, so routing to a real address would silently
fail. Swap `EMAIL_TO` for real, verified addresses once you have them — the
code already supports comma-separating several recipients, and `emailer.py`
is the only file that would need touching to add per-category routing
(pothole → PWD, garbage → sanitation, etc.) later.

## Email setup (Gmail)

1. Turn on 2-Step Verification on the sending Gmail account.
2. Create an App Password: https://myaccount.google.com/apppasswords
3. In `.env`, set:
   ```
   EMAIL_USER=your_sending_gmail@gmail.com
   EMAIL_PASSWORD=the_16_character_app_password
   EMAIL_TO=vc810620@gmail.com
   ```
4. Restart the server. If email fails, the report is still saved — check the
   `email_error` field in the API response or the `reports` table.

## How the pipeline works

1. **Capture** (`report.html`) — camera or file picker, plus
   `navigator.geolocation` for GPS coordinates.
2. **Classify** (`POST /classify`) — runs the photo through `classifier.py`
   and shows the guessed category to the player **before** anything is
   saved, so they can confirm or correct it. Low-confidence guesses are
   flagged "needs review" instead of trusted blindly.
3. **Submit** (`POST /report`) — saves the photo, reverse-geocodes the GPS
   coordinates via OpenStreetMap Nominatim (`geocode.py`), stores the report
   in SQLite (`db.py`), and sends the alert email (`emailer.py`).
4. **Dashboard** (`dashboard.html`) — pulls `/reports` and `/stats`, plots
   every report on a Leaflet/OpenStreetMap map, and lets you change a
   report's status (Reported → Acknowledged → In Progress → Resolved) to
   simulate the authority side updating progress.

## The classifier is a heuristic baseline — read this before your viva

`classifier.py` does **not** use a trained model. It uses plain OpenCV rules
(contour shape for potholes, color/edge variance for garbage, brightness
patterns for streetlights, specular-highlight detection for water) so the
whole pipeline runs with no dataset, no GPU, and no internet access to a
model hub.

This is an honest, explainable baseline — not a shortcut dressed up as one.
Confidence is deliberately capped low so the human-confirmation step catches
most of its mistakes, matching the "confidence thresholding" approach from
the project design discussion.

**For your actual submission**, replace it with a trained CNN. The swap is
one function:

```python
# classifier.py
def classify_image(image_bytes) -> ClassificationResult:
    ...
```

Nothing else in the app needs to change as long as this function still
returns a `ClassificationResult(category, confidence, scores)`. To train a
real model:

1. Get labeled images per category (Kaggle has pothole and garbage datasets;
   you'll likely need to collect/label your own streetlight and
   water-leakage examples — a few hundred per class is enough for a
   fine-tuned pretrained backbone).
2. Fine-tune a small CNN (ResNet18/EfficientNet-B0 via `torchvision`, or
   YOLOv8-cls) on the four categories plus a "none of these" class.
3. Export it (e.g., ONNX or a `.pt` file) and load it once at startup inside
   `classifier.py`, replacing the OpenCV heuristics with
   `model(image_tensor)`.

## Project structure

```
civic-issue-detector/
├── backend/
│   ├── main.py          # FastAPI app, all routes
│   ├── classifier.py    # heuristic baseline — swap for a trained model
│   ├── geocode.py        # Nominatim reverse geocoding
│   ├── emailer.py        # Gmail SMTP alert emails
│   ├── db.py              # SQLite storage
│   ├── requirements.txt
│   ├── .env.example
│   └── uploads/           # saved report photos (gitignored in practice)
└── frontend/
    ├── report.html        # camera + geolocation + confirm + submit
    └── dashboard.html      # map + stats + status tracking
```

## API reference

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/classify` | Classify a photo without saving it |
| POST | `/report` | Save a confirmed report, geocode it, email it |
| GET | `/reports` | List all reports (filter with `?category=` / `?status=`) |
| GET | `/reports/{id}` | Get one report |
| POST | `/reports/{id}/status` | Update a report's status |
| GET | `/stats` | Totals, resolution rate, counts by category/status |

## Known limitations (be upfront about these in your report)

- **Classifier accuracy** is low by design (see above) — it's a baseline to
  demonstrate the pipeline, not a production detector.
- **No deduplication yet** — two people photographing the same pothole
  create two reports. A location+category proximity check (e.g., reports
  within ~30m of each other) would be the natural next addition.
- **No fake-photo protection** — nothing stops someone uploading an old or
  unrelated photo. A production version would force live camera capture
  only (already partly true here — camera mode doesn't use the gallery) and
  add a per-user trust score over time.
- **Status updates are manual** — there's no real integration with a
  municipal system, so "Resolved" means someone with dashboard access
  marked it that way, not that the pothole was actually fixed.

These are exactly the "realistic challenges" worth a paragraph each in your
project report's limitations/future-work section.
