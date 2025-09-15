import requests
import pandas as pd
import streamlit as st
import time
import json
import matplotlib.pyplot as plt
from datetime import datetime

API_KEY = "6ea1df8523514452a5671306250808"  # Replace with your WeatherAPI.com key
STATE_CITY_COORD_FILE = "india_state_cities.json"  # Merged JSON file


def fetch_weather(lat, lon):
    """Fetch current weather data for given coordinates."""
    url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={lat},{lon}&aqi=no"
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"API error at ({lat}, {lon}): {e}")
        return None


def fetch_city_weather(city_dict):
    """Fetch weather for all cities in a state."""
    results = []
    for city_name, coords in city_dict.items():
        lat, lon = coords
        data = fetch_weather(lat, lon)
        if data and "current" in data:
            c = data["current"]
            results.append({
                "City": city_name,
                "Temperature (°C)": c.get("temp_c"),
                "Temperature (°F)": c.get("temp_f"),
                "Humidity (%)": c.get("humidity"),
                "Wind Speed (kph)": c.get("wind_kph"),
                "Condition": c.get("condition", {}).get("text", "N/A"),
                "Lat": lat,
                "Lon": lon
            })
        else:
            st.warning(f"Could not fetch data for {city_name}")
        time.sleep(0.6)
    return pd.DataFrame(results)


def fetch_state_weather(state_city_coords):
    """Fetch weather for all states using first city as representative."""
    results = []
    for state, cities in state_city_coords.items():
        # Take first city as representative for state weather
        city_name = list(cities.keys())[0]
        lat, lon = cities[city_name]
        data = fetch_weather(lat, lon)
        if data and "current" in data:
            c = data["current"]
            results.append({
                "State": state,
                "Temperature (°C)": c.get("temp_c"),
                "Temperature (°F)": c.get("temp_f"),
                "Humidity (%)": c.get("humidity"),
                "Wind Speed (kph)": c.get("wind_kph"),
                "Condition": c.get("condition", {}).get("text", "N/A"),
                "Lat": lat,
                "Lon": lon
            })
        else:
            st.warning(f"Could not fetch data for state {state}")
        time.sleep(0.6)
    return pd.DataFrame(results)


def main():
    st.set_page_config(page_title="India Weather Dashboard", layout="wide")
    st.title("Live Weather Dashboard — States & Cities of India")
    # st.caption("Real-time weather updates using WeatherAPI.com")

    # Load state-city coordinates
    with open(STATE_CITY_COORD_FILE) as f:
        STATE_CITIES = json.load(f)

    unit = st.sidebar.radio("Temperature Unit", ["Celsius (°C)", "Fahrenheit (°F)"])
    auto_refresh = st.sidebar.checkbox("Auto-refresh every 1 minutes", value=False)

    st.sidebar.header("City Weather Options")
    state_name = st.sidebar.selectbox("Select State", list(STATE_CITIES.keys()))
    city_options = list(STATE_CITIES[state_name].keys())
    city_name = st.sidebar.selectbox("Select City (Optional)", ["All Cities"] + city_options)

    st.sidebar.markdown("---")
    if st.sidebar.button("Fetch Weather") or True:
        # =========================
        # Top: State-level weather
        # =========================
        st.subheader("State-wise Weather Overview")
        state_df = fetch_state_weather(STATE_CITIES)
        temp_col = "Temperature (°C)" if unit.startswith("Celsius") else "Temperature (°F)"
        st.dataframe(
            state_df[["State", temp_col, "Humidity (%)", "Wind Speed (kph)", "Condition"]],
            use_container_width=True
        )

        if st.sidebar.checkbox("State Bar Chart"):
            st.bar_chart(state_df.set_index("State")[temp_col])

        # =========================
        # Bottom: City-level weather
        # =========================
        st.subheader(f"City Weather — {state_name}")
        if city_name == "All Cities":
            city_df = fetch_city_weather(STATE_CITIES[state_name])
        else:
            coords = STATE_CITIES[state_name][city_name]
            data = fetch_weather(coords[0], coords[1])
            if data and "current" in data:
                c = data["current"]
                city_df = pd.DataFrame([{
                    "City": city_name,
                    "Temperature (°C)": c.get("temp_c"),
                    "Temperature (°F)": c.get("temp_f"),
                    "Humidity (%)": c.get("humidity"),
                    "Wind Speed (kph)": c.get("wind_kph"),
                    "Condition": c.get("condition", {}).get("text", "N/A"),
                    "Lat": coords[0],
                    "Lon": coords[1]
                }])
            else:
                st.error(f"Could not fetch data for {city_name}")
                city_df = pd.DataFrame()

        if not city_df.empty:
            st.dataframe(
                city_df[["City", temp_col, "Humidity (%)", "Wind Speed (kph)", "Condition"]],
                use_container_width=True
            )

            if st.sidebar.checkbox("City Bar Chart"):
                st.bar_chart(city_df.set_index("City")[temp_col])

            st.download_button(
                "Download City Data as CSV",
                data=city_df.to_csv(index=False),
                file_name=f"{state_name}_weather.csv",
                mime="text/csv",
            )

    if auto_refresh:
        st.experimental_rerun()


if __name__ == "__main__":
    main()
