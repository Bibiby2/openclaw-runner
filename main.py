import os
import time
import requests

# =========================
# CONFIG
# =========================
VC_KEY = os.getenv("VISUAL_CROSSING_KEY")
TG_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# 👉 Execution Settings
BANKROLL = 100
MIN_EDGE = 0.10
KELLY_FRACTION = 0.1
TARGET_HOUR = 12
SLEEP_TIME = 180

DRY_RUN = True  # ⚠️ VERY IMPORTANT (noch kein echtes Geld)

# =========================
# TELEGRAM
# =========================
def send_tg(msg):
    try:
        url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        requests.post(url, json={
            "chat_id": CHAT_ID,
            "text": msg,
            "parse_mode": "Markdown"
        })
    except:
        print("Telegram error")

# =========================
# WEATHER
# =========================
def get_weather(lat, lon):
    try:
        url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{lat},{lon}/today?unitGroup=metric&elements=precipprob&key={VC_KEY}&contentType=json"
        r = requests.get(url, timeout=10).json()
        return r["days"][0]["hours"][TARGET_HOUR]["precipprob"] / 100
    except Exception as e:
        print("❌ Weather error:", e)
        return None

# =========================
# POLYMARKET PRICE (REAL)
# =========================
def get_market_price(token_id):
    try:
        url = f"https://clob.polymarket.com/price?token_id={token_id}&side=BUY"
        r = requests.get(url, timeout=10).json()
        return float(r["price"])
    except Exception as e:
        print("❌ Market error:", e)
        return None

# =========================
# KELLY
# =========================
def kelly(prob, price, bankroll):
    if prob <= price:
        return 0

    if price <= 0 or price >= 1:
        return 0

    b = (1 - price) / price
    f = (prob * (b + 1) - 1) / b

    safe_f = f * KELLY_FRACTION
    bet = safe_f * bankroll

    # Safety Cap
    return round(min(bet, bankroll * 0.10), 2)

# =========================
# EXECUTION (SAFE)
# =========================
def execute_trade(city, price, size, prob, edge):
    if DRY_RUN:
        print(f"🧪 DRY RUN → BUY YES {city} | ${size}")
        send_tg(
            f"🧪 *DRY TRADE*\n\n"
            f"📍 {city}\n"
            f"💰 Size: ${size}\n"
            f"📊 Price: {price*100:.1f}%\n"
            f"🧠 Model: {prob*100:.1f}%\n"
            f"💎 Edge: {edge*100:.1f}%"
        )
    else:
        # 🚨 HIER kommt später echte Order rein
        send_tg("⚠️ REAL TRADE WOULD EXECUTE HERE")

# =========================
# MAIN LOOP
# =========================
def run():
    send_tg("🚀 *EXECUTION BOT STARTED*\nMode: DRY RUN")

    markets = [
        {
            "city": "New York",
            "lat": 40.71,
            "lon": -74.00,
            "token_id": "REPLACE_WITH_REAL"
        },
    ]

    while True:
        print("\n--- NEW CYCLE ---")

        for m in markets:
            try:
                prob = get_weather(m["lat"], m["lon"])
                if prob is None:
                    continue

                price = get_market_price(m["token_id"])
                if price is None:
                    print("⚠️ No market price")
                    continue

                edge = prob - price

                print(f"{m['city']} | Model: {prob:.2f} | Market: {price:.2f} | Edge: {edge:.2f}")

                if edge < MIN_EDGE:
                    print("⚠️ No trade")
                    continue

                size = kelly(prob, price, BANKROLL)

                if size <= 0:
                    print("⚠️ Kelly = 0")
                    continue

                execute_trade(m["city"], price, size, prob, edge)

                time.sleep(180)

            except Exception as e:
                print("❌ Loop error:", e)
                continue

        time.sleep(SLEEP_TIME)

# =========================
# START
# =========================
if __name__ == "__main__":
    run()
