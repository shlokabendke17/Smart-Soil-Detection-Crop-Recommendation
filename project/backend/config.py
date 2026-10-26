"""
config.py  —  Configuration for Smart Soil Detection System backend.

WEATHER API SETUP:
  1. Go to https://www.weatherapi.com/signup.aspx  (free forever tier)
  2. Copy your API key from the dashboard
  3. Replace "YOUR_FREE_API_KEY_HERE" below with your key
  4. Restart the Flask server

Alternatively, enter the key in the Settings panel inside the web UI —
it will be stored in your browser and sent with every weather request.
"""

# WeatherAPI.com key (free tier: 1 million calls/month)
WEATHER_API_KEY = "b56e1d9633a345b4a13111523262708"
