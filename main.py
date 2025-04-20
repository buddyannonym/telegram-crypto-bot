
import requests
import datetime
import time

TOKEN = '7885990268:AAGQix5ysRybJt5Lk5CwCZ5cu0DFwD3Q7as'
CHAT_ID = '1783328313'

TRADING_PAIRS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'PEPEUSDT', 'XRPUSDT', 'DOGEUSDT']
API_URL = 'https://api.binance.com/api/v3/klines'
TRADINGVIEW_URL = 'https://www.tradingview.com/symbols/'

def get_rsi(closes, period=14):
    gains, losses = [], []
    for i in range(1, len(closes)):
        delta = closes[i] - closes[i - 1]
        gains.append(max(delta, 0))
        losses.append(max(-delta, 0))
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 2)

def get_macd(closes, short=12, long=26, signal=9):
    def ema(values, period):
        alpha = 2 / (period + 1)
        ema_values = [values[0]]
        for price in values[1:]:
            ema_values.append((1 - alpha) * ema_values[-1] + alpha * price)
        return ema_values
    macd_line = [a - b for a, b in zip(ema(closes, short), ema(closes, long))]
    signal_line = ema(macd_line, signal)
    return macd_line[-1], signal_line[-1]

def get_price_data(symbol):
    response = requests.get(API_URL, params={'symbol': symbol, 'interval': '5m', 'limit': 100})
    closes = [float(c[4]) for c in response.json()]
    return closes

def format_symbol(symbol):
    return symbol.replace('USDT', '')

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': text}
    requests.post(url, data=payload)

def calculate_trade(entry_price, direction='long'):
    if direction == 'long':
        tp = entry_price * 1.02
        sl = entry_price * 0.99
    else:
        tp = entry_price * 0.98
        sl = entry_price * 1.01
    return round(entry_price, 6), round(tp, 6), round(sl, 6)

def run_alerts():
    for pair in TRADING_PAIRS:
        try:
            closes = get_price_data(pair)
            rsi = get_rsi(closes)
            macd, signal = get_macd(closes)
            current_price = closes[-1]

            direction = None
            if rsi > 90:
                direction = 'short'
            elif rsi < 10:
                direction = 'long'
            elif abs(macd - signal) > 0.5:
                direction = 'long' if macd > signal else 'short'

            if direction:
                entry, tp, sl = calculate_trade(current_price, direction)
                emoji = '🚀' if direction == 'long' else '🔻'
                msg = (
                    
msg = (
    f"{emoji} ALERT for #{format_symbol(pair)}\n"
    f"Direction: {'LONG ✅' if direction == 'long' else 'SHORT ❌'}\n"
    f"Price: {current_price}\n"
    f"RSI: {rsi}\n"
    f"MACD: {macd:.2f} | Signal: {signal:.2f}\n"
    f"🎯 Entry: {entry}\n💰 TP: {tp}\n🛑 SL: {sl}\n"
    f"🔗 {TRADINGVIEW_URL}{format_symbol(pair)}USDT/"
)
send_message(msg)
                    msg = (
    f"{emoji} ALERT for #{format_symbol(pair)}\n"
    f"Direction: {'LONG ✅' if direction == 'long' else 'SHORT ❌'}\n"
    f"Price: {current_price}\n"
    f"RSI: {rsi}\n"
    f"MACD: {macd:.2f} | Signal: {signal:.2f}\n"
    f"🎯 Entry: {entry}\n💰 TP: {tp}\n🛑 SL: {sl}\n"
    f"🔗 {TRADINGVIEW_URL}{format_symbol(pair)}USDT/"
)
send_message(msg)
        except Exception as e:
            print(f"Error with {pair}: {e}")

def run_summary():
    summary = "🕒 3H Market Summary\n"
    ranking = []
    for pair in TRADING_PAIRS:
        try:
            closes = get_price_data(pair)
            rsi = get_rsi(closes)
            macd, signal = get_macd(closes)
            change = (closes[-1] - closes[-36]) / closes[-36] * 100
            ranking.append((pair, change))
            summary += (
                summary += (
    f"#{format_symbol(pair)} – RSI: {rsi} | MACD: {macd:.2f} | Change: {change:.2f}%\n"
    f"🔗 {TRADINGVIEW_URL}{format_symbol(pair)}USDT/\n"
)
        except:
            continue
    top = sorted(ranking, key=lambda x: abs(x[1]), reverse=True)[:3]
    summary += "\n Top Movers (3h):\n"
 Top Movers (3h):

    for s, ch in top:
        summary += f"- #{format_symbol(s)}: {ch:.2f}%

    send_message(summary)

while True:
    now = datetime.datetime.now()
    run_alerts()
    if now.hour % 3 == 0 and now.minute < 5:
        run_summary()
    time.sleep(300)
