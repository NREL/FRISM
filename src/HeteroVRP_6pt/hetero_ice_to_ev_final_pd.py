from hetero_ini_vrp_b import cal_total_cost

def _build_pd_maps(data):
    """
    Returns:
      pd_pairs: list of (p,d)
      node_to_pair: dict mapping node -> (p,d)
    """
    pd_pairs = [tuple(x) for x in data['pickups_deliveries']]
    node_to_pair = {}
    for p, d in pd_pairs:
        node_to_pair[p] = (p, d)
        node_to_pair[d] = (p, d)
    return pd_pairs, node_to_pair


def extract_customers(route, data=None):
    """
    For PD: returns a list of (pickup, delivery) pairs that appear in `route`.
    Keeps compatibility with find_best_move by returning 'cust' items to move.
    """
    if data is None:
        raise ValueError("extract_customers(route, data) needs `data` for PD mode.")
    
    _, node_to_pair = _build_pd_maps(data)

    seen = set()
    pairs_in_route = []
    for n in route:
        if n == 0:
            continue
        pair = node_to_pair.get(n)
        if pair is None:
            # Node is not part of any PD request
            continue
        if pair not in seen:
            seen.add(pair)
            pairs_in_route.append(pair)
    return pairs_in_route


def remove_first_occurrence(route, customer):
    """
    customer is a tuple: (pickup_node, delivery_node)
    Removes the first occurrence of pickup and first occurrence of delivery.
    """
    p, d = customer
    new_r = route[:]

    # Remove pickup and delivery if present
    if p in new_r:
        new_r.remove(p)
    if d in new_r:
        new_r.remove(d)

    return new_r
def _ptid_and_is_ev(veh_type, data):
    """
    veh_type can be:
      - pt_id int (0..5), or
      - powertrain string like 'BE', 'D', etc.
    Returns (pt_id, is_ev_like)
    """
    if isinstance(veh_type, str):
        pt_id = data['veh_pt_and_ids'][veh_type]
    else:
        pt_id = int(veh_type)

    pt_name = data['veh_pwrtrn_types'][pt_id]  # ['D','G','BE','H2','PD','PG']
    is_ev_like = pt_name in {'BE', 'H2', 'PD', 'PG'}
    return pt_id, is_ev_like


def _infer_battery_capacity(data):
    """
    Your data['battery_capacities'] looks like it is per-vehicle instance
    (many None then 500). We'll pick the first non-None.
    """
    for b in data.get('battery_capacities', []):
        if b is not None:
            return b
    return None


def insert_customer_and_evaluate(route, customer, data, veh_type=1):
    """
    PD version.
    customer is (pickup_node, delivery_node).

    Returns list of dicts with keys:
      - 'route'
      - 'cost'
      - 'feasible'
      - 'position' (optional: (i,j))
    """
    results = []
    p, d = customer

    # Basic sanity: don’t insert if either already present
    if route.count(p) > 0 or route.count(d) > 0:
        return [{'position': None, 'route': route, 'cost': None, 'feasible': False}]

    time_windows  = data['time_windows']
    service_times = data['service_times']
    ev_savings    = data['EV_time_savings']
    vehicle_capacity = data['vehicle_capacities'][0]  

    pt_id, is_ev_like = _ptid_and_is_ev(veh_type, data)
    battery_capacity = _infer_battery_capacity(data) if is_ev_like else None

    n = len(route)

    # Pickup insertion position i: between route[i-1] and route[i]
    # We skip i=0 because depot at start, but allow i=1..n-1
    for i in range(1, n):
        # Insert pickup
        r_with_p = route[:i] + [p] + route[i:]

        # Delivery insertion position j must be AFTER pickup, in r_with_p
        # j ranges from i+1 .. len(r_with_p)-1 (before final depot is allowed; including right before last depot)
        for j in range(i + 1, len(r_with_p)):
            new_route = r_with_p[:j] + [d] + r_with_p[j:]

            # Duplicate guard (should not happen, but safe)
            if new_route.count(p) > 1 or new_route.count(d) > 1:
                continue

            feasible = True

            # ---- Capacity feasibility: dynamic along the route ----
            load = 0
            for node in new_route:
                if node == 0:
                    continue
                load += data['demands'][node]  # pickups +, deliveries -
                if load < 0 or load > vehicle_capacity:
                    feasible = False
                    break

            # ---- Time windows + (optional) battery feasibility ----
            if feasible:
                time = 0
                battery = battery_capacity if battery_capacity is not None else float('inf')

                for k in range(len(new_route) - 1):
                    from_node = new_route[k]
                    to_node   = new_route[k + 1]

                    travel_time = data['distance_matrix'][from_node][to_node]


                    base_service = service_times[from_node]
                    saving       = ev_savings[from_node]
                    service_time = max(0, base_service - saving)

                    time += travel_time

                    earliest, latest = time_windows[to_node]
                    time = max(time, earliest)
                    if time > latest:
                        feasible = False
                        break

                    time += service_time

                    if battery_capacity is not None:
                        battery -= travel_time
                        if to_node in data['charging_stations']:
                            battery = battery_capacity
                        if battery < 0:
                            feasible = False
                            break

            # ---- Cost if feasible ----
            if feasible:
                cost = cal_total_cost([new_route], data, pt_id)  # cal_total_cost expects pt_id indexing
            else:
                cost = None

            results.append({
                'position': (i, j),
                'route': new_route,
                'cost': cost,
                'feasible': feasible
            })

    return results

# ---- main improvement loop ----

def find_best_move_pd(ICE_Routes, selected_pt_ice, EV_Routes, selected_pt_ev, data):
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
            ice_customers = extract_customers(ice_route, data)
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
                    insertions = insert_customer_and_evaluate(ev_route, cust, data, veh_type=selected_pt_ev)

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


