import os
import requests
from bs4 import BeautifulSoup

# Constants
URL = "http://openinsider.com/screener?s=&o=&pl=&ph=&ll=&lh=&fd=365&fdr=&td=0&tdr=&fdlyl=&fdlyh=6&daysago=&xp=1&vl=25&vh=&ocl=1&och=&sic1=-1&sicl=100&sich=9999&isceo=1&iscfo=1&isvp=1&isdirector=1&istenpercent=1&grp=2&nfl=&nfh=&nil=3&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=0&cnt=1&page=1"
token = "7012997345:AAGft8E_tJ5JJXvF24Ivc-3G_F3bB69IvIw"
chat_id = "54508698"
TELEGRAM_BOT_URL = f"https://api.telegram.org/bot{token}/sendMessage"
PROJECT_ID = os.environ.get("GCP_PROJECT")  # Cloud Function sets this automatically
SECRET_ID = "last-filing-date"

SELECTORS = {
    "filling_date": ".tinytable > tbody:nth-child(2) > tr:nth-child(1) > td:nth-child(2) > div:nth-child(1) > a:nth-child(1)",
    "ticker": ".tinytable > tbody:nth-child(2) > tr:nth-child(1) > td:nth-child(4) > b:nth-child(1) > a:nth-child(1)",
    "industry": ".tinytable > tbody:nth-child(2) > tr:nth-child(1) > td:nth-child(6) > a:nth-child(1)",
    "delta_own": ".tinytable > tbody:nth-child(2) > tr:nth-child(1) > td:nth-child(12)",
    "value": ".tinytable > tbody:nth-child(2) > tr:nth-child(1) > td:nth-child(13)",
}
LAST_SEEN_FILE = ".last_seen.txt"

def get_last_seen():
    if os.path.exists(LAST_SEEN_FILE):
        with open(LAST_SEEN_FILE, "r") as f:
            return f.read().strip()
    return None

def set_last_seen(value):
    with open(LAST_SEEN_FILE, "w") as f:
        f.write(value)

def send_to_telegram_bot(data):
    message = f"""
🔔 New Insider Buy Detected 🔔
Filing Date: {data['filling_date']}  
Ticker:      {data['ticker']}  
Industry:    {data['industry']}  
ΔOwn:        {data['delta_own']}  
Value:       {data['value']}
"""
    payload = {"chat_id": chat_id, "text": message}
    requests.post(TELEGRAM_BOT_URL, data=payload)

def scrape_handler(request):
    try:
        res = requests.get(URL)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        data = {k: (soup.select_one(sel).text.strip() if soup.select_one(sel) else "[not found]")
                for k, sel in SELECTORS.items()}

        last_seen = get_last_seen()
        if data["filling_date"] != last_seen:
            send_to_telegram_bot(data)
            set_last_seen(data["filling_date"])
            return "Update sent", 200
        else:
            return "No change", 200

    except Exception as e:
        print(f"Error: {e}")
        return f"Error: {str(e)}", 500
