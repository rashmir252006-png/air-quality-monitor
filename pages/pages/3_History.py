import pandas as pd
import streamlit as st
from database import get_history, get_distinct_cities, get_city_history
from utils import require_login, render_top_nav

st.set_page_config(page_title="Search History", page_icon="💾", layout="wide")
require_login(st)
render_top_nav(st, current="History")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg-deep: #101A2E;
    --bg-twilight: #1B2C4D;
    --cloud: #EDEFF5;
    --mist: #8C97AE;
    --cyan: #4FD6C4;
}

.stApp {
    background: radial-gradient(circle at 15% -10%, var(--bg-twilight) 0%, var(--bg-deep) 55%, #0A1220 100%);
}
#MainMenu, footer, header { visibility: hidden; }
html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: var(--cloud); }

.page-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    letter-spacing: 0.18em;
    color: var(--cyan);
    text-transform: uppercase;
    margin-bottom: 0.6rem;
}
.page-title {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 2.1rem;
    color: var(--cloud);
    margin-bottom: 1.6rem;
}
.section-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--mist);
    margin: 1.8rem 0 0.7rem 0;
}

.st-key-table_card, .st-key-trend_card {
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 16px;
    padding: 1.4rem 1.5rem;
}

[data-testid="stDataFrame"] {
    border-radius: 10px;
    overflow: hidden;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="page-eyebrow">Global Air Quality Monitor</div>', unsafe_allow_html=True)
st.markdown('<div class="page-title">💾 Your Search History</div>', unsafe_allow_html=True)

COLUMNS = ["id", "user_email", "city", "aqi", "co", "no2", "o3", "so2",
           "pm2_5", "pm10", "nh3", "searched_at"]

rows = get_history(st.session_state.user_email)

if not rows:
    st.info("No searches yet. Go to the Search page to look up a city's air quality!")
else:
    df = pd.DataFrame(rows, columns=COLUMNS)

    st.markdown('<div class="section-label">All Searches</div>', unsafe_allow_html=True)
    with st.container(key="table_card"):
        st.dataframe(
            df[["city", "aqi", "pm2_5", "pm10", "co", "no2", "o3", "so2", "nh3", "searched_at"]],
            use_container_width=True,
            hide_index=True,
        )

    st.markdown('<div class="section-label">AQI Trend for a City</div>', unsafe_allow_html=True)
    with st.container(key="trend_card"):
        cities = get_distinct_cities(st.session_state.user_email)
        selected_city = st.selectbox("Pick a city", cities)

        if selected_city:
            city_rows = get_city_history(st.session_state.user_email, selected_city)
            city_df = pd.DataFrame(city_rows, columns=COLUMNS)
            city_df["searched_at"] = pd.to_datetime(city_df["searched_at"])
            city_df = city_df.set_index("searched_at")

            if len(city_df) < 2:
                st.info(f"Only one search recorded for {selected_city} so far — search again later to see a trend.")
            else:
                st.line_chart(city_df["aqi"])

            st.caption("Pollutant trend (μg/m³)")
            st.line_chart(city_df[["pm2_5", "pm10", "co", "no2", "o3", "so2", "nh3"]])
