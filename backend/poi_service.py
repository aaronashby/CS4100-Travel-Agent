import requests
import random
import time

WIKIPEDIA_API_URL = "https://en.wikipedia.org/w/api.php"

# Keywords to try and guess the category of a Wikipedia article
CATEGORY_KEYWORDS = {
    "Museums": ["museum", "gallery", "art", "history", "exhibition", "institute", "memorial"],
    "Outdoors": ["park", "garden", "forest", "lake", "river", "mountain", "beach", "square"],
    "Food & Drink": ["restaurant", "cafe", "market", "brewery", "distillery", "vineyard", "bistro", "pub"],
    "Shopping": ["mall", "market", "street", "avenue", "boutique", "plaza"],
    "Nightlife": ["club", "bar", "pub", "theater", "theatre", "music", "lounge"],
    "Relaxation": ["spa", "beach", "resort", "retreat", "bath", "park"],
}

# Words that usually indicate an event or historical period rather than a place
EXCLUDE_WORDS = [
    "timeline", "siege", "battle", "war", "treaty", "history", "century", 
    "empire", "republic", "dynasty", "assassination", "commune", "riot", 
    "epidemic", "scandal", "conference", "summit", "scandal"
]


def _fetch_wikipedia_places(lat, lon, radius=10000, limit=200):
    """Fetch nearby Wikipedia articles with coordinates."""
    params = {
        "action": "query",
        "list": "geosearch",
        "gscoord": f"{lat}|{lon}",
        "gsradius": radius,
        "gslimit": limit,
        "format": "json"
    }
    headers = {"User-Agent": "CS4100-Travel-Agent/1.0 (Student Project)"}
    try:
        resp = requests.get(WIKIPEDIA_API_URL, params=params, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("query", {}).get("geosearch", [])
    except Exception as e:
        print(f"  [POI] Wikipedia API failed: {e}")
    return []


def _guess_category(title, requested_activities):
    """Guess category based on keywords, or return a random requested activity."""
    title_lower = title.lower()
    
    # Filter out obvious non-places (historical events, etc)
    if any(word in title_lower for word in EXCLUDE_WORDS):
        return None
        
    # Try to match keywords
    for act in requested_activities:
        keywords = CATEGORY_KEYWORDS.get(act, [])
        if any(kw in title_lower for kw in keywords):
            return act
            
    # Default: assign it randomly to one of the requested activities
    if requested_activities:
        return random.choice(requested_activities)
    return "Local Attraction"


def fetch_city_pois(lat, lon, activities, radius_m=10000, limit_per_cat=15):
    """
    Fetch real places from Wikipedia Geosearch. This is extremely fast
    and reliable compared to Overpass/Wikidata.
    """
    if not activities:
        activities = ["Museums", "Food & Drink", "Outdoors"]

    print(f"  [POI] Fetching Wikipedia POIs near ({lat:.2f}, {lon:.2f})...")
    raw_places = _fetch_wikipedia_places(lat, lon, radius=radius_m)
    
    if not raw_places:
        print("  [POI] No places found via Wikipedia.")
        return []

    categorized_pois = {act: [] for act in activities}
    
    for place in raw_places:
        title = place.get("title", "")
        plat = place.get("lat")
        plon = place.get("lon")
        
        category = _guess_category(title, activities)
        if category and category in categorized_pois:
            categorized_pois[category].append({
                "name": title,
                "lat": plat,
                "lon": plon,
                "category": category
            })

    # Flatten and limit per category
    final_pois = []
    for cat, places in categorized_pois.items():
        # Shuffle to get variety if we assigned randomly
        random.shuffle(places)
        selected = places[:limit_per_cat]
        final_pois.extend(selected)
        print(f"  [POI] Kept {len(selected)} '{cat}' POIs.")

    print(f"  [POI] Total POIs returning: {len(final_pois)}")
    return final_pois


if __name__ == "__main__":
    # Test for Paris
    pois = fetch_city_pois(48.8566, 2.3522, ["Museums", "Food & Drink", "Outdoors"])
    for p in pois[:20]:
        print(f"{p['category']:15s} | {p['name']}")
