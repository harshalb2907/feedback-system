# backend/email_service.py
# Uses port 587 + STARTTLS — works on Render (port 465 is blocked on most cloud servers)

import smtplib
import traceback
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr, formatdate, make_msgid
import os
from dotenv import load_dotenv

load_dotenv()

SENDER_EMAIL        = os.getenv("SENDER_EMAIL",        "").strip()
SENDER_APP_PASSWORD = os.getenv("SENDER_APP_PASSWORD", "").strip()
RECEIVER_EMAIL      = os.getenv("RECEIVER_EMAIL",      "").strip()


def send_complaint_email(
    customer_name: str,
    service:       str,
    rating:        int,
    message:       str,
) -> bool:

    # ── Validate env vars ────────────────────────────────────────
    if not SENDER_EMAIL:
        print("[EMAIL] ❌ SENDER_EMAIL is not set"); return False
    if not SENDER_APP_PASSWORD:
        print("[EMAIL] ❌ SENDER_APP_PASSWORD is not set"); return False
    if not RECEIVER_EMAIL:
        print("[EMAIL] ❌ RECEIVER_EMAIL is not set"); return False

    print(f"[EMAIL] From : {SENDER_EMAIL}")
    print(f"[EMAIL] To   : {RECEIVER_EMAIL}")
    print(f"[EMAIL] Port : 587 (STARTTLS)")

    try:
        # ── Build message ────────────────────────────────────────
        msg = MIMEMultipart("alternative")
        msg["Subject"]    = f"Brain Checker - Customer Feedback ({rating}/5 Stars)"
        msg["From"]       = formataddr(("Brain Checker Feedback", SENDER_EMAIL))
        msg["To"]         = formataddr(("Brain Checker Admin",    RECEIVER_EMAIL))
        msg["Date"]       = formatdate(localtime=True)
        msg["Message-ID"] = make_msgid(domain="gmail.com")

        stars_filled = "★" * rating
        stars_empty  = "☆" * (5 - rating)

        # Plain text
        plain = f"""Brain Checker — Customer Feedback
====================================
Customer Name  : {customer_name}
Service / Test : {service}
Rating         : {stars_filled}{stars_empty} ({rating}/5)

Feedback:
{message}

------------------------------------
Brain Checker AI Feedback System""".strip()

        # HTML
        html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#f4f7fb;font-family:Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="padding:32px 16px;">
<tr><td align="center">
<table width="560" cellpadding="0" cellspacing="0"
       style="background:#fff;border-radius:12px;border:1px solid #dde5ee;
              box-shadow:0 2px 12px rgba(0,0,0,0.06);overflow:hidden;">
  <tr>
    <td style="background:#00897b;padding:22px 28px;color:#fff;">
      <h2 style="margin:0;font-size:18px;">Brain Checker &mdash; Customer Feedback</h2>
      <p style="margin:5px 0 0;font-size:13px;opacity:0.85;">Automated alert</p>
    </td>
  </tr>
  <tr><td style="padding:28px;">
    <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;margin-bottom:22px;">
      <tr style="border-bottom:1px solid #f0f0f0;">
        <td style="padding:11px 0;font-weight:700;color:#546e7a;font-size:13px;width:140px;">Customer Name</td>
        <td style="padding:11px 0;color:#1a2332;font-size:14px;font-weight:600;">{customer_name}</td>
      </tr>
      <tr style="border-bottom:1px solid #f0f0f0;">
        <td style="padding:11px 0;font-weight:700;color:#546e7a;font-size:13px;">Service / Test</td>
        <td style="padding:11px 0;color:#1a2332;font-size:14px;">{service}</td>
      </tr>
      <tr>
        <td style="padding:11px 0;font-weight:700;color:#546e7a;font-size:13px;">Rating</td>
        <td style="padding:11px 0;font-size:20px;color:#ffb300;">
          {stars_filled}<span style="color:#ddd;">{stars_empty}</span>
          <span style="color:#888;font-size:13px;margin-left:8px;">({rating}/5)</span>
        </td>
      </tr>
    </table>
    <div style="background:#fff8f8;border-left:4px solid #e57373;border-radius:6px;padding:16px 20px;">
      <p style="margin:0 0 8px;font-weight:700;color:#c62828;font-size:12px;text-transform:uppercase;">Feedback</p>
      <p style="margin:0;line-height:1.8;color:#333;font-size:14px;">{message}</p>
    </div>
    <p style="margin:24px 0 0;color:#bbb;font-size:11px;text-align:center;">
      Brain Checker AI Feedback System
    </p>
  </td></tr>
</table>
</td></tr>
</table>
</body></html>"""

        msg.attach(MIMEText(plain, "plain", "utf-8"))
        msg.attach(MIMEText(html,  "html",  "utf-8"))

        # ── Send using port 587 STARTTLS (works on Render) ───────
        print("[EMAIL] Connecting to smtp.gmail.com port 587 ...")
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as server:
            server.ehlo()
            print("[EMAIL] Starting TLS ...")
            server.starttls()
            server.ehlo()
            print("[EMAIL] Logging in ...")
            server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
            print("[EMAIL] Sending ...")
            server.sendmail(SENDER_EMAIL, [RECEIVER_EMAIL], msg.as_string())

        print(f"[EMAIL] ✅ SUCCESS — email delivered to {RECEIVER_EMAIL}")
        return True

    except smtplib.SMTPAuthenticationError:
        print("[EMAIL] ❌ AUTHENTICATION FAILED")
        print("[EMAIL]    Your SENDER_APP_PASSWORD is wrong.")
        print("[EMAIL]    Steps to fix:")
        print("[EMAIL]    1. Go to https://myaccount.google.com/security")
        print("[EMAIL]    2. Enable 2-Step Verification")
        print("[EMAIL]    3. Search 'App Passwords' → generate one for Mail")
        print("[EMAIL]    4. Copy the 16-char code into Render env SENDER_APP_PASSWORD")
        return False

    except smtplib.SMTPRecipientsRefused as e:
        print(f"[EMAIL] ❌ RECEIVER EMAIL REFUSED: {e}")
        print(f"[EMAIL]    Check RECEIVER_EMAIL value in Render env vars")
        return False

    except ConnectionRefusedError:
        print("[EMAIL] ❌ CONNECTION REFUSED on port 587")
        print("[EMAIL]    Render may be blocking outbound SMTP")
        return False

    except OSError as e:
        print(f"[EMAIL] ❌ NETWORK ERROR: {e}")
        print("[EMAIL]    Render free tier may block SMTP. Try upgrading plan.")
        return False

    except Exception as e:
        print(f"[EMAIL] ❌ UNEXPECTED ERROR: {type(e).__name__}: {e}")
        print(traceback.format_exc())
        return False
