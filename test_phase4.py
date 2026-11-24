import json
import app

client = app.app.test_client()

print("--- Testing Phase 4 Emergency Assistance Endpoints ---")

# 1. Test GET /sos Hub
r1 = client.get("/sos")
print(f"1. GET /sos -> {r1.status_code}")
assert r1.status_code == 200, f"Expected 200, got {r1.status_code}"
assert b"Emergency Assistance Hub" in r1.data
assert b"One-Touch SOS" in r1.data
assert b"Walk With Me" in r1.data
assert b"112" in r1.data
print("   Emergency Assistance Hub verified!")

# 2. Test GET /api/contacts
r2 = client.get("/api/contacts")
print(f"2. GET /api/contacts -> {r2.status_code}")
assert r2.status_code == 200
contacts_data = r2.get_json()
assert contacts_data.get("success") is True
contacts = contacts_data.get("contacts", [])
print(f"   Contacts API returned {len(contacts)} contacts")

# 3. Test POST /api/contacts (Add Contact)
r3 = client.post("/api/contacts", json={
    "name": "Sister / Guardian",
    "phone": "+91 99887 76655",
    "relationship": "Family",
    "email": "sister@example.com",
    "is_primary": True
})
print(f"3. POST /api/contacts (Add Contact) -> {r3.status_code}")
assert r3.status_code == 200
add_data = r3.get_json()
assert add_data.get("success") is True
new_contact_id = add_data.get("contact_id")
print(f"   Contact created with ID: {new_contact_id}")

# 4. Test POST /api/contacts/<id>/primary
r4 = client.post(f"/api/contacts/{new_contact_id}/primary")
print(f"4. POST /api/contacts/{new_contact_id}/primary -> {r4.status_code}")
assert r4.status_code == 200
assert r4.get_json().get("success") is True
print("   Primary contact setting verified!")

# 5. Test POST /api/sos-send (Multi-channel dispatch)
r5 = client.post("/api/sos-send", json={
    "latitude": 19.0760,
    "longitude": 72.8777,
    "name": "Test User"
})
print(f"5. POST /api/sos-send -> {r5.status_code}")
assert r5.status_code == 200
sos_res = r5.get_json()
assert sos_res.get("success") is True
assert "tracking_token" in sos_res
assert "tracking_url" in sos_res
assert "broadcast_whatsapp_link" in sos_res
assert len(sos_res.get("whatsapp_links", [])) > 0
print(f"   SOS Dispatched! Live Tracking URL: {sos_res.get('tracking_url')}")
print(f"   WhatsApp Links Generated: {len(sos_res.get('whatsapp_links'))}")

# 6. Test Live Tracking Lifecycle
# 6a. Start Tracking
r6a = client.post("/api/tracking/start", json={
    "latitude": 19.0553,
    "longitude": 72.8267,
    "user_name": "Kartik"
})
print(f"6a. POST /api/tracking/start -> {r6a.status_code}")
assert r6a.status_code == 200
track_res = r6a.get_json()
assert track_res.get("success") is True
token = track_res.get("token")
print(f"    Started tracking with token: {token}")

# 6b. Update Tracking Position
r6b = client.post("/api/tracking/update", json={
    "token": token,
    "latitude": 19.0560,
    "longitude": 72.8275,
    "speed": 18.5,
    "heading": 90
})
print(f"6b. POST /api/tracking/update -> {r6b.status_code}")
assert r6b.status_code == 200
assert r6b.get_json().get("active") is True

# 6c. Get Tracking Status
r6c = client.get(f"/api/tracking/{token}")
print(f"6c. GET /api/tracking/{token} -> {r6c.status_code}")
assert r6c.status_code == 200
sess_data = r6c.get_json().get("session")
assert sess_data.get("active") == 1
assert len(sess_data.get("trail")) >= 2
print(f"    Trail points tracked: {len(sess_data.get('trail'))}, Speed: {sess_data.get('speed')} km/h")

# 6d. View Tracking Web Page
r6d = client.get(f"/track/{token}")
print(f"6d. GET /track/{token} -> {r6d.status_code}")
assert r6d.status_code == 200
assert b"Live Location" in r6d.data
assert b"Kartik" in r6d.data
print("    Live Web Tracking Page render verified!")

# 6e. Stop Tracking
r6e = client.post("/api/tracking/stop", json={"token": token})
print(f"6e. POST /api/tracking/stop -> {r6e.status_code}")
assert r6e.status_code == 200
assert r6e.get_json().get("success") is True
print("    Live tracking successfully stopped!")

# 7. Delete Test Contact
r7 = client.delete(f"/api/contacts/{new_contact_id}")
print(f"7. DELETE /api/contacts/{new_contact_id} -> {r7.status_code}")
assert r7.status_code == 200
assert r7.get_json().get("success") is True
print("   Contact cleanup verified!")

print("\n ALL PHASE 4 EMERGENCY ASSISTANCE TESTS PASSED SUCCESSFULLY!")
