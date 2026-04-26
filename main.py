import os
import time
import requests

# --- CONFIG ---
VC_API_KEY = os.getenv("VISUAL_CROSSING_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

MIN_EDGE = 0.08
SLEEP_TIME = 300  # 5 Minuten

MARKETS = [
    {"city": "New York", "lat": 40.71, "lon": -74.00, "token_id": "REPLACE_WITH_REAL"},
    {"city": "London", "lat": 51.50, "lon": -0.12, "token_id": "REPLACE_WITH_REAL"},
    {"city": "Hong Kong", "lat": 22.28, "lon": 114.15, "token_id": "REPLACE_WITH_REAL"},
]

# --- TELEGRAM ---
def send_tg(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown"
    })

# --- WEATHER ---
def get_weather(lat, lon):
    try:
        url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{lat},{lon}/today?unitGroup=metric&elements=precipprob&key={VC_API_KEY}&contentType=json"
        r = requests.get(url).json()
        prob = r["days"][0]["precipprob"]
        return prob / 100
    except:
        return None

# --- MARKET ---
def get_market_price(token_id):
    try:
        url = f"https://clob.polymarket.com/price?token_id={token_id}&side=BUY"
        r = requests.get(url).json()
        return float(r["price"])
    except:
        return None

# --- MAIN LOGIC ---
def run():
    send_tg("🚀 *REAL EDGE BOT STARTED*\nStrategy: Weather Arbitrage")

    while True:
        print("\n--- New Cycle ---")

        for m in MARKETS:
            weather_prob = get_weather(m["lat"], m["lon"])
            market_price = get_market_price(m["token_id"])

            if weather_prob is None or market_price is None:
                print(f"❌ Data error: {m['city']}")
                continue

            edge = weather_prob - market_price

            print(f"{m['city']} | Model: {weather_prob:.2f} | Market: {market_price:.2f} | Edge: {edge:.2f}")

            if edge > MIN_EDGE:
                msg = (
                    f"🎯 *TRADE SIGNAL*\n\n"
                    f"📍 {m['city']}\n"
                    f"🧠 Model: {weather_prob*100:.1f}%\n"
                    f"📊 Market: {market_price*100:.1f}%\n"
                    f"💎 Edge: {edge*100:.1f}%\n\n"
                    f"👉 BUY YES"
                )
                send_tg(msg)

                print("✅ TRADE SIGNAL SENT")

                time.sleep(300)

            else:
                print("⚠️ No trade")

        time.sleep(SLEEP_TIME)

# --- START ---
if __name__ == "__main__":
    run()
