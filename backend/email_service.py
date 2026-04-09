# backend/email_service.py
# Sends complaint emails to ONE fixed address (RECEIVER_EMAIL in .env)

import smtplib
import traceback
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

# ── Read from environment ────────────────────────────────────────
SENDER_EMAIL        = os.getenv("SENDER_EMAIL",        "").strip()
SENDER_APP_PASSWORD = os.getenv("SENDER_APP_PASSWORD", "").strip()
RECEIVER_EMAIL      = os.getenv("RECEIVER_EMAIL",      "").strip()


def send_complaint_email(
    customer_name: str,
    service:       str,
    rating:        int,
    message:       str,
) -> bool:
    """Send complaint alert to RECEIVER_EMAIL via Gmail SMTP."""

    # ── Safety checks — print clear errors if .env is wrong ──────
    if not SENDER_EMAIL:
        print("[EMAIL] ❌ SENDER_EMAIL is missing in .env / Render environment variables")
        return False
    if not SENDER_APP_PASSWORD:
        print("[EMAIL] ❌ SENDER_APP_PASSWORD is missing in .env / Render environment variables")
        return False
    if not RECEIVER_EMAIL:
        print("[EMAIL] ❌ RECEIVER_EMAIL is missing in .env / Render environment variables")
        return False

    print(f"[EMAIL] Attempting to send from {SENDER_EMAIL} → {RECEIVER_EMAIL}")

    try:
        # ── Build email ──────────────────────────────────────────
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"New Complaint — {rating}/5 Stars | Brain Checker"
        msg["From"]    = SENDER_EMAIL
        msg["To"]      = RECEIVER_EMAIL

        # Plain text fallback
        plain = f"""
Brain Checker — Customer Complaint
===================================
Customer Name  : {customer_name}
Service / Test : {service}
Rating         : {rating} / 5

Complaint:
{message}

---
Sent by Brain Checker AI Feedback System
        """.strip()

        # HTML version
        stars_filled = "⭐" * rating
        stars_empty  = "☆"  * (5 - rating)

        html = f"""
<!DOCTYPE html>
<html>
<body style="margin:0;padding:0;background:#f4f7fb;font-family:Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="padding:32px 16px;">
    <tr>
      <td align="center">
        <table width="580" cellpadding="0" cellspacing="0"
               style="background:#fff;border-radius:12px;overflow:hidden;
                      border:1px solid #e0e0e0;box-shadow:0 2px 12px rgba(0,0,0,0.07);">

          <!-- Header -->
          <tr>
            <td style="background:linear-gradient(135deg,#4db6ac,#00897b);
                       padding:24px 28px;color:#fff;">
              <h2 style="margin:0;font-size:1.2rem;">&#9888;&#65039; Customer Complaint</h2>
              <p style="margin:4px 0 0;opacity:0.85;font-size:0.85rem;">
                Brain Checker AI Feedback System
              </p>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:28px;">

              <table width="100%" cellpadding="0" cellspacing="0"
                     style="border-collapse:collapse;margin-bottom:20px;">
                <tr style="border-bottom:1px solid #f0f0f0;">
                  <td style="padding:10px 0;font-weight:700;color:#555;width:150px;">
                    Customer Name
                  </td>
                  <td style="padding:10px 0;color:#1a2332;font-weight:600;">
                    {customer_name}
                  </td>
                </tr>
                <tr style="border-bottom:1px solid #f0f0f0;">
                  <td style="padding:10px 0;font-weight:700;color:#555;">
                    Service / Test
                  </td>
                  <td style="padding:10px 0;color:#1a2332;">
                    {service}
                  </td>
                </tr>
                <tr>
                  <td style="padding:10px 0;font-weight:700;color:#555;">
                    Rating
                  </td>
                  <td style="padding:10px 0;font-size:1.15rem;">
                    {stars_filled}{stars_empty}
                    <span style="color:#888;font-size:0.82rem;margin-left:6px;">
                      ({rating}/5)
                    </span>
                  </td>
                </tr>
              </table>

              <!-- Complaint box -->
              <div style="background:#fff8f8;border-left:4px solid #e57373;
                          border-radius:6px;padding:16px 20px;">
                <p style="margin:0 0 8px;font-weight:700;color:#c62828;
                          font-size:0.8rem;text-transform:uppercase;letter-spacing:0.06em;">
                  Complaint Message
                </p>
                <p style="margin:0;line-height:1.75;color:#333;">
                  {message}
                </p>
              </div>

              <p style="margin-top:24px;color:#bbb;font-size:11px;">
                Sent automatically by the Brain Checker Feedback System.
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
        """

        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html,  "html"))

        # ── Connect and send ─────────────────────────────────────
        print("[EMAIL] Connecting to smtp.gmail.com:465 ...")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=20) as server:
            print("[EMAIL] Connected. Logging in ...")
            server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
            print("[EMAIL] Login successful. Sending ...")
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())

        print(f"[EMAIL] ✅ Email sent successfully to {RECEIVER_EMAIL}")
        return True

    except smtplib.SMTPAuthenticationError:
        print("[EMAIL] ❌ AUTHENTICATION FAILED.")
        print("[EMAIL]    → Make sure SENDER_APP_PASSWORD is a Gmail App Password")
        print("[EMAIL]    → NOT your regular Gmail password")
        print("[EMAIL]    → Get one at: Google Account → Security → App Passwords")
        return False

    except smtplib.SMTPException as e:
        print(f"[EMAIL] ❌ SMTP error: {e}")
        return False

    except Exception as e:
        print(f"[EMAIL] ❌ Unexpected error: {e}")
        print(traceback.format_exc())
        return False
