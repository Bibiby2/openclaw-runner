import requests
import os
import time
from datetime import datetime, timedelta

# ==============================
# ENV
# ==============================
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ==============================
# SETTINGS
# ==============================
CITIES = ["Vienna", "London", "New York", "Hong Kong"]

# starke Signal-Schwellen (B-Modus)
HOT_THRESHOLD = 30        # °C
COLD_THRESHOLD = 3        # °C
WIND_THRESHOLD = 12       # m/s (starker Wind)
RAIN_REQUIRED = True      # Regen muss explizit erkannt werden

# Anti-Spam: pro Stadt/Signal nur alle X Minuten erneut senden
COOLDOWN_MINUTES = 60

# interner Speicher für letzte Signale
last_signal_time = {}  # key: (city, signal) -> datetime

# ==============================
# TELEGRAM
# ==============================
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    try:
        r = requests.post(url, data=data, timeout=10)
        print("Telegram status:", r.text)
    except Exception as e:
        print("Telegram Fehler:", e)

# ==============================
# WEATHER
# ==============================
def get_weather(city):
    url = (
        f"http://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={WEATHER_API_KEY}&units=metric"
    )
    r = requests.get(url, timeout=10)
    return r.json()

# ==============================
# SIGNAL LOGIK (STARK)
# ==============================
def analyze_strong_signal(city, data):
    """
    Gibt (signal, reason_text) zurück oder (None, None)
    """
    main = data.get("main", {})
    weather_list = data.get("weather", [{}])
    wind = data.get("wind", {})

    temp = main.get("temp")
    description = weather_list[0].get("description", "").lower()
    main_weather = weather_list[0].get("main", "").lower()
    wind_speed = wind.get("speed", 0)

    # 1) Starkes Regen-Signal (inkl. Thunderstorm)
    if RAIN_REQUIRED and ("rain" in main_weather or "thunderstorm" in main_weather):
        if "heavy" in description or "thunderstorm" in description:
            return "RAIN_STRONG", f"Heavy rain/thunderstorm detected ({description})"

    # 2) Extreme Hitze
    if temp is not None and temp >= HOT_THRESHOLD:
        return "EXTREME_HEAT", f"Temperature {temp}°C ≥ {HOT_THRESHOLD}°C"

    # 3) Extreme Kälte
    if temp is not None and temp <= COLD_THRESHOLD:
        return "EXTREME_COLD", f"Temperature {temp}°C ≤ {COLD_THRESHOLD}°C"

    # 4) Starker Wind (optional als Edge)
    if wind_speed is not None and wind_speed >= WIND_THRESHOLD:
        return "HIGH_WIND", f"Wind {wind_speed} m/s ≥ {WIND_THRESHOLD} m/s"

    return None, None

# ==============================
# COOLDOWN CHECK
# ==============================
def can_send(city, signal):
    key = (city, signal)
    now = datetime.utcnow()

    if key not in last_signal_time:
        last_signal_time[key] = now
        return True

    if now - last_signal_time[key] >= timedelta(minutes=COOLDOWN_MINUTES):
        last_signal_time[key] = now
        return True

    return False

# ==============================
# MESSAGE FORMAT
# ==============================
def build_message(city, signal, reason, data):
    temp = data["main"]["temp"]
    weather_desc = data["weather"][0]["description"]

    strategy = {
        "RAIN_STRONG": "Buy rain / precipitation markets",
        "EXTREME_HEAT": "Buy high temperature markets",
        "EXTREME_COLD": "Buy low temperature markets",
        "HIGH_WIND": "Check weather volatility markets"
    }.get(signal, "Check market manually")

    msg = f"""
🚨 HIGH QUALITY SIGNAL 🚨

📍 City: {city}
🌡 Temp: {temp}°C
☁️ Weather: {weather_desc}

📊 Signal: {signal}
🧠 Reason: {reason}

👉 Action:
{strategy}

⚠️ Manual confirmation recommended
"""
    return msg.strip()

# ==============================
# LOOP
# ==============================
def run():
    print("🚀 STRONG SIGNAL BOT gestartet...")
    send_telegram("✅ Bot ONLINE (Strong Signal Mode)")

    while True:
        print("\n--- Neue Analyse Runde ---")

        for city in CITIES:
            try:
                data = get_weather(city)

                # basic log
                temp = data["main"]["temp"]
                weather = data["weather"][0]["main"]
                print(f"{city}: {temp}°C | {weather}")

                signal, reason = analyze_strong_signal(city, data)

                if signal:
                    if can_send(city, signal):
                        print(f"✅ SIGNAL: {city} -> {signal}")
                        msg = build_message(city, signal, reason, data)
                        send_telegram(msg)
                    else:
                        print(f"⏳ Cooldown aktiv für {city} ({signal})")
                else:
                    print(f"— Kein starkes Signal für {city}")

            except Exception as e:
                print(f"❌ Fehler bei {city}:", e)

        time.sleep(300)  # alle 5 Minuten

if __name__ == "__main__":
    run()
