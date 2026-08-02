import streamlit as st
from api import get_air_quality
from database import save_search
from utils import get_aqi_label, require_login, render_top_nav

st.set_page_config(page_title="Compare Cities", page_icon="📊", layout="wide")
require_login(st)
render_top_nav(st, current="Compare")

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
    margin-bottom: 0.4rem;
}
.page-tagline {
    color: var(--mist);
    margin-bottom: 1.6rem;
}

.st-key-compare_card {
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

/* 👇 Compare button — same orange-red style as Search button */
.st-key-compare_submit_btn .stButton button {
    background: linear-gradient(90deg, #F5924A, #EF5757) !important;
    color: #1a0f0a !important;
}
.st-key-compare_submit_btn .stButton button:hover {
    box-shadow: 0 8px 22px rgba(239, 87, 87, 0.3) !important;
}

.compare-card {
    border-radius: 16px;
    padding: 1.6rem 1.6rem;
    background: var(--aqi-bg, rgba(79,214,196,0.08));
    border: 1px solid var(--aqi-border, rgba(79,214,196,0.35));
    text-align: center;
    height: 100%;
}
.compare-city {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 1.3rem;
    color: var(--cloud);
    margin-bottom: 0.2rem;
}
.compare-aqi {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    font-size: 1.05rem;
    color: var(--aqi-color, var(--cyan));
    margin-bottom: 1rem;
}
.compare-stats {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.6rem;
    text-align: left;
}
.compare-stat {
    background: rgba(255,255,255,0.04);
    border-radius: 8px;
    padding: 0.5rem 0.7rem;
}
.compare-stat-name {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    color: var(--mist);
    text-transform: uppercase;
}
.compare-stat-value {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    font-size: 0.95rem;
    color: var(--cloud);
}

.winner-banner {
    margin-top: 1.4rem;
    text-align: center;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    font-size: 1.05rem;
    color: var(--cyan);
    background: rgba(79,214,196,0.08);
    border: 1px solid rgba(79,214,196,0.3);
    border-radius: 12px;
    padding: 0.9rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="page-eyebrow">Global Air Quality Monitor</div>', unsafe_allow_html=True)
st.markdown('<div class="page-title">📊 Compare Air Quality</div>', unsafe_allow_html=True)
st.markdown('<div class="page-tagline">See AQI and pollutants for two cities, side by side.</div>', unsafe_allow_html=True)

AQI_COLORS = {
    1: ("#4ADE80", "rgba(74,222,128,0.10)", "rgba(74,222,128,0.35)"),
    2: ("#A8D861", "rgba(168,216,97,0.10)", "rgba(168,216,97,0.35)"),
    3: ("#F5D547", "rgba(245,213,71,0.10)", "rgba(245,213,71,0.35)"),
    4: ("#F5924A", "rgba(245,146,74,0.10)", "rgba(245,146,74,0.35)"),
    5: ("#EF5757", "rgba(239,87,87,0.10)", "rgba(239,87,87,0.35)"),
}

with st.container(key="compare_card"):
    col1, col2 = st.columns(2)
    with col1:
        city1 = st.text_input("City 1", placeholder="e.g. Chennai")
    with col2:
        city2 = st.text_input("City 2", placeholder="e.g. Delhi")
    compare_clicked = st.button("Compare", key="compare_submit_btn")

if compare_clicked:
    if not city1.strip() or not city2.strip():
        st.warning("Please enter both city names.")
    else:
        with st.spinner("Fetching data for both cities..."):
            data1 = get_air_quality(city1.strip())
            data2 = get_air_quality(city2.strip())

        error = False
        for d in (data1, data2):
            if "error" in d:
                st.error(d["error"])
                error = True

        if not error:
            save_search(st.session_state.user_email, data1)
            save_search(st.session_state.user_email, data2)

            c1, c2 = st.columns(2)
            for col, data in zip((c1, c2), (data1, data2)):
                label, _ = get_aqi_label(data["aqi"])
                color, bg, border = AQI_COLORS.get(
                    data["aqi"], ("#4FD6C4", "rgba(79,214,196,0.08)", "rgba(79,214,196,0.35)")
                )
                with col:
                    st.markdown(f"""
                        <div class="compare-card" style="--aqi-bg:{bg}; --aqi-border:{border};">
                            <div class="compare-city">{data['city']}</div>
                            <div class="compare-aqi" style="--aqi-color:{color};">AQI {data['aqi']} — {label}</div>
                            <div class="compare-stats">
                                <div class="compare-stat">
                                    <div class="compare-stat-name">PM2.5</div>
                                    <div class="compare-stat-value">{data['pm2_5']:.2f}</div>
                                </div>
                                <div class="compare-stat">
                                    <div class="compare-stat-name">PM10</div>
                                    <div class="compare-stat-value">{data['pm10']:.2f}</div>
                                </div>
                                <div class="compare-stat">
                                    <div class="compare-stat-name">CO</div>
                                    <div class="compare-stat-value">{data['co']:.2f}</div>
                                </div>
                                <div class="compare-stat">
                                    <div class="compare-stat-name">NO2</div>
                                    <div class="compare-stat-value">{data['no2']:.2f}</div>
                                </div>
                                <div class="compare-stat">
                                    <div class="compare-stat-name">O3</div>
                                    <div class="compare-stat-value">{data['o3']:.2f}</div>
                                </div>
                                <div class="compare-stat">
                                    <div class="compare-stat-name">SO2</div>
                                    <div class="compare-stat-value">{data['so2']:.2f}</div>
                                </div>
                                <div class="compare-stat">
                                    <div class="compare-stat-name">NH3</div>
                                    <div class="compare-stat-value">{data['nh3']:.2f}</div>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

            better = data1["city"] if data1["aqi"] < data2["aqi"] else (
                data2["city"] if data2["aqi"] < data1["aqi"] else None
            )
            if better:
                st.markdown(f'<div class="winner-banner">🏆 {better} has better air quality right now.</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="winner-banner">Both cities currently have the same AQI level.</div>', unsafe_allow_html=True)
