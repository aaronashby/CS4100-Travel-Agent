import math
import random
from city_graph import CityGraph

class LocationSearcher:
    def __init__(self, activities): 
        # Parse activity keywords
        self.activities = [a.lower() for a in activities]
        self.relaxation = "relaxation" in self.activities
        self.museum = "museums" in self.activities
        self.outdoors = "outdoors" in self.activities
        self.nightlife = "nightlife" in self.activities
        self.shopping = "shopping" in self.activities
        self.food = "food & drink" in self.activities
        
        self.graph = CityGraph()

    def diminishing(self, x, max_score, k):
        # Smooth diminishing returns curve
        return (max_score * x) / (x + k)
        
    def energy(self, name):
        city = self.graph.get_city(name)
        if not city:
            return 0
            
        total = 0

        # Museums
        if self.museum:
            total += self.diminishing(x=city.get("museum_count", 0), max_score=10, k=85)

        # Relaxation (beaches)
        if self.relaxation:
            total += self.diminishing(x=city.get("beach_count", 0), max_score=10, k=15)

        # Outdoors (hikes)
        if self.outdoors:
            total += self.diminishing(x=city.get("hike_count", 0), max_score=10, k=15)

        # Nightlife
        if self.nightlife:
            total += self.diminishing(x=city.get("nightlife_count", 0), max_score=10, k=750)

        # Shopping (malls)
        if self.shopping:
            total += self.diminishing(x=city.get("mall_count", 0), max_score=10, k=70)

        # Proxy Metric
        if self.food:
            nightlife_val = city.get("nightlife_count", 0)
            tourism_val = city.get("tourism_score", 0) 
            proxy_food_count = (nightlife_val * 0.5) + (tourism_val * 50)
            total += self.diminishing(x=proxy_food_count, max_score=10, k=400)

        return total * -1

    def get_best_place(self):
        # First-Choice Hill Climbing implementation
        if not self.graph.data:
            return None, 0

        starting_node = random.choice(self.graph.data)
        failed_moves = 0
        
        t = 197.5
        d = 0.985

        current_energy = self.energy(starting_node["name"])
        current_city = starting_node

        while True:
            all_neighbors = current_city.get("neighbors", [])
            if not all_neighbors:
                return current_city, current_energy

            chosen_neighbor_name = random.choice(all_neighbors)
            chosen_neighbor = self.graph.get_city(chosen_neighbor_name["name"])
            
            if not chosen_neighbor:
                failed_moves += 1
                continue

            place_energy = self.energy(chosen_neighbor["name"])

            if place_energy < current_energy:
                failed_moves = 0
                t = t * d
                current_energy = place_energy
                current_city = chosen_neighbor
            else:
                difference = place_energy - current_energy
                if t > 0.1 and math.exp(-difference / t) * 1000 > random.randint(0, 1000):
                    failed_moves = 0
                    t = t * d
                    current_energy = place_energy
                    current_city = chosen_neighbor
                else:
                    failed_moves += 1
                    t = t * d
            
            # If several random moves fail to find a better or acceptable state, stop.
            if failed_moves >= 10:
                return current_city, current_energy
            
    def search(self, n_runs=5):
        # Repeated search to avoid local optima
        best_city = None
        best_energy = float('inf')
        
        for _ in range(n_runs):
            city, energy = self.get_best_place()
            if energy < best_energy:
                best_energy = energy
                best_city = city
                
        return best_city

if __name__ == "__main__":
    tester = LocationSearcher(["Museums", "Food & Drink", "Nightlife"])
    best = tester.search()
    print(f"Best City Found: {best['name']} with Energy: {tester.energy(best['name'])}")
