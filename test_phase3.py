import app
import json

client = app.app.test_client()

print("--- Testing Phase 3 Smart Navigation Endpoints ---")

# 1. Blank Safe Route page
r1 = client.get("/safe-route")
print(f"1. GET /safe-route -> {r1.status_code}")
assert r1.status_code == 200
assert b"Multi-Route Comparison" in r1.data
print("   Safe Route page base render verified!")

# 2. Plan Safe Route: Bandra West to Marine Drive
r2 = client.get("/safe-route?start=Bandra+West&destination=Marine+Drive")
print(f"2. GET /safe-route?start=Bandra+West&destination=Marine+Drive -> {r2.status_code}")
assert r2.status_code == 200
assert b"Route Alternatives" in r2.data
assert b"routeMap" in r2.data
assert (b"Safest Route" in r2.data or b"Safest" in r2.data)
assert b"Recommended Best Route" in r2.data
assert b"Side-by-Side Route Comparison" in r2.data
assert b"Show Both Routes Equally" in r2.data
assert b"Nearest Police Stations" in r2.data
assert b"Nearest Hospitals" in r2.data
assert b"tel:" in r2.data
assert b"Turn-by-Turn Directions" in r2.data
assert b"https://www.google.com/maps/dir/" in r2.data
print("   Multi-Route Comparison & Map Rendering verified!")

# 3. Route API
r3 = client.post("/api/route", json={
    "start_lat": 19.0596,
    "start_lon": 72.8295,
    "destination_lat": 18.9440,
    "destination_lon": 72.8235
})
print(f"3. POST /api/route -> {r3.status_code}")
assert r3.status_code == 200
data_route = r3.get_json()
assert data_route.get("success") is True
routes = data_route.get("routes", [])
comparison = data_route.get("comparison", {})
nearest_help = data_route.get("nearest_help", {})
print(f"   API Route returned {len(routes)} alternatives")
assert len(routes) >= 2, "Expected at least 2 route alternatives"
assert routes[0].get("is_best") is True
assert routes[0].get("google_maps_url", "").startswith("https://www.google.com/maps/dir/")
assert routes[0]["safety_score"] >= routes[1]["safety_score"]
assert comparison.get("best_route_id") == 1
assert len(comparison.get("reasons", [])) >= 1
assert len(nearest_help.get("hospitals", [])) >= 1
assert len(nearest_help.get("police", [])) >= 1
assert all(h.get("call_number") for h in nearest_help["hospitals"])
assert all(p.get("call_number") for p in nearest_help["police"])

for idx, r in enumerate(routes):
    print(f"   Route #{r['id']} ({r.get('badge')}): {r['distance_km']} km, {r['duration_minutes']} mins, Safety Score: {r['safety_score']}/10, Blackspots: {r['hotspots_count']}")
    assert "safety_score" in r
    assert "distance_km" in r
    assert "duration_minutes" in r

print("\n ALL PHASE 3 SMART NAVIGATION TESTS PASSED SUCCESSFULLY!")
