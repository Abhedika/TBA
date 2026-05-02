from email_handler import fetch_emails, send_email
from agent import run_agent

def run():
    emails = fetch_emails()

    if not emails:
        print("No new emails found.")
        return

    for mail in emails:
        print("\nProcessing email...")

        result = run_agent(mail["body"])
        print(result)

        result_lower = result.lower()

        # 🔹 Extract response safely
        response = ""
        if "response:" in result_lower:
            try:
                response = result.split("RESPONSE:")[-1].strip()
            except:
                response = ""

        # 🔹 CASE 1: Reply (more flexible detection)
        if "reply" in result_lower and "no-reply" not in result_lower:
            if response and response.lower() != "none" and len(response) > 5:
                send_email(mail["from"], response)
                print("Reply sent ✔")
            else:
                print("Skipped empty or invalid reply ❌")

        # 🔹 CASE 2: Spam
        elif "no-reply" in result_lower or "spam" in result_lower:
            print("Spam detected → no reply")

        # 🔹 CASE 3: Ignore
        elif "ignore" in result_lower or "trash" in result_lower:
            print("Ignored email")

        # 🔹 CASE 4: Fallback (VERY IMPORTANT)
        else:
            print("Unknown format → applying fallback")

            # fallback: treat as normal email
            fallback_reply = "Thank you for your email. I will get back to you shortly."

            send_email(mail["from"], fallback_reply)
            print("Fallback reply sent ✔")


if __name__ == "__main__":
    run()