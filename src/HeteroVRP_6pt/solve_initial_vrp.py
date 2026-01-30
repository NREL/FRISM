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
        # -----------------------------



        def earliest_from_depot(node: int) -> int:
            """Earliest possible arrival time at `node` if we depart depot at dep_tw0."""
            return int(dep_tw0 + srv[depot] + dist[depot][node])

        # 2a) Per-node "obvious unreachable from depot" (still useful, but only a necessary condition)
        impossible_nodes = []
        for node in range(num_nodes):
            if node == depot:
                continue
            ea = earliest_from_depot(node)
            if ea > tw[node][1]:
                impossible_nodes.append((node, ea, tw[node]))

        if impossible_nodes:
            log("OBVIOUSLY UNREACHABLE nodes from depot (earliest direct arrival > node latest TW):")
            for node, ea, twn in impossible_nodes[:20]:
                log(f"  node={node}, earliest={ea}, TW={twn}")
        else:
            log("No node is obviously unreachable from depot by direct earliest-arrival check (necessary, not sufficient).")

        # 2b) Pickup-delivery pair feasibility checks (much more relevant than depot-only)
        if data.get('prob_type') == 'pickup_delivery' and 'pickups_deliveries' in data:
            pd_fatal = []
            pd_warn  = []
            seen = set()

            for (p, d) in data['pickups_deliveries']:
                if (p, d) in seen:
                    continue
                seen.add((p, d))

                if p >= num_nodes or d >= num_nodes:
                    pd_fatal.append(("PD index out of modeled range", (p, d), num_nodes))
                    continue

                # Must have pickup before delivery in time (OR-Tools adds precedence constraint later)
                # Quick necessary condition: pickup earliest TW must be <= delivery latest TW
                if tw[p][0] > tw[d][1]:
                    pd_fatal.append(("pickup earliest > delivery latest (TW order impossible)", (p, d), tw[p], tw[d]))
                    continue

                # Earliest feasible service time at pickup, assuming we drive depot->pickup
                # (This is a conservative "best-case" route start for that pair.)
                t_arr_p = earliest_from_depot(p)
                t_serv_p = max(tw[p][0], t_arr_p)            # wait until pickup opens if early
                t_done_p = t_serv_p + srv[p]                  # finish service at pickup

                # Earliest possible arrival at delivery after pickup
                t_arr_d = t_done_p + dist[p][d]
                t_serv_d = max(tw[d][0], t_arr_d)

                # If even this best-case violates delivery latest, pair is impossible
                if t_serv_d > tw[d][1]:
                    pd_fatal.append((
                        "cannot reach delivery in time even with direct depot->pickup->delivery",
                        (p, d),
                        {"depot_tw": (dep_tw0, dep_tw1), "pickup_tw": tw[p], "deliv_tw": tw[d]},
                        {"earliest_pick_arr": t_arr_p, "pick_start": t_serv_p, "pick_done": t_done_p,
                        "earliest_deliv_arr": t_arr_d, "deliv_start": t_serv_d}
                    ))

                # Capacity sanity: with standard PD convention, pickup demand positive, delivery demand negative
                # A necessary check: max load after pickup should not exceed max vehicle capacity
                if dem[p] > 0:
                    max_cap = max(data['vehicle_capacities']) if 'vehicle_capacities' in data else None
                    if max_cap is not None and dem[p] > max_cap:
                        pd_fatal.append(("pickup demand exceeds vehicle capacity", (p, d), dem[p], max_cap))
                # Warn if pickup and delivery are not opposite signs (common data bug)
                if dem[p] + dem[d] != 0:
                    pd_warn.append(("pickup+delivery demands do not sum to 0", (p, d), dem[p], dem[d]))

            if pd_fatal:
                log("\nP/D FATAL precheck issues (these pairs are effectively infeasible):")
                for item in pd_fatal[:20]:
                    log(" ", item)

            if pd_warn:
                log("\nP/D WARNINGS (may be okay, but often indicates data issues):")
                for item in pd_warn[:20]:
                    log(" ", item)
            else:
                log("No pickup-delivery pair issues found in prechecks.")


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
                # print("hi from cost_callback")
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
                print("hi from time_callback")
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
        print("time_dimension:", time_dimension)

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
            # print("hi from demand_callback")
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
        search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC

        # Optional: enable some logging (can be noisy)
        # search_parameters.log_search = True

        # -----------------------------
        # 11) Solve + report status
        # -----------------------------
        print("Starting solver...")
        solution = routing.SolveWithParameters(search_parameters)
        log("solution:", solution)

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

