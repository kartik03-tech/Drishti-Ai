"""
One-time setup/verification helper for Dynamic Risk Intelligence, Safety & Threat Identification.
Run:
    python setup.py
"""
import sqlite3
from pathlib import Path

BASE = Path(__file__).resolve().parent
DB = BASE / "database.db"
DATA = BASE / "data" / "mumbai places safety full.xlsx"

TABLES = ["hospitals", "police_stations", "fire_stations", "pharmacies", "blood_banks"]

if not DB.exists():
    raise SystemExit(f"database.db not found: {DB}")

if not DATA.exists():
    raise SystemExit(f"Safety Excel not found: {DATA}")

conn = sqlite3.connect(DB)
print("Dynamic Risk Intelligence database verification")
for table in TABLES:
    try:
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table:18} {count:>5} records")
    except sqlite3.Error as exc:
        print(f"  {table:18} ERROR: {exc}")
conn.close()
print(f"\nSafety workbook: {DATA}")
print("Setup check completed.")
