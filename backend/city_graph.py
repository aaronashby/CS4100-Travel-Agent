import os
import json
import pandas as pd
import numpy as np
from sklearn.neighbors import BallTree

# ------------------------------------------------------------
# BUILD FUNCTION — generates touristy_cities.json
# ------------------------------------------------------------

def build_city_graph(output_path="touristy_cities.json"):
    print("No cache found — generating dataset...")

    # -----------------------------
    # Load local world cities CSV
    # -----------------------------
    print("Loading world cities dataset from local file...")

    cities = pd.read_csv("cities.csv")

    # Rename SimpleMaps columns to match expected names
    cities = cities.rename(columns={
        "city": "name",
        "lat": "latitude",
        "lng": "longitude"
    })

    # Drop rows missing essential data
    cities = cities.dropna(subset=["latitude", "longitude", "population"])

    print("Loaded", len(cities), "cities from local CSV")

    # -----------------------------
    # Scrape tourism lists (robust)
    # -----------------------------
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
            print(f"  Found {len(tables)} tables")

            for table in tables:
                normalized_cols = [str(c).strip().lower() for c in table.columns]
                city_cols = [c for c in table.columns if "city" in str(c).lower()]

                if city_cols:
                    col = city_cols[0]
                    print(f"  Extracting city column: {col}")
                    tourist_cities.append(table[col].dropna())

        except Exception as e:
            print(f"  Error reading {url}: {e}")

    if not tourist_cities:
        print("WARNING: No tourism tables found. Using empty list.")
        tourist_cities = pd.Series([], dtype=str)
    else:
        tourist_cities = pd.concat(tourist_cities).drop_duplicates().reset_index(drop=True)

    print("Found", len(tourist_cities), "unique tourism-ranked cities")

    # -----------------------------
    # Compute tourism scores
    # -----------------------------
    print("Computing tourism scores...")

    cities["tourism_score"] = 5.0 * (cities["population"] / cities["population"].max())

    # Boost score for cities found in tourism lists
    cities.loc[cities["name"].isin(tourist_cities), "tourism_score"] += 5.0

    # -----------------------------
    # Select top 2000 cities
    # -----------------------------
    print("Selecting top 2000 most touristy cities...")

    top2000 = cities.sort_values("tourism_score", ascending=False).head(2000).reset_index(drop=True)

    # -----------------------------
    # Compute nearest neighbors
    # -----------------------------
    print("Computing nearest neighbors...")

    coords = np.radians(top2000[["latitude", "longitude"]].values)
    tree = BallTree(coords, metric="haversine")

    neighbors_list = []
    for i, coord in enumerate(coords):
        distances, indices = tree.query([coord], k=6)
        distances = distances[0] * 6371.0  # convert to km
        indices = indices[0]

        neighbor_entries = []
        for dist, idx in zip(distances[1:], indices[1:]):
            neighbor_entries.append({
                "name": top2000.iloc[idx]["name"],
                "distance_km": float(dist)
            })

        neighbors_list.append(neighbor_entries)

    top2000["neighbors"] = neighbors_list

    # -----------------------------
    # Save JSON
    # -----------------------------
    print("Saving dataset to", output_path)
    top2000.to_json(output_path, orient="records", indent=2)
    print("Dataset saved successfully!")

    # Show sample
    print("\nSample city entry:")
    print(top2000.head(1).to_string())

    return output_path


# ------------------------------------------------------------
# CITYGRAPH CLASS — for loading and querying the graph
# ------------------------------------------------------------

class CityGraph:
    def __init__(self, json_path="touristy_cities.json"):
        with open(json_path, "r") as f:
            self.cities = json.load(f)

        # Fast lookup by name
        self.by_name = {city["name"]: city for city in self.cities}

    def get_city(self, name):
        return self.by_name.get(name)

    def neighbors_of(self, name):
        city = self.by_name.get(name)
        if not city:
            return []
        return city["neighbors"]

    def all_cities(self):
        return self.cities

    def has_city(self, name):
        return name in self.by_name


# ------------------------------------------------------------
# MAIN — only runs when executed directly
# ------------------------------------------------------------

if __name__ == "__main__":
    build_city_graph()
