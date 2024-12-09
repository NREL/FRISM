import random
import time
from utilities import calculate_route_cost,calculate_total_cost, is_route_feasible
from data_model import create_data_model
from new_insert_ch_stn import flatten_route, insert_charging_stations, insert_charging_stations_single_route




def variable_neighborhood_search(data, initial_routes, max_iterations=1000, no_improvement_limit=25, num_customers=None):

    if num_customers is None:
        num_customers = len(data['customer_nodes'])  # Set num_customers based on the data if not passed
    max_time_seconds = 8 * num_customers
    """
    Performs Variable Neighborhood Search (VNS) to improve the solution of the EVRP.
    Evaluates based on total route costs.
    Ensures that each customer is visited exactly once.
    """
    start_time = time.time()
    current_routes = initial_routes[:]
    current_cost = calculate_total_cost(data, current_routes, charging_rate=data['charging_rate'])
    best_routes = current_routes[:]
    best_cost = current_cost
    iteration = 0
    no_improvement_counter = 0

    # Define neighborhood operators
    neighborhood_operators = [
        intra_route_2opt_swap,
        intra_route_or_opt,
        inter_route_swap,
        inter_route_relocate,
        route_merge
    ]

    print(f"Starting VNS with initial cost: {best_cost}")

    all_customers = set(data['customer_nodes'])  # Set of all customer nodes

    while iteration < max_iterations and (time.time() - start_time) < max_time_seconds:
        k = 0  # Neighborhood index
        improvement = False

        while k < len(neighborhood_operators):
            iteration += 1
            operator = neighborhood_operators[k]

            # Shaking: Generate a neighbor solution
            shaken_routes = operator(data, best_routes)
            print(f'Generated shaken routes using operator {k}: {shaken_routes}')

            if shaken_routes != best_routes:
                # Feasibility and Cost Evaluation
                combined_customers = set()
                feasible_shaken_routes = []
                feasible = True
                for route in shaken_routes:
                    # Remove charging stations from route
                    route_without_cs = [node for node in route if node not in data['charging_stations']]
                    # Insert charging stations using the helper function
                    updated_route = insert_charging_stations_single_route(data, route_without_cs)
                    if updated_route is None:
                        feasible = False
                        break
                    if is_route_feasible(data, updated_route):
                        feasible_shaken_routes.append(updated_route)
                        route_customers = set(node for node in updated_route if node in all_customers)
                        combined_customers.update(route_customers)
                    else:
                        feasible = False
                        break

                # Check for unvisited customers
                unvisited_customers = all_customers - combined_customers
                if feasible and not unvisited_customers:
                    shaken_cost = calculate_total_cost(data, feasible_shaken_routes, charging_rate=data['charging_rate'])

                    # Local Search on Shaken Solution
                    refined_routes = local_search(data, feasible_shaken_routes)
                    refined_cost = calculate_total_cost(data, refined_routes, charging_rate=data['charging_rate'])

                    if refined_cost < best_cost:
                        best_routes = refined_routes
                        best_cost = refined_cost
                        print(f"Iteration {iteration}: Improved solution found with cost {best_cost}")
                        k = 0  # Reset neighborhood index
                        no_improvement_counter = 0
                        improvement = True
                        break  # Start over with the first neighborhood
                    else:
                        k += 1  # Move to next neighborhood
                else:
                    print(f"Unvisited customers detected: {unvisited_customers}")
                    # Attempt to reinsert unvisited customers if feasible
                    # Implement logic here if desired
                    k += 1  # Solution not feasible, move to next neighborhood
            else:
                k += 1  # No change, move to next neighborhood

            # Check time limit
            if (time.time() - start_time) >= max_time_seconds:
                print("Time limit reached. Terminating VNS.")
                break

        if not improvement:
            no_improvement_counter += 1
            if no_improvement_counter >= no_improvement_limit:
                print(f"No improvement in the last {no_improvement_limit} iterations. Terminating VNS.")
                break
        else:
            no_improvement_counter = 0  # Reset counter if there was an improvement

    print(f"VNS completed. Best cost found: {best_cost}")
    return best_routes










def local_search(data, routes):
    """
    Performs local search on the given routes to improve the solution.
    Evaluates based on total route costs.
    Ensures that each customer is visited exactly once.
    """
    best_routes = [route[:] for route in routes]
    best_cost = calculate_total_cost(data, best_routes, charging_rate=data['charging_rate'])
    improved = True
    all_customers = set(data['customer_nodes'])  # Set of all customer nodes for completeness check

    while improved:
        improved = False
        # Keep track of customer assignments
        customer_assignment = {}
        for route_index, route in enumerate(best_routes):
            for node in route:
                if node in all_customers:
                    customer_assignment[node] = route_index

        for route_index, route in enumerate(best_routes):
            if len(route) <= 3:
                continue  # Not enough nodes to perform local search

            # Apply intra-route 2-opt swap directly on the route without charging stations
            route_without_cs = [node for node in route if node not in data['charging_stations']]
            new_route = intra_route_2opt_swap_single_route(data, route_without_cs)
            if new_route and new_route != route_without_cs:
                # Insert charging stations using the helper function
                updated_route = insert_charging_stations_single_route(data, new_route)
                if updated_route is None:
                    continue  # Skip infeasible route

                # Ensure feasibility and uniqueness of customers
                route_customers = set(node for node in updated_route if node in all_customers)
                duplicates = [node for node in route_customers if customer_assignment.get(node, route_index) != route_index]
                if duplicates:
                    print(f"Debug: Duplicate customers after local search: {duplicates}")
                    continue  # Skip this modification

                # Update customer assignment
                for node in route_customers:
                    customer_assignment[node] = route_index

                # Check final feasibility
                if is_route_feasible(data, updated_route):
                    # Replace the route and check for cost improvement
                    new_routes = best_routes[:]
                    new_routes[route_index] = updated_route
                    new_cost = calculate_total_cost(data, new_routes, charging_rate=data['charging_rate'])
                    if new_cost < best_cost:
                        best_routes = new_routes
                        best_cost = new_cost
                        improved = True
                        break  # Exit to re-evaluate routes
        if not improved:
            break  # Exit if no improvement found
    return best_routes





def intra_route_2opt_swap_single_route(data, route):
    """
    Applies 2-opt swap on a single route without charging stations.
    """
    if len(route) <= 3:
        return route  # Not enough nodes to perform 2-opt swap

    best_route = route[:]
    best_cost = calculate_route_cost(data, route, charging_rate=data['charging_rate'])
    improved = False

    # Identify customer node indices
    all_customers = set(data['customer_nodes'])
    customer_indices = [i for i, node in enumerate(route) if node in all_customers]

    for i in range(len(customer_indices) - 1):
        for j in range(i + 1, len(customer_indices)):
            if customer_indices[j] - customer_indices[i] == 1:
                continue  # Skip adjacent nodes
            # Perform 2-opt swap on customer nodes
            new_route = route[:]
            new_route[customer_indices[i]:customer_indices[j]+1] = reversed(new_route[customer_indices[i]:customer_indices[j]+1])

            # Insert charging stations using the helper function
            updated_route = insert_charging_stations_single_route(data, new_route)
            if updated_route is None:
                continue  # Skip infeasible route

            # Check feasibility
            if is_route_feasible(data, updated_route):
                new_cost = calculate_route_cost(data, updated_route, charging_rate=data['charging_rate'])
                if new_cost < best_cost:
                    best_route = new_route
                    best_cost = new_cost
                    improved = True
                    break  # Accept first improvement
        if improved:
            break

    return best_route












def calculate_distance(data, node1, node2):
    # Use the distance matrix from data to get the distance between node1 and node2
    return data['distance_matrix'][node1][node2]




def intra_route_2opt_swap(data, routes):
    """
    Performs intra-route 2-opt swaps to improve routes.
    Since swapping is within the same route, customer assignments remain consistent.
    """
    new_routes = [route[:] for route in routes]  # Deep copy to avoid modifying the original routes
    all_customers = set(data['customer_nodes'])  # Set of all customer nodes

    for route_index, route in enumerate(routes):
        if len(route) <= 3:
            continue  # Not enough nodes to perform 2-opt swap

        # Identify indices of customer nodes
        customer_indices = [i for i, node in enumerate(route) if node in all_customers]

        if len(customer_indices) <= 3:
            continue  # Not enough customer nodes to perform 2-opt swap

        best_route = route[:]
        best_cost = calculate_route_cost(data, route, data['charging_rate'])
        improved = False

        for i in range(len(customer_indices) - 1):
            for j in range(i + 1, len(customer_indices)):
                if customer_indices[j] - customer_indices[i] == 1:
                    continue  # Skip adjacent nodes

                # Perform 2-opt swap on customer nodes
                new_route = route[:]
                new_route[customer_indices[i]:customer_indices[j]+1] = reversed(new_route[customer_indices[i]:customer_indices[j]+1])

                # Since we are swapping within the same route, customer assignments remain consistent

                # Check feasibility
                route_with_charging, unvisited_nodes = insert_charging_stations(data, [new_route])
                if unvisited_nodes:
                    continue  # Skip infeasible route
                route_with_charging = route_with_charging[0]

                if is_route_feasible(data, route_with_charging):
                    new_cost = calculate_route_cost(data, route_with_charging, data['charging_rate'])
                    if new_cost < best_cost:
                        best_route = route_with_charging
                        best_cost = new_cost
                        improved = True
                        break  # Accept first improvement
            if improved:
                break

        new_routes[route_index] = best_route

    return new_routes






def intra_route_or_opt(data, routes):
    """
    Applies the Or-opt move within each route.
    Ensures that customer assignments remain consistent and that no customers are lost or duplicated.
    """
    new_routes = [route[:] for route in routes]
    all_customers = set(data['customer_nodes'])
    depot = data['depot']

    for route_index, route in enumerate(routes):
        # Remove charging stations from the route
        route_without_cs = [node for node in route if node not in data['charging_stations']]
        if len(route_without_cs) <= 3:
            continue  # Not enough nodes to perform Or-opt

        original_customers = set(node for node in route_without_cs if node in all_customers)
        best_route = route_without_cs[:]
        best_cost = calculate_route_cost(data, route, charging_rate=data['charging_rate'])
        improved = False

        # Define segment length (e.g., 1 to 3 nodes)
        for segment_length in range(1, 4):
            for i in range(1, len(route_without_cs) - segment_length):
                segment = route_without_cs[i:i + segment_length]
                remaining_route = route_without_cs[:i] + route_without_cs[i + segment_length:]

                for j in range(1, len(remaining_route)):
                    new_route = remaining_route[:j] + segment + remaining_route[j:]

                    # Ensure the route starts and ends with the depot
                    if new_route[0] != depot:
                        new_route.insert(0, depot)
                    if new_route[-1] != depot:
                        new_route.append(depot)

                    # Check that the new route contains the same customers
                    new_customers = set(node for node in new_route if node in all_customers)
                    if new_customers != original_customers:
                        continue  # Skip if customers are missing or extra

                    # Insert charging stations using the helper function
                    updated_route = insert_charging_stations_single_route(data, new_route)
                    if updated_route is None:
                        continue  # Skip infeasible route

                    # Check feasibility
                    if is_route_feasible(data, updated_route):
                        new_cost = calculate_route_cost(data, updated_route, charging_rate=data['charging_rate'])
                        if new_cost < best_cost:
                            best_route = updated_route
                            best_cost = new_cost
                            improved = True
                            break  # Accept first improvement
                if improved:
                    break
            if improved:
                break

        if improved:
            new_routes[route_index] = best_route

    # After updating all routes, check for missing or duplicated customers
    assigned_customers = set()
    customer_counts = {}
    for route in new_routes:
        route_customers = set(node for node in route if node in all_customers)
        for customer in route_customers:
            customer_counts[customer] = customer_counts.get(customer, 0) + 1
        assigned_customers.update(route_customers)

    missing_customers = all_customers - assigned_customers
    duplicated_customers = [customer for customer, count in customer_counts.items() if count > 1]

    if missing_customers:
        print(f"Error: Missing customers in new_routes after intra-route Or-opt: {missing_customers}")
        # Handle missing customers appropriately
    if duplicated_customers:
        print(f"Error: Duplicated customers in new_routes after intra-route Or-opt: {duplicated_customers}")
        # Handle duplicated customers appropriately

    return new_routes









def inter_route_swap(data, routes):
    """
    Swaps customer nodes between two different routes.
    Ensures that each customer is visited exactly once.
    """
    if len(routes) < 2:
        return routes  # Need at least two routes to swap nodes

    new_routes = [route[:] for route in routes]  # Deep copy
    all_customers = set(data['customer_nodes'])
    depot = data['depot']

    # Build customer assignment map
    customer_assignment = {}
    for route_index, route in enumerate(new_routes):
        for node in route:
            if node in all_customers:
                customer_assignment[node] = route_index

    # Randomly select two different routes to swap nodes
    route_indices = random.sample(range(len(routes)), 2)
    route1_index, route2_index = route_indices[0], route_indices[1]
    route1 = new_routes[route1_index]
    route2 = new_routes[route2_index]

    # Remove charging stations from routes
    route1_without_cs = [node for node in route1 if node not in data['charging_stations']]
    route2_without_cs = [node for node in route2 if node not in data['charging_stations']]

    # Identify customer nodes in each route
    customers1 = [node for node in route1_without_cs if node in all_customers]
    customers2 = [node for node in route2_without_cs if node in all_customers]

    if not customers1 or not customers2:
        return routes  # Cannot swap if no customers in one of the routes

    # Randomly select a customer node from each route
    node1 = random.choice(customers1)
    node2 = random.choice(customers2)

    index1 = route1_without_cs.index(node1)
    index2 = route2_without_cs.index(node2)

    # Swap the nodes in the routes without charging stations
    route1_new = route1_without_cs[:]
    route2_new = route2_without_cs[:]
    route1_new[index1] = node2
    route2_new[index2] = node1

    # Ensure the routes start and end with the depot
    if route1_new[0] != depot:
        route1_new.insert(0, depot)
    if route1_new[-1] != depot:
        route1_new.append(depot)
    if route2_new[0] != depot:
        route2_new.insert(0, depot)
    if route2_new[-1] != depot:
        route2_new.append(depot)

    # Check for duplicates
    customers_route1 = set(node for node in route1_new if node in all_customers)
    customers_route2 = set(node for node in route2_new if node in all_customers)
    duplicates = customers_route1 & customers_route2
    if duplicates:
        print(f"Duplicate customers detected after swap: {duplicates}")
        return routes  # Revert to original routes

    # Update customer assignments
    customer_assignment[node1] = route2_index
    customer_assignment[node2] = route1_index

    # Insert charging stations using the helper function
    updated_route1 = insert_charging_stations_single_route(data, route1_new)
    updated_route2 = insert_charging_stations_single_route(data, route2_new)

    if updated_route1 is None or updated_route2 is None:
        return routes  # Skip if any route is infeasible

    # Check feasibility
    if is_route_feasible(data, updated_route1) and is_route_feasible(data, updated_route2):
        # Replace the routes in new_routes
        new_routes[route1_index] = updated_route1
        new_routes[route2_index] = updated_route2

        # Check for missing or duplicated customers
        assigned_customers = set()
        customer_counts = {}
        for route in new_routes:
            route_customers = set(node for node in route if node in all_customers)
            for customer in route_customers:
                customer_counts[customer] = customer_counts.get(customer, 0) + 1
            assigned_customers.update(route_customers)

        missing_customers = all_customers - assigned_customers
        duplicated_customers = [customer for customer, count in customer_counts.items() if count > 1]

        if missing_customers:
            print(f"Error: Missing customers after inter-route swap: {missing_customers}")
            return routes  # Revert to original routes
        if duplicated_customers:
            print(f"Error: Duplicated customers after inter-route swap: {duplicated_customers}")
            return routes  # Revert to original routes

        # Calculate total cost
        total_cost = calculate_total_cost(data, new_routes, data['charging_rate'])
        original_cost = calculate_total_cost(data, routes, data['charging_rate'])

        # Update new_routes if there's an improvement
        if total_cost < original_cost:
            return new_routes
        else:
            return routes
    else:
        return routes  # Return original routes if infeasible








def inter_route_relocate(data, routes):
    """
    Moves a customer node from one route to another.
    Ensures that each customer is visited exactly once.
    """
    if len(routes) < 2:
        return routes  # Need at least two routes to perform relocation

    new_routes = [route[:] for route in routes]  # Deep copy
    all_customers = set(data['customer_nodes'])
    depot = data['depot']

    # Build customer assignment map
    customer_assignment = {}
    for route_index, route in enumerate(new_routes):
        for node in route:
            if node in all_customers:
                customer_assignment[node] = route_index

    # Randomly select two different routes for relocation
    route_indices = random.sample(range(len(routes)), 2)
    source_index, target_index = route_indices[0], route_indices[1]
    source_route = new_routes[source_index]
    target_route = new_routes[target_index]

    # Remove charging stations from routes
    source_route_without_cs = [node for node in source_route if node not in data['charging_stations']]
    target_route_without_cs = [node for node in target_route if node not in data['charging_stations']]

    # Identify customer nodes in the source route
    source_customers = [node for node in source_route_without_cs if node in all_customers]

    if not source_customers:
        return routes  # No customers to relocate

    # Randomly select a customer node from source route
    node_to_move = random.choice(source_customers)
    index_in_source = source_route_without_cs.index(node_to_move)

    # Remove the node from the source route
    source_route_new = source_route_without_cs[:]
    source_route_new.pop(index_in_source)

    # Randomly select an insertion index in the target route
    insertion_indices = list(range(1, len(target_route_without_cs)))
    if not insertion_indices:
        return routes  # Cannot insert into target route

    insert_idx_in_target = random.choice(insertion_indices)

    # Insert the node into the target route
    target_route_new = target_route_without_cs[:]
    target_route_new.insert(insert_idx_in_target, node_to_move)

    # Ensure routes start and end with depot
    if source_route_new[0] != depot:
        source_route_new.insert(0, depot)
    if source_route_new[-1] != depot:
        source_route_new.append(depot)
    if target_route_new[0] != depot:
        target_route_new.insert(0, depot)
    if target_route_new[-1] != depot:
        target_route_new.append(depot)

    # Check for duplicates
    customers_source = set(node for node in source_route_new if node in all_customers)
    customers_target = set(node for node in target_route_new if node in all_customers)
    duplicates = customers_source & customers_target
    if duplicates:
        print(f"Duplicate customers detected after relocation: {duplicates}")
        return routes  # Revert to original routes

    # Update customer assignments
    customer_assignment[node_to_move] = target_index

    # Insert charging stations using the helper function
    updated_source_route = insert_charging_stations_single_route(data, source_route_new)
    updated_target_route = insert_charging_stations_single_route(data, target_route_new)

    if updated_source_route is None or updated_target_route is None:
        return routes  # Skip if any route is infeasible

    # Check feasibility
    if is_route_feasible(data, updated_source_route) and is_route_feasible(data, updated_target_route):
        # Replace the routes in new_routes
        new_routes[source_index] = updated_source_route
        new_routes[target_index] = updated_target_route

        # Check for missing or duplicated customers
        assigned_customers = set()
        customer_counts = {}
        for route in new_routes:
            route_customers = set(node for node in route if node in all_customers)
            for customer in route_customers:
                customer_counts[customer] = customer_counts.get(customer, 0) + 1
            assigned_customers.update(route_customers)

        missing_customers = all_customers - assigned_customers
        duplicated_customers = [customer for customer, count in customer_counts.items() if count > 1]

        if missing_customers:
            print(f"Error: Missing customers after inter-route relocate: {missing_customers}")
            return routes  # Revert to original routes
        if duplicated_customers:
            print(f"Error: Duplicated customers after inter-route relocate: {duplicated_customers}")
            return routes  # Revert to original routes

        # Calculate total cost
        total_cost = calculate_total_cost(data, new_routes, data['charging_rate'])
        original_cost = calculate_total_cost(data, routes, data['charging_rate'])

        # Update new_routes if there's an improvement
        if total_cost < original_cost:
            return new_routes
        else:
            return routes
    else:
        return routes  # Return original routes if infeasible













def flatten_route(route):
    """
    Flattens a route that may contain sublists into a flat list of node indices.
    """
    flat_route = []
    for node in route:
        if isinstance(node, list):
            flat_route.extend(flatten_route(node))
        else:
            flat_route.append(node)
    return flat_route





def route_merge(data, routes):
    """
    Attempts to merge two routes into one.
    Ensures that each customer is visited exactly once.
    """
    if len(routes) < 2:
        return routes  # Need at least two routes to merge

    new_routes = [route[:] for route in routes]  # Deep copy
    all_customers = set(data['customer_nodes'])
    depot = data['depot']

    # Build customer assignment map
    customer_assignment = {}
    for route_index, route in enumerate(new_routes):
        for node in route:
            if node in all_customers:
                customer_assignment[node] = route_index

    # Randomly select two different routes to merge
    route_indices = random.sample(range(len(routes)), 2)
    route1_index, route2_index = route_indices[0], route_indices[1]
    route1 = new_routes[route1_index]
    route2 = new_routes[route2_index]

    # Remove charging stations from routes
    route1_without_cs = [node for node in route1 if node not in data['charging_stations']]
    route2_without_cs = [node for node in route2 if node not in data['charging_stations']]

    # Identify customer nodes
    customers_route1 = [node for node in route1_without_cs if node in all_customers]
    customers_route2 = [node for node in route2_without_cs if node in all_customers]

    # Merge customer nodes, ensuring no duplicates
    merged_customers = customers_route1 + [node for node in customers_route2 if node not in customers_route1]

    # Create a new merged route
    merged_route = [depot] + merged_customers + [depot]

    # Insert charging stations using the helper function
    updated_merged_route = insert_charging_stations_single_route(data, merged_route)
    if updated_merged_route is None:
        return routes  # Skip if merged route is infeasible

    # Check feasibility
    if is_route_feasible(data, updated_merged_route):
        # Remove the original two routes from new_routes
        new_routes_temp = new_routes[:]
        # Remove routes in reverse order to avoid index shift
        for idx in sorted([route1_index, route2_index], reverse=True):
            del new_routes_temp[idx]
        # Add the merged route to new_routes_temp
        new_routes_temp.append(updated_merged_route)

        # Check for missing or duplicated customers
        assigned_customers = set()
        customer_counts = {}
        for route in new_routes_temp:
            route_customers = set(node for node in route if node in all_customers)
            for customer in route_customers:
                customer_counts[customer] = customer_counts.get(customer, 0) + 1
            assigned_customers.update(route_customers)

        missing_customers = all_customers - assigned_customers
        duplicated_customers = [customer for customer, count in customer_counts.items() if count > 1]

        if missing_customers:
            print(f"Error: Missing customers after route merge: {missing_customers}")
            return routes  # Revert to original routes
        if duplicated_customers:
            print(f"Error: Duplicated customers after route merge: {duplicated_customers}")
            return routes  # Revert to original routes

        # Calculate total cost
        total_cost = calculate_total_cost(data, new_routes_temp, data['charging_rate'])
        original_cost = calculate_total_cost(data, routes, data['charging_rate'])

        # Update new_routes if there's an improvement
        if total_cost < original_cost:
            return new_routes_temp
        else:
            return routes
    else:
        return routes  # Return original routes if infeasible







def validate_route(route, data):
    if route[0] != data['depot'] or route[-1] != data['depot']:
        print(f"Route does not start or end at the depot: {route}")
        return False
