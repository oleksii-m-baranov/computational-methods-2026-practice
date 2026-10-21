def light_travel_time(distance_km):
    speed_of_light = 299792.458
    return distance_km / speed_of_light


distances = [0, 100, 1000, 300000]

for distance in distances:
    result = light_travel_time(distance)
    print(f"Відстань: {distance} км")
    print(f"Час: {result:.9f} секунд")
    print("-----------------------")