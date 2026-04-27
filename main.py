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

DRY_RUN = True

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

        hours = r["days"][0]["hours"]

        # Safety: falls Stunde nicht existiert
        if TARGET_HOUR >= len(hours):
            return None

        prob = hours[TARGET_HOUR]["precipprob"] / 100
        return prob

    except Exception as e:
        print("❌ Weather error:", e)
        return None

# =========================
# FIND TOKEN (ROBUST)
# =========================
def find_weather_token(city):
    try:
        url = f"https://gamma-api.polymarket.com/markets?active=true&closed=false&q={city}%20rain"
        r = requests.get(url, timeout=10).json()

        today_str = datetime.utcnow().strftime("%Y-%m-%d")

        for m in r:
            question = m.get("question", "").lower()
            end_date = m.get("endDate", "")
            volume = m.get("volume", 0)

            # 🔥 FILTERS
            if city.lower() not in question:
                continue
            if "rain" not in question:
                continue
            if today_str not in end_date:
                continue
            if volume < 1000:  # 🚨 LIQUIDITY FILTER
                continue

            token_ids = m.get("clobTokenIds", [])

            # YES/NO CHECK
            if len(token_ids) < 2:
                continue

            print(f"✅ Found market: {m['question']}")
            return token_ids[0]  # YES

        return None

    except Exception as e:
        print("❌ Gamma error:", e)
        return None

# =========================
# MARKET PRICE
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
# KELLY (SAFE)
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
        print(f"🧪 DRY TRADE → {city} ${size}")
        send_tg(
            f"🧪 *DRY TRADE*\n\n"
            f"📍 {city}\n"
            f"💰 Size: ${size}\n"
            f"📊 Price: {price*100:.1f}%\n"
            f"🧠 Model: {prob*100:.1f}%\n"
            f"💎 Edge: {edge*100:.1f}%"
        )
    else:
        send_tg("⚠️ REAL EXECUTION NOT ENABLED YET")

# =========================
# MAIN LOOP
# =========================
def run():
    send_tg("🚀 *FINAL EXECUTION BOT STARTED*\nMode: DRY RUN SAFE")

    cities = [
        {"name": "New York", "lat": 40.71, "lon": -74.00},
        {"name": "London", "lat": 51.50, "lon": -0.12},
    ]

    while True:
        print("\n--- NEW CYCLE ---")

        for c in cities:
            try:
                # 1. MARKET FIND
                token_id = find_weather_token(c["name"])

                if not token_id:
                    print(f"⚠️ No valid market for {c['name']}")
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
