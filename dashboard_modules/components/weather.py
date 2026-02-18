"""
Weather information fetching
"""
import streamlit as st


@st.cache_data(ttl=1800)  # 30分キャッシュ
def fetch_tokyo_weather() -> dict:
    """東京の天気情報を取得"""
    try:
        import requests
        # wttr.in API（無料、APIキー不要）
        response = requests.get("https://wttr.in/Tokyo?format=j1", timeout=5)
        data = response.json()

        current = data["current_condition"][0]
        temp_c = current["temp_C"]
        weather_desc = current["weatherDesc"][0]["value"]
        feels_like = current["FeelsLikeC"]
        humidity = current["humidity"]

        # 天気アイコンマッピング
        weather_code = current["weatherCode"]
        icon = "☀️"  # default sunny
        if weather_code in ["113"]:
            icon = "☀️"  # Clear/Sunny
        elif weather_code in ["116", "119", "122"]:
            icon = "⛅"  # Partly cloudy
        elif weather_code in ["143", "248", "260"]:
            icon = "🌫️"  # Fog/Mist
        elif weather_code in ["176", "263", "266", "293", "296"]:
            icon = "🌧️"  # Light rain
        elif weather_code in ["299", "302", "305", "308", "356"]:
            icon = "🌧️"  # Heavy rain
        elif weather_code in ["227", "230", "323", "326", "329", "332", "335", "338"]:
            icon = "❄️"  # Snow
        elif weather_code in ["200", "386", "389", "392", "395"]:
            icon = "⛈️"  # Thunderstorm

        return {
            "temp": temp_c,
            "feels_like": feels_like,
            "weather": weather_desc,
            "humidity": humidity,
            "icon": icon
        }
    except Exception as e:
        return {
            "temp": "--",
            "feels_like": "--",
            "weather": "N/A",
            "humidity": "--",
            "icon": "☁️"
        }
