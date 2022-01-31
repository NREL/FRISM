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
# def x_y_finder(meso):
#     try:
#         find_index=CBGzone_df.index[CBGzone_df['MESOZONE']==meso]
#         x_cord= CBGzone_df.iloc[find_index].X_cord.values[0]
#         y_cord= CBGzone_df.iloc[find_index].Y_cord.values[0]
#         return x_cord, y_cord
#     except:
#         return "NA", "NA"


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
    # if problem is delivery, we start with full laod at depot
    # if problem is pickup, we start with empty load
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
            data['demands'].append(copy(-1 * demand))

            # Add pickup service time and delivery service time
            service_time = float(df_prob.loc[df_prob['payload_id'] == i]['pu_stop_duration'].values[0])
            data['stop_durations'].append(copy(service_time))
            service_time = float(df_prob.loc[df_prob['payload_id'] == i]['del_stop_duration'].values[0])
            data['stop_durations'].append(copy(service_time))

            # Assuming that if a carrier has pickup_delivery jobs it only has that
            data['pickups_deliveries'].append([index, index+1])
            index += 2

    # After gathering demand by location, change demand of depot to full load at the depot
    #JU: this need to be double checked for a problem where one vehile is not enough to deliver everything
    # Below did not work if more than 1 vehicle is needed to handle depot demand
    # if prob_type == 'delivery':
    #     data['demands'][0] = -1 * sum(data['demands'])


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
    for i in range(0,int(f_prob['md_veh'].values[0])):
        data['vehicle_capacities'].append(int(v_df[v_df['veh_category'] == 'MD']['payload_capacity_weight'].values[0]))
        data['vehicle_ids'].append(md_veh_id)
        data['vehicle_types'].append(1)  # 1 represent medium duty
        md_veh_id += 1
    # Adding heavy duty capacities
    for i in range(0,int(f_prob['hd_veh'].values[0])):
        data['vehicle_capacities'].append(int(v_df[v_df['veh_category'] == 'HD']['payload_capacity_weight'].values[0]))
        data['vehicle_ids'].append(hd_veh_id)
        data['vehicle_types'].append(2)   # 2 represent heavy duty
        hd_veh_id += 1

    data['num_vehicles'] = int(f_prob['md_veh'].values[0] + f_prob['hd_veh'].values[0])
    print("veh_capacity: ", veh_capacity, " num_veh: ", data['num_vehicles'])
    data['depot'] = 0
    return data


def print_solution(data, manager, routing, solution, tour_df, carr_id, carrier_df, payload_df, prob_type):
    """Prints solution on console."""
    global tour_id
    global payload_i
    print(f'Objective: {solution.ObjectiveValue()}')
    time_dimension = routing.GetDimensionOrDie('Time')
    total_time = 0
    for vehicle_id in range(data['num_vehicles']):
        route_load = 0
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
            seqId = 0

            if prob_type == 'delivery':
                beg_index = payload_i   # to be used to adjust load info for delivery problems
                node_list = []

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
                    payload_df.loc[payload_i] = [int(-1), int(seqId), int(tour_id),
                                                 int(1),
                                                 int(data['demands'][node_index]), int(route_load), 1,
                                                 int(data['loc_zones'][node_index]),
                                                 int((solution.Min(time_var) - data['stop_durations'][
                                                     node_index]) * 60),
                                                 int(0 * 60),
                                                 int(0 * 60),
                                                 int(0 * 60)]

                elif(node_index != 0): # Only add the payload info if this is not the depot
                    payload_df.loc[payload_i] = [int(data['payload_ids'][node_index-1]), int(seqId), int(tour_id), int(1),
                                                 int(data['demands'][node_index]), int(route_load), 1, int(data['loc_zones'][node_index]),
                                                int((solution.Min(time_var)-data['stop_durations'][node_index])*60),
                                                 int(data['time_windows'][node_index][0]*60),
                                                int(data['time_windows'][node_index][1]*60),
                                                 int(data['stop_durations'][node_index]*60)]
                payload_i += 1
                seqId += 1


                if prob_type == 'delivery': node_list.append(copy(node_index))
                else:
                    plan_output_l += ' {0} Load({1}) -> '.format(node_index, route_load)
                previous_index = index
                index = solution.Value(routing.NextVar(index))

            # Node of depot
            node_index = manager.IndexToNode(index)
            payload_df.loc[payload_i] = [int(-1), int(seqId), int(tour_id),
                                         int(1),
                                         int(data['demands'][node_index]), int(route_load), 1,
                                         int(data['loc_zones'][node_index]),
                                         int((solution.Min(time_var) - data['stop_durations'][
                                             node_index]) * 60),
                                         int(0 * 60),
                                         int(0 * 60),
                                         int(0 * 60)]


            if prob_type == 'delivery':
                tot_load = route_load
                end_index = payload_i   # to be used to adjust load info for delivery problems
                # payload_df.loc[beg_index]['cummulativeWeightInlb'] = tot_load

                for k in range(beg_index, end_index):
                    temp_load = tot_load - payload_df.loc[k]['weightInlb']
                    payload_df.loc[k]['cummulativeWeightInlb'] = temp_load
                    plan_output_l += ' {0} Load({1}) -> '.format(node_index, temp_load)
                    tot_load = copy(temp_load)

                # When the vehicle goes back to the depot, it's load is zero
                payload_df.loc[end_index]['cummulativeWeightInlb'] = 0
                route_load = temp_load

                #Increment the load index
            payload_i +=1

            time_var = time_dimension.CumulVar(index)
            plan_output += '{0} Time({1},{2})\n'.format(manager.IndexToNode(index),
                                                        solution.Min(time_var),
                                                        solution.Max(time_var))
            plan_output_l += ' {0} Load({1})'.format(manager.IndexToNode(index),
                                                 route_load)
            if prob_type != 'delivery': plan_output += 'Time of the route: {}min'.format(
                solution.Min(time_var) - start_time)

            print(plan_output)
            print(plan_output_l)
            total_time += solution.Min(time_var)- start_time
            tour_id += 1 # Incrementing for the tour id
    print('Total time of all routes: {}min'.format(total_time))

def input_files_processing(travel_file, dist_file, CBGzone_file, carrier_file, payload_file, vehicleType_file):

    # KJ: read travel time, distance, zonal file as inputs  # Slow step
    tt_df = pd.read_csv(travel_file, compression='gzip', header=0, sep=',', quotechar='"', error_bad_lines=False)
    dist_df = pd.read_csv(dist_file)  # Slow step
    CBGzone_df = gp.read_file(CBGzone_file)

    # We need to know the depot using the carrier file
    c_df = pd.read_csv(carrier_file)
    c_df = c_df.dropna(axis=1, how='all')   # Removing all nan
    c_df = c_df[c_df["num_veh_type_1"]>0]  # Removing carriers don't have vehicles (Temporary solution)- need to check Shipment code

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
    vc_df['md_start_id']=np.nan
    vc_df['hd_start_id']=np.nan
    vc_df = vc_df.fillna(int(0));
    vc_df = vc_df.reset_index()

    n=0
    for i in range (0, vc_df.shape[0]):
        vc_df.loc[i,'md_start_id'] =  n
        vc_df.loc[i,'hd_start_id'] =  n + vc_df.loc[i,'md_veh']
        n= vc_df.loc[i,'hd_start_id'] + vc_df.loc[i,'hd_veh']

    # Reading vehicles by carrier
    #vc_df = pd.read_csv(vehicleCarrier_file)

    return tt_df, dist_df, CBGzone_df, c_df, p_df, v_df, vc_df

def random_points_in_polygon(polygon):
    temp = polygon.bounds
    finished= False
    while not finished:
        point = Point(random.uniform(temp.minx.values[0], temp.maxx.values[0]), random.uniform(temp.miny, temp.maxy.values[0]))
        finished = polygon.contains(point).values[0]
    return point

def random_loc (t_df,c_df,p_df,SFBay_CBG):
    c_df['depot_zone_x']=0.0
    c_df['depot_zone_y']=0.0
    carr_id=0.0
    for i in range(0,c_df.shape[0]):
        if c_df.carrierId[i] == carr_id:
            c_df.loc[i,'depot_zone_x']=c_df.loc[i-1,'depot_zone_x']
            c_df.loc[i,'depot_zone_y']=c_df.loc[i-1,'depot_zone_y']
        else:
            point=random_points_in_polygon(SFBay_CBG.geometry[SFBay_CBG.MESOZONE==c_df.depot_zone[i]])
            c_df.loc[i,'depot_zone_x']=point.x
            c_df.loc[i,'depot_zone_y']=point.y
            carr_id = c_df.carrierId[i]

    t_df['departureLocation_x']=0.0
    t_df['departureLocation_y']=0.0
    for i in range(0,t_df.shape[0]):
        temp=c_df[c_df.depot_zone==t_df.departureLocation_zone[i]][['depot_zone_x','depot_zone_y']].reset_index()
        t_df.loc[i,'departureLocation_x']=temp.depot_zone_x[0]
        t_df.loc[i,'departureLocation_y']=temp.depot_zone_y[0]

    p_df['locationZone_x']=0.0
    p_df['locationZone_y']=0.0
    for i in range(0,p_df.shape[0]):
        point=random_points_in_polygon(SFBay_CBG.geometry[SFBay_CBG.MESOZONE==p_df['locationZone'][i]])
        p_df.loc[i,'locationZone_x']=point.x
        p_df.loc[i,'locationZone_y']=point.y

    return c_df, t_df, p_df

def external_zone (t_df,c_df,p_df,ex_zone,tt_df, dist_df, CBGzone_df):

    p_df=p_df.merge(ex_zone, how ='left', left_on='locationZone', right_on='MESOZONE')
    p_df.BoundaryZONE.fillna('no', inplace=True)
    c_df =c_df.merge(ex_zone, how ='left', left_on='depot_zone', right_on='MESOZONE')
    c_df.BoundaryZONE.fillna('no', inplace=True)

    p_df_update=pd.DataFrame()

    list_nm=['payloadId','sequenceRank','tourId','payloadType','weightInlb','requestType',
                                             'locationZone','estimatedTimeOfArrivalInSec','arrivalTimeWindowInSec_lower',
                                             'arrivalTimeWindowInSec_upper','operationDurationInSec']
    for tour_id in p_df['tourId'].unique():
        temp_payload = p_df[p_df['tourId']==tour_id].reset_index()
        if c_df[c_df['tourId']==tour_id]['BoundaryZONE'].values[0] == 'no'  :
            index_tour= "out_bound"
        else:
            index_tour= "in_bound"
        if index_tour== "out_bound":
            temp_payload_update=pd.DataFrame(columns = list_nm)
            loc_flag="in"
            loc_from = c_df[c_df['tourId']==tour_id]['depot_zone'].values[0]
            dtime_from= t_df[t_df['tour_id']==tour_id]['departureTimeInSec'].values[0]
            for i in range(0,temp_payload.shape[0]):
                if temp_payload.loc[i,'BoundaryZONE'] == 'no' and loc_flag=="in":
                    loc_from= temp_payload.loc[i,'locationZone']
                    dtime_from = temp_payload.loc[i,'estimatedTimeOfArrivalInSec']+temp_payload.loc[i,'operationDurationInSec']
                    temp_payload_update=pd.concat([temp_payload_update,temp_payload.loc[[i],list_nm]], ignore_index=True)
                elif temp_payload.loc[i,'BoundaryZONE'] != 'no' and loc_flag=="in":
                    temp_payload.loc[i,'locationZone']=temp_payload.loc[i,'BoundaryZONE']
                    seq_out=temp_payload.loc[i,'sequenceRank']
                    loc_to = temp_payload.loc[i,'BoundaryZONE']
                    org_geoID=get_geoId(loc_from, CBGzone_df)
                    dest_geoID=get_geoId(loc_to, CBGzone_df)
                    travel_time = tt_cal(loc_from, loc_to, org_geoID, dest_geoID, tt_df, dist_df)*60
                    temp_payload_update=pd.concat([temp_payload_update,temp_payload.loc[[i],list_nm]], ignore_index=True)
                    temp_payload_update.loc[temp_payload_update.index[-1],'estimatedTimeOfArrivalInSec']= dtime_from+travel_time
                    a=temp_payload.loc[i,'MESOZONE']
                    b=loc_to
                    org_geoID=get_geoId(a, CBGzone_df)
                    dest_geoID=get_geoId(b, CBGzone_df)
                    travel_time = tt_cal(a, b, org_geoID, dest_geoID, tt_df, dist_df)*60
                    temp_payload_update.loc[temp_payload_update.index[-1],'operationDurationInSec']= temp_payload.loc[i,'estimatedTimeOfArrivalInSec'] + \
                                                                                                     temp_payload.loc[i,'operationDurationInSec'] - \
                                                                                                     temp_payload_update.loc[temp_payload_update.index[-1],'estimatedTimeOfArrivalInSec'] + \
                                                                                                     travel_time
                    loc_flag="out"

                elif temp_payload.loc[i,'BoundaryZONE'] != 'no' and loc_flag=="out":
                    temp_payload_update.loc[temp_payload_update.index[-1],'weightInlb']=temp_payload_update.loc[temp_payload_update.index[-1],'weightInlb']+ \
                                                                                        temp_payload.loc[i,'weightInlb']
                    a=temp_payload.loc[i,'MESOZONE']
                    b=loc_to
                    org_geoID=get_geoId(a, CBGzone_df)
                    dest_geoID=get_geoId(b, CBGzone_df)
                    travel_time = tt_cal(a, b, org_geoID, dest_geoID, tt_df, dist_df)*60
                    temp_payload_update.loc[temp_payload_update.index[-1],'operationDurationInSec']= temp_payload.loc[i,'estimatedTimeOfArrivalInSec'] - \
                                                                                                     temp_payload_update.loc[temp_payload_update.index[-1],'estimatedTimeOfArrivalInSec']+ \
                                                                                                     travel_time

                elif temp_payload.loc[i,'BoundaryZONE'] == 'no' and loc_flag=="out":
                    a=temp_payload.loc[i,'MESOZONE']
                    b=loc_to
                    org_geoID=get_geoId(a, CBGzone_df)
                    dest_geoID=get_geoId(b, CBGzone_df)
                    travel_time = tt_cal(a, b, org_geoID, dest_geoID, tt_df, dist_df)*60
                    temp_payload_update.loc[temp_payload_update.index[-1],'operationDurationInSec']= temp_payload.loc[i,'estimatedTimeOfArrivalInSec'] - \
                                                                                                     temp_payload_update.loc[temp_payload_update.index[-1],'estimatedTimeOfArrivalInSec']- \
                                                                                                     travel_time
                    temp_payload_update=pd.concat([temp_payload_update,temp_payload.loc[[i],list_nm]], ignore_index=True)
                    loc_flag="in"

            temp_payload_update['sequenceRank']=range(1,temp_payload_update.shape[0]+1)
            p_df_update = pd.concat([p_df_update,temp_payload_update], ignore_index=True)

        elif index_tour== "in_bound": # maybe need to revisit later
            temp_payload_update=pd.DataFrame(columns = list_nm)
            loc_flag="out"
            ex_depot = c_df[c_df['tourId']==tour_id]['BoundaryZONE'].values[0]
            #dtime_from= t_df[t_df['tour_id']==tour_id]['departureTimeInSec'].values[0]
            n=0
            for i in range(0,temp_payload.shape[0]):
                if temp_payload.loc[i,'BoundaryZONE'] == 'no' and loc_flag=="out":
                    day=int(temp_payload.loc[i,'estimatedTimeOfArrivalInSec']/24*60*60)
                    loc_from = ex_depot
                    loc_to = temp_payload.loc[i,'locationZone']
                    org_geoID=get_geoId(loc_from, CBGzone_df)
                    dest_geoID=get_geoId(loc_to, CBGzone_df)
                    travel_time = tt_cal(loc_from, loc_to, org_geoID, dest_geoID, tt_df, dist_df)*60

                    arr_time = temp_payload.loc[i,'estimatedTimeOfArrivalInSec']-day*24*60*60
                    dep_time= temp_payload.loc[i,'estimatedTimeOfArrivalInSec']-day*24*60*60 - travel_time
                    if dep_time <=0:
                        dep_time =0
                        arr_time = travel_time
                    loc_flag="in"

                    temp_payload_update=pd.concat([temp_payload_update,temp_payload.loc[[i],list_nm]], ignore_index=True)


                    loc_from= temp_payload.loc[i,'locationZone']
                    dtime_from = temp_payload.loc[i,'estimatedTimeOfArrivalInSec']+temp_payload.loc[i,'operationDurationInSec']
                    temp_payload_update=pd.concat([temp_payload_update,temp_payload.loc[[i],list_nm]], ignore_index=True)
                    temp_payload_update.loc[temp_payload_update.index[-1],'estimatedTimeOfArrivalInSec'] = arr_time
                    if n==0:
                        c_df.loc[c_df['tourId']== tour_id,'depot_zone']= ex_depot
                        t_df.loc[t_df['tour_id']== tour_id,'departureLocation_zone']= ex_depot
                        t_df.loc[t_df['tour_id']== tour_id, 'departureTimeInSec']= dep_time
                    n=n+1
                elif temp_payload.loc[i,'BoundaryZONE'] == 'no' and loc_flag=="in":
                    temp_payload_update=pd.concat([temp_payload_update,temp_payload.loc[[i],list_nm]], ignore_index=True)
                    temp_payload_update.loc[temp_payload_update.index[-1],'estimatedTimeOfArrivalInSec'] = temp_payload_update.loc[temp_payload_update.index[-2],'estimatedTimeOfArrivalInSec'] + \
                                                                                                           (temp_payload.loc[i,'estimatedTimeOfArrivalInSec']- temp_payload.loc[i-1,'estimatedTimeOfArrivalInSec'])

            temp_payload_update['sequenceRank']=range(1,temp_payload_update.shape[0]+1)
            p_df_update = pd.concat([p_df_update,temp_payload_update], ignore_index=True)
    return t_df, c_df, p_df_update
    p_df=p_df.merge(ex_zone, how ='left', left_on='locationZone', right_on='MESOZONE')
    p_df.BoundaryZONE.fillna('no', inplace=True)

    p_df_update=pd.DataFrame()
    for tour_id in p_df['tourId'].unique():
    #for tour_id in [0,1]:
        temp_payload = p_df[p_df['tourId']==tour_id].reset_index()
        if temp_payload.loc[0,'BoundaryZONE'] == 'no':
            index_tour= "out_bound"
        else:
            index_tour= "in_bound"
        if index_tour== "out_bound":
            n=0
            temp_payload['within_flg']=0
            for i in range(0,temp_payload.shape[0]):
                if temp_payload.loc[i,'BoundaryZONE'] == 'no':
                    n=n+0
                    temp_payload.loc[i,'within_flg']=n
                else:
                    n=n+1
                    temp_payload.loc[i,'within_flg']=n
                    temp_payload.loc[i,'locationZone']=temp_payload.loc[i,'BoundaryZONE']

            temp_payload=temp_payload[temp_payload['within_flg']<=1]
            temp_payload=temp_payload.loc[:,"payloadId":"operationDurationInSec"]
            p_df_update = pd.concat([p_df_update,temp_payload], ignore_index=True)
        elif index_tour== "in_bound":
            n=0
            temp_payload['within_flg']=0
            for i in range(0,temp_payload.shape[0]):
                if temp_payload.loc[i,'BoundaryZONE'] != 'no':
                    n=n+0
                    temp_payload.loc[i,'within_flg']=n
                else:
                    ex_depot=temp_payload.loc[i-1,'BoundaryZONE']
                    ex_depature_time = temp_payload.loc[i,'estimatedTimeOfArrivalInSec']-1.5*60*60
                    n=n+1
                    temp_payload.loc[i,'within_flg']=n


            temp_payload=temp_payload[temp_payload['within_flg']>=1]
            temp_payload['sequenceRank'] = temp_payload['within_flg']
            temp_payload=temp_payload.loc[:,"payloadId":"operationDurationInSec"]
            c_df.loc[c_df['tourId']== tour_id,'depot_zone']= ex_depot
            t_df.loc[t_df['tour_id']== tour_id,'departureLocation_zone']= ex_depot
            t_df.loc[t_df['tour_id']== tour_id, 'departureTimeInSec']= ex_depature_time
            p_df_update = pd.concat([p_df_update,temp_payload], ignore_index=True)
        return t_df, c_df, p_df_update

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

    args = parser.parse_args()


    tt_df, dist_df, CBGzone_df, c_df, p_df, v_df, vc_df = input_files_processing(args.travel_file, args.dist_file,args.CBGzone_file, args.carrier_file, args.payload_file, args.vehicleType_file)

    b_time = time()
    # data frames for the tour, carrier and payload
    tour_df = pd.DataFrame(columns = ['tour_id', 'departureTimeInSec', 'departureLocation_zone', 'maxTourDurationInSec'])
    # Format for carrier data frame: carrierId,tourId, vehicleId,vehicleTypeId,depot_zone
    carrier_df = pd.DataFrame(columns = ['carrierId','tourId', 'vehicleId', 'vehicleTypeId','depot_zone'])
    # format for payload format
    # payloadId, sequenceRank, tourId, payloadType, weightInlb, requestType,locationZone,
    # estimatedTimeOfArrivalInSec, arrivalTimeWindowInSec_lower, arrivalTimeWindowInSec_upper,operationDurationInSec
    payload_df = pd.DataFrame(columns = ['payloadId','sequenceRank','tourId','payloadType','weightInlb','cummulativeWeightInlb',
                                         'requestType','locationZone','estimatedTimeOfArrivalInSec','arrivalTimeWindowInSec_lower',
                                         'arrivalTimeWindowInSec_upper','operationDurationInSec'])

    error_list = []
    error_list.append(['carrier', 'reason'])

    for carr_id in c_df['carrier_id'].unique():
        try:
            # Initialize parameters used for probelm setting
            veh_capacity = 0
            fleet_type = 'homo'
            num_veh = 0
            fleet_miz = False

            # Depot location
            depot_loc = c_df.loc[c_df['carrier_id'] == carr_id]['depot_zone'].values[0]

            # To simplify the problem, look at a small problem with same carrier and same commodity id
            df_prob = p_df[(p_df['carrier_id'] == carr_id)]
            df_prob = df_prob.dropna()
            f_prob = vc_df[vc_df['carrier_id'] == carr_id]
            f_prob = f_prob.dropna()
            c_prob = c_df[c_df['carrier_id'] == carr_id]
            c_prob = c_prob.dropna()
            vc_prob = vc_df[vc_df['carrier_id']== carr_id]
            vc_prob = vc_prob.dropna()

            if len(df_prob) == 0:
                print('Could not solve problem for carrier ', carr_id, ': NO PAYLOAD INFO')
                print('\n')
                error_list.append([carr_id, 'NO PAYLOAD INFO'])

            elif len(f_prob) == 0 or len(vc_prob) == 0:
                print('Could not solve problem for carrier ', carr_id, ': NO VEHICLE TYPE INFO')
                print('\n')
                error_list.append([carr_id, 'NO VEHICLE TYPE INFO'])

            elif len(c_prob) == 0:
                print('Could not solve problem for carrier ', carr_id, ': NO CARRIER INFO')
                print('\n')
                error_list.append([carr_id, 'NO CARRIER INFO'])

            else:

                md_start_id = int(vc_prob['md_start_id'].values[0])
                hd_start_id = int(vc_prob['hd_start_id'].values[0])
                prob_type = str(df_prob.iloc[0]['job'])
                
            # for now pickup and delivery works
            # TO DO: work on pickup_delivery  # Removed prob_type != 'pickup_delivery'and
            # if len(df_prob)> 0 and len(f_prob)> 0 and len(c_prob)> 0 and len(vc_prob)>0:
                print('Solvign problem for carrier ', carr_id, ' with type', prob_type)
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
                    if carr_id == 7252990.0:
                        print('time: ', data['time_windows'])
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
                                   payload_df, prob_type)
                    print('\n')

                else:
                    print('Could not find a solution for carrier: ', carr_id)
                    error_list.append([carr_id, 'NO SOLUTION'])
                    print('\n')


        except Exception as e:
            print('Could not solve problem for carrier: ', carr_id, ': ', e)
            error_list.append([carr_id, e])
            print('\n')

    run_time = time() - b_time
    print('Time for the run: ', run_time)
    print('\n')

    # Saving the created data frames
    if "B2B" in args.payload_file:
        ship_type="B2B"
    elif "B2C" in args.payload_file:
        ship_type="B2C"

    #  Saving the carrier ids with errors
    with open("../Sim_outputs/error.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(error_list)

    tour_df.to_csv("../Sim_outputs/Tour_plan/%s_freight_tours.csv" %ship_type, index=False)
    carrier_df.to_csv("../Sim_outputs/Tour_plan/%s_carrier.csv" %ship_type, index=False)
    payload_df.to_csv("../Sim_outputs/Tour_plan/%s_payload.csv" %ship_type, index=False)

    print ('Completed saving tour-plan files for %s' %ship_type, '\n')

    dir_geo='../Sim_inputs/Geo_data/'
    polygon_CBG = gp.read_file(dir_geo+'sfbay_freight.geojson') # include polygon for all the mesozones in the US
    ex_zone_match= pd.read_csv(dir_geo+"External_Zones_Mapping.csv") # relationship between external zones and boundary zones
    if (ship_type =='B2B') :
        print ("Starting external zone processing for B2B")
        tour_df,carrier_df,payload_df= external_zone (tour_df,carrier_df,payload_df,ex_zone_match,tt_df, dist_df, CBGzone_df)

    print ("Assigning x_y coordinate into depots and delivery locations")
    tour_df_xy,carrier_df_xy,payload_df_xy=random_loc (tour_df,carrier_df,payload_df, polygon_CBG)
    tour_df.to_csv("../Sim_outputs/Tour_plan/%s_freight_tours_xy.csv" %ship_type, index=False)
    carrier_df.to_csv("../Sim_outputs/Tour_plan/%s_carrier_xy.csv" %ship_type, index=False)
    payload_df.to_csv("../Sim_outputs/Tour_plan/%s_payload_xy.csv" %ship_type, index=False)
    print ("Complete saving tour-plan with xy coordinate for %s" %ship_type)



if __name__ == "__main__":
    main()
