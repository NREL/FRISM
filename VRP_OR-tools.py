import pandas as pd
import geopandas as gp
import numpy as np
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
from copy import copy
import os
import inspect
from xml.dom import minidom
import math
import networkx as nx
from networkx import DiGraph
from vrpy import VehicleRoutingProblem
import matplotlib.pyplot as plt
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from time import time
import numpy as np
from argparse import ArgumentParser



# Global Variables
tour_id = 0
payload_i = 0



# Function to get travel time using mesozone ID refering CBGID in tt_df
def tt_cal(org_meso, dest_meso, org_geoID, dest_geoID, sel_tt, sel_dist):
    #Added sel_tt_df for selected tt_df data frame and sel_dist_df for selected dist_df
    travel_time = -1
    try:
        travel_time = sel_tt['TIME_minutes'].to_numpy()[(sel_tt['origin'].to_numpy() == org_geoID)
                                              &(sel_tt['destination'].to_numpy() == dest_geoID)].item()
    except:
        try:
            dist = sel_dist['dist'].to_numpy()[(sel_dist['Origin'].to_numpy() == org_meso)
                                              &(sel_dist['Destination'].to_numpy() == dest_meso)].item()
            travel_time= dist/40*60
        except:
            travel_time = 60*3
    return travel_time

# Function to create coorinate info after having the results
def x_y_finder(meso):
    try:
        find_index=CBGzone_df.index[CBGzone_df['MESOZONE']==meso]
        x_cord= CBGzone_df.iloc[find_index].X_cord.values[0]
        y_cord= CBGzone_df.iloc[find_index].Y_cord.values[0]
        return x_cord, y_cord
    except:
        return "NA", "NA"


def get_geoId(zone, CBGzone_df):
    try:
        org_geoID= int(CBGzone_df[CBGzone_df['MESOZONE']==zone].GEOID.values[0])
    except:
        org_geoID = -1
    return int(org_geoID)


# Receives a data frame for a problem for a particular carrier id
# To account for service time, we add service time of destination to regular travel time
def create_data_model(df_prob, depot_loc, prob_type, v_df, f_prob, c_prob, carrier_id,
                     md_start_id, hd_start_id, CBGzone_df, tt_df, dist_df):
    """Stores the data for the problem."""
    data = {}
    data['time_matrix'] = []
    data['loc_zones'] = []    # zones corresponding to locations
    data['payload_ids'] = []
    data['stop_durations'] = []

    if prob_type == 'pickup_delivery':
        data['pickups_deliveries']=[]

    time_l = []
    # Adding time 0 for the depot and location for depot
    time_l.append(0)
    data['loc_zones'].append(depot_loc)
    depot_service_time = float(c_prob.loc[c_prob['carrier_id'] == carrier_id]['depot_time_before'].values[0])
    data['stop_durations'].append(depot_service_time)

    data['time_windows'] = []
    # Add time window for depot
    data['time_windows'].append((int(c_prob.loc[c_prob['carrier_id'] == carrier_id]['depot_lower'].values[0]),
                                int(c_prob.loc[c_prob['carrier_id'] == carrier_id]['depot_upper'].values[0])))
    data['demands'] = []
    data['demands'].append(0.0) # Adding demand for depot

    data['geo_ids'] = []
    data['geo_ids'].append(get_geoId(depot_loc, CBGzone_df))

    index = 1
    for i in df_prob['payload_id'].unique():
        if prob_type == 'delivery':
            temp_zone = (int(df_prob.loc[df_prob['payload_id'] == i]['del_zone'].values[0])) # find zone
            data['loc_zones'].append(copy(temp_zone))     # saving zone
            data['geo_ids'].append(get_geoId(temp_zone, CBGzone_df))

            # Adding time window
            data['time_windows'].append((int(df_prob.loc[df_prob['payload_id'] == i]['del_tw_lower'].values[0]),
                                int(df_prob.loc[df_prob['payload_id'] == i]['del_tw_upper'].values[0])))

            data['payload_ids'].append(copy(i))

            demand = math.ceil(df_prob.loc[df_prob['payload_id'] == i]['weight'].values[0])
            data['demands'].append(copy(demand))

            service_time = float(df_prob.loc[df_prob['payload_id'] == i]['del_stop_duration'].values[0])
            data['stop_durations'].append(copy(service_time))


        elif prob_type =='pickup':
            temp_zone = int(df_prob.loc[df_prob['payload_id'] == i]['pu_zone'].values[0]) # find zone
            data['loc_zones'].append(copy(temp_zone))   # saving zone
            data['geo_ids'].append(get_geoId(temp_zone, CBGzone_df))

            # Adding time window
            data['time_windows'].append((int(df_prob.loc[df_prob['payload_id'] == i]['pu_tw_lower'].values[0]),
                                int(df_prob.loc[df_prob['payload_id'] == i]['pu_tw_upper'].values[0])))

            data['payload_ids'].append(copy(i))

            demand = math.ceil(df_prob.loc[df_prob['payload_id'] == i]['weight'].values[0])
            data['demands'].append(copy(demand))

            service_time = float(df_prob.loc[df_prob['payload_id'] == i]['pu_stop_duration'].values[0])
            data['stop_durations'].append(copy(service_time))

        elif prob_type == 'pickup_delivery':
            temp_zone_d = int(df_prob.loc[df_prob['payload_id'] == i]['del_zone'].values[0]) # find delivery zone
            temp_zone_p = int(df_prob.loc[df_prob['payload_id'] == i]['pu_zone'].values[0]) # find pickup zone
            # Adding pickup and delivery zone to data frame
            data['loc_zones'].append(copy(temp_zone_p))
            data['loc_zones'].append(copy(temp_zone_d))
            data['geo_ids'].append(get_geoId(temp_zone_p, CBGzone_df))
            data['geo_ids'].append(get_geoId(temp_zone_d, CBGzone_df))

            # Adding time pickup and delivery windows
            data['time_windows'].append((int(df_prob.loc[df_prob['payload_id'] == i]['pu_tw_lower'].values[0]),
                                int(df_prob.loc[df_prob['payload_id'] == i]['pu_tw_upper'].values[0])))
            data['time_windows'].append((int(df_prob.loc[df_prob['payload_id'] == i]['del_tw_lower'].values[0]),
                                int(df_prob.loc[df_prob['payload_id'] == i]['del_tw_upper'].values[0])))


            data['payload_ids'].append(copy(i))
            data['payload_ids'].append(copy(i))

            demand = math.ceil(df_prob.loc[df_prob['payload_id'] == i]['weight'].values[0])
            data['demands'].append(copy(demand))
            data['demands'].append(copy(0))

            # Add pickup service time and delivery service time
            service_time = float(df_prob.loc[df_prob['payload_id'] == i]['pu_stop_duration'].values[0])
            data['stop_durations'].append(copy(service_time))
            service_time = float(df_prob.loc[df_prob['payload_id'] == i]['del_stop_duration'].values[0])
            data['stop_durations'].append(copy(service_time))

            # Assuming that if a carrier has pickup_delivery jobs it only has that
            data['pickups_deliveries'].append([index, index+1])
            index += 2

    # Adding travel time for rest of locations
    print("Beginning to get time matrix")

    b_timing = time()
    sel_tt= tt_df[(tt_df['origin'].isin(data['geo_ids'])) &
                     (tt_df['destination'].isin(data['geo_ids']))]
    sel_dist = dist_df[(dist_df['Origin'].isin(data['loc_zones'])) &
                       (dist_df['Destination'].isin(data['loc_zones']))]
    print('len of tt ', len(sel_tt), ' len of dist ', len(sel_dist))

    for i in range(len(data['loc_zones'])):
        time_l = []
        travel_time = 0

        for j in range(len(data['loc_zones'])):
            if i == j or data['loc_zones'][i] == data['loc_zones'][j]:
                time_l.append(0)
            else:
                travel_time = tt_cal(data['loc_zones'][i], data['loc_zones'][j],
                                     data['geo_ids'][i], data['geo_ids'][j], sel_tt, sel_dist)
                time_l.append(int(travel_time))

        data['time_matrix'].append(copy(time_l))

    print("calculating matrix time, ", time()-b_timing)

    # We assume first value in graph is medium duty and second is duty
    veh_capacity = [int(v_df[v_df['veh_category'] == 'MD']['payload_capacity_weight'].values[0]),
                    int(v_df[v_df['veh_category'] == 'HD']['payload_capacity_weight'].values[0])]

    # Adding vehicle capacities
    data['vehicle_capacities'] = []
    data['vehicle_ids'] = []
    data['vehicle_types'] = []
    md_veh_id = md_start_id
    hd_veh_id = hd_start_id

    # Adding medium duty capacities
    for i in range(0,f_prob['md_veh'].values[0]):
        data['vehicle_capacities'].append(int(v_df[v_df['veh_category'] == 'MD']['payload_capacity_weight'].values[0]))
        data['vehicle_ids'].append(md_veh_id)
        data['vehicle_types'].append(1)  # 1 represent medium duty
        md_veh_id += 1
    # Adding heavy duty capacities
    for i in range(0,f_prob['hd_veh'].values[0]):
        data['vehicle_capacities'].append(int(v_df[v_df['veh_category'] == 'HD']['payload_capacity_weight'].values[0]))
        data['vehicle_ids'].append(hd_veh_id)
        data['vehicle_types'].append(2)   # 2 represent heavy duty
        hd_veh_id += 1

    data['num_vehicles'] = int(f_prob['md_veh'].values[0] + f_prob['hd_veh'].values[0])
    print("veh_capacity: ", veh_capacity, " num_veh: ", data['num_vehicles'])
    data['depot'] = 0
    return data


def print_solution(data, manager, routing, solution, tour_df, carr_id, carrier_df, payload_df):
    """Prints solution on console."""
    global tour_id
    global payload_i
    print(f'Objective: {solution.ObjectiveValue()}')
    time_dimension = routing.GetDimensionOrDie('Time')
    total_time = 0
    route_load = 0
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        start_loc = manager.IndexToNode(index)
        next_loc = manager.IndexToNode(solution.Value(routing.NextVar(index)))

        # Print out solution from vehicles that left the dept
        if start_loc != next_loc:
            start_time = solution.Min(time_dimension.CumulVar(index))

            # Adding tour, carrier info to csv
            # Format for tour csv: ['tour_id', 'departureTimeInSec', 'departureLocation_zone', 'maxTourDurationInSec']
            # Fomat for carrier csv: ['carrierId','tourId', 'vehicleId', 'vehicleTypeId','depot_zone']
            tour_df.loc[tour_id] = [tour_id, start_time*60, data['loc_zones'][manager.IndexToNode(index)], 3600]
            carrier_df.loc[tour_id] = [carr_id, tour_id, data['vehicle_ids'][vehicle_id],
                                       data['vehicle_types'][vehicle_id], data['loc_zones'][manager.IndexToNode(index)]]

            plan_output = 'Route for vehicle {0} with id {1}:\n'.format(vehicle_id, data['vehicle_ids'][vehicle_id])
            plan_output_l = 'Load for vehicle {}:\n'.format(vehicle_id)
            seqId = 1
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                time_var = time_dimension.CumulVar(index)
                plan_output += '{0} Time({1},{2}) -> '.format(
                    manager.IndexToNode(index), solution.Min(time_var),
                    solution.Max(time_var))

                if(node_index != 0): # Only add the payload info if this is not the depot
                    payload_df.loc[payload_i] = [int(data['payload_ids'][node_index-1]), int(seqId), int(tour_id), int(1),
                                                 data['demands'][node_index], 1, int(data['loc_zones'][node_index]),
                                                int((solution.Min(time_var)-data['stop_durations'][node_index])*60),
                                                 int(data['time_windows'][node_index][0]*60),
                                                int(data['time_windows'][node_index][1]*60),
                                                 int(data['stop_durations'][node_index]*60)]
                    payload_i += 1
                    seqId += 1

                # Load info
                route_load += data['demands'][node_index]
                plan_output_l += ' {0} Load({1}) -> '.format(node_index, route_load)
                previous_index = index
                index = solution.Value(routing.NextVar(index))

            time_var = time_dimension.CumulVar(index)
            plan_output += '{0} Time({1},{2})\n'.format(manager.IndexToNode(index),
                                                        solution.Min(time_var),
                                                        solution.Max(time_var))
            plan_output_l += ' {0} Load({1})'.format(manager.IndexToNode(index),
                                                 route_load)
            plan_output += 'Time of the route: {}min'.format(
                solution.Min(time_var) - start_time)
            print(plan_output)
            print(plan_output_l)
            total_time += solution.Min(time_var)- start_time
            tour_id += 1 # Incrementing for the tour id
    print('Total time of all routes: {}min'.format(total_time))

def input_files_processing(travel_file, dist_file, CBGzone_file, carrier_file, payload_file, vehicleType_file,
                         vehicleCarrier_file):
    # KJ: read travel time, distance, zonal file as inputs  # Slow step
    tt_df = pd.read_csv(travel_file, compression='gzip', header=0, sep=',', quotechar='"', error_bad_lines=False)
    dist_df = pd.read_csv(dist_file)  # Slow step
    CBGzone_df = gp.read_file(CBGzone_file)

    # We need to know the depot using the carrier file
    c_df = pd.read_csv(carrier_file)
    c_df = c_df.dropna(axis=1, how='all')   # Removing all nan

    # reading payload definition
    p_df = pd.read_csv(payload_file)
    p_df = p_df.dropna(axis=1, how='all')   # Removing all nan

    # just relax upper time window because of outside of region destination
    #c_df['depot_upper']=50000
    #p_df['del_tw_upper']=50000
    # Removing nans
    c_df = c_df.fillna(0); # Fill all nan with zeros

    # Removing nans
    p_df['carrier_id'] = p_df['carrier_id'].astype(int)
    p_df['sequence_id'] = np.nan
    p_df['tour_id'] = np.nan
    p_df['pu_arrival_time'] = np.nan
    p_df['del_arrival_time'] = np.nan
    p_df = p_df.fillna(int(0));

    # Adding in additional colums for vehicle tours
    # Changing tour id and sequence id into ints
    p_df['tour_id'] = p_df['tour_id'].astype(int)
    p_df['sequence_id'] = p_df['sequence_id'].astype(int)

    # Reading in vehicle information
    v_df = pd.read_csv(vehicleType_file)
    v_df = v_df.dropna(axis=1, how='all')   # Removing all nan

    # Create vehicle sequence vehicle ID
    vc_df = c_df[['carrier_id', 'num_veh_type_1','num_veh_type_2']]
    vc_df.columns= ['carrier_id', 'md_veh', 'hd_veh']
    vc_df['md_start_id']=0
    vc_df['hd_start_id']=0

    n=0
    for i in range (0, vc_df.shape[0]):
        vc_df['md_start_id'][i] =  n
        vc_df['hd_start_id'][i] =  n+vc_df['md_veh'][i]
        n=vc_df['hd_start_id'][i]+vc_df['hd_veh'][i]

    # Reading vehicles by carrier
    vc_df = pd.read_csv(vehicleCarrier_file)

    return tt_df, dist_df, CBGzone_df, c_df, p_df, v_df, vc_df


def main(args=None):
    parser = ArgumentParser()
    parser.add_argument("-t", "--travel_time_file", dest="travel_file",
                        help="travel time file in gz format", required=True, type=str)
    parser.add_argument("-d", "--distance_file", dest="dist_file",
                        help="distance file in csv format", required=True, type=str)
    parser.add_argument("-ct", "--freigh_centroid_file", dest="CBGzone_file",
                        help="travel time file in geojson format", required=True, type=str)
    parser.add_argument("-cr", "--carrier_file", dest="carrier_file",
                        help="carrier file in csv format", required=True, type=str)
    parser.add_argument("-pl", "--payload_file", dest="payload_file",
                        help="payload file in csv format", required=True, type=str)
    parser.add_argument("-vt", "--vehicle_type_file", dest="vehicleType_file",
                        help="vehicle type file in csv format", required=True, type=str)
    parser.add_argument("-vc", "--vehicle_by_carrier_file", dest="vehicleCarrier_file",
                        help="vehicle by carrier file in csv format", required=True, type=str)

    args = parser.parse_args()


    tt_df, dist_df, CBGzone_df, c_df, p_df, v_df, vc_df = input_files_processing(args.travel_file, args.dist_file,
                                                    args.CBGzone_file, args.carrier_file, args.payload_file,
                                                    args.vehicleType_file, args.vehicleCarrier_file)

    b_time = time()
    # data frames for the tour, carrier and payload
    tour_df = pd.DataFrame(columns = ['tour_id', 'departureTimeInSec', 'departureLocation_zone', 'maxTourDurationInSec'])
    # Format for carrier data frame: carrierId,tourId, vehicleId,vehicleTypeId,depot_zone
    carrier_df = pd.DataFrame(columns = ['carrierId','tourId', 'vehicleId', 'vehicleTypeId','depot_zone'])
    # format for payload format
    # payloadId, sequenceRank, tourId, payloadType, weightInlb, requestType,locationZone,
    # estimatedTimeOfArrivalInSec, arrivalTimeWindowInSec_lower, arrivalTimeWindowInSec_upper,operationDurationInSec
    payload_df = pd.DataFrame(columns = ['payloadId','sequenceRank','tourId','payloadType','weightInlb','requestType',
                                         'locationZone','estimatedTimeOfArrivalInSec','arrivalTimeWindowInSec_lower',
                                         'arrivalTimeWindowInSec_upper','operationDurationInSec'])


    for carr_id in c_df['carrier_id'].unique():
        # Initialize parameters used for probelm setting
        veh_capacity = 0
        fleet_type = 'homo'
        num_veh = 0
        fleet_miz = False

        # Depot location
        depot_loc = c_df.loc[c_df['carrier_id'] == carr_id]['depot_zone'].values[0]

        # To simplify the problem, look at a small problem with same carrier and same commodity id
        df_prob = p_df[(p_df['carrier_id'] == carr_id)]
        f_prob = vc_df[vc_df['carrier_id'] == carr_id]
        c_prob = c_df[c_df['carrier_id'] == carr_id]
        vc_prob = vc_df[vc_df['carrier_id']== carr_id]

        if len(vc_prob) > 0:
            md_start_id = int(vc_prob['md_start_id'].values[0])
            hd_start_id = int(vc_prob['hd_start_id'].values[0])
            #print(df_prob)

        if len(df_prob) > 0:
            prob_type = str(df_prob.iloc[0]['job'])
            print('problem type is: ', prob_type, " len main ", len(df_prob), " len freight ", len(f_prob)
                 , " len carrier ", len(c_prob), " len vc ", len(vc_prob))

        # for now pickup and delivery works
        # TO DO: work on pickup_delivery  # Removed prob_type != 'pickup_delivery'and
        if len(df_prob)> 0 and len(f_prob)> 0 and len(c_prob)> 0 and len(vc_prob)>0:
            print('carr_id is ', carr_id)
            data = create_data_model(df_prob, depot_loc, prob_type, v_df, f_prob, c_prob, carr_id,
                                    md_start_id, hd_start_id, CBGzone_df, tt_df, dist_df)

            # Create the routing index manager.
            manager = pywrapcp.RoutingIndexManager(len(data['time_matrix']),
                                                   data['num_vehicles'], data['depot'])

            # Create Routing Model.
            routing = pywrapcp.RoutingModel(manager)

            # Create and register a transit callback.
            def time_callback(from_index, to_index):
                """Returns the travel time between the two nodes."""
                # Convert from routing variable Index to time matrix NodeIndex.
                from_node = manager.IndexToNode(from_index)
                to_node = manager.IndexToNode(to_index)
                return data['time_matrix'][from_node][to_node] + data['stop_durations'][to_node]

            # Add Capacity constraint.
            def demand_callback(from_index):
                """Returns the demand of the node."""
                # Convert from routing variable Index to demands NodeIndex.
                from_node = manager.IndexToNode(from_index)
                return data['demands'][from_node]

            transit_callback_index = routing.RegisterTransitCallback(time_callback)

            # Define cost of each arc.
            routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

            # Add Time Windows constraint.
            time_dim = 'Time'
            routing.AddDimension(
                transit_callback_index,
                30,  # allow waiting time
                86400,  # maximum time per vehicle, JU: set to minutes in a day assuming no trip goes beyod a day
                False,  # Don't force start cumul to zero.
                time_dim)
            time_dimension = routing.GetDimensionOrDie(time_dim)

            # Add time window constraints for each location except depot.
            for location_idx, time_window in enumerate(data['time_windows']):
                if location_idx == data['depot']:
                    continue
                index = manager.NodeToIndex(location_idx)
                time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])

            # Add time window constraints for each vehicle start node.
            depot_idx = data['depot']
            for vehicle_id in range(data['num_vehicles']):
                index = routing.Start(vehicle_id)
                time_dimension.CumulVar(index).SetRange(
                    data['time_windows'][depot_idx][0],
                    data['time_windows'][depot_idx][1])

            if prob_type == 'pickup_delivery':
                # Define Transportation Requests.
                for request in data['pickups_deliveries']:
                    pickup_index = manager.NodeToIndex(request[0])
                    delivery_index = manager.NodeToIndex(request[1])
                    routing.AddPickupAndDelivery(pickup_index, delivery_index)
                    routing.solver().Add(
                        routing.VehicleVar(pickup_index) == routing.VehicleVar(
                            delivery_index))
                    routing.solver().Add(
                        time_dimension.CumulVar(pickup_index) <=
                        time_dimension.CumulVar(delivery_index))

            demand_callback_index = routing.RegisterUnaryTransitCallback(
                    demand_callback)
            routing.AddDimensionWithVehicleCapacity(
                demand_callback_index,
                0,  # null capacity slack
                data['vehicle_capacities'],  # vehicle maximum capacities
                True,  # start cumul to zero
                'Capacity')

            # Instantiate route start and end times to produce feasible times.
            for i in range(data['num_vehicles']):
                routing.AddVariableMinimizedByFinalizer(
                    time_dimension.CumulVar(routing.Start(i)))
                routing.AddVariableMinimizedByFinalizer(
                    time_dimension.CumulVar(routing.End(i)))

            # Setting first solution heuristic.
            search_parameters = pywrapcp.DefaultRoutingSearchParameters()
            search_parameters.time_limit.seconds = 2   #set a time limit of 2 seconds for a search
            search_parameters.solution_limit = 10     #set a solution limit of 10 for a search

            s_time = time()
            search_parameters.first_solution_strategy = (
                routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

            # Solve the problem.
            solution = routing.SolveWithParameters(search_parameters)

            solve_time = time() - s_time
            print('Time to solve is: ', solve_time)

            # Print solution on console.
            if solution:
                print_solution(data, manager, routing, solution, tour_df, carr_id, carrier_df,
                               payload_df)
                print('\n')


    run_time = time() - b_time
    print('Time for the run: ', run_time)
    print('\n')

    # Saving the created data frames
    tour_df.to_csv("output/freight_tours.csv", index=False)
    carrier_df.to_csv("output/carrier.csv", index=False)
    payload_df.to_csv("output/payload.csv", index=False)




if __name__ == "__main__":
    main()
