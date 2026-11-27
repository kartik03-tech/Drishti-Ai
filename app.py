
import json
import math
import os
import re
import secrets
import sqlite3
import smtplib
import socket
import uuid
import urllib.parse
from email.message import EmailMessage
from datetime import datetime, timedelta, timezone
from functools import wraps

import pandas as pd
import requests
from dotenv import load_dotenv
from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import check_password_hash, generate_password_hash
import ai_model
import hangout_places



# ============================================================
# DYNAMIC RISK INTELLIGENCE, SAFETY & THREAT IDENTIFICATION - MAIN FLASK APPLICATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "database.db")
SAFETY_FILE = os.path.join(
    BASE_DIR,
    "data",
    "mumbai places safety full.xlsx",
)
STATIONS_FILE = os.path.join(
    BASE_DIR,
    "data",
    "mumbai_stations.csv",
)

# Load .env before reading any settings.
# override=True makes sure the values in the project's .env file win over
# an old Windows environment variable with the same name.
ENV_FILE = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_FILE, override=True)

app = Flask(__name__)
# Enable ProxyFix so Flask correctly identifies HTTPS scheme and host behind reverse proxies (Render, Railway, etc.)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

app.config["SECRET_KEY"] = os.environ.get(
    "DRISTI_SECRET_KEY",
    os.environ.get("SAFEGUARD_SECRET_KEY", "dynamic-risk-intelligence-key"),
)
app.config["JSON_SORT_KEYS"] = False
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)


# ============================================================
# AUTOMATED SOS EMAIL
# ============================================================
# Gmail/SMTP is used instead of Twilio so the demo can send a
# custom SOS message without the Twilio trial-template restriction.

def _env_value(name, default=""):
    """Read and clean an environment value, including quoted .env values."""
    value = os.environ.get(name, default)
    if value is None:
        return ""
    value = str(value).strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"\"", "'"}:
        value = value[1:-1].strip()
    return value


def load_email_config():
    """Load the SMTP configuration fresh, with safe Gmail defaults."""
    load_dotenv(ENV_FILE, override=True)

    host = _env_value("SMTP_HOST", "smtp.gmail.com")

    # Recover from common mistakes such as https://smtp.gmail.com or
    # smtp.gmail.com:465 being pasted into SMTP_HOST.
    host = re.sub(r"^https?://", "", host, flags=re.I).strip().rstrip("/")
    if ":" in host and host.count(":") == 1:
        maybe_host, maybe_port = host.rsplit(":", 1)
        if maybe_port.isdigit():
            host = maybe_host.strip()

    if not host:
        host = "smtp.gmail.com"

    port_text = _env_value("SMTP_PORT", "465")
    try:
        port = int(port_text)
    except (TypeError, ValueError):
        port = 465

    if port not in {465, 587}:
        port = 465

    user = _env_value("SMTP_USER", "")
    password = _env_value("SMTP_PASSWORD", "").replace(" ", "")
    recipient = _env_value("SOS_EMAIL_TO", "")

    return {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
        "recipient": recipient,
    }


def email_configuration_status():
    """Return non-sensitive email configuration status."""
    cfg = load_email_config()
    return {
        "smtp_configured": bool(cfg["host"] and cfg["port"]),
        "sender_configured": bool(cfg["user"] and cfg["password"]),
        "default_recipient_configured": bool(cfg["recipient"]),
        "host": cfg["host"],
        "port": cfg["port"],
        "env_file_exists": os.path.exists(ENV_FILE),
    }


# ============================================================
# SERVICE CONFIGURATION
# ============================================================

SERVICE_TABLES = {
    "hospital": "hospitals",
    "police": "police_stations",
    "fire": "fire_stations",
    "pharmacy": "pharmacies",
    "blood_bank": "blood_banks",
}

SERVICE_LABELS = {
    "hospital": "Hospitals",
    "police": "Police Stations",
    "fire": "Fire Stations",
    "pharmacy": "Medical Stores",
    "blood_bank": "Blood Banks",
}

SERVICE_ICONS = {
    "hospital": "fa-hospital",
    "police": "fa-shield-halved",
    "fire": "fa-fire-extinguisher",
    "pharmacy": "fa-prescription-bottle-medical",
    "blood_bank": "fa-droplet",
}

SERVICE_ALIASES = {
    "medical": "pharmacy",
    "medical_store": "pharmacy",
    "medical_stores": "pharmacy",
    "pharmacy": "pharmacy",
    "hospital": "hospital",
    "hospitals": "hospital",
    "police": "police",
    "police_station": "police",
    "police_stations": "police",
    "fire": "fire",
    "fire_station": "fire",
    "fire_stations": "fire",
    "blood_bank": "blood_bank",
    "blood_banks": "blood_bank",
}

EMERGENCY_CONTACTS = [
    {
        "name": "Emergency",
        "number": "112",
        "icon": "fa-triangle-exclamation",
        "description": "National emergency assistance",
    },
    {
        "name": "Police",
        "number": "100",
        "icon": "fa-shield-halved",
        "description": "Police emergency assistance",
    },
    {
        "name": "Ambulance",
        "number": "108",
        "icon": "fa-truck-medical",
        "description": "Medical / ambulance assistance",
    },
    {
        "name": "Fire",
        "number": "101",
        "icon": "fa-fire-extinguisher",
        "description": "Fire and rescue emergency",
    },
]


# ============================================================
# DATABASE HELPERS + MIGRATION
# ============================================================

def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def table_exists(conn, table_name):
    row = conn.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table' AND name = ?
        """,
        (table_name,),
    ).fetchone()
    return row is not None


def table_columns(conn, table_name):
    if not table_exists(conn, table_name):
        return []

    rows = conn.execute(
        f'PRAGMA table_info("{table_name}")'
    ).fetchall()

    return [row["name"] for row in rows]


def ensure_column(conn, table_name, column_name, column_type):
    if column_name in table_columns(conn, table_name):
        return

    conn.execute(
        f'ALTER TABLE "{table_name}" '
        f'ADD COLUMN "{column_name}" {column_type}'
    )


def initialize_database():
    """
    Create application tables and repair older versions of database.db.
    Existing emergency-service tables are never deleted or recreated.
    """
    conn = get_db()

    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                search_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                report_type TEXT,
                place_name TEXT,
                route_text TEXT,
                issue_type TEXT NOT NULL,
                description TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                expires_at TEXT NOT NULL,
                used INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )

        # Repair existing users table.
        user_cols = table_columns(conn, "users")
        if "password_hash" not in user_cols:
            ensure_column(conn, "users", "password_hash", "TEXT")
            user_cols = table_columns(conn, "users")

        if "created_at" not in user_cols:
            ensure_column(
                conn,
                "users",
                "created_at",
                "TEXT",
            )

        # Some older builds stored the password in a column named password.
        if "password" in user_cols and "password_hash" in user_cols:
            conn.execute(
                """
                UPDATE users
                SET password_hash = password
                WHERE (password_hash IS NULL OR password_hash = '')
                  AND password IS NOT NULL
                """
            )

        # Repair existing search history.
        search_cols = table_columns(conn, "search_history")

        if "created_at" not in search_cols:
            ensure_column(
                conn,
                "search_history",
                "created_at",
                "TEXT",
            )

        if (
            "search_text" not in search_cols
            and "place" not in search_cols
        ):
            ensure_column(
                conn,
                "search_history",
                "search_text",
                "TEXT",
            )

        # Repair existing reports table (Phase 5: Community Reporting)
        report_cols = table_columns(conn, "reports")
        if "created_at" not in report_cols:
            ensure_column(conn, "reports", "created_at", "TEXT")
        if "latitude" not in report_cols:
            ensure_column(conn, "reports", "latitude", "REAL")
        if "longitude" not in report_cols:
            ensure_column(conn, "reports", "longitude", "REAL")
        if "severity" not in report_cols:
            ensure_column(conn, "reports", "severity", "TEXT DEFAULT 'Medium'")
        if "status" not in report_cols:
            ensure_column(conn, "reports", "status", "TEXT DEFAULT 'Active'")
        if "upvotes" not in report_cols:
            ensure_column(conn, "reports", "upvotes", "INTEGER DEFAULT 1")

        # Seed sample community reports if table is empty (Phase 5)
        cur_rep = conn.cursor()
        cur_rep.execute("SELECT COUNT(*) FROM reports")
        if cur_rep.fetchone()[0] == 0:
            sample_reports = [
                (1, "place", "Bandra Kurla Complex (BKC)", 19.0674, 72.8687, "Broken Streetlight", "Critical", "Streetlights completely non-operational along Diamond Bourse connector. Very dark corridor after 8 PM.", "Active", 14),
                (1, "place", "Kurla West Station Road", 19.0726, 72.8845, "Waterlogging / Flood", "Medium", "Monsoon drain overflow causing 6-inch water pooling near auto-stand entrance.", "Active", 9),
                (1, "place", "SVT Road, Santacruz West", 19.0843, 72.8360, "Hazardous Pothole", "Medium", "Deep cluster of potholes across slow lane, causing two-wheelers to swerve abruptly.", "Active", 7),
                (1, "place", "Andheri West, Link Road", 19.1364, 72.8277, "Broken Streetlight", "Medium", "Four consecutive street poles dark between Metro Pillars 108 and 112.", "Active", 12),
                (1, "place", "Dadar TT Circle", 19.0178, 72.8478, "Road Blockage", "Low", "Utility duct maintenance barricades narrowing traffic flow to one lane.", "Resolved", 5),
            ]
            conn.executemany(
                """
                INSERT INTO reports (user_id, report_type, place_name, latitude, longitude, issue_type, severity, description, status, upvotes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                sample_reports
            )

        # Ensure emergency_contacts table exists and has all required fields (Phase 4)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS emergency_contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                relationship TEXT,
                email TEXT,
                is_primary INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )

        ec_cols = table_columns(conn, "emergency_contacts")
        if "email" not in ec_cols:
            ensure_column(conn, "emergency_contacts", "email", "TEXT")
        if "is_primary" not in ec_cols:
            ensure_column(conn, "emergency_contacts", "is_primary", "INTEGER DEFAULT 0")

        # Seed sample contacts for default user if table is empty
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM emergency_contacts")
        if cur.fetchone()[0] == 0:
            now_init = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            conn.execute(
                """
                INSERT INTO emergency_contacts (user_id, name, phone, relationship, email, is_primary, created_at)
                VALUES 
                (1, 'Family Guardian', '+91 98200 12345', 'Family', 'guardian@example.com', 1, ?),
                (1, 'Personal Friend', '+91 98211 54321', 'Friend', 'friend@example.com', 0, ?)
                """,
                (now_init, now_init)
            )

        # Ensure tracking_sessions table exists for Live "Walk With Me" (Phase 4)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tracking_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token TEXT UNIQUE NOT NULL,
                user_id INTEGER,
                user_name TEXT,
                active INTEGER DEFAULT 1,
                current_lat REAL,
                current_lon REAL,
                heading REAL DEFAULT 0,
                speed REAL DEFAULT 0,
                battery INTEGER DEFAULT 100,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                trail_json TEXT DEFAULT '[]'
            )
            """
        )

        conn.commit()

    except sqlite3.Error as exc:
        conn.rollback()
        print("Database initialization error:", exc)

    finally:
        conn.close()


# ============================================================
# GENERAL HELPERS
# ============================================================

def clean(value):
    if value is None:
        return ""

    try:
        if pd.isna(value):
            return ""
    except Exception:
        pass

    return str(value).strip()


def to_float(value):
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def safe_int(value, default=8):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def valid_coordinates(lat, lon):
    return (
        lat is not None
        and lon is not None
        and -90 <= lat <= 90
        and -180 <= lon <= 180
    )


def normalize_email(value):
    return clean(value).lower()


def normalize_service_type(value):
    value = clean(value).lower()
    return SERVICE_ALIASES.get(value, value)


def current_user_record():
    user_id = session.get("user_id")

    if user_id:
        conn = get_db()
        try:
            if not table_exists(conn, "users"):
                return None

            row = conn.execute(
                """
                SELECT id, name, email
                FROM users
                WHERE id = ?
                """,
                (user_id,),
            ).fetchone()
        finally:
            conn.close()

        if row:
            return {
                "id": row["id"],
                "name": clean(row["name"]),
                "email": clean(row["email"]),
                "is_guest": False,
            }

        session.clear()

    if session.get("guest"):
        return {
            "id": None,
            "name": "Guest",
            "email": "",
            "is_guest": True,
        }

    return None


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id") and not session.get("guest"):
            return redirect(
                url_for(
                    "login",
                    next=request.full_path,
                )
            )
        return view(*args, **kwargs)

    return wrapped


# ============================================================
# SAFETY EXCEL
# ============================================================

def load_safety_data():
    if not os.path.exists(SAFETY_FILE):
        app.logger.warning(
            "Safety Excel file not found: %s",
            SAFETY_FILE,
        )
        return pd.DataFrame()

    try:
        df = pd.read_excel(
            SAFETY_FILE,
            sheet_name="Mumbai Places Safety",
        )

        df.columns = [
            str(column).strip()
            for column in df.columns
        ]

        return df

    except Exception as exc:
        app.logger.exception(
            "Unable to read safety Excel: %s",
            exc,
        )
        return pd.DataFrame()


def safety_record(place_name):
    df = load_safety_data()

    if df.empty or "Place" not in df.columns:
        return None

    query = clean(place_name).casefold()

    if not query:
        return None

    def normalize_text(value):
        value = clean(value).casefold()
        value = re.sub(r"[^a-z0-9\\s]", " ", value)
        value = re.sub(r"\\s+", " ", value).strip()
        return value

    query_normalized = normalize_text(query)

    places = df["Place"].astype(str).str.strip()
    place_normalized = places.map(normalize_text)

    exact = df[place_normalized == query_normalized]

    if not exact.empty:
        row = exact.iloc[0]
    else:
        contains_query = df[
            place_normalized.str.contains(
                query_normalized,
                na=False,
                regex=False,
            )
        ]

        if not contains_query.empty:
            row = contains_query.iloc[0]
        else:
            query_contains_place = df[
                place_normalized.apply(
                    lambda value: (
                        bool(value)
                        and value in query_normalized
                    )
                )
            ]

            if query_contains_place.empty:
                stripped = re.sub(
                    r"\b(west|east|north|south|station|area|road|rd)\b",
                    " ",
                    query_normalized,
                )
                stripped = re.sub(r"\s+", " ", stripped).strip()
                if stripped and stripped != query_normalized:
                    stripped_hits = df[
                        place_normalized.str.contains(
                            stripped,
                            na=False,
                            regex=False,
                        )
                    ]
                    if not stripped_hits.empty:
                        row = stripped_hits.iloc[0]
                    else:
                        return None
                else:
                    return None
            else:
                match_index = max(
                    query_contains_place.index,
                    key=lambda index: len(
                        normalize_text(
                            query_contains_place.loc[index, "Place"]
                        )
                    ),
                )
                row = query_contains_place.loc[match_index]

    score = to_float(
        row.get("Safety Score (1-10, est.)")
    )

    return {
        "place": clean(row.get("Place")),
        "zone": clean(row.get("Zone")),
        "category": clean(row.get("Category")),
        "score": (
            round(score, 1)
            if score is not None
            else None
        ),
        "lighting": clean(row.get("Street Lighting")),
        "best_time": clean(row.get("Best Time to Visit")),
        "notes": clean(row.get("Notes / Caution")),
    }


def all_safety_places():
    df = load_safety_data()

    if df.empty:
        return []

    records = []

    for _, row in df.iterrows():
        score = to_float(
            row.get("Safety Score (1-10, est.)")
        )

        records.append(
            {
                "place": clean(row.get("Place")),
                "zone": clean(row.get("Zone")),
                "category": clean(row.get("Category")),
                "score": round(score, 1) if score is not None else None,
                "lighting": clean(row.get("Street Lighting")),
                "best_time": clean(row.get("Best Time to Visit")),
                "notes": clean(row.get("Notes / Caution")),
            }
        )

    return records


# ============================================================
# LOCATION + GEOCODING
# ============================================================

def is_coordinate_string(value):
    value = clean(value)
    if not value:
        return None

    parts = [
        part.strip()
        for part in value.split(",")
    ]

    if len(parts) != 2:
        return None

    lat = to_float(parts[0])
    lon = to_float(parts[1])

    if not valid_coordinates(lat, lon):
        return None

    return lat, lon


MUMBAI_LOCATION_FALLBACKS = {
    "marine drive": (18.9436, 72.8238),
    "gateway of india": (18.9220, 72.8347),
    "colaba": (18.9151, 72.8258),
    "colaba causeway": (18.9226, 72.8314),
    "nariman point": (18.9256, 72.8242),
    "churchgate": (18.9322, 72.8264),
    "fort": (18.9345, 72.8371),
    "cst": (18.9400, 72.8353),
    "girgaon": (18.9562, 72.8188),
    "malabar hill": (18.9548, 72.7985),
    "byculla": (18.9750, 72.8295),
    "mahalaxmi": (18.9827, 72.8236),
    "lower parel": (18.9953, 72.8306),
    "prabhadevi": (19.0166, 72.8295),
    "worli": (19.0166, 72.8167),
    "dadar": (19.0178, 72.8478),
    "dadar west": (19.0200, 72.8420),
    "matunga": (19.0274, 72.8550),
    "sion": (19.0434, 72.8633),
    "mahim": (19.0410, 72.8410),
    "bandra": (19.0607, 72.8362),
    "bandra west": (19.0553, 72.8267),
    "bandra east": (19.0620, 72.8520),
    "bkc": (19.0674, 72.8687),
    "khar": (19.0700, 72.8330),
    "santacruz": (19.0843, 72.8360),
    "vile parle": (19.0997, 72.8438),
    "juhu": (19.0883, 72.8262),
    "andheri": (19.1197, 72.8468),
    "andheri west": (19.1364, 72.8277),
    "andheri east": (19.1150, 72.8690),
    "sakinaka": (19.1030, 72.8878),
    "marol": (19.1190, 72.8825),
    "lokhandwala": (19.1436, 72.8257),
    "chandivali": (19.1112, 72.8976),
    "wadala": (19.0172, 72.8648),
    "dharavi": (19.0422, 72.8536),
    "versova": (19.1352, 72.8143),
    "jogeshwari": (19.1378, 72.8498),
    "goregaon": (19.1663, 72.8526),
    "goregaon west": (19.1630, 72.8420),
    "malad": (19.1874, 72.8484),
    "malad west": (19.1865, 72.8480),
    "kandivali": (19.2045, 72.8522),
    "kandivali west": (19.2080, 72.8380),
    "borivali": (19.2307, 72.8567),
    "borivali west": (19.2288, 72.8500),
    "dahisar": (19.2574, 72.8596),
    "kurla": (19.0726, 72.8845),
    "ghatkopar": (19.0860, 72.9080),
    "ghatkopar east": (19.0850, 72.9150),
    "vikhroli": (19.1114, 72.9279),
    "kanjurmarg": (19.1300, 72.9318),
    "kanjurmarg west": (19.1310, 72.9280),
    "bhandup": (19.1449, 72.9372),
    "bhandup west": (19.1455, 72.9260),
    "powai": (19.1176, 72.9060),
    "mulund": (19.1726, 72.9567),
    "mulund west": (19.1726, 72.9485),
    "chembur": (19.0522, 72.8994),
    "govandi": (19.0550, 72.9150),
    "mankhurd": (19.0494, 72.9324),
    "thane": (19.2183, 72.9781),
    "airoli": (19.1579, 72.9935),
    "vashi": (19.0771, 72.9986),
    "nerul": (19.0330, 73.0197),
    "belapur": (19.0197, 73.0416),
}


def _find_nearest_mumbai_locality(lat, lon):
    """Find the closest Mumbai locality name to given GPS coordinates."""
    if not valid_coordinates(lat, lon):
        return None

    best_name = None
    min_dist = float("inf")

    for name, (c_lat, c_lon) in MUMBAI_LOCATION_FALLBACKS.items():
        d_lat = math.radians(lat - c_lat)
        d_lon = math.radians(lon - c_lon)
        a = (
            math.sin(d_lat / 2) ** 2
            + math.cos(math.radians(c_lat))
            * math.cos(math.radians(lat))
            * math.sin(d_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        dist_km = 6371.0 * c

        if dist_km < min_dist:
            min_dist = dist_km
            best_name = name

    if best_name:
        title_name = best_name.title()
        return {
            "name": f"{title_name}, Mumbai",
            "display_name": f"{title_name}, Mumbai, Maharashtra",
            "distance_km": round(min_dist, 2),
        }
    return None


_MUMBAI_STATIONS_CACHE = None


def load_mumbai_stations():
    """Load Mumbai Local / Metro station coordinates from CSV once."""
    global _MUMBAI_STATIONS_CACHE
    if _MUMBAI_STATIONS_CACHE is not None:
        return _MUMBAI_STATIONS_CACHE

    if not os.path.exists(STATIONS_FILE):
        _MUMBAI_STATIONS_CACHE = []
        return _MUMBAI_STATIONS_CACHE

    stations = []
    try:
        df = pd.read_csv(STATIONS_FILE)
        for _, row in df.iterrows():
            name = clean(row.get("Station"))
            line = clean(row.get("Line"))
            lat = to_float(row.get("Latitude"))
            lon = to_float(row.get("Longitude"))
            if name and valid_coordinates(lat, lon):
                stations.append(
                    {
                        "station": name,
                        "line": line or "Mumbai Rail",
                        "latitude": lat,
                        "longitude": lon,
                    }
                )
    except Exception as exc:
        app.logger.warning("Unable to load Mumbai stations CSV: %s", exc)

    _MUMBAI_STATIONS_CACHE = stations
    return _MUMBAI_STATIONS_CACHE


def nearest_station(lat, lon):
    """Return the closest Mumbai railway/metro station for given coordinates."""
    lat = to_float(lat)
    lon = to_float(lon)
    if not valid_coordinates(lat, lon):
        return None

    stations = load_mumbai_stations()
    if not stations:
        return None

    best = None
    best_dist = float("inf")
    for st in stations:
        dist = haversine_km(lat, lon, st["latitude"], st["longitude"])
        if dist < best_dist:
            best_dist = dist
            best = st

    if not best:
        return None

    return {
        "station": best["station"],
        "line": best["line"],
        "distance_km": round(best_dist, 2),
        "latitude": best["latitude"],
        "longitude": best["longitude"],
    }


def _station_location(query):
    normalized = clean(query).casefold()
    if not normalized:
        return None
    clean_q = re.sub(r"\bstation\b", "", normalized).strip()
    for st in load_mumbai_stations():
        st_name = st["station"].casefold()
        if clean_q == st_name or st_name in clean_q:
            return {
                "lat": st["latitude"],
                "lon": st["longitude"],
                "display_name": f"{st['station']} Station ({st['line']} Line), Mumbai",
            }
    return None


def _hangout_location(query):
    normalized = clean(query).casefold()
    if not normalized:
        return None
    for place in hangout_places.RAW_HANGOUT_PLACES:
        place_name = place["name"].casefold()
        if normalized == place_name or normalized == place["slug"] or place_name in normalized:
            return {
                "lat": place["lat"],
                "lon": place["lon"],
                "display_name": f"{place['name']}, {place['area']}, Mumbai, Maharashtra, India",
            }
    return None


def _local_coordinates(query):
    """Fast local coordinate resolution without external network calls."""
    direct = is_coordinate_string(query)
    if direct:
        return {
            "lat": direct[0],
            "lon": direct[1],
            "display_name": "Current Location",
        }
    normalized = clean(query).casefold()
    if normalized in MUMBAI_LOCATION_FALLBACKS:
        lat, lon = MUMBAI_LOCATION_FALLBACKS[normalized]
        return {
            "lat": lat,
            "lon": lon,
            "display_name": f"{query}, Mumbai, Maharashtra, India",
        }
    return (
        _hangout_location(query)
        or _station_location(query)
        or _fallback_location(query)
    )


def _resolve_place_coords(query, rec=None):
    """Resolve coordinates from query, matched place name, or zone parts without network calls."""
    coords = _local_coordinates(query)
    if coords:
        return coords
    if rec:
        coords = _local_coordinates(rec.get("place"))
        if coords:
            return coords
        zone_text = clean(rec.get("zone"))
        for part in re.split(r"[/,]", zone_text):
            coords = _local_coordinates(part.strip())
            if coords:
                return coords
    return None


def _fallback_location(query):
    hangout_match = _hangout_location(query)
    if hangout_match:
        return hangout_match

    normalized = clean(query).casefold()

    if not normalized:
        return None

    if normalized in MUMBAI_LOCATION_FALLBACKS:
        lat, lon = MUMBAI_LOCATION_FALLBACKS[normalized]
        return {
            "lat": lat,
            "lon": lon,
            "display_name": f"{query}, Mumbai, Maharashtra, India",
        }

    station_match = _station_location(query)
    if station_match:
        return station_match

    for name, coordinates in MUMBAI_LOCATION_FALLBACKS.items():
        if name in normalized or normalized in name:
            lat, lon = coordinates
            return {
                "lat": lat,
                "lon": lon,
                "display_name": f"{query}, Mumbai, Maharashtra, India",
            }

    return None


def geocode(query):
    query = clean(query)

    if not query:
        return None

    direct = is_coordinate_string(query)

    if direct:
        return {
            "lat": direct[0],
            "lon": direct[1],
            "display_name": "Current Location",
        }

    params = {
        "q": f"{query}, Mumbai, Maharashtra, India",
        "format": "jsonv2",
        "limit": 1,
        "countrycodes": "in",
    }

    headers = {
        "User-Agent": (
            "DynamicRiskIntelligence/1.0 "
            "(academic emergency-assistance project)"
        )
    }

    try:
        response = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params=params,
            headers=headers,
            timeout=7,
        )
        response.raise_for_status()

        results = response.json()

        if results:
            return {
                "lat": float(results[0]["lat"]),
                "lon": float(results[0]["lon"]),
                "display_name": results[0].get(
                    "display_name",
                    query,
                ),
            }

    except (
        requests.RequestException,
        ValueError,
        KeyError,
        TypeError,
    ) as exc:
        app.logger.warning(
            "Nominatim geocoding failed for %s: %s",
            query,
            exc,
        )

    try:
        photon_response = requests.get(
            "https://photon.komoot.io/api/",
            params={
                "q": f"{query}, Mumbai, India",
                "limit": 1,
            },
            headers=headers,
            timeout=7,
        )
        photon_response.raise_for_status()

        photon_data = photon_response.json()
        features = photon_data.get("features", [])

        if features:
            geometry = features[0].get("geometry", {})
            coordinates = geometry.get("coordinates", [])

            if len(coordinates) >= 2:
                return {
                    "lat": float(coordinates[1]),
                    "lon": float(coordinates[0]),
                    "display_name": (
                        features[0]
                        .get("properties", {})
                        .get("name")
                        or query
                    ),
                }

    except (
        requests.RequestException,
        ValueError,
        KeyError,
        TypeError,
        IndexError,
    ) as exc:
        app.logger.warning(
            "Photon geocoding failed for %s: %s",
            query,
            exc,
        )

    fallback = _fallback_location(query)

    if fallback:
        app.logger.info(
            "Using local Mumbai geocoding fallback for %s",
            query,
        )
        return fallback

    return None


def reverse_geocode(lat, lon):
    lat = to_float(lat)
    lon = to_float(lon)
    if not valid_coordinates(lat, lon):
        return None

    # First find nearest local Mumbai locality as guaranteed offline fallback
    nearest_fallback = _find_nearest_mumbai_locality(lat, lon)

    params = {
        "lat": lat,
        "lon": lon,
        "format": "jsonv2",
        "zoom": 16,
        "addressdetails": 1,
    }

    headers = {
        "User-Agent": (
            "DynamicRiskIntelligence/1.0 "
            "(academic emergency-assistance project)"
        )
    }

    try:
        response = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params=params,
            headers=headers,
            timeout=2.5,
        )
        if response.status_code == 200:
            data = response.json()
            addr = data.get("address", {})
            suburb = (
                addr.get("suburb")
                or addr.get("neighbourhood")
                or addr.get("residential")
                or addr.get("subdistrict")
            )
            city = addr.get("city") or addr.get("town") or "Mumbai"
            if suburb:
                clean_locality = f"{suburb}, {city}"
            else:
                clean_locality = data.get("display_name", "").split(",")[0]
                if "mumbai" not in clean_locality.lower():
                    clean_locality = f"{clean_locality}, {city}"

            return {
                "locality": clean_locality,
                "display_name": data.get("display_name", clean_locality),
                "address": addr,
            }
    except Exception as exc:
        app.logger.warning(
            "Reverse geocoding network lookup failed for %.4f, %.4f: %s",
            lat,
            lon,
            exc,
        )

    # Use closest Mumbai locality from local mapping
    if nearest_fallback:
        return {
            "locality": nearest_fallback["name"],
            "display_name": nearest_fallback["display_name"],
            "address": {"suburb": nearest_fallback["name"], "city": "Mumbai"},
        }

    return {
        "locality": "Mumbai Central",
        "display_name": "Mumbai, Maharashtra, India",
        "address": {},
    }


@app.route("/api/reverse-geocode")
def api_reverse_geocode():
    lat = to_float(request.args.get("lat"))
    lon = to_float(request.args.get("lon"))
    if not valid_coordinates(lat, lon):
        return jsonify({"success": False, "message": "Valid coordinates required."}), 400

    result = reverse_geocode(lat, lon)
    if not result:
        return jsonify({"success": True, "locality": "Mumbai Central", "display_name": "Mumbai Central, Mumbai"})

    return jsonify({
        "success": True,
        "locality": result.get("locality", "Mumbai Central"),
        "display_name": result.get("display_name", "Mumbai, Maharashtra"),
        "lat": lat,
        "lon": lon
    })


def safety_record_from_coordinates(lat, lon):
    lat = to_float(lat)
    lon = to_float(lon)

    if not valid_coordinates(lat, lon):
        return None

    reverse_result = reverse_geocode(lat, lon)

    if not reverse_result:
        return None

    address = reverse_result.get("address", {}) or {}

    candidates = [
        address.get("neighbourhood"),
        address.get("suburb"),
        address.get("city_district"),
        address.get("town"),
        address.get("city"),
        address.get("road"),
        address.get("village"),
        reverse_result.get("display_name"),
    ]

    seen = set()

    for candidate in candidates:
        candidate = clean(candidate)
        key = candidate.casefold()

        if not candidate or key in seen:
            continue

        seen.add(key)

        result = safety_record(candidate)

        if result:
            return result

    return None


def resolve_location(value):
    value = clean(value)

    if not value:
        return None

    direct = is_coordinate_string(value)
    if direct:
        return {
            "lat": direct[0],
            "lon": direct[1],
            "display_name": "Current Location",
        }

    hangout_match = _hangout_location(value)
    if hangout_match:
        return hangout_match

    return geocode(value)


def haversine_km(lat1, lon1, lat2, lon2):
    radius = 6371.0

    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(p1)
        * math.cos(p2)
        * math.sin(dlon / 2) ** 2
    )

    return radius * 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a),
    )


# ============================================================
# OSRM ROUTING
# ============================================================

def _format_step_distance(meters):
    m = to_float(meters) or 0.0
    if m >= 1000:
        return f"{round(m / 1000.0, 2)} km"
    return f"{int(round(m))} m"


def _normalize_osrm_steps(legs):
    instructions = []
    for leg in legs or []:
        for step in leg.get("steps") or []:
            maneuver = step.get("maneuver") or {}
            m_type = clean(maneuver.get("type")).replace("-", " ")
            m_mod = clean(maneuver.get("modifier")).replace("-", " ")
            road = clean(step.get("name")) or clean(step.get("ref"))
            dist_m = to_float(step.get("distance")) or 0.0
            if m_type == "depart":
                action = "Start"
            elif m_type == "arrive":
                action = "Arrive at destination"
            else:
                parts = [p for p in [m_type.title(), m_mod] if p]
                action = " ".join(parts) if parts else "Continue"
            text = f"{action} onto {road}" if road and m_type != "arrive" else action
            instructions.append(
                {
                    "instruction": text,
                    "road": road,
                    "distance_text": _format_step_distance(dist_m),
                }
            )
    return instructions


def _normalize_valhalla_steps(legs):
    instructions = []
    for leg in legs or []:
        for man in leg.get("maneuvers") or []:
            text = clean(man.get("instruction"))
            if not text:
                continue
            length_km = to_float(man.get("length")) or 0.0
            streets = man.get("street_names") or []
            road = clean(streets[0]) if streets else ""
            instructions.append(
                {
                    "instruction": text,
                    "road": road,
                    "distance_text": _format_step_distance(length_km * 1000.0),
                }
            )
    return instructions


def _format_route_result(raw_routes, provider='OSRM'):
    """Convert routing-provider routes to Dynamic Risk Intelligence's common structure."""
    routes = []

    for index, raw_route in enumerate(raw_routes):
        distance = to_float(raw_route.get("distance")) or 0
        duration = to_float(raw_route.get("duration")) or 0
        legs = raw_route.get("legs", [])

        routes.append(
            {
                "id": index + 1,
                "distance_km": round(distance / 1000, 2),
                "duration_minutes": round(duration / 60),
                "geometry": raw_route.get("geometry"),
                "steps": legs,
                "turn_instructions": _normalize_osrm_steps(legs),
                "provider": provider,
            }
        )

    if not routes:
        return None

    return {
        "shortest": routes[0],
        "alternative": routes[1] if len(routes) > 1 else None,
        "all_routes": routes,
        "provider": provider,
    }


def _decode_polyline6(encoded):
    """Decode Valhalla's encoded polyline with 6 decimal places."""
    if not encoded:
        return []

    coordinates = []
    index = 0
    latitude = 0
    longitude = 0

    try:
        while index < len(encoded):
            result = 0
            shift = 0
            while True:
                byte = ord(encoded[index]) - 63
                index += 1
                result |= (byte & 0x1F) << shift
                shift += 5
                if byte < 0x20:
                    break
            delta_lat = ~(result >> 1) if result & 1 else result >> 1
            latitude += delta_lat

            result = 0
            shift = 0
            while True:
                byte = ord(encoded[index]) - 63
                index += 1
                result |= (byte & 0x1F) << shift
                shift += 5
                if byte < 0x20:
                    break
            delta_lon = ~(result >> 1) if result & 1 else result >> 1
            longitude += delta_lon

            coordinates.append(
                [
                    longitude / 1_000_000,
                    latitude / 1_000_000,
                ]
            )
    except (IndexError, TypeError, ValueError):
        return []

    return coordinates


def _route_geometry_from_valhalla(trip):
    """Build GeoJSON geometry from Valhalla leg shapes."""
    coordinates = []

    for leg in trip.get("legs", []) or []:
        shape = leg.get("shape")
        decoded = _decode_polyline6(shape)
        if not decoded:
            continue

        if coordinates and decoded and coordinates[-1] == decoded[0]:
            decoded = decoded[1:]

        coordinates.extend(decoded)

    if len(coordinates) < 2:
        return None

    return {
        "type": "LineString",
        "coordinates": coordinates,
    }


def _route_from_osrm(url, timeout=18, alternatives=True):
    """Request an OSRM-compatible route endpoint."""
    params = {
        "alternatives": "true" if alternatives else "false",
        "steps": "true",
        "overview": "full",
        "geometries": "geojson",
    }

    response = requests.get(
        url,
        params=params,
        timeout=timeout,
        headers={
            "User-Agent": "DynamicRiskIntelligence/1.0 (academic project)",
        },
    )
    response.raise_for_status()
    data = response.json()

    if data.get("code") != "Ok":
        raise RuntimeError(
            f"Routing service returned code {data.get('code', 'unknown')}"
        )

    raw_routes = data.get("routes") or []
    return _format_route_result(raw_routes, provider="OSRM")


def _route_from_valhalla(start_lat, start_lon, end_lat, end_lon):
    """Use the public Valhalla OSM routing service as a fallback."""
    payload = {
        "locations": [
            {
                "lat": float(start_lat),
                "lon": float(start_lon),
                "type": "break",
            },
            {
                "lat": float(end_lat),
                "lon": float(end_lon),
                "type": "break",
            },
        ],
        "costing": "auto",
        "alternates": 2,
        "units": "kilometers",
        "directions_options": {
            "units": "kilometers",
            "language": "en-US",
        },
    }

    response = requests.post(
        "https://valhalla1.openstreetmap.de/route",
        json=payload,
        timeout=25,
        headers={
            "User-Agent": "DynamicRiskIntelligence/1.0 (academic project)",
            "X-Client-Id": "dynamic-risk-intelligence",
        },
    )
    response.raise_for_status()
    data = response.json()

    trip = data.get("trip") or {}
    summary = trip.get("summary") or {}

    distance_km = to_float(summary.get("length"))
    duration_minutes = to_float(summary.get("time"))

    if distance_km is None or duration_minutes is None:
        raise RuntimeError("Valhalla returned no usable route summary")

    # Valhalla time is in seconds; its length is in the requested units.
    legs = trip.get("legs", []) or []
    primary = {
        "distance_km": round(distance_km, 2),
        "duration_minutes": round(duration_minutes / 60),
        "geometry": _route_geometry_from_valhalla(trip),
        "steps": legs,
        "turn_instructions": _normalize_valhalla_steps(legs),
        "provider": "Valhalla",
        "id": 1,
    }

    all_routes = [primary]
    for alt_idx, alt_entry in enumerate(data.get("alternates") or [], start=2):
        alt_trip = alt_entry.get("trip") or {}
        alt_sum = alt_trip.get("summary") or {}
        alt_dist = to_float(alt_sum.get("length"))
        alt_dur = to_float(alt_sum.get("time"))
        alt_geom = _route_geometry_from_valhalla(alt_trip)
        if alt_dist is not None and alt_dur is not None and alt_geom:
            alt_legs = alt_trip.get("legs", []) or []
            all_routes.append(
                {
                    "id": alt_idx,
                    "distance_km": round(alt_dist, 2),
                    "duration_minutes": round(alt_dur / 60),
                    "geometry": alt_geom,
                    "steps": alt_legs,
                    "turn_instructions": _normalize_valhalla_steps(alt_legs),
                    "provider": "Valhalla",
                }
            )

    return {
        "shortest": primary,
        "alternative": all_routes[1] if len(all_routes) > 1 else None,
        "all_routes": all_routes,
        "provider": "Valhalla",
    }


def _route_from_tomtom(start_lat, start_lon, end_lat, end_lon):
    """Use TomTom free-tier Routing API (live traffic + alternatives) when TOMTOM_API_KEY is configured."""
    api_key = _env_value("TOMTOM_API_KEY", "")
    if not api_key:
        return None

    url = (
        "https://api.tomtom.com/routing/1/calculateRoute/"
        f"{start_lat},{start_lon}:{end_lat},{end_lon}/json"
    )
    response = requests.get(
        url,
        params={
            "key": api_key,
            "traffic": "true",
            "maxAlternatives": 2,
            "instructionsType": "text",
            "routeRepresentation": "polyline",
        },
        timeout=15,
    )
    response.raise_for_status()
    data = response.json()
    raw_routes = data.get("routes") or []
    if not raw_routes:
        return None

    formatted = []
    for idx, rt in enumerate(raw_routes, start=1):
        summary = rt.get("summary") or {}
        dist_m = to_float(summary.get("lengthInMeters")) or 0.0
        dur_s = to_float(summary.get("travelTimeInSeconds")) or 0.0
        coords = []
        for leg in rt.get("legs") or []:
            for pt in leg.get("points") or []:
                lat_v = to_float(pt.get("latitude"))
                lon_v = to_float(pt.get("longitude"))
                if valid_coordinates(lat_v, lon_v):
                    coords.append([lon_v, lat_v])
        if len(coords) < 2:
            continue

        turns = []
        for ins in (rt.get("guidance") or {}).get("instructions") or []:
            msg = clean(ins.get("message"))
            if msg:
                turns.append(
                    {
                        "instruction": msg,
                        "road": clean(ins.get("street")),
                        "distance_text": _format_step_distance(ins.get("routeOffsetInMeters") or 0),
                    }
                )

        formatted.append(
            {
                "id": idx,
                "distance_km": round(dist_m / 1000.0, 2),
                "duration_minutes": max(1, round(dur_s / 60.0)),
                "geometry": {"type": "LineString", "coordinates": coords},
                "steps": [],
                "turn_instructions": turns,
                "provider": "TomTom Traffic Routing",
            }
        )

    if not formatted:
        return None

    return {
        "shortest": formatted[0],
        "alternative": formatted[1] if len(formatted) > 1 else None,
        "all_routes": formatted,
        "provider": "TomTom Traffic Routing",
    }


def _route_from_ors(start_lat, start_lon, end_lat, end_lon):
    """Use OpenRouteService free-tier Routing API when ORS_API_KEY is configured."""
    api_key = _env_value("ORS_API_KEY", "")
    if not api_key:
        return None

    response = requests.post(
        "https://api.openrouteservice.org/v2/directions/driving-car/geojson",
        json={
            "coordinates": [[float(start_lon), float(start_lat)], [float(end_lon), float(end_lat)]],
            "alternative_routes": {"target_count": 2, "weight_factor": 1.4, "share_factor": 0.6},
            "instructions": True,
        },
        headers={
            "Authorization": api_key,
            "Content-Type": "application/json",
        },
        timeout=18,
    )
    response.raise_for_status()
    data = response.json()
    features = data.get("features") or []
    if not features:
        return None

    formatted = []
    for idx, feat in enumerate(features, start=1):
        props = feat.get("properties") or {}
        summary = props.get("summary") or {}
        dist_m = to_float(summary.get("distance")) or 0.0
        dur_s = to_float(summary.get("duration")) or 0.0
        geom = feat.get("geometry") or {}

        turns = []
        for seg in props.get("segments") or []:
            for step in seg.get("steps") or []:
                instr = clean(step.get("instruction"))
                if instr:
                    turns.append(
                        {
                            "instruction": instr,
                            "road": clean(step.get("name")),
                            "distance_text": _format_step_distance(step.get("distance") or 0),
                        }
                    )

        formatted.append(
            {
                "id": idx,
                "distance_km": round(dist_m / 1000.0, 2),
                "duration_minutes": max(1, round(dur_s / 60.0)),
                "geometry": geom,
                "steps": [],
                "turn_instructions": turns,
                "provider": "OpenRouteService",
            }
        )

    if not formatted:
        return None

    return {
        "shortest": formatted[0],
        "alternative": formatted[1] if len(formatted) > 1 else None,
        "all_routes": formatted,
        "provider": "OpenRouteService",
    }


def _fallback_mumbai_route_options(start_lat, start_lon, end_lat, end_lon):
    """Generate high-fidelity local geometric route options across Mumbai."""
    dist_direct = haversine_km(start_lat, start_lon, end_lat, end_lon)
    dist_km1 = round(max(0.5, dist_direct * 1.28), 1)
    duration_min1 = max(3, round((dist_km1 / 28.0) * 60))

    num_pts = max(15, min(50, int(dist_km1 * 3)))
    coords1 = []
    for i in range(num_pts + 1):
        frac = i / float(num_pts)
        lat = start_lat + frac * (end_lat - start_lat)
        lon = start_lon + frac * (end_lon - start_lon)
        curve = math.sin(frac * math.pi) * 0.005
        coords1.append([round(lon + curve, 5), round(lat, 5)])

    dist_km2 = round(dist_km1 * 1.10, 1)
    duration_min2 = max(4, round((dist_km2 / 24.0) * 60))
    coords2 = []
    for i in range(num_pts + 1):
        frac = i / float(num_pts)
        lat = start_lat + frac * (end_lat - start_lat)
        lon = start_lon + frac * (end_lon - start_lon)
        curve = math.sin(frac * math.pi) * -0.012
        coords2.append([round(lon + curve, 5), round(lat, 5)])

    routes = [
        {
            "id": 1,
            "distance_km": dist_km1,
            "duration_minutes": duration_min1,
            "geometry": {"type": "LineString", "coordinates": coords1},
            "steps": [],
            "provider": "Dynamic Risk Intelligence Route Engine"
        },
        {
            "id": 2,
            "distance_km": dist_km2,
            "duration_minutes": duration_min2,
            "geometry": {"type": "LineString", "coordinates": coords2},
            "steps": [],
            "provider": "Dynamic Risk Arterial Corridor"
        }
    ]

    return {
        "shortest": routes[0],
        "alternative": routes[1],
        "all_routes": routes,
        "provider": "Dynamic Risk Intelligence Route Engine"
    }


def route_options(start_lat, start_lon, end_lat, end_lon):
    """Calculate a driving route with multiple public OSM routing fallbacks."""
    start_lat = to_float(start_lat)
    start_lon = to_float(start_lon)
    end_lat = to_float(end_lat)
    end_lon = to_float(end_lon)

    if not valid_coordinates(start_lat, start_lon):
        app.logger.warning("Invalid start coordinates: %r, %r", start_lat, start_lon)
        return None

    if not valid_coordinates(end_lat, end_lon):
        app.logger.warning("Invalid destination coordinates: %r, %r", end_lat, end_lon)
        return None

    endpoints = [
        (
            "OSRM demo",
            "https://router.project-osrm.org/route/v1/driving/"
            f"{start_lon},{start_lat};{end_lon},{end_lat}",
        ),
        (
            "OSRM OpenStreetMap.de",
            "https://routing.openstreetmap.de/routed-car/route/v1/driving/"
            f"{start_lon},{start_lat};{end_lon},{end_lat}",
        ),
    ]

    errors = []

    # 1. Try free-tier TomTom (with traffic) and OpenRouteService if API keys are set.
    for opt_name, opt_fn in [
        ("TomTom Traffic Routing", _route_from_tomtom),
        ("OpenRouteService", _route_from_ors),
    ]:
        try:
            opt_res = opt_fn(start_lat, start_lon, end_lat, end_lon)
            if opt_res and opt_res.get("shortest"):
                app.logger.info("Route calculated using %s", opt_name)
                return opt_res
        except (requests.RequestException, ValueError, TypeError, RuntimeError) as exc:
            errors.append(f"{opt_name}: {exc}")
            app.logger.warning("%s failed: %s", opt_name, exc)

    # 2. Try keyless public OSRM-compatible services.
    for name, url in endpoints:
        try:
            result = _route_from_osrm(url, timeout=18, alternatives=True)
            if result and result.get("shortest"):
                app.logger.info("Route calculated using %s", name)
                result["provider"] = name
                result["shortest"]["provider"] = name
                for route in result.get("all_routes", []):
                    route["provider"] = name
                if result.get("alternative"):
                    result["alternative"]["provider"] = name
                return result
        except (
            requests.RequestException,
            ValueError,
            TypeError,
            RuntimeError,
        ) as exc:
            errors.append(f"{name}: {exc}")
            app.logger.warning("%s failed: %s", name, exc)

        # Some public servers can reject detailed alternatives/steps.
        try:
            base_result = _route_from_osrm(url, timeout=18, alternatives=False)
            if base_result and base_result.get("shortest"):
                app.logger.info("Route calculated using %s (basic request)", name)
                base_result["provider"] = f"{name} basic"
                base_result["shortest"]["provider"] = f"{name} basic"
                return base_result
        except (
            requests.RequestException,
            ValueError,
            TypeError,
            RuntimeError,
        ) as exc:
            errors.append(f"{name} basic: {exc}")
            app.logger.warning("%s basic request failed: %s", name, exc)

    # Final public OSM fallback: Valhalla.
    try:
        result = _route_from_valhalla(
            start_lat,
            start_lon,
            end_lat,
            end_lon,
        )
        if result and result.get("shortest"):
            app.logger.info("Route calculated using Valhalla fallback")
            return result
    except (
        requests.RequestException,
        ValueError,
        TypeError,
        RuntimeError,
    ) as exc:
        errors.append(f"Valhalla: {exc}")
        app.logger.warning("Valhalla routing failed: %s", exc)

    if errors:
        app.logger.warning("External routing failed, using Dynamic Risk Intelligence Engine fallback.")
        return _fallback_mumbai_route_options(start_lat, start_lon, end_lat, end_lon)

    return None


# ============================================================
# EMERGENCY SERVICE DATABASE
# ============================================================

def row_value(row, names):
    keys = set(row.keys())

    for name in names:
        if name in keys:
            return row[name]

    return ""


def service_rows(service_type=None):
    requested = (
        normalize_service_type(service_type)
        if service_type
        else None
    )

    if requested and requested not in SERVICE_TABLES:
        return []

    conn = get_db()
    services = []

    try:
        kinds = (
            [requested]
            if requested
            else list(SERVICE_TABLES.keys())
        )

        for kind in kinds:
            table = SERVICE_TABLES[kind]

            if not table_exists(conn, table):
                continue

            rows = conn.execute(
                f'SELECT * FROM "{table}"'
            ).fetchall()

            for row in rows:
                lat = to_float(
                    row_value(
                        row,
                        [
                            "latitude",
                            "lat",
                            "Latitude",
                            "LATITUDE",
                        ],
                    )
                )

                lon = to_float(
                    row_value(
                        row,
                        [
                            "longitude",
                            "lon",
                            "lng",
                            "Longitude",
                            "LONGITUDE",
                        ],
                    )
                )

                if not valid_coordinates(lat, lon):
                    continue

                name = clean(
                    row_value(
                        row,
                        [
                            "name",
                            "Name",
                            "hospital_name",
                            "station_name",
                        ],
                    )
                )

                address = clean(
                    row_value(
                        row,
                        [
                            "address",
                            "Address",
                            "location",
                        ],
                    )
                )

                phone = clean(
                    row_value(
                        row,
                        [
                            "phone",
                            "Phone",
                            "contact",
                            "mobile",
                        ],
                    )
                )

                services.append(
                    {
                        "id": row_value(
                            row,
                            ["id", "ID"],
                        ),
                        "name": (
                            name
                            or SERVICE_LABELS[kind]
                        ),
                        "type": kind,
                        "label": SERVICE_LABELS[kind],
                        "icon": SERVICE_ICONS[kind],
                        "latitude": lat,
                        "longitude": lon,
                        "address": address,
                        "phone": phone,
                    }
                )

    except sqlite3.Error as exc:
        app.logger.warning(
            "Service database error: %s",
            exc,
        )

    finally:
        conn.close()

    return services


def nearest_services(
    lat,
    lon,
    service_type=None,
    limit=8,
):
    lat = to_float(lat)
    lon = to_float(lon)

    if not valid_coordinates(lat, lon):
        return []

    limit = max(
        1,
        min(
            safe_int(limit, 8),
            50,
        ),
    )

    services = service_rows(service_type)

    for item in services:
        item["distance_km"] = round(
            haversine_km(
                lat,
                lon,
                item["latitude"],
                item["longitude"],
            ),
            2,
        )

    services.sort(
        key=lambda item: item["distance_km"]
    )

    return services[:limit]


def route_service_preview(
    route,
    limit=15,
    radius_km=1.0,
):
    if not route:
        return []

    geometry = route.get("geometry")
    if not geometry:
        return []

    coordinates = geometry.get(
        "coordinates",
        [],
    )

    if not coordinates:
        return []

    step = max(
        1,
        len(coordinates) // 100,
    )

    sampled = []

    for point in coordinates[::step]:
        if len(point) < 2:
            continue

        lon = to_float(point[0])
        lat = to_float(point[1])

        if valid_coordinates(lat, lon):
            sampled.append((lat, lon))

    if not sampled:
        return []

    nearby = []

    for service in service_rows():
        closest = min(
            haversine_km(
                route_lat,
                route_lon,
                service["latitude"],
                service["longitude"],
            )
            for route_lat, route_lon in sampled
        )

        if closest <= radius_km:
            item = service.copy()
            item["distance_km"] = round(
                closest,
                2,
            )
            nearby.append(item)

    nearby.sort(
        key=lambda item: item["distance_km"]
    )

    return nearby[:limit]


def _sanitize_tel_number(raw_phone):
    cleaned = re.sub(r"[^0-9+]", "", clean(raw_phone))
    return cleaned if len(cleaned) >= 3 else ""


def route_nearest_help(ranked_routes, per_type=5, radius_km=2.0):
    """Locate nearest hospitals and police stations along the recommended route with callable numbers."""
    if not ranked_routes:
        return {"hospitals": [], "police": [], "all": []}

    route = ranked_routes[0]
    coordinates = (route.get("geometry") or {}).get("coordinates", [])
    if not coordinates:
        return {"hospitals": [], "police": [], "all": []}

    step = max(1, len(coordinates) // 80)
    sampled = []
    for pt in coordinates[::step]:
        if len(pt) >= 2:
            lon = to_float(pt[0])
            lat = to_float(pt[1])
            if valid_coordinates(lat, lon):
                sampled.append((lat, lon))

    if not sampled:
        return {"hospitals": [], "police": [], "all": []}

    def _collect(service_type, fallback_num, fallback_label):
        candidates = []
        for service in service_rows(service_type):
            closest = min(
                haversine_km(rlat, rlon, service["latitude"], service["longitude"])
                for rlat, rlon in sampled
            )
            item = service.copy()
            item["distance_km"] = round(closest, 2)
            direct_tel = _sanitize_tel_number(item.get("phone", ""))
            item["direct_tel"] = direct_tel
            item["has_direct_phone"] = bool(direct_tel)
            item["call_number"] = direct_tel or fallback_num
            item["call_label"] = f"Call {item['phone']}" if direct_tel else fallback_label
            item["emergency_number"] = fallback_num
            candidates.append(item)

        within_radius = [c for c in candidates if c["distance_km"] <= radius_km]
        pool = within_radius if len(within_radius) >= per_type else candidates
        pool.sort(key=lambda c: (c["distance_km"], not c["has_direct_phone"], c["name"].lower()))
        return pool[:per_type]

    hospitals = _collect("hospital", "108", "Call 108 Ambulance")
    police = _collect("police", "100", "Call 100 Police")

    return {
        "hospitals": hospitals,
        "police": police,
        "all": hospitals + police,
    }


# ============================================================
# DASHBOARD DATA
# ============================================================

def dashboard_stats():
    conn = get_db()
    stats = {}

    try:
        for kind, table in SERVICE_TABLES.items():
            if table_exists(conn, table):
                stats[kind] = conn.execute(
                    f'SELECT COUNT(*) FROM "{table}"'
                ).fetchone()[0]
            else:
                stats[kind] = 0
    except sqlite3.Error:
        for kind in SERVICE_TABLES:
            stats.setdefault(kind, 0)
    finally:
        conn.close()

    stats["safety_places"] = len(
        all_safety_places()
    )

    return stats


def save_search_history(search_text):
    user_id = session.get("user_id")
    search_text = clean(search_text)

    if not user_id or not search_text:
        return

    conn = get_db()

    try:
        columns = table_columns(
            conn,
            "search_history",
        )

        if (
            "search_text" in columns
            and "place" in columns
        ):
            conn.execute(
                """
                INSERT INTO search_history
                (user_id, search_text, place, created_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                """,
                (
                    user_id,
                    search_text,
                    search_text,
                ),
            )

        elif "search_text" in columns:
            conn.execute(
                """
                INSERT INTO search_history
                (user_id, search_text, created_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                """,
                (
                    user_id,
                    search_text,
                ),
            )

        elif "place" in columns:
            conn.execute(
                """
                INSERT INTO search_history
                (user_id, place)
                VALUES (?, ?)
                """,
                (
                    user_id,
                    search_text,
                ),
            )

        conn.commit()

    except sqlite3.Error as exc:
        app.logger.warning(
            "Could not save search history: %s",
            exc,
        )

    finally:
        conn.close()


def get_recent_searches(limit=6):
    user_id = session.get("user_id")

    if not user_id:
        return []

    conn = get_db()

    try:
        columns = table_columns(
            conn,
            "search_history",
        )

        search_column = (
            "search_text"
            if "search_text" in columns
            else "place"
            if "place" in columns
            else None
        )

        if not search_column:
            return []

        has_created_at = (
            "created_at" in columns
        )

        if has_created_at:
            rows = conn.execute(
                f"""
                SELECT {search_column} AS search_text,
                       created_at
                FROM search_history
                WHERE user_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (
                    user_id,
                    int(limit),
                ),
            ).fetchall()
        else:
            rows = conn.execute(
                f"""
                SELECT {search_column} AS search_text
                FROM search_history
                WHERE user_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (
                    user_id,
                    int(limit),
                ),
            ).fetchall()

        return [
            {
                "search_text": clean(
                    row["search_text"]
                ),
                "place": clean(
                    row["search_text"]
                ),
                "created_at": (
                    clean(row["created_at"])
                    if "created_at" in row.keys()
                    else ""
                ),
            }
            for row in rows
        ]

    except sqlite3.Error as exc:
        app.logger.warning(
            "Could not load recent searches: %s",
            exc,
        )
        return []

    finally:
        conn.close()


# ============================================================
# TEMPLATE GLOBALS
# ============================================================

@app.context_processor
def inject_globals():
    return {
        "current_user": current_user_record(),
        "service_labels": SERVICE_LABELS,
        "service_icons": SERVICE_ICONS,
        "emergency_contacts": EMERGENCY_CONTACTS,
        "current_year": datetime.now(
            timezone.utc
        ).year,
    }


# ============================================================
# HOME & TOURIST HANGOUT SUGGESTIONS
# ============================================================

_HANGOUT_CATALOG_CACHE = None


def get_hangout_catalog():
    global _HANGOUT_CATALOG_CACHE
    if _HANGOUT_CATALOG_CACHE is None:
        _HANGOUT_CATALOG_CACHE = hangout_places.build_hangout_catalog(
            safety_record,
            nearest_services,
            nearest_station,
        )
    return _HANGOUT_CATALOG_CACHE


def _parse_hangout_filters(args):
    category = clean(args.get("category")) or "all"
    zone = clean(args.get("zone")) or "all"
    search_query = clean(args.get("q"))
    min_score_raw = clean(args.get("min_score"))
    min_score = to_float(min_score_raw) if min_score_raw else None
    sort_by = clean(args.get("sort")) or "recommended"
    night_mode = clean(args.get("night")).lower() in {"1", "true", "yes", "on"}
    hide_closed = clean(args.get("hide_closed")).lower() in {"1", "true", "yes", "on"}
    solo_mode = clean(args.get("solo")).lower() in {"1", "true", "yes", "on"}
    return {
        "category": category,
        "zone": zone,
        "query": search_query,
        "min_score": min_score,
        "min_score_raw": min_score_raw,
        "sort_by": sort_by,
        "night_mode": night_mode,
        "hide_closed": hide_closed,
        "solo_mode": solo_mode,
    }


@app.route("/")
def index():
    catalog = get_hangout_catalog()
    featured_hangouts = [p for p in catalog if p.get("featured")]
    if len(featured_hangouts) < 6:
        featured_hangouts = catalog[:6]

    return render_template(
        "home.html",
        stats=dashboard_stats(),
        featured_hangouts=featured_hangouts[:6],
        hangout_categories=[c for c in hangout_places.HANGOUT_CATEGORIES if c["key"] != "all"],
        hotspots_count=len(ai_model.get_accident_hotspots()),
        total_hangouts=len(catalog),
    )


@app.route("/hangouts")
def hangouts():
    catalog = get_hangout_catalog()
    f = _parse_hangout_filters(request.args)

    filtered = hangout_places.filter_hangout_places(
        catalog,
        category=f["category"],
        zone=f["zone"],
        query=f["query"],
        min_score=f["min_score"],
        sort_by=f["sort_by"],
        night_mode=f["night_mode"],
        hide_closed=f["hide_closed"],
        solo_mode=f["solo_mode"],
    )

    category_counts = {"all": len(catalog)}
    for cat in hangout_places.HANGOUT_CATEGORIES:
        if cat["key"] != "all":
            category_counts[cat["key"]] = sum(1 for p in catalog if p["category"] == cat["key"])

    zones = sorted({p["zone_group"] for p in catalog})
    night_safe_count = sum(1 for p in catalog if p.get("night_safe"))
    solo_safe_count = sum(1 for p in catalog if p.get("solo_safe"))

    return render_template(
        "hangouts.html",
        hangouts=filtered,
        categories=hangout_places.HANGOUT_CATEGORIES,
        category_counts=category_counts,
        zones=zones,
        selected_category=f["category"],
        selected_zone=f["zone"],
        search_query=f["query"],
        min_score=f["min_score_raw"],
        sort_by=f["sort_by"],
        night_mode=f["night_mode"],
        hide_closed=f["hide_closed"],
        solo_mode=f["solo_mode"],
        night_safe_count=night_safe_count,
        solo_safe_count=solo_safe_count,
        total_count=len(catalog),
    )


@app.route("/api/hangouts")
def api_hangouts():
    catalog = get_hangout_catalog()
    f = _parse_hangout_filters(request.args)

    filtered = hangout_places.filter_hangout_places(
        catalog,
        category=f["category"],
        zone=f["zone"],
        query=f["query"],
        min_score=f["min_score"],
        sort_by=f["sort_by"],
        night_mode=f["night_mode"],
        hide_closed=f["hide_closed"],
        solo_mode=f["solo_mode"],
    )
    return jsonify(
        {
            "hangouts": filtered,
            "count": len(filtered),
            "night_mode": f["night_mode"],
            "solo_mode": f["solo_mode"],
        }
    )


# ============================================================
# LOGIN
# ============================================================

@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(
            url_for("dashboard")
        )

    if request.method == "POST":
        email = normalize_email(
            request.form.get("email")
        )
        password = request.form.get(
            "password",
            "",
        )

        if not email or not password:
            return render_template(
                "login.html",
                error=(
                    "Please enter your "
                    "email and password."
                ),
            )

        conn = get_db()

        try:
            user = conn.execute(
                """
                SELECT *
                FROM users
                WHERE email = ?
                """,
                (email,),
            ).fetchone()
        finally:
            conn.close()

        valid = False

        if user:
            password_hash = ""

            if "password_hash" in user.keys():
                password_hash = clean(
                    user["password_hash"]
                )

            # Compatibility with older databases.
            if not password_hash and "password" in user.keys():
                password_hash = clean(
                    user["password"]
                )

            if password_hash:
                try:
                    valid = check_password_hash(
                        password_hash,
                        password,
                    )
                except (
                    ValueError,
                    TypeError,
                ):
                    valid = False

        if valid:
            session.clear()
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session.permanent = True

            next_url = (
                request.args.get("next")
                or request.form.get("next")
            )

            if (
                next_url
                and next_url.startswith("/")
            ):
                return redirect(next_url)

            return redirect(
                url_for("dashboard")
            )

        return render_template(
            "login.html",
            error="Invalid email or password.",
        )

    return render_template(
        "login.html"
    )


# ============================================================
# REGISTER
# ============================================================

@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(
            url_for("dashboard")
        )

    if request.method == "POST":
        name = clean(
            request.form.get("name")
        )
        email = normalize_email(
            request.form.get("email")
        )
        password = request.form.get(
            "password",
            "",
        )

        if len(name) < 2:
            return render_template(
                "register.html",
                error=(
                    "Please enter your full name."
                ),
            )

        if (
            "@" not in email
            or "." not in email.split("@")[-1]
        ):
            return render_template(
                "register.html",
                error=(
                    "Please enter a valid "
                    "email address."
                ),
            )

        if len(password) < 6:
            return render_template(
                "register.html",
                error=(
                    "Password must contain "
                    "at least 6 characters."
                ),
            )

        conn = get_db()
        cursor = conn.cursor()

        try:
            columns = table_columns(
                conn,
                "users",
            )

            if "password_hash" not in columns:
                ensure_column(
                    conn,
                    "users",
                    "password_hash",
                    "TEXT",
                )

            cursor.execute(
                """
                INSERT INTO users
                (name, email, password_hash)
                VALUES (?, ?, ?)
                """,
                (
                    name,
                    email,
                    generate_password_hash(password),
                ),
            )

            conn.commit()
            new_user_id = cursor.lastrowid

            # Automatically log the user in upon successful registration
            session.clear()
            session["user_id"] = new_user_id
            session["user_name"] = name
            session.permanent = True

            return redirect(
                url_for("dashboard")
            )

        except sqlite3.IntegrityError:
            return render_template(
                "register.html",
                error=(
                    "That email address is "
                    "already registered."
                ),
            )
        except Exception as exc:
            app.logger.error("Registration error: %s", exc)
            return render_template(
                "register.html",
                error=(
                    "An error occurred while creating your account. Please try again."
                ),
            )

        finally:
            conn.close()

    return render_template(
        "register.html"
    )


# ============================================================
# GUEST / LOGOUT
# ============================================================

@app.route("/guest")
def guest():
    session.clear()
    session["guest"] = True
    session["user_name"] = "Guest"

    return redirect(
        url_for("dashboard")
    )


@app.route("/logout")
def logout():
    session.clear()

    return redirect(
        url_for("login")
    )


# ============================================================
# FORGOT PASSWORD
# ============================================================

@app.route(
    "/forgot-password",
    methods=["GET", "POST"],
)
def forgot_password():
    if request.method == "POST":
        email = normalize_email(
            request.form.get("email")
        )

        message = (
            "If an account exists for that "
            "email, a password-reset option "
            "has been prepared."
        )

        conn = get_db()

        try:
            user = conn.execute(
                """
                SELECT id
                FROM users
                WHERE email = ?
                """,
                (email,),
            ).fetchone()

            reset_link = None

            if user:
                token = secrets.token_urlsafe(32)

                expires_at = (
                    datetime.now(timezone.utc)
                    + timedelta(minutes=30)
                ).isoformat()

                conn.execute(
                    """
                    INSERT INTO password_reset_tokens
                    (user_id, token, expires_at)
                    VALUES (?, ?, ?)
                    """,
                    (
                        user["id"],
                        token,
                        expires_at,
                    ),
                )

                conn.commit()

                reset_link = url_for(
                    "reset_password",
                    token=token,
                    _external=True,
                )

            return render_template(
                "forgot_password.html",
                message=message,
                reset_link=reset_link,
            )

        finally:
            conn.close()

    return render_template(
        "forgot_password.html"
    )


@app.route(
    "/reset-password/<token>",
    methods=["GET", "POST"],
)
def reset_password(token):
    token = clean(token)

    conn = get_db()

    try:
        row = conn.execute(
            """
            SELECT *
            FROM password_reset_tokens
            WHERE token = ?
              AND used = 0
            """,
            (token,),
        ).fetchone()

        if not row:
            return render_template(
                "reset_password.html",
                error=(
                    "This password-reset link "
                    "is invalid or has already "
                    "been used."
                ),
            )

        try:
            expiry = datetime.fromisoformat(
                clean(row["expires_at"])
            )
            if expiry.tzinfo is None:
                expiry = expiry.replace(
                    tzinfo=timezone.utc
                )
        except ValueError:
            return render_template(
                "reset_password.html",
                error="The reset link is invalid.",
            )

        if datetime.now(timezone.utc) > expiry:
            return render_template(
                "reset_password.html",
                error=(
                    "This reset link has expired. "
                    "Please request a new one."
                ),
            )

        if request.method == "POST":
            password = request.form.get(
                "password",
                "",
            )
            confirm_password = request.form.get(
                "confirm_password",
                "",
            )

            if len(password) < 6:
                return render_template(
                    "reset_password.html",
                    error=(
                        "Password must contain "
                        "at least 6 characters."
                    ),
                )

            if password != confirm_password:
                return render_template(
                    "reset_password.html",
                    error="Passwords do not match.",
                )

            conn.execute(
                """
                UPDATE users
                SET password_hash = ?
                WHERE id = ?
                """,
                (
                    generate_password_hash(password),
                    row["user_id"],
                ),
            )

            conn.execute(
                """
                UPDATE password_reset_tokens
                SET used = 1
                WHERE id = ?
                """,
                (row["id"],),
            )

            conn.commit()

            return redirect(
                url_for("login")
            )

        return render_template(
            "reset_password.html",
            token=token,
        )

    finally:
        conn.close()


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard")
def dashboard():
    location = clean(
        request.args.get("location")
    )
    night_mode = clean(request.args.get("night")).lower() in {"1", "true", "yes", "on"}
    solo_mode = clean(request.args.get("solo")).lower() in {"1", "true", "yes", "on"}

    safety_result = None
    ai_explanation = None
    safety_modes = None
    nearest_station_info = None
    nearest_police_info = None
    nearest_hospital_info = None

    if location:
        save_search_history(location)

        coordinates = is_coordinate_string(location)

        if coordinates:
            safety_result = safety_record_from_coordinates(
                coordinates[0],
                coordinates[1],
            )
            loc_coords = {"lat": coordinates[0], "lon": coordinates[1]}
        else:
            safety_result = safety_record(
                location
            )
            loc_coords = _resolve_place_coords(location, safety_result)

        if loc_coords and valid_coordinates(loc_coords.get("lat"), loc_coords.get("lon")):
            lat_val = loc_coords["lat"]
            lon_val = loc_coords["lon"]
            nearest_station_info = nearest_station(lat_val, lon_val)
            police_hits = nearest_services(lat_val, lon_val, "police", limit=1) or []
            hospital_hits = nearest_services(lat_val, lon_val, "hospital", limit=1) or []
            nearest_police_info = police_hits[0] if police_hits else None
            nearest_hospital_info = hospital_hits[0] if hospital_hits else None

        if safety_result:
            safety_modes = hangout_places.assess_time_and_solo_safety(
                score=safety_result.get("score"),
                lighting=safety_result.get("lighting"),
                best_time=safety_result.get("best_time"),
                notes=safety_result.get("notes"),
                category=safety_result.get("category"),
                police_distance_km=(nearest_police_info.get("distance_km") if nearest_police_info else None),
            )
            try:
                ai_explanation = ai_model.explain_prediction(
                    lighting_score=safety_result.get("lighting", "Good"),
                    category_str=safety_result.get("category", "Commercial"),
                    zone_str=safety_result.get("zone", "South Mumbai"),
                    caution_text=safety_result.get("notes", ""),
                )
            except Exception as e:
                app.logger.warning("AI explanation error: %s", e)

    all_places = all_safety_places()
    catalog = get_hangout_catalog()
    night_safe_spots = [p for p in catalog if p.get("night_safe")][:4]
    solo_safe_spots = [p for p in catalog if p.get("solo_safe")][:4]

    return render_template(
        "dashboard.html",
        safety_result=safety_result,
        ai_explanation=ai_explanation,
        safety_modes=safety_modes,
        nearest_station_info=nearest_station_info,
        nearest_police_info=nearest_police_info,
        nearest_hospital_info=nearest_hospital_info,
        night_mode=night_mode,
        solo_mode=solo_mode,
        night_safe_spots=night_safe_spots,
        solo_safe_spots=solo_safe_spots,
        hotspots=ai_model.get_accident_hotspots()[:4],
        stats=dashboard_stats(),
        recent_places=all_places[:8],
        recent_searches=get_recent_searches(),
        location=location,
    )


# ============================================================
# AI INTELLIGENCE & INSIGHTS (PHASE 2)
# ============================================================

@app.route("/ai-insights")
def ai_insights():
    metrics = ai_model.get_model_metrics()
    hotspots = ai_model.get_accident_hotspots()
    all_places = all_safety_places()
    hangouts_list = get_hangout_catalog()
    place_names = sorted(
        {p["place"] for p in all_places if p.get("place")}
        | {h["name"] for h in hangouts_list if h.get("name")}
    )
    selected_location = clean(request.args.get("location"))
    return render_template(
        "ai_insights.html",
        metrics=metrics,
        hotspots=hotspots,
        place_names=place_names,
        selected_location=selected_location,
    )


@app.route("/api/hotspots")
def api_hotspots():
    return jsonify({
        "success": True,
        "hotspots": ai_model.get_accident_hotspots(),
    })


@app.route("/api/ai-predict", methods=["POST"])
def api_ai_predict():
    data = request.get_json(silent=True) or {}
    location_query = clean(data.get("location"))

    lighting = clean(data.get("lighting")) or "Good"
    category = clean(data.get("category")) or "Commercial"
    zone = clean(data.get("zone")) or "South Mumbai"
    notes = clean(data.get("notes"))

    location_details = None
    if location_query:
        rec = safety_record(location_query)
        matched_hangout = None
        if not rec:
            q_low = location_query.casefold()
            for item in hangout_places.RAW_HANGOUT_PLACES:
                if q_low == item["name"].casefold() or item["name"].casefold() in q_low:
                    matched_hangout = item
                    rec = safety_record(item["safety_lookup"])
                    break

        loc_coords = _resolve_place_coords(location_query, rec)

        station_info = None
        police_info = None
        hospital_info = None
        if loc_coords and valid_coordinates(loc_coords.get("lat"), loc_coords.get("lon")):
            station_info = nearest_station(loc_coords["lat"], loc_coords["lon"])
            p_hits = nearest_services(loc_coords["lat"], loc_coords["lon"], "police", limit=1) or []
            h_hits = nearest_services(loc_coords["lat"], loc_coords["lon"], "hospital", limit=1) or []
            police_info = p_hits[0] if p_hits else None
            hospital_info = h_hits[0] if h_hits else None

        if rec:
            lighting = rec.get("lighting") or lighting
            category = rec.get("category") or category
            zone = rec.get("zone") or zone
            notes = rec.get("notes") or notes

            modes = hangout_places.assess_time_and_solo_safety(
                score=rec.get("score"),
                lighting=lighting,
                best_time=rec.get("best_time"),
                notes=notes,
                category=category,
                open_late=(matched_hangout.get("open_late") if matched_hangout else None),
                police_distance_km=(police_info.get("distance_km") if police_info else None),
            )
            location_details = {
                "matched": True,
                "query": location_query,
                "place": matched_hangout["name"] if matched_hangout else rec.get("place"),
                "safety_record_place": rec.get("place"),
                "zone": zone,
                "category": category,
                "lighting": lighting,
                "best_time": rec.get("best_time") or "Day & Evening Hours",
                "notes": notes,
                "dataset_score": rec.get("score"),
                "night_label": modes["night_label"],
                "night_safe": modes["night_safe"],
                "solo_label": modes["solo_label"],
                "solo_safe": modes["solo_safe"],
                "nearest_station": station_info,
                "nearest_police": (
                    {"name": police_info.get("name"), "distance_km": police_info.get("distance_km")}
                    if police_info
                    else None
                ),
                "nearest_hospital": (
                    {"name": hospital_info.get("name"), "distance_km": hospital_info.get("distance_km")}
                    if hospital_info
                    else None
                ),
            }
        else:
            location_details = {
                "matched": False,
                "query": location_query,
                "place": location_query,
                "zone": zone,
                "category": category,
                "lighting": lighting,
                "notes": notes,
                "nearest_station": station_info,
                "nearest_police": (
                    {"name": police_info.get("name"), "distance_km": police_info.get("distance_km")}
                    if police_info
                    else None
                ),
                "nearest_hospital": (
                    {"name": hospital_info.get("name"), "distance_km": hospital_info.get("distance_km")}
                    if hospital_info
                    else None
                ),
            }

    result = ai_model.explain_prediction(
        lighting_score=lighting,
        category_str=category,
        zone_str=zone,
        caution_text=notes,
    )
    return jsonify({
        "success": True,
        "prediction": result,
        "location_details": location_details,
    })


# ============================================================
# SAFE ROUTE
# ============================================================

@app.route(
    "/safe-route",
    methods=["GET", "POST"],
)
def safe_route():
    if request.method == "POST":
        start = clean(
            request.form.get("start")
        )
        destination = clean(
            request.form.get("destination")
        )
    else:
        start = clean(
            request.args.get("start")
        )
        destination = clean(
            request.args.get("destination")
        )

    route_result = None
    start_safety = None
    destination_safety = None
    error = None

    if destination:
        destination_safety = safety_record(
            destination
        )

    if start:
        start_coordinates = is_coordinate_string(start)

        if start_coordinates:
            start_safety = safety_record_from_coordinates(
                start_coordinates[0],
                start_coordinates[1],
            )
        else:
            start_safety = safety_record(start)

    if start and destination:

        start_location = resolve_location(start)

        destination_location = resolve_location(
            destination
        )

        if not start_location:
            error = (
                "Starting location could not be found. "
                "Please enter a more specific Mumbai location "
                "or use Current Location."
            )

        elif not destination_location:
            error = (
                "Destination could not be found. "
                "Please enter a more specific Mumbai destination."
            )

        else:
            routes = route_options(
                start_location["lat"],
                start_location["lon"],
                destination_location["lat"],
                destination_location["lon"],
            )

            if not routes:
                routes = _fallback_mumbai_route_options(
                    start_location["lat"],
                    start_location["lon"],
                    destination_location["lat"],
                    destination_location["lon"],
                )

            # Score and rank all route alternatives with AI safety scoring
            ranked_routes = ai_model.evaluate_and_rank_routes(
                routes.get("all_routes", []),
                start_lat=start_location["lat"],
                start_lon=start_location["lon"],
                end_lat=destination_location["lat"],
                end_lon=destination_location["lon"],
            )

            route_help = route_nearest_help(ranked_routes)
            route_result = {
                "start": start_location,
                "destination": destination_location,
                "start_name": start,
                "destination_name": destination,
                "routes": routes,
                "ranked_routes": ranked_routes,
                "comparison": ai_model.build_route_comparison(ranked_routes),
                "safest_route": next((r for r in ranked_routes if "Safest" in r.get("badge", "")), ranked_routes[0]),
                "fastest_route": next((r for r in ranked_routes if "Fastest" in r.get("badge", "")), ranked_routes[-1] if len(ranked_routes) > 1 else ranked_routes[0]),
                "hotspots": ai_model.get_accident_hotspots(),
                "nearest_help": route_help,
            }

    conn = get_db()
    community_reports = []
    try:
        cur_comm = conn.cursor()
        cur_comm.execute("SELECT place_name, latitude, longitude, issue_type, severity, description FROM reports WHERE status = 'Active' LIMIT 30")
        community_reports = [dict(r) for r in cur_comm.fetchall()]
    except Exception:
        pass
    finally:
        conn.close()

    return render_template(
        "safe_route.html",
        start=start,
        destination=destination,
        route_result=route_result,
        start_safety=start_safety,
        destination_safety=destination_safety,
        safety=destination_safety,
        community_reports=community_reports,
        emergency_services=(route_result.get("nearest_help", {}).get("all", []) if route_result else []),
        error=error,
    )


# ============================================================
# NAVIGATION
# ============================================================

@app.route("/navigation")
def navigation():
    return redirect(url_for("safe_route", **request.args))
    start = clean(
        request.args.get("start")
    )
    destination = clean(
        request.args.get("destination")
    )

    start_lat = to_float(
        request.args.get("start_lat")
    )
    start_lon = to_float(
        request.args.get("start_lon")
    )
    destination_lat = to_float(
        request.args.get("destination_lat")
    )
    destination_lon = to_float(
        request.args.get("destination_lon")
    )

    error = None
    route_result = None
    destination_safety = None
    nearby_services = []

    if (
        start_lat is not None
        and start_lon is not None
    ):
        start_location = {
            "lat": start_lat,
            "lon": start_lon,
            "display_name": "Current Location",
        }
        if not start:
            start = "Current Location"
    else:
        start_location = (
            resolve_location(start)
            if start
            else None
        )

    if (
        destination_lat is not None
        and destination_lon is not None
    ):
        destination_location = {
            "lat": destination_lat,
            "lon": destination_lon,
            "display_name": (
                destination
                or "Destination"
            ),
        }
    else:
        destination_location = (
            resolve_location(destination)
            if destination
            else None
        )

    if start and destination:
        if not start_location:
            error = (
                "Starting location could not be found. "
                "Try a Mumbai landmark, area or use Current Location."
            )

        elif not destination_location:
            error = (
                "Destination could not be found. "
                "Try a more specific Mumbai destination."
            )

        else:
            routes = route_options(
                start_location["lat"],
                start_location["lon"],
                destination_location["lat"],
                destination_location["lon"],
            )

            if not routes:
                error = (
                    "No road route could be calculated "
                    "between these locations."
                )

            else:
                shortest = routes["shortest"]

                route_result = {
                    "start_lat": start_location["lat"],
                    "start_lon": start_location["lon"],
                    "destination_lat": destination_location["lat"],
                    "destination_lon": destination_location["lon"],
                    "start_name": start,
                    "destination_name": destination,
                    "route": shortest,
                    "routes": routes,
                    "start": start_location,
                    "destination": destination_location,
                }

                destination_safety = (
                    safety_record(destination)
                    if destination
                    else None
                )

                nearby_services = (
                    route_service_preview(
                        shortest
                    )
                )

    return render_template(
        "navigation.html",
        start=start,
        destination=destination,
        route_result=route_result,
        destination_safety=destination_safety,
        nearby_services=nearby_services,
        error=error,
    )


# ============================================================
# SAFETY MAP (Redirected to Safe Route)
# ============================================================

@app.route("/safety-map")
def safety_map():
    destination = clean(request.args.get("location")) or clean(request.args.get("name"))
    if destination:
        return redirect(url_for("safe_route", destination=destination))
    return redirect(url_for("safe_route"))


# ============================================================
# EMERGENCY / SOS
# ============================================================

def search_services(query, service_type=None, limit=30):
    """Search emergency services by name or address keyword."""
    query = clean(query).lower()
    if not query:
        return []
    services = service_rows(service_type)
    matched = []
    for item in services:
        name = clean(item.get("name", "")).lower()
        addr = clean(item.get("address", "")).lower()
        if query in name or query in addr:
            matched.append(item)
            if len(matched) >= limit:
                break
    return matched


@app.route("/emergency")
def emergency():
    lat = to_float(request.args.get("lat"))
    lon = to_float(request.args.get("lon"))
    selected_service = normalize_service_type(request.args.get("service") or "")
    if selected_service not in SERVICE_TABLES:
        selected_service = ""

    ref_lat = lat if lat is not None else 19.0178
    ref_lon = lon if lon is not None else 72.8478

    services = nearest_services(
        ref_lat,
        ref_lon,
        selected_service or None,
        limit=24,
    )

    return render_template(
        "emergency.html",
        stats=dashboard_stats(),
        emergency_contacts=EMERGENCY_CONTACTS,
        services=services,
        selected_service=selected_service,
        current_lat=lat,
        current_lon=lon,
    )


def normalize_sos_email(value):
    """Normalize a recipient email address."""
    email = clean(value).lower()
    if not email:
        return ""

    # Basic email validation suitable for this application.
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return ""

    return email


def send_sos_email(to_email, subject, message, html_message=None):
    """Send a custom SOS email through the configured SMTP account.

    Tries the configured SSL port first. If that connection fails, it
    automatically tries Gmail's STARTTLS port 587. This is useful on
    college/office networks where port 465 may be blocked.
    """
    cfg = load_email_config()
    smtp_host = cfg["host"]
    smtp_port = cfg["port"]
    smtp_user = cfg["user"]
    smtp_password = cfg["password"]

    if not smtp_user or not smtp_password:
        return {
            "success": False,
            "message": (
                "Gmail sender is not configured. Put SMTP_USER and "
                "SMTP_PASSWORD (Google App Password) in .env and restart Flask."
            ),
        }

    if not to_email:
        return {
            "success": False,
            "message": "A valid recipient email address is required.",
        }

    # Give a much clearer message than a raw socket.gaierror when the
    # hostname cannot be resolved.
    try:
        socket.getaddrinfo(smtp_host, smtp_port, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        return {
            "success": False,
            "message": (
                f"Cannot resolve SMTP host '{smtp_host}'. "
                "Keep SMTP_HOST=smtp.gmail.com and check your internet/DNS connection. "
                f"Details: {exc}"
            ),
        }

    mail = EmailMessage()
    mail["From"] = smtp_user
    mail["To"] = to_email
    mail["Subject"] = subject
    mail.set_content(message)

    if html_message:
        mail.add_alternative(html_message, subtype="html")

    errors = []

    # Try preferred SSL port first, then STARTTLS as a fallback.
    connection_methods = []
    if smtp_port == 465:
        connection_methods = [("ssl", 465), ("starttls", 587)]
    else:
        connection_methods = [("starttls", 587), ("ssl", 465)]

    for method, port in connection_methods:
        try:
            if method == "ssl":
                with smtplib.SMTP_SSL(
                    smtp_host,
                    port,
                    timeout=20,
                ) as smtp:
                    smtp.login(smtp_user, smtp_password)
                    smtp.send_message(mail)
            else:
                with smtplib.SMTP(
                    smtp_host,
                    port,
                    timeout=20,
                ) as smtp:
                    smtp.ehlo()
                    smtp.starttls()
                    smtp.ehlo()
                    smtp.login(smtp_user, smtp_password)
                    smtp.send_message(mail)

            return {
                "success": True,
                "message": "SOS email sent successfully.",
                "recipient": to_email,
                "smtp_method": method,
                "smtp_port": port,
            }

        except smtplib.SMTPAuthenticationError as exc:
            code = getattr(exc, "smtp_code", "")
            detail = getattr(exc, "smtp_error", b"")
            if isinstance(detail, bytes):
                detail = detail.decode("utf-8", errors="replace")
            errors.append(
                f"{method}:{port} -> SMTP authentication failed "
                f"({code}): {detail}"
            )
        except smtplib.SMTPConnectError as exc:
            errors.append(f"{method}:{port} -> SMTP connection failed: {exc}")
        except (TimeoutError, ConnectionError, OSError) as exc:
            errors.append(f"{method}:{port} -> network error: {exc}")
        except smtplib.SMTPException as exc:
            errors.append(f"{method}:{port} -> SMTP error: {exc}")

    app.logger.error(
        "SOS email sending failed. %s",
        " | ".join(errors),
    )

    last_error = errors[-1] if errors else "unknown SMTP error"
    lower_error = last_error.lower()

    if "authentication failed" in lower_error or "535" in lower_error:
        user_hint = (
            "Gmail rejected the login. Make sure SMTP_USER is the exact Gmail "
            "account where you created the Google App Password, and paste the "
            "16-character App Password (without spaces) into SMTP_PASSWORD. "
            "Do not use the normal Gmail password."
        )
    elif "cannot connect" in lower_error or "connection failed" in lower_error or "network error" in lower_error:
        user_hint = (
            "The computer could not connect to Gmail SMTP. Check internet access, "
            "firewall/VPN/college-network restrictions, and try port 587."
        )
    else:
        user_hint = (
            "Check SMTP_USER, SMTP_PASSWORD, SMTP_HOST=smtp.gmail.com and "
            "SMTP_PORT=465 in .env."
        )

    return {
        "success": False,
        "message": user_hint,
        "smtp_detail": last_error,
    }


def get_current_user_id():
    """Returns logged-in user_id or default 1 for guest sessions."""
    uid = session.get("user_id")
    if uid:
        return uid
    if "guest_user_id" not in session:
        session["guest_user_id"] = 1
    return session["guest_user_id"]


@app.route("/sos")
def sos():
    user_id = get_current_user_id()
    conn = get_db()
    personal_contacts = []
    try:
        rows = conn.execute(
            """
            SELECT id, user_id, name, phone, relationship, email, is_primary, created_at
            FROM emergency_contacts
            WHERE user_id = ?
            ORDER BY is_primary DESC, id ASC
            """,
            (user_id,)
        ).fetchall()
        personal_contacts = [dict(r) for r in rows]
    except Exception as e:
        print("Error fetching contacts:", e)
    finally:
        conn.close()

    return render_template(
        "sos.html",
        emergency_contacts=EMERGENCY_CONTACTS,
        personal_contacts=personal_contacts,
        email_status=email_configuration_status(),
    )


# ============================================================
# PHASE 4: TRUSTED CONTACTS API
# ============================================================

@app.route("/api/contacts", methods=["GET"])
def api_get_contacts():
    user_id = get_current_user_id()
    conn = get_db()
    try:
        rows = conn.execute(
            """
            SELECT id, user_id, name, phone, relationship, email, is_primary, created_at
            FROM emergency_contacts
            WHERE user_id = ?
            ORDER BY is_primary DESC, id ASC
            """,
            (user_id,)
        ).fetchall()
        return jsonify({"success": True, "contacts": [dict(r) for r in rows]})
    finally:
        conn.close()


@app.route("/api/contacts", methods=["POST"])
def api_add_contact():
    user_id = get_current_user_id()
    data = request.get_json(silent=True) or {}
    name = clean(data.get("name"))
    phone = clean(data.get("phone"))
    relationship = clean(data.get("relationship") or "Family")
    email = normalize_sos_email(data.get("email"))
    is_primary = 1 if data.get("is_primary") else 0

    if not name:
        return jsonify({"success": False, "message": "Contact name is required."}), 400
    if not phone:
        return jsonify({"success": False, "message": "Phone number is required."}), 400

    conn = get_db()
    try:
        if is_primary:
            conn.execute("UPDATE emergency_contacts SET is_primary = 0 WHERE user_id = ?", (user_id,))

        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        cur = conn.execute(
            """
            INSERT INTO emergency_contacts (user_id, name, phone, relationship, email, is_primary, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, name, phone, relationship, email, is_primary, now_str)
        )
        new_id = cur.lastrowid
        conn.commit()
        return jsonify({
            "success": True,
            "message": "Emergency contact added successfully.",
            "contact_id": new_id
        })
    finally:
        conn.close()


@app.route("/api/contacts/<int:contact_id>", methods=["DELETE"])
def api_delete_contact(contact_id):
    user_id = get_current_user_id()
    conn = get_db()
    try:
        conn.execute("DELETE FROM emergency_contacts WHERE id = ? AND user_id = ?", (contact_id, user_id))
        conn.commit()
        return jsonify({"success": True, "message": "Contact deleted successfully."})
    finally:
        conn.close()


@app.route("/api/contacts/<int:contact_id>/primary", methods=["POST"])
def api_set_primary_contact(contact_id):
    user_id = get_current_user_id()
    conn = get_db()
    try:
        conn.execute("UPDATE emergency_contacts SET is_primary = 0 WHERE user_id = ?", (user_id,))
        conn.execute("UPDATE emergency_contacts SET is_primary = 1 WHERE id = ? AND user_id = ?", (contact_id, user_id))
        conn.commit()
        return jsonify({"success": True, "message": "Contact marked as primary emergency contact."})
    finally:
        conn.close()


# ============================================================
# PHASE 4: MULTI-CHANNEL EMERGENCY SOS DISPATCH
# ============================================================

@app.route("/api/sos-send", methods=["POST"])
def api_sos_send():
    """Send immediate multi-channel emergency SOS (Email, WhatsApp, SMS, and Live Tracking)."""
    data = request.get_json(silent=True) or {}
    user_id = get_current_user_id()

    latitude = to_float(data.get("latitude"))
    longitude = to_float(data.get("longitude"))

    if not valid_coordinates(latitude, longitude):
        return jsonify({
            "success": False,
            "message": "A valid current GPS location is required.",
        }), 400

    # Create an automatic live tracking session token for this SOS event
    tracking_token = uuid.uuid4().hex[:10]
    tracking_url = f"{request.host_url.rstrip('/')}/track/{tracking_token}"

    user_name = "User"
    user_rec = current_user_record()
    if user_rec and user_rec.get("name"):
        user_name = user_rec["name"]
    elif data.get("name"):
        user_name = clean(data.get("name"))

    conn = get_db()
    contacts = []
    try:
        # Save tracking session
        conn.execute(
            """
            INSERT INTO tracking_sessions (token, user_id, user_name, active, current_lat, current_lon, trail_json)
            VALUES (?, ?, ?, 1, ?, ?, ?)
            """,
            (tracking_token, user_id, user_name, latitude, longitude, json.dumps([[latitude, longitude]]))
        )
        # Fetch user's emergency contacts
        rows = conn.execute(
            "SELECT id, name, phone, relationship, email, is_primary FROM emergency_contacts WHERE user_id = ?",
            (user_id,)
        ).fetchall()
        contacts = [dict(r) for r in rows]
        conn.commit()
    finally:
        conn.close()

    maps_link = f"https://www.google.com/maps?q={latitude:.6f},{longitude:.6f}"
    generated_at = datetime.now(timezone.utc).strftime("%d %b %Y, %H:%M UTC")

    # Generate multi-channel WhatsApp and SMS alerts for each contact
    whatsapp_links = []
    sms_numbers = []
    for c in contacts:
        phone_raw = c.get("phone", "")
        clean_phone = re.sub(r"[^\d+]", "", phone_raw)
        wa_phone = re.sub(r"[^\d]", "", clean_phone)
        if wa_phone.startswith("0"):
            wa_phone = "91" + wa_phone[1:]
        elif len(wa_phone) == 10:
            wa_phone = "91" + wa_phone

        sos_text = (
            f"🚨 DYNAMIC RISK INTELLIGENCE & SAFETY (DRISTI) — EMERGENCY SOS ALERT!\n\n"
            f"I need immediate help! My live coordinates:\n"
            f"📍 Google Maps: {maps_link}\n"
            f"📡 Live GPS Tracker: {tracking_url}\n"
            f"⏰ Time: {generated_at}\n\n"
            f"Please call or track me immediately!"
        )

        wa_url = f"https://wa.me/{wa_phone}?text={urllib.parse.quote(sos_text)}"
        whatsapp_links.append({
            "name": c.get("name"),
            "relationship": c.get("relationship"),
            "phone": phone_raw,
            "url": wa_url,
            "is_primary": bool(c.get("is_primary"))
        })
        if clean_phone:
            sms_numbers.append(clean_phone)

    # General broadcast WhatsApp link
    general_sos_text = (
        f"🚨 DYNAMIC RISK INTELLIGENCE & SAFETY (DRISTI) — EMERGENCY SOS ALERT!\n\n"
        f"I need immediate emergency help!\n"
        f"📍 Google Maps: {maps_link}\n"
        f"📡 Live GPS Tracker: {tracking_url}\n"
        f"⏰ Time: {generated_at}\n\n"
        f"Please check my location or send assistance immediately!"
    )
    broadcast_whatsapp_link = f"https://api.whatsapp.com/send?text={urllib.parse.quote(general_sos_text)}"

    # Determine recipient email(s)
    recipient_email = normalize_sos_email(data.get("recipient_email") or data.get("email"))
    email_recipients = []
    if recipient_email:
        email_recipients.append((data.get("name") or "Trusted Contact", recipient_email))
    else:
        for c in contacts:
            if c.get("email"):
                email_recipients.append((c.get("name"), c["email"]))
        if not email_recipients:
            cfg = load_email_config()
            env_rec = normalize_sos_email(cfg.get("recipient"))
            if env_rec:
                email_recipients.append(("Guardian", env_rec))

    # Send email alert
    email_success = False
    email_message = "No email addresses available."
    if email_recipients:
        subject = "🚨 DYNAMIC RISK INTELLIGENCE — EMERGENCY SOS ALERT"
        msg_body = (
            f"DYNAMIC RISK INTELLIGENCE — EMERGENCY SOS ALERT\n\n"
            f"An SOS emergency alert has been triggered for {user_name}.\n\n"
            f"Current GPS Location: {latitude:.6f}, {longitude:.6f}\n"
            f"Google Maps Link: {maps_link}\n"
            f"Live GPS Tracker: {tracking_url}\n\n"
            f"Alert Timestamp: {generated_at}\n\n"
            f"Please contact the user or dispatch emergency help immediately."
        )

        safe_name = user_name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        html_body = f"""
        <html>
          <body style=\"font-family:Arial,sans-serif;line-height:1.6;color:#1e293b;max-width:600px;margin:0 auto;padding:20px;\">
            <div style=\"background:#dc2626;color:white;padding:16px 20px;border-radius:12px;text-align:center;\">
              <h2 style=\"margin:0;font-size:22px;\">🚨 EMERGENCY SOS ALERT</h2>
              <p style=\"margin:4px 0 0;font-size:14px;\">Dynamic Risk Intelligence Rapid Response</p>
            </div>
            <div style=\"padding:20px 0;\">
              <p>An emergency SOS alert has been triggered for <strong>{safe_name}</strong>.</p>
              <div style=\"background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:14px;margin:16px 0;\">
                <p style=\"margin:0 0 6px;\"><strong>Coordinates:</strong> {latitude:.6f}, {longitude:.6f}</p>
                <p style=\"margin:0 0 6px;\"><strong>Time:</strong> {generated_at}</p>
              </div>
              <div style=\"display:flex;gap:10px;margin:20px 0;\">
                <a href=\"{maps_link}\" target=\"_blank\" style=\"display:inline-block;padding:12px 20px;background:#0f172a;color:white;text-decoration:none;border-radius:8px;font-weight:bold;margin-right:8px;\">Open in Google Maps</a>
                <a href=\"{tracking_url}\" target=\"_blank\" style=\"display:inline-block;padding:12px 20px;background:#2563eb;color:white;text-decoration:none;border-radius:8px;font-weight:bold;\">Open Live GPS Tracker</a>
              </div>
              <p style=\"font-size:13px;color:#64748b;\">Please call or verify the user's safety immediately if this is an active emergency.</p>
            </div>
          </body>
        </html>
        """

        last_res = None
        for name, to_mail in email_recipients:
            res = send_sos_email(to_mail, subject, msg_body, html_body)
            last_res = res
            if res.get("success"):
                email_success = True

        email_message = last_res.get("message") if last_res else "Email sent."

    return jsonify({
        "success": True,
        "message": "Emergency SOS triggered successfully.",
        "email_sent": email_success,
        "email_message": email_message,
        "tracking_token": tracking_token,
        "tracking_url": tracking_url,
        "maps_link": maps_link,
        "broadcast_whatsapp_link": broadcast_whatsapp_link,
        "whatsapp_links": whatsapp_links,
        "sms_link": f"sms:{','.join(sms_numbers)}?body={urllib.parse.quote(general_sos_text)}" if sms_numbers else "",
        "coordinates": {"lat": latitude, "lon": longitude}
    }), 200


# ============================================================
# PHASE 4: LIVE "WALK WITH ME" TRACKING
# ============================================================

@app.route("/api/tracking/start", methods=["POST"])
def api_tracking_start():
    user_id = get_current_user_id()
    data = request.get_json(silent=True) or {}
    lat = to_float(data.get("latitude") or 19.0760)
    lon = to_float(data.get("longitude") or 72.8777)
    user_name = clean(data.get("user_name")) or "User"

    user_rec = current_user_record()
    if user_rec and user_rec.get("name"):
        user_name = user_rec["name"]

    token = uuid.uuid4().hex[:10]
    tracking_url = f"{request.host_url.rstrip('/')}/track/{token}"

    conn = get_db()
    try:
        conn.execute(
            """
            INSERT INTO tracking_sessions (token, user_id, user_name, active, current_lat, current_lon, trail_json)
            VALUES (?, ?, ?, 1, ?, ?, ?)
            """,
            (token, user_id, user_name, lat, lon, json.dumps([[lat, lon]]))
        )
        conn.commit()
        return jsonify({
            "success": True,
            "token": token,
            "tracking_url": tracking_url,
            "message": "Live tracking started."
        })
    finally:
        conn.close()


@app.route("/api/tracking/update", methods=["POST"])
def api_tracking_update():
    data = request.get_json(silent=True) or {}
    token = clean(data.get("token"))
    lat = to_float(data.get("latitude"))
    lon = to_float(data.get("longitude"))
    heading = to_float(data.get("heading") or 0)
    speed = to_float(data.get("speed") or 0)
    battery = int(data.get("battery") or 100)

    if not token or not valid_coordinates(lat, lon):
        return jsonify({"success": False, "message": "Invalid tracking data."}), 400

    conn = get_db()
    try:
        row = conn.execute("SELECT trail_json, active FROM tracking_sessions WHERE token = ?", (token,)).fetchone()
        if not row:
            return jsonify({"success": False, "message": "Session not found."}), 404
        if not row["active"]:
            return jsonify({"success": False, "message": "Tracking session ended by user.", "active": False})

        trail = json.loads(row["trail_json"] or "[]")
        trail.append([lat, lon])
        if len(trail) > 300:
            trail = trail[-300:]

        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        conn.execute(
            """
            UPDATE tracking_sessions
            SET current_lat = ?, current_lon = ?, heading = ?, speed = ?, battery = ?, last_updated = ?, trail_json = ?
            WHERE token = ?
            """,
            (lat, lon, heading, speed, battery, now_str, json.dumps(trail), token)
        )
        conn.commit()
        return jsonify({"success": True, "active": True})
    finally:
        conn.close()


@app.route("/api/tracking/stop", methods=["POST"])
def api_tracking_stop():
    data = request.get_json(silent=True) or {}
    token = clean(data.get("token"))
    if not token:
        return jsonify({"success": False, "message": "Token required."}), 400

    conn = get_db()
    try:
        conn.execute("UPDATE tracking_sessions SET active = 0 WHERE token = ?", (token,))
        conn.commit()
        return jsonify({"success": True, "message": "Tracking session ended."})
    finally:
        conn.close()


@app.route("/api/tracking/<token>")
def api_tracking_status(token):
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT token, user_name, active, current_lat, current_lon, heading, speed, battery, last_updated, created_at, trail_json FROM tracking_sessions WHERE token = ?",
            (token,)
        ).fetchone()
        if not row:
            return jsonify({"success": False, "message": "Tracking session not found."}), 404

        session_data = dict(row)
        session_data["trail"] = json.loads(session_data.get("trail_json") or "[]")
        return jsonify({"success": True, "session": session_data})
    finally:
        conn.close()


@app.route("/track/<token>")
def track_view(token):
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT token, user_name, active, current_lat, current_lon, heading, speed, battery, last_updated, created_at, trail_json FROM tracking_sessions WHERE token = ?",
            (token,)
        ).fetchone()
        if not row:
            return render_template("track.html", error="Tracking session not found or link has expired.", track_session=None)

        session_data = dict(row)
        session_data["trail"] = json.loads(session_data.get("trail_json") or "[]")
        return render_template("track.html", track_session=session_data, error=None)
    finally:
        conn.close()


@app.route("/api/email-status")
def api_email_status():
    """Show email setup state without exposing credentials."""
    return jsonify({
        "success": True,
        "status": email_configuration_status(),
    })


@app.route("/api/email-test", methods=["POST"])
def api_email_test():
    """Send a simple test email to SOS_EMAIL_TO to diagnose SMTP setup."""
    cfg = load_email_config()
    recipient = normalize_sos_email(cfg.get("recipient"))
    if not recipient:
        return jsonify({
            "success": False,
            "message": "SOS_EMAIL_TO is missing or invalid in .env.",
        }), 400

    result = send_sos_email(
        recipient,
        "Dynamic Risk Intelligence - Email Test",
        "This is a test email from Dynamic Risk Intelligence, Safety & Threat Identification. Your SMTP configuration is working.",
    )
    return jsonify(result), 200


# ============================================================
# REPORT
# ============================================================

# ============================================================
# PHASE 5: COMMUNITY INCIDENT REPORTING & SAFETY NETWORK
# ============================================================

def _compute_report_stats(conn):
    """Compute aggregate community hazard stats across Mumbai."""
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM reports")
    total = cur.fetchone()[0] or 0

    cur.execute("SELECT COUNT(*) FROM reports WHERE status = 'Active'")
    active = cur.fetchone()[0] or 0

    cur.execute("SELECT COUNT(*) FROM reports WHERE status = 'Resolved'")
    resolved = cur.fetchone()[0] or 0

    cur.execute("SELECT COUNT(*) FROM reports WHERE issue_type LIKE '%Streetlight%'")
    streetlights = cur.fetchone()[0] or 0

    cur.execute("SELECT COUNT(*) FROM reports WHERE issue_type LIKE '%Pothole%'")
    potholes = cur.fetchone()[0] or 0

    cur.execute("SELECT COUNT(*) FROM reports WHERE issue_type LIKE '%Waterlogging%' OR issue_type LIKE '%Flood%'")
    waterlogging = cur.fetchone()[0] or 0

    cur.execute("SELECT COUNT(*) FROM reports WHERE issue_type LIKE '%Harassment%' OR issue_type LIKE '%Deserted%'")
    harassment = cur.fetchone()[0] or 0

    return {
        "total": total,
        "active": active,
        "resolved": resolved,
        "streetlights": streetlights,
        "potholes": potholes,
        "waterlogging": waterlogging,
        "harassment": harassment,
    }


@app.route("/report", methods=["GET", "POST"])
def report():
    conn = get_db()
    try:
        if request.method == "POST":
            place_name = clean(request.form.get("place_name") or request.form.get("place"))
            issue_type = clean(request.form.get("issue_type"))
            severity = clean(request.form.get("severity") or "Medium")
            description = clean(request.form.get("description"))
            lat = to_float(request.form.get("latitude"))
            lon = to_float(request.form.get("longitude"))

            if not issue_type or not description:
                stats = _compute_report_stats(conn)
                cur = conn.cursor()
                cur.execute("SELECT * FROM reports ORDER BY id DESC LIMIT 40")
                reports_list = [dict(r) for r in cur.fetchall()]
                return render_template("report.html", reports=reports_list, stats=stats, error="Please select an issue type and provide a brief description.")

            # Geocode coordinates if missing
            if not valid_coordinates(lat, lon) and place_name:
                geo = geocode(place_name)
                if geo:
                    lat, lon = geo["lat"], geo["lon"]

            # Reverse geocode place_name if missing
            if not place_name and valid_coordinates(lat, lon):
                rev = reverse_geocode(lat, lon)
                if rev:
                    place_name = rev["locality"]

            now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO reports (user_id, report_type, place_name, latitude, longitude, issue_type, severity, description, status, upvotes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Active', 1, ?)
                """,
                (get_current_user_id(), "place", place_name or "Mumbai Locality", lat, lon, issue_type, severity or "Medium", description, now_str)
            )
            conn.commit()
            return redirect(url_for("report", success="1"))

        # GET request
        stats = _compute_report_stats(conn)
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, user_id, report_type, place_name, latitude, longitude, issue_type, severity, description, status, upvotes, created_at
            FROM reports
            ORDER BY id DESC
            LIMIT 50
            """
        )
        reports_list = [dict(r) for r in cur.fetchall()]
        success_flag = bool(request.args.get("success"))

        return render_template("report.html", reports=reports_list, stats=stats, success="Your community safety hazard report has been published!" if success_flag else None)
    finally:
        conn.close()


@app.route("/api/reports", methods=["GET"])
def api_get_reports():
    issue_type = clean(request.args.get("issue_type"))
    status_filter = clean(request.args.get("status"))
    limit = int(request.args.get("limit") or 40)

    conn = get_db()
    try:
        query = "SELECT id, user_id, place_name, latitude, longitude, issue_type, severity, description, status, upvotes, created_at FROM reports WHERE 1=1"
        params = []
        if issue_type:
            query += " AND issue_type LIKE ?"
            params.append(f"%{issue_type}%")
        if status_filter:
            query += " AND status = ?"
            params.append(status_filter)

        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)

        cur = conn.cursor()
        cur.execute(query, tuple(params))
        rows = [dict(r) for r in cur.fetchall()]
        stats = _compute_report_stats(conn)

        return jsonify({"success": True, "reports": rows, "stats": stats})
    finally:
        conn.close()


@app.route("/api/reports", methods=["POST"])
def api_create_report():
    data = request.get_json(silent=True) or {}
    place_name = clean(data.get("place_name"))
    issue_type = clean(data.get("issue_type"))
    severity = clean(data.get("severity") or "Medium")
    description = clean(data.get("description"))
    lat = to_float(data.get("latitude"))
    lon = to_float(data.get("longitude"))

    if not issue_type or not description:
        return jsonify({"success": False, "message": "Hazard type and description are required."}), 400

    if not valid_coordinates(lat, lon) and place_name:
        geo = geocode(place_name)
        if geo:
            lat, lon = geo["lat"], geo["lon"]

    if not place_name and valid_coordinates(lat, lon):
        rev = reverse_geocode(lat, lon)
        if rev:
            place_name = rev["locality"]

    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO reports (user_id, report_type, place_name, latitude, longitude, issue_type, severity, description, status, upvotes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Active', 1, ?)
            """,
            (get_current_user_id(), "place", place_name or "Mumbai Area", lat, lon, issue_type, severity, description, now_str)
        )
        report_id = cur.lastrowid
        conn.commit()
        return jsonify({"success": True, "message": "Incident report published to community safety network.", "report_id": report_id})
    finally:
        conn.close()


@app.route("/api/reports/<int:report_id>/upvote", methods=["POST"])
def api_upvote_report(report_id):
    conn = get_db()
    try:
        conn.execute("UPDATE reports SET upvotes = upvotes + 1 WHERE id = ?", (report_id,))
        conn.commit()
        row = conn.execute("SELECT upvotes FROM reports WHERE id = ?", (report_id,)).fetchone()
        upvotes = row[0] if row else 1
        return jsonify({"success": True, "upvotes": upvotes})
    finally:
        conn.close()


@app.route("/api/reports/<int:report_id>/resolve", methods=["POST"])
def api_resolve_report(report_id):
    conn = get_db()
    try:
        conn.execute("UPDATE reports SET status = 'Resolved' WHERE id = ?", (report_id,))
        conn.commit()
        return jsonify({"success": True, "message": "Hazard marked as resolved."})
    finally:
        conn.close()


# ============================================================
# SERVICES API
# ============================================================

@app.route(
    "/api/services",
    methods=["GET", "POST"],
)
def api_services():
    data = (
        request.get_json(silent=True)
        or {}
    )

    selected = (
        request.args.get("service")
        or data.get("service")
        or ""
    )

    selected = normalize_service_type(
        selected
    )

    if (
        selected
        and selected not in SERVICE_TABLES
    ):
        return jsonify(
            {
                "success": False,
                "message": "Unknown service type.",
            }
        ), 400

    return jsonify(
        {
            "success": True,
            "services": service_rows(
                selected or None
            ),
        }
    )


# ============================================================
# NEAREST SERVICES API
# ============================================================

@app.route("/api/nearest")
def api_nearest():
    lat = to_float(
        request.args.get("lat")
    )
    lon = to_float(
        request.args.get("lon")
    )
    q = clean(request.args.get("q", ""))

    selected = normalize_service_type(
        request.args.get("service")
        or request.args.get("type")
        or ""
    )

    limit = safe_int(
        request.args.get("limit", 20),
        20,
    )

    if (
        selected
        and selected not in SERVICE_TABLES
    ):
        return jsonify(
            {
                "success": False,
                "message": "Unknown service type.",
            }
        ), 400

    if q and not valid_coordinates(lat, lon):
        services = search_services(q, selected or None, limit=limit)
        return jsonify(
            {
                "success": True,
                "services": services,
            }
        )

    if not valid_coordinates(lat, lon):
        # Default coordinates: Central Mumbai (Dadar) for immediate display
        lat, lon = 19.0178, 72.8478

    return jsonify(
        {
            "success": True,
            "services": nearest_services(
                lat,
                lon,
                selected or None,
                limit,
            ),
        }
    )


# ============================================================
# ROUTE API
# ============================================================

@app.route(
    "/api/route",
    methods=["GET", "POST"],
)
def api_route():
    data = (
        request.get_json(silent=True)
        or {}
    )

    def request_value(name):
        return (
            request.args.get(name)
            or data.get(name)
        )

    values = [
        to_float(
            request_value(name)
        )
        for name in (
            "start_lat",
            "start_lon",
            "destination_lat",
            "destination_lon",
        )
    ]

    if any(
        value is None
        for value in values
    ):
        return jsonify(
            {
                "success": False,
                "message": (
                    "Four valid coordinates "
                    "are required."
                ),
            }
        ), 400

    route = route_options(*values)

    if not route:
        route = _fallback_mumbai_route_options(*values)

    ranked_routes = ai_model.evaluate_and_rank_routes(
        route.get("all_routes", []),
        start_lat=values[0],
        start_lon=values[1],
        end_lat=values[2],
        end_lon=values[3],
    )

    return jsonify(
        {
            "success": True,
            "route": route,
            "routes": ranked_routes,
            "comparison": ai_model.build_route_comparison(ranked_routes),
            "nearest_help": route_nearest_help(ranked_routes),
            "safest_route": next((r for r in ranked_routes if "Safest" in r.get("badge", "")), ranked_routes[0]),
            "fastest_route": next((r for r in ranked_routes if "Fastest" in r.get("badge", "")), ranked_routes[-1] if len(ranked_routes) > 1 else ranked_routes[0]),
        }
    )


# ============================================================
# SAFETY API
# ============================================================

@app.route("/api/safety")
def api_safety():
    place = clean(
        request.args.get("place")
    )

    if not place:
        return jsonify(
            {
                "success": False,
                "message": "A place is required.",
            }
        ), 400

    result = safety_record(place)

    if not result:
        return jsonify(
            {
                "success": False,
                "message": (
                    "Place not found in the "
                    "Mumbai safety dataset."
                ),
            }
        ), 404

    return jsonify(
        {
            "success": True,
            "safety": result,
        }
    )


# ============================================================
# SEARCH HISTORY API
# ============================================================

@app.route("/api/search-history")
@login_required
def api_search_history():
    return jsonify(
        {
            "success": True,
            "searches": get_recent_searches(20),
        }
    )


# ============================================================
# FAVICON
# ============================================================

@app.route("/favicon.ico")
def favicon():
    return "", 204


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def not_found(_error):
    template_path = os.path.join(
        BASE_DIR,
        "templates",
        "404.html",
    )

    if os.path.exists(template_path):
        return render_template(
            "404.html"
        ), 404

    return (
        "Dynamic Risk Intelligence: Page not found.",
        404,
    )


@app.errorhandler(500)
def server_error(_error):
    app.logger.exception(
        "Unhandled server error"
    )

    template_path = os.path.join(
        BASE_DIR,
        "templates",
        "404.html",
    )

    if os.path.exists(template_path):
        return render_template(
            "404.html",
            server_error=True,
        ), 500

    return (
        "Dynamic Risk Intelligence: Internal server error.",
        500,
    )


# ============================================================
# STARTUP
# ============================================================

initialize_database()

print()
print("=" * 62)
print("   Dynamic Risk Intelligence, Safety & Threat Identification")
print("=" * 62)
print(
    "Intelligent Emergency Assistance & Road Safety System"
)
print("-" * 62)
print(f"Database: {DATABASE_PATH}")
print(f"Safety file: {SAFETY_FILE}")
print(
    f"Safety file exists: "
    f"{os.path.exists(SAFETY_FILE)}"
)
print("Server: http://127.0.0.1:5000")
print("=" * 62)
print()


print("=")
print(
    "Email configuration:",
    email_configuration_status(),
)
print(
    "Tip: keep SMTP_HOST=smtp.gmail.com and use a Google App Password in SMTP_PASSWORD."
)
print()


if __name__ == "__main__":
    debug_value = _env_value("FLASK_DEBUG", "0").lower() in {"1", "true", "yes", "on"}
    host_value = os.environ.get("HOST", "0.0.0.0")
    port_value = int(os.environ.get("PORT", 5000))
    app.run(
        host=host_value,
        port=port_value,
        debug=debug_value,
    )
