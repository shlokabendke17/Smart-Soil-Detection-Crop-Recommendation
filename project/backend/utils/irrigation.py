"""
irrigation.py
Rule-based irrigation suggestion based on rainfall, temperature, and humidity.
Consumed by backend/app.py — never wired to the CNN output.
"""


def irrigation_suggestion(rainfall: float, temperature: float, humidity: float) -> list:
    """Return a list of plain-language irrigation recommendation strings."""
    tips = []

    # Rainfall-based primary recommendation
    if rainfall < 30:
        tips.append(
            "Critical water deficit — implement daily drip or micro-sprinkler irrigation "
            "to maintain minimum soil moisture."
        )
        tips.append(
            "Apply mulch (straw or dry leaves) over the root zone to reduce soil moisture evaporation."
        )
    elif rainfall < 50:
        tips.append(
            "Low rainfall — drip or furrow irrigation recommended 2–3 times per week; "
            "aim for 25–40 mm per session."
        )
    elif rainfall < 100:
        tips.append(
            "Moderate rainfall — supplemental irrigation may be needed during extended dry spells; "
            "monitor soil moisture at 15 cm depth."
        )
    elif rainfall < 200:
        tips.append(
            "Adequate rainfall — maintain current irrigation schedule and check field drainage after "
            "heavy rainfall events."
        )
    else:
        tips.append(
            "Very high rainfall — prioritise field drainage; waterlogging can cause root asphyxiation "
            "and nutrient leaching."
        )

    # Temperature modifier
    if temperature > 38:
        tips.append(
            "Extreme heat detected — schedule all irrigation sessions between 05:00–07:00 or after 18:00 "
            "to minimise evaporative losses (up to 40% reduction)."
        )
    elif temperature > 32:
        tips.append(
            "High temperature — irrigate in early morning or late evening to reduce evapotranspiration stress."
        )

    # Humidity modifier
    if humidity < 35:
        tips.append(
            "Very low humidity increases evapotranspiration demand — increase irrigation frequency "
            "or switch to mist irrigation for sensitive crops."
        )
    elif humidity > 85 and rainfall > 100:
        tips.append(
            "High humidity combined with heavy rainfall — avoid overhead irrigation to reduce "
            "disease (fungal) pressure."
        )

    if not tips:
        tips.append("Irrigation conditions appear optimal — maintain your current schedule.")

    return tips
