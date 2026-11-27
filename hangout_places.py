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
        "pickup_note": "Well-lit Rampart Row taxi stand & quick app-cab pickup outside gallery lane.",
        "open_late": True,
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
        "pickup_note": "Main Shahid Bhagat Singh Rd metered black-and-yellow cabs & Colaba Police Station nearby.",
        "open_late": True,
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
        "safety_lookup": "Prithvi Theatre",
        "highlight": "Open-air bamboo garden cafe inside the famous Prithvi Theatre.",
        "vibe": "Theatre Courtyard & Irish Coffee",
        "budget": "₹600–₹1,000 for two",
        "tourist_tip": "Best from late afternoon to evening; use metered rickshaws or app cabs at the theatre gate.",
        "pickup_note": "Verified theatre-gate cab/rickshaw drop-off on Janki Kutir Rd with Juhu Chowky nearby.",
        "open_late": True,
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
        "safety_lookup": "Pali Hill",
        "highlight": "Charming multi-level Portuguese villa cafe loved by travellers and locals.",
        "vibe": "Garden Terraces & Bakery",
        "budget": "₹600–₹1,100 for two",
        "tourist_tip": "Busy and welcoming till 10 PM; exit onto main Pali Hill or Carter Road for quick cabs.",
        "pickup_note": "Main Pali Hill / Dr Ambedkar Rd cab pickup & steady evening auto-rickshaws.",
        "open_late": True,
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
        "pickup_note": "Best reached during daytime via Horniman Circle / Flora Fountain main taxi stands.",
        "open_late": False,
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
        "pickup_note": "Wide Ballard Estate heritage avenues with metered taxis outside during lunch hours.",
        "open_late": False,
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
        "pickup_note": "Direct restaurant doorstep cab bay & lit Kala Ghoda main road.",
        "open_late": True,
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
        "pickup_note": "Heavy Colaba police presence near Taj Palace & continuous metered cab line.",
        "open_late": True,
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
        "pickup_note": "Busy Hanuman Road cab/auto frontage 5 mins from Vile Parle station.",
        "open_late": True,
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
        "pickup_note": "Congested lanes; board/alight cabs along the main JJ Flyover stretch.",
        "open_late": True,
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
        "pickup_note": "Main Ridge Road taxi drop-off outside park entrance; closes after evening hours.",
        "open_late": False,
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
        "pickup_note": "Main Malabar Hill Ridge Rd gate; park closes in the evening.",
        "open_late": False,
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
        "pickup_note": "Daytime taxi stand at Asiatic Library steps; surrounding offices empty after dusk.",
        "open_late": False,
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
        "pickup_note": "Well-lit Veer Savarkar Marg perimeter with cabs & Dadar Chowky nearby.",
        "open_late": False,
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
        "pickup_note": "Residential circle near King's Circle station; visit before 9 PM.",
        "open_late": False,
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
        "pickup_note": "Board cabs/autos right outside Western Express Highway main park gate before dusk.",
        "open_late": False,
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
        "pickup_note": "Dedicated indoor valet & security-monitored Uber/Ola pickup bay open late.",
        "open_late": True,
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
        "pickup_note": "24/7 patrolled courtyard gates with dedicated cab pickup lane on Senapati Bapat Marg.",
        "open_late": True,
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
        "pickup_note": "Security-monitored indoor mall pickup zone at Gate 1 (LBS Marg).",
        "open_late": True,
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
        "pickup_note": "Bright Link Road security gate with autos & cabs available until late.",
        "open_late": True,
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
        "pickup_note": "Verified mall main-gate cab bay along LBS Marg with security staff.",
        "open_late": True,
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
        "pickup_note": "Board metered cabs along Shahid Bhagat Singh Rd once shops begin shutting at 9:30 PM.",
        "open_late": False,
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
        "pickup_note": "Continuous Taj Mahal Palace police patrol & official metered taxi queue.",
        "open_late": True,
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
        "pickup_note": "24/7 Marine Drive police patrol & continuous metered cabs along the seafront road.",
        "open_late": True,
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
        "pickup_note": "Regal Circle taxi rank directly outside the main museum gate during daytime hours.",
        "open_late": False,
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
        "safety_lookup": "Bandstand, Bandra",
        "highlight": "Breezy coastal walkway with views of Bandra-Worli Sea Link & Bandra Fort.",
        "vibe": "Seafront Walk & Fort View",
        "budget": "Free Entry",
        "tourist_tip": "Bustling at sunset; stay on the lit promenade and avoid isolated rocks after dark.",
        "pickup_note": "Stick to the lit Taj Lands End / Bandstand Rd side for cabs; avoid Fort rocks after dusk.",
        "open_late": False,
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
        "pickup_note": "Use the pedestrian subway / Haji Ali junction cab stand along Lala Lajpatrai Marg.",
        "open_late": False,
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
        "pickup_note": "Brightly lit Adi Shankaracharya Marg & Hiranandani Gardens cab/auto stands.",
        "open_late": True,
        "featured": False,
    },
    # Additional Cafes
    {
        "slug": "subko-chapel-road",
        "name": "Subko Craft Coffee Roasters",
        "category": "cafe",
        "area": "Chapel Road, Bandra West",
        "zone": "Bandra & Khar",
        "zone_group": "Western Suburbs",
        "lat": 19.0543,
        "lon": 72.8278,
        "safety_lookup": "Pali Hill",
        "highlight": "Specialty Indian craft coffee roastery & bakehouse inside a restored Bandra bungalow.",
        "vibe": "Artisanal Coffee & Pastry",
        "budget": "₹600–₹1,100 for two",
        "tourist_tip": "Quiet lane off Chapel Road; walk out toward Hill Road or Carter Road for quick cabs after dark.",
        "pickup_note": "Quick rickshaw/cab access via adjacent Waroda & Hill Road main junctions.",
        "open_late": False,
        "featured": False,
    },
    {
        "slug": "cafe-mondegar",
        "name": "Cafe Mondegar",
        "category": "cafe",
        "area": "Colaba",
        "zone": "South Mumbai",
        "zone_group": "South Mumbai",
        "lat": 18.9222,
        "lon": 72.8318,
        "safety_lookup": "Colaba Causeway",
        "highlight": "Retro 1932 Colaba cafe famous for Mario Miranda wall murals & classic jukebox.",
        "vibe": "Retro Jukebox & Murals",
        "budget": "₹800–₹1,400 for two",
        "tourist_tip": "Right beside Regal Cinema junction; brightly lit main road with taxis outside till late.",
        "pickup_note": "Regal Circle metered cab stand steps from the entrance.",
        "open_late": True,
        "featured": False,
    },
    {
        "slug": "kyani-and-co",
        "name": "Kyani & Co.",
        "category": "cafe",
        "area": "Dhobi Talao, Marine Lines",
        "zone": "South Mumbai",
        "zone_group": "South Mumbai",
        "lat": 18.9437,
        "lon": 72.8283,
        "safety_lookup": "Metro House / Dhobi Talao",
        "highlight": "Mumbai's oldest 1904 Irani cafe beloved for mawa cake, kheema pav & chai.",
        "vibe": "1904 Heritage Irani Cafe",
        "budget": "₹250–₹550 for two",
        "tourist_tip": "Safe daytime & early-evening breakfast/snack stop near Metro Cinema and Marine Lines station.",
        "pickup_note": "Well-lit Metro Junction taxi stand & 3-minute walk to Marine Lines station.",
        "open_late": False,
        "featured": False,
    },
    {
        "slug": "aromas-powai",
        "name": "Aromas Cafe & Bistro, Powai",
        "category": "cafe",
        "area": "Hiranandani Gardens, Powai",
        "zone": "Powai & Ghatkopar",
        "zone_group": "Suburbs & Beyond",
        "lat": 19.1190,
        "lon": 72.9110,
        "safety_lookup": "Hiranandani Gardens, Powai",
        "highlight": "European-boulevard cafe in Powai's leafy Hiranandani promenade.",
        "vibe": "Boulevard Cafe & All-Day Dining",
        "budget": "₹800–₹1,400 for two",
        "tourist_tip": "Modern, upscale neighbourhood with strong private security and good lighting till late evening.",
        "pickup_note": "Main Hiranandani Central Avenue cab & auto pickup point right outside.",
        "open_late": True,
        "featured": False,
    },
    # Additional Restaurants
    {
        "slug": "the-bombay-canteen",
        "name": "The Bombay Canteen",
        "category": "restaurant",
        "area": "Kamala Mills, Lower Parel",
        "zone": "Mahalaxmi & Worli",
        "zone_group": "Central Mumbai",
        "lat": 19.0005,
        "lon": 72.8286,
        "safety_lookup": "Kamala Mills area",
        "highlight": "Award-winning modern Indian restaurant & cocktail bar celebrating regional flavours.",
        "vibe": "Modern Indian Dining",
        "budget": "₹2,200–₹3,500 for two",
        "tourist_tip": "Located inside gated Kamala Mills compound; book app cabs directly to the compound gate.",
        "pickup_note": "Security-monitored Kamala Mills gate cab bay with Lower Parel station nearby.",
        "open_late": True,
        "featured": False,
    },
    {
        "slug": "cafe-madras-matunga",
        "name": "Cafe Madras",
        "category": "restaurant",
        "area": "Matunga East",
        "zone": "Dadar & Parel",
        "zone_group": "Central Mumbai",
        "lat": 19.0268,
        "lon": 72.8551,
        "safety_lookup": "Matunga Market",
        "highlight": "Iconic 1940 South Indian eatery famous for filter kaapi, tuppa dosa & rasam vada.",
        "vibe": "Classic South Indian Tiffin",
        "budget": "₹250–₹500 for two",
        "tourist_tip": "Very busy morning and lunch hours right opposite King's Circle garden; safe family crowd.",
        "pickup_note": "Steps away from King's Circle station & main Dr Ambedkar Rd taxi stand.",
        "open_late": False,
        "featured": False,
    },
    {
        "slug": "khyber-fort",
        "name": "Khyber Restaurant",
        "category": "restaurant",
        "area": "Kala Ghoda, Fort",
        "zone": "South Mumbai",
        "zone_group": "South Mumbai",
        "lat": 18.9288,
        "lon": 72.8323,
        "safety_lookup": "Kala Ghoda",
        "highlight": "Grand heritage North-West Frontier dining hall featuring M.F. Husain murals.",
        "vibe": "Heritage Fine Dining",
        "budget": "₹2,000–₹3,200 for two",
        "tourist_tip": "Well-lit Kala Ghoda cultural stretch with valet and easy evening cab pickups.",
        "pickup_note": "Valet & main Mahatma Gandhi Rd taxi pickup directly outside.",
        "open_late": True,
        "featured": False,
    },
    {
        "slug": "carter-road-khau-galli",
        "name": "Carter Road Promenade & Food Strip",
        "category": "restaurant",
        "area": "Bandra West",
        "zone": "Bandra & Khar",
        "zone_group": "Western Suburbs",
        "lat": 19.0623,
        "lon": 72.8213,
        "safety_lookup": "Carter Road, Bandra",
        "highlight": "Popular seafront boardwalk lined with cafes, shawarma joints, waffles & dessert bars.",
        "vibe": "Seafront Street Food & Hangout",
        "budget": "₹350–₹800 for two",
        "tourist_tip": "One of Bandra's liveliest evening spots with families and joggers; keep bags close in food queues.",
        "pickup_note": "Brightly lit Carter Road main stretch with continuous autos and app cabs.",
        "open_late": True,
        "featured": False,
    },
    # Additional Gardens & Parks
    {
        "slug": "byculla-zoo-garden",
        "name": "Veermata Jijabai Udyan & Zoo",
        "category": "garden",
        "area": "Byculla East",
        "zone": "Dadar & Parel",
        "zone_group": "Central Mumbai",
        "lat": 18.9788,
        "lon": 72.8351,
        "safety_lookup": "Byculla Zoo (Veermata Jijabai Udyan)",
        "highlight": "160-year-old heritage botanical gardens, penguin exhibit & Bhau Daji Lad Museum.",
        "vibe": "Botanical Garden & Heritage Zoo",
        "budget": "Nominal Entry Ticket",
        "tourist_tip": "Daytime visit only (closes around 5:30 PM); pair with the Bhau Daji Lad Museum at the gate.",
        "pickup_note": "Main Dr Ambedkar Rd gate 2 minutes from Byculla railway station.",
        "open_late": False,
        "featured": False,
    },
    {
        "slug": "oval-maidan",
        "name": "Oval Maidan",
        "category": "garden",
        "area": "Churchgate",
        "zone": "South Mumbai",
        "zone_group": "South Mumbai",
        "lat": 18.9296,
        "lon": 72.8276,
        "safety_lookup": "Oval Maidan",
        "highlight": "Historic 22-acre green ground framed by UNESCO Victorian Gothic & Art Deco buildings.",
        "vibe": "UNESCO Heritage Promenade & Park",
        "budget": "Free Entry",
        "tourist_tip": "Safe and bustling during daytime & early evening cricket/walks; avoid crossing inner turf late at night.",
        "pickup_note": "2-minute walk to Churchgate station & well-lit Maharshi Karve Rd cabs.",
        "open_late": False,
        "featured": False,
    },
    {
        "slug": "mahim-nature-park",
        "name": "Maharashtra Nature Park (BKC Edge)",
        "category": "garden",
        "area": "Sion / BKC Edge",
        "zone": "Dadar & Parel",
        "zone_group": "Central Mumbai",
        "lat": 19.0518,
        "lon": 72.8588,
        "safety_lookup": "Mahim Nature Park",
        "highlight": "37-acre urban biodiversity forest with butterfly trails & Mithi river viewpoints.",
        "vibe": "Urban Eco-Forest Trail",
        "budget": "Nominal Entry Ticket",
        "tourist_tip": "Daytime guided nature walks only; closes before dusk.",
        "pickup_note": "Book cab from the main park gate along Sion–Bandra Link Road before closing.",
        "open_late": False,
        "featured": False,
    },
    # Additional Malls & Shopping
    {
        "slug": "inorbit-mall-malad",
        "name": "Inorbit Mall, Malad West",
        "category": "mall",
        "area": "Malad West",
        "zone": "Jogeshwari & Goregaon",
        "zone_group": "Western Suburbs",
        "lat": 19.1731,
        "lon": 72.8354,
        "safety_lookup": "Inorbit Mall, Malad",
        "highlight": "Spacious New Link Road lifestyle mall with dining atrium, multiplex & fashion stores.",
        "vibe": "Suburban Lifestyle Mall",
        "budget": "Mid-range",
        "tourist_tip": "Well-secured indoor mall open till late evening with easy cab/auto pickups at the front gate.",
        "pickup_note": "Security-staffed New Link Road pickup zone outside main entrance.",
        "open_late": True,
        "featured": False,
    },
    {
        "slug": "linking-road-bandra",
        "name": "Linking Road & Hill Road Shopping",
        "category": "mall",
        "area": "Bandra West",
        "zone": "Bandra & Khar",
        "zone_group": "Western Suburbs",
        "lat": 19.0642,
        "lon": 72.8342,
        "safety_lookup": "Linking Road, Bandra",
        "highlight": "Mumbai's famous street-style footwear, boutique & bargain fashion corridor.",
        "vibe": "Street Fashion & Boutiques",
        "budget": "Budget to Mid",
        "tourist_tip": "Lively until 9:30 PM; watch bags on crowded pavements and use main junctions for autos.",
        "pickup_note": "Brightly lit Linking Road / National College junction with continuous autos & cabs.",
        "open_late": False,
        "featured": False,
    },
    {
        "slug": "crawford-market",
        "name": "Crawford Market (MJP Mandai)",
        "category": "mall",
        "area": "Fort / CSMT",
        "zone": "South Mumbai",
        "zone_group": "South Mumbai",
        "lat": 18.9475,
        "lon": 72.8342,
        "safety_lookup": "Crawford Market",
        "highlight": "1869 Norman-Gothic market hall known for spices, dry fruits, chocolates & fresh produce.",
        "vibe": "Historic Wholesale & Spice Market",
        "budget": "Budget Friendly",
        "tourist_tip": "Visit during daytime hours only; narrow lanes are very congested—keep phones and wallets zipped.",
        "pickup_note": "Board taxis on the main Lokmanya Tilak Marg side near Mumbai Police Headquarters.",
        "open_late": False,
        "featured": False,
    },
    # Additional Tourist Attractions
    {
        "slug": "csmt-heritage-terminus",
        "name": "Chhatrapati Shivaji Maharaj Terminus (CSMT)",
        "category": "attraction",
        "area": "Fort",
        "zone": "South Mumbai",
        "zone_group": "South Mumbai",
        "lat": 18.9398,
        "lon": 72.8355,
        "safety_lookup": "CST (Chhatrapati Shivaji Terminus)",
        "highlight": "UNESCO World Heritage Victorian-Gothic railway station, stunningly illuminated at dusk.",
        "vibe": "UNESCO Heritage Landmark",
        "budget": "Free Exterior Viewing",
        "tourist_tip": "View the illuminated facade from the pedestrian subway/heritage plaza; watch belongings in commuter rush.",
        "pickup_note": "Adjacent to CSMT station taxi bay & major bus/metro links.",
        "open_late": False,
        "featured": False,
    },
    {
        "slug": "global-vipassana-pagoda",
        "name": "Global Vipassana Pagoda",
        "category": "attraction",
        "area": "Gorai",
        "zone": "Kandivali & Borivali",
        "zone_group": "Suburbs & Beyond",
        "lat": 19.2283,
        "lon": 72.8059,
        "safety_lookup": "Global Vipassana Pagoda",
        "highlight": "Monumental golden stone meditation dome overlooking Gorai Creek.",
        "vibe": "Peaceful Spiritual Monument",
        "budget": "Free Entry",
        "tourist_tip": "Peaceful, well-maintained daytime attraction; check Gorai ferry timings before sunset.",
        "pickup_note": "Return via official Gorai Creek ferry to Marve/Borivali before evening.",
        "open_late": False,
        "featured": False,
    },
    {
        "slug": "siddhivinayak-temple",
        "name": "Siddhivinayak Temple",
        "category": "attraction",
        "area": "Prabhadevi",
        "zone": "Dadar & Parel",
        "zone_group": "Central Mumbai",
        "lat": 19.0169,
        "lon": 72.8304,
        "safety_lookup": "Siddhivinayak Temple, Prabhadevi",
        "highlight": "Iconic 1801 Ganesha temple with organised security & visitor walkways.",
        "vibe": "Revered Cultural Landmark",
        "budget": "Free Entry",
        "tourist_tip": "Heavily secured temple campus; Tuesdays are busiest—keep footwear & bags at official counters.",
        "pickup_note": "Main S.K. Bole Road & Gokhale Road taxi/cab stands right outside security gate.",
        "open_late": True,
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


def assess_time_and_solo_safety(
    score,
    lighting,
    best_time,
    notes="",
    category="",
    open_late=None,
    police_distance_km=None,
):
    """Evaluate After-9-PM safety and Solo & Women-Traveller suitability consistently."""
    score_val = float(score) if score is not None else 6.5
    light_l = (lighting or "").lower()
    time_l = (best_time or "").lower()
    notes_l = (notes or "").lower()
    cat_l = (category or "").lower()
    combined = f"{time_l} {notes_l}"

    daytime_only_markers = [
        "daytime only",
        "day visits only",
        "day only",
        "closes",
        "avoid after dark",
        "avoid after closing",
        "no night",
        "quiet at night",
        "quiet after",
        "quieter",
        "isolated",
        "fewer visitors after dark",
        "less patrolled",
        "ferry hours",
        "museum hours",
        "gallery hours",
        "park hours",
        "early morning only",
        "sunset only",
        "high tide",
    ]
    is_daytime_only = (
        open_late is False
        or "poor" in light_l
        or "limited" in light_l
        or any(marker in combined for marker in daytime_only_markers)
    )

    good_lighting = "good" in light_l
    late_markers = ["late night", "late evening", "night spot"]
    has_late_signal = any(m in combined for m in late_markers)

    if is_daytime_only and not (open_late is True and score_val >= 7.5 and good_lighting):
        if "park" in cat_l or "garden" in cat_l or "beach" in cat_l or "closes" in combined:
            night_advisory = (
                "After 9 PM Warning: Typically closes at dusk or gets quiet/dim after dark—plan your visit during daylight or sunset."
            )
        else:
            night_advisory = (
                "After 9 PM Warning: Reduced evening footfall or limited hours—prefer daytime visits or stick to lit main roads."
            )
        night_status = "avoid"
        night_label = "Daytime Only / Closes at Dusk"
    elif (has_late_signal or open_late is True) and score_val >= 7.0 and good_lighting:
        night_status = "safe"
        night_label = "Safe After 9 PM"
        night_advisory = (
            "Recommended After 9 PM: Bright street lighting, steady late-evening footfall, and active nearby security/patrol."
        )
    elif score_val >= 7.5 and good_lighting and "early evening" not in time_l:
        night_status = "safe"
        night_label = "Safe After 9 PM"
        night_advisory = (
            "Recommended After 9 PM: Well-lit high-activity zone suitable for evening visits; stick to main streets when leaving."
        )
    else:
        night_status = "caution"
        night_label = "Use Caution After 9 PM"
        night_advisory = (
            "Moderate Caution After 9 PM: Stay in busy, well-lit stretches, watch belongings in crowds, and book a verified cab."
        )

    police_close = police_distance_km is None or police_distance_km <= 2.5
    solo_safe = (
        score_val >= 7.0
        and good_lighting
        and night_status != "avoid"
        and police_close
    )

    if solo_safe:
        solo_label = "Solo & Women-Safe Verified"
        solo_reason = (
            "Brightly lit, high-footfall area with nearby police presence and straightforward main-road cab/station access."
        )
    else:
        solo_label = "Best in Daytime / Group"
        solo_reason = (
            "Lower lighting, quieter late hours, or denser crowd pockets—prefer daytime visits, travel with companions, or keep Walk With Me active."
        )

    return {
        "night_safe": night_status == "safe",
        "night_status": night_status,
        "night_label": night_label,
        "night_advisory": night_advisory,
        "solo_safe": solo_safe,
        "solo_label": solo_label,
        "solo_reason": solo_reason,
    }


def build_hangout_catalog(safety_lookup_fn, nearest_service_fn, nearest_station_fn=None):
    """Enrich curated Mumbai hangout places with live safety scores, night/solo assessment, and nearest help."""
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
        station_info = nearest_station_fn(item["lat"], item["lon"]) if nearest_station_fn else None

        lighting = record.get("lighting") or "Good"
        best_time = record.get("best_time") or "Daytime–evening"
        caution_notes = record.get("notes") or item["tourist_tip"]

        safety_modes = assess_time_and_solo_safety(
            score=score,
            lighting=lighting,
            best_time=best_time,
            notes=caution_notes,
            category=item["category"],
            open_late=item.get("open_late"),
            police_distance_km=(nearest_police.get("distance_km") if nearest_police else None),
        )

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
                "lighting": lighting,
                "best_time": best_time,
                "caution_notes": caution_notes,
                **safety_modes,
                "nearest_station": station_info,
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


def filter_hangout_places(
    catalog,
    category="all",
    zone="all",
    query="",
    min_score=None,
    sort_by="recommended",
    night_mode=False,
    hide_closed=False,
    solo_mode=False,
):
    """Filter and sort enriched hangout places with optional After-9-PM and Solo/Women-Safe modes."""
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
        if solo_mode and not place.get("solo_safe"):
            continue
        if night_mode and hide_closed and place.get("night_status") == "avoid":
            continue
        if q:
            station_name = (place.get("nearest_station") or {}).get("station", "")
            haystack = " ".join(
                [
                    place["name"],
                    place["area"],
                    place["zone"],
                    place["zone_group"],
                    place["category_label"],
                    place["highlight"],
                    place["vibe"],
                    station_name,
                ]
            ).lower()
            if q not in haystack:
                continue
        results.append(place)

    night_rank = {"safe": 0, "caution": 1, "avoid": 2}
    if night_mode and sort_by == "recommended":
        results.sort(
            key=lambda p: (
                night_rank.get(p.get("night_status", "caution"), 1),
                -p["safety_score"],
                p["name"].lower(),
            )
        )
    elif sort_by == "name":
        results.sort(key=lambda p: p["name"].lower())
    elif sort_by == "safest":
        results.sort(key=lambda p: (-p["safety_score"], p["name"].lower()))
    else:
        results.sort(key=lambda p: (not p.get("featured", False), -p["safety_score"], p["name"].lower()))

    return results
