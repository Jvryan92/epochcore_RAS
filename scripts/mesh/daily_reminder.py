"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: jryan2k19@gmail.com for licensing inquiries.
"""

import os
import smtplib
from datetime import datetime, time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "epochcore.system@gmail.com"  # You'll need to set this up
# Create an app password in Google Account
SENDER_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
RECIPIENT_EMAIL = "jryan2k19@gmail.com"

REMINDER_TIMES = [
    (9, 0),   # 9:00 AM
    (12, 0),  # 12:00 PM
    (17, 0)   # 5:00 PM
]

TASKS = """
=== Daily Progress Update ===

📈 Portfolio Status:
- Chess Rating: 2100+ 
- MeshCredit Portfolio: 215,000 MESH Total
  • 75,000 MESH in AA & A tranches
  • 75,000 MESH in enterprise software
  • 65,000 MESH liquid

🌅 Morning Check (9:00 AM):
- Social media performance
- Chess tournament standings
- Portfolio value update
- Security status

🌞 Noon Update (12:00 PM):
- Engagement metrics
- Match results
- Transaction status
- System health

🌆 Evening Summary (5:00 PM):
- Social growth analytics
- Daily performance recap
- Portfolio changes
- Tomorrow's strategy

{social_insights}

⚠️ IMPORTANT:
- Never share API keys
- Keep .env file secure
- Test all integrations
"""


def send_email_reminder(time_slot):
    """Send email reminder for the specified time slot."""
    if not SENDER_PASSWORD:
        print("Error: Email password not set. Please set EMAIL_APP_PASSWORD environment variable.")
        return False

    hour = time_slot[0]
    meridian = "AM" if hour < 12 else "PM"
    hour_12 = hour if hour <= 12 else hour - 12

    subject = f"MeshCredit Tasks Reminder - {hour_12:02d}:00 {meridian}"

    # Create message
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = subject

    # Add tasks to email body
    body = TASKS
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Setup SMTP server connection
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)

        # Send email
        text = msg.as_string()
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, text)
        server.quit()

        print(f"✅ Reminder email sent for {hour_12:02d}:00 {meridian}")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {str(e)}")
        return False


def create_reminder():
    """Create reminder file and set up email notifications."""
    home = Path.home()
    reminder_file = home / "meshcredit_tasks.txt"

    # Save tasks to file
    with open(reminder_file, "w") as f:
        f.write(TASKS)

    print("\n=== MeshCredit Task Reminders Set ===")
    print(f"Reminder file created: {reminder_file}")

    # Setup crontab entries for email reminders
    print("\nTo set up automatic email reminders, add these to your crontab:")
    print("(Run 'crontab -e' to edit)")
    script_path = os.path.abspath(__file__)
    for hour, minute in REMINDER_TIMES:
        print(f"{minute} {hour} * * * PYTHONPATH=/workspaces/epochcore_RAS python3 {script_path}")

    # Send test email
    print("\nSending test email...")
    if send_email_reminder(REMINDER_TIMES[0]):
        print("✅ Email system configured successfully!")
    else:
        print("❌ Email configuration needed. Please set up:")
        print("1. Create an App Password in your Google Account")
        print("2. Set it as EMAIL_APP_PASSWORD environment variable")


def main():
    current_time = datetime.now().time()

    # If script is run directly, create initial setup
    if __name__ == "__main__":
        create_reminder()
    else:
        # When run from cron, send email for the matching time slot
        for time_slot in REMINDER_TIMES:
            reminder_time = time(time_slot[0], time_slot[1])
            if (current_time.hour == reminder_time.hour and
                current_time.minute >= reminder_time.minute and
                    current_time.minute < reminder_time.minute + 5):
                send_email_reminder(time_slot)
                break


if __name__ == "__main__":
    main()
