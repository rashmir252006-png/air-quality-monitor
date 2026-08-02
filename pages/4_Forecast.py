import numpy as np
import pandas as pd
import streamlit as st
from sklearn.linear_model import LinearRegression

from database import get_distinct_cities, get_city_history
from utils import get_aqi_label, require_login, render_top_nav

st.set_page_config(page_title="AQI Forecast", page_icon="🤖", layout="wide")
require_login(st)
render_top_nav(st, current="Forecast")

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
    margin-bottom: 0.5rem;
}
.page-tagline {
    color: var(--mist);
    max-width: 42rem;
    line-height: 1.55;
    margin-bottom: 1.8rem;
}

.st-key-controls_card {
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1.6rem;
}

.st-key-chart_card {
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1.6rem;
}

.forecast-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,0.09);
    border-left: 3px solid var(--row-accent, var(--cyan));
    border-radius: 10px;
    padding: 0.7rem 1.1rem;
    margin-bottom: 0.5rem;
}
.forecast-date {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    color: var(--mist);
}
.forecast-aqi {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    font-size: 0.95rem;
    color: var(--cloud);
}
.forecast-label {
    font-weight: 600;
}

.model-note {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: var(--mist);
    margin-top: 1rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="page-eyebrow">Global Air Quality Monitor</div>', unsafe_allow_html=True)
st.markdown('<div class="page-title">🤖 AQI Forecast</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="page-tagline">A simple linear regression trained on your own saved search '
    'history projects the AQI trend forward. The more searches you save for a city — ideally '
    'across several days — the more meaningful the forecast becomes.</div>',
    unsafe_allow_html=True,
)

AQI_COLORS = {
    1: "#4ADE80", 2: "#A8D861", 3: "#F5D547", 4: "#F5924A", 5: "#EF5757",
}

cities = get_distinct_cities(st.session_state.user_email)

if not cities:
    st.info("No history yet. Search a few cities first (ideally on different days), then come back here.")
else:
    with st.container(key="controls_card"):
        c1, c2 = st.columns([2, 1])
        with c1:
            city = st.selectbox("Pick a city to forecast", cities)
        with c2:
            days_ahead = st.slider("Days to forecast ahead", 1, 7, 3)

    COLUMNS = ["id", "user_email", "city", "aqi", "co", "no2", "o3", "so2",
               "pm2_5", "pm10", "nh3", "searched_at"]
    rows = get_city_history(st.session_state.user_email, city)
    df = pd.DataFrame(rows, columns=COLUMNS)
    df["searched_at"] = pd.to_datetime(df["searched_at"])

    if len(df) < 3:
        st.warning(
            f"Only {len(df)} data point(s) for {city}. Need at least 3 searches "
            "(ideally on different days) to build a meaningful forecast."
        )
    else:
        t0 = df["searched_at"].min()
        df["days_elapsed"] = (df["searched_at"] - t0).dt.total_seconds() / 86400.0

        X = df[["days_elapsed"]].values
        y = df["aqi"].values

        model = LinearRegression()
        model.fit(X, y)

        last_day = df["days_elapsed"].max()
        future_days = np.arange(1, days_ahead + 1) + last_day
        preds = model.predict(future_days.reshape(-1, 1))
        preds = np.clip(np.round(preds), 1, 5)

        future_dates = [t0 + pd.Timedelta(days=d) for d in future_days]
        forecast_df = pd.DataFrame({"AQI": preds}, index=pd.Index(future_dates, name="date"))
        history_df = df.set_index("searched_at")[["aqi"]].rename(columns={"aqi": "AQI"})
        combined = pd.concat([history_df, forecast_df])

        with st.container(key="chart_card"):
            st.markdown(f'<div class="model-note">HISTORY + {days_ahead}-DAY PROJECTION — {city.upper()}</div>', unsafe_allow_html=True)
            st.line_chart(combined)

        st.markdown(f"###### Forecast for {city}")
        for date, row in forecast_df.iterrows():
            aqi_val = int(row["AQI"])
            label, _ = get_aqi_label(aqi_val)
            color = AQI_COLORS.get(aqi_val, "#4FD6C4")
            st.markdown(f"""
                <div class="forecast-row" style="--row-accent:{color};">
                    <span class="forecast-date">{date.strftime('%Y-%m-%d')}</span>
                    <span class="forecast-aqi">AQI {aqi_val} &nbsp;
                        <span class="forecast-label" style="color:{color};">{label}</span>
                    </span>
                </div>
            """, unsafe_allow_html=True)

        st.markdown(
            '<div class="model-note">⚠️ Simple linear trend model for demonstration purposes, '
            'not a scientific air-quality forecast.</div>',
            unsafe_allow_html=True,
        )
