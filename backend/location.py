import math
import random

import requests
import calendar

#graph for the local search
from city_graph import CityGraph

class get_location:

    # info used to calculate for the energy function
    # for temp year and month put in requested temp, year and month,
    # fot the rest like beach, give Booleans if the user selected them
    def __init__(self, temp, year, month, beach, museum): 
        self.temp = temp
        self.year = year
        self.month = month
        self.beach = beach
        self.museum = museum

        self.temp_cache = {}
        self.museum_cache = {}

    #will get the energy of the function given the long and lat
    def energy(self, lat, long):
        total_energy = 0

        temp_energy = self.get_temp_energy(lat, long)
        total_energy += temp_energy
        print("temp energy:", temp_energy)

        if (self.museum):
            #museum_energy = self.get_museums_energy(lat, long)
            museum_energy = 0
            total_energy += museum_energy


        if (self.beach):
            beach_energy = self.get_beach_energy(lat, long)
            total_energy += beach_energy

        return total_energy

    #local search using the energy function to get the best logation.
    def get_best_place(self):

        graph = CityGraph()  # loads touristy_cities.json automatically

        # starts at boston
        starting_node = graph.get_city("Boston")

        failed_moves = 0
        #decay and temp constants
        #these t and d are such that assuming max ^e = -5 then the first bad choice has a 95% chance to be acepted
        #after 100 turns the bad choice has a 20% chance of being accepted 
        t = 97.5
        d = 0.965

        curent_energy = self.energy(starting_node["latitude"], starting_node["longitude"])
        #we need to either create or find a graph for neiboring cities to use for this local search
        curent_city = starting_node

        #counter only here so I can see that the function is working.
        counter = 0
        while (True):
            print("move", counter)
            counter += 1
            #list of all possible neighbors
            all_neighbors = curent_city["neighbors"]

            chosen_neighbor_name = random.choice(all_neighbors)

            chosen_neighbor =  graph.get_city(chosen_neighbor_name["name"])

            place_energy = self.energy(chosen_neighbor["latitude"],chosen_neighbor["longitude"])

            print(place_energy)
            print("failed moves:",failed_moves)
            print("name:", curent_city['name'])

            print ("testing if good move: ",  place_energy < curent_energy)

            if place_energy < curent_energy:
                # good move
                failed_moves = 0
                t = t * d
                curent_energy = place_energy
                curent_city = chosen_neighbor
                continue
            else:
                #bad move chosen
                if math.e ** (-place_energy/t) * 1000 > random.randint(0, 1000):
                    failed_moves = 0
                    t = t * d
                    curent_energy = place_energy
                    curent_city = chosen_neighbor
                    continue
                else:
                    #bad move not chosen
                    failed_moves += 1
                    t = t * d
            #if 5 random moves fail in a row then return the location as the solution
            if failed_moves >= 5:
                #this will be the output for one of the runs
                return curent_city
            
    #energy helper classes to make sure that the energy function is not too cluddred
    #scalar will be there just if in the future we want to make small changed to what gets wrighted more


    def get_temp_energy(self, lat, lon, scaler=1):
        if not hasattr(self, "temp_cache"):
            self.temp_cache = {}

        key = (round(lat, 3), round(lon, 3))
        if key in self.temp_cache:
            return self.temp_cache[key]

        url = (
            "https://archive-api.open-meteo.com/v1/era5?"
            f"latitude={lat}&longitude={lon}"
            "&start_date=2005-01-01"
            "&end_date=2025-12-31"
            "&monthly=temperature_2m_mean"
        )

        try:
            data = requests.get(url, timeout=10).json()
        except:
            self.temp_cache[key] = 10000
            return 10000

        print("RAW API RESPONSE:", data)

        try:
            temps = data["monthly"]["temperature_2m_mean"]
            # pick the correct month (0-indexed)
            mean_temp = temps[self.month - 1]
        except:
            self.temp_cache[key] = 10000
            return 10000

        energy = abs(mean_temp - self.temp) * scaler
        self.temp_cache[key] = energy
        return energy





    #currently not working

    # def get_museums_energy(self, lat, long, radius_km=10, scaler = 1):
    #     """
    #     Count museums near a given latitude/longitude using OpenStreetMap Overpass API.
    #     radius_km: search radius in kilometers
    #     """
    #     # Convert km → meters for Overpass
    #     radius_m = int(radius_km * 1000)

    #     # Overpass QL query
    #     query = f"""
    #     [out:json];
    #     (
    #     node["tourism"="museum"](around:{radius_m},{lat},{long});
    #     way["tourism"="museum"](around:{radius_m},{lat},{long});
    #     relation["tourism"="museum"](around:{radius_m},{lat},{long});
    #     );
    #     out count;
    #     """

    #     url = "https://overpass-api.de/api/interpreter"
    #     response = requests.post(url, data=query)

    #     data = response.json()

    #     # Overpass returns: {"elements":[{"type":"count","tags":{"nodes":"X"}}]}
    #     if "elements" in data and len(data["elements"]) > 0:
    #         count = int(data["elements"][0]["tags"]["nodes"])
    #         #negetive 1 because the amount of meuseums should be a positive and this local search minimizes the energy function
    #         return count * scaler * -1

    #     return 0
    
    #small helper to convert a differnence with lat and long to km
    def haversine(self, lat1, long1, lat2, long2):
        R = 6371  # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(long2 - long1)
        a = (
            math.sin(dlat/2)**2 +
            math.cos(math.radians(lat1)) *
            math.cos(math.radians(lat2)) *
            math.sin(dlon/2)**2
        )
        return 2 * R * math.asin(math.sqrt(a))

    def get_beach_energy(self, lat, long, radius_km=50, scaler=1):
        radius_m = int(radius_km * 1000)

        query = f"""
        [out:json];
        (
        node["natural"="beach"](around:{radius_m},{lat},{long});
        way["natural"="beach"](around:{radius_m},{lat},{long});
        relation["natural"="beach"](around:{radius_m},{lat},{long});
        );
        out center;
        """

        url = "https://overpass-api.de/api/interpreter"

        try:
            response = requests.post(url, data=query, timeout=20)
            data = response.json()
        except Exception:
            # Overpass failed — treat as “no beach found”
            return 10000 * scaler

        if "elements" not in data or len(data["elements"]) == 0:
            return 10000 * scaler

        # compute nearest beach
        min_dist = float("inf")
        for el in data["elements"]:
            if "lat" in el and "lon" in el:
                blat, blong = el["lat"], el["lon"]
            elif "center" in el:
                blat, blong = el["center"]["lat"], el["center"]["lon"]
            else:
                continue

            dist = self.haversine(lat, long, blat, blong)
            min_dist = min(min_dist, dist)

        return min_dist * scaler

#running the function
#this function will take a while just because calling the APIS will take time

if __name__ == "__main__":

    # Example user preferences
    loc = get_location(
        temp=25,
        year=2026,
        month=7,
        beach=True, 
        museum=False
    )

    results = []

    print("\n=== Running 5 Local Search Trials ===\n")

    for i in range(1):
        final_city = loc.get_best_place()
        energy = loc.energy(final_city["latitude"], final_city["longitude"])

        results.append((final_city["name"], energy))

        print(f"Run {i+1}: {final_city['name']}  |  Energy = {energy:.2f}")

    print("\n=== Summary of Final Energies ===")
    for i, (city, energy) in enumerate(results, start=1):
        print(f"{i}. {city:<20}  Energy = {energy:.2f}")

