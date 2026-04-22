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

# =========================
# WEATHER FUNCTION
# =========================
def get_weather(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        data = requests.get(url).json()

        temp = data["main"]["temp"]
        description = data["weather"][0]["description"]

        return {
            "city": city,
            "temp": temp,
            "description": description
        }

    except Exception as e:
        print("Weather Error:", e)
        return None

# =========================
# TELEGRAM FUNCTION
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
# POLYMARKET FUNCTION
# =========================
def get_polymarket_markets():
    try:
        url = "https://gamma-api.polymarket.com/markets"
        data = requests.get(url).json()
        return data
    except Exception as e:
        print("Polymarket Error:", e)
        return []

# =========================
# DECISION ENGINE 🧠
# =========================
def analyze_and_signal(weather_data, markets):
    signals = []

    city = weather_data["city"]
    temp = weather_data["temp"]

    for market in markets[:20]:  # nur erste 20 scannen
        question = market.get("question", "").lower()
        price = market.get("lastTradePrice", None)

        if price is None:
            continue

        # 🎯 RULE 1: Regen erkennen
        if "rain" in question and city.lower() in question:
            if "rain" in weather_data["description"]:
                if float(price) < 0.6:
                    signals.append(f"🌧 BUY YES → {question} (Market underpriced)")
                else:
                    signals.append(f"⚖️ HOLD → {question}")

        # 🎯 RULE 2: Temperatur High
        if "temperature" in question and city.lower() in question:
            if temp > 25 and float(price) < 0.7:
                signals.append(f"🔥 BUY YES → {question} (Hot weather edge)")

            elif temp < 10 and float(price) > 0.6:
                signals.append(f"❄️ BUY NO → {question} (Cold weather edge)")

    return signals

# =========================
# MAIN LOOP
# =========================
def main():
    print("🚀 Phase 3.2 Bot gestartet")

    while True:
        print("\n--- Neue Analyse ---")

        markets = get_polymarket_markets()

        for city in CITIES:
            weather = get_weather(city)

            if not weather:
                continue

            print(f"{city}: {weather['temp']}°C | {weather['description']}")

            signals = analyze_and_signal(weather, markets)

            if signals:
                for signal in signals:
                    send_telegram(f"📊 SIGNAL ({city}):\n{signal}")
            else:
                print(f"No signals for {city}")

        time.sleep(300)

# =========================
# START
# =========================
if __name__ == "__main__":
    main()
