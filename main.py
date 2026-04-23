import requests
import os
import time
import random

# ENV
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

CITIES = ["Vienna", "London", "New York", "Hong Kong"]

balance = 100  # Start Kapital (Simulation)

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, data=data)
    except:
        print("Telegram Fehler")

def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    return requests.get(url).json()

def analyze(city, data):
    temp = data["main"]["temp"]
    weather = data["weather"][0]["main"].lower()

    if "rain" in weather:
        return "RAIN"
    elif temp > 28:
        return "HOT"
    elif temp < 5:
        return "COLD"
    return None

# 🔥 SIMULIERTER TRADE
def execute_trade(city, signal):
    global balance

    trade_amount = 2  # pro Trade
    outcome = random.choice(["WIN", "LOSS"])  # Simulation

    if outcome == "WIN":
        profit = trade_amount * 0.8
        balance += profit
    else:
        balance -= trade_amount

    message = f"""
🤖 AUTO TRADE (SIMULATION)

📍 {city}
📊 Signal: {signal}
💸 Einsatz: ${trade_amount}
🎯 Ergebnis: {outcome}

💰 Balance: ${round(balance,2)}
"""
    send_telegram(message)

def run():
    print("AUTO BOT läuft (Simulation)...")

    while True:
        for city in CITIES:
            try:
                data = get_weather(city)
                signal = analyze(city, data)

                if signal:
                    execute_trade(city, signal)

            except Exception as e:
                print("Fehler:", e)

        time.sleep(300)

if __name__ == "__main__":
    run()
