import math
import heapq

class AStarPathfinder:
    def __init__(self):
        pass

    def haversine_distance(self, p1, p2):
        """
        Calculates the great circle distance between two points on the Earth.
        :param p1, p2: (lat, lon) tuples
        """
        lat1, lon1 = p1
        lat2, lon2 = p2
        R = 6371  # Earth radius in kilometers

        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)

        a = math.sin(dphi / 2)**2 + \
            math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    def find_path(self, start_coords, end_coords, intermediate_nodes=[]):
        """
        A* Search implementation.
        In this context, we take the shortest path between start and end.
        If we have a graph of intermediate points, we'd traverse them.
        For this assignment, we'll implement the logic of f(n) = g(n) + h(n).
        """
        open_set = []
        heapq.heappush(open_set, (0 + self.haversine_distance(start_coords, end_coords), start_coords))
        
        # Tracking costs
        g_score = {start_coords: 0}
        came_from = {}
        
        while open_set:
            _, current = heapq.heappop(open_set)
            
            if current == end_coords:
                # Path found
                return self.reconstruct_path(came_from, current), g_score[current]
                
            
            # we'll treat the end_coords as the only "reachable" neighbor for a single hop.
            neighbors = [end_coords] + [n for n in intermediate_nodes if n != current]
            
            for neighbor in neighbors:
                tentative_g_score = g_score[current] + self.haversine_distance(current, neighbor)
                
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score = tentative_g_score + self.haversine_distance(neighbor, end_coords)
                    heapq.heappush(open_set, (f_score, neighbor))
                    
        return None, float('inf')

    def reconstruct_path(self, came_from, current):
        total_path = [current]
        while current in came_from:
            current = came_from[current]
            total_path.append(current)
        return total_path[::-1]

if __name__ == "__main__":
    # Test
    finder = AStarPathfinder()
    start = (48.8584, 2.2945) # Eiffel Tower
    end = (48.8606, 2.3376)   # Louvre
    path, dist = finder.find_path(start, end)
    print(f"Path distance: {dist:.2f} km")
    print(f"Path points: {path}")
