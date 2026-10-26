"""
risk_alerts.py
Rainfall / temperature / humidity based risk warnings.
"""


def compute_risk_alerts(temperature: float, humidity: float, rainfall: float) -> list:
    alerts = []

    if rainfall < 50:
        alerts.append("Low rainfall — irrigation is required to maintain adequate soil moisture.")
    elif rainfall > 300:
        alerts.append("Very high rainfall — risk of waterlogging; ensure field drainage.")

    if humidity > 85:
        alerts.append("High humidity — elevated risk of fungal disease; monitor crop canopy closely.")
    elif humidity < 30:
        alerts.append("Low humidity — increased crop water stress; consider mulching.")

    if temperature > 38:
        alerts.append("High temperature — heat stress risk; consider shade nets or adjusted sowing dates.")
    elif temperature < 10:
        alerts.append("Low temperature — cold stress risk for warm-season crops; protect seedlings.")

    return alerts
