
from insert_ch_stn import insert_charging_stations,insert_charging_stations_single_route,find_accessible_charging_station
from VNS import variable_neighborhood_search
from map_extend_data import adapt_to_dataset_structure, extend_data_with_charging_stations



# Main function to handle the EV and ICE routes
def process_routes_with_charging_and_vns(data, ev_routes, ice_routes):
    print("EV Routes:", ev_routes)
    print("ICE Routes:", ice_routes)

    # Step 4: Gather customers served by EV routes
    served_by_ev = set(node for route in ev_routes for node in route if node in data['customer_nodes'])
    remaining_customers = served_by_ev

    print("\nCustomers served by EV routes:", served_by_ev)
    print("Remaining customers to be processed for EV:", remaining_customers)

    # Step 5: Process EV routes for charging station insertion
    print("\nInserting charging stations into EV routes...")
    updated_ev_routes, unvisited_customers = insert_charging_stations(data, ev_routes, remaining_customers)
    print("\nFeasible EV Routes after Charging Station Insertion:")
    for route in updated_ev_routes:
        print(route)

    # Handle unvisited customers for EV
    if unvisited_customers:
        print(f"Unvisited customers after EV adjustment: {unvisited_customers}")
        # Add unvisited customers back to remaining_customers
        remaining_customers.update(unvisited_customers)

    # Step 6: Optimize EV routes using VNS
    print("\nStarting VNS optimization for EV routes...")
    optimized_ev_routes = variable_neighborhood_search(data, updated_ev_routes, num_customers=len(data['customer_nodes']), remaining_customers=remaining_customers)
    print("\nOptimized EV Routes (after VNS):")
    for route in optimized_ev_routes:
        print(route)

    # Step 7: Combine ICE and EV routes
    print("\nFinal ICE Routes:")
    for route in ice_routes:
        print(route)

    print("\nFinal EV Routes (Optimized):")
    for route in optimized_ev_routes:
        print(route)

    # Filter out depot-only routes like [0, 0]
    filtered_ice_routes = [route for route in ice_routes if len(route) > 2 or (len(route) == 2 and route[0] != route[1])]
    filtered_ev_routes = [route for route in optimized_ev_routes if len(route) > 2 or (len(route) == 2 and route[0] != route[1])]

    # Combine ICE and EV routes after filtering
    final_routes = filtered_ice_routes + filtered_ev_routes

    print("\nFinal Combined Heterogeneous Routes (ICE + Optimized EV):")
    for route in final_routes:
        print(route)

    return final_routes
