# Authors: Juliette Ugirumurera and Kyungsoo Jeong

"""Run to generate vehicles' tour plans considering timing and load constraints.

"""
import pandas as pd
import geopandas as gp
import csv
import numpy as np
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
from copy import copy
import os
import inspect
from xml.dom import minidom
import math
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from time import time
import numpy as np
from argparse import ArgumentParser
from shapely.geometry import Point
import random
import config
import pickle
import h5py

# Global Variables
tour_id = 0
payload_i = 0
depot_i = 0
def tt_cal(org_taz, dest_taz, sel_tt, sel_dist):
    """Retreives the travel time between an origin and destination.

    Retrieves travel time between origin and destination geo ids (geo ids are census block group ids); 
    if we can't get travel time with geo ids, the travel time is calculated from
    the distance between the origin and destination mesozones (mesozones are assigned by synthfirm module).

    Args:
        org_meso: origin mesozone id
        dest_meso: destination mesozone id
        org_geoID: origin geo id
        dest_geoId: dest geo id
        sel_tt: subset of origin-destination travel time dataframe containing data for org_geoID and dest_geoID
        sei_dist: subset of origin-destination distance dataframe contaning data org_meso and dest_meso

    Returns:
        travel_time: travel time between the origin and destination
    """
    travel_time = -1
    try:
        # print('org_geo: ', org_geoID, ' dest geo: ', dest_geoID)
        travel_time = sel_tt['TIME_minutes'].to_numpy()[(sel_tt['origin'].to_numpy() == org_taz)
                                              &(sel_tt['destination'].to_numpy() == dest_taz)].item()
    except:
        try:
            dist = sel_dist['dist'].to_numpy()[(sel_dist['Origin'].to_numpy() == org_taz)
                                              &(sel_dist['Destination'].to_numpy() == dest_taz)].item()
            travel_time= dist/40*60
        except:
            travel_time = 60*3
    return travel_time

def create_data_model(df_prob, depot_loc, prob_type, v_df, f_prob, c_prob, carrier_id,
                      tt_df, dist_df, veh, commodity, ship_index, path_stops):
    """Create the data model for the vehicle routing problem.

    Args:
        df_prob: payload information for the vehicle routing problem
        depot_loc: mesozone id of depot location for the problem
        prob_type: problem type(Pickup, Delivery, or Pickup and Delivery)
        v_df: dataframe with vehicle types infomation (vehicle capacity, vehicle technology: diezel or gasoline,..)
        f_prob: dataframe with individual vehicle information (vehicle id, vehicle capacity, ...)
        c_prob: carrier information dataframe
        carrier_id: carrier id
        CBGzone_df: dataframe that maps geo ids to mesozones
        tt_df: orgin-destination travel time dataframe
        dist_df: origin-destination distance dataframe
        veh: vehicle type
        commodity: commodity id of shipment to be carried
        ship_index: integer that indicates if the shipments inside the region or has a 
                    destination external to the region

    Returns:
        data: returns a dictionary with with all data necessary to formulate and solve a vehile routing
        problem using ortools library.
    """

    random.seed(10) # seeding the random generator to ensre consistent results for testing purposes

    try:
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
        if commodity != 2 and ship_index =='internal':
            data['stops'] = []  # parameter to keep track of number of stops per node
            data['stops'].append(0.0) # No stop counted for depot

            data['vehicle_max_stops'] = []
            data['vehicle_slack_stops'] = []

        # if problem is delivery, we start with full laod at depot
        # if problem is pickup, we start with empty load
        data['demands'].append(0.0) # Adding demand for depot

        # data['geo_ids'] = []
        # data['geo_ids'].append(get_geoId(depot_loc, CBGzone_df))

        index = 1
        for i in df_prob['payload_id'].unique():
            if prob_type == 'delivery':
                temp_zone = (int(df_prob.loc[df_prob['payload_id'] == i]['del_zone'].values[0])) # find zone
                data['loc_zones'].append(copy(temp_zone))     # saving zone
                # data['geo_ids'].append(get_geoId(temp_zone, CBGzone_df))

                # Adding time window
                data['time_windows'].append((int(df_prob.loc[df_prob['payload_id'] == i]['del_tw_lower'].values[0]),
                                    int(df_prob.loc[df_prob['payload_id'] == i]['del_tw_upper'].values[0])))

                data['payload_ids'].append(copy(i))

                demand = math.ceil(df_prob.loc[df_prob['payload_id'] == i]['weight'].values[0])
                data['demands'].append(copy(demand))
                if commodity != 2 and ship_index =='internal': data['stops'].append(1)  # stop for this demand location

                service_time = float(df_prob.loc[df_prob['payload_id'] == i]['del_stop_duration'].values[0])
                data['stop_durations'].append(copy(service_time))


            elif prob_type =='pickup':
                temp_zone = int(df_prob.loc[df_prob['payload_id'] == i]['pu_zone'].values[0]) # find zone
                data['loc_zones'].append(copy(temp_zone))   # saving zone
                # data['geo_ids'].append(get_geoId(temp_zone, CBGzone_df))

                # Adding time window
                data['time_windows'].append((int(df_prob.loc[df_prob['payload_id'] == i]['pu_tw_lower'].values[0]),
                                    int(df_prob.loc[df_prob['payload_id'] == i]['pu_tw_upper'].values[0])))

                data['payload_ids'].append(copy(i))

                demand = math.ceil(df_prob.loc[df_prob['payload_id'] == i]['weight'].values[0])
                data['demands'].append(copy(demand))
                if commodity != 2 and ship_index =='internal': data['stops'].append(1) 

                service_time = float(df_prob.loc[df_prob['payload_id'] == i]['pu_stop_duration'].values[0])
                data['stop_durations'].append(copy(service_time))

            elif prob_type == 'pickup_delivery':
                temp_zone_d = int(df_prob.loc[df_prob['payload_id'] == i]['del_zone'].values[0]) # find delivery zone
                temp_zone_p = int(df_prob.loc[df_prob['payload_id'] == i]['pu_zone'].values[0]) # find pickup zone
                # Adding pickup and delivery zone to data frame
                data['loc_zones'].append(copy(temp_zone_p))
                data['loc_zones'].append(copy(temp_zone_d))
                # data['geo_ids'].append(get_geoId(temp_zone_p, CBGzone_df))
                # data['geo_ids'].append(get_geoId(temp_zone_d, CBGzone_df))

                # Adding time pickup and delivery windows
                data['time_windows'].append((int(df_prob.loc[df_prob['payload_id'] == i]['pu_tw_lower'].values[0]),
                                    int(df_prob.loc[df_prob['payload_id'] == i]['pu_tw_upper'].values[0])))
                data['time_windows'].append((int(df_prob.loc[df_prob['payload_id'] == i]['del_tw_lower'].values[0]),
                                    int(df_prob.loc[df_prob['payload_id'] == i]['del_tw_upper'].values[0])))


                data['payload_ids'].append(copy(i))
                data['payload_ids'].append(copy(i))

                demand = math.ceil(df_prob.loc[df_prob['payload_id'] == i]['weight'].values[0])
                data['demands'].append(copy(demand))
                data['demands'].append(copy(-1 * demand))
                if commodity != 2 and ship_index =='internal':
                    data['stops'].append(1)  # Add stop for pickup
                    data['stops'].append(1)  # Add stop for delivery

                # Add pickup service time and delivery service time
                service_time = float(df_prob.loc[df_prob['payload_id'] == i]['pu_stop_duration'].values[0])
                data['stop_durations'].append(copy(service_time))
                service_time = float(df_prob.loc[df_prob['payload_id'] == i]['del_stop_duration'].values[0])
                data['stop_durations'].append(copy(service_time))

                # Assuming that if a carrier has pickup_delivery jobs it only has that
                data['pickups_deliveries'].append([index, index+1])
                index += 2

        # After gathering demand by location, change demand of depot to full load at the depot
        #TODO: this need to be double checked for a problem where one vehile is not enough to deliver everything
        # Below did not work if more than 1 vehicle is needed to handle depot demand

        b_timing = time()
        sel_tt=pd.DataFrame()
        n=0
        for i in data['loc_zones']:
            for j in data['loc_zones']:
                temp =pd.DataFrame({
                    'origin' : i,
                    'destination': j,
                        'TIME_minutes': tt_df[i-1][j-1]/100
                }, index=[n]
                )
                n=n+1
                sel_tt=pd.concat([sel_tt,temp])
        sel_dist=pd.DataFrame()
        n=0
        for i in data['loc_zones']:
            for j in data['loc_zones']:
                temp =pd.DataFrame({
                    'Origin' : i,
                    'Destination': j,
                        'dist': dist_df[i-1][j-1]/100
                }, index=[n]
                )
                n=n+1
                sel_dist=pd.concat([sel_dist,temp])

        max_tt = 0
        for i in range(len(data['loc_zones'])):
            time_l = []
            travel_time = 0
            for j in range(len(data['loc_zones'])):

                travel_time = tt_cal(data['loc_zones'][i], data['loc_zones'][j],
                                    sel_tt, sel_dist)
                time_l.append(int(travel_time))
                if travel_time > max_tt: max_tt = copy(travel_time)

            data['time_matrix'].append(copy(time_l))

        # print("calculating matrix time, ", time()-b_timing)
        # print('max travel time seen: ', max_tt)

        # We assume first value in graph is medium duty and second is duty
        # Adding vehicle capacities
        data['vehicle_capacities'] = []
        data['vehicle_ids'] = []
        data['vehicle_types'] = []
        
        # TODO: this will need to change is we have stop durations for commodity type 2
        if commodity != 2 and ship_index =='internal':
            prefix = ''
            if commodity == 1: prefix = 'bulk'
            elif commodity == 3: prefix= 'interm_food'
            elif commodity == 4: prefix= 'mfr_goods'
            elif commodity == 5: prefix = 'other'

            # stop_df = pd.read_csv('../../../FRISM_input_output_AT/Survey_Data/' + prefix + '_stops_distribution.csv')
            stop_df = pd.read_csv(path_stops + prefix + '_stops_distribution.csv')

        #################### KJ added for veh_tech
        veh_index= veh.split("_")[0]+"_"+veh.split("_")[1]
        veh_id= int(f_prob[veh_index+"_start_id"].values[0])
        veh_capacity =int(v_df[v_df['veh_type_id'] == veh]['payload_capacity_weight'].values[0])
        for i in range(0, int(f_prob[veh_index].values[0])):
            data['vehicle_capacities'].append(int(veh_capacity))
            data['vehicle_ids'].append(veh_id)
            data['vehicle_types'].append(veh) 
            veh_id += 1

            if commodity != 2 and ship_index =='internal':
                    prob = random.uniform(0, 1)
                    temp = stop_df[stop_df.Cum_Prob >= prob].reset_index()
                    max_stops = temp.loc[0,'Num_Trips_per_Tour']
                    slack_stops = temp.loc[len(temp)-1, 'Num_Trips_per_Tour']
                    data['vehicle_max_stops'].append(int(max_stops))
                    data['vehicle_slack_stops'].append(int(slack_stops))

        data['num_vehicles'] = int(f_prob[veh_index].values[0])

        # print("veh_capacity: ", veh_capacity, " num_veh: ", data['num_vehicles'])
        data['depot'] = 0

        # print(data)
        # Saving dictionary for testing purposes
        # with open('test_data/b2b_pickup_delivery_internal.pickle', 'wb') as handle:
        #     pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

    except Exception as e:
        print('Could not build data dictionary for: ', carrier_id, 'and vehicle ', veh , ' : ', e)
        return {}

    return data

def print_solution(data, manager, routing, solution, tour_df, carr_id, carrier_df, payload_df, prob_type,
                   count_num, ship_type, c_prob, df_prob, comm):
    """Prints the vehicle routing problem solution on console.

    Args:
        data: dictionary of vehicle routing problem (VRP) data
        manager: VRP's routing index manager
        routing: VRP's routing model
        solution: VRP's solution
        tour_df: dataframe to save vehicles' tour information 
        carr_id: carrier id for the particular problem solved
        carrier_df: dataframe to save carrier information from VRP solution
        payload_df: dataframe to save payload information from VRP solution
        prob_type: problem type (pickup, delivery, or pickup and delivery)
        count_num: county number
        ship_type: shipment type, business to business (B2B) or business to consumer (B2C)
        c_prob: dataframe with VRP's carrier 
        df_prob:dataframe with VRP's payload

    Returns:
        used_veh: a list of ids of vehicle used
    """


    global tour_id
    global payload_i
    global depot_i

    used_veh = []

    # print(f'Objective: {solution.ObjectiveValue()}')
    time_dimension = routing.GetDimensionOrDie('Time')
    total_time = 0
    req_type = 0
    for vehicle_id in range(data['num_vehicles']):
        route_load = 0
        index = routing.Start(vehicle_id)
        start_loc = manager.IndexToNode(index)
        next_loc = manager.IndexToNode(solution.Value(routing.NextVar(index)))

        # Print out solution from vehicles that left the dept
        if start_loc != next_loc:
            used_veh.append(vehicle_id)
            start_time = solution.Min(time_dimension.CumulVar(index))

            # Adding tour, carrier info to csv
            # Format for tour csv: ['tour_id', 'departureTimeInSec', 'departureLocation_zone', 'maxTourDurationInSec']
            # Fomat for carrier csv: ['carrierId','tourId', 'vehicleId', 'vehicleTypeId','depot_zone']
            depot_x = c_prob['c_x'].values[0]
            depot_y = c_prob['c_y'].values[0]
            true_depot = c_prob['true_depot_zone'].values[0]

            tour_df.loc[tour_id] = [tour_id, start_time*60, data['loc_zones'][manager.IndexToNode(index)], 3600*12,
                                    depot_x, depot_y,true_depot]
            carrier_df.loc[tour_id] = [carr_id, tour_id, "c"+str(count_num)+"_"+str(data['vehicle_ids'][vehicle_id]),
                                       data['vehicle_types'][vehicle_id], data['loc_zones'][manager.IndexToNode(index)],
                                       depot_x,depot_y,true_depot]

            plan_output = 'Route for vehicle {0} with id {1}:\n'.format(vehicle_id, data['vehicle_ids'][vehicle_id])
            plan_output_l = 'Load for vehicle {}:\n'.format(vehicle_id)
            seqId = 0

            if prob_type == 'delivery':
                beg_index = payload_i   # to be used to adjust load info for delivery problems
                node_list = []
                req_type = 1
            elif prob_type == 'pickup': req_type = 2
            else: req_type = 3    

            while not routing.IsEnd(index):

                node_index = manager.IndexToNode(index)
                time_var = time_dimension.CumulVar(index)
                plan_output += '{0} Time({1},{2}) -> '.format(
                    manager.IndexToNode(index), solution.Min(time_var),
                    solution.Max(time_var))

                # Load info
                route_load += data['demands'][node_index]

                # Add processing for depot
                if node_index == 0:
                    payload_df.loc[payload_i] = [str(count_num) + '_d' + ship_type + str(depot_i), int(seqId), int(tour_id),
                                                 int(comm),
                                                 int(data['demands'][node_index]), int(route_load), req_type,
                                                 int(data['loc_zones'][node_index]),
                                                 int(solution.Min(time_var) * 60),
                                                 int(0 * 60),
                                                 int(0 * 60),
                                                 int(0 * 60), depot_x, depot_y,true_depot,"NA","NA","NA"]

                elif(node_index != 0):
                    id_payload = str(data['payload_ids'][node_index-1])
                    loc_x = 0
                    loc_y = 0
                    if prob_type == 'pickup':
                        loc_x = df_prob[df_prob['payload_id'] == id_payload]['pu_x'].values[0]
                        loc_y = df_prob[df_prob['payload_id'] == id_payload]['pu_y'].values[0]
                        true_zone = df_prob[df_prob['payload_id'] == id_payload]['true_pu_zone'].values[0]
                    
                    elif prob_type == 'delivery':
                        loc_x = df_prob[df_prob['payload_id'] == id_payload]['del_x'].values[0]
                        loc_y = df_prob[df_prob['payload_id'] == id_payload]['del_y'].values[0]
                        true_zone = df_prob[df_prob['payload_id'] == id_payload]['true_del_zone'].values[0]

                    elif prob_type == 'pickup_delivery':
                        if data['demands'][node_index] > 0:
                            loc_x = df_prob[df_prob['payload_id'] == id_payload]['pu_x'].values[0]
                            loc_y = df_prob[df_prob['payload_id'] == id_payload]['pu_y'].values[0]
                            true_zone = df_prob[df_prob['payload_id'] == id_payload]['true_pu_zone'].values[0]                       
                        elif data['demands'][node_index] < 0:
                            loc_x = df_prob[df_prob['payload_id'] == id_payload]['del_x'].values[0]
                            loc_y = df_prob[df_prob['payload_id'] == id_payload]['del_y'].values[0]
                            true_zone = df_prob[df_prob['payload_id'] == id_payload]['true_del_zone'].values[0]
                    true_mode = df_prob[df_prob['payload_id'] == id_payload]['truck_mode'].values[0]
                    buy_naics = df_prob[df_prob['payload_id'] == id_payload]['BuyerNAICS'].values[0]
                    seller_naics = df_prob[df_prob['payload_id'] == id_payload]['SellerNAICS'].values[0]
                    payload_df.loc[payload_i] = [str(data['payload_ids'][node_index-1]), int(seqId), int(tour_id), int(comm),
                                                 int(data['demands'][node_index]), int(route_load), req_type, int(data['loc_zones'][node_index]),
                                                int(solution.Min(time_var)*60),
                                                 int(data['time_windows'][node_index][0]*60),
                                                int(data['time_windows'][node_index][1]*60),
                                                 int(data['stop_durations'][node_index]*60),
                                                 loc_x, loc_y, true_zone,buy_naics,seller_naics,true_mode]
                payload_i += 1
                seqId += 1


                if prob_type == 'delivery': node_list.append(copy(node_index))
                else:
                    plan_output_l += ' {0} Load({1}) -> '.format(node_index, route_load)
                previous_index = index
                index = solution.Value(routing.NextVar(index))

            # Node of depot
            node_index = manager.IndexToNode(index)
            time_var = time_dimension.CumulVar(index)
            
            ['payloadId','sequenceRank','tourId','payloadType','weightInlb','cummulativeWeightInlb',
                                         'requestType','locationZone','estimatedTimeOfArrivalInSec','arrivalTimeWindowInSec_lower',
                                         'arrivalTimeWindowInSec_upper','operationDurationInSec', 'locationZone_x', 'locationZone_y']
            payload_df.loc[payload_i] = [str(count_num) + '_d' + ship_type + str(depot_i) + '_', int(seqId), int(tour_id),
                                         int(comm),
                                         int(data['demands'][node_index]), int(route_load), req_type,
                                         int(data['loc_zones'][node_index]),
                                         int(solution.Min(time_var) * 60),
                                         int(0 * 60),
                                         int(0 * 60),
                                         int(0 * 60),
                                         depot_x, depot_y,true_depot,"NA","NA","NA"]


            if prob_type == 'delivery':
                tot_load = route_load
                end_index = payload_i   # to be used to adjust load info for delivery problems
                # payload_df.loc[beg_index]['cummulativeWeightInlb'] = tot_load

                l = 0
                for k in range(beg_index, end_index):
                    temp_load = tot_load - payload_df.loc[k]['weightInlb']
                    payload_df.loc[k,('cummulativeWeightInlb')] = temp_load
                    if k == beg_index: payload_df.loc[k,('weightInlb')] = temp_load
                    else:
                        payload_df.loc[k,('weightInlb')] = -1 * payload_df.loc[k]['weightInlb']

                    plan_output_l += ' {0} Load({1}) -> '.format(node_list[l], temp_load)
                    tot_load = copy(temp_load)
                    l += 1

                # When the vehicle goes back to the depot, it's load is zero
                payload_df.loc[end_index,'cummulativeWeightInlb'] = 0
                route_load = temp_load

                #Increment the load index
            payload_i +=1

            plan_output += '{0} Time({1},{2})'.format(manager.IndexToNode(index),
                                                        solution.Min(time_var),
                                                        solution.Max(time_var))
            plan_output_l += ' {0} Load({1})\n'.format(manager.IndexToNode(index),
                                                 route_load)
            if prob_type != 'delivery': plan_output += 'Time of the route: {}min'.format(
                solution.Min(time_var) - start_time)

            # print(plan_output)
            # print(plan_output_l)
            total_time += solution.Min(time_var)- start_time
            tour_id += 1 # Incrementing for the tour id
            depot_i +=1
    
    # print('Used Vehicles: ', used_veh)
    # print('Total time of all routes: {}min'.format(total_time))

    return used_veh

def input_files_processing(travel_file, carrier_file, payload_file, vehicleType_file):
    """Processes input files.

    Reads in input files and processes them to generate dataframe with necessary to generate tours for
    vehicles.

    Args:
        travel_file: file with origin-destination travel time information.
        dist_file: file with origin-destination distance information.
        CBGzone_file: file that maps mesozones ids to geo ids.
        carrier_file: file with carrier information.
        payload_file: file with payload information.
        vehicleType_file: file with vehicle type information

    Returns:
        tt_df: origin-destination travel time dataframe.
        dist_df: origin-destination distance dataframe.
        CBGzone_df: dataframe that maps mesozones to geo ids.
        c_df: carrier information dataframe.
        p_df: paylaod information dataframe.
        v_df: dataframe with vehicle type information (capacity, weight, diezel or electric, ...)
        vc_df: dataframe with individual vehicle information (id, capacity, ...)
    """
    try:
        # KJ: read travel time, distance, zonal file as inputs  # Slow step
        f = h5py.File(travel_file, 'r')

        f_7to8=f['Skims']
        list(f_7to8.keys())
        tt_df = f['Skims']['heavy_truckt']
        dist_df = f['Skims']['heavy_truckd']  # Slow step
        
        # We need to know the depot using the carrier file
        c_df = pd.read_csv(carrier_file)
        c_df = c_df.dropna(axis=1, how='all')   # Removing all nan
        c_df = c_df.astype({'depot_zone': int, 'true_depot_zone': int})
        #c_df = c_df[c_df["num_veh_type_1"]>0]  # Removing carriers don't have vehicles (Temporary solution)- need to check Shipment code

        # reading payload definition
        p_df = pd.read_csv(payload_file)
        p_df = p_df.dropna(axis=1, how='all')   # Removing all nan
        p_df = p_df.astype({'pu_zone': int, 'del_zone': int})

        # Removing nans
        c_df = c_df.fillna(0); # Fill all nan with zeros

        # Removing nans
        p_df['carrier_id'] = p_df['carrier_id'].astype(str)
        p_df['sequence_id'] = np.nan
        p_df['tour_id'] = np.nan
        p_df['pu_arrival_time'] = np.nan
        p_df['del_arrival_time'] = np.nan
        p_df = p_df.fillna(int(0))

        # Adding in additional colums for vehicle tours
        # Changing tour id and sequence id into ints
        p_df['tour_id'] = p_df['tour_id'].astype(int)
        p_df['sequence_id'] = p_df['sequence_id'].astype(int)

        # Reading in vehicle information
        v_df = pd.read_csv(vehicleType_file)
        v_df = v_df.dropna(axis=1, how='all')   # Removing all nan
        ################ KJ added for veh_tech
        veh_list=p_df["veh_type"].unique()
        veh_list = [ x.split("_")[0]+"_"+x.split("_")[1] for x in veh_list]
        veh_list = list(dict.fromkeys(veh_list))
        # Create vehicle sequence vehicle ID
        vc_df = pd.DataFrame()
        vc_df['carrier_id']=c_df['carrier_id']
        for key in veh_list:
            vc_df[key]=c_df[key]
            vc_df[key+'_start_id']=np.nan
        vc_df = vc_df.fillna(int(0))
        vc_df = vc_df.reset_index()
        n=0
        for i in range (0, vc_df.shape[0]):
            for j in range(0,len(veh_list)):
                if j==0:
                    veh_type_id=veh_list[j]
                    vc_df.loc[i,veh_type_id+"_start_id"]=n
                else:
                    veh_type_id=veh_list[j]
                    n=n+ vc_df.loc[i,veh_list[j-1]]
                    vc_df.loc[i,veh_type_id+"_start_id"]=n 
                if j== len(veh_list)-1:
                    n=  n + vc_df.loc[i,veh_type_id] 
        return tt_df, dist_df, c_df, p_df, v_df, vc_df
    except Exception as e:
        prefix = ''
        if 'gzipped' in str(e): prefix = 'Travel time file'
        print('Could not parse input files: exception: ', prefix, e)
        return None

def form_solve(data, tour_df, carr_id, carrier_df, payload_df, prob_type, count_num, ship_type, c_prob, 
                df_prob, max_time, index, comm, error_list):
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
        return data['time_matrix'][from_node][to_node] + data['stop_durations'][from_node]

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

    if index == 'internal' and comm != 2:
                # Add Capacity constraint.
        def stops_callback(from_index):
            """Returns the stops of the node."""
            # Convert from routing variable Index to demands NodeIndex.
            from_node = manager.IndexToNode(from_index)
            return data['stops'][from_node]

        stops_callback_index = routing.RegisterUnaryTransitCallback(
            stops_callback)
        routing.AddDimensionWithVehicleCapacity(
            stops_callback_index,
            0,  # null capacity slack
            data['vehicle_slack_stops'],  # vehicle maximum capacities
            True,  # start cumul to zero
            'Stops')
        
        stop_dimension = routing.GetDimensionOrDie('Stops')
        
        penalty_stop = 100000
        for v in range(data['num_vehicles']):
            stop_dimension.SetCumulVarSoftUpperBound(routing.End(v), data['vehicle_max_stops'][v], penalty_stop)
    #     # Allow to go over number of stops
        penalty_drop = 100000
        for node in range(1, len(data['time_matrix'])):
            routing.AddDisjunction([manager.NodeToIndex(node)], penalty_drop)

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
    search_parameters.time_limit.seconds = max_time   #set a time limit of 900 seconds for a search

    s_time = time()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    #print('before solving the problem')
    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    solve_time = time() - s_time
    # print('\nTime to solve is: ', solve_time)
    #print('after solving the problem')
    # Print solution on console.
    if solution:
        try:
            used_veh = print_solution(data, manager, routing, solution, tour_df, carr_id, carrier_df,
                                  payload_df, prob_type, count_num, ship_type, c_prob, df_prob, comm)
            # print('\n')
            return used_veh
        except Exception as e:
            veh = data['vehicle_types'][0]
            print('Could not write out solution for : ', carr_id, ' : ', e)
            error_list.append([carr_id, veh, comm, index, e])

    else:
        st = routing.status()
        message = ''
        if st == 0:
            message = 'PROBLEM NOT YET SOLVED'
        elif st == 2:
            message = 'NO SOLUTION FOUND FOR PROBLEM'
        elif st == 3:
            message = 'TIME LIMIT REACHED BEFORE FINDING A SOLUTION'
        elif st ==4:
            message = 'MODEL, PARAMETERS, OR FLAGS ARE INVALID'

        veh = data['vehicle_types'][0]
        print('Could not find a solution for carrier: ', carr_id, ' with prob type', prob_type, ' and veh type ', veh,
        ' comm ', comm, ' index ', index, ': ', message)
        error_list.append([carr_id, veh, comm, index, message])
        # print('\n')
        return []
