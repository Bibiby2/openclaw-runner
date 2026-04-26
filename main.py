import os
import time
import requests

# =========================
# CONFIG
# =========================
VC_KEY = os.getenv("VISUAL_CROSSING_KEY")
TG_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

BANKROLL = 100  # später dynamisch
MIN_EDGE = 0.10
KELLY_FRACTION = 0.1
TARGET_HOUR = 12
SLEEP_TIME = 300

TEST_MODE = True  # später False

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

        # 👉 gezielte Stunde
        prob = hours[TARGET_HOUR]["precipprob"] / 100

        return prob

    except Exception as e:
        print("❌ Weather error:", e)
        return None

# =========================
# MARKET (MOCK → später echt)
# =========================
def get_market_price(city):
    # ⚠️ später durch echte API ersetzen
    return 0.65

# =========================
# KELLY (SAFE)
# =========================
def kelly(prob, price, bankroll):
    try:
        if prob <= price:
            return 0

        if price <= 0 or price >= 1:
            return 0

        b = (1 - price) / price
        f = (prob * (b + 1) - 1) / b

        safe_f = f * KELLY_FRACTION

        bet = safe_f * bankroll

        # 🛡️ HARD CAP (max 10%)
        bet = min(bet, bankroll * 0.10)

        return round(max(bet, 0), 2)

    except:
        return 0

# =========================
# STRATEGY LOOP
# =========================
def run():
    send_tg("🚀 *INSTITUTIONAL WEATHER BOT STARTED*\nMode: Kelly + Hourly")

    cities = [
        {"name": "New York", "lat": 40.71, "lon": -74.00},
        {"name": "London", "lat": 51.50, "lon": -0.12},
    ]

    while True:
        print("\n--- NEW CYCLE ---")

        for city in cities:
            try:
                prob = get_weather(city["lat"], city["lon"])

                if prob is None:
                    continue

                market_price = get_market_price(city["name"])
                edge = prob - market_price

                print(f"{city['name']} | Model: {prob:.2f} | Market: {market_price:.2f} | Edge: {edge:.2f}")

                # =========================
                # EDGE FILTER
                # =========================
                if edge < MIN_EDGE:
                    print("⚠️ No trade (edge too small)")
                    continue

                # =========================
                # POSITION SIZE
                # =========================
                bet = kelly(prob, market_price, BANKROLL)

                if bet <= 0:
                    print("⚠️ Kelly = 0")
                    continue

                # =========================
                # SIGNAL
                # =========================
                send_tg(
                    f"💎 *ALPHA TRADE*\n\n"
                    f"📍 {city['name']}\n"
                    f"⏱️ Hour: {TARGET_HOUR}:00\n\n"
                    f"🌧️ Model: {prob*100:.1f}%\n"
                    f"📊 Market: {market_price*100:.1f}%\n"
                    f"📈 Edge: {edge*100:.1f}%\n\n"
                    f"💰 Bet (Kelly Safe): ${bet}"
                )

                # Cooldown → wichtig gegen Overtrading
                time.sleep(180)

            except Exception as e:
                print(f"❌ Error in {city['name']}: {e}")
                continue

        time.sleep(SLEEP_TIME)

# =========================
# START
# =========================
if __name__ == "__main__":
    run()
