import random

class ItineraryCSP:
    def __init__(self, days, pois, preferences):
        # Initialize scheduling variables
        self.days = days
        self.pois = pois
        self.preferences = [p.lower() for p in preferences]
        
        # Variables: (day, slot) where slot is 0=Morning, 1=Lunch, 2=Afternoon, 3=Evening
        self.variables = []
        for d in range(days):
            for s in range(4):
                self.variables.append((d, s))
        # Domains: POIs filtered by category weight
        self.domains = {v: self._get_initial_domain(v) for v in self.variables}
        
    def _get_initial_domain(self, var):
        day, slot = var
        # For lunch/evening, prioritize Food & Drink
        is_meal_time = (slot == 1 or slot == 3)
        
        # Also filter by user preferences
        valid_pois = []
        for poi in self.pois:
            cat = poi.get("category", "General").lower()
            
            # Simple heuristic matching
            if is_meal_time and cat == "food & drink":
                valid_pois.append(poi)
            elif not is_meal_time and cat != "food & drink":
                # For activity slots, use preferred categories
                if cat in self.preferences or cat == "general":
                    valid_pois.append(poi)
        # Fallbacks if domain is empty
        if not valid_pois:
            valid_pois = [p for p in self.pois if p.get("category", "General").lower() in self.preferences]
        if not valid_pois:
            return self.pois
            
        return valid_pois

    def is_consistent(self, var, val, assignment):
        # Check if POI assignment satisfies constraints
        day, slot = var
        
        # Constraint 1: Uniqueness
        # Softened: strict uniqueness only if enough POIs exist
        if len(self.pois) >= len(self.variables):
            if any(val['name'] == other_val['name'] for other_val in assignment.values()):
                return False
        # Constraint 2: Category Variety
        # Softened: Enforce only if multiple preferences selected
        if slot > 0 and len(self.preferences) > 1:
            prev_var = (day, slot - 1)
            if prev_var in assignment:
                if assignment[prev_var]['category'] == val['category'] and val['category'] != "General":
                    return False
                    
        return True

    def backtrack_search(self, assignment=None):
        # Recursive backtracking solver
        if assignment is None:
            assignment = {}
            
        if len(assignment) == len(self.variables):
            return assignment
            
        # Select unassigned variable (next chronologically)
        unassigned = [v for v in self.variables if v not in assignment]
        var = unassigned[0]
        
        # Shuffle domain to get different results each time
        domain = list(self.domains[var])
        random.shuffle(domain)
        
        for val in domain:
            if self.is_consistent(var, val, assignment):
                assignment[var] = val
                result = self.backtrack_search(assignment)
                if result:
                    return result
                del assignment[var]
                
        return None

    def solve(self, start_date_str):
        itinerary = self.backtrack_search()
        if not itinerary:
            return None
            
        from datetime import datetime, timedelta
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d") if start_date_str else datetime.now()

        # Reformulate into frontend structure
        result = []
        for d in range(self.days):
            current_date = start_date + timedelta(days=d)
            day_plan = {
                "dayNumber": d + 1,
                "date": current_date.strftime("%Y-%m-%d"),
                "weather": random.choice(["sunny", "partly-cloudy", "cloudy"]),
                "morning": {"activities": []},
                "afternoon": {"activities": []},
                "evening": {"activities": []}
            }
            
            for s in range(4):
                poi = itinerary.get((d, s))
                if not poi: continue
                
                # Map slots to frontend
                activity_item = {
                    "id": f"d{d+1}-s{s}",
                    "name": poi["name"],
                    "cost": random.randint(0, 50) if poi["category"] != "General" else 0,
                    "lat": poi["lat"],
                    "lng": poi["lon"], # Frontend expects 'lng'
                    "category": poi["category"]
                }
                
                if s == 0 or s == 1: # Morning + Lunch
                    day_plan["morning"]["activities"].append(activity_item)
                elif s == 2:
                    day_plan["afternoon"]["activities"].append(activity_item)
                elif s == 3:
                    day_plan["evening"]["activities"].append(activity_item)
                    
            result.append(day_plan)
        return result

if __name__ == "__main__":
    # Test
    mock_pois = [
        {"name": "Eiffel Tower", "category": "General", "lat": 48.8584, "lon": 2.2945},
        {"name": "Louvre Museum", "category": "Museums", "lat": 48.8606, "lon": 2.3376},
        {"name": "Le Jules Verne", "category": "Food & Drink", "lat": 48.8583, "lon": 2.2944},
        {"name": "Café de Flore", "category": "Food & Drink", "lat": 48.8542, "lon": 2.3331},
        {"name": "Luxembourg Gardens", "category": "Outdoors", "lat": 48.8462, "lon": 2.3371},
        {"name": "A* Shop", "category": "Shopping", "lat": 48.8566, "lon": 2.3522},
        {"name": "Midnight Bar", "category": "Nightlife", "lat": 48.8566, "lon": 2.3522},
    ]
    csp = ItineraryCSP(1, mock_pois, ["Museums", "Food & Drink"])
    plan = csp.solve()
    print(plan)
