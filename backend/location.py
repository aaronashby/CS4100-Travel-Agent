import math
import random


#graph for the local search
from city_graph import CityGraph

class get_location:

    # info used to calculate for the energy function
    # for temp year and month put in requested temp, year and month,
    # fot the rest like beach, give Booleans if the user selected them
    def __init__(self, relaxation, museum, outdoors, nightlife, shopping): 
        self.relaxation = relaxation
        self.museum = museum
        self.outdoors = outdoors
        self.nightlife = nightlife
        self.shopping = shopping
        self.graph = CityGraph()

        #uncomment this to run the local search and get the best location based on the energy function.
        #get_location.get_best_of5(self)


    #gives diminishing returns for really gigh nums
    def diminishing(self, x, max_score, k):
        # Smooth diminishing returns curve
        return (max_score * x) / (x + k)
        
    #energy function for the local
    def energy(self, name):
        city = self.graph.get_city(name)
        total = 0

        # Museums
        if self.museum:
            total += self.diminishing(
                x=city["museum_count"],
                max_score=10,
                k = 85  
            )

        # Relaxation (beaches)
        if self.relaxation:
            total += self.diminishing(
                x=city["beach_count"],
                max_score=10,
                k = 15  
            )

        # Outdoors (hikes)
        if self.outdoors:
            total += self.diminishing(
                x=city["hike_count"],
                max_score=10,
                k = 15   
            )

        # Nightlife
        if self.nightlife:
            total += self.diminishing(
                x=city["nightlife_count"],
                max_score=10,
                k = 750
            )

        # Shopping (malls)
        if self.shopping:
            total += self.diminishing(
                x=city["mall_count"],
                max_score=10,
                k = 70  
            )

        return total * -1  # Negate to convert to energy (lower is better)


    #local search using the energy function to get the best logation.
    def get_best_place(self):

        # starts at a random city
        starting_node = random.choice(self.graph.data)

        failed_moves = 0
        #decay and temp constants
        t = 197.5
        d = 0.985

        curent_energy = self.energy(starting_node["name"])
        curent_city = starting_node

        #counter only here so I can see that the function is working.
        while (True):
            #list of all possible neighbors
            all_neighbors = curent_city["neighbors"]

            chosen_neighbor_name = random.choice(all_neighbors)

            chosen_neighbor =  self.graph.get_city(chosen_neighbor_name["name"])
            
            #energy of the place we are trying to move to
            place_energy = self.energy(chosen_neighbor["name"])

            if place_energy < curent_energy:
                # good move
                failed_moves = 0
                t = t * d
                curent_energy = place_energy
                curent_city = chosen_neighbor
                continue
            else:
                #bad move chosen
                #difference has to be positive becuase place energy > current energy.
                difference = place_energy - curent_energy
                if math.e ** (-difference /t) * 1000 > random.randint(0, 1000):
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
                return curent_city, curent_energy
            
    def get_best_of5(self):
        for ran in range(5):
            city, energy = self.get_best_place()
            print("run:", ran, "city:", city['name'], "energy:", energy)

            #this will be the output for all 5 runs, we can use this to see which city is the best overall
            #2 options, 1 to return all 5 cities and energies, or just return the best one. 



if __name__ == "__main__":
    tester = get_location(True, True, True, True,True)
    tester.get_best_of5()