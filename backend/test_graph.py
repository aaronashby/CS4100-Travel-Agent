from city_graph import CityGraph

graph = CityGraph()

print(graph.has_city("Boston"))

city = graph.get_city("Tokyo")
print("City:", city)

print(city["latitude"])

neighbors = city["neighbors"]

print("\nNeighbors:")
for n in neighbors:
    print(f" - {n['name']} ({n['distance_km']:.1f} km)")
