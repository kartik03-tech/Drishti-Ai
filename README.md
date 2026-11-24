# Dynamic Risk Intelligence, Safety & Threat Identification (DRISTI)

## What is included
- Flask web application
- Login / registration / guest mode
- Professional responsive UI
- Dashboard with service counts
- Safety-place lookup from the supplied `Mumbai Places Safety` Excel sheet
- Safe Route page using Nominatim geocoding + OSRM routing
- Route map with alternative routes
- Emergency-service directory backed by SQLite
- Nearest emergency-service API
- Safety map using browser-side geocoding
- SOS page with user-initiated 112 call link
- 404 handling and basic validation

## Important data decision
The app uses the supplied Excel workbook as the source for place-level safety records.
The separate `mumbai_safety_data_with_score.csv` is not used by this version because its sample rows contain coordinates outside Mumbai despite the Mumbai label, and its `data_note` explicitly says the coordinates were retained as provided.

## Run
1. Open a terminal in this folder.
2. `python -m venv .venv`
3. Windows: `.venv\Scripts\activate`
4. `pip install -r requirements.txt`
5. `python setup.py`
6. `python app.py`
7. Open http://127.0.0.1:5000

## Project structure
app.py
database.db
data/mumbai places safety full.xlsx
templates/
static/css/style.css
static/js/main.js
setup.py
requirements.txt
