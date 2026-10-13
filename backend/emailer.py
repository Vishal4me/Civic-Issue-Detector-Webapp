"""
Sends a report alert email with the photo attached, via the Resend API.

WHY RESEND INSTEAD OF GMAIL SMTP:
This project originally sent mail with smtplib over raw SMTP (port 465)
straight to Gmail. That works fine locally, but most free cloud hosts
(Render included) now block outbound traffic on SMTP ports 25/465/587 to
stop their platform being used for spam -- see Render's own changelog:
https://render.com/changelog/free-web-services-will-no-longer-allow-outbound-traffic-to-smtp-ports
So on a deployed free instance, smtplib fails with
"[Errno 101] Network is unreachable" even with correct credentials.

Resend sends mail over a normal HTTPS POST request (https://api.resend.com),
which no cloud host blocks, so it works identically locally and deployed.
It has a free tier (no card required) generous enough for a student project.

Configured through environment variables (see .env.example):
  RESEND_API_KEY  - API key from https://resend.com/api-keys
  EMAIL_FROM      - sender address shown on the email (defaults to Resend's
                    shared sandbox sender, see note below)
  EMAIL_TO        - who receives the alert; comma-separate for several

IMPORTANT sandbox limitation: until you verify your own domain on Resend
(https://resend.com/domains), the shared sender "onboarding@resend.dev" can
only deliver to the email address you signed up to Resend with. That's
exactly this project's situation -- EMAIL_TO is a single inbox you control
(nagarmitrasolution@gmail.com), so just sign up to Resend with that same
address and it works with zero extra setup. If you later add real,
verified department addresses to EMAIL_TO, you'll need to verify your own
domain on Resend first, and set EMAIL_FROM to an address on that domain.
"""
import base64
import os

import requests

RESEND_API_URL = "https://api.resend.com/emails"

CATEGORY_LABELS = {
    "pothole": "Pothole",
    "garbage": "Garbage / Waste Pile",
    "broken_streetlight": "Broken Streetlight",
    "water_leakage": "Water Leakage",
}


def send_report_email(report_id, category, confidence, address, latitude, longitude,
                       image_bytes, image_filename):
    api_key = os.environ.get("RESEND_API_KEY")
    from_addr = os.environ.get("EMAIL_FROM", "Streetline Alerts <onboarding@resend.dev>")
    to_addrs = [a.strip() for a in os.environ.get("EMAIL_TO", "").split(",") if a.strip()]

    if not api_key or not to_addrs:
        return False, "Email not configured (RESEND_API_KEY / EMAIL_TO missing in .env)"

    label = CATEGORY_LABELS.get(category, category)
    maps_link = f"https://www.google.com/maps?q={latitude},{longitude}"

    text_body = f"""A new civic issue has been reported.

Report ID:   {report_id}
Category:    {label}
Confidence:  {confidence * 100:.0f}%
Location:    {address}
Coordinates: {latitude}, {longitude}
Map link:    {maps_link}

Photo attached.

---
This is an automated alert from a student civic-issue-reporting project.
It is currently sent to a test inbox, not an official department address.
"""

    subtype = "jpeg" if image_filename.lower().endswith((".jpg", ".jpeg")) else "png"
    payload = {
        "from": from_addr,
        "to": to_addrs,
        "subject": f"[Civic Report #{report_id}] {label} reported",
        "text": text_body,
        "attachments": [
            {
                "filename": image_filename,
                "content": base64.b64encode(image_bytes).decode("ascii"),
                "content_type": f"image/{subtype}",
            }
        ],
    }

    try:
        resp = requests.post(
            RESEND_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=15,
        )
        if resp.status_code >= 400:
            # Resend returns a JSON body describing the problem (e.g. the
            # sandbox-sender-recipient-mismatch case documented above).
            try:
                detail = resp.json().get("message", resp.text)
            except ValueError:
                detail = resp.text
            return False, f"Resend API error {resp.status_code}: {detail}"
        return True, None
    except requests.RequestException as e:
        return False, str(e)
