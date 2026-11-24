import app
import ai_model

print("Testing route safety analysis...")

# Test coordinates: Bandra West (19.0596, 72.8295) to Marine Drive (18.9440, 72.8235)
routes = app.route_options(19.0596, 72.8295, 18.9440, 72.8235)
print("Routes returned by OSRM:", len(routes.get("all_routes", [])) if routes else 0)

if routes and routes.get("all_routes"):
    for idx, r in enumerate(routes["all_routes"]):
        coords = r.get("geometry", {}).get("coordinates", [])
        print(f"\nRoute {idx+1}: {r['distance_km']} km, {r['duration_minutes']} mins, {len(coords)} points")
