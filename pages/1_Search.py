import streamlit as st
from api import get_air_quality
from database import save_search
from utils import get_aqi_label, require_login, render_top_nav

st.set_page_config(page_title="Search AQI", page_icon="🔍", layout="wide")
require_login(st)
render_top_nav(st, current="Search")

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
.st-key-search_card {
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 16px;
    padding: 1.6rem 1.8rem;
    margin-bottom: 1.8rem;
}
.stTextInput input {
    background: rgba(255,255,255,0.045);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 9px;
    color: var(--cloud);
    padding: 0.65rem 0.8rem;
}
.aqi-result {
    border-radius: 16px;
    padding: 1.6rem 1.8rem;
    background: var(--aqi-bg, rgba(79,214,196,0.08));
    border: 1px solid var(--aqi-border, rgba(79,214,196,0.35));
    margin-bottom: 1.6rem;
}
.aqi-result-city {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    color: var(--mist);
    text-transform: uppercase;
    margin-bottom: 0.4rem;
}
.aqi-result-value {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 2.2rem;
    color: var(--cloud);
}
.aqi-result-label {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    font-size: 1.2rem;
    color: var(--aqi-color, var(--cyan));
}
.pollutant-tile {
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 12px;
    padding: 0.9rem 1rem;
    text-align: center;
}
.pollutant-name {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: var(--mist);
    text-transform: uppercase;
    margin-bottom: 0.3rem;
}
.pollutant-value {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    font-size: 1.1rem;
    color: var(--cloud);
}

.st-key-search_submit_btn .stButton button {
    background: linear-gradient(90deg, #F5924A, #EF5757) !important;
    color: #1a0f0a !important;
}
.st-key-search_submit_btn .stButton button:hover {
    box-shadow: 0 8px 22px rgba(239, 87, 87, 0.3) !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="page-eyebrow">Global Air Quality Monitor</div>', unsafe_allow_html=True)
st.markdown('<div class="page-title">🔍 Search Air Quality</div>', unsafe_allow_html=True)

AQI_COLORS = {
    1: ("#4ADE80", "rgba(74,222,128,0.10)", "rgba(74,222,128,0.35)"),
    2: ("#A8D861", "rgba(168,216,97,0.10)", "rgba(168,216,97,0.35)"),
    3: ("#F5D547", "rgba(245,213,71,0.10)", "rgba(245,213,71,0.35)"),
    4: ("#F5924A", "rgba(245,146,74,0.10)", "rgba(245,146,74,0.35)"),
    5: ("#EF5757", "rgba(239,87,87,0.10)", "rgba(239,87,87,0.35)"),
}

with st.container(key="search_card"):
    city = st.text_input("City", placeholder="e.g. Chennai")
    search_clicked = st.button("Search", key="search_submit_btn")

if search_clicked:
    if not city.strip():
        st.warning("Please enter a city name.")
    else:
        with st.spinner(f"Fetching air quality for {city}..."):
            data = get_air_quality(city.strip())

        if "error" in data:
            st.error(data["error"])
        else:
            label, _ = get_aqi_label(data["aqi"])
            color, bg, border = AQI_COLORS.get(data["aqi"], ("#4FD6C4", "rgba(79,214,196,0.08)", "rgba(79,214,196,0.35)"))
            save_search(st.session_state.user_email, data)

            st.markdown(f"""
                <div class="aqi-result" style="--aqi-bg:{bg}; --aqi-border:{border};">
                    <div class="aqi-result-city">{data['city']}</div>
                    <div class="aqi-result-value">AQI {data['aqi']}
                        &nbsp;<span class="aqi-result-label" style="--aqi-color:{color};">— {label}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("###### Pollutant Breakdown (μg/m³)")
            pollutants = [
                ("CO", data["co"]), ("NO2", data["no2"]), ("O3", data["o3"]),
                ("SO2", data["so2"]), ("PM2.5", data["pm2_5"]),
                ("PM10", data["pm10"]), ("NH3", data["nh3"]),
            ]
            cols = st.columns(4)
            for i, (name, value) in enumerate(pollutants):
                with cols[i % 4]:
                    st.markdown(f"""
                        <div class="pollutant-tile">
                            <div class="pollutant-name">{name}</div>
                            <div class="pollutant-value">{value:.2f}</div>
                        </div>
                    """, unsafe_allow_html=True)

            st.success("Saved to your history! Check the History page anytime.")
