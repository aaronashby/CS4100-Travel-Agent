import os
import json
import time
import requests
import pandas as pd
import numpy as np
from sklearn.neighbors import BallTree


class CityGraph:
    def __init__(self, json_path="touristy_cities.json"):
        import json
        with open(json_path, "r") as f:
            self.data = json.load(f)

    def get_city(self, name):
        for city in self.data:
            if city["name"].lower() == name.lower():
                return city
        return None


# You can switch servers if needed
OVERPASS_URL = "https://overpass.kumi.systems/api/interpreter"


# ============================================================
# ONE API CALL PER CITY — museums, malls, hikes, beaches, nightlife
# ============================================================

def fetch_poi_bundle(lat, lon, radius_m=50000, retries=5):
    """
    Fetch museums, malls, hikes, beaches, and nightlife in ONE Overpass API call.
    Hikes use Option A: only route=hiking relations.
    Nightlife includes only nightclub, bar, and pub.
    """

    query = f"""
    [out:json][timeout:25];
    (
      // Museums
      node["tourism"="museum"](around:{radius_m},{lat},{lon});
      way["tourism"="museum"](around:{radius_m},{lat},{lon});
      relation["tourism"="museum"](around:{radius_m},{lat},{lon});

      // Malls
      node["shop"="mall"](around:{radius_m},{lat},{lon});
      way["shop"="mall"](around:{radius_m},{lat},{lon});
      relation["shop"="mall"](around:{radius_m},{lat},{lon});

      // Hikes 
      relation["route"="hiking"](around:{radius_m},{lat},{lon});

      // Beaches
      node["natural"="beach"](around:{radius_m},{lat},{lon});
      way["natural"="beach"](around:{radius_m},{lat},{lon});
      relation["natural"="beach"](around:{radius_m},{lat},{lon});

      // Nightlife (only nightclub, bar, pub)
      node["amenity"="nightclub"](around:{radius_m},{lat},{lon});
      node["amenity"="bar"](around:{radius_m},{lat},{lon});
      node["amenity"="pub"](around:{radius_m},{lat},{lon});

      way["amenity"="nightclub"](around:{radius_m},{lat},{lon});
      way["amenity"="bar"](around:{radius_m},{lat},{lon});
      way["amenity"="pub"](around:{radius_m},{lat},{lon});

      relation["amenity"="nightclub"](around:{radius_m},{lat},{lon});
      relation["amenity"="bar"](around:{radius_m},{lat},{lon});
      relation["amenity"="pub"](around:{radius_m},{lat},{lon});
    );
    out center;
    """

    for attempt in range(1, retries + 1):
        try:
            response = requests.get(OVERPASS_URL, params={'data': query}, timeout=30)

            if response.status_code != 200 or not response.text.strip():
                print(f"[Attempt {attempt}] Empty or invalid response")
                time.sleep(1)
                continue

            try:
                data = response.json()
            except ValueError:
                print(f"[Attempt {attempt}] Invalid JSON")
                time.sleep(1)
                continue

            museums = 0
            malls = 0
            hikes = 0
            beaches = 0
            nightlife = 0

            for el in data.get("elements", []):
                tags = el.get("tags", {})

                if tags.get("tourism") == "museum":
                    museums += 1

                if tags.get("shop") == "mall":
                    malls += 1

                if tags.get("route") == "hiking":
                    hikes += 1

                if tags.get("natural") == "beach":
                    beaches += 1

                if tags.get("amenity") in ("nightclub", "bar", "pub"):
                    nightlife += 1

            return {
                "museum_count": museums,
                "mall_count": malls,
                "hike_count": hikes,
                "beach_count": beaches,
                "nightlife_count": nightlife,
            }

        except requests.exceptions.RequestException:
            print(f"[Attempt {attempt}] Request failed")
            time.sleep(1)

    print("All retries failed — returning zeros")
    return {
        "museum_count": 0,
        "mall_count": 0,
        "hike_count": 0,
        "beach_count": 0,
        "nightlife_count": 0,
    }


# ============================================================
# BUILD CITY GRAPH
# ============================================================

def build_city_graph(output_path="touristy_cities.json"):
    print("Starting city graph build...")

    # --------------------------------------------------------
    # Load old JSON for caching
    # --------------------------------------------------------
    if os.path.exists(output_path):
        print("Loading existing dataset for caching...")
        old_data = pd.read_json(output_path)

        old_lookup = {
            row["name"]: {
                "museum_count": row.get("museum_count"),
                "mall_count": row.get("mall_count"),
                "hike_count": row.get("hike_count"),
                "beach_count": row.get("beach_count"),
                "nightlife_count": row.get("nightlife_count"),
            }
            for _, row in old_data.iterrows()
        }
    else:
        old_lookup = {}

    # --------------------------------------------------------
    # Load world cities CSV
    # --------------------------------------------------------
    print("Loading world cities dataset...")
    cities = pd.read_csv("cities.csv")

    cities = cities.rename(columns={
        "city": "name",
        "lat": "latitude",
        "lng": "longitude"
    })

    cities = cities.dropna(subset=["latitude", "longitude", "population"])
    print("Loaded", len(cities), "cities")

    # --------------------------------------------------------
    # Scrape tourism lists
    # --------------------------------------------------------
    print("Scraping tourism lists from Wikipedia...")

    tourism_urls = [
        "https://en.wikipedia.org/wiki/List_of_cities_by_international_visitors",
        "https://en.wikipedia.org/wiki/World%27s_most-visited_cities",
    ]

    tourist_cities = []

    for url in tourism_urls:
        print(f"Fetching tables from: {url}")
        try:
            tables = pd.read_html(url)
            for table in tables:
                city_cols = [c for c in table.columns if "city" in str(c).lower()]
                if city_cols:
                    tourist_cities.append(table[city_cols[0]].dropna())
        except Exception as e:
            print(f"Error reading {url}: {e}")

    if tourist_cities:
        tourist_cities = pd.concat(tourist_cities).drop_duplicates().reset_index(drop=True)
    else:
        tourist_cities = pd.Series([], dtype=str)

    print("Found", len(tourist_cities), "tourism-ranked cities")

    # --------------------------------------------------------
    # Compute tourism scores
    # --------------------------------------------------------
    print("Computing tourism scores...")

    cities["tourism_score"] = 5.0 * (cities["population"] / cities["population"].max())
    cities.loc[cities["name"].isin(tourist_cities), "tourism_score"] += 5.0

    # --------------------------------------------------------
    # Select top 2000 cities
    # --------------------------------------------------------
    print("Selecting top 2000 cities...")

    top2000 = cities.sort_values("tourism_score", ascending=False).head(2000).reset_index(drop=True)

    # --------------------------------------------------------
    # Fetch POI bundle (cached when possible)
    # --------------------------------------------------------
    print("Fetching POI bundle (museums, malls, hikes, beaches, nightlife)...")

    museum_counts = []
    mall_counts = []
    hike_counts = []
    beach_counts = []
    nightlife_counts = []

    for i, row in top2000.iterrows():
        name = row["name"]
        lat = row["latitude"]
        lon = row["longitude"]

        # Use cached values if available
        if name in old_lookup:
            cached = old_lookup[name]
            museum_counts.append(cached.get("museum_count"))
            mall_counts.append(cached.get("mall_count"))
            hike_counts.append(cached.get("hike_count"))
            beach_counts.append(cached.get("beach_count"))
            nightlife_counts.append(cached.get("nightlife_count"))
        else:
            bundle = fetch_poi_bundle(lat, lon)
            museum_counts.append(bundle["museum_count"])
            mall_counts.append(bundle["mall_count"])
            hike_counts.append(bundle["hike_count"])
            beach_counts.append(bundle["beach_count"])
            nightlife_counts.append(bundle["nightlife_count"])
            time.sleep(1)

        if i % 50 == 0:
            print(f"Processed {i} / {len(top2000)} cities")

    top2000["museum_count"] = museum_counts
    top2000["mall_count"] = mall_counts
    top2000["hike_count"] = hike_counts
    top2000["beach_count"] = beach_counts
    top2000["nightlife_count"] = nightlife_counts

    # --------------------------------------------------------
    # Compute nearest neighbors
    # --------------------------------------------------------
    print("Computing nearest neighbors...")

    coords = np.radians(top2000[["latitude", "longitude"]].values)
    tree = BallTree(coords, metric="haversine")

    neighbors_list = []
    for i, coord in enumerate(coords):
        distances, indices = tree.query([coord], k=6)
        distances = distances[0] * 6371.0
        indices = indices[0]

        neighbor_entries = []
        for dist, idx in zip(distances[1:], indices[1:]):
            neighbor_entries.append({
                "name": top2000.iloc[idx]["name"],
                "distance_km": float(dist),
            })

        neighbors_list.append(neighbor_entries)

    top2000["neighbors"] = neighbors_list

    # --------------------------------------------------------
    # Save JSON
    # --------------------------------------------------------
    print("Saving dataset to", output_path)
    top2000.to_json(output_path, orient="records", indent=2)
    print("Dataset saved successfully!")

    print("\nSample city entry:")
    print(top2000.head(1).to_string())

    return output_path

if __name__ == "__main__":
    build_city_graph()
