
import requests
import time
import schedule

BOT_TOKEN = "7885990268:AAGQix5ysRybJt5Lk5CwCZ5cu0DFwD3Q7as"
CHAT_ID = "1783328313"
TRADING_PAIRS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "PEPEUSDT", "XRPUSDT", "DOGEUSDT"]
API_URL = "https://api.binance.com/api/v3/klines"
TRADINGVIEW_URL = "https://www.tradingview.com/symbols/"

def send_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=payload)

def get_price_data(symbol):
    try:
        response = requests.get(API_URL, params={"symbol": symbol, "interval": "5m", "limit": 100})
        response.raise_for_status()
        data = response.json()
        if len(data) < 37:
            raise ValueError("Not enough data")
        return [float(candle[4]) for candle in data]
    except Exception as e:
        raise RuntimeError(f"Error fetching {symbol}: {str(e)}")

def get_rsi(data, period=14):
    gains = []
    losses = []
    for i in range(1, period + 1):
        delta = data[-i] - data[-i - 1]
        if delta > 0:
            gains.append(delta)
        else:
            losses.append(abs(delta))
    avg_gain = sum(gains) / period if gains else 0
    avg_loss = sum(losses) / period if losses else 0
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 2)

def get_macd(data):
    def ema(prices, period):
        k = 2 / (period + 1)
        ema_val = prices[0]
        for price in prices[1:]:
            ema_val = price * k + ema_val * (1 - k)
        return ema_val
    macd = ema(data[-26:], 12) - ema(data[-26:], 26)
    signal = ema(data[-26:], 9)
    return macd, signal

def format_symbol(pair):
    return pair.replace("USDT", "")

def run_summary():
    summary = "🕒 3H Market Summary\n\n"
    ranking = []

    for pair in TRADING_PAIRS:
        try:
            closes = get_price_data(pair)
            rsi = get_rsi(closes)
            macd, signal = get_macd(closes)
            change = (closes[-1] - closes[-36]) / closes[-36] * 100
            ranking.append((pair, change))

            summary += (
                f"#{format_symbol(pair)} – RSI: {rsi:.2f} | MACD: {macd:.2f} | Change: {change:.2f}%\n"
                f"{TRADINGVIEW_URL}{format_symbol(pair)}USDT/\n\n"
            )
        except Exception as e:
            summary += f"⚠️ {str(e)}\n"

    summary += "* Top Movers (3h):\n"
    top = sorted(ranking, key=lambda x: abs(x[1]), reverse=True)[:3]
    for s, ch in top:
        summary += f"- #{format_symbol(s)}: {ch:.2f}%\n"

    send_message(summary)

# Harmonogram działania co 3 godziny
schedule.every(3).hours.do(run_summary)

# Start od razu po uruchomieniu
run_summary()

while True:
    schedule.run_pending()
    time.sleep(1)
