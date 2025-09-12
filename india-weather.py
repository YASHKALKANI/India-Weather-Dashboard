# import requests
# import pandas as pd
# import streamlit as st
# import time
# import json
# import matplotlib.pyplot as plt
# from datetime import datetime

# API_KEY = "6ea1df8523514452a5671306250808"  # Replace with your WeatherAPI.com key
# STATES_JSON_FILE = "india_states.json"
# STATE_COORDINATES_FILE = "india_coordinates.json"


# def fetch_weather(lat, lon):
#     """Fetch current weather data for given coordinates."""
#     url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={lat},{lon}&aqi=no"
#     try:
#         resp = requests.get(url)
#         resp.raise_for_status()
#         return resp.json()
#     except Exception as e:
#         st.error(f"API error at ({lat}, {lon}): {e}")
#         return None


# def main():
#     st.set_page_config(page_title="India Weather Dashboard", layout="wide")

#     # Simple CSS styling
#     st.markdown(
#         """
#         <style>
#             .main {background-color: #f7f7f7;}
#             h1, h2, h3 {color: #1E3A8A;}
#             .stDataFrame {background: white;}
#         </style>
#         """,
#         unsafe_allow_html=True,
#     )

#     st.title("Live Weather Dashboard — Indian States")
#     st.caption("Real-time weather updates for all Indian states using WeatherAPI.com")

#     # Sidebar controls
#     st.sidebar.header("Controls")
#     fetch_button = st.sidebar.button("Fetch Latest Weather")

#     show_bar_chart = st.sidebar.checkbox("Bar Chart (Temperature)", value=False)
#     show_pie_chart = st.sidebar.checkbox("Pie Chart (Conditions)", value=False)
#     show_line_chart = st.sidebar.checkbox("Line Chart (Temperature Trend)", value=False)
#     show_heatmap = st.sidebar.checkbox("Heatmap (Temperature)", value=False)

#     unit = st.sidebar.radio("Temperature Unit", ["Celsius (°C)", "Fahrenheit (°F)"])
#     auto_refresh = st.sidebar.checkbox("Auto-refresh every 10 minutes", value=False)

#     # Load states and coordinates
#     with open(STATES_JSON_FILE) as f:
#         states_list = json.load(f)
#     with open(STATE_COORDINATES_FILE) as f:
#         STATE_COORDS = json.load(f)

#     abbr_to_name = {s["abbreviation"]: s["name"] for s in states_list}

#     if "weather_data" not in st.session_state:
#         st.session_state.weather_data = None
#         st.session_state.last_updated = None

#     # Fetch data
#     if fetch_button or st.session_state.weather_data is None:
#         results = []
#         bar = st.progress(0)
#         total = len(STATE_COORDS)

#         for i, (abbr, coords) in enumerate(STATE_COORDS.items()):
#             lat, lon = coords
#             data = fetch_weather(lat, lon)
#             if data and "current" in data:
#                 c = data["current"]
#                 results.append({
#                     "State": abbr_to_name.get(abbr, abbr),
#                     "Temperature (°C)": c.get("temp_c"),
#                     "Temperature (°F)": c.get("temp_f"),
#                     "Humidity (%)": c.get("humidity"),
#                     "Wind Speed (kph)": c.get("wind_kph"),
#                     "Condition": c.get("condition", {}).get("text", "N/A"),
#                     "Lat": lat,
#                     "Lon": lon,
#                 })
#             else:
#                 st.warning(f"Could not fetch data for {abbr}")
#             bar.progress((i + 1) / total)
#             time.sleep(0.6)

#         st.session_state.weather_data = pd.DataFrame(results)
#         st.session_state.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         st.success(f"Weather updated for {len(results)} states/UTs.")

#     df = st.session_state.weather_data

#     if st.session_state.last_updated:
#         st.info(f"Last Updated: {st.session_state.last_updated}")

#     if df is not None:
#         # Choose unit for display
#         temp_col = "Temperature (°C)" if unit.startswith("Celsius") else "Temperature (°F)"
#         st.dataframe(
#             df[["State", temp_col, "Humidity (%)", "Wind Speed (kph)", "Condition"]]
#             .style.format({
#                 temp_col: "{:.1f}",
#                 "Humidity (%)": "{}%",
#                 "Wind Speed (kph)": "{:.1f}"
#             }),
#             use_container_width=True
#         )

#         # Search filter
#         search = st.text_input("Search a State:")
#         if search:
#             filt = df[df["State"].str.contains(search, case=False)]
#             st.write(f"Results for {search}:")
#             st.table(filt)

#         # KPIs
#         st.markdown("### Key Weather Stats")
#         k1, k2, k3 = st.columns(3)
#         k4, k5, k6 = st.columns(3)

#         k1.metric("Total States/UTs", len(df))
#         k2.metric(f"Avg Temp ({'°C' if 'C' in temp_col else '°F'})",
#                   f"{df[temp_col].mean():.2f}")
#         k3.metric("Avg Humidity", f"{df['Humidity (%)'].mean():.2f}%")
#         k4.metric("Avg Wind Speed (kph)", f"{df['Wind Speed (kph)'].mean():.2f}")
#         k5.metric("Max Wind Speed (kph)", f"{df['Wind Speed (kph)'].max():.2f}")
#         k6.metric(f"Min Temp ({'°C' if 'C' in temp_col else '°F'})",
#                   f"{df[temp_col].min():.2f}")

#         # Charts
#         if show_bar_chart:
#             st.subheader("Temperature by State")
#             st.bar_chart(df.set_index("State")[temp_col])

#         if show_pie_chart:
#             st.subheader("Weather Conditions Distribution")
#             cond = df["Condition"].value_counts()
#             fig, ax = plt.subplots()
#             cond.plot.pie(autopct="%1.1f%%", ax=ax, figsize=(6,6))
#             ax.set_ylabel("")
#             st.pyplot(fig)

#         if show_line_chart:
#             st.subheader("Temperature Trend (Sorted by State)")
#             st.line_chart(df.sort_values("State").set_index("State")[temp_col])

#         if show_heatmap:
#             st.subheader("Temperature Heatmap")
#             st.map(df.rename(columns={"Lat": "latitude", "Lon": "longitude"}),
#                    size=0.001, color="Temperature (°C)")

#         # Top wind speeds
#         st.markdown("---")
#         st.subheader("Top 5 States/UTs by Wind Speed")
#         c1, c2 = st.columns(2)
#         with c1:
#             st.write("Highest Wind Speeds (kph)")
#             st.table(df.nlargest(5, "Wind Speed (kph)")[["State", "Wind Speed (kph)"]])
#         with c2:
#             st.write("Lowest Wind Speeds (kph)")
#             st.table(df.nsmallest(5, "Wind Speed (kph)")[["State", "Wind Speed (kph)"]])

#         # Download CSV
#         st.download_button(
#             "Download Data as CSV",
#             data=df.to_csv(index=False),
#             file_name="india_weather.csv",
#             mime="text/csv",
#         )

#     if auto_refresh:
#         st.experimental_rerun()


# if __name__ == "__main__":
#     main()




# import requests
# import pandas as pd
# import streamlit as st
# import time
# import json
# import matplotlib.pyplot as plt
# from datetime import datetime

# API_KEY = "6ea1df8523514452a5671306250808"  # replace with your key
# STATES_JSON_FILE = "india_states.json"
# STATE_COORDINATES_FILE = "india_coordinates.json"
# STATE_CITIES_FILE = "india_state_cities.json"

# def fetch_weather(lat, lon):
#     url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={lat},{lon}&aqi=no"
#     try:
#         r = requests.get(url, timeout=10)
#         r.raise_for_status()
#         return r.json()
#     except Exception as e:
#         st.error(f"API error ({lat},{lon}): {e}")
#         return None

# def fetch_city_weather(city_list):
#     results = []
#     bar = st.progress(0)
#     for i, cty in enumerate(city_list):
#         data = fetch_weather(cty["lat"], cty["lon"])
#         if data and "current" in data:
#             c = data["current"]
#             results.append({
#                 "City": cty["city"],
#                 "Temperature (°C)": c["temp_c"],
#                 "Temperature (°F)": c["temp_f"],
#                 "Humidity (%)": c["humidity"],
#                 "Wind Speed (kph)": c["wind_kph"],
#                 "Condition": c["condition"]["text"],
#                 "Lat": cty["lat"],
#                 "Lon": cty["lon"],
#             })
#         bar.progress((i + 1) / len(city_list))
#         time.sleep(0.3)
#     return pd.DataFrame(results)

# def main():
#     st.set_page_config(page_title="India Weather Dashboard", layout="wide")
#     st.title("Live Weather Dashboard — Indian States & Cities")
#     st.caption("Real-time weather updates using WeatherAPI.com")

#     # Sidebar controls
#     st.sidebar.header("Controls")
#     mode = st.sidebar.radio("View Mode", ["All States", "Cities of a State"])
#     unit = st.sidebar.radio("Temperature Unit", ["Celsius (°C)", "Fahrenheit (°F)"])
#     auto_refresh = st.sidebar.checkbox("Auto-refresh every 10 minutes", value=False)

#     # Load base data
#     with open(STATES_JSON_FILE) as f:
#         states_list = json.load(f)
#     with open(STATE_COORDINATES_FILE) as f:
#         STATE_COORDS = json.load(f)
#     with open(STATE_CITIES_FILE) as f:
#         STATE_CITIES = json.load(f)

#     abbr_to_name = {s["abbreviation"]: s["name"] for s in states_list}

#     # ---------------- Mode 1: All States ----------------
#     if mode == "All States":
#         fetch_button = st.sidebar.button("Fetch Latest Weather")
#         if "weather_data" not in st.session_state:
#             st.session_state.weather_data = None
#             st.session_state.last_updated = None

#         if fetch_button or st.session_state.weather_data is None:
#             results = []
#             bar = st.progress(0)
#             for i, (abbr, coords) in enumerate(STATE_COORDS.items()):
#                 lat, lon = coords
#                 data = fetch_weather(lat, lon)
#                 if data and "current" in data:
#                     c = data["current"]
#                     results.append({
#                         "State": abbr_to_name.get(abbr, abbr),
#                         "Temperature (°C)": c["temp_c"],
#                         "Temperature (°F)": c["temp_f"],
#                         "Humidity (%)": c["humidity"],
#                         "Wind Speed (kph)": c["wind_kph"],
#                         "Condition": c["condition"]["text"],
#                         "Lat": lat,
#                         "Lon": lon,
#                     })
#                 bar.progress((i + 1) / len(STATE_COORDS))
#                 time.sleep(0.6)
#             st.session_state.weather_data = pd.DataFrame(results)
#             st.session_state.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#             st.success("Weather updated.")

#         df = st.session_state.weather_data
#         if df is not None:
#             temp_col = "Temperature (°C)" if unit.startswith("C") else "Temperature (°F)"
#             st.dataframe(df[["State", temp_col, "Humidity (%)", "Wind Speed (kph)", "Condition"]],
#                          use_container_width=True)
#     # ---------------- Mode 2: Cities of a State ----------------
#     else:
#         state_name = st.sidebar.selectbox("Select a State", sorted(STATE_CITIES.keys()))
#         if st.sidebar.button("Fetch City Weather"):
#             city_df = fetch_city_weather(STATE_CITIES[state_name])
#             st.session_state.city_df = city_df
#             st.session_state.city_last = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#         if "city_df" in st.session_state:
#             temp_col = "Temperature (°C)" if unit.startswith("C") else "Temperature (°F)"
#             st.info(f"{state_name} — Last Updated: {st.session_state.city_last}")
#             st.dataframe(st.session_state.city_df[["City", temp_col, "Humidity (%)",
#                                                    "Wind Speed (kph)", "Condition"]],
#                          use_container_width=True)

#     if auto_refresh:
#         st.experimental_rerun()

# if __name__ == "__main__":
#     main()




# import requests
# import pandas as pd
# import streamlit as st
# import time
# import json
# import matplotlib.pyplot as plt
# from datetime import datetime

# API_KEY = "6ea1df8523514452a5671306250808"  # Replace with your WeatherAPI.com key
# STATE_CITY_COORD_FILE = "india_state_cities.json"  # Merged JSON file


# def fetch_weather(lat, lon):
#     """Fetch current weather data for given coordinates."""
#     url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={lat},{lon}&aqi=no"
#     try:
#         resp = requests.get(url)
#         resp.raise_for_status()
#         return resp.json()
#     except Exception as e:
#         st.error(f"API error at ({lat}, {lon}): {e}")
#         return None


# def fetch_city_weather(city_dict):
#     """Fetch weather for all cities in a state."""
#     results = []
#     for city_name, coords in city_dict.items():
#         lat, lon = coords  # unpack list [lat, lon]
#         data = fetch_weather(lat, lon)
#         if data and "current" in data:
#             c = data["current"]
#             results.append({
#                 "City": city_name,
#                 "Temperature (°C)": c.get("temp_c"),
#                 "Temperature (°F)": c.get("temp_f"),
#                 "Humidity (%)": c.get("humidity"),
#                 "Wind Speed (kph)": c.get("wind_kph"),
#                 "Condition": c.get("condition", {}).get("text", "N/A"),
#                 "Lat": lat,
#                 "Lon": lon
#             })
#         else:
#             st.warning(f"Could not fetch data for {city_name}")
#         time.sleep(0.6)
#     return pd.DataFrame(results)


# def main():
#     st.set_page_config(page_title="India Weather Dashboard", layout="wide")
#     st.title("Live Weather Dashboard — Indian States & Cities")
#     st.caption("Real-time weather updates using WeatherAPI.com")

#     # Load state-city coordinates
#     with open(STATE_CITY_COORD_FILE) as f:
#         STATE_CITIES = json.load(f)

#     unit = st.sidebar.radio("Temperature Unit", ["Celsius (°C)", "Fahrenheit (°F)"])
#     auto_refresh = st.sidebar.checkbox("Auto-refresh every 10 minutes", value=False)

#     # State selection
#     state_name = st.sidebar.selectbox("Select State", list(STATE_CITIES.keys()))
#     city_options = list(STATE_CITIES[state_name].keys())
#     city_name = st.sidebar.selectbox("Select City (Optional)", ["All Cities"] + city_options)

#     if st.sidebar.button("Fetch Weather"):
#         if city_name == "All Cities":
#             df = fetch_city_weather(STATE_CITIES[state_name])
#         else:
#             coords = STATE_CITIES[state_name][city_name]
#             data = fetch_weather(coords[0], coords[1])
#             if data and "current" in data:
#                 c = data["current"]
#                 df = pd.DataFrame([{
#                     "City": city_name,
#                     "Temperature (°C)": c.get("temp_c"),
#                     "Temperature (°F)": c.get("temp_f"),
#                     "Humidity (%)": c.get("humidity"),
#                     "Wind Speed (kph)": c.get("wind_kph"),
#                     "Condition": c.get("condition", {}).get("text", "N/A"),
#                     "Lat": coords[0],
#                     "Lon": coords[1]
#                 }])
#             else:
#                 st.error(f"Could not fetch data for {city_name}")
#                 return

#         temp_col = "Temperature (°C)" if unit.startswith("Celsius") else "Temperature (°F)"
#         st.dataframe(
#             df[["City", temp_col, "Humidity (%)", "Wind Speed (kph)", "Condition"]]
#             .style.format({
#                 temp_col: "{:.1f}",
#                 "Humidity (%)": "{}%",
#                 "Wind Speed (kph)": "{:.1f}"
#             }),
#             use_container_width=True
#         )

#         # KPIs
#         st.markdown("### Key Weather Stats")
#         k1, k2, k3 = st.columns(3)
#         k1.metric("Total Cities", len(df))
#         k2.metric(f"Avg Temp ({'°C' if 'C' in temp_col else '°F'})", f"{df[temp_col].mean():.2f}")
#         k3.metric("Avg Humidity", f"{df['Humidity (%)'].mean():.2f}%")

#         # Charts
#         if st.sidebar.checkbox("Bar Chart (Temperature)"):
#             st.subheader("Temperature by City")
#             st.bar_chart(df.set_index("City")[temp_col])

#         if st.sidebar.checkbox("Pie Chart (Conditions)"):
#             st.subheader("Weather Conditions Distribution")
#             cond = df["Condition"].value_counts()
#             fig, ax = plt.subplots()
#             cond.plot.pie(autopct="%1.1f%%", ax=ax, figsize=(6,6))
#             ax.set_ylabel("")
#             st.pyplot(fig)

#         if st.sidebar.checkbox("Line Chart (Temperature Trend)"):
#             st.subheader("Temperature Trend (Sorted by City)")
#             st.line_chart(df.sort_values("City").set_index("City")[temp_col])

#         if st.sidebar.checkbox("Heatmap (Temperature)"):
#             st.subheader("Temperature Heatmap")
#             st.map(df.rename(columns={"Lat": "latitude", "Lon": "longitude"}), size=0.001)

#         # Download CSV
#         st.download_button(
#             "Download Data as CSV",
#             data=df.to_csv(index=False),
#             file_name=f"{state_name}_weather.csv",
#             mime="text/csv",
#         )

#     if auto_refresh:
#         st.experimental_rerun()


# if __name__ == "__main__":
#     main()



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
    st.caption("Real-time weather updates using WeatherAPI.com")

    # Load state-city coordinates
    with open(STATE_CITY_COORD_FILE) as f:
        STATE_CITIES = json.load(f)

    unit = st.sidebar.radio("Temperature Unit", ["Celsius (°C)", "Fahrenheit (°F)"])
    auto_refresh = st.sidebar.checkbox("Auto-refresh every 10 minutes", value=False)

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
