import streamlit as st
from database import init_db, create_user, verify_user
from utils import render_top_nav

init_db()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = None

st.set_page_config(
    page_title="Global Air Quality Monitor",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed" if not st.session_state.logged_in else "auto",
)

# ------------------------------------------------------------------
# Theme: "Atmosphere" — dusk-indigo instrument panel with an AQI
# spectrum gauge as the signature element.
# ------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg-deep: #101A2E;
    --bg-mid: #16233D;
    --bg-twilight: #1B2C4D;
    --cloud: #EDEFF5;
    --mist: #8C97AE;
    --cyan: #4FD6C4;
    --aqi-good: #4ADE80;
    --aqi-fair: #A8D861;
    --aqi-moderate: #F5D547;
    --aqi-poor: #F5924A;
    --aqi-verypoor: #EF5757;
}

.stApp {
    background: radial-gradient(circle at 15% -10%, var(--bg-twilight) 0%, var(--bg-deep) 55%, #0A1220 100%);
}
#MainMenu, footer, header { visibility: hidden; }

html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: var(--cloud); }
h1, h2, h3 { font-family: 'Space Grotesk', sans-serif !important; letter-spacing: -0.01em; }

.st-key-hero_panel {
    padding: 2.5rem 1.5rem 1.5rem 0.5rem;
}
.hero-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    letter-spacing: 0.18em;
    color: var(--cyan);
    text-transform: uppercase;
    margin-bottom: 0.9rem;
}
.hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 2.6rem;
    line-height: 1.12;
    color: var(--cloud);
    margin-bottom: 0.9rem;
}
.hero-title span { color: var(--cyan); }
.hero-tagline {
    font-size: 1.02rem;
    color: var(--mist);
    max-width: 30rem;
    line-height: 1.55;
    margin-bottom: 2.6rem;
}

.gauge-wrap { max-width: 30rem; }
.gauge-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: var(--mist);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.6rem;
}
.gauge-track {
    position: relative;
    height: 10px;
    border-radius: 999px;
    background: linear-gradient(90deg,
        var(--aqi-good) 0%, var(--aqi-fair) 25%,
        var(--aqi-moderate) 50%, var(--aqi-poor) 75%, var(--aqi-verypoor) 100%);
    box-shadow: 0 0 18px rgba(79, 214, 196, 0.15);
    overflow: visible;
}
.gauge-marker {
    position: absolute;
    top: -5px;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: var(--cloud);
    box-shadow: 0 0 0 4px rgba(237, 239, 245, 0.15), 0 0 14px rgba(255,255,255,0.6);
    animation: drift 7s ease-in-out infinite;
}
@keyframes drift {
    0%   { left: 2%; }
    50%  { left: 92%; }
    100% { left: 2%; }
}
.gauge-ticks {
    display: flex;
    justify-content: space-between;
    margin-top: 0.7rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    color: var(--mist);
}

.st-key-auth_card {
    background: rgba(255, 255, 255, 0.035);
    border: 1px solid rgba(255, 255, 255, 0.09);
    backdrop-filter: blur(18px);
    border-radius: 18px;
    padding: 2.2rem 2.2rem 1.6rem 2.2rem;
    box-shadow: 0 20px 60px rgba(0,0,0,0.35);
}

.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: rgba(255,255,255,0.04);
    padding: 4px;
    border-radius: 10px;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    font-size: 0.92rem;
    color: var(--mist);
    border-radius: 8px;
    padding: 0.5rem 0;
}
.stTabs [aria-selected="true"] {
    background: rgba(79, 214, 196, 0.12) !important;
    color: var(--cyan) !important;
}
.stTabs [data-baseweb="tab-highlight"] { background: transparent; }
.stTabs [data-baseweb="tab-border"] { display: none; }

.stTextInput label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--mist) !important;
}
.stTextInput input {
    background: rgba(255,255,255,0.045);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 9px;
    color: var(--cloud);
    padding: 0.65rem 0.8rem;
}
.stTextInput input:focus {
    border-color: var(--cyan);
    box-shadow: 0 0 0 3px rgba(79, 214, 196, 0.15);
}

div[data-testid="stButton"] {
    width: 100%;
}
.stButton button {
    width: 100%;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    font-size: 1.1rem;
    background: linear-gradient(90deg, var(--cyan), #3fb8a8);
    color: #06231e;
    border: none;
    border-radius: 10px;
    padding: 1.1rem 0;
    margin-top: 0.8rem;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.stButton button:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 22px rgba(79, 214, 196, 0.25);
    color: #06231e;
}

.st-key-dash_header {
    padding: 1.5rem 0 0.5rem 0;
}
.dash-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    letter-spacing: 0.18em;
    color: var(--cyan);
    text-transform: uppercase;
    margin-bottom: 0.7rem;
}
.dash-title {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 2.3rem;
    color: var(--cloud);
    margin-bottom: 0.5rem;
}
.dash-tagline {
    font-size: 1rem;
    color: var(--mist);
    max-width: 34rem;
    line-height: 1.5;
}

.feature-card {
    border-radius: 14px;
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,0.09);
    border-top: 3px solid var(--accent, var(--cyan));
    padding: 1.4rem 1.3rem;
    height: 100%;
}
.feature-icon { font-size: 1.6rem; margin-bottom: 0.6rem; }
.feature-title {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    font-size: 1.05rem;
    color: var(--cloud);
    margin-bottom: 0.35rem;
}
.feature-desc {
    font-size: 0.85rem;
    color: var(--mist);
    line-height: 1.45;
}

.st-key-card_search .feature-card   { --accent: var(--aqi-good); }
.st-key-card_compare .feature-card  { --accent: var(--aqi-fair); }
.st-key-card_history .feature-card  { --accent: var(--aqi-moderate); }
.st-key-card_forecast .feature-card { --accent: var(--cyan); }

.dash-hint {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    color: var(--mist);
    margin: 1.6rem 0 0.8rem 0;
}
</style>
""", unsafe_allow_html=True)

if not st.session_state.logged_in:
    st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    [data-testid="stSidebarCollapsedControl"] { display: none; }
    </style>
    """, unsafe_allow_html=True)


if st.session_state.logged_in:
    render_top_nav(st, current="Home")

    with st.container(key="dash_header"):
        st.markdown('<div class="dash-eyebrow">Global Air Quality Monitor</div>', unsafe_allow_html=True)
        st.markdown('<div class="dash-title">🌍 Control Panel</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="dash-tagline">Real-time AQI tracking with Data Science powered '
            'predictions.</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="dash-hint">Pick a page above to get started</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4, gap="medium")

    with c1:
        with st.container(key="card_search"):
            st.markdown("""
                <div class="feature-card">
                    <div class="feature-icon">🔍</div>
                    <div class="feature-title">Search</div>
                    <div class="feature-desc">Live Air Quality Index for any city, anywhere.</div>
                </div>
            """, unsafe_allow_html=True)

    with c2:
        with st.container(key="card_compare"):
            st.markdown("""
                <div class="feature-card">
                    <div class="feature-icon">📊</div>
                    <div class="feature-title">Compare</div>
                    <div class="feature-desc">See AQI side by side between two cities.</div>
                </div>
            """, unsafe_allow_html=True)

    with c3:
        with st.container(key="card_history"):
            st.markdown("""
                <div class="feature-card">
                    <div class="feature-icon">💾</div>
                    <div class="feature-title">History</div>
                    <div class="feature-desc">Track and revisit all of your past searches.</div>
                </div>
            """, unsafe_allow_html=True)

    with c4:
        with st.container(key="card_forecast"):
            st.markdown("""
                <div class="feature-card">
                    <div class="feature-icon">🤖</div>
                    <div class="feature-title">Forecast</div>
                    <div class="feature-desc">ML-powered AQI predictions from your history.</div>
                </div>
            """, unsafe_allow_html=True)

else:
    left, right = st.columns([1, 1], gap="large")

    with left:
        with st.container(key="hero_panel"):
            st.markdown('<div class="hero-eyebrow">Global Air Quality Monitor</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="hero-title">Know the air<br>before you <span>breathe</span> it.</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                '<div class="hero-tagline">Real-time AQI for any city, side-by-side comparisons, '
                'and ML-powered forecasts built on your own search history.</div>',
                unsafe_allow_html=True,
            )
            st.markdown("""
                <div class="gauge-wrap">
                    <div class="gauge-label">Live AQI Spectrum</div>
                    <div class="gauge-track"><div class="gauge-marker"></div></div>
                    <div class="gauge-ticks">
                        <span>Good</span><span>Fair</span><span>Moderate</span>
                        <span>Poor</span><span>Very&nbsp;Poor</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    with right:
        with st.container(key="auth_card"):
            tab1, tab2 = st.tabs(["Login", "Sign Up"])

            with tab1:
                login_email = st.text_input("Email", key="login_email")
                login_password = st.text_input("Password", type="password", key="login_password")

                if st.button("Login", key="login_btn"):
                    if not login_email or not login_password:
                        st.warning("Please fill in both fields.")
                    elif verify_user(login_email, login_password):
                        st.session_state.logged_in = True
                        st.session_state.user_email = login_email
                        st.rerun()
                    else:
                        st.error("Invalid email or password.")

            with tab2:
                signup_email = st.text_input("Email", key="signup_email")
                signup_password = st.text_input("Password", type="password", key="signup_password")
                signup_confirm = st.text_input("Confirm Password", type="password", key="signup_confirm")

                if st.button("Create Account", key="signup_btn"):
                    if not signup_email or not signup_password:
                        st.warning("Please fill in all fields.")
                    elif signup_password != signup_confirm:
                        st.error("Passwords do not match.")
                    elif len(signup_password) < 6:
                        st.error("Password must be at least 6 characters.")
                    else:
                        success = create_user(signup_email, signup_password)
                        if success:
                            st.success("Account created! Please go to the Login tab.")
                        else:
                            st.error("This email is already registered.")