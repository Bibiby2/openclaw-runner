import requests
import time
import os

# =========================
# ENV VARS
# =========================
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# =========================
# SETTINGS
# =========================
CITIES = ["Vienna", "London", "New York", "Hong Kong"]

TEST_MODE = True  # 🔥 HIER STEUERST DU ALLES

# =========================
# WEATHER FUNCTION
# =========================
def get_weather(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        data = requests.get(url).json()

        return {
            "city": city,
            "temp": data["main"]["temp"],
            "description": data["weather"][0]["description"].lower()
        }

    except Exception as e:
        print("Weather Error:", e)
        return None

# =========================
# TELEGRAM
# =========================
def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message
        })
        print("📩 Sent:", message)
    except Exception as e:
        print("Telegram Error:", e)

# =========================
# POLYMARKET
# =========================
def get_polymarket_markets():
    try:
        url = "https://gamma-api.polymarket.com/markets"
        return requests.get(url).json()
    except Exception as e:
        print("Polymarket Error:", e)
        return []

# =========================
# DECISION ENGINE
# =========================
def analyze_and_signal(weather, markets):
    signals = []

    city = weather["city"].lower()
    temp = weather["temp"]
    desc = weather["description"]

    for market in markets[:50]:
        question = market.get("question", "").lower()
        price = market.get("lastTradePrice")

        if not price:
            continue

        try:
            price = float(price)
        except:
            continue

        # 🌧 Regen / Clouds
        if city in question and ("rain" in question or "precipitation" in question):
            if "rain" in desc or "cloud" in desc:
                if price < 0.7:
                    signals.append(f"🌧 BUY YES → {question}")

        # 🔥 Temperatur
        if city in question and "temperature" in question:
            if temp > 22 and price < 0.75:
                signals.append(f"🔥 BUY YES → {question}")
            elif temp < 8 and price > 0.65:
                signals.append(f"❄️ BUY NO → {question}")

    # =========================
    # 🧪 TEST MODE
    # =========================
    if TEST_MODE and len(signals) == 0:
        signals.append(f"🧪 TEST SIGNAL → {weather['city']} funktioniert!")

    return signals

# =========================
# MAIN
# =========================
def main():
    print("🚀 Bot läuft...")

    while True:
        print("\n--- Neue Runde ---")

        markets = get_polymarket_markets()

        for city in CITIES:
            weather = get_weather(city)

            if not weather:
                continue

            print(f"{city}: {weather['temp']}°C | {weather['description']}")

            signals = analyze_and_signal(weather, markets)

            for signal in signals:
                send_telegram(f"📊 SIGNAL ({city}):\n{signal}")

        time.sleep(300)

# =========================
# START
# =========================
if __name__ == "__main__":
    main()
