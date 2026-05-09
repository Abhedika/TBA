import requests
from bs4 import BeautifulSoup


URL = "https://projects.devlab.ac.nz/"


def fetch_website_data():

    try:

        response = requests.get(URL, timeout=10)

        soup = BeautifulSoup(response.text, "html.parser")

        # 🔹 Extract website text
        text = soup.get_text(separator=" ", strip=True)

        # 🔹 Limit size
        return text[:5000]

    except Exception as e:

        print("Website fetch error:", e)

        return ""