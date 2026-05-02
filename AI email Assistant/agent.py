import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

def run_agent(email_content):
    prompt = f"""
You are an AI email assistant.

Follow instructions STRICTLY.

DO NOT explain anything.
DO NOT write paragraphs outside the format.
DO NOT say "None".

ONLY respond in EXACT format:

CATEGORY: NORMAL or SPAM or TRASH
ACTION: reply or no-reply or ignore
RESPONSE: <write a professional email reply ONLY if ACTION is reply, otherwise leave blank>

Rules:
- NORMAL → reply (MUST write a reply of at least 2-3 sentences)
- SPAM → no-reply
- TRASH → ignore

Email:
{email_content}
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": "tinyllama",
                "prompt": prompt,
                "stream": False
            }
        )

        output = response.json().get("response", "")

        # 🔹 Basic cleanup (important for messy model output)
        output = output.strip()

        return output

    except Exception as e:
        print("Error:", e)
        return "CATEGORY: ERROR\nACTION: ignore\nRESPONSE:"