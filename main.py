
import requests
from datetime import datetime
import os
import telegram
from pytz import timezone
from apscheduler.schedulers.blocking import BlockingScheduler

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
PAIRS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "PEPEUSDT", "XRPUSDT", "DOGEUSDT", "XAUUSD", "XAGUSD"]
INTERVAL = "15m"

bot = telegram.Bot(token=TELEGRAM_TOKEN)

def fetch_technical_summary(pair):
    try:
        url = "https://scanner.tradingview.com/crypto/scan"
        payload = {
            "symbols": {"tickers": [f"BINANCE:{pair}"], "query": {"types": []}},
            "columns": ["RSI", "MACD.macd", "MACD.signal", "close"]
        }
        response = requests.post(url, json=payload)
        data = response.json()
        d = data["data"][0]["d"]

        rsi = d[0]
        macd = d[1] - d[2]
        price = d[3]

        direction = "LONG" if rsi < 30 and macd > 0 else "SHORT" if rsi > 70 and macd < 0 else "Brak sygnału"
        entry = round(price, 2)
        tp = round(entry * 1.01, 2) if direction == "LONG" else round(entry * 0.99, 2)
        sl = round(entry * 0.99, 2) if direction == "LONG" else round(entry * 1.01, 2)

        return f"{pair} | RSI: {rsi:.2f}, MACD: {macd:.2f}, Price: {price:.2f}\nDirection: {direction}, Entry: {entry}, TP: {tp}, SL: {sl}"
    except Exception as e:
        return f"{pair} | Error: {str(e)}"

def send_summary():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    summary = f"🕒 3H Market Summary ({now})\n\n"
    for pair in PAIRS:
        summary += fetch_technical_summary(pair) + "\n\n"
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=summary)

scheduler = BlockingScheduler()
scheduler.add_job(send_summary, 'interval', hours=3, timezone=timezone('Europe/Berlin'))
send_summary()
scheduler.start()
