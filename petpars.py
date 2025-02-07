import requests
from bs4 import BeautifulSoup

BASE_URL = "https://petition.president.gov.ua"

# Парсинг інформації про петицію
def get_petition_info(url: str):
    response = requests.get(url)
    if response.status_code != 200:
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.select_one("h1").text.strip()
    votes_collected = int(soup.select_one(".petition_votes_txt span").text.strip().replace(" ", ""))
    days_remaining_text = soup.select_one(".votes_progress_label").text.strip()
    days_remaining = int(''.join(filter(str.isdigit, days_remaining_text)))
    
    return {"title": title, "votes_collected": votes_collected, "days_remaining": days_remaining, "url": url}
