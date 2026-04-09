# backend/email_service.py
# Sends complaint emails — fixed to avoid Gmail spam filters

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
        print("[EMAIL] ERROR: SENDER_EMAIL not set in environment variables"); return False
    if not SENDER_APP_PASSWORD:
        print("[EMAIL] ERROR: SENDER_APP_PASSWORD not set in environment variables"); return False
    if not RECEIVER_EMAIL:
        print("[EMAIL] ERROR: RECEIVER_EMAIL not set in environment variables"); return False

    print(f"[EMAIL] Sending from {SENDER_EMAIL} to {RECEIVER_EMAIL}")

    try:
        msg = MIMEMultipart("alternative")

        # ── Headers that prevent going to spam ───────────────────
        msg["Subject"]    = f"Brain Checker - Customer Feedback ({rating}/5 Stars)"
        msg["From"]       = formataddr(("Brain Checker Feedback", SENDER_EMAIL))
        msg["To"]         = formataddr(("Brain Checker Admin",    RECEIVER_EMAIL))
        msg["Date"]       = formatdate(localtime=True)
        msg["Message-ID"] = make_msgid(domain="brainchecker.com")
        msg["X-Mailer"]   = "Brain Checker Feedback System"
        # This tells Gmail it is NOT spam
        msg["X-Priority"] = "1"
        msg["Importance"] = "High"

        stars_filled = "★" * rating
        stars_empty  = "☆" * (5 - rating)

        # ── Plain text ───────────────────────────────────────────
        plain = f"""Brain Checker — Customer Feedback Alert
========================================
Customer Name  : {customer_name}
Service / Test : {service}
Rating         : {stars_filled}{stars_empty} ({rating}/5)

Feedback / Complaint:
{message}

----------------------------------------
Sent by Brain Checker AI Feedback System
Do not reply to this email.
""".strip()

        # ── HTML ─────────────────────────────────────────────────
        html = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f4f7fb;font-family:Arial,Helvetica,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="padding:32px 16px;">
  <tr><td align="center">
    <table width="560" cellpadding="0" cellspacing="0"
           style="background:#ffffff;border-radius:12px;border:1px solid #dde5ee;
                  box-shadow:0 2px 12px rgba(0,0,0,0.06);overflow:hidden;">

      <!-- Header -->
      <tr>
        <td style="background:#00897b;padding:22px 28px;color:#fff;">
          <h2 style="margin:0;font-size:18px;font-weight:700;">
            Brain Checker &mdash; Customer Feedback
          </h2>
          <p style="margin:5px 0 0;font-size:13px;opacity:0.85;">
            Automated alert from the Feedback System
          </p>
        </td>
      </tr>

      <!-- Content -->
      <tr>
        <td style="padding:28px;">

          <!-- Info table -->
          <table width="100%" cellpadding="0" cellspacing="0"
                 style="border-collapse:collapse;margin-bottom:22px;">
            <tr style="border-bottom:1px solid #f0f0f0;">
              <td style="padding:11px 0;font-weight:700;color:#546e7a;font-size:13px;width:140px;">
                Customer Name
              </td>
              <td style="padding:11px 0;color:#1a2332;font-size:14px;font-weight:600;">
                {customer_name}
              </td>
            </tr>
            <tr style="border-bottom:1px solid #f0f0f0;">
              <td style="padding:11px 0;font-weight:700;color:#546e7a;font-size:13px;">
                Service / Test
              </td>
              <td style="padding:11px 0;color:#1a2332;font-size:14px;">
                {service}
              </td>
            </tr>
            <tr>
              <td style="padding:11px 0;font-weight:700;color:#546e7a;font-size:13px;">
                Rating
              </td>
              <td style="padding:11px 0;font-size:20px;color:#ffb300;">
                {stars_filled}<span style="color:#ddd;">{stars_empty}</span>
                <span style="color:#888;font-size:13px;margin-left:8px;">({rating} / 5)</span>
              </td>
            </tr>
          </table>

          <!-- Complaint message -->
          <div style="background:#fff8f8;border-left:4px solid #e57373;
                      border-radius:6px;padding:16px 20px;">
            <p style="margin:0 0 8px;font-weight:700;color:#c62828;font-size:12px;
                      text-transform:uppercase;letter-spacing:0.06em;">
              Feedback / Complaint
            </p>
            <p style="margin:0;line-height:1.8;color:#333;font-size:14px;">
              {message}
            </p>
          </div>

          <p style="margin:24px 0 0;color:#bbb;font-size:11px;text-align:center;">
            Brain Checker AI Feedback System &bull; Do not reply to this email
          </p>

        </td>
      </tr>

    </table>
  </td></tr>
</table>
</body>
</html>"""

        msg.attach(MIMEText(plain, "plain", "utf-8"))
        msg.attach(MIMEText(html,  "html",  "utf-8"))

        # ── Send ─────────────────────────────────────────────────
        print("[EMAIL] Connecting to smtp.gmail.com:465 ...")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=20) as server:
            server.ehlo()
            print("[EMAIL] Logging in ...")
            server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
            print("[EMAIL] Sending message ...")
            server.sendmail(SENDER_EMAIL, [RECEIVER_EMAIL], msg.as_string())

        print(f"[EMAIL] SUCCESS — sent to {RECEIVER_EMAIL}")
        return True

    except smtplib.SMTPAuthenticationError:
        print("[EMAIL] AUTH ERROR — SENDER_APP_PASSWORD is wrong")
        print("[EMAIL] Use a Gmail App Password (Google Account > Security > App Passwords)")
        return False
    except smtplib.SMTPRecipientsRefused as e:
        print(f"[EMAIL] RECIPIENT REFUSED — check RECEIVER_EMAIL: {e}")
        return False
    except smtplib.SMTPException as e:
        print(f"[EMAIL] SMTP ERROR: {e}")
        return False
    except Exception as e:
        print(f"[EMAIL] UNEXPECTED ERROR: {e}")
        print(traceback.format_exc())
        return False
