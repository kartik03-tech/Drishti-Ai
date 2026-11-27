import app

client = app.app.test_client()

print("--- Testing Phase 1 Endpoints ---")

# 1. Tourist Home Landing Page
r0 = client.get("/")
print(f"0. GET / -> {r0.status_code}")
assert r0.status_code == 200, f"Expected 200, got {r0.status_code}"
assert b"Explore Mumbai Safely" in r0.data
assert b"Hangout Place Suggestions" in r0.data
print("   Tourist Home Landing Page verified!")

# 1b. Dashboard Risk Search
r1 = client.get("/dashboard")
print(f"1. GET /dashboard -> {r1.status_code}")
assert r1.status_code == 200, f"Expected 200, got {r1.status_code}"

# 1c. Hangout Place Suggestions & API
r_hangouts = client.get("/hangouts")
print(f"1c. GET /hangouts -> {r_hangouts.status_code}")
assert r_hangouts.status_code == 200
assert b"Kala Ghoda Cafe" in r_hangouts.data
assert b"Hanging Gardens" in r_hangouts.data
assert b"Gateway of India" in r_hangouts.data

for cat in ["cafe", "restaurant", "garden", "mall", "attraction"]:
    r_api = client.get(f"/api/hangouts?category={cat}")
    assert r_api.status_code == 200
    payload = r_api.get_json()
    assert payload["count"] >= 5, f"Expected >=5 places for {cat}, got {payload['count']}"
    assert payload["hangouts"][0].get("nearest_station") is not None, "Expected nearest station on hangout"

# 1d. After 9 PM Night Mode & Solo / Women-Safe Mode
r_night = client.get("/hangouts?night=1")
assert r_night.status_code == 200
assert b"After 9 PM Mode Active" in r_night.data
assert b"After 9 PM Warning" in r_night.data

r_night_filtered = client.get("/api/hangouts?night=1&hide_closed=1")
assert r_night_filtered.status_code == 200
night_places = r_night_filtered.get_json()["hangouts"]
assert len(night_places) > 0
assert all(p["night_status"] != "avoid" for p in night_places)

r_solo = client.get("/hangouts?solo=1")
assert r_solo.status_code == 200
assert b"Solo &amp; Women-Traveller Safe Mode Active" in r_solo.data
assert b"Walk With Me" in r_solo.data

r_solo_api = client.get("/api/hangouts?solo=1")
assert r_solo_api.status_code == 200
solo_places = r_solo_api.get_json()["hangouts"]
assert len(solo_places) > 0
assert all(p["solo_safe"] for p in solo_places)
print("   Hangout Place Suggestions, Stations, Night & Solo Modes verified!")

# 2. Location Search & Area Risk Assessment
r2 = client.get("/dashboard?location=Bandra+West&night=1&solo=1")
print(f"2. GET /dashboard?location=Bandra+West&night=1&solo=1 -> {r2.status_code}")
assert r2.status_code == 200
assert b"Bandra West" in r2.data, "Bandra West should be in response"
assert b"Nearest Station" in r2.data, "Nearest station should appear on dashboard search"
assert b"After 9 PM Check" in r2.data, "After 9 PM check should appear on dashboard search"
print("   Location Search & Risk Assessment card verified!")

# 3. Emergency Directory
r3 = client.get("/emergency")
print(f"3. GET /emergency -> {r3.status_code}")
assert r3.status_code == 200
assert b"Emergency Services" in r3.data
print("   Emergency Directory verified!")

# 4. Safe Route Navigation Map
r4 = client.get("/safe-route")
print(f"4. GET /safe-route -> {r4.status_code}")
assert r4.status_code == 200
assert b"leafletMap" in r4.data or b"map" in r4.data
print("   Safe Route Navigation verified!")

# 4b. Legacy /safety-map redirects cleanly
r4_redir = client.get("/safety-map")
assert r4_redir.status_code in [200, 302]

# 5. API Nearest Services
r5 = client.get("/api/nearest?lat=19.0178&lon=72.8478&limit=5")
print(f"5. GET /api/nearest -> {r5.status_code}")
assert r5.status_code == 200
services = r5.get_json().get("services", [])
print(f"   API Nearest returned {len(services)} services")
assert len(services) > 0, "Expected services in nearest API"

print("\n ALL PHASE 1 TESTS PASSED SUCCESSFULLY!")
