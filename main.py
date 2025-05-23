import requests
import random
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from apscheduler.schedulers.blocking import BlockingScheduler

# Email config
EMAIL_ADDRESS = "chitwenarora@gmail.com"
EMAIL_PASSWORD = "ehjmijmmkpgeepml"
EMAIL_TO = "chitwenarora@gmail.com"

filtered_stocks = []

def fetch_nse_preopen_data():
    global filtered_stocks
    print("[INFO] Fetching NSE Pre-Open Data...")
    
    url = "https://www.nseindia.com/api/market-data-pre-open?key=FO"
    headers_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    ]
    headers = {
        "User-Agent": random.choice(headers_list),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nseindia.com/",
    }

    session = requests.Session()
    session.get("https://www.nseindia.com", headers=headers)
    time.sleep(1)

    response = session.get(url, headers=headers)
    data = response.json()
    
    filtered = []
    for stock in data.get("data", []):
        try:
            symbol = stock.get("symbol")
            prev_close = float(stock.get("previousClose", 0))
            pre_open_price = float(stock.get("preOpenPrice", 0))
            volume = int(stock.get("quantity", 0))
            index = stock.get("indexName", "")
            gap_percent = ((pre_open_price - prev_close) / prev_close) * 100 if prev_close else 0

            if gap_percent > 1.5 and volume > 100000 and index == "NIFTY 50":
                filtered.append({
                    "symbol": symbol,
                    "gap_percent": round(gap_percent, 2),
                    "volume": volume,
                    "news_link": f"https://www.google.com/search?q={symbol}+stock+news"
                })
        except:
            continue

    filtered_stocks = filtered
    print(f"[INFO] Found {len(filtered_stocks)} filtered stocks.")
    send_email_alert(filtered_stocks)

def send_email_alert(stocks):
    if not stocks:
        print("[INFO] No stocks to alert.")
        return

    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_TO
    msg['Subject'] = "📈 NSE Pre-Open Screener Alert"

    html = """
    <html><body>
    <h2>NSE Pre-Open Screener Alert (NIFTY 50)</h2>
    <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">
    <tr><th>Stock</th><th>Gap %</th><th>Volume</th><th>News Link</th></tr>
    """

    for s in stocks:
        color = "green" if s["gap_percent"] > 0 else "red"
        html += f"""
        <tr>
            <td>{s['symbol']}</td>
            <td style='color:{color};'>{s['gap_percent']}%</td>
            <td>{s['volume']:,}</td>
            <td><a href="{s['news_link']}" target="_blank">View</a></td>
        </tr>
        """

    html += "</table></body></html>"
    msg.attach(MIMEText(html, 'html'))

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("[✅] Email alert sent successfully.")
    except Exception as e:
        print("[ERROR] Failed to send email:", e)

def scheduled_job():
    print("[INFO] Running scheduled job at 9:08 AM...")
    fetch_nse_preopen_data()

# if __name__ == "__main__":
#     scheduler = BlockingScheduler(timezone="Asia/Kolkata")
#     scheduler.add_job(scheduled_job, 'cron', hour=9, minute=8)
#     print("[⏱️] Scheduler started. Waiting for 9:08 AM IST...")
#     scheduler.start()
if __name__ == "__main__":
    print("[INFO] Starting script manually (no scheduler)...")
    fetch_nse_preopen_data()
    print("[INFO] Script finished.")
