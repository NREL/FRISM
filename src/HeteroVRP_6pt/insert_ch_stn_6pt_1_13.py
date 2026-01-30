
# ELECTRIC AND HETEROGENEOUS MIXED FLEET VARIANT OF FRISM

from utilities_b import calculate_route_cost, calculate_total_cost, is_route_feasible, flatten_route

def find_accessible_charging_station(data, current_node, battery_remaining):
    """Finds the nearest charging station that can be reached with the remaining battery."""
    min_distance = float('inf')
    nearest_station = None
    for station in data['charging_stations']:
        distance = data['distance_matrix'][current_node][station]       # Need to be adjusted if charging discharging rate is different from 1
        if distance <= battery_remaining and distance < min_distance: 
            min_distance = distance
            nearest_station = station
    return nearest_station

def filter_pd_pairs_for_ev(data, ev_customers):
    pd_pairs = data.get('pickups_deliveries', [])
    ev_pairs = []
    for (p, d) in pd_pairs:
        if int(p) in ev_customers and int(d) in ev_customers:
            ev_pairs.append((int(p), int(d)))
    return ev_pairs




# ----------------------------
# Helper (shared)
# ----------------------------
def find_accessible_charging_station(data, current_node, battery_remaining):
    """
    Delivery-only / generic helper:
    returns a reachable CS (heuristic = nearest by distance_matrix).
    """
    min_distance = float("inf")
    nearest_station = None
    for station in data.get("charging_stations", []):
        if station == current_node:
            continue
        dist = data["distance_matrix"][current_node][station]
        if dist <= battery_remaining and dist < min_distance:
            min_distance = dist
            nearest_station = station
    return nearest_station


# ============================================================
# 1) DELIVERY-ONLY: single route CS insertion (cleaned)
# ============================================================
def insert_charging_stations_single_route(data, route, selected_pt):
    """
    Delivery-only EV route feasibility with CS insertion.
    - No pickup/delivery constraints.
    - Respects time windows & service times.
    Returns:
        updated_route (list[int]) if feasible else None
    """

    # --- normalize route nodes to ints ---
    norm_route = []
    for node in route:
        if isinstance(node, str):
            if node.isdigit():
                norm_route.append(int(node))
            else:
                raise ValueError(
                    f"Route contains non-integer node '{node}' which cannot index distance_matrix."
                )
        else:
            norm_route.append(int(node))
    route = norm_route

    depot = int(data["depot"])
    charging_stations = set(data.get("charging_stations", []))

    battery_capacity = data["battery_capacities"][-1]  # EV battery
    charging_rate = data["charging_rate"]

    # if OR-Tools route doesn't start at depot, we'll still simulate from depot
    updated_route = [depot]
    battery_remaining = battery_capacity
    current_time = 0.0

    def _lookup(tbl, idx, default):
        if tbl is None:
            return default
        if isinstance(tbl, dict):
            return tbl.get(idx, default)
        try:
            return tbl[idx]
        except Exception:
            return default

    def energy_needed(i, j):
      
        # Keep same approach as requested.
        return data["distance_matrix"][i][j]

    def try_drive(i, j):
        nonlocal battery_remaining, current_time
        tt = data["distance_matrix"][i][j]
        e_need = energy_needed(i, j)
        if battery_remaining < e_need:
            return False
        battery_remaining -= e_need
        current_time += tt
        return True

    def charge_to(level=1.0):
        nonlocal battery_remaining, current_time
        target_energy = level * battery_capacity
        if target_energy <= battery_remaining:
            return
        missing = target_energy - battery_remaining
        t_charge = missing / charging_rate
        current_time += t_charge
        battery_remaining = target_energy

    def apply_node_visit(node_id):
        nonlocal current_time
        tw_earliest, tw_latest = _lookup(
            data.get("time_windows"), node_id, (0, float("inf"))
        )

        if current_time < tw_earliest:
            current_time = tw_earliest
        if current_time > tw_latest:
            return False

        if node_id in charging_stations:
            charge_to(level=1.0)
        else:
            base_service = _lookup(data.get("service_times"), node_id, 0.0)
            ev_save = _lookup(data.get("EV_time_savings"), node_id, 0.0)
            dwell = max(0.0, base_service - ev_save)
            current_time += dwell
        return True

    # visit depot first
    if not apply_node_visit(depot):
        return None

    idx = 1
    while idx < len(route):
        target = route[idx]
        curr = updated_route[-1]

        # proactive recharge if SoC is LOW
        soc = battery_remaining / battery_capacity
        if soc < data.get("soc_threshold", 0.0):
            cs = find_accessible_charging_station(data, curr, battery_remaining)
            if cs is not None and cs != curr:
                if not try_drive(curr, cs):
                    return None
                updated_route.append(cs)
                if not apply_node_visit(cs):
                    return None
                continue  # retry same target

        # try drive curr -> target
        if not try_drive(curr, target):
            cs = find_accessible_charging_station(data, curr, battery_remaining)
            if cs is None or cs == curr:
                return None
            if not try_drive(curr, cs):
                return None
            updated_route.append(cs)
            if not apply_node_visit(cs):
                return None
            continue  # retry same target

        # arrived target
        updated_route.append(target)
        if not apply_node_visit(target):
            return None

        idx += 1

    # ensure end at depot (with CS hops if needed)
    if updated_route[-1] != depot:
        curr = updated_route[-1]
        while curr != depot:
            if try_drive(curr, depot):
                updated_route.append(depot)
                if not apply_node_visit(depot):
                    return None
                break
            cs = find_accessible_charging_station(data, curr, battery_remaining)
            if cs is None or cs == curr:
                return None
            if not try_drive(curr, cs):
                return None
            updated_route.append(cs)
            if not apply_node_visit(cs):
                return None
            curr = cs

    return updated_route


# ============================================================
# 2) DELIVERY-ONLY: multi-route CS insertion 
# ============================================================
def insert_charging_stations(data, routes, remaining_customers, selected_pt):
    """
    Delivery-only version of the multi-route wrapper.
    Returns:
        updated_routes: list[list[int]]
        final_unvisited: list[int]
    """
    depot = int(data["depot"])
    charging_stations = set(data.get("charging_stations", []))
    all_customers = set(int(c) for c in remaining_customers)

    def _is_valid_route(obj):
        if not isinstance(obj, list):
            return False
        for n in obj:
            if isinstance(n, int):
                continue
            if isinstance(n, str) and n.isdigit():
                continue
            return False
        return True

    def _normalized_route(route):
        out = []
        for n in route:
            if isinstance(n, int):
                out.append(int(n))
            elif isinstance(n, str) and n.isdigit():
                out.append(int(n))
            else:
                raise ValueError(
                    f"Route has non-integer node '{n}' which cannot index distance_matrix."
                )
        return out

    def _collect_customers_from_route(route):
        custs = []
        for node in route:
            if node == depot:
                continue
            if node in charging_stations:
                continue
            if node in all_customers:
                custs.append(node)
        return custs

    updated_routes = []
    unvisited_customers = set()

    # 1) process each given route
    for route in routes:
        if not route:
            continue

        trial_result = insert_charging_stations_single_route(
            data, route, selected_pt
        )

        if _is_valid_route(trial_result):
            updated_routes.append(_normalized_route(trial_result))
        else:
            unvisited_customers.update(_collect_customers_from_route(_normalized_route(route)))

    # 2) served so far
    served_so_far = set()
    for r in updated_routes:
        served_so_far.update(_collect_customers_from_route(r))

    unvisited_customers.update(all_customers - served_so_far)

    # 3) try inserting each unvisited customer into existing routes
    for customer in list(unvisited_customers):
        best_insertion_cost = float("inf")
        best_route_index = None
        best_trial_route_with_cs = None

        for idx, base_route in enumerate(updated_routes):
            route_wo_cs = [n for n in base_route if n not in charging_stations]

            for pos in range(1, len(route_wo_cs)):
                trial_route_no_cs = route_wo_cs[:pos] + [customer] + route_wo_cs[pos:]

                trial_result = insert_charging_stations_single_route(
                    data, trial_route_no_cs, selected_pt
                )
                if not _is_valid_route(trial_result):
                    continue

                trial_norm = _normalized_route(trial_result)

                if is_route_feasible(data, trial_norm):
                    trial_cost = calculate_route_cost(
                        data, trial_norm, selected_pt, data["charging_rate"]
                    )
                    if trial_cost < best_insertion_cost:
                        best_insertion_cost = trial_cost
                        best_route_index = idx
                        best_trial_route_with_cs = trial_norm

        if best_route_index is not None:
            updated_routes[best_route_index] = best_trial_route_with_cs
            unvisited_customers.discard(customer)

    # 4) create new route for leftover singles
    for customer in list(unvisited_customers):
        simple_route = [depot, customer, depot]
        trial_result = insert_charging_stations_single_route(
            data, simple_route, selected_pt
        )

        if _is_valid_route(trial_result):
            trial_norm = _normalized_route(trial_result)
            if is_route_feasible(data, trial_norm):
                updated_routes.append(trial_norm)
                unvisited_customers.remove(customer)

    # 5) final accounting
    served_after = set()
    for r in updated_routes:
        served_after.update(_collect_customers_from_route(r))

    final_unvisited = list(all_customers - served_after)
    return updated_routes, final_unvisited


def insert_charging_stations_single_route_pd(
    data,
    route,
    selected_pt,              
    required_pd_pairs=None,   # None => allow partial PD service in this route
):
    """
    PD version that follows ONLY the same processes as insert_charging_stations_single_route():
      - step through nodes in the given route
      - time windows
      - battery check; if insufficient insert a reachable charging station
      - service time for non-CS nodes; charging time for CS nodes
      - enforce pickup-before-delivery (PD necessary change)
      - attempt return to depot at end
      - if required_pd_pairs given, require those pairs completed in this route
    """

   
    # print("route in insert_charging_stations_single_route_pd:", route)
    norm_route = []
    for node in route:
        if isinstance(node, int):
            norm_route.append(int(node))
        elif isinstance(node, str) and node.isdigit():
            norm_route.append(int(node))
        else:
            raise ValueError(
                f"Route contains non-integer node '{node}' which cannot index distance_matrix."
            )
    route = norm_route

    depot = int(data["depot"])
    charging_stations = set(int(x) for x in data.get("charging_stations", []))


    battery_capacity = float(data["battery_capacities"][-1])
    battery_remaining = battery_capacity

    charging_rate = float(data["charging_rate"])  

    arrival_time = 0.0
    infeasible = False

    # ---- PD ordering setup ----
    all_pd_pairs = data.get("pickups_deliveries", [])
    all_pd_pairs = [(int(p), int(d)) for (p, d) in all_pd_pairs]

    pickup_nodes = set(p for p, d in all_pd_pairs)
    dropoff_nodes = set(d for p, d in all_pd_pairs)

    prereq_for = {}
    for p, d in all_pd_pairs:
        prereq_for.setdefault(d, set()).add(p)

    visited_pickups = set()
    visited_dropoffs = set()

    def ok_to_visit(node_id: int) -> bool:
        """PD rule: dropoff only after required pickup(s) visited."""
        if node_id == depot or node_id in charging_stations:
            return True
        if node_id in pickup_nodes:
            return True
        if node_id in dropoff_nodes:
            needed = prereq_for.get(node_id, set())
            return needed.issubset(visited_pickups)
        # If it's neither pickup nor dropoff, treat as normal customer
        return True

    def _lookup(tbl, idx, default):
        if tbl is None:
            return default
        if isinstance(tbl, dict):
            return tbl.get(idx, default)
        try:
            return tbl[idx]
        except Exception:
            return default

    def find_accessible_charging_station_pd(curr, battery_rem, next_node):
        """
        Minimal necessary improvement: choose a CS that is reachable now,
        AND from which next_node is reachable after a full charge.
        """
        best_cs = None
        best_score = float("inf")
        for cs in charging_stations:
            if cs == curr:
                continue
            e_to_cs = data["distance_matrix"][curr][cs]
            if e_to_cs > battery_rem:
                continue
            e_cs_to_next = data["distance_matrix"][cs][next_node]
            if e_cs_to_next > battery_capacity:
                continue
            score = e_to_cs + e_cs_to_next
            if score < best_score:
                best_score = score
                best_cs = cs
        return best_cs

    updated_route = [depot]

    # ---- main loop, same structure as delivery-only ----
    i = 1
    while i < len(route):
        from_node = updated_route[-1]
        to_node = int(route[i])

        # PD ordering check (necessary PD change)
        if not ok_to_visit(to_node):
            infeasible = True
            # print("infeasible at PD ordering")
            break

        travel_time = float(data["distance_matrix"][from_node][to_node])
        battery_consumption = travel_time  

        # update arrival time and enforce time window at to_node
        arrival_time += travel_time
        tw_earliest, tw_latest = _lookup(data.get("time_windows"), to_node, (0.0, float("inf")))

        if arrival_time < tw_earliest:
            arrival_time = tw_earliest
        elif arrival_time > tw_latest:
            infeasible = True
            # print("infeasible at time window")
            break

        if battery_remaining >= battery_consumption:
            # go to the node
            updated_route.append(to_node)
            battery_remaining -= battery_consumption

            # service or charge at the node
            if to_node in charging_stations:
                # FIX: compute missing BEFORE setting battery to full
                missing = battery_capacity - battery_remaining
                charging_time = missing * charging_rate
                battery_remaining = battery_capacity
                departure_time = arrival_time + charging_time
            else:
                service_time = float(_lookup(data.get("service_times"), to_node, 0.0))
                departure_time = arrival_time + service_time

            if departure_time > tw_latest:
                infeasible = True
                # print("infeasible at service/charge time window")
                break

            arrival_time = departure_time

            # update PD visited sets if applicable
            if to_node in pickup_nodes:
                visited_pickups.add(to_node)
            if to_node in dropoff_nodes:
                visited_dropoffs.add(to_node)

            i += 1

        else:
            # Not enough battery to reach to_node -> insert a charging station
            cs = find_accessible_charging_station_pd(from_node, battery_remaining, to_node)
            if cs is None or updated_route[-1] == cs:
                infeasible = True
                # print("infeasible at CS selection")
                break

            # drive to CS (still must be reachable by our selection)
            e_to_cs = float(data["distance_matrix"][from_node][cs])
            if battery_remaining < e_to_cs:
                infeasible = True
                # print("infeasible at CS reachability")
                break

            updated_route.append(cs)
            battery_remaining -= e_to_cs

            # apply time window at CS too (same logic as any node)
            arrival_time += e_to_cs
            cs_tw_earliest, cs_tw_latest = _lookup(data.get("time_windows"), cs, (0.0, float("inf")))
            if arrival_time < cs_tw_earliest:
                arrival_time = cs_tw_earliest
            elif arrival_time > cs_tw_latest:
                infeasible = True
                # print("infeasible at CS time window")
                break

            # charge at CS (FIXED)
            missing = battery_capacity - battery_remaining
            charging_time = missing * charging_rate
            battery_remaining = battery_capacity
            departure_time = arrival_time + charging_time

            if departure_time > cs_tw_latest:
                infeasible = True
                break

            arrival_time = departure_time
            # do NOT increment i; we will retry the same to_node next iteration

    # ---- attempt return to depot (same spirit as delivery-only) ----
    if not infeasible:
        last_node = updated_route[-1]
        if last_node != depot:
            dist_to_depot = float(data["distance_matrix"][last_node][depot])
            if battery_remaining >= dist_to_depot:
                updated_route.append(depot)
                arrival_time += dist_to_depot
            else:
                # try one CS hop then depot (minimal extension; otherwise PD routes die too often)
                cs = find_accessible_charging_station_pd(last_node, battery_remaining, depot)
                if cs is None or cs == last_node:
                    infeasible = True
                else:
                    e_to_cs = float(data["distance_matrix"][last_node][cs])
                    if battery_remaining < e_to_cs:
                        infeasible = True
                    else:
                        updated_route.append(cs)
                        battery_remaining -= e_to_cs
                        arrival_time += e_to_cs

                        cs_tw_earliest, cs_tw_latest = _lookup(data.get("time_windows"), cs, (0.0, float("inf")))
                        if arrival_time < cs_tw_earliest:
                            arrival_time = cs_tw_earliest
                        elif arrival_time > cs_tw_latest:
                            infeasible = True

                        if not infeasible:
                            missing = battery_capacity - battery_remaining
                            charging_time = missing * charging_rate
                            battery_remaining = battery_capacity
                            arrival_time += charging_time

                            dist_cs_to_depot = float(data["distance_matrix"][cs][depot])
                            if battery_remaining >= dist_cs_to_depot:
                                updated_route.append(depot)
                                arrival_time += dist_cs_to_depot
                            else:
                                infeasible = True

    if infeasible:
        return None

    # ---- required PD completion (
    if required_pd_pairs is not None:
        req = [(int(p), int(d)) for (p, d) in required_pd_pairs]
        for (p, d) in req:
            if p not in visited_pickups or d not in visited_dropoffs:
                return None

    return updated_route

    

def insert_charging_stations_pd(data, routes, required_pd_pairs, selected_pt):

    print("hi from insert_charging_stations_pd")
    """
    PD multi-route wrapper WITH the additional operations from insert_charging_stations:
      1) process each given route (insert CS)
      2) identify unserved required PD pairs
      3) try inserting each unserved (p,d) pair into existing routes (best cost)
      4) create new route(s) for leftover pair(s)
      5) final accounting: return updated_routes and final_unvisited customer nodes

    Returns:
      updated_routes: list[list[int]]
      final_unvisited_customers: list[int]  # pickup/delivery nodes from pairs still not served
    """
    depot = int(data["depot"])
    charging_stations = set(int(x) for x in data.get("charging_stations", []))
    required_pd_pairs = [(int(p), int(d)) for (p, d) in required_pd_pairs]

    # -----------------------
    # helpers
    # -----------------------
    def _is_valid_route(obj):
        if not isinstance(obj, list):
            return False
        for n in obj:
            if isinstance(n, int):
                continue
            if isinstance(n, str) and n.isdigit():
                continue
            return False
        return True

    def _normalized_route(route):
        out = []
        for n in route:
            if isinstance(n, int):
                out.append(int(n))
            elif isinstance(n, str) and n.isdigit():
                out.append(int(n))
            else:
                raise ValueError(
                    f"Route has non-integer node '{n}' which cannot index distance_matrix."
                )
        return out

    def _route_wo_cs(route):
        return [n for n in route if n not in charging_stations]

    def _extract_pd_served(route):
        """
        Served required pairs in this route by precedence:
          served if pickup appears before delivery somewhere in the route.
        """
        first_pos = {}
        for i, n in enumerate(route):
            if n not in first_pos:
                first_pos[n] = i

        served = set()
        for (p, d) in required_pd_pairs:
            if p in first_pos and d in first_pos and first_pos[p] < first_pos[d]:
                served.add((p, d))
        return served

    def _check_required_precedence(route, pairs_to_check=None):
        """
        Extra guard: ensure for each (p,d) in pairs_to_check that if both appear,
        then p must appear before d.
        """
        if pairs_to_check is None:
            pairs_to_check = required_pd_pairs

        first_pos = {}
        for i, n in enumerate(route):
            if n not in first_pos:
                first_pos[n] = i

        for (p, d) in pairs_to_check:
            if p in first_pos and d in first_pos:
                if first_pos[p] >= first_pos[d]:
                    return False
        return True

    def _try_insert_pair_into_route(base_route, p, d):
        """
        Try all (i,j) insertion positions on the CS-stripped base route,
        with i<j, inserting p then d. For each trial:
          - run insert_charging_stations_single_route_pd
          - check precedence + is_route_feasible
          - compute cost
        Return best (trial_route_with_cs, trial_cost) or (None, inf)
        """
        route0 = _route_wo_cs(base_route)

        L = len(route0)
        if L < 2:
            return None, float("inf")

        best_cost = float("inf")
        best_route = None

        # Insert pickup at position i, delivery at position j>i
        # Positions are indices in the list (before element at that index).
        # We typically avoid inserting before the first depot (i=0),
        # so start at 1. Also allow inserting before the final depot.
        for i in range(1, L):  # pickup insertion
            for j in range(i + 1, L + 1):  # delivery insertion after pickup
                trial_no_cs = route0[:i] + [p] + route0[i:]
                # after inserting pickup, list length increased by 1, so delivery index shifts by +1 if j>i
                trial_no_cs = trial_no_cs[:j] + [d] + trial_no_cs[j:]

                trial = insert_charging_stations_single_route_pd(
                    data,
                    trial_no_cs,
                    selected_pt,
                    required_pd_pairs=None,  # allow partial in a route; we'll enforce precedence ourselves
                )
                if not _is_valid_route(trial):
                    continue

                trial = _normalized_route(trial)

                # precedence guard for ALL required pairs that appear in this route
                if not _check_required_precedence(trial, required_pd_pairs):
                    continue

                if not is_route_feasible(data, trial):
                    continue

                trial_cost = calculate_route_cost(
                    data, trial, selected_pt, data["charging_rate"]
                )
                if trial_cost < best_cost:
                    best_cost = trial_cost
                    best_route = trial

        return best_route, best_cost

    # -----------------------
    # 1) process each given route (CS insertion)
    # -----------------------
    updated_routes = []
    served_pairs = set()

    for route in routes:
        if not route:
            continue

        trial = insert_charging_stations_single_route_pd(
            data,
            route,
            selected_pt,
            required_pd_pairs=None,  # allow partial
        )

        if not _is_valid_route(trial):
           
            continue

        trial = _normalized_route(trial)

        # extra precedence guard (avoid returning a route with reversed required PD order)
        if not _check_required_precedence(trial, required_pd_pairs):
            continue

        updated_routes.append(trial)
        served_pairs |= _extract_pd_served(trial)

    # -----------------------
    # 2) compute unserved pairs
    # -----------------------
    unserved_pd_pairs = [pair for pair in required_pd_pairs if pair not in served_pairs]

    # -----------------------
    # 3) try inserting each unserved pair into existing routes (best insertion)
    # -----------------------
    # Iterate over a copy; we will remove from set as we serve
    unserved_set = set(unserved_pd_pairs)
    print("unserved_set at start of insertion:", unserved_set)

    for (p, d) in list(unserved_set):
        print(f"Attempting to insert unserved pair ({p},{d}) into existing routes")
        best_insertion_cost = float("inf")
        best_route_index = None
        best_trial_route_with_cs = None

        for idx, base_route in enumerate(updated_routes):
            print(f"Evaluating route {idx} for insertion of pair ({p},{d})")
            trial_route, trial_cost = _try_insert_pair_into_route(base_route, p, d)
            print(f"Trying to insert pair ({p},{d}) into route {idx}: trial_cost={trial_cost}, trial_route={trial_route}")
            if trial_route is None:
                continue

            if trial_cost < best_insertion_cost:
                best_insertion_cost = trial_cost
                best_route_index = idx
                best_trial_route_with_cs = trial_route

        if best_route_index is not None:
            updated_routes[best_route_index] = best_trial_route_with_cs
            served_pairs.add((p, d))
            unserved_set.discard((p, d))

    # -----------------------
    # 4) create new route(s) for leftover pairs
    # -----------------------
    for (p, d) in list(unserved_set):
        simple_route = [depot, p, d, depot]
        print(f"Creating new route for unserved pair ({p},{d}), simple_route={simple_route}")

        trial = insert_charging_stations_single_route_pd(
            data,
            simple_route,
            selected_pt,
            required_pd_pairs=None,
        )
        print("trial result for new route:", trial)


        if not _is_valid_route(trial):
            continue

        trial = _normalized_route(trial)

        if not _check_required_precedence(trial, [(p, d)]):
            continue

        if is_route_feasible(data, trial):
            updated_routes.append(trial)
            served_pairs.add((p, d))
            unserved_set.discard((p, d))

    # -----------------------
    # 5) final accounting: return updated_routes and final_unvisited customer nodes
    # -----------------------
    final_unserved_pairs = [pair for pair in required_pd_pairs if pair not in served_pairs]

    final_unvisited_customers = set()
    for (p, d) in final_unserved_pairs:
        final_unvisited_customers.add(p)
        final_unvisited_customers.add(d)

    return updated_routes, list(final_unvisited_customers), final_unserved_pairs



# def insert_charging_stations_pd(data, routes, required_pd_pairs, selected_pt):
#     """
#     PD multi-route wrapper.

#     - Each route is processed independently with CS insertion.
#     - We DO NOT force every route to serve all pairs.
#     - We return which required pairs remain unserved overall.

#     Args:
#       routes: list of base routes (may include pickups and deliveries)
#       required_pd_pairs: list of (pickup, delivery) pairs that must be served overall

#     Returns:
#       updated_routes: list[list[int]]
#       unserved_pd_pairs: list[(p,d)]
#     """
#     depot = int(data["depot"])
#     charging_stations = set(data.get("charging_stations", []))

#     required_pd_pairs = [(int(p), int(d)) for (p, d) in required_pd_pairs]
#     print("depot:", depot)
#     print("charging_stations:", charging_stations)
#     print("required_pd_pairs:", required_pd_pairs)

#     def _is_valid_route(obj):
#         if not isinstance(obj, list):
#             return False
#         for n in obj:
#             if isinstance(n, int):
#                 continue
#             if isinstance(n, str) and n.isdigit():
#                 continue
#             return False
#         return True

#     def _normalized_route(route):
#         out = []
#         for n in route:
#             if isinstance(n, int):
#                 out.append(int(n))
#             elif isinstance(n, str) and n.isdigit():
#                 out.append(int(n))
#             else:
#                 raise ValueError(
#                     f"Route has non-integer node '{n}' which cannot index distance_matrix."
#                 )
#         return out

#     def _extract_pd_served(route):
#         """
#         Determine served required pairs in this route by order:
#           served if pickup appears before delivery somewhere in the route.
#         """
#         first_pos = {}
#         for i, n in enumerate(route):
#             if n not in first_pos:
#                 first_pos[n] = i

#         served = set()
#         for (p, d) in required_pd_pairs:
#             if p in first_pos and d in first_pos and first_pos[p] < first_pos[d]:
#                 served.add((p, d))
#         return served

#     updated_routes = []
#     served_pairs = set()

#     for route in routes:
#         if not route:
#             continue

#         trial = insert_charging_stations_single_route_pd(
#             data,
#             route,
#             selected_pt,
#             required_pd_pairs=None,  # IMPORTANT: allow partial service per route
#         )

#         if not _is_valid_route(trial):
#             continue

#         trial = _normalized_route(trial)
#         updated_routes.append(trial)
#         served_pairs |= _extract_pd_served(trial)

#     unserved_pd_pairs = [pair for pair in required_pd_pairs if pair not in served_pairs]
#     print("unserved_pd_pairs:", unserved_pd_pairs)
#     # Flatten unserved_pd_pairs to a single list of unique customer node IDs
#     unvisited_customers = set()
#     for p, d in unserved_pd_pairs:
#         unvisited_customers.add(p)
#         unvisited_customers.add(d)
#     unvisited_customers = list(unvisited_customers)
#     return updated_routes, unvisited_customers

