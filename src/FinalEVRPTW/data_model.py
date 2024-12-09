import random
import numpy as np
import math
import contextlib
import os

# Check if the 'results' folder exists, if not, create it
if not os.path.exists('results'):
    os.makedirs('results')
# Check if the 'data' folder exists, if not, create it
if not os.path.exists('data'):
    os.makedirs('data')


# Ensure no overlap in locations
def generate_unique_location(existing_locations, range_min=-50, range_max=50):
    while True:
        x = random.randint(range_min, range_max)
        y = random.randint(range_min, range_max)
        if (x, y) not in existing_locations:
            return (x, y)

def create_data_model(num_customers, num_stations, output_file=f'results/data_model.txt'):
    """Creates the data for the VRP with charging stations and saves output to a text file."""
    data = {}

    # Generate random coordinates for each customer, depot, and charging stations
    locations = [(0, 0)]  # Depot at (0,0)
    
    # Generate unique locations for customers
    for _ in range(num_customers):
        locations.append(generate_unique_location(locations))  

    # Add unique locations for charging stations
    for _ in range(num_stations):
        locations.append(generate_unique_location(locations))

    # Store locations in the data model
    data['locations'] = locations

    # Calculate Euclidean distance between all locations (distance matrix)
    def euclidean_distance(loc1, loc2):
        return round(math.hypot(loc1[0] - loc2[0], loc1[1] - loc2[1]))

    distance_matrix = []
    for i in range(len(locations)):
        row = []
        for j in range(len(locations)):
            if i == j:
                row.append(0)
            else:
                row.append(euclidean_distance(locations[i], locations[j]))
        distance_matrix.append(row)

    data['distance_matrix'] = distance_matrix

    # Number of vehicles (40% of customers, rounded up)
    data['num_vehicles'] = math.ceil(0.4 * num_customers)

    # Depot location index
    data['depot'] = 0

    # Set customer node indices (1 to num_customers)
    data['customer_nodes'] = list(range(1, num_customers + 1))

    # Set charging station node indices (after customers)
    data['charging_stations'] = list(range(num_customers + 1, num_customers + 1 + num_stations))

    # Randomly generate customer demands and set 0 demand for charging stations
    data['demands'] = [0] + [random.randint(1, 10) for _ in range(num_customers)] + [0] * num_stations 

    # Vehicle capacities
    data['vehicle_capacities'] = [random.randint(25, 30) for _ in range(data['num_vehicles'])]

    # Service times (No service time for depot, random for customers, fixed for charging stations)
    data['service_times'] = [0] + [random.randint(10, 15) for _ in range(num_customers)] + [0] * num_stations

    # Battery capacities for each vehicle (in arbitrary units)
    data['battery_capacities'] = [100 for _ in range(data['num_vehicles'])]

    # Time windows (Depot gets a larger window)
    data['time_windows'] = [(0, 1000)] + [(random.randint(0, 50), 500) for _ in range(num_customers)] + [(0, 1000)] * num_stations

    # Charging rate (units per minute)
    data['charging_rate'] = 1  # Adjust this value as needed

    # Redirect print output to a file
    output_file=f'data/data_model_{num_customers}_{num_stations}.txt'
    with open(output_file, "w") as f:
        with contextlib.redirect_stdout(f):
            print("Location coordinates of network setup:")
            print(data['locations'])
            print(f"\nDepot Index: {data['depot']}")
            print(f"\nCustomer node indices: {data['customer_nodes']}")
            print(f"\nCharging station indices: {data['charging_stations']}")
            print(f"\nRandom service times: {data['service_times']}")
            print(f"\nTime Windows: {data['time_windows']}")
            print(f"\nDemands: {data['demands']}")
            print(f"\nVehicle Capacities: {data['vehicle_capacities']}")
            print(f"\nBattery Capacities: {data['battery_capacities']}")
            print("\nDistance Matrix:")
            for row in data['distance_matrix']:
                print(row)

    return data

# # test case
# create_data_model(10, 5)

