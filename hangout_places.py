"""Curated Mumbai tourist hangout suggestions enriched with safety intelligence."""

HANGOUT_CATEGORIES = [
    {"key": "all", "label": "All Places", "icon": "fa-solid fa-compass"},
    {"key": "cafe", "label": "Cafes", "icon": "fa-solid fa-mug-saucer"},
    {"key": "restaurant", "label": "Restaurants", "icon": "fa-solid fa-utensils"},
    {"key": "garden", "label": "Gardens & Parks", "icon": "fa-solid fa-tree"},
    {"key": "mall", "label": "Malls & Shopping", "icon": "fa-solid fa-bag-shopping"},
    {"key": "attraction", "label": "Tourist Attractions", "icon": "fa-solid fa-landmark"},
]

CATEGORY_META = {
    "cafe": {"label": "Cafe", "icon": "fa-solid fa-mug-saucer", "badge_bg": "#FEF3C7", "badge_color": "#92400E"},
    "restaurant": {"label": "Restaurant", "icon": "fa-solid fa-utensils", "badge_bg": "#FDECEF", "badge_color": "#8F1226"},
    "garden": {"label": "Garden & Park", "icon": "fa-solid fa-tree", "badge_bg": "#ECFDF5", "badge_color": "#065F46"},
    "mall": {"label": "Mall & Shopping", "icon": "fa-solid fa-bag-shopping", "badge_bg": "#EFF6FF", "badge_color": "#1E40AF"},
    "attraction": {"label": "Tourist Attraction", "icon": "fa-solid fa-landmark", "badge_bg": "#F5F3FF", "badge_color": "#5B21B6"},
}

RAW_HANGOUT_PLACES = [
    # Cafes
    {
        "slug": "kala-ghoda-cafe",
        "name": "Kala Ghoda Cafe",
        "category": "cafe",
        "area": "Kala Ghoda",
        "zone": "South Mumbai",
        "zone_group": "South Mumbai",
        "lat": 18.9286,
        "lon": 72.8323,
        "safety_lookup": "Kala Ghoda",
        "highlight": "Artistic heritage cafe tucked in Mumbai's cultural gallery precinct.",
        "vibe": "Specialty Coffee & Brunch",
        "budget": "₹500–₹900 for two",
        "tourist_tip": "Walkable from CSMVS Museum & Jehangir Art Gallery; bustling and well-lit till evening.",
        "featured": True,
    },
    {
        "slug": "leopold-cafe",
        "name": "Leopold Cafe & Bar",
        "category": "cafe",
        "area": "Colaba Causeway",
        "zone": "South Mumbai",
        "zone_group": "South Mumbai",
        "lat": 18.9225,
        "lon": 72.8318,
        "safety_lookup": "Colaba Causeway",
        "highlight": "Iconic 1871 Colaba cafe steps away from Gateway of India.",
        "vibe": "Historic Backpacker Hub",
        "budget": "₹900–₹1,600 for two",
        "tourist_tip": "Lively main road with steady police patrol; keep bags zipped in dense Causeway crowds.",
        "featured": False,
    },
    {
        "slug": "prithvi-cafe",
        "name": "Prithvi Cafe",
        "category": "cafe",
        "area": "Juhu",
        "zone": "Juhu & Santacruz",
        "zone_group": "Western Suburbs",
        "lat": 19.1059,
        "lon": 72.8257,
        "safety_lookup": "Juhu",
        "highlight": "Open-air bamboo garden cafe inside the famous Prithvi Theatre.",
        "vibe": "Theatre Courtyard & Irish Coffee",
        "budget": "₹600–₹1,000 for two",
        "tourist_tip": "Best from late afternoon to evening; use metered rickshaws or app cabs at the theatre gate.",
        "featured": False,
    },
    {
        "slug": "candies-bandra",
        "name": "Candies, Pali Hill",
        "category": "cafe",
        "area": "Bandra West",
        "zone": "Bandra & Khar",
        "zone_group": "Western Suburbs",
        "lat": 19.0604,
        "lon": 72.8266,
        "safety_lookup": "Bandra West",
        "highlight": "Charming multi-level Portuguese villa cafe loved by travellers and locals.",
        "vibe": "Garden Terraces & Bakery",
        "budget": "₹600–₹1,100 for two",
        "tourist_tip": "Busy and welcoming till 10 PM; exit onto main Pali Hill or Carter Road for quick cabs.",
        "featured": False,
    },
    {
        "slug": "yazdani-bakery",
        "name": "Yazdani Bakery & Cafe",
        "category": "cafe",
        "area": "Fort",
        "zone": "South Mumbai",
        "zone_group": "South Mumbai",
        "lat": 18.9329,
        "lon": 72.8351,
        "safety_lookup": "Fort area",
        "highlight": "Century-old Irani bakery famous for warm bun maska and Irani chai.",
        "vibe": "Heritage Irani Cafe",
        "budget": "₹150–₹400 for two",
        "tourist_tip": "Great for morning or daytime heritage walks; Fort lanes become quieter after 8 PM.",
        "featured": False,
    },
    # Restaurants
    {
        "slug": "britannia-and-co",
        "name": "Britannia & Co.",
        "category": "restaurant",
        "area": "Ballard Estate, Fort",
        "zone": "South Mumbai",
        "zone_group": "South Mumbai",
        "lat": 18.9355,
        "lon": 72.8404,
        "safety_lookup": "Fort area",
        "highlight": "Legendary Parsi dining room renowned for Berry Pulao and Salli Boti.",
        "vibe": "Classic Parsi Heritage Dining",
        "budget": "₹1,000–₹1,800 for two",
        "tourist_tip": "Open for lunch hours in calm Ballard Estate; clean sidewalks and safe daytime traffic.",
        "featured": True,
    },
    {
        "slug": "trishna-kala-ghoda",
        "name": "Trishna",
        "category": "restaurant",
        "area": "Kala Ghoda",
        "zone": "South Mumbai",
        "zone_group": "South Mumbai",
        "lat": 18.9293,
        "lon": 72.8327,
        "safety_lookup": "Kala Ghoda",
        "highlight": "Acclaimed Mangalorean seafood restaurant famous for butter-garlic crab.",
        "vibe": "Coastal Fine Dining",
        "budget": "₹1,800–₹3,000 for two",
        "tourist_tip": "Well-lit Fort precinct with steady dinner crowds and easy cab pickups outside.",
        "featured": False,
    },
    {
        "slug": "bademiya-colaba",
        "name": "Bademiya, Colaba",
        "category": "restaurant",
        "area": "Colaba",
        "zone": "South Mumbai",
        "zone_group": "South Mumbai",
        "lat": 18.9228,
        "lon": 72.8322,
        "safety_lookup": "Gateway of India",
        "highlight": "Famous Mumbai kebab & roll institution behind the Taj Mahal Palace.",
        "vibe": "Late-Evening Grill & Rolls",
        "budget": "₹600–₹1,100 for two",
        "tourist_tip": "Very crowded at dinner; dine in the seated section and keep phones/wallets secure.",
        "featured": False,
    },
    {
        "slug": "gajalee-vile-parle",
        "name": "Gajalee, Vile Parle",
        "category": "restaurant",
        "area": "Vile Parle East",
        "zone": "Santacruz & Juhu",
        "zone_group": "Western Suburbs",
        "lat": 19.1003,
        "lon": 72.8482,
        "safety_lookup": "Vile Parle",
        "highlight": "Beloved Malvani seafood spot just minutes from Mumbai Airport.",
        "vibe": "Authentic Coastal Cuisine",
        "budget": "₹1,200–₹2,200 for two",
        "tourist_tip": "Safe commercial street with brisk evening footfall and convenient airport cab access.",
        "featured": False,
    },
    {
        "slug": "mohammed-ali-road",
        "name": "Mohammed Ali Road Food Street",
        "category": "restaurant",
        "area": "Mohammed Ali Road",
        "zone": "South Mumbai",
        "zone_group": "South Mumbai",
        "lat": 18.9531,
        "lon": 72.8342,
        "safety_lookup": "Mohammed Ali Road",
        "highlight": "Iconic culinary trail serving kebabs, malpua, and traditional desserts.",
        "vibe": "Heritage Street Food Walk",
        "budget": "₹300–₹700 for two",
        "tourist_tip": "Go with companions during active evening hours and keep valuables in front pockets.",
        "featured": False,
    },
    # Gardens & Parks
    {
        "slug": "hanging-gardens",
        "name": "Hanging Gardens (Pherozeshah Mehta)",
        "category": "garden",
        "area": "Malabar Hill",
        "zone": "South Mumbai",
        "zone_group": "South Mumbai",
        "lat": 18.9570,
        "lon": 72.8049,
        "safety_lookup": "Hanging Gardens",
        "highlight": "Terraced hilltop gardens offering lush topiary walks and sunset sea views.",
        "vibe": "Scenic Sunset Garden",
        "budget": "Free Entry",
        "tourist_tip": "Family-friendly during open daylight hours; plan exit before evening closing gates.",
        "featured": True,
    },
    {
        "slug": "kamala-nehru-park",
        "name": "Kamala Nehru Park",
        "category": "garden",
        "area": "Malabar Hill",
        "zone": "South Mumbai",
        "zone_group": "South Mumbai",
        "lat": 18.9565,
        "lon": 72.8054,
        "safety_lookup": "Kamala Nehru Park",
        "highlight": "Panoramic Queen's Necklace viewpoint park with the iconic Boot House.",
        "vibe": "Skyline Overlook Park",
        "budget": "Free Entry",
        "tourist_tip": "Well-maintained and safe during morning and sunset hours; pair with Hanging Gardens.",
        "featured": False,
    },
    {
        "slug": "horniman-circle-gardens",
        "name": "Horniman Circle Gardens",
        "category": "garden",
        "area": "Fort",
        "zone": "South Mumbai",
        "zone_group": "South Mumbai",
        "lat": 18.9319,
        "lon": 72.8345,
        "safety_lookup": "Horniman Circle",
        "highlight": "Serene circular green plaza framed by neoclassical Fort architecture.",
        "vibe": "Heritage Urban Oasis",
        "budget": "Free Entry",
        "tourist_tip": "Great shaded rest stop between heritage landmarks; quiet late at night.",
        "featured": False,
    },
    {
        "slug": "shivaji-park",
        "name": "Shivaji Park",
        "category": "garden",
        "area": "Dadar West",
        "zone": "Dadar & Parel",
        "zone_group": "Central Mumbai",
        "lat": 19.0273,
        "lon": 72.8384,
        "safety_lookup": "Shivaji Park",
        "highlight": "Mumbai's historic seafront park famous for evening strolls and cricket.",
        "vibe": "Lively Community Park",
        "budget": "Free Entry",
        "tourist_tip": "Very vibrant and well-lit in evenings with families, walkers, and street snacks.",
        "featured": False,
    },
    {
        "slug": "five-gardens-matunga",
        "name": "Five Gardens",
        "category": "garden",
        "area": "Matunga East",
        "zone": "Dadar & Parel",
        "zone_group": "Central Mumbai",
        "lat": 19.0241,
        "lon": 72.8525,
        "safety_lookup": "Five Gardens",
        "highlight": "Five leafy colonial-era roundabout parks in a calm residential quarter.",
        "vibe": "Quiet Leafy Walk",
        "budget": "Free Entry",
        "tourist_tip": "Peaceful and safe neighbourhood for daytime and early-evening walks.",
        "featured": False,
    },
    {
        "slug": "sanjay-gandhi-national-park",
        "name": "Sanjay Gandhi National Park",
        "category": "garden",
        "area": "Borivali East",
        "zone": "Kandivali & Borivali",
        "zone_group": "Suburbs & Beyond",
        "lat": 19.2147,
        "lon": 72.9106,
        "safety_lookup": "Sanjay Gandhi National Park (main gate)",
        "highlight": "Vast urban forest reserve with cycling trails, boating, and Kanheri Caves.",
        "vibe": "Nature Reserve & Caves",
        "budget": "Nominal Entry Ticket",
        "tourist_tip": "Daytime visits only; leave forested trails well before sunset gate closure.",
        "featured": False,
    },
    # Malls & Shopping
    {
        "slug": "jio-world-drive",
        "name": "Jio World Drive & Centre",
        "category": "mall",
        "area": "BKC",
        "zone": "Bandra Kurla Complex",
        "zone_group": "Central Mumbai",
        "lat": 19.0642,
        "lon": 72.8673,
        "safety_lookup": "Jio World Centre, BKC",
        "highlight": "Upscale lifestyle mall with open-air plaza, drive-in theatre, and cafes.",
        "vibe": "Luxury Mall & Open Plaza",
        "budget": "Mid to Luxury",
        "tourist_tip": "Modern private security, bright lighting, and organised app-cab pickup bays.",
        "featured": True,
    },
    {
        "slug": "high-street-phoenix",
        "name": "High Street Phoenix & Palladium",
        "category": "mall",
        "area": "Lower Parel",
        "zone": "Mahalaxmi & Worli",
        "zone_group": "Central Mumbai",
        "lat": 18.9946,
        "lon": 72.8249,
        "safety_lookup": "High Street Phoenix / Lower Parel",
        "highlight": "Premier mill-compound shopping courtyard, global dining, and cinema.",
        "vibe": "Upscale Courtyard Mall",
        "budget": "Mid to Luxury",
        "tourist_tip": "Well-secured campus till late evening; book cabs from inside the courtyard gate.",
        "featured": False,
    },
    {
        "slug": "phoenix-marketcity-kurla",
        "name": "Phoenix Marketcity, Kurla",
        "category": "mall",
        "area": "Kurla West",
        "zone": "Kurla & Sion",
        "zone_group": "Central Mumbai",
        "lat": 19.0865,
        "lon": 72.8891,
        "safety_lookup": "Phoenix Marketcity, Kurla",
        "highlight": "Expansive indoor mall with Dublin Square events, dining, and arcade.",
        "vibe": "Mega Mall & Entertainment",
        "budget": "Budget to Luxury",
        "tourist_tip": "Safe, air-conditioned indoor complex; use designated cab bays on LBS Marg.",
        "featured": False,
    },
    {
        "slug": "infinity-mall-andheri",
        "name": "Infinity Mall, Andheri West",
        "category": "mall",
        "area": "Andheri West",
        "zone": "Andheri",
        "zone_group": "Western Suburbs",
        "lat": 19.1411,
        "lon": 72.8310,
        "safety_lookup": "Infinity Mall, Andheri",
        "highlight": "Lively Link Road shopping mall with cinema, indoor rides, and food court.",
        "vibe": "Suburban Shopping & Cinema",
        "budget": "Mid-range",
        "tourist_tip": "Well-lit Link Road frontage with metro and auto access just outside.",
        "featured": False,
    },
    {
        "slug": "r-city-mall",
        "name": "R City Mall, Ghatkopar",
        "category": "mall",
        "area": "Ghatkopar West",
        "zone": "Powai & Ghatkopar",
        "zone_group": "Suburbs & Beyond",
        "lat": 19.0997,
        "lon": 72.9165,
        "safety_lookup": "R City Mall, Ghatkopar",
        "highlight": "Sprawling open-courtyard mall featuring KidZania and terrace restaurants.",
        "vibe": "Family Mall & Courtyard",
        "budget": "Mid-range",
        "tourist_tip": "Well-secured premises; plan return cab from the main mall exit.",
        "featured": False,
    },
    {
        "slug": "colaba-causeway-market",
        "name": "Colaba Causeway Market",
        "category": "mall",
        "area": "Colaba",
        "zone": "South Mumbai",
        "zone_group": "South Mumbai",
        "lat": 18.9188,
        "lon": 72.8304,
        "safety_lookup": "Colaba Causeway",
        "highlight": "Famous street-shopping boulevard for jewellery, crafts, clothes & cafes.",
        "vibe": "Tourist Street Bazaar",
        "budget": "Budget Friendly",
        "tourist_tip": "Best from late morning to 8 PM; bargain politely and guard pockets in crowds.",
        "featured": False,
    },
    # Tourist Attractions
    {
        "slug": "gateway-of-india",
        "name": "Gateway of India",
        "category": "attraction",
        "area": "Apollo Bunder, Colaba",
        "zone": "South Mumbai",
        "zone_group": "South Mumbai",
        "lat": 18.9220,
        "lon": 72.8347,
        "safety_lookup": "Gateway of India",
        "highlight": "Mumbai's landmark 1924 waterfront arch and Elephanta Island ferry hub.",
        "vibe": "Iconic Heritage Monument",
        "budget": "Free Entry",
        "tourist_tip": "Heavily policed plaza; avoid unverified boat touts and buy ferry tickets at official booths.",
        "featured": True,
    },
    {
        "slug": "marine-drive",
        "name": "Marine Drive",
        "category": "attraction",
        "area": "Nariman Point to Chowpatty",
        "zone": "South Mumbai",
        "zone_group": "South Mumbai",
        "lat": 18.9438,
        "lon": 72.8235,
        "safety_lookup": "Marine Drive",
        "highlight": "Iconic 3.6 km Queen's Necklace promenade along Back Bay.",
        "vibe": "Sunset & Night Promenade",
        "budget": "Free Entry",
        "tourist_tip": "One of Mumbai's safest, best-lit night spots with steady crowds and police patrol.",
        "featured": True,
    },
    {
        "slug": "csmvs-museum",
        "name": "CSMVS Museum",
        "category": "attraction",
        "area": "Kala Ghoda, Fort",
        "zone": "South Mumbai",
        "zone_group": "South Mumbai",
        "lat": 18.9269,
        "lon": 72.8325,
        "safety_lookup": "CSMVS Museum (Prince of Wales)",
        "highlight": "Grand Indo-Saracenic museum showcasing Indian art, coins & sculptures.",
        "vibe": "Art & History Museum",
        "budget": "Ticketed Entry",
        "tourist_tip": "Gated heritage gardens with security screening; ideal daytime cultural stop.",
        "featured": False,
    },
    {
        "slug": "bandra-bandstand",
        "name": "Bandra Bandstand Promenade",
        "category": "attraction",
        "area": "Bandra West",
        "zone": "Bandra & Khar",
        "zone_group": "Western Suburbs",
        "lat": 19.0462,
        "lon": 72.8195,
        "safety_lookup": "Bandra West",
        "highlight": "Breezy coastal walkway with views of Bandra-Worli Sea Link & Bandra Fort.",
        "vibe": "Seafront Walk & Fort View",
        "budget": "Free Entry",
        "tourist_tip": "Bustling at sunset; stay on the lit promenade and avoid isolated rocks after dark.",
        "featured": False,
    },
    {
        "slug": "haji-ali-dargah",
        "name": "Haji Ali Dargah",
        "category": "attraction",
        "area": "Worli Bay",
        "zone": "Mahalaxmi & Worli",
        "zone_group": "Central Mumbai",
        "lat": 18.9827,
        "lon": 72.8089,
        "safety_lookup": "Haji Ali Dargah",
        "highlight": "Historic 15th-century marble shrine linked by a dramatic sea causeway.",
        "vibe": "Sea-Causeway Landmark",
        "budget": "Free Entry",
        "tourist_tip": "Visit during low tide before dusk; causeway closes when waves rise at high tide.",
        "featured": False,
    },
    {
        "slug": "powai-lake-promenade",
        "name": "Powai Lake Promenade",
        "category": "attraction",
        "area": "Powai",
        "zone": "Powai & Ghatkopar",
        "zone_group": "Suburbs & Beyond",
        "lat": 19.1260,
        "lon": 72.9045,
        "safety_lookup": "Powai Lake",
        "highlight": "Tranquil lakeside walkway next to Hiranandani's cafes and gardens.",
        "vibe": "Lakeside Sunset Walk",
        "budget": "Free Entry",
        "tourist_tip": "Modern, well-lit lakeside promenade popular with families and evening walkers.",
        "featured": False,
    },
]


def _safety_badge(score):
    if score is None:
        return {"label": "Standard Advisory", "level": "moderate"}
    if score >= 7.5:
        return {"label": "High Safety", "level": "safe"}
    if score >= 6.0:
        return {"label": "Moderate Caution", "level": "moderate"}
    return {"label": "Daytime Caution", "level": "caution"}


def build_hangout_catalog(safety_lookup_fn, nearest_service_fn):
    """Enrich curated Mumbai hangout places with live safety scores and nearest help."""
    enriched = []
    for item in RAW_HANGOUT_PLACES:
        record = safety_lookup_fn(item["safety_lookup"]) or {}
        score = record.get("score")
        if score is None:
            score = 7.0
        badge = _safety_badge(score)
        cat_meta = CATEGORY_META.get(
            item["category"],
            {"label": item["category"].title(), "icon": "fa-solid fa-location-dot", "badge_bg": "#FDECEF", "badge_color": "#8F1226"},
        )

        police_list = nearest_service_fn(item["lat"], item["lon"], "police", limit=1) or []
        hospital_list = nearest_service_fn(item["lat"], item["lon"], "hospital", limit=1) or []

        nearest_police = police_list[0] if police_list else None
        nearest_hospital = hospital_list[0] if hospital_list else None

        enriched.append(
            {
                **item,
                "category_label": cat_meta["label"],
                "category_icon": cat_meta["icon"],
                "badge_bg": cat_meta["badge_bg"],
                "badge_color": cat_meta["badge_color"],
                "safety_score": round(float(score), 1),
                "safety_label": badge["label"],
                "safety_level": badge["level"],
                "lighting": record.get("lighting") or "Good",
                "best_time": record.get("best_time") or "Daytime–evening",
                "caution_notes": record.get("notes") or item["tourist_tip"],
                "nearest_police": (
                    {
                        "name": nearest_police.get("name"),
                        "distance_km": nearest_police.get("distance_km"),
                        "phone": nearest_police.get("phone"),
                    }
                    if nearest_police
                    else None
                ),
                "nearest_hospital": (
                    {
                        "name": nearest_hospital.get("name"),
                        "distance_km": nearest_hospital.get("distance_km"),
                        "phone": nearest_hospital.get("phone"),
                    }
                    if nearest_hospital
                    else None
                ),
            }
        )
    return enriched


def filter_hangout_places(catalog, category="all", zone="all", query="", min_score=None, sort_by="recommended"):
    """Filter and sort enriched hangout places."""
    cat = (category or "all").strip().lower()
    zn = (zone or "all").strip().lower()
    q = (query or "").strip().lower()

    results = []
    for place in catalog:
        if cat and cat != "all" and place["category"] != cat:
            continue
        if zn and zn != "all" and place["zone_group"].lower() != zn:
            continue
        if min_score is not None and place["safety_score"] < min_score:
            continue
        if q:
            haystack = " ".join(
                [
                    place["name"],
                    place["area"],
                    place["zone"],
                    place["zone_group"],
                    place["category_label"],
                    place["highlight"],
                    place["vibe"],
                ]
            ).lower()
            if q not in haystack:
                continue
        results.append(place)

    if sort_by == "name":
        results.sort(key=lambda p: p["name"].lower())
    elif sort_by == "safest":
        results.sort(key=lambda p: (-p["safety_score"], p["name"].lower()))
    else:
        results.sort(key=lambda p: (not p.get("featured", False), -p["safety_score"], p["name"].lower()))

    return results
