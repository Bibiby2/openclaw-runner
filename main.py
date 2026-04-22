import requests
import time
import os

# =========================
# ENV VARS (Railway)
# =========================
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# =========================
# WEATHER FUNCTION
# =========================
def get_weather(city="Vienna"):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()

        temp = data["main"]["temp"]
        description = data["weather"][0]["description"]

        return f"{city}: {temp}°C | {description}"

    except Exception as e:
        return f"❌ Weather Error: {e}"

# =========================
# TELEGRAM FUNCTION
# =========================
def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message
        }

        requests.post(url, data=payload)
        print("📩 Telegram gesendet:", message)

    except Exception as e:
        print("❌ Telegram Fehler:", e)

# =========================
# POLYMARKET FUNCTION
# =========================
def get_polymarket_data():
    try:
        url = "https://gamma-api.polymarket.com/markets"
        response = requests.get(url)
        data = response.json()

        messages = []

        # wir nehmen die ersten 5 Märkte
        for market in data[:5]:
            question = market.get("question", "N/A")
            price = market.get("lastTradePrice", "N/A")

            msg = f"📊 {question}\n💰 Price: {price}"
            print(msg)
            messages.append(msg)

        return messages

    except Exception as e:
        error_msg = f"❌ Polymarket Error: {e}"
        print(error_msg)
        return [error_msg]

# =========================
# MAIN LOOP
# =========================
def main():
    print("🚀 Bot gestartet...")

    while True:
        print("\n--- Neue Runde ---")

        # WEATHER
        weather = get_weather("Vienna")
        print(weather)
        send_telegram(f"🌦 Weather Update:\n{weather}")

        # POLYMARKET
        markets = get_polymarket_data()
        for m in markets:
            send_telegram(m)

        # WAIT (5 Minuten)
        time.sleep(300)

# =========================
# START
# =========================
if __name__ == "__main__":
    main()
