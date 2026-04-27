import os
import time
import requests
from datetime import datetime

# =========================
# CONFIG
# =========================
VC_KEY = os.getenv("VISUAL_CROSSING_KEY")
TG_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

BANKROLL = 100
MIN_EDGE = 0.10
KELLY_FRACTION = 0.1
TARGET_HOUR = 12
SLEEP_TIME = 180

DRY_RUN = True  # ⚠️ später False

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
# WEATHER (HOURLY)
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
# FIND TOKEN ID (GAMMA API)
# =========================
def find_weather_token_id(city):
    try:
        url = f"https://gamma-api.polymarket.com/markets?active=true&closed=false&q={city}%20rain"
        r = requests.get(url, timeout=10).json()

        today = datetime.utcnow().strftime("%B").lower()

        for m in r:
            question = m.get("question", "").lower()

            if "rain" in question and city.lower() in question:
                # optional: Datum-Check verbessern später
                token_ids = m.get("clobTokenIds", [])

                if token_ids:
                    print(f"✅ Found market: {m['question']}")
                    return token_ids[0]

        return None

    except Exception as e:
        print("❌ Gamma error:", e)
        return None

# =========================
# MARKET PRICE (CLOB)
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

    return round(min(bet, bankroll * 0.10), 2)

# =========================
# EXECUTION
# =========================
def execute_trade(city, price, size, prob, edge):
    if DRY_RUN:
        print(f"🧪 DRY TRADE {city} ${size}")
        send_tg(
            f"🧪 *DRY TRADE*\n\n"
            f"📍 {city}\n"
            f"💰 Size: ${size}\n"
            f"📊 Price: {price*100:.1f}%\n"
            f"🧠 Model: {prob*100:.1f}%\n"
            f"💎 Edge: {edge*100:.1f}%"
        )
    else:
        send_tg("⚠️ REAL TRADE EXECUTION NOT IMPLEMENTED YET")

# =========================
# MAIN LOOP
# =========================
def run():
    send_tg("🚀 *DYNAMIC WEATHER BOT STARTED*\nMode: Execution Ready")

    cities = [
        {"name": "New York", "lat": 40.71, "lon": -74.00},
        {"name": "London", "lat": 51.50, "lon": -0.12},
    ]

    while True:
        print("\n--- NEW CYCLE ---")

        for c in cities:
            try:
                # 1. FIND MARKET
                token_id = find_weather_token_id(c["name"])

                if not token_id:
                    print(f"⚠️ No market for {c['name']}")
                    continue

                # 2. WEATHER
                prob = get_weather(c["lat"], c["lon"])
                if prob is None:
                    continue

                # 3. MARKET PRICE
                price = get_market_price(token_id)
                if price is None:
                    continue

                edge = prob - price

                print(f"{c['name']} | Model: {prob:.2f} | Market: {price:.2f} | Edge: {edge:.2f}")

                # 4. EDGE FILTER
                if edge < MIN_EDGE:
                    print("⚠️ No trade")
                    continue

                # 5. POSITION SIZE
                size = kelly(prob, price, BANKROLL)

                if size <= 0:
                    continue

                # 6. EXECUTE
                execute_trade(c["name"], price, size, prob, edge)

                time.sleep(120)

            except Exception as e:
                print("❌ Loop error:", e)
                continue

        time.sleep(SLEEP_TIME)

# =========================
# START
# =========================
if __name__ == "__main__":
    run()
