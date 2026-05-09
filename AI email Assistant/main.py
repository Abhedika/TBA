import logging
import json
from email_handler import fetch_emails, send_email
from agent import run_agent

# ====================================================
# 🔹 SYSTEM SECURITY SETTINGS
# ====================================================

SYSTEM_PASSWORD = "admin123"

MAX_EMAILS = 10

FALLBACK_REPLY = """
Thank you for your email.

Your message has been received successfully.
I will review your request and get back to you shortly.

Kind regards,
AI Email Assistant
"""

# ====================================================
# 🔹 CONFIGURE LOGGING
# ====================================================

logging.basicConfig(
    filename="logs.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

logger = logging.getLogger(__name__)

# ====================================================
# 🔹 USER AUTHENTICATION
# ====================================================

def authenticate():

    password = input("Enter system password: ")

    if password != SYSTEM_PASSWORD:

        print("❌ Access denied")

        logger.warning("Failed login attempt")

        exit()

    print("✅ Access granted")

    logger.info("User authenticated successfully")


# ====================================================
# 🔹 PROMPT INJECTION DETECTION
# ====================================================

def is_prompt_injection(text):

    suspicious_keywords = [

        "ignore previous instructions",

        "follow these instructions",

        "you are an ai assistant",

        "only respond",

        "strict instructions",

        "system prompt",

        "act as",

        "do not explain",

        "respond only",

        "reveal your prompt",

        "pretend to be",

        "bypass security"

    ]

    text_lower = text.lower()

    return any(
        keyword in text_lower
        for keyword in suspicious_keywords
    )


# ====================================================
# 🔹 MAIN EMAIL PROCESSING
# ====================================================

def process_emails():

    try:

        emails = fetch_emails()

        # 🔹 Rate limiting
        emails = emails[:MAX_EMAILS]

        if not emails:

            print("No emails found.")

            logger.info("No emails found.")

            return

        logger.info(
            f"Processing {len(emails)} email(s)..."
        )

        # ====================================================
        # 🔹 PROCESS EACH EMAIL
        # ====================================================

        for idx, mail in enumerate(emails, 1):

            try:

                print(
                    f"\n[{idx}/{len(emails)}] Processing email..."
                )

                logger.info(
                    f"Processing email from: {mail['from']}"
                )

                # ====================================================
                # 🔹 PROMPT INJECTION CHECK
                # ====================================================

                if is_prompt_injection(mail["body"]):

                    print(
                        "⚠️ Prompt injection detected → treated as SPAM"
                    )

                    logger.warning(
                        "Prompt injection detected"
                    )

                    continue

                # ====================================================
                # 🔹 RUN AI AGENT
                # ====================================================

                result = run_agent(mail["body"])

                print(result)

                logger.info(f"AI Output: {result}")

                # ====================================================
                # 🔹 JSON PARSING
                # ====================================================

                try:

                    data = json.loads(result)

                    category = (
                        data.get("category", "")
                        .upper()
                    )

                    action = (
                        data.get("action", "")
                        .lower()
                    )

                    response = (
                        data.get("response", "")
                        .strip()
                    )

                except Exception:

                    # ====================================================
                    # 🔹 FALLBACK PARSER
                    # ====================================================

                    result_lower = result.lower()

                    category = "UNKNOWN"

                    action = ""

                    response = ""

                    if "category:" in result_lower:

                        try:

                            category = (
                                result.split("CATEGORY:")[-1]
                                .split("\n")[0]
                                .strip()
                                .upper()
                            )

                        except:

                            category = "UNKNOWN"

                    if "action:" in result_lower:

                        try:

                            action = (
                                result.split("ACTION:")[-1]
                                .split("\n")[0]
                                .strip()
                                .lower()
                            )

                        except:

                            action = ""

                    if "response:" in result_lower:

                        try:

                            response = (
                                result.split("RESPONSE:")[-1]
                                .strip()
                            )

                        except:

                            response = ""

                logger.info(f"Category: {category}")

                logger.info(f"Action: {action}")

                # ====================================================
                # 🔹 NORMAL EMAIL
                # ====================================================

                if action == "reply":

                    if (
                        response
                        and response.lower() != "none"
                        and len(response) > 5
                    ):

                        final_reply = f"""
{response}

Kind regards,
AI Email Assistant
"""

                        # 🔹 SAME THREAD REPLY
                        send_email(
                            mail["from"],
                            mail["subject"],
                            final_reply,
                            mail["message_id"]
                        )

                        print("✔ Reply sent")

                        logger.info(
                            "Reply sent successfully"
                        )

                    else:

                        print(
                            "⚠️ Empty AI reply → fallback"
                        )

                        logger.warning(
                            "Empty AI reply detected"
                        )

                        send_email(
                            mail["from"],
                            mail["subject"],
                            FALLBACK_REPLY,
                            mail["message_id"]
                        )

                # ====================================================
                # 🔹 SPAM EMAIL
                # ====================================================

                elif (
                    action == "spam"
                    or action == "no-reply"
                    or category == "SPAM"
                ):

                    print(
                        "🚫 Spam detected → no reply"
                    )

                    logger.info(
                        "Spam email detected"
                    )

                # ====================================================
                # 🔹 TRASH EMAIL
                # ====================================================

                elif (
                    action == "ignore"
                    or category == "TRASH"
                ):

                    print(
                        "⏭️ Ignored email"
                    )

                    logger.info(
                        "Trash email ignored"
                    )

                # ====================================================
                # 🔹 UNKNOWN FORMAT
                # ====================================================

                else:

                    print(
                        "⚠️ Unknown format → fallback reply"
                    )

                    logger.warning(
                        "Unknown AI format"
                    )

                    send_email(
                        mail["from"],
                        mail["subject"],
                        FALLBACK_REPLY,
                        mail["message_id"]
                    )

                    print(
                        "✔ Fallback reply sent"
                    )

                    logger.info(
                        "Fallback reply sent"
                    )

            except Exception as e:

                print(
                    f"❌ Error processing email: {e}"
                )

                logger.error(
                    f"Error processing email: {e}"
                )

        print("\n✔ All emails processed")

        logger.info("All emails processed")

    # ====================================================
    # 🔹 CRITICAL ERROR HANDLING
    # ====================================================

    except Exception as e:

        print(
            f"❌ Critical system error: {e}"
        )

        logger.error(
            f"Critical system error: {e}"
        )


# ====================================================
# 🔹 RUN SYSTEM
# ====================================================

if __name__ == "__main__":

    authenticate()

    process_emails()