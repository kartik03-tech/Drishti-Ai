import json
import app

client = app.app.test_client()

print("--- Testing Phase 5 Community Safety Network Endpoints ---")

# 1. Test GET /report
r1 = client.get("/report")
print(f"1. GET /report -> {r1.status_code}")
assert r1.status_code == 200, f"Expected 200, got {r1.status_code}"
assert b"Community Hazard" in r1.data
assert b"Report an Issue" in r1.data
assert b"Live Mumbai Incident Feed" in r1.data
print("   Community Reporting page verified!")

# 2. Test GET /api/reports
r2 = client.get("/api/reports")
print(f"2. GET /api/reports -> {r2.status_code}")
assert r2.status_code == 200
data_rep = r2.get_json()
assert data_rep.get("success") is True
reports = data_rep.get("reports", [])
stats = data_rep.get("stats", {})
print(f"   API returned {len(reports)} reports, Total in DB: {stats.get('total')}")
assert len(reports) >= 1, "Expected at least 1 community report"

# 3. Test POST /api/reports (Publish New Incident Report)
r3 = client.post("/api/reports", json={
    "place_name": "Powai Hiranandani",
    "issue_type": "Broken Streetlight",
    "severity": "Critical",
    "description": "Dark stretch near galleria mall, lights completely off."
})
print(f"3. POST /api/reports -> {r3.status_code}")
assert r3.status_code == 200
res_add = r3.get_json()
assert res_add.get("success") is True
new_rep_id = res_add.get("report_id")
print(f"   Created community report with ID: {new_rep_id}")

# 4. Test POST /api/reports/<id>/upvote
r4 = client.post(f"/api/reports/{new_rep_id}/upvote")
print(f"4. POST /api/reports/{new_rep_id}/upvote -> {r4.status_code}")
assert r4.status_code == 200
assert r4.get_json().get("upvotes") >= 2
print("   Community upvote / verification verified!")

# 5. Test POST /api/reports/<id>/resolve
r5 = client.post(f"/api/reports/{new_rep_id}/resolve")
print(f"5. POST /api/reports/{new_rep_id}/resolve -> {r5.status_code}")
assert r5.status_code == 200
assert r5.get_json().get("success") is True
print("   Community issue resolution verified!")

# 6. Test Safe Route Community Alert Integration
r6 = client.get("/safe-route?start=Bandra+West&destination=Marine+Drive")
print(f"6. GET /safe-route with Community Alerts -> {r6.status_code}")
assert r6.status_code == 200
assert b"Live Citizen Alerts" in r6.data
print("   Safe route community hazard alerts verified!")

print("\n ALL PHASE 5 COMMUNITY SAFETY TESTS PASSED SUCCESSFULLY!")
