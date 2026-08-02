def get_aqi_label(aqi):
    labels = {
        1: ("Good", "Air quality is satisfactory."),
        2: ("Fair", "Air quality is acceptable."),
        3: ("Moderate", "Sensitive groups may be affected."),
        4: ("Poor", "Everyone may start to feel effects."),
        5: ("Very Poor", "Health warning: serious risk to everyone."),
    }
    return labels.get(aqi, ("Unknown", "No data available."))


def require_login(st):
    if not st.session_state.get("logged_in", False):
        st.warning("Please log in first from the Home page.")
        st.stop()


def hide_sidebar(st):
    st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    [data-testid="stSidebarCollapsedControl"] { display: none; }
    </style>
    """, unsafe_allow_html=True)


def render_top_nav(st, current="Home"):
    hide_sidebar(st)

    pages = {
        "Home": "app.py",
        "Search": "pages/1_Search.py",
        "Compare": "pages/2_Compare.py",
        "History": "pages/3_History.py",
        "Forecast": "pages/4_Forecast.py",
    }

    cols = st.columns(len(pages) + 1)

    for i, (name, path) in enumerate(pages.items()):
        with cols[i]:
            btn_type = "primary" if name == current else "secondary"
            if st.button(name, key=f"nav_{name}", use_container_width=True, type=btn_type):
                st.switch_page(path)

    with cols[-1]:
        if st.session_state.get("logged_in", False):
            if st.button("Logout", key="nav_logout", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.user_email = None
                st.switch_page("app.py")