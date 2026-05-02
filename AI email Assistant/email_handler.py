import imaplib
import email
import smtplib
from email.mime.text import MIMEText
from email.utils import parseaddr
from config import *

# 🔹 Fetch emails (ALL emails for testing, limited to last 10)
def fetch_emails():
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(EMAIL, APP_PASSWORD)
    mail.select("inbox")

    # 🔥 CHANGE HERE: ALL instead of UNSEEN
    _, data = mail.search(None, "ALL")
    email_ids = data[0].split()

    emails = []

    # ⚠️ Only last 10 emails (to avoid spam)
    for e_id in email_ids[-10:]:
        _, msg_data = mail.fetch(e_id, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])

        body = ""

        try:
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode(errors="ignore")
                        break
            else:
                body = msg.get_payload(decode=True).decode(errors="ignore")
        except:
            body = ""

        # Extract clean email address
        sender_email = parseaddr(msg["from"])[1]

        emails.append({
            "from": sender_email,
            "body": body
        })

    mail.logout()
    return emails


# 🔹 Send email (professional format)
def send_email(to, message):
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL, APP_PASSWORD)

        msg = MIMEText(message)
        msg["Subject"] = "Re: Your Email"
        msg["From"] = EMAIL
        msg["To"] = to

        server.sendmail(EMAIL, to, msg.as_string())
        server.quit()

        print("Email sent successfully ✔")

    except Exception as e:
        print("Failed to send email:", e)