import app
import json

client = app.app.test_client()

print("--- Testing Phase 2 AI Intelligence Endpoints ---")

# 1. AI Insights Hub Page
r1 = client.get("/ai-insights")
print(f"1. GET /ai-insights -> {r1.status_code}")
assert r1.status_code == 200, f"Expected 200, got {r1.status_code}"
assert b"Safety Intelligence" in r1.data or b"Explainable AI" in r1.data
assert b"Global Feature Importance" in r1.data
print("   AI Insights page verified!")

# 2. Hotspots API
r2 = client.get("/api/hotspots")
print(f"2. GET /api/hotspots -> {r2.status_code}")
assert r2.status_code == 200
data_hs = r2.get_json()
assert data_hs.get("success") is True
hotspots = data_hs.get("hotspots", [])
print(f"   API Hotspots returned {len(hotspots)} Mumbai corridors")
assert len(hotspots) >= 10, "Expected at least 10 accident hotspots"

# 3. AI Predict & Explain API
r3 = client.post("/api/ai-predict", json={
    "lighting": "Good",
    "category": "Commercial",
    "zone": "South Mumbai",
    "notes": "safe with crowds"
})
print(f"3. POST /api/ai-predict -> {r3.status_code}")
assert r3.status_code == 200
pred_data = r3.get_json()
assert pred_data.get("success") is True
prediction = pred_data.get("prediction", {})
print(f"   Predicted Score: {prediction.get('predicted_score')}, Risk Level: {prediction.get('risk_level')}")
assert len(prediction.get("factors", [])) > 0, "Expected factors in explainability breakdown"
print("   AI Explainability (XAI) API verified!")

# 4. Area Search with AI Explainability
r4 = client.get("/dashboard?location=Marine+Drive")
print(f"4. GET /dashboard?location=Marine+Drive -> {r4.status_code}")
assert r4.status_code == 200
assert b"AI Prediction Explanation" in r4.data
print("   Dashboard XAI Factor Breakdown verified!")

# 5. Hotspots on Dashboard
assert b"Mumbai Accident & Road Hazard Hotspots" in r4.data
print("   Dashboard Accident Hotspot Radar verified!")

print("\n ALL PHASE 2 AI INTELLIGENCE TESTS PASSED SUCCESSFULLY!")
