import imaplib
import email
import smtplib
import logging
from email.mime.text import MIMEText
from email.utils import parseaddr
from config import EMAIL, APP_PASSWORD

logger = logging.getLogger(__name__)

# ====================================================
# 🔹 DANGEROUS FILE TYPES
# ====================================================

DANGEROUS_EXTENSIONS = [
    ".exe",
    ".bat",
    ".js",
    ".scr",
    ".cmd",
    ".vbs",
    ".msi"
]


# ====================================================
# 🔹 FETCH EMAILS
# ====================================================

def fetch_emails(limit=10):

    """
    Fetch recent emails from Gmail inbox.
    """

    try:

        mail = imaplib.IMAP4_SSL("imap.gmail.com")

        mail.login(EMAIL, APP_PASSWORD)

        mail.select("inbox")

        _, data = mail.search(None, "ALL")

        email_ids = data[0].split()

        emails = []

        # ====================================================
        # 🔹 FETCH LAST N EMAILS
        # ====================================================

        for e_id in email_ids[-limit:]:

            try:

                _, msg_data = mail.fetch(e_id, "(RFC822)")

                msg = email.message_from_bytes(msg_data[0][1])

                body = ""

                # ====================================================
                # 🔹 ATTACHMENT SCANNING
                # ====================================================

                dangerous_attachment_found = False

                for part in msg.walk():

                    filename = part.get_filename()

                    if filename:

                        for ext in DANGEROUS_EXTENSIONS:

                            if filename.lower().endswith(ext):

                                logger.warning(
                                    f"⚠️ Dangerous attachment detected: {filename}"
                                )

                                print(
                                    f"⚠️ Dangerous attachment blocked: {filename}"
                                )

                                dangerous_attachment_found = True

                # 🔹 Skip dangerous emails
                if dangerous_attachment_found:
                    continue

                # ====================================================
                # 🔹 EXTRACT EMAIL BODY
                # ====================================================

                try:

                    if msg.is_multipart():

                        for part in msg.walk():

                            if part.get_content_type() == "text/plain":

                                body = (
                                    part.get_payload(decode=True)
                                    .decode(errors="ignore")
                                )

                                break

                    else:

                        body = (
                            msg.get_payload(decode=True)
                            .decode(errors="ignore")
                        )

                except ValueError as ve:

                    logger.warning(
                        f"Error decoding email body: {ve}"
                    )

                    body = ""

                # ====================================================
                # 🔹 EXTRACT SENDER
                # ====================================================

                sender_email = parseaddr(msg["from"])[1]

                if sender_email:

                    emails.append({

                        "from": sender_email,

                        "body": body,

                        # 🔹 Needed for SAME THREAD reply
                        "subject": msg["Subject"],

                        "message_id": msg["Message-ID"]

                    })

            except Exception as e:

                logger.warning(
                    f"Error processing email {e_id}: {e}"
                )

                continue

        mail.logout()

        logger.info(
            f"✔ Fetched {len(emails)} safe emails"
        )

        return emails

    # ====================================================
    # 🔹 ERROR HANDLING
    # ====================================================

    except imaplib.IMAP4.error as e:

        logger.error(f"❌ IMAP error: {e}")

        return []

    except smtplib.SMTPException as e:

        logger.error(f"❌ SMTP error: {e}")

        return []

    except Exception as e:

        logger.error(f"❌ Error fetching emails: {e}")

        return []


# ====================================================
# 🔹 SEND EMAIL (SAME THREAD)
# ====================================================

def send_email(to, subject, message, message_id=None):

    """
    Send email reply in SAME thread.
    """

    try:

        if not to or not message:

            logger.warning(
                "⚠️ Skipping send: empty recipient or message"
            )

            return False

        # ====================================================
        # 🔹 CONNECT SMTP SERVER
        # ====================================================

        server = smtplib.SMTP(
            "smtp.gmail.com",
            587
        )

        server.starttls()

        server.login(
            EMAIL,
            APP_PASSWORD
        )

        # ====================================================
        # 🔹 CREATE EMAIL
        # ====================================================

        msg = MIMEText(message)

        # 🔹 SAME THREAD SUBJECT
        msg["Subject"] = f"Re: {subject}"

        msg["From"] = EMAIL

        msg["To"] = to

        # ====================================================
        # 🔹 THREADING HEADERS
        # ====================================================

        if message_id:

            msg["In-Reply-To"] = message_id

            msg["References"] = message_id

        # ====================================================
        # 🔹 SEND EMAIL
        # ====================================================

        server.sendmail(
            EMAIL,
            to,
            msg.as_string()
        )

        server.quit()

        logger.info(
            f"✔ Reply sent to {to}"
        )

        print(
            f"✔ Reply sent to {to}"
        )

        return True

    # ====================================================
    # 🔹 ERROR HANDLING
    # ====================================================

    except smtplib.SMTPAuthenticationError:

        logger.error(
            "❌ SMTP authentication failed"
        )

        print(
            "❌ SMTP authentication failed"
        )

        return False

    except smtplib.SMTPException as e:

        logger.error(
            f"❌ SMTP error: {e}"
        )

        print(
            f"❌ SMTP error: {e}"
        )

        return False

    except Exception as e:

        logger.error(
            f"❌ Error sending email: {e}"
        )

        print(
            f"❌ Error sending email: {e}"
        )

        return False