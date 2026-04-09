# backend/email_service.py
# Sends complaint emails to ONE fixed email address (set in .env)
# No branch selection — all complaints go to RECEIVER_EMAIL

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

# -------------------------------------------------------
# Email config — set these in your .env file
# -------------------------------------------------------
SENDER_EMAIL       = os.getenv("SENDER_EMAIL",       "your_system_email@gmail.com")
SENDER_APP_PASSWORD= os.getenv("SENDER_APP_PASSWORD", "your_app_password_here")

# Single receiver — all complaints go here
RECEIVER_EMAIL     = os.getenv("RECEIVER_EMAIL",      "admin@brainchecker.com")


def send_complaint_email(
    customer_name: str,
    service:       str,
    rating:        int,
    message:       str,
) -> bool:
    """
    Send a complaint alert email to the one fixed receiver.

    Args:
        customer_name: Name of the customer
        service:       Service/test the customer took
        rating:        Star rating (1-3)
        message:       The complaint text

    Returns:
        True if email sent successfully, False otherwise.
    """
    try:
        # ── Build the email ──────────────────────────────────────
        msg = MIMEMultipart("alternative")
        msg["Subject"]  = f"⚠️ Customer Complaint — {rating}/5 Stars"
        msg["From"]     = SENDER_EMAIL    # system email sends it
        msg["To"]       = RECEIVER_EMAIL  # one fixed receiver

        # Plain text body
        body = f"""
Customer Complaint Alert
========================

Customer Name  : {customer_name}
Service / Test : {service}
Rating         : {rating} / 5

Complaint:
----------
{message}

========================
Sent automatically by the Brain Checker Feedback System.
        """.strip()

        # HTML body (looks better in Gmail)
        stars_html = "⭐" * rating + "☆" * (5 - rating)
        html_body = f"""
<html>
<body style="font-family: Arial, sans-serif; color: #333; background: #f9f9f9; padding: 20px;">
  <div style="max-width: 580px; margin: auto; background: #fff;
              border-radius: 12px; overflow: hidden;
              border: 1px solid #e0e0e0; box-shadow: 0 2px 12px rgba(0,0,0,0.08);">

    <!-- Header -->
    <div style="background: linear-gradient(135deg, #4db6ac, #00897b);
                padding: 24px 28px; color: white;">
      <h2 style="margin: 0; font-size: 1.3rem;">⚠️ Customer Complaint Alert</h2>
      <p style="margin: 6px 0 0; opacity: 0.9; font-size: 0.9rem;">
        Brain Checker Feedback System
      </p>
    </div>

    <!-- Details -->
    <div style="padding: 28px;">
      <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
        <tr style="border-bottom: 1px solid #f0f0f0;">
          <td style="padding: 10px 0; font-weight: 700; color: #555; width: 150px;">
            Customer Name
          </td>
          <td style="padding: 10px 0; color: #1a2332; font-weight: 600;">
            {customer_name}
          </td>
        </tr>
        <tr style="border-bottom: 1px solid #f0f0f0;">
          <td style="padding: 10px 0; font-weight: 700; color: #555;">
            Service / Test
          </td>
          <td style="padding: 10px 0; color: #1a2332;">
            {service}
          </td>
        </tr>
        <tr>
          <td style="padding: 10px 0; font-weight: 700; color: #555;">
            Rating
          </td>
          <td style="padding: 10px 0; font-size: 1.1rem;">
            {stars_html} &nbsp;<span style="color:#555; font-size:0.85rem;">({rating}/5)</span>
          </td>
        </tr>
      </table>

      <!-- Complaint box -->
      <div style="background: #fff8f8; border-left: 4px solid #e57373;
                  border-radius: 6px; padding: 16px 20px;">
        <p style="margin: 0 0 6px; font-weight: 700; color: #c62828; font-size: 0.85rem;
                  text-transform: uppercase; letter-spacing: 0.05em;">
          Complaint Message
        </p>
        <p style="margin: 0; line-height: 1.7; color: #333;">
          {message}
        </p>
      </div>

      <p style="margin-top: 24px; color: #aaa; font-size: 12px;">
        This alert was sent automatically by the Brain Checker Feedback System.
      </p>
    </div>
  </div>
</body>
</html>
        """

        msg.attach(MIMEText(body,      "plain"))
        msg.attach(MIMEText(html_body, "html"))

        # ── Send via Gmail SMTP SSL ──────────────────────────────
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())

        print(f"[EMAIL] ✅ Complaint sent to {RECEIVER_EMAIL}")
        return True

    except smtplib.SMTPAuthenticationError:
        print("[EMAIL] ❌ Auth failed — check SENDER_EMAIL and SENDER_APP_PASSWORD in .env")
        return False
    except Exception as e:
        print(f"[EMAIL] ❌ Failed: {e}")
        return False
