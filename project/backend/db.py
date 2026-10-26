"""
db.py  —  MongoDB integration for Smart Soil Detection System
Database: soil_sense_db (on PharmacyCluster Atlas)

Collections:
  analyses   — soil params, weather, health, crops, fertilizer, alerts
  images     — uploaded soil image (base64) + CNN classification result
  weather    — location + weather data fetched from WeatherAPI
  reports    — PDF report metadata (filename, date, download_url)
"""

import os
from datetime import datetime, timezone

try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
    _pymongo_available = True
except ImportError:
    _pymongo_available = False

# ── MongoDB connection URI ────────────────────────────────────────────────────
MONGO_URI = os.environ.get(
    "MONGO_URI",
    "mongodb+srv://soiluser:anuja@pharmacycluster.ixcqnmj.mongodb.net/?appName=PharmacyCluster"
)
DB_NAME = "Soil_detection"

_client = None
_db     = None
_db_attempted = False


def get_db():
    """Return the MongoDB database instance, connecting once on first call."""
    global _client, _db, _db_attempted
    if _db is not None:
        return _db
    if _db_attempted:
        return None
    _db_attempted = True
    if not _pymongo_available:
        return None
    try:
        _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000, connectTimeoutMS=2000)
        _client.admin.command("ping")          # verify connection
        _db = _client[DB_NAME]
        print(f"[MongoDB] Connected to '{DB_NAME}' on PharmacyCluster.")
        _ensure_indexes(_db)
        return _db
    except (ConnectionFailure, ServerSelectionTimeoutError, Exception) as e:
        print(f"[MongoDB] Connection unavailable ({e}). Running with in-memory persistence.")
        return None


def _ensure_indexes(db):
    """Create useful indexes on first run."""
    try:
        db["analyses"].create_index([("created_at", -1)])
        db["images"].create_index([("created_at", -1)])
        db["weather"].create_index([("location", 1), ("created_at", -1)])
        db["reports"].create_index([("created_at", -1)])
    except Exception:
        pass


# ── Public save functions ─────────────────────────────────────────────────────

def save_analysis(payload: dict, cnn_result: dict | None = None) -> str | None:
    """
    Save a soil analysis result to the analyses and soil_data collections.
    Returns the inserted document _id as a string, or None if DB unavailable.
    """
    db = get_db()
    if db is None:
        return None
    doc = {
        "type":         "soil_analysis",
        "created_at":   datetime.now(timezone.utc),
        "soil_params":  payload.get("soil_params", {}),
        "weather":      payload.get("weather", {}),
        "health":       payload.get("health", {}),
        "crops":        payload.get("crops", []),
        "fertilizer":   payload.get("fertilizer", []),
        "irrigation":   payload.get("irrigation", []),
        "advisory":     payload.get("advisory", []),
        "alerts":       payload.get("alerts", []),
        "cnn_result":   cnn_result,
        "lang":         payload.get("lang", "en"),
    }
    try:
        result = db["analyses"].insert_one(doc)
        try:
            # Also mirror into soil_data collection
            db["soil_data"].insert_one(doc.copy())
        except Exception:
            pass
        return str(result.inserted_id)
    except Exception as e:
        print(f"[MongoDB] save_analysis error: {e}")
        return None


def save_image(image_bytes: bytes, filename: str, cnn_result: dict | None = None) -> str | None:
    """
    Save a soil image (binary) and its CNN classification to the images and soil_data collections.
    Returns the inserted _id as string, or None.
    """
    db = get_db()
    if db is None:
        return None
    import base64
    doc = {
        "type":         "soil_image",
        "created_at":   datetime.now(timezone.utc),
        "filename":     filename,
        "image_b64":    base64.b64encode(image_bytes).decode("utf-8"),
        "cnn_result":   cnn_result,
    }
    try:
        result = db["images"].insert_one(doc)
        try:
            db["soil_data"].insert_one(doc.copy())
        except Exception:
            pass
        return str(result.inserted_id)
    except Exception as e:
        print(f"[MongoDB] save_image error: {e}")
        return None


def save_weather(location: dict, weather: dict) -> str | None:
    """
    Save a weather lookup result to the weather and soil_data collections.
    Returns the inserted _id as string, or None.
    """
    db = get_db()
    if db is None:
        return None
    doc = {
        "type":       "weather_search",
        "created_at": datetime.now(timezone.utc),
        "location":   location,
        "weather":    weather,
    }
    try:
        result = db["weather"].insert_one(doc)
        try:
            db["soil_data"].insert_one(doc.copy())
        except Exception:
            pass
        return str(result.inserted_id)
    except Exception as e:
        print(f"[MongoDB] save_weather error: {e}")
        return None


def save_report(filename: str, download_url: str, lang: str, summary: dict) -> str | None:
    """
    Save PDF report metadata to the reports and soil_data collections.
    Returns the inserted _id as string, or None.
    """
    db = get_db()
    if db is None:
        return None
    doc = {
        "type":         "report_generation",
        "created_at":   datetime.now(timezone.utc),
        "filename":     filename,
        "download_url": download_url,
        "lang":         lang,
        "health_score": summary.get("health", {}).get("score"),
        "top_crop":     summary.get("crops", [{}])[0].get("crop") if summary.get("crops") else None,
        "soil_params":  summary.get("soil_params", {}),
        "weather":      summary.get("weather", {}),
    }
    try:
        result = db["reports"].insert_one(doc)
        try:
            db["soil_data"].insert_one(doc.copy())
        except Exception:
            pass
        return str(result.inserted_id)
    except Exception as e:
        print(f"[MongoDB] save_report error: {e}")
        return None


def get_stats() -> dict:
    """Return quick stats from MongoDB (for dashboard or admin use)."""
    db = get_db()
    if db is None:
        return {"connected": False}
    try:
        return {
            "connected":  True,
            "analyses":   db["analyses"].count_documents({}),
            "images":     db["images"].count_documents({}),
            "weather":    db["weather"].count_documents({}),
            "reports":    db["reports"].count_documents({}),
        }
    except Exception as e:
        return {"connected": False, "error": str(e)}
