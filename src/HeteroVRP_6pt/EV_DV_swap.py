from hetero_ini_vrp_b import solve_initial_vrp, cal_total_cost

def get_ch_st_IDS(EV_routes, data):
    CS_IDS = set()
    for route in EV_routes:
        CS_IDS.update(set(route) & set(data['charging_stations']))
    return CS_IDS


def remove_cs(route, cs_ids):
    """Return a copy of route without charging-station nodes (keep depot)."""
    return [n for n in route if (n == 0 or n not in cs_ids)]

def swap_veh_type_EtoD(EV_routes, data, CS_IDS, selected_pt, selected_pt_ice):
    summary = []
    for idx, r in enumerate(EV_routes):
        # Cost as EV (with CS nodes included)
        ev_cost = cal_total_cost([r], data, selected_pt)

        # Convert to diesel: drop CS nodes
        ice_r = remove_cs(r, CS_IDS)

        # Cost as ICE (no battery/CS constraints)
        ice_cost = cal_total_cost([ice_r], data, selected_pt_ice)

        delta = ice_cost - ev_cost  # negative means diesel is cheaper
        summary.append({
            "route_idx": idx,
            "ev_route": r,
            "ice_route": ice_r,
            "ev_cost": ev_cost,
            "ice_cost": ice_cost,
            "delta_cost": delta
        })

    # Decide which to convert (independent, so convert all with negative deltas)
    to_convert = [s for s in summary if s["delta_cost"] < 0]

    # print("Per-route comparison (ICE - EV):")
    # for s in summary:
    #     print(f"Route {s['route_idx']}: EV={s['ev_cost']:.2f}, ICE={s['ice_cost']:.2f}, Δ={s['delta_cost']:.2f}")

    if to_convert:
        print("\nRecommended conversions (cheaper as diesel):", [s["route_idx"] for s in to_convert])
    else:
        print("\nNo route becomes cheaper by converting to diesel.")

    # Build the best overall plan (convert all with negative Δ)
    best_plan = []
    for s in summary:
        best_plan.append(s["ice_route"] if s["delta_cost"] < 0 else s["ev_route"])

    best_total_cost = (
        cal_total_cost([best_plan[i] for i,s in enumerate(summary) if s["delta_cost"] < 0], data, veh_type=0)
        + cal_total_cost([best_plan[i] for i,s in enumerate(summary) if s["delta_cost"] >= 0], data, veh_type=1)
    )

    current_total_cost = cal_total_cost(EV_routes, data, veh_type=1)

    # print(f"\nCurrent total EV cost = {current_total_cost:.2f}")
    # print(f"Best mixed plan total  = {best_total_cost:.2f}")
    # print("Best plan routes:")
    best_plan_dict = {}
    for i, r in enumerate(best_plan):
        tag = "ICE" if summary[i]["delta_cost"] < 0 else "EV"
        best_plan_dict[i] = {"route_idx": i, "route": r, "tag": tag}
        # print(f"  Route {i} ({tag}): {r}")
    
    return best_plan, best_total_cost, best_plan_dict


def swap_veh_type_DtoE(ICE_routes, data):
    summary = []
    for idx, r in enumerate(ICE_routes):
        # Cost as EV (with CS nodes included)
        ev_cost = cal_total_cost([r], data, veh_type=1)
        # print("ev_cost:", ev_cost)

        # Cost as ICE (no battery/CS constraints)
        ice_cost = cal_total_cost([r], data, veh_type=0)
        # print("ice_cost:", ice_cost)

        delta = ev_cost - ice_cost  # negative means ev is cheaper
        summary.append({
            "route_idx": idx,
            "route": r,
      
            "ev_cost": ev_cost,
            "ice_cost": ice_cost,
            "delta_cost": delta
        })

    # Decide which to convert (independent, so convert all with negative deltas)
    to_convert = [s for s in summary if s["delta_cost"] < 0]
    # print("to_convert:", to_convert)

    # print("Per-route comparison (ICE - EV):")
    # for s in summary:
    #     print(f"Route {s['route_idx']}: EV={s['ev_cost']:.2f}, ICE={s['ice_cost']:.2f}, Δ={s['delta_cost']:.2f}")

    if to_convert:
        print("\nRecommended conversions (cheaper as EV):", [s["route_idx"] for s in to_convert])
    else:
        print("\nNo route becomes cheaper by converting to EV.")

    # Build the best overall plan (convert all with negative Δ)
    best_plan = []
    for s in summary:
        best_plan.append(s["route"] if s["delta_cost"] < 0 else s["route"])

    # print("delta:", s)

    best_total_cost = (
        cal_total_cost([best_plan[i] for i,s in enumerate(summary) if s["delta_cost"] < 0], data, veh_type=1)
        + cal_total_cost([best_plan[i] for i,s in enumerate(summary) if s["delta_cost"] >= 0], data, veh_type=0)
    )

    current_total_cost = cal_total_cost(ICE_routes, data, veh_type=0)
    # print("current_total_cost:", current_total_cost)

    # print(f"\nCurrent total ICE cost = {current_total_cost:.2f}")
    # print(f"Best mixed plan total  = {best_total_cost:.2f}")
    # print("Best plan routes:")
    best_plan_dict = {}
    for i, r in enumerate(best_plan):
        tag = "EV" if summary[i]["delta_cost"] < 0 else "ICE"
        best_plan_dict[i] = {"route_idx": i, "route": r, "tag": tag}
        # print(f"  Route {i} ({tag}): {r}")
    
    return best_plan, best_total_cost, best_plan_dict