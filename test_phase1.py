import app

client = app.app.test_client()

print("--- Testing Phase 1 Endpoints ---")

# 1. Dashboard Home
r1 = client.get("/dashboard")
print(f"1. GET /dashboard -> {r1.status_code}")
assert r1.status_code == 200, f"Expected 200, got {r1.status_code}"

# 2. Location Search & Area Risk Assessment
r2 = client.get("/dashboard?location=Bandra+West")
print(f"2. GET /dashboard?location=Bandra+West -> {r2.status_code}")
assert r2.status_code == 200
assert b"Bandra West" in r2.data, "Bandra West should be in response"
print("   Location Search & Risk Assessment card verified!")

# 3. Emergency Directory
r3 = client.get("/emergency")
print(f"3. GET /emergency -> {r3.status_code}")
assert r3.status_code == 200
assert b"Emergency Services" in r3.data
print("   Emergency Directory verified!")

# 4. Interactive Safety Map
r4 = client.get("/safety-map")
print(f"4. GET /safety-map -> {r4.status_code}")
assert r4.status_code == 200
assert b"leafletMap" in r4.data
print("   Interactive Safety Map verified!")

# 5. API Nearest Services
r5 = client.get("/api/nearest?lat=19.0178&lon=72.8478&limit=5")
print(f"5. GET /api/nearest -> {r5.status_code}")
assert r5.status_code == 200
services = r5.get_json().get("services", [])
print(f"   API Nearest returned {len(services)} services")
assert len(services) > 0, "Expected services in nearest API"

print("\n ALL PHASE 1 TESTS PASSED SUCCESSFULLY!")
