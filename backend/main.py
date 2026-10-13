import os
import uuid
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()  # load .env before anything reads os.environ

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse

import db
import geocode
import emailer
from classifier import classify_image, CATEGORIES

BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
FRONTEND_DIR = BASE_DIR.parent / "frontend"

CONFIDENCE_THRESHOLD = float(os.environ.get("CLASSIFIER_CONFIDENCE_THRESHOLD", 0.45))

app = FastAPI(title="Civic Issue Reporter API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # fine for a local student project; tighten for real deployment
    allow_methods=["*"],
    allow_headers=["*"],
)

db.init_db()

app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")


@app.get("/")
def root():
    # The Render dashboard (and anyone sharing the bare domain) links straight
    # to this URL, so it should open the actual app, not a JSON status blob.
    return RedirectResponse(url="/app/report.html")


@app.get("/api-info")
def api_info():
    # The old root response, kept at its own path for anyone who wants a
    # quick machine-readable pointer to the other URLs (e.g. curl scripts).
    return {
        "service": "civic-issue-reporter",
        "docs": "/docs",
        "report_page": "/app/report.html",
        "dashboard": "/app/dashboard.html",
    }


@app.get("/app/{path:path}")
def serve_frontend(path: str):
    file_path = FRONTEND_DIR / path
    if not file_path.exists():
        raise HTTPException(404, "Not found")
    return FileResponse(file_path)


@app.post("/classify")
async def classify_only(image: UploadFile = File(...)):
    """
    Step 1 of the two-step flow: classify the photo and show the player
    what the system thinks it is, WITHOUT saving or emailing yet. The
    frontend shows this for human confirmation before the real submit
    (see README -> "why two steps").
    """
    image_bytes = await image.read()
    try:
        result = classify_image(image_bytes)
    except ValueError as e:
        raise HTTPException(400, str(e))

    return {
        "category": result.category,
        "confidence": result.confidence,
        "needs_review": result.confidence < CONFIDENCE_THRESHOLD,
        "scores": result.scores,
        "categories": CATEGORIES,
    }


@app.post("/report")
async def create_report(
    image: UploadFile = File(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    category: str = Form(...),       # player-confirmed (or corrected) category
    confidence: float = Form(...),   # from the earlier /classify call
):
    if category not in CATEGORIES:
        raise HTTPException(400, f"category must be one of {CATEGORIES}")

    image_bytes = await image.read()
    ext = Path(image.filename or "photo.jpg").suffix or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    image_path = UPLOAD_DIR / filename
    image_path.write_bytes(image_bytes)

    address = geocode.reverse_geocode(latitude, longitude)

    needs_review = confidence < CONFIDENCE_THRESHOLD

    report_id_holder = {}

    def _save(email_sent, email_error):
        rid = db.create_report(
            image_path=f"/uploads/{filename}",
            latitude=latitude,
            longitude=longitude,
            address=address,
            category=category,
            confidence=confidence,
            needs_review=needs_review,
            email_sent=email_sent,
            email_error=email_error,
        )
        report_id_holder["id"] = rid
        return rid

    # Save first so we have a report ID to put in the email subject.
    report_id = _save(email_sent=False, email_error=None)

    sent, error = emailer.send_report_email(
        report_id=report_id,
        category=category,
        confidence=confidence,
        address=address,
        latitude=latitude,
        longitude=longitude,
        image_bytes=image_bytes,
        image_filename=filename,
    )

    with db.get_conn() as conn:
        conn.execute(
            "UPDATE reports SET email_sent = ?, email_error = ? WHERE id = ?",
            (int(sent), error, report_id),
        )

    return {
        "id": report_id,
        "category": category,
        "confidence": confidence,
        "address": address,
        "needs_review": needs_review,
        "email_sent": sent,
        "email_error": error,
    }


@app.get("/reports")
def get_reports(category: str | None = None, status: str | None = None):
    return db.list_reports(category=category, status=status)


@app.get("/reports/{report_id}")
def get_report(report_id: int):
    r = db.get_report(report_id)
    if not r:
        raise HTTPException(404, "Report not found")
    return r


@app.post("/reports/{report_id}/status")
def set_status(report_id: int, status: str = Form(...)):
    if not db.get_report(report_id):
        raise HTTPException(404, "Report not found")
    try:
        db.update_status(report_id, status)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return db.get_report(report_id)


@app.get("/stats")
def get_stats():
    return db.stats()
