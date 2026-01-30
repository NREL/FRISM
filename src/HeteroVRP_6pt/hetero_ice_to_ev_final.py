from hetero_ini_vrp_b import cal_total_cost

def extract_customers(route):
    # assumes depot is 0
    return [n for n in route if n != 0]

def remove_first_occurrence(route, customer):
    new_r = route[:]
    new_r.remove(customer)
    return new_r
def insert_customer_and_evaluate(route, customer, data, veh_type=1):
    results = []
    demand = data['demands'][customer]
    time_windows = data['time_windows']
    service_times = data['service_times']
    ev_savings = data['EV_time_savings']
    vehicle_capacity = data['vehicle_capacities'][0]  # Assuming all vehicles have same capacity
    battery_capacity = data['battery_capacities'][2] if veh_type == 1 else None  # EV only

    for pos in range(1, len(route)):  # skip depot at position 0, always end at depot
        new_route = route[:pos] + [customer] + route[pos:]
        # Check for duplicate customer
        if new_route.count(customer) > 1:
            continue

        # Check vehicle capacity
        load = 0
        feasible = True
        for node in new_route:
            if node in data['customer_nodes']:
                load += data['demands'][node]
        if load > vehicle_capacity:
            feasible = False

        # Check time windows and battery
        time = 0
        battery = battery_capacity if battery_capacity is not None else float('inf')
        for i in range(len(new_route) - 1):
            from_node = new_route[i]
            to_node = new_route[i + 1]
            travel_time = data['distance_matrix'][from_node][to_node]
            base_service = service_times[from_node]
            saving = ev_savings[from_node]
            service_time = max(0, base_service - saving)
            time += travel_time
            # Check time window
            earliest, latest = time_windows[to_node]
            time = max(time, earliest)
            if time > latest:
                feasible = False
                break
            time += service_time
            # Battery check for EV
            if veh_type == 1 and battery_capacity is not None:
                battery -= travel_time
                if to_node in data['charging_stations']:
                    battery = battery_capacity
                if battery < 0:
                    feasible = False
                    break

        # Calculate cost if feasible
        if feasible:
            cost = cal_total_cost([new_route], data, veh_type)
        else:
            cost = None
        results.append({'position': pos, 'route': new_route, 'cost': cost, 'feasible': feasible})

    return results



# ---- main improvement loop ----

def find_best_move(ICE_Routes, selected_pt_ice, EV_Routes, selected_pt_ev, data):
    improved = True
    iteration = 0

    while improved:
        iteration += 1
        improved = False
        # print(f"\n=== Iteration {iteration} ===")

        # Current baseline costs
        current_EV_cost  = cal_total_cost(EV_Routes,  data, selected_pt_ev)
        current_ICE_cost = cal_total_cost(ICE_Routes, data, selected_pt_ice)
        current_total_cost = current_EV_cost + current_ICE_cost
        # print("Current total cost:", current_total_cost)

        best_move = None
        best_delta = 0.0  # we want negative

        # Enumerate all ICE customers across all ICE routes
        for ice_r_idx, ice_route in enumerate(ICE_Routes):
            ice_customers = extract_customers(ice_route)
            if not ice_customers:
                continue

            # Cost of this ICE route alone
            ice_route_cost_before = cal_total_cost([ice_route], data, selected_pt_ice)

            for cust in ice_customers:
                # Remove customer from its ICE route
                new_ice_route = remove_first_occurrence(ice_route, cust)
                # Cost of ICE route after removal (could be depot->depot)
                ice_route_cost_after = cal_total_cost([new_ice_route], data, selected_pt_ice) if len(new_ice_route) > 2 else 0.0
                delta_ice = ice_route_cost_after - ice_route_cost_before  # can be negative if route becomes empty

                # Try inserting into each EV route
                for ev_r_idx, ev_route in enumerate(EV_Routes):
                    # Cost of this EV route alone (before)
                    ev_route_cost_before = cal_total_cost([ev_route], data, selected_pt_ev)

                    # Get all feasible insertions of `cust` into this EV route 
                    insertions = insert_customer_and_evaluate(ev_route, cust, data, veh_type=1)

                    for ins in insertions:
                        if not ins.get('feasible'):
                            continue
                        cand_ev_route_cost = ins.get('cost', None)
                        cand_ev_route      = ins.get('route', None)
                        if cand_ev_route_cost is None or cand_ev_route is None:
                            continue

                        # New total cost if we apply this specific move:
                        # Replace the EV route cost, replace the ICE route cost (after removal), others unchanged
                        new_total_cost = (
                            current_total_cost
                            - ev_route_cost_before + cand_ev_route_cost
                            - ice_route_cost_before + ice_route_cost_after
                        )
                        delta_total = new_total_cost - current_total_cost  # negative is good

                        # Track the best improving move
                        if delta_total < best_delta - 1e-9:
                            best_delta = delta_total
                            best_move = {
                                'ice_r_idx': ice_r_idx,
                                'cust': cust,
                                'ev_r_idx': ev_r_idx,
                                'cand_ev_route': cand_ev_route,
                                'new_ice_route': new_ice_route,
                                'new_total_cost': new_total_cost
                            }

        # Apply the best move (if any)
        if best_move is not None:
            # print(f"Applying best move: ICE customer {best_move['cust']} -> EV route {best_move['ev_r_idx']}")
            # print(f"Δtotal cost = {best_delta:.4f} | New total = {best_move['new_total_cost']:.4f}")

            # Update ICE route: remove the customer (and possibly drop empty routes)
            ICE_Routes[best_move['ice_r_idx']] = best_move['new_ice_route']
            
            if len(ICE_Routes[best_move['ice_r_idx']]) <= 2:
                ICE_Routes[best_move['ice_r_idx']] = [0, 0]  

            # Update the specific EV route with the candidate route returned by the oracle
            EV_Routes[best_move['ev_r_idx']] = best_move['cand_ev_route']

            improved = True
        else:
            print("No improving move found. Stopping.")
    return ICE_Routes, EV_Routes


