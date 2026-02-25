import random

class get_location:

    # avarage tempature desired by the user:
    # also can add manhaten distance if user wants a specific location: ex(europe, north usa ...)
    #numbers taken from a weather API
    def __init__(self, temp): 
        self.temp = temp

    #nums will be tempatures from a location in select dates. 
    def energy(nums):
        if not nums:
            return temp
        
        #avarage temp
        avg = sum(nums)/ len(nums)

        out = avg - temp

        #returns the absolute value of avrage temp - desired temp, this is the energy function
        return abs(out)

    #local search using the energy function to get the best logation.
    def get_best_place:
        #decay and temp constants
        int temp = 0
        int dec = 0

        curent_energy = 1000
        curent_neighbor = ""

        while (True):
            #list of all possible neighbors
            all_neighbors = []

            chosen_neighbor = random.choice(all_neighbors)
            #get this data from the API
            place_temp = []
            place_energy = energy(place_temp)
            if place_energy < curent_energy:
                curent_energy = place_energy
                curent_neighbor = chosen_neighbor
                continue

            else:
                #bad move
                if math.e ** (-4/t) * 1000 > random.randint(1, 1000):
                    temp = temp * dec
                    curent_energy = place_energy
                    curent_neighbor = chosen_neighbor
                    continue
                else:
                    temp = temp * dec
            #randome retart or reurn final location continu here
            



    
