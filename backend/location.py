import math
import random

class get_location:
    # avarage tempature desired by the user:
    # also can add manhaten distance if user wants a specific location: ex(europe, north usa ...)
    #numbers taken from a weather API
    def __init__(self, tmp): 
        self.temp = tmp

    #nums will be tempatures from a location in select dates. 
    def energy(self, nums):
        if not nums:
            return self.temp
        
        #avarage temp
        avg = sum(nums)/ len(nums)

        out = avg - self.temp

        #returns the absolute value of avrage temp - desired temp, this is the energy function
        return abs(out)

    #local search using the energy function to get the best logation.
    def get_best_place(self):
        failed_moves = 0
        #decay and temp constants
        #these t and d are such that assuming max ^e = -5 then the first bad choice has a 95% chance to be acepted
        #after 100 turns the bad choice has a 20% chance of being accepted 
        t = 97.5
        d = 0.965

        curent_energy = 1000
        #we need to either create or find a graph for neiboring cities to use for this local search
        curent_solution = ""

        while (True):
            #list of all possible neighbors
            all_neighbors = []

            chosen_neighbor = random.choice(all_neighbors)
            #get this data from the API
            place_temp = []
            place_energy = self.energy(place_temp)
            if place_energy < curent_energy:
                # good move
                failed_moves = 0
                t = t * d
                curent_energy = place_energy
                curent_solution = chosen_neighbor
                continue
            else:
                #bad move chosen
                if math.e ** (-place_energy/t) * 1000 > random.randint(0, 1000):
                    failed_moves = 0
                    t = t * d
                    curent_energy = place_energy
                    curent_solution = chosen_neighbor
                    continue
                else:
                    #bad move not chosen
                    failed_moves += 1
                    t = t * d
            #if 5 random moves fail in a row then return the location as the solution
            if failed_moves >= 5:
                #this will be the output for one of the runs
                return curent_solution
                



#small test for energy function
if __name__ == "__main__":
    list1 = [84, 60, 96, 70, 77]
    list2 = [67, 84, 67, 97, 91]
    list3 = [66, 84, 76, 93, 81]
    list4 = [99, 91, 82, 68, 77]
    list5 = [72, 75, 77, 70, 61]


    test = get_location(80)
    assert(test.energy(list1) == 2.5999999999999943)
    assert(test.energy(list2) == 1.2000000000000028)git checkout your-branch-name
    assert(test.energy(list3) == 0)
    assert(test.energy(list4) == 3.4000000000000057)
    assert(test.energy(list5) == 9.0)
