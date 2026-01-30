# Author: Megh KC
# ELECTRIC AND HETEROGENEOUS MIXED FLEET VARIANT OF FRISM


# Import necessary modules for the test
import random
import numpy as np
import math
import contextlib
import os
import ortools
import traceback
import copy
# print("ortools version:", ortools.__version__)


# Set a seed for reproducibility

from ortools.constraint_solver import routing_enums_pb2, pywrapcp

# Check if the 'results' folder exists, if not, create it
if not os.path.exists('results'):
    os.makedirs('results')
# Check if the 'data' folder exists, if not, create it
if not os.path.exists('data'):
    os.makedirs('data')

# Define the generate_unique_location function
def generate_unique_location(existing_locations, range_min=-50, range_max=50):
    while True:
        x = random.randint(range_min, range_max)
        y = random.randint(range_min, range_max)
        if (x, y) not in existing_locations:
            return (x, y)


def cal_total_cost(routes, data, selected_pt, do_ceil=False):
    """
    veh_type is the POWERTRAIN ID (pt_id), e.g. 0,1,2,3,4,5
    to match: calculate_total_cost(...) behavior
    """
    total_cost = 0.0
    used_vehicles = 0

    for route in routes:
        if len(route) <= 2:
            continue

        used_vehicles += 1
        pt_id = data['veh_pt_and_ids'][selected_pt]
        fixed = data['fixed_cost'][pt_id]
        # print(" data['fixed_cost'][pt_id]:",  data['fixed_cost'][pt_id])

        route_time = 0.0
        
        for i in range(len(route) - 1):
            from_node = route[i]
            to_node   = route[i + 1]

            travel_time = data['distance_matrix'][from_node][to_node]  

            service_time = 0.0
            if to_node in data['customer_nodes']:
                base = data['service_times'][to_node]
                save = data['EV_time_savings'][to_node]
                service_time = max(0, base - save)

            route_time += travel_time + service_time
        

        total_cost += fixed + route_time * data['cost_per_unit_time'][pt_id]
        # print("cost=", data['cost_per_unit_time'][pt_id])

    return math.ceil(total_cost) if do_ceil else total_cost


def solve_initial_vrp(data, index, comm=None, num_customers=None, verbose=True):
    """
    Adds:
      - preflight validation (sizes, indices, time window sanity)
      - feasibility diagnostics (depot reachability wrt TW, PD reachability)
      - try/except blocks with tracebacks
      - prints solver status if solution=None


    """

    def log(*args):
        if verbose:
            print(*args)

    try:
        # -----------------------------
        # 0) Basic counts / node set
        # -----------------------------
        if num_customers is None:
            num_customers = len(data['customer_nodes'])
        log(f"Solving initial VRP for {num_customers} customers.")

        num_nodes = len(data['customer_nodes']) + 1  # depot + customers
        log("num_nodes:", num_nodes)
        log("num vehicles:", data.get('num_vehicles'),
            "start len:", len(data.get('start', [])),
            "end len:", len(data.get('end', [])))

        # -----------------------------
        # 1) Preflight shape checks
        # -----------------------------
        # Matrix sizes
        dist = data['distance_matrix']
        tw   = data['time_windows']
        dem  = data['demands']
        srv  = data['service_times']
        evs  = data['EV_time_savings']

        assert len(dist) >= num_nodes, f"distance_matrix rows={len(dist)} < num_nodes={num_nodes}"
        for r, row in enumerate(dist[:num_nodes]):
            assert len(row) >= num_nodes, f"distance_matrix row {r} cols={len(row)} < num_nodes={num_nodes}"

        assert len(tw) >= num_nodes, f"time_windows len={len(tw)} < num_nodes={num_nodes}"
        assert len(dem) >= num_nodes, f"demands len={len(dem)} < num_nodes={num_nodes}"
        assert len(srv) >= num_nodes, f"service_times len={len(srv)} < num_nodes={num_nodes}"
        assert len(evs) >= num_nodes, f"EV_time_savings len={len(evs)} < num_nodes={num_nodes}"

        nv = data['num_vehicles']
        assert len(data['start']) == nv, f"start len {len(data['start'])} != num_vehicles {nv}"
        assert len(data['end']) == nv,   f"end len {len(data['end'])} != num_vehicles {nv}"
        assert len(data['vehicle_types_bin']) == nv, f"vehicle_types_bin len != num_vehicles"
        assert len(data['vehicle_types_id'])  == nv, f"vehicle_types_id len != num_vehicles"

        # Capacities length: OR-Tools expects one per vehicle.
        caps = data['vehicle_capacities']
        assert len(caps) == nv, f"vehicle_capacities len {len(caps)} != num_vehicles {nv}"

        # Time window sanity
        bad_tw = [(i, tw[i]) for i in range(num_nodes) if tw[i][0] > tw[i][1]]
        if bad_tw:
            log("BAD time windows (start> end):", bad_tw)
            # This is a hard modeling error
            return None, None, None

        # -----------------------------
        # 2) Quick infeasibility hints BEFORE OR-Tools
        # -----------------------------
        depot = data['depot']
        dep_tw0, dep_tw1 = tw[depot]

        # 2a) Can any node be reached from depot within its TW (simple earliest-arrival check)?
        #     This is not sufficient for feasibility, but catches obvious impossibilities.
        impossible_from_depot = []
        for i in range(num_nodes):
            if i == depot:
                continue
            travel = dist[depot][i]
            service_depot = srv[depot]
            earliest_arrival = dep_tw0 + travel + service_depot
            latest = tw[i][1]
            if earliest_arrival > latest:
                impossible_from_depot.append((i, earliest_arrival, tw[i]))
        if impossible_from_depot:
            log("OBVIOUSLY IMPOSSIBLE nodes from depot (earliest_arrival > latest):")
            for tup in impossible_from_depot[:20]:
                log("  node", tup[0], "earliest", tup[1], "TW", tup[2])
            # Not returning, because multi-stop might still reach; but usually this is fatal.

        # since there is repitition in pd pairs in the data to support the charging location, we will remove the repitition (only first occurrence will be kept)    
        if data.get('prob_type') == 'pickup_delivery':
            # keep only first occurrences
            data['pickups_deliveries'] = list(dict.fromkeys(map(tuple, data['pickups_deliveries'])))
            # convert back to list of lists
            data['pickups_deliveries'] = [list(x) for x in data['pickups_deliveries']]
            log(f"Total P/D pairs: {len(data['pickups_deliveries'])}")

        # 2b) Pickup-delivery quick checks (if present)
        if data.get('prob_type') == 'pickup_delivery' and 'pickups_deliveries' in data:
            pd_issues = []
            for (p, d) in data['pickups_deliveries']:
                if p >= num_nodes or d >= num_nodes:
                    pd_issues.append(("PD index out of model range", (p, d)))
                    continue
                # Check TW ordering (pickup must be able to happen before delivery in time)
                if tw[p][0] > tw[d][1]:
                    pd_issues.append(("pickup earliest after delivery latest", (p, d), tw[p], tw[d]))
            if pd_issues:
                log("P/D obvious issues:")
                for x in pd_issues[:20]:
                    log(" ", x)
                # Not returning, but strongly suspect infeasible.

        # -----------------------------
        # 3) Build manager / routing
        # -----------------------------
        manager = pywrapcp.RoutingIndexManager(num_nodes, nv, data['start'], data['end'])
        routing = pywrapcp.RoutingModel(manager)
        log("Routing model created.")

        # -----------------------------
        # 4) Callbacks registration (try/except inside loop)
        # -----------------------------
        time_callback_indices = []

        for vehicle_id in range(nv):
            vbin = data['vehicle_types_bin'][vehicle_id]      # 0/1 for EV savings logic
            vid  = data['vehicle_types_id'][vehicle_id]       # 0/2/... for cost arrays

            # Guard: vid must be within cost arrays
            if vid >= len(data['cost_per_unit_time']) or vid >= len(data['fixed_cost']):
                raise IndexError(f"vehicle_types_id[{vehicle_id}]={vid} out of range for cost arrays")

            def cost_callback(from_index, to_index, vehicle=vehicle_id, vtype=vbin, vtypeid=vid):
                try:
                    from_node = manager.IndexToNode(int(from_index))
                    to_node   = manager.IndexToNode(int(to_index))
                    travel_time  = data['distance_matrix'][from_node][to_node]
                    base_service = data['service_times'][from_node]
                    ev_saving    = data['EV_time_savings'][from_node] * vtype
                    service_time = max(0, base_service - ev_saving)
                    cpu = data['cost_per_unit_time'][vtypeid]
                    return int(round((travel_time + service_time) * cpu))
                except Exception as e:
                    print("\nERROR inside cost_callback:")
                    print("  vehicle:", vehicle, "from_index:", from_index, "to_index:", to_index)
                    traceback.print_exc()
                    raise

            cost_cb_idx = routing.RegisterTransitCallback(cost_callback)
            routing.SetArcCostEvaluatorOfVehicle(cost_cb_idx, vehicle_id)
            routing.SetFixedCostOfVehicle(int(data['fixed_cost'][vid]), vehicle_id)

            def time_callback(from_index, to_index, vehicle=vehicle_id, vtype=vbin):
                try:
                    from_node = manager.IndexToNode(int(from_index))
                    to_node   = manager.IndexToNode(int(to_index))
                    travel_time  = data['distance_matrix'][from_node][to_node]
                    base_service = data['service_times'][from_node]
                    ev_saving    = data['EV_time_savings'][from_node] * vtype
                    service_time = max(0, base_service - ev_saving)
                    return int(travel_time + service_time)
                except Exception as e:
                    print("\nERROR inside time_callback:")
                    print("  vehicle:", vehicle, "from_index:", from_index, "to_index:", to_index)
                    traceback.print_exc()
                    raise

            tcb_idx = routing.RegisterTransitCallback(time_callback)
            time_callback_indices.append(tcb_idx)

        # -----------------------------
        # 5) Time dimension
        # -----------------------------
        routing.AddDimensionWithVehicleTransitAndCapacity(
            time_callback_indices,
            30,
            [86400] * nv,
            False,
            "Time"
        )
        time_dimension = routing.GetDimensionOrDie("Time")

        # -----------------------------
        # 6) Stops dimension / disjunctions (only if internal & comm != 2)
        # -----------------------------
        if index == 'internal' and (comm is not None) and comm != 2:
            # Ensure needed fields exist
            for k in ['stops', 'vehicle_slack_stops', 'vehicle_max_stops']:
                if k not in data:
                    raise KeyError(f"Missing data['{k}'] required for Stops dimension")

            def stops_callback(from_index):
                from_node = manager.IndexToNode(int(from_index))
                return int(data['stops'][from_node])

            stops_cb_idx = routing.RegisterUnaryTransitCallback(stops_callback)
            routing.AddDimensionWithVehicleCapacity(
                stops_cb_idx,
                0,
                data['vehicle_slack_stops'],
                True,
                "Stops"
            )
            stop_dimension = routing.GetDimensionOrDie("Stops")

            penalty_stop = 100000
            for v in range(nv):
                stop_dimension.SetCumulVarSoftUpperBound(
                    routing.End(v),
                    int(data['vehicle_max_stops'][v]),
                    penalty_stop
                )

            penalty_drop = 100000
           
            # So disjunctions must be within [1, num_nodes-1].
            if data.get('prob_type') != 'pickup_delivery':
                for node in range(1, num_nodes):
                    routing.AddDisjunction([manager.NodeToIndex(node)], penalty_drop)

        # -----------------------------
        # 7) Time windows
        # -----------------------------
        for location_idx, (a, b) in enumerate(tw[:num_nodes]):
            if location_idx == depot:
                continue
            idx = manager.NodeToIndex(location_idx)
            time_dimension.CumulVar(idx).SetRange(int(a), int(b))

        for vehicle_id in range(nv):
            start_idx = routing.Start(vehicle_id)
            time_dimension.CumulVar(start_idx).SetRange(int(dep_tw0), int(dep_tw1))

        # -----------------------------
        # 8) Capacity dimension
        # -----------------------------
        def demand_callback(from_index):
            from_node = manager.IndexToNode(int(from_index))
            return int(dem[from_node])

        demand_cb_idx = routing.RegisterUnaryTransitCallback(demand_callback)
        routing.AddDimensionWithVehicleCapacity(
            demand_cb_idx,
            0,
            [int(c) for c in caps],
            True,
            "Capacity"
        )

        # -----------------------------
        # 9) Pickup & delivery
        # -----------------------------
        if data.get('prob_type') == 'pickup_delivery' and 'pickups_deliveries' in data:
            for (p, d) in data['pickups_deliveries']:
                if p >= num_nodes or d >= num_nodes:
                    raise IndexError(f"Pickup/delivery node ({p},{d}) outside model num_nodes={num_nodes}")

                p_idx = manager.NodeToIndex(p)
                d_idx = manager.NodeToIndex(d)

                routing.AddPickupAndDelivery(p_idx, d_idx)
                routing.solver().Add(routing.VehicleVar(p_idx) == routing.VehicleVar(d_idx))
                routing.solver().Add(time_dimension.CumulVar(p_idx) <= time_dimension.CumulVar(d_idx))

        # -----------------------------
        # 10) Search parameters
        # -----------------------------
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION
        # search_parameters.local_search_metaheuristic = (routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
        # search_parameters.time_limit.seconds = 15 * num_customers


        # -----------------------------
        # 11) Solve + report status
        # -----------------------------
        solution = routing.SolveWithParameters(search_parameters)
        # log("solution:", solution)

        if solution:
            return manager, routing, solution

        # If no solution, print status + some useful hints
        st = routing.status()
        status_map = {
            0: "ROUTING_NOT_SOLVED",
            1: "ROUTING_SUCCESS",
            2: "ROUTING_FAIL",
            3: "ROUTING_FAIL_TIMEOUT",
            4: "ROUTING_INVALID",
        }
        log(f"No solution. routing.status()={st} ({status_map.get(st,'UNKNOWN')})")

        # Common additional hints:
        log("Hints to check next:")
        log(" - Are any pickups/deliveries outside [0..num_nodes-1]?")
        log(" - Do any nodes have TW so tight they can't be inserted with travel+service?")
        log(" - Any negative transit time? (should be avoided; here we clamp service >=0)")
        log(" - Are vehicle_capacities reasonable vs max cumulative pickup load?")

        return None, None, None

    except Exception as e:
        print("\nEXCEPTION while building/solving VRP:")
        traceback.print_exc()
        return None, None, None

