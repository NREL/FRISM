import random
import time
from utilities_b import calculate_route_cost,calculate_total_cost, is_route_feasible
# from hetero_ini_vrp_b import create_data_model
from insert_ch_stn_6pt_1_13 import flatten_route, insert_charging_stations_pd, insert_charging_stations_single_route_pd



def variable_neighborhood_search_pd(
    data,
    initial_routes,
    selected_pt,
    required_pd_pairs,
    max_iterations=1000,
    no_improvement_limit=25,
    num_customers=None,
):
    required_pairs, all_pairs, pickup_nodes, delivery_nodes, pair_of, prereq_for = build_pd_structures(data, required_pd_pairs)
    # print("initial_routes in VNS_pd:", initial_routes)

    if num_customers is None:
        num_customers = len(required_pairs)
    max_time_seconds = 8 * max(1, num_customers)

    start_time = time.time()

    # Initial feasibility cleanup: insert CS for all initial routes
    # current_routes = []
    # for r in initial_routes:
    #     r0 = remove_charging_stations(r, set(data.get("charging_stations", [])))
    #     upd = cs_insert_and_check_pd(data, r0, selected_pt, prereq_for)
    #     if upd is None:
    #         continue
    #     current_routes.append(upd)
    # print("current_routes after initial CS insert:", current_routes)

    # if not current_routes:
    #     return initial_routes
    current_routes = initial_routes[:]
    # print("current_routes at start of VNS_pd:", current_routes)

    best_routes = [r[:] for r in current_routes]
    # print("best_routes at start of VNS_pd:", best_routes)
    best_cost = calculate_total_cost(data, best_routes, selected_pt, charging_rate=data["charging_rate"])

    iteration = 0
    no_improvement_counter = 0

    # PD-safe operators 
    neighborhood_operators = [
        intra_route_or_opt_pd_safe,                  # will be gated by PD checks in evaluation
        route_merge,                         # will be gated by PD checks in evaluation
        inter_route_swap_pd_pair,            # PD-safe
        inter_route_relocate_pd_pair,        # PD-safe
        intra_route_2opt_swap_pd,       # PD-safe
    ]

    while iteration < max_iterations and (time.time() - start_time) < max_time_seconds:
        k = 0
        improvement = False

        while k < len(neighborhood_operators):
            iteration += 1
            operator = neighborhood_operators[k]
            # print(f"Iteration {iteration}, applying operator: {operator.__name__}")
            # print("required_pd_pairs:", required_pairs)

            # Shaking
            
            shaken_routes = operator(data, best_routes, selected_pt, required_pairs)
            # print("shaken_routes:", shaken_routes)


            if shaken_routes == best_routes:
                k += 1
                continue

            # Evaluate shaken solution: CS insert + precedence + feasibility for each route
            feasible_routes = []
            served_pairs = set()
            feasible = True

            for route in shaken_routes:
                r0 = remove_charging_stations(route, set(data.get("charging_stations", [])))
                upd = cs_insert_and_check_pd(data, r0, selected_pt, prereq_for)
                if upd is None:
                    feasible = False
                    break
                feasible_routes.append(upd)
                served_pairs |= extract_served_required_pairs(upd, required_pairs)

            unserved = set(required_pairs) - served_pairs

            if feasible and not unserved:
                shaken_cost = calculate_total_cost(data, feasible_routes, selected_pt, charging_rate=data["charging_rate"])

           
                refined_routes = local_search_pd(data, feasible_routes, selected_pt, required_pd_pairs)
                refined_cost = calculate_total_cost(data, refined_routes, selected_pt, charging_rate=data['charging_rate'])


                if refined_cost < best_cost:
                    best_routes = [r[:] for r in refined_routes]
                    best_cost = refined_cost
                    k = 0
                    no_improvement_counter = 0
                    improvement = True
                    break
                else:
                    k += 1
            else:
                # Debug prints if needed
                # print("Unserved pairs:", list(unserved)[:10])
                k += 1

            if (time.time() - start_time) >= max_time_seconds:
                # print("Time limit reached during VNS_pd.")
                break

        if not improvement:
            no_improvement_counter += 1
            if no_improvement_counter >= no_improvement_limit:
                # print("No improvement limit reached. Ending VNS_pd.")
                break
        else:
            no_improvement_counter = 0
            # print("Improvement found. Continuing VNS_pd.")
        print("iteration count:", iteration, "best_cost:", best_cost)

    return best_routes


import random

def _normalize_route_nodes(route):
    out = []
    for n in route:
        if isinstance(n, int):
            out.append(int(n))
        elif isinstance(n, str) and n.isdigit():
            out.append(int(n))
        else:
            # keep non-int nodes out of distance matrix indexing
            raise ValueError(f"Non-integer node in route: {n}")
    return out

def local_search_pd(data, routes, selected_pt, required_pd_pairs):
    """
    PD-safe local search for EV routes.

    Methodology mirrors delivery-only local_search:
      - Loop over routes
      - Remove charging stations
      - Perform intra-route improvement
      - Reinsert charging stations
      - Enforce PD feasibility + uniqueness
      - Accept first improving move

    required_pd_pairs: list of (pickup, delivery) pairs
    """

    required_pd_pairs = [(int(p), int(d)) for (p, d) in required_pd_pairs]

    # --- helper maps ---
    node_to_pair = {}
    for pid, (p, d) in enumerate(required_pd_pairs):
        node_to_pair[p] = pid
        node_to_pair[d] = pid

    def strip_cs(route):
        return [n for n in route if n not in data["charging_stations"]]

    def pairs_in_route(route_wo_cs):
        """Return PD-pair indices fully contained in this route; None if split."""
        present = set(route_wo_cs)
        pairs = set()
        for pid, (p, d) in enumerate(required_pd_pairs):
            if p in present or d in present:
                if not (p in present and d in present):
                    return None  # split PD pair
                pairs.add(pid)
        return pairs

    def pd_order_ok(route_wo_cs):
        """Pickup must appear before delivery."""
        pos = {n: i for i, n in enumerate(route_wo_cs)}
        for (p, d) in required_pd_pairs:
            if p in pos or d in pos:
                if not (p in pos and d in pos):
                    return False
                if pos[p] >= pos[d]:
                    return False
        return True

    def generate_2opt(route):
        """Simple intra-route 2-opt (endpoints fixed)."""
        n = len(route)
        for i in range(1, n - 2):
            for k in range(i + 1, n - 1):
                yield route[:i] + list(reversed(route[i:k + 1])) + route[k + 1 :]

    # --- initial solution ---
    best_routes = [r[:] for r in routes]
    best_cost = calculate_total_cost(
        data, best_routes, selected_pt, charging_rate=data["charging_rate"]
    )

    improved = True
    while improved:
        improved = False

        # Track PD-pair → route assignment
        pair_assignment = {}

        for r_idx, route in enumerate(best_routes):
            for node in route:
                if node in node_to_pair:
                    pid = node_to_pair[node]
                    pair_assignment[pid] = r_idx

        for r_idx, route in enumerate(best_routes):
            if len(route) <= 3:
                continue

            route_wo_cs = strip_cs(route)

            # Skip infeasible base routes
            base_pairs = pairs_in_route(route_wo_cs)
            if base_pairs is None or not pd_order_ok(route_wo_cs):
                continue

            for cand_wo_cs in generate_2opt(route_wo_cs):

                # PD ordering must hold
                if not pd_order_ok(cand_wo_cs):
                    continue

                cand_pairs = pairs_in_route(cand_wo_cs)
                if cand_pairs is None:
                    continue

                # PD-aware charging insertion
                updated_route = insert_charging_stations_single_route_pd(
                    data,
                    cand_wo_cs,
                    selected_pt,
                    required_pd_pairs=[required_pd_pairs[pid] for pid in cand_pairs],
                )

                if updated_route is None:
                    continue
                if not is_route_feasible(data, updated_route):
                    continue

                # Enforce PD-pair uniqueness across routes
                conflict = False
                for pid in cand_pairs:
                    if pair_assignment.get(pid, r_idx) != r_idx:
                        conflict = True
                        break
                if conflict:
                    continue

                # Evaluate move
                new_routes = best_routes[:]
                new_routes[r_idx] = updated_route
                new_cost = calculate_total_cost(
                    data, new_routes, selected_pt, charging_rate=data["charging_rate"]
                )

                if new_cost < best_cost:
                    best_routes = new_routes
                    best_cost = new_cost
                    improved = True
                    break

            if improved:
                break

    return best_routes


def build_pd_structures(data, required_pd_pairs=None):
    """
    Returns:
      required_pairs: list[(p,d)]
      all_pairs: list[(p,d)]
      pickup_nodes, delivery_nodes
      pair_of: dict[node -> (p,d)]
      prereq_for: dict[delivery -> set(pickups)]
    """

    all_pairs = [(int(p), int(d)) for (p, d) in data.get("pickups_deliveries", [])]
    # print("all_pairs:", all_pairs)

    if required_pd_pairs is None:
        required_pairs = [(int(p), int(d)) for (p, d) in all_pairs]
    else:
        required_pairs = [(int(p), int(d)) for (p, d) in required_pd_pairs]
    # print("required_pairs:", required_pairs)


    pickup_nodes = set(p for p, _ in all_pairs)
    delivery_nodes   = set(d for _, d in all_pairs)
    # print("pickup_nodes:", pickup_nodes)
    # print("delivery_nodes:", delivery_nodes)

    pair_of = {}
    prereq_for = {}
    for p, d in all_pairs:
        pair_of[p] = (p, d)
        pair_of[d] = (p, d)
        prereq_for.setdefault(d, set()).add(p)

    # print("pair_of:", pair_of)
    # print("prereq_for:", prereq_for)

    return required_pairs, all_pairs, pickup_nodes, delivery_nodes, pair_of, prereq_for

def pd_precedence_ok(route, prereq_for, charging_stations=None, depot=None):
    """
    Returns False if any delivery appears before its pickup(s).
    Ignores depot/charging stations for ordering.
    """
    if charging_stations is None:
        charging_stations = set()
    seen_pickups = set()

    for n in route:
        if depot is not None and n == depot:
            continue
        if n in charging_stations:
            continue

        # if this node is a delivery, ensure its pickup(s) are already seen
        needed = prereq_for.get(n, None)
        if needed is not None and not needed.issubset(seen_pickups):
            return False

        # if it's a pickup, mark it as seen
        # (safe to mark everything; only pickups matter via prereq check)
        seen_pickups.add(n)

    return True

def extract_served_required_pairs(route, required_pairs):
    """
    A required pair (p,d) is served if both appear and p appears before d.
    """
    first_pos = {}
    for i, n in enumerate(route):
        if n not in first_pos:
            first_pos[n] = i

    served = set()
    for (p, d) in required_pairs:
        if p in first_pos and d in first_pos and first_pos[p] < first_pos[d]:
            served.add((p, d))
    return served

def remove_charging_stations(route, charging_stations):
    return [n for n in route if n not in charging_stations]


def cs_insert_and_check_pd(data, route_wo_cs, selected_pt, prereq_for):
    """
    1) Insert charging stations 
    2) Check PD precedence
    3) Check general feasibility 
    """
    depot = int(data["depot"])
    charging_stations = set(int(x) for x in data.get("charging_stations", []))
    # print("selected_pt in cs_insert_and_check_pd:", selected_pt)

    # Ensure route starts/ends at depot 
    if route_wo_cs[0] != depot:
        route_wo_cs = [depot] + route_wo_cs
    if route_wo_cs[-1] != depot:
        route_wo_cs = route_wo_cs + [depot]

    updated = insert_charging_stations_single_route_pd(
        data=data,
        route=route_wo_cs,
        selected_pt=selected_pt,
        required_pd_pairs=None
    )

    if updated is None:
        return None

    # precedence gate (critical)
    if not pd_precedence_ok(updated, prereq_for, charging_stations=charging_stations, depot=depot):
        return None

    if not is_route_feasible(data, updated):
        return None

    return updated



def intra_route_2opt_swap_pd(
    data,
    routes,
    selected_pt,
    required_pd_pairs,   # list of (p,d) pairs that must be respected
):
    """
    Intra-route 2-opt for Pickup & Delivery

    Same structure as delivery-only:
      - for each route: generate 2-opt moves (on customer nodes)
      - reject moves that violate pickup-before-delivery
      - reinsert charging stations (PD-aware)
      - accept first improvement
    """

    new_routes = [route[:] for route in routes]

    # Normalize PD pairs to ints and build lookup
    required_pd_pairs = [(int(p), int(d)) for (p, d) in required_pd_pairs]
    pickup_set = set(p for p, _ in required_pd_pairs)
    delivery_set = set(d for _, d in required_pd_pairs)
    pd_nodes = pickup_set | delivery_set

    # Map node -> (pair_id, role)
    node_to_pair = {}
    for pid, (p, d) in enumerate(required_pd_pairs):
        node_to_pair[p] = (pid, "P")
        node_to_pair[d] = (pid, "D")

    def strip_cs(route):
        return [n for n in route if n not in data["charging_stations"]]

    def pd_order_ok(route_wo_cs):
        """Check pickup appears before delivery for every PD pair present in this route."""
        pos = {n: i for i, n in enumerate(route_wo_cs)}
        for (p, d) in required_pd_pairs:
            if p in pos or d in pos:
                # if one is present, require both (no split pairs inside this route)
                if not (p in pos and d in pos):
                    return False
                if pos[p] >= pos[d]:
                    return False
        return True

    def pairs_present(route_wo_cs):
        """Return list of PD pairs (p,d) fully present in the route."""
        present = set(route_wo_cs)
        pairs_here = []
        for (p, d) in required_pd_pairs:
            if p in present or d in present:
                if not (p in present and d in present):
                    return None  # split pair
                pairs_here.append((p, d))
        return pairs_here

    for route_index, route in enumerate(routes):
        if len(route) <= 3:
            continue

        route_wo_cs = strip_cs(route)

        # Indices of PD nodes only (so we 2-opt "customers")
        customer_indices = [i for i, node in enumerate(route_wo_cs) if node in pd_nodes]
        if len(customer_indices) <= 3:
            new_routes[route_index] = route[:]  # unchanged
            continue

        best_route = route[:]  # keep original (with CS) as baseline
        best_cost = calculate_route_cost(data, route, selected_pt, data["charging_rate"])
        improved = False

        # Try 2-opt moves (first improvement)
        for a in range(len(customer_indices) - 1):
            for b in range(a + 1, len(customer_indices)):

                i = customer_indices[a]
                j = customer_indices[b]
                if j - i == 1:
                    continue  # skip adjacent

                cand_wo_cs = route_wo_cs[:]
                cand_wo_cs[i : j + 1] = reversed(cand_wo_cs[i : j + 1])

                # PD precedence filter (core PD change)
                if not pd_order_ok(cand_wo_cs):
                    continue

                # Identify which PD pairs are in this route to pass into PD-aware charging insertion
                pairs_here = pairs_present(cand_wo_cs)
                if pairs_here is None:
                    continue

                # Insert charging stations with PD-aware inserter
               
                cand_with_cs = insert_charging_stations_single_route_pd(
                    data,
                    cand_wo_cs,
                    selected_pt,
                    required_pd_pairs=pairs_here,
                )
                if cand_with_cs is None:
                    continue

                if not is_route_feasible(data, cand_with_cs):
                    continue

                new_cost = calculate_route_cost(data, cand_with_cs, selected_pt, data["charging_rate"])
                if new_cost < best_cost:
                    best_route = cand_with_cs
                    best_cost = new_cost
                    improved = True
                    break
            if improved:
                break

        new_routes[route_index] = best_route

    return new_routes

def intra_route_or_opt_pd_safe(data, routes, selected_pt, required_pd_pairs):
    """
    PD-safe intra-route Or-opt (segment relocate) using the SAME principles as delivery-only Or-opt:
      - Work route-by-route
      - Remove charging stations
      - Try Or-opt moves (segment length 1..3)
      - Ensure the same requests remain in the route (no loss/duplication)
      - Enforce pickup-before-delivery (precedence) + no split pairs
      - Reinsert charging stations with PD-aware inserter
      - Accept first improvement

    required_pd_pairs: list of (pickup_node, delivery_node) pairs.
    Assumes:
      - data['depot'], data['charging_stations'], data['charging_rate'] exist
      - insert_charging_stations_single_route_pd(data, route_wo_cs, selected_pt, required_pd_pairs=...) exists
      - is_route_feasible(...) and calculate_route_cost(...) exist
    """
    depot = data["depot"]
    charging_stations = set(data["charging_stations"])
    required_pd_pairs = [(int(p), int(d)) for (p, d) in required_pd_pairs]

    # Node -> pair id lookup (useful for fast membership checks)
    node_to_pair = {}
    for pid, (p, d) in enumerate(required_pd_pairs):
        node_to_pair[p] = pid
        node_to_pair[d] = pid

    def strip_cs(route):
        return [n for n in route if n not in charging_stations]

    def pairs_in_route(route_wo_cs):
        """
        Return set of pair-ids fully present in this route.
        If any pair is split (only p or only d), return None.
        """
        present = set(route_wo_cs)
        pair_ids = set()
        for pid, (p, d) in enumerate(required_pd_pairs):
            if p in present or d in present:
                if not (p in present and d in present):
                    return None
                pair_ids.add(pid)
        return pair_ids

    def precedence_ok(route_wo_cs):
        """Pickup must occur before delivery for every pair present in the route."""
        pos = {n: i for i, n in enumerate(route_wo_cs)}
        for (p, d) in required_pd_pairs:
            if p in pos or d in pos:
                if not (p in pos and d in pos):
                    return False
                if pos[p] >= pos[d]:
                    return False
        return True

    new_routes = [r[:] for r in routes]

    for route_index, route in enumerate(routes):
        # Remove charging stations (operate on the pure PD visit sequence)
        route_wo_cs = strip_cs(route)
        if len(route_wo_cs) <= 3:
            continue

        # Ensure depot at ends in the working sequence
        if route_wo_cs[0] != depot:
            route_wo_cs = [depot] + route_wo_cs
        if route_wo_cs[-1] != depot:
            route_wo_cs = route_wo_cs + [depot]

        # Identify which PD requests belong to this route (and validate no split)
        base_pair_ids = pairs_in_route(route_wo_cs)
        if base_pair_ids is None:
            continue  # route already splits a request
        if not precedence_ok(route_wo_cs):
            continue  # route already violates precedence

        # For "same customers" logic in PD: keep the same set of PAIRS in the route
        original_pair_ids = set(base_pair_ids)

        # Baseline: use cost of the original route (with CS) like delivery-only function
        best_route = route[:]  # keep best WITH charging stations
        best_cost = calculate_route_cost(data, route, selected_pt, charging_rate=data["charging_rate"])
        improved = False

        # Or-opt segment lengths 1..3 (same principle)
        for segment_length in range(1, 4):
            # don't move depot endpoints
            for i in range(1, len(route_wo_cs) - segment_length):
                segment = route_wo_cs[i : i + segment_length]

                # Skip if segment includes depot (shouldn't happen because i starts at 1, but safe)
                if depot in segment:
                    continue

                remaining_route = route_wo_cs[:i] + route_wo_cs[i + segment_length :]

                for j in range(1, len(remaining_route)):
                    cand_wo_cs = remaining_route[:j] + segment + remaining_route[j:]

                    # Ensure depot at ends 
                    if cand_wo_cs[0] != depot:
                        cand_wo_cs.insert(0, depot)
                    if cand_wo_cs[-1] != depot:
                        cand_wo_cs.append(depot)

                    # PD constraints: no split pairs + precedence
                    cand_pair_ids = pairs_in_route(cand_wo_cs)
                    if cand_pair_ids is None:
                        continue
                    if cand_pair_ids != original_pair_ids:
                        continue  # ensures no request is lost/added 
                    if not precedence_ok(cand_wo_cs):
                        continue

                    # Build required pair list for this route (only the pairs in this route)
                    required_pairs_here = [required_pd_pairs[pid] for pid in sorted(cand_pair_ids)]

                    # Insert charging stations with PD-aware function 
                    updated_route = insert_charging_stations_single_route_pd(
                        data, cand_wo_cs, selected_pt, required_pd_pairs=required_pairs_here
                    )
                    if updated_route is None:
                        continue

                    # Feasibility + cost check
                    if is_route_feasible(data, updated_route):
                        new_cost = calculate_route_cost(
                            data, updated_route, selected_pt, charging_rate=data["charging_rate"]
                        )
                        if new_cost < best_cost:
                            best_route = updated_route
                            best_cost = new_cost
                            improved = True
                            break  # accept first improvement

                if improved:
                    break
            if improved:
                break

        if improved:
            new_routes[route_index] = best_route

    # --- Global sanity check: each PD pair should appear in exactly one route ---
    pair_counts = {pid: 0 for pid in range(len(required_pd_pairs))}

    for r in new_routes:
        r_wo_cs = strip_cs(r)
        present = set(r_wo_cs)
        for pid, (p, d) in enumerate(required_pd_pairs):
            if p in present or d in present:
                # count only if both are present; if split, treat as an issue
                if p in present and d in present:
                    pair_counts[pid] += 1
                else:
                    print(f"Warning: Split PD pair in final routes: {(p, d)}")

    missing_pairs = [required_pd_pairs[pid] for pid, c in pair_counts.items() if c == 0]
    duplicated_pairs = [required_pd_pairs[pid] for pid, c in pair_counts.items() if c > 1]

    if missing_pairs:
        print(f"Warning: Missing PD pairs after intra-route Or-opt: {missing_pairs}")
    if duplicated_pairs:
        print(f"Warning: Duplicated PD pairs after intra-route Or-opt: {duplicated_pairs}")

    return new_routes


import random

def route_merge(data, routes, selected_pt, required_pd_pairs):
    """
    PD-safe route merge operator.

    Attempts to merge two EV routes into one for Pickup & Delivery.
    Ensures:
      - No split requests: if a pickup/delivery appears, its paired node must also appear
      - Precedence: pickup occurs before delivery for every request in the merged route
      - Each PD pair is served exactly once across all routes (pair-level uniqueness)
      - EV feasibility after charging-station insertion

    Inputs:
      data: must contain
        - 'depot'
        - 'charging_stations'
        - 'charging_rate'
      routes: list[list[int]] routes, may include charging stations
      selected_pt: passed through to cost/charging insertion
      required_pd_pairs: list[(pickup, delivery)] defining all requests in the current solution


    """

    if len(routes) < 2:
        return routes

    depot = data["depot"]
    charging_stations = set(data["charging_stations"])
    pd_pairs = [(int(p), int(d)) for (p, d) in required_pd_pairs]

    # --- maps for fast checks ---
    node_to_pair = {}
    for pid, (p, d) in enumerate(pd_pairs):
        node_to_pair[p] = (pid, "P")
        node_to_pair[d] = (pid, "D")

    def strip_cs(route):
        return [n for n in route if n not in charging_stations]

    def pair_ids_in_route(route_wo_cs):
        """
        Return set of pair ids fully present in this route.
        If any request is split (only p or only d), return None.
        """
        present = set(route_wo_cs)
        ids = set()
        for pid, (p, d) in enumerate(pd_pairs):
            if p in present or d in present:
                if not (p in present and d in present):
                    return None
                ids.add(pid)
        return ids

    def precedence_ok(route_wo_cs):
        """Pickup must occur before delivery for each pair present."""
        pos = {n: i for i, n in enumerate(route_wo_cs)}
        for (p, d) in pd_pairs:
            if p in pos or d in pos:
                if not (p in pos and d in pos):
                    return False
                if pos[p] >= pos[d]:
                    return False
        return True

    def repair_precedence(sequence):
        """
        Simple precedence repair:
          - keep relative order as much as possible
          - whenever a delivery appears before its pickup, move pickup just before that delivery

        Returns repaired sequence (without charging stations). Depot endpoints preserved outside.
        """
        seq = sequence[:]
        # positions update loop
        changed = True
        while changed:
            changed = False
            pos = {n: i for i, n in enumerate(seq)}
            for (p, d) in pd_pairs:
                if p in pos and d in pos and pos[p] > pos[d]:
                    # move pickup to just before delivery
                    seq.pop(pos[p])
                    pos = {n: i for i, n in enumerate(seq)}  # refresh after pop
                    insert_at = pos[d]
                    seq.insert(insert_at, p)
                    changed = True
                    break
        return seq

    # Work on a copy
    new_routes = [r[:] for r in routes]

    # Randomly select two different routes to merge
    r1_idx, r2_idx = random.sample(range(len(new_routes)), 2)
    r1 = new_routes[r1_idx]
    r2 = new_routes[r2_idx]

    r1_wo_cs = strip_cs(r1)
    r2_wo_cs = strip_cs(r2)

    # Identify which PD requests belong to each route (must be fully present)
    r1_pair_ids = pair_ids_in_route(r1_wo_cs)
    r2_pair_ids = pair_ids_in_route(r2_wo_cs)
    if r1_pair_ids is None or r2_pair_ids is None:
        return routes  # don't merge if either route already splits a request

    # Build global pair assignment from the CURRENT solution (pair -> route index)
    pair_assignment = {}
    for idx, rt in enumerate(new_routes):
        ids = pair_ids_in_route(strip_cs(rt))
        if ids is None:
            return routes  # solution already inconsistent for PD
        for pid in ids:
            # If pid appears in multiple routes, solution is already inconsistent
            if pid in pair_assignment and pair_assignment[pid] != idx:
                return routes
            pair_assignment[pid] = idx

    # Determine merged pair set; must not conflict outside r1/r2 (it shouldn't, but we enforce)
    merged_pair_ids = set(r1_pair_ids) | set(r2_pair_ids)
    for pid in merged_pair_ids:
        assigned = pair_assignment.get(pid, None)
        if assigned is not None and assigned not in (r1_idx, r2_idx):
            return routes  # would duplicate a request across routes

    # --- Construct merged sequence (without charging stations) ---
    # Preserve as much original order as possible:
    # take route1's PD nodes in order, then route2's PD nodes that are not already added
    def pd_nodes_in_order(route_wo_cs, allowed_pair_ids):
        nodes = []
        for n in route_wo_cs:
            if n == depot:
                continue
            if n in node_to_pair:
                pid, _ = node_to_pair[n]
                if pid in allowed_pair_ids:
                    nodes.append(n)
        return nodes

    seq1 = pd_nodes_in_order(r1_wo_cs, r1_pair_ids)
    seq2 = pd_nodes_in_order(r2_wo_cs, r2_pair_ids)

    seen = set()
    merged_seq = []
    for n in seq1 + seq2:
        if n not in seen:
            merged_seq.append(n)
            seen.add(n)

    # Precedence repair (ensures pickup before delivery)
    merged_seq = repair_precedence(merged_seq)

    merged_route_wo_cs = [depot] + merged_seq + [depot]

    # Final PD checks (no split + precedence)
    final_ids = pair_ids_in_route(merged_route_wo_cs)
    if final_ids is None or final_ids != merged_pair_ids:
        return routes
    if not precedence_ok(merged_route_wo_cs):
        return routes

    required_pairs_here = [pd_pairs[pid] for pid in sorted(merged_pair_ids)]

    # Insert charging stations (PD-aware)
    updated_merged_route = insert_charging_stations_single_route_pd(
        data,
        merged_route_wo_cs,
        selected_pt,
        required_pd_pairs=required_pairs_here,
    )
    if updated_merged_route is None:
        return routes

    # Check feasibility
    if not is_route_feasible(data, updated_merged_route):
        return routes

    # Build new route set: remove originals, add merged
    new_routes_temp = new_routes[:]
    for idx in sorted([r1_idx, r2_idx], reverse=True):
        del new_routes_temp[idx]
    new_routes_temp.append(updated_merged_route)

    # Global PD sanity: every pair appears exactly once across routes
    counts = {pid: 0 for pid in range(len(pd_pairs))}
    for rt in new_routes_temp:
        ids = pair_ids_in_route(strip_cs(rt))
        if ids is None:
            return routes
        for pid in ids:
            counts[pid] += 1

    missing_pairs = [pd_pairs[pid] for pid, c in counts.items() if c == 0]
    duplicated_pairs = [pd_pairs[pid] for pid, c in counts.items() if c > 1]
    if missing_pairs or duplicated_pairs:
        return routes

    # Cost improvement check
    total_cost = calculate_total_cost(data, new_routes_temp, selected_pt, data["charging_rate"])
    original_cost = calculate_total_cost(data, routes, selected_pt, data["charging_rate"])

    return new_routes_temp if total_cost < original_cost else routes


# def route_merge(data, routes, selected_pt, remaining_customers):
#     """
#     Attempts to merge two EV routes into one, focusing on `remaining_customers`.
#     Ensures that each `remaining_customer` is visited exactly once.
#     """
#     if len(routes) < 2:
#         return routes  # Need at least two routes to merge

#     new_routes = [route[:] for route in routes]  # Deep copy
#     remaining_customers = set(remaining_customers)  # Convert to set for faster checks
#     depot = data['depot']

#     # Build customer assignment map
#     customer_assignment = {}
#     for route_index, route in enumerate(new_routes):
#         for node in route:
#             if node in remaining_customers:
#                 customer_assignment[node] = route_index

#     # Randomly select two different routes to merge
#     route_indices = random.sample(range(len(routes)), 2)
#     route1_index, route2_index = route_indices[0], route_indices[1]
#     route1 = new_routes[route1_index]
#     route2 = new_routes[route2_index]

#     # Remove charging stations from routes
#     route1_without_cs = [node for node in route1 if node not in data['charging_stations']]
#     route2_without_cs = [node for node in route2 if node not in data['charging_stations']]

#     # Identify customer nodes
#     customers_route1 = [node for node in route1_without_cs if node in remaining_customers]
#     customers_route2 = [node for node in route2_without_cs if node in remaining_customers]

#     # Merge customer nodes, ensuring no duplicates
#     merged_customers = customers_route1 + [node for node in customers_route2 if node not in customers_route1]

#     # Create a new merged route
#     merged_route = [depot] + merged_customers + [depot]

#     # Insert charging stations using the helper function
#     updated_merged_route = insert_charging_stations_single_route_pd(data, merged_route, selected_pt)
#     if updated_merged_route is None:
#         return routes  # Skip if merged route is infeasible

#     # Check feasibility
#     if is_route_feasible(data, updated_merged_route):
#         # Remove the original two routes from new_routes
#         new_routes_temp = new_routes[:]
#         # Remove routes in reverse order to avoid index shift
#         for idx in sorted([route1_index, route2_index], reverse=True):
#             del new_routes_temp[idx]
#         # Add the merged route to new_routes_temp
#         new_routes_temp.append(updated_merged_route)

#         # Check for missing or duplicated `remaining_customers`
#         assigned_customers = set()
#         customer_counts = {}
#         for route in new_routes_temp:
#             route_customers = set(node for node in route if node in remaining_customers)
#             for customer in route_customers:
#                 customer_counts[customer] = customer_counts.get(customer, 0) + 1
#             assigned_customers.update(route_customers)

#         missing_customers = remaining_customers - assigned_customers
#         duplicated_customers = [customer for customer, count in customer_counts.items() if count > 1]

#         if missing_customers:
#             print(f"Warning: Missing customers after route merge: {missing_customers}")
#             return routes  # Revert to original routes if critical customers are missing
#         if duplicated_customers:
#             print(f"Warning: Duplicated customers after route merge: {duplicated_customers}")
#             return routes  # Revert to original routes if duplicates are found

#         # Calculate total cost
#         total_cost = calculate_total_cost(data, new_routes_temp, selected_pt,  data['charging_rate'])
#         original_cost = calculate_total_cost(data, routes, selected_pt, data['charging_rate'])

#         # Update new_routes if there's an improvement
#         if total_cost < original_cost:
#             return new_routes_temp
#         else:
#             return routes
#     else:
#         return routes  # Return original routes if infeasible



def inter_route_relocate_pd_pair(data, routes, selected_pt, required_pd_pairs):
    """
    Move a whole (p,d) pair from one route to another, keeping p before d.
    """
    if len(routes) < 2:
        return routes

    depot = int(data["depot"])
    charging_stations = set(int(x) for x in data.get("charging_stations", []))
    required_pairs, all_pairs, pickup_nodes, delivery_nodes, pair_of, prereq_for = build_pd_structures(data, required_pd_pairs)

    new_routes = [r[:] for r in routes]

    # pick source/target routes
    src_idx, tgt_idx = random.sample(range(len(new_routes)), 2)
    src = remove_charging_stations(new_routes[src_idx], charging_stations)
    tgt = remove_charging_stations(new_routes[tgt_idx], charging_stations)

    # find which required pairs are fully present in src
    src_pairs_present = []
    src_set = set(src)
    for (p, d) in required_pairs:
        if p in src_set and d in src_set:
            # ensure p occurs before d in src
            if src.index(p) < src.index(d):
                src_pairs_present.append((p, d))

    if not src_pairs_present:
        return routes

    p, d = random.choice(src_pairs_present)

    # remove p and d from src
    src2 = [n for n in src if n not in (p, d)]
    if len(src2) < 2:  # must still be depot..depot
        return routes

    # insert into tgt: choose insertion positions i<j
    # positions between 1 and len-1 (inside depots)
    if tgt[0] != depot:
        tgt = [depot] + tgt
    if tgt[-1] != depot:
        tgt = tgt + [depot]

    best = None
    best_cost = float("inf")

    for i in range(1, len(tgt)):         # pickup position
        for j in range(i + 1, len(tgt)+1):  # delivery position after pickup
            trial_tgt = tgt[:i] + [p] + tgt[i:]
            trial_tgt = trial_tgt[:j] + [d] + trial_tgt[j:]

            upd_src = cs_insert_and_check_pd(data, src2, selected_pt, prereq_for)
            if upd_src is None:
                continue
            upd_tgt = cs_insert_and_check_pd(data, trial_tgt, selected_pt, prereq_for)
            if upd_tgt is None:
                continue

            trial_routes = new_routes[:]
            trial_routes[src_idx] = upd_src
            trial_routes[tgt_idx] = upd_tgt

            cost = calculate_total_cost(data, trial_routes, selected_pt, charging_rate=data["charging_rate"])
            if cost < best_cost:
                best_cost = cost
                best = trial_routes

    return best if best is not None else routes


def inter_route_swap_pd_pair(data, routes, selected_pt, required_pd_pairs):
    """
    Swap (p1,d1) in route A with (p2,d2) in route B (whole pairs).
    """
    if len(routes) < 2:
        return routes

    depot = int(data["depot"])
    charging_stations = set(int(x) for x in data.get("charging_stations", []))
    required_pairs, all_pairs, pickup_nodes, delivery_nodes, pair_of, prereq_for = build_pd_structures(data, required_pd_pairs)

    new_routes = [r[:] for r in routes]
    a_idx, b_idx = random.sample(range(len(new_routes)), 2)
    a = remove_charging_stations(new_routes[a_idx], charging_stations)
    b = remove_charging_stations(new_routes[b_idx], charging_stations)

    a_set, b_set = set(a), set(b)

    a_pairs = [(p, d) for (p, d) in required_pairs if p in a_set and d in a_set and a.index(p) < a.index(d)]
    b_pairs = [(p, d) for (p, d) in required_pairs if p in b_set and d in b_set and b.index(p) < b.index(d)]
    if not a_pairs or not b_pairs:
        return routes

    p1, d1 = random.choice(a_pairs)
    p2, d2 = random.choice(b_pairs)

    a2 = [n for n in a if n not in (p1, d1)]
    b2 = [n for n in b if n not in (p2, d2)]

    if a2[0] != depot: a2 = [depot] + a2
    if a2[-1] != depot: a2 = a2 + [depot]
    if b2[0] != depot: b2 = [depot] + b2
    if b2[-1] != depot: b2 = b2 + [depot]

    # simplest: insert swapped pair as consecutive (p then d) near end
    def try_insert_pair(base, p, d):
        best = None
        best_cost = float("inf")
        for i in range(1, len(base)):
            for j in range(i + 1, len(base)+1):
                trial = base[:i] + [p] + base[i:]
                trial = trial[:j] + [d] + trial[j:]
                upd = cs_insert_and_check_pd(data, trial, selected_pt, prereq_for)
                if upd is None:
                    continue
                c = calculate_route_cost(data, upd, selected_pt, charging_rate=data["charging_rate"])
                if c < best_cost:
                    best_cost = c
                    best = upd
        return best

    upd_a = try_insert_pair(a2, p2, d2)
    upd_b = try_insert_pair(b2, p1, d1)
    if upd_a is None or upd_b is None:
        return routes

    trial_routes = new_routes[:]
    trial_routes[a_idx] = upd_a
    trial_routes[b_idx] = upd_b

    # accept if improves
    if calculate_total_cost(data, trial_routes, selected_pt, data["charging_rate"]) < \
       calculate_total_cost(data, routes, selected_pt, data["charging_rate"]):
        return trial_routes

    return routes
