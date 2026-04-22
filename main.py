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
        description = data["weather"][0]["description"].lower()

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

    city = weather_data["city"].lower()
    temp = weather_data["temp"]
    desc = weather_data["description"]

    for market in markets[:50]:  # mehr Märkte scannen
        question = market.get("question", "").lower()
        price = market.get("lastTradePrice", None)

        if price is None:
            continue

        try:
            price = float(price)
        except:
            continue

        # =========================
        # 🌧 REGEN / CLOUD STRATEGIE (lockerer)
        # =========================
        if city in question and ("rain" in question or "precipitation" in question):
            if "rain" in desc or "cloud" in desc:
                if price < 0.7:
                    signals.append(f"🌧 BUY YES → {question} (edge detected)")
                elif price > 0.8:
                    signals.append(f"⚠️ BUY NO → {question} (overpriced)")

        # =========================
        # 🔥 HITZE STRATEGIE
        # =========================
        if city in question and "temperature" in question:
            if temp > 22 and price < 0.75:
                signals.append(f"🔥 BUY YES → {question} (warm edge)")
            elif temp < 8 and price > 0.65:
                signals.append(f"❄️ BUY NO → {question} (cold edge)")

        # =========================
        # 🧪 FALLBACK (damit du sicher Signale siehst)
        # =========================
        if city in question and len(signals) == 0:
            if price < 0.5:
                signals.append(f"🧪 TEST EDGE → {question} (low price opportunity)")

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
