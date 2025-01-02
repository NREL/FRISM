import random
import math
import numpy as np

# For data adaptation from previous FRISM implementation results, I made the following
# 1. We have depot location 0 and customer location in (x,y) format. We have corresponding travel time matrci as well.
# 2. I assumed the charging locations from a set of customer locations (50% of custmer number in network if 6 customers, 3 charging station locations will be added)
# 3. As we have travel time from each depot ot customer node to other customer nodes, we can map the travel time for each edges from existing travel time matrix. Now, added charging locations allow us to have effective travel time matrix
# 4. from th  mapping. For example, we have depot 0, customers 1-6. Then, we will assume 3 charging stations selecting randomly to be located in the location of 1-6 customers. Now, we will have depot+6 customers+3 charging stations.
# 5. Newly transformed travel time matrix of (10*10 will be created instead of existing 7*7 travel time matrix). Here, accurate travel times will be passed.
# 6. demands, time windows, stop durations, EV capacity, Battery capacity and charging rates are added to make new EV compatible dataset.

def extend_data_with_charging_stations(previous_results):
    # Extract the original data
    time_matrix = previous_results['time_matrix']
    loc_x_y = previous_results['loc_x_y']
    stop_durations = previous_results['stop_durations']
    time_windows = previous_results['time_windows']
    demands = previous_results['demands']

    # Number of customers
    num_customers = len(loc_x_y) - 1  # Exclude depot
    charging_station_count = num_customers // 2  # Half of the customers

    # Randomly select customers as charging stations
    charging_station_indices = random.sample(range(1, num_customers + 1), charging_station_count)

    # Step 1: Extend location coordinates
    charging_station_coords = [loc_x_y[i] for i in charging_station_indices]
    extended_loc_x_y = loc_x_y + charging_station_coords

    # Step 2: Extend time matrix
    extended_time_matrix = np.array(time_matrix)
    for cs_index in charging_station_indices:
        # Add the row corresponding to the charging station
        new_row = extended_time_matrix[cs_index].tolist()
        extended_time_matrix = np.vstack([extended_time_matrix, new_row])

        # Add the column corresponding to the charging station
        new_column = extended_time_matrix[:, cs_index].reshape(-1, 1)
        extended_time_matrix = np.hstack([extended_time_matrix, new_column])

    extended_time_matrix = extended_time_matrix.tolist()

    # Step 3: Extend stop durations (service times)
    extended_stop_durations = stop_durations + [0] * charging_station_count

    # Step 4: Extend time windows
    depot_time_window = time_windows[0]
    extended_time_windows = time_windows + [depot_time_window] * charging_station_count

    # Step 5: Extend demands
    extended_demands = demands + [0] * charging_station_count

    # Update the result dictionary to include extended fields
    previous_results['time_matrix'] = extended_time_matrix
    previous_results['loc_x_y'] = extended_loc_x_y
    previous_results['stop_durations'] = extended_stop_durations
    previous_results['time_windows'] = extended_time_windows
    previous_results['demands'] = extended_demands
    previous_results['charging_stations'] = list(range(num_customers + 1, num_customers + 1 + charging_station_count))

    return previous_results, charging_station_indices



def adapt_to_dataset_structure(previous_results):
    # Extract extended data
    extended_time_matrix = previous_results['time_matrix']
    extended_loc_x_y = previous_results['loc_x_y']
    extended_stop_durations = previous_results['stop_durations']
    extended_time_windows = previous_results['time_windows']
    extended_demands = previous_results['demands']
    charging_station_indices = previous_results['charging_stations']

    # Identify depot, customer, and charging station locations
    depot_index = 0  # Depot is always at index 0
    num_customers = len(extended_loc_x_y) - len(charging_station_indices) - 1
    customer_indices = list(range(1, num_customers + 1))
    charging_station_indices = list(range(num_customers + 1, len(extended_loc_x_y)))

    # Adapt data to match the existing dataset structure
    data = {
        "distance_matrix": extended_time_matrix,  # Use the extended time matrix as distance matrix
        "locations": extended_loc_x_y,  # All locations (depot, customers, charging stations)
        "service_times": extended_stop_durations,  # Service times, including 0 for charging stations
        "time_windows": extended_time_windows,  # Time windows, extended for charging stations
        "demands": extended_demands,  # Demands, with 0 for charging stations
        "depot": depot_index,  # Depot index
        "customer_nodes": customer_indices,  # Indices of customers
        "charging_stations": charging_station_indices,  # Indices of charging stations
        "vehicle_capacities": [8000],  # EV capacity (manually assigned)
        "vehicle_types": ["EV"],  # Only EVs are considered
        "vehicle_type_list": ["EV"] , # One vehicle for now, extend as needed
        "battery_capacities": [75],  # Battery capacity of EVs
        "charging_rate":1
    }

    return data

# # Example Usage
# adapted_data = adapt_to_dataset_structure(previous_results)

# # Print the adapted dataset for verification
# print("Adapted Dataset:")
# for key, value in adapted_data.items():
#     print(f"{key}: {value}")
