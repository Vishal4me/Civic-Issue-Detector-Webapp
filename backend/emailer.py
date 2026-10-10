"""
Sends a report alert email with the photo attached, via Gmail SMTP.

Configured through environment variables (see .env.example):
  EMAIL_USER      - the Gmail account that sends the mail
  EMAIL_PASSWORD  - a Gmail "App Password" (not the normal account password)
  EMAIL_TO        - who receives the alert; comma-separate for several

For now EMAIL_TO defaults to the project owner's own inbox rather than a
real government address, per instructions. Swap it for verified department
emails later -- see README.md.
"""
import os
import smtplib
from email.message import EmailMessage

CATEGORY_LABELS = {
    "pothole": "Pothole",
    "garbage": "Garbage / Waste Pile",
    "broken_streetlight": "Broken Streetlight",
    "water_leakage": "Water Leakage",
}


def send_report_email(report_id, category, confidence, address, latitude, longitude,
                       image_bytes, image_filename):
    user = os.environ.get("EMAIL_USER")
    password = os.environ.get("EMAIL_PASSWORD")
    to_addrs = [a.strip() for a in os.environ.get("EMAIL_TO", "").split(",") if a.strip()]

    if not user or not password or not to_addrs:
        return False, "Email not configured (EMAIL_USER / EMAIL_PASSWORD / EMAIL_TO missing in .env)"

    label = CATEGORY_LABELS.get(category, category)
    maps_link = f"https://www.google.com/maps?q={latitude},{longitude}"

    msg = EmailMessage()
    msg["Subject"] = f"[Civic Report #{report_id}] {label} reported"
    msg["From"] = user
    msg["To"] = ", ".join(to_addrs)
    msg.set_content(
        f"""A new civic issue has been reported.

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
    )

    subtype = "jpeg" if image_filename.lower().endswith((".jpg", ".jpeg")) else "png"
    msg.add_attachment(image_bytes, maintype="image", subtype=subtype, filename=image_filename)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as smtp:
            smtp.login(user, password)
            smtp.send_message(msg)
        return True, None
    except Exception as e:
        return False, str(e)
