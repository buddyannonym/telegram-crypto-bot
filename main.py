
import os
import requests
import time
from datetime import datetime
import telegram

# Konfiguracja
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
bot = telegram.Bot(token=BOT_TOKEN)

PAIRS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "PEPEUSDT", "XRPUSDT"]
INTERVAL = "3h"

def fetch_data(symbol):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=5m&limit=50"
    res = requests.get(url)
    prices = [float(candle[4]) for candle in res.json()]
    return prices

def fetch_current_price(symbol):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    res = requests.get(url).json()
    return float(res["price"])

def calculate_indicators(prices):
    if len(prices) < 14:
        return None, None

    gains = [max(0, prices[i] - prices[i - 1]) for i in range(1, len(prices))]
    losses = [max(0, prices[i - 1] - prices[i]) for i in range(1, len(prices))]
    avg_gain = sum(gains[-14:]) / 14
    avg_loss = sum(losses[-14:]) / 14
    rs = avg_gain / avg_loss if avg_loss != 0 else 0
    rsi = 100 - (100 / (1 + rs))
    macd = prices[-1] - sum(prices[-26:]) / 26  # uproszczony MACD

    return round(rsi, 2), round(macd, 2)

def get_recommendation(rsi, macd):
    if rsi < 30 and macd > 0:
        return "LONG"
    elif rsi > 70 and macd < 0:
        return "SHORT"
    return "NEUTRAL"

def calculate_tp_sl(entry, direction):
    if direction == "LONG":
        tp = entry * 1.03
        sl = entry * 0.985
    elif direction == "SHORT":
        tp = entry * 0.97
        sl = entry * 1.015
    else:
        tp = sl = None
    return tp, sl

def build_message():
    lines = ["🕒 *3H Market Summary*"]
    for pair in PAIRS:
        try:
            prices = fetch_data(pair)
            rsi, macd = calculate_indicators(prices)
            change = ((prices[-1] - prices[0]) / prices[0]) * 100
            price = fetch_current_price(pair)
            direction = get_recommendation(rsi, macd)
            tp, sl = calculate_tp_sl(price, direction)

            message = f"\n*#{pair.replace('USDT', '')}* – RSI: {rsi} | MACD: {macd} | Change: {change:.2f}%\n"
            message += f"Recommendation: *{direction}*\nEntry: `{price:.2f}`"
            if tp and sl:
                message += f" | TP: `{tp:.2f}` | SL: `{sl:.2f}`"
            message += f"\n[Chart](https://www.tradingview.com/symbols/{pair}/)"
            lines.append(message)
        except Exception as e:
            lines.append(f"⚠️ Error fetching {pair}: {e}")
    return "\n".join(lines)

if __name__ == "__main__":
    msg = build_message()
    bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode=telegram.ParseMode.MARKDOWN)
