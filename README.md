# 🌍 Global Air Quality Monitor

A web application that tracks real-time Air Quality Index (AQI) for any city, compares air quality across cities, keeps a personal search history, and uses Machine Learning to forecast future AQI trends.

Built as a Data Science + Web Development project combining a live weather API, a SQLite database, and a scikit-learn regression model.

---

## ✨ Features

- 🔐 **Secure Login/Signup** — accounts protected with SHA-256 password hashing
- 🔍 **Live AQI Search** — real-time air quality data for any city worldwide (via OpenWeatherMap API)
- 📊 **City Comparison** — compare AQI and pollutant levels between two cities side by side
- 💾 **Search History** — every search is saved per user and viewable anytime
- 🤖 **ML-Powered Forecast** — a Linear Regression model (scikit-learn) trained on your own search history predicts AQI for the next few days
- 🎨 **Custom Dark Theme UI** — color-coded AQI cards, emoji indicators, and plain-language health advice so results are easy to understand at a glance

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python |
| Web Framework | Streamlit |
| Database | SQLite |
| Machine Learning | scikit-learn (Linear Regression) |
| Data Handling | Pandas, NumPy |
| External API | OpenWeatherMap (Geocoding + Air Pollution API) |
| Charts | Streamlit native charts (`st.line_chart`) |

---

## 📁 Project Structure

```
Global_Air_Quality_Monitor/
│
├── app.py                 # Home page — login/signup, dashboard landing
├── api.py                 # OpenWeatherMap API integration
├── database.py             # SQLite setup, user auth, history storage
├── utils.py                 # Shared helpers (AQI labels, login guard, top nav)
├── requirements.txt
│
├── pages/
│   ├── 1_Search.py         # Live city search
│   ├── 2_Compare.py        # Two-city comparison
│   ├── 3_History.py        # Past search history + trend charts
│   └── 4_Forecast.py       # ML-based AQI forecast
│
└── database.db              # SQLite database (auto-created on first run)
```

---

## ⚙️ Setup & Installation

1. **Clone or download this project**, then open the folder in a terminal.

2. **Create a virtual environment** (recommended):
   ```
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # Mac/Linux
   ```

3. **Install dependencies**:
   ```
   pip install streamlit pandas numpy matplotlib scikit-learn requests
   ```

4. **Add your OpenWeatherMap API key**
   Get a free key at [openweathermap.org](https://openweathermap.org), then update `API_KEY` in `api.py`.
   > Note: new API keys can take up to a couple of hours to activate.

5. **Run the app**:
   ```
   streamlit run app.py
   ```

6. Open the app in your browser at `http://localhost:8501`, sign up for an account, and start searching!

---

## 🤖 How the Forecast Works

The Forecast page trains a simple **Linear Regression** model on a user's own saved AQI history for a chosen city (time elapsed vs. AQI value), then projects the trend forward by a few days. It's a lightweight, explainable statistical model — not an official weather-service forecast — intended to demonstrate applying ML to real, self-collected data.

More history for a city (ideally spread across different days) produces a more meaningful forecast.

---

## 🔒 Security Notes

- Passwords are never stored in plain text — they are hashed with SHA-256 before being saved.
- Each user's search history is private and tied to their account.
- API keys should be kept out of public repositories in a real deployment (e.g. via environment variables).

---

## 📌 Possible Future Improvements

- Switch to bcrypt/argon2 for password hashing
- Add email verification on signup
- Deploy to Streamlit Community Cloud for public access
- Add more advanced forecasting models (e.g. moving average, ARIMA)
- Add downloadable PDF/CSV reports of search history

---

## 👤 Author

Built as a personal Data Science + Web Development learning project.
