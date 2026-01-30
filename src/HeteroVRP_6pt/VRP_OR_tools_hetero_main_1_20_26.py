# Authors: Juliette Ugirumurera and Kyungsoo Jeong

"""Run to generate vehicles' tour plans considering timing and load constraints.

"""
# %%
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
import traceback
import sys

from hetero_ini_vrp_b import solve_initial_vrp, cal_total_cost
from insert_ch_stn_6pt_1_13 import  insert_charging_stations, insert_charging_stations_pd, find_accessible_charging_station, filter_pd_pairs_for_ev
from VNS_6pt import variable_neighborhood_search
from VNS_6pt_pd import variable_neighborhood_search_pd
from hetero_ice_to_ev_final import find_best_move
from hetero_ice_to_ev_final_pd import find_best_move_pd
from EV_DV_swap import get_ch_st_IDS, remove_cs, swap_veh_type_EtoD, swap_veh_type_DtoE
from utilities_b import calculate_route_cost, calculate_total_cost, is_route_feasible

# %%
# Global Variables


run_time  = 120

#%%
def tt_cal(org_meso, dest_meso, org_geoID, dest_geoID, sel_tt, sel_dist):
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
        travel_time = sel_tt['TIME_minutes'].to_numpy()[(sel_tt['origin'].to_numpy() == org_geoID)
                                              &(sel_tt['destination'].to_numpy() == dest_geoID)].item()
    except:
        try:
            dist = sel_dist['dist'].to_numpy()[(sel_dist['Origin'].to_numpy() == org_meso)
                                              &(sel_dist['Destination'].to_numpy() == dest_meso)].item()
            travel_time= dist/40*60
        except:
            travel_time = 60*1
    return travel_time

#%%
def get_geoId(zone, CBGzone_df):
    """Retreives the geo ID of a given mesozone.

    Give mesozone id, retreives the corresponding geo id from dataframe that
     maps mesozone to geo ids to mesozone ids.

    Args:
        zone: mesozone id
        CBGzone_df: dataframe that maps mesozones to geo ids

    Returns:
        org_geoID: returns the corresponding geo id. If mesozone was not found, org_geoID is
        set to -1.
    """
    try:
        org_geoID= int(CBGzone_df[CBGzone_df['MESOZONE']==zone].GEOID.values[0])
    except:
        org_geoID = -1
    return int(org_geoID)

#%%
def create_data_model(df_prob,  depot_loc, prob_type, v_df, f_prob, c_prob, carrier_id,
                     CBGzone_df, tt_df, dist_df, veh, commodity, ship_index, path_stops, EV_savings_pct, fixed_cost, cost_per_unit_time, EV_battery_capacity, soc_threshold):
  
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
        # print("df_prob:")
        # print(df_prob)
        # print("prob_type:", prob_type)
        data = {}
        data['soc_threshold'] = soc_threshold  # state of charge threshold in percentage

        data['scenario'] = ['S3']
        data['X'] = [100]
        data['veh_pwrtrn_types'] = ['D', 'G', 'BE', 'H2', 'PD', 'PG'] #two powertrin types considered, diesel and electric
        data['veh_ids'] = [0, 1, 2, 3, 4, 5]  # vehicle type ids corresponding to veh_pwrtrn_types
        data['veh_pt_and_ids'] = {}
        for i in range(len(data['veh_pwrtrn_types'])):
            data['veh_pt_and_ids'][data['veh_pwrtrn_types'][i]] = data['veh_ids'][i]
        # print("veh_pt_and_ids:", data['veh_pt_and_ids'])
        data['fixed_cost'] = fixed_cost #

        data['cost_per_unit_time'] = cost_per_unit_time # first value - cost per minute of D and second value - cost per minute of EV
        # print('fixed cost:',data['fixed_cost'] )
        # print('variable cost:',data['cost_per_unit_time'] )
        # print("variable cost:",data['cost_per_unit_time'] )
        data['time_matrix'] = []
        data['loc_zones'] = []    # zones corresponding to locations
        data['payload_ids'] = []
        data['stop_durations'] = [] # regular service time
        data['EV_time_savings'] = [] # savings in service time when electric vehicles are used
        data['prob_type'] = prob_type

        if prob_type == 'pickup_delivery':
            data['pickups_deliveries']=[]

        time_l = []
        # print("EV_savings in data model creation: ", EV_savings_pct)
        
        # Adding time 0 for the depot and location for depot
        time_l.append(0)
        data['loc_zones'].append(depot_loc)
        depot_service_time = int(c_prob.loc[c_prob['carrier_id'] == carrier_id]['depot_time_before'].values[0])
        data['stop_durations'].append(depot_service_time)
        data['EV_time_savings'].append(0) #assume depot service time does not change wrt the type of power train types
        data['time_windows'] = []
        # Add time window for depot
        data['time_windows'].append((int(c_prob.loc[c_prob['carrier_id'] == carrier_id]['depot_lower'].values[0]),
                                    int(c_prob.loc[c_prob['carrier_id'] == carrier_id]['depot_upper'].values[0])))
        data['demands'] = []
        if commodity != 2 and ship_index =='internal':
            data['stops'] = []  # parameter to keep track of number of stops per node
            data['stops'].append(0) # No stop counted for depot

            data['vehicle_max_stops'] = []
            data['vehicle_slack_stops'] = []

        # if problem is delivery, we start with full laod at depot
        # if problem is pickup, we start with empty load
        data['demands'].append(0) # Adding demand for depot

        data['geo_ids'] = []
        data['geo_ids'].append(get_geoId(depot_loc, CBGzone_df))

        index = 1
        # print("df_prob")
        # print(df_prob)
        # print("payload_ids in create_data_model:", df_prob['payload_id'].unique())
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
                if commodity != 2 and ship_index =='internal': data['stops'].append(1)  # stop for this demand location

                service_time = int(df_prob.loc[df_prob['payload_id'] == i]['del_stop_duration'].values[0])
                data['stop_durations'].append(copy(service_time))
                # print("service_time for payload_id ", i, " is ", service_time)
                service_time_1 = int(service_time * float(EV_savings_pct))


                # service_time_1 = int(service_time * EV_savings_pct )
                data['EV_time_savings'].append(copy(service_time_1))
                # print("EV_time_savings for payload_id ", i, " is ", service_time_1)


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
                if commodity != 2 and ship_index =='internal': data['stops'].append(1)

                service_time = int(df_prob.loc[df_prob['payload_id'] == i]['pu_stop_duration'].values[0])
                data['stop_durations'].append(copy(service_time))

                service_time_1 = int(service_time * float(EV_savings_pct))

                
                data['EV_time_savings'].append(copy(service_time_1))

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
                if commodity != 2 and ship_index =='internal':
                    data['stops'].append(1)  # Add stop for pickup
                    data['stops'].append(1)  # Add stop for delivery

                # Add pickup service time and delivery service time
                service_time = int(df_prob.loc[df_prob['payload_id'] == i]['pu_stop_duration'].values[0])
                data['stop_durations'].append(copy(service_time))
                service_time_1 = int(service_time * float(EV_savings_pct))
                data['EV_time_savings'].append(copy(service_time_1))

                service_time = int(df_prob.loc[df_prob['payload_id'] == i]['del_stop_duration'].values[0])
                data['stop_durations'].append(copy(service_time))
                service_time_1 = int(service_time * float(EV_savings_pct))
                data['EV_time_savings'].append(copy(service_time_1))

                # Assuming that if a carrier has pickup_delivery jobs it only has that
                data['pickups_deliveries'].append([index, index+1])
                index += 2
        data['customer_nodes'] = list(range(1, len(data['loc_zones'])))
        # print("customer nodes:", data['customer_nodes'])
        # data['customer_nodes'] = list(range(1, len(df_prob['payload_id'].unique()) + 1))


        num_stations = 0
        #adding charging stations as nodes with zero demand and zero service time
        index = 1
        for i in df_prob['payload_id'].unique():
            if prob_type == 'delivery':
                temp_zone = (int(df_prob.loc[df_prob['payload_id'] == i]['del_zone'].values[0])) # find zone
                data['loc_zones'].append(copy(temp_zone))     # saving zone
                data['geo_ids'].append(get_geoId(temp_zone, CBGzone_df))

                # Adding time window
                data['time_windows'].append((0, 50000))

                data['payload_ids'].append(copy(i))

                demand = math.ceil(0)
                data['demands'].append(copy(demand))
                
                data['stop_durations'].append(0)

                data['EV_time_savings'].append(0)
                num_stations += 1

            elif prob_type =='pickup':
                temp_zone = (int(df_prob.loc[df_prob['payload_id'] == i]['del_zone'].values[0])) # find zone
                data['loc_zones'].append(copy(temp_zone))     # saving zone
                data['geo_ids'].append(get_geoId(temp_zone, CBGzone_df))

                # Adding time window
                data['time_windows'].append((0, 50000))

                data['payload_ids'].append(copy(i))

                demand = math.ceil(0)
                data['demands'].append(copy(demand))
                
                data['stop_durations'].append(0)

                data['EV_time_savings'].append(0)
                num_stations += 1

            elif prob_type == 'pickup_delivery':
                temp_zone_d = int(df_prob.loc[df_prob['payload_id'] == i]['del_zone'].values[0]) # find delivery zone
                temp_zone_p = int(df_prob.loc[df_prob['payload_id'] == i]['pu_zone'].values[0]) # find pickup zone
                # Adding pickup and delivery zone to data frame
                data['loc_zones'].append(copy(temp_zone_p))
                data['loc_zones'].append(copy(temp_zone_d))
                data['geo_ids'].append(get_geoId(temp_zone_p, CBGzone_df))
                data['geo_ids'].append(get_geoId(temp_zone_d, CBGzone_df))

                # Adding time pickup and delivery windows
                data['time_windows'].append((0, 50000))
                data['time_windows'].append((0, 50000))


                data['payload_ids'].append(copy(i))
                data['payload_ids'].append(copy(i))

                demand = math.ceil(0)
                data['demands'].append(copy(demand))
                data['demands'].append(copy(demand))


                # Add pickup service time and delivery service time
                
                data['stop_durations'].append(0)

                data['EV_time_savings'].append(0)

                data['stop_durations'].append(0)

                data['EV_time_savings'].append(0)

                # Assuming that if a carrier has pickup_delivery jobs it only has that
                # data['pickups_deliveries'].append([index, index+1])
                index += 2
                num_stations += 2
    
  

        # After gathering demand by location, change demand of depot to full load at the depot
        #TODO: this need to be double checked for a problem where one vehile is not enough to deliver everything
        # Below did not work if more than 1 vehicle is needed to handle depot demand
        # print("dist_df")
        # print(dist_df)
        # print("tt_df")
        # print(len(tt_df))

        b_timing = time()

        sel_tt= tt_df[(tt_df['origin'].isin(data['geo_ids'])) &
                        (tt_df['destination'].isin(data['geo_ids']))]

       
        sel_dist = dist_df[(dist_df['Origin'].isin(data['loc_zones'])) &
                        (dist_df['Destination'].isin(data['loc_zones']))]
     
        max_tt = 0
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
                    if travel_time > max_tt: max_tt = copy(travel_time)

            data['time_matrix'].append(copy(time_l))


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
        #veh_index= veh.split("_")[0]+"_"+veh.split("_")[1]
        data['num_vehicles'] = 0
        data['num_Dt'] = 0
        data['num_Gt'] = 0
        data['num_BEt'] = 0
        data['num_H2t'] = 0
        data['num_PDt'] = 0
        data['num_PGt'] = 0
        #for pw_tr in ["_D", "_E"]:
        for pw_tr in data['veh_pwrtrn_types']: 
            # print('pw_tr: ', pw_tr)
            
            veh_index = veh + '_' + pw_tr 
            # print("veh_index: ", veh_index)
            # print(f_prob)
        
            veh_id= int(f_prob[veh_index+"_start_id"].values[0])
            # print("veh_id: ", veh_id)
 
            veh_capacity =int(v_df[v_df['veh_type_id_2'] == veh]['payload_capacity_weight'].values[0])
         
            for i in range(0, int(f_prob[veh_index].values[0])):
                
                data['vehicle_capacities'].append(int(veh_capacity))
                data['vehicle_ids'].append(veh_id)
                data['vehicle_types'].append(veh + '_' + pw_tr)
                veh_id += 1
               

                if commodity != 2 and ship_index =='internal':
                        prob = random.uniform(0, 1)
                        temp = stop_df[stop_df.Cum_Prob >= prob].reset_index()
                        max_stops = temp.loc[0,'Num_Trips_per_Tour']
                        slack_stops = temp.loc[len(temp)-1, 'Num_Trips_per_Tour']
                        data['vehicle_max_stops'].append(int(max_stops)) # [6, 5, 6, 4, 8, 9, 6, 4]
                        if len(data['vehicle_max_stops']) > 0:
                            max_stops_all = max(data['vehicle_max_stops'])
                            data['vehicle_max_stops'] = [max_stops_all] * len(data['vehicle_max_stops'])
                        data['vehicle_slack_stops'].append(int(slack_stops))
            
            num_veh = int(f_prob[veh_index].values[0])
            # print("num+veh", num_veh)
            data['num_vehicles'] += num_veh
            if pw_tr == "D":
                data['num_Dt'] += num_veh
            elif pw_tr == "G":
                data['num_Gt'] += num_veh
            elif pw_tr == "BE":
                data['num_BEt'] += num_veh
            elif pw_tr == "H2":
                data['num_H2t'] += num_veh
            elif pw_tr == "PD":
                data['num_PDt'] += num_veh
            elif pw_tr == "PG":
                data['num_PGt'] += num_veh


                
        

        # Initialize an empty list to store vehicle types as binary values: 0 for diesel vehicles, 1 for electric vehicles.
        data['vehicle_types_bin'] = []   
        for _ in range(int(data['num_Dt'])):
            data['vehicle_types_bin'].append(0)
        for _ in range(int(data['num_Gt'])):
            data['vehicle_types_bin'].append(0)
        for _ in range(int(data['num_BEt'])):
            data['vehicle_types_bin'].append(1)
        for _ in range(int(data['num_H2t'])):
            data['vehicle_types_bin'].append(1)
        for _ in range(int(data['num_PDt'])):
            data['vehicle_types_bin'].append(1)
        for _ in range(int(data['num_PGt'])):
            data['vehicle_types_bin'].append(1)
        
        data['vehicle_types_id'] = []   
        for _ in range(int(data['num_Dt'])):
            data['vehicle_types_id'].append(0)
        for _ in range(int(data['num_Gt'])):
            data['vehicle_types_id'].append(1)
        for _ in range(int(data['num_BEt'])):
            data['vehicle_types_id'].append(2)
        for _ in range(int(data['num_H2t'])):
            data['vehicle_types_id'].append(3)
        for _ in range(int(data['num_PDt'])):
            data['vehicle_types_id'].append(4)
        for _ in range(int(data['num_PGt'])):
            data['vehicle_types_id'].append(5)
 
        # print( "total num vehicles:", data['num_vehicles'])
        # print( "num diesel vehicles:", data['num_Dt'])
        # print( "num electric vehicle:", data['num_Et'])

    
        data['start'] = [0]* data['num_vehicles']
        data['end'] = [0]* data['num_vehicles']
        # #print("veh_capacity: ", veh_capacity, " num_veh: ", data['num_vehicles'])
        
        data['depot'] = 0
        # data['customer_nodes'] = list(range(1, len(data['demands']) + 1))
        data['charging_stations'] = list(range(len(data['customer_nodes']) + 1, len(data['customer_nodes']) + 1 + num_stations))
        data['distance_matrix'] = data['time_matrix']
  
        data['service_times'] = data['stop_durations']
        data['battery_capacities'] = [
        EV_battery_capacity if vehicle_type == 1 else None for vehicle_type in data['vehicle_types_bin']]
        data['charging_rate'] = 1


        #print("veh_factors", data['vehicle_factors'])

        # #print(data)
        # Saving dictionary for testing purposes
        # with open('test_data/b2b_pickup_delivery_internal.pickle', 'wb') as handle:
        #     pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

    except Exception as e:
        traceback.print_exc()
        print('Could not build data dictionary for: ', carrier_id, 'and vehicle ', veh , ' : ', e)
        return {}

    return data

#%%

def input_files_processing(travel_file, dist_file, CBGzone_file, carrier_file, payload_file, vehicleType_file, powertrain_types):
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
        powertrain_types = powertrain_types
        # print("powertrain_types:", powertrain_types)
        # KJ: read travel time, distance, zonal file as inputs  # Slow step
        tt_df = pd.read_csv(travel_file, compression='gzip', header=0, sep=',', quotechar='"', on_bad_lines='skip')
        dist_df = pd.read_csv(dist_file, compression='gzip', header=0, sep=',', quotechar='"', on_bad_lines='skip')  # Slow step
        dist_df.columns=['Origin','Destination','dist']
        CBGzone_df = gp.read_file(CBGzone_file)
        # print("carrier_file", carrier_file)
        # We need to know the depot using the carrier file
        c_df = pd.read_csv(carrier_file)
        # print("c_df2")
        # print(c_df)
        c_df = c_df.dropna(axis=1, how='all')   # Removing all nan
        #c_df = c_df[c_df["num_veh_type_1"]>0]  # Removing carriers don't have vehicles (Temporary solution)- need to check Shipment code

        # reading payload definition
        p_df = pd.read_csv(payload_file)
        p_df = p_df.dropna(axis=1, how='all')   # Removing all nan

        # Removing nans
        c_df = c_df.fillna(0); # Fill all nan with zeros

        # Removing nans
        p_df['carrier_id'] = p_df['carrier_id'].astype(str)
        p_df['sequence_id'] = np.nan
        p_df['tourId'] = np.nan
        p_df['pu_arrival_time'] = np.nan
        p_df['del_arrival_time'] = np.nan
        p_df = p_df.fillna(int(0))

        # Adding in additional colums for vehicle tours
        # Changing tour id and sequence id into ints
        p_df['tourId'] = p_df['tourId'].astype(int)
        p_df['sequence_id'] = p_df['sequence_id'].astype(int)

        # Reading in vehicle information
        v_df = pd.read_csv(vehicleType_file)
        # print("v_df")
        # print(v_df)
        v_df = v_df.dropna(axis=1, how='all')   # Removing all nan
            # print("hi")
            # print("p_df")
            # print(p_df)
        ################ KJ added for veh_tech
        veh_list_temp = p_df["veh_type_2"].unique() #md_D or md_E md_E_bh
        # print("veh_list_temp:", veh_list_temp)

        """NEW FOR FOUR Electric vehicle types: BE, H2, PD, PG. modify the c_df to consider the ev_type columns"""
        c_df_new = c_df.copy()
        # Map full EV type to short code
        ev_code = { 'Battery Electric': 'BE', 'H2 Fuel Cell': 'H2',  'PHEV Diesel': 'PD',  'PHEV Gasoline': 'PG'}
        veh_types = veh_list_temp
        # Precompute code per row (e.g., 'BE', 'H2', 'PD', 'PG')
        ev_col = c_df_new['ev_type'].map(ev_code)
        # Create a working copy to accumulate results
        new_df = c_df_new.drop(columns=[c for c in c_df_new.columns if c.endswith('_E')], errors='ignore').copy()

        # For each vehicle type, create the new EV-type columns
        for vt in veh_types:
            e_col = f'{vt}_E'
            # Get the source column if it exists, otherwise fill zeros
            base_vals = c_df_new[e_col] if e_col in c_df_new.columns else 0

            # Create columns for all EV types
            for code in ['BE', 'H2', 'PD', 'PG']:
                new_col = f'{vt}_{code}'
                new_df[new_col] = np.where(ev_col == code, base_vals, 0)

        # dfc_df_new now contains original data + new columns, with _E columns removed
        c_df_new = new_df
        # print("c_df_new")
        # print(c_df_new)

        veh_list =[]
        for vtype in veh_list_temp:
            for ptype in powertrain_types:
            
                veh_type_temp =  vtype + '_' +  ptype
                veh_list.append(veh_type_temp)
        # print ("veh_list_2=", veh_list)
        veh_list = list(dict.fromkeys(veh_list))
        # print ("veh_list_3=", veh_list)
        # Create vehicle sequence vehicle ID
        vc_df = pd.DataFrame()
        # print("vc_df1")
        # print(vc_df)
        vc_df['carrier_id']=c_df_new['carrier_id']
        # print("vc_df2")
        # print(vc_df)

        for key in veh_list:
            # print("key:", key)

            if key not in c_df_new.columns:
                c_df_new[key]=0
            
            vc_df[key]=c_df_new[key]
            # print("vc_df")
            # print(vc_df)
    
            vc_df[key+'_start_id']=np.nan
  
        vc_df = vc_df.fillna(int(0))
     
        vc_df = vc_df.reset_index()
        # print("vc_df")
        # print(vc_df)
   
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
        # print("final_vc_df")
        # print(vc_df)
        # print("printing vc_df was successful")
        #saving the vc_df to check 
        vc_df.to_csv('vc_df.csv', index=False)
        # print("Input files processed successfully.")
        return tt_df, dist_df, CBGzone_df, c_df, p_df, v_df, vc_df
    except Exception as e:
        traceback.print_exc()
        prefix = ''
        if 'gzipped' in str(e): prefix = 'Travel time file'
        # print('Could not parse input files: exception: ', prefix, e)

        return None

# TODO: ask Kyungsoo to add comments here
def random_points_in_polygon(polygon):
    temp = polygon.bounds
    finished= False
    while not finished:
        point = Point(random.uniform(temp.minx.values[0], temp.maxx.values[0]), random.uniform(temp.miny, temp.maxy.values[0]))
        finished = polygon.contains(point).values[0]
    return point

# TODO: ask Kyungsoo to add comments here
def random_loc (t_df,c_df,p_df,SFBay_CBG):
    c_df['depot_zone_x']=0
    c_df['depot_zone_y']=0
    c_df =c_df.sort_values(by=['carrierId']).reset_index(drop=True)
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
    t_df=t_df.merge(c_df[['tourId','depot_zone_x','depot_zone_y']], right_on='tourId', left_on='tourId', how='left')
    t_df=t_df.rename({'depot_zone_x':'departureLocation_x',
                     'depot_zone_y':'departureLocation_y'}, axis=1)

    p_df['locationZone_x']=0.0
    p_df['locationZone_y']=0.0
    for i in range(0,p_df.shape[0]):
        if "d" in str(p_df.loc[i,"payloadId"]):
            p_df.loc[i,['locationZone_x','locationZone_y']]=c_df.loc[c_df["tourId"]==p_df.loc[i,"tourId"], ['depot_zone_x','depot_zone_y']]
        else:
            point=random_points_in_polygon(SFBay_CBG.geometry[SFBay_CBG.MESOZONE==p_df['locationZone'][i]])
            p_df.loc[i,'locationZone_x']=point.x
            p_df.loc[i,'locationZone_y']=point.y

    return c_df, t_df, p_df

#%%



def build_node_to_payload_id(data):
    """
    Build a mapping from node index to payload_id using the data dictionary.
    Assumes that:
      - depot is node 0 (not a customer)
      - customer nodes are 1..N and correspond to data['payload_ids']
    """
    mapping = {}
    # Map customer nodes to payload_ids
    if 'customer_nodes' in data and 'payload_ids' in data:
        for idx, node in enumerate(data['customer_nodes']):
            # payload_ids may be shorter if there are charging stations or other nodes
            if idx < len(data['payload_ids']):
                mapping[node] = data['payload_ids'][idx]
    return mapping

def build_node_to_demand(data):
    """
    Build a mapping from node index to demand using the data dictionary.
    Returns a dict: {node_index: demand}
    """
    if 'demands' in data:
        return {i: demand for i, demand in enumerate(data['demands'])}
    return {}


# def get_payload_id(node):
#     return node_to_payload_id.get(node, node)

def normalize_route(route, depot):
    # ensure route ends at depot for clean traversal
    return route if route and route[-1] == depot else route + [depot]

def simulate_arrivals(route, data, vtype_bin):
    """
    route: list of node ids (e.g., [0, 1, 2, 3, 0])
    vtype_bin: 1 for EV, 0 for ICE (applies EV_time_savings)
    returns: list of (node, arrival_time, seq)
    """
    depot = data['depot']
    seq =0
    current_time = 0
    out = []
    out.append((depot, current_time, seq))
    # start time at depot earliest TW if present, else 0
    if 'time_windows' in data and len(data['time_windows']) > depot:
        current_time = data['time_windows'][depot][0]
    else:
        current_time = 0
    r = normalize_route(route, depot)
    for a, b in zip(r,  r[1:] + [r[0]]):
        # print(a, b)
        # travel
        current_time += int(data['time_matrix'][a][b])

        # on arrival at b (skip depot rows)
        if b != depot:
            seq += 1
            # wait to satisfy earliest time window
            if 'time_windows' in data and len(data['time_windows']) > b:
                early, late = data['time_windows'][b]
                if current_time < early:
                    current_time = early
            out.append((b, current_time, seq))

            # service time (reduced for EV if applicable)
            base_service = data['stop_durations'][b]
            ev_save = data['EV_time_savings'][b] * vtype_bin
            service = max(0, base_service - ev_save)
            current_time += service
    out.append((depot, current_time, seq + 1))
    return out

#to print and save the routes as rows in the required format
def routes_to_rows( count_num, ship_type, df_prob, c_prob, EV_routes, ICE_routes, data, carrier_id, tourId, customer_nodes=None):

    # print("calling routes_to_rows for carrier ", carrier_id)
    node_to_payload_id = build_node_to_payload_id(data)

    node_to_demand     = build_node_to_demand(data)


    payload_rows = []
    tour_rows = []
    carrier_rows = []
    depot = data['depot']

    def get_req_type(node, df_prob):
        payload_id = node_to_payload_id.get(node, node)
        match = df_prob.loc[df_prob['payload_id'] == payload_id, 'job']
        job_type = match.iloc[0] if len(match) > 0 else None

        if job_type == 'delivery':
            return 1
        elif job_type == 'pickup':
            return 2
        elif job_type == 'pickup_delivery':
            return 3
        else:
            return 3

    def add_routes(routes, vlabel, vbin):
        """
        routes      : list of routes (each route is list of node IDs like [0, 5, 7, 0])
        vlabel      : "EV" or "ICE" (used for vehicleTypeId and veh_type column)
        vbin        : 1 for EV (use EV time savings), 0 for ICE
        """
        nonlocal tourId

        # use enumerate so we also get a stable per-vtype vehicleId
        for veh_idx, r in enumerate(routes):
           
            if len(r) <= 2:
                # ignore trivial routes [0,0] or depot only
                continue

            # total load carried out of depot for this tour
            total_load = sum(node_to_demand.get(n, 0) for n in r if n != depot)
            current_load = total_load
            

            tourId += 1  # new tour
            arrivals = simulate_arrivals(r, data, vbin)  # [(node, arrival_time, seq), ...]
            n_arr = len(arrivals)

            # create tour_row once at first depot, and carrier_row once per tour
            tour_row = None

            # precompute depot_zone fields from c_prob (carrier file)
            depot_zone    = str(data['loc_zones'][depot]) if 'loc_zones' in data else None
            depot_zone_x  = c_prob.loc[c_prob['carrier_id'] == carrier_id, 'c_x'].values[0]
            depot_zone_y  = c_prob.loc[c_prob['carrier_id'] == carrier_id, 'c_y'].values[0]
            true_depot_zone = c_prob.loc[c_prob['carrier_id'] == carrier_id, 'true_depot_zone'].values[0]

            for i, (node, at, seq) in enumerate(arrivals):
                
                # optionally skip non-customers for payload rows (but still include depot rows)
                if customer_nodes is not None and (node != depot) and (node not in customer_nodes):
                    continue

                # defaults for payload_row
                
                weightInlb = 0
                cummulativeWeightInlb = 0
                locationZone = None
                arrivalTimeWindowInSec_lower = None
                arrivalTimeWindowInSec_upper = None
                payloadType_val = None
                req_type = None
                operationDurationInSec = 0
                locationZone_x = None
                locationZone_y = None
                true_locationZone = None
                BuyerNAICS = "NA"
                SellerNAICS = "NA"
                truck_mode = "NA"

                # -------------------------------------------------
                # Start depot (first record in this tour)
                # -------------------------------------------------
                if node == depot and i == 0:
                    weightInlb = total_load
                    
                    cummulativeWeightInlb = total_load
                    custom_payload_id = f"{count_num}_d{ship_type}{tourId}"

                    # depot zone geometry/time window info
                    locationZone = depot_zone
                    if 'time_windows' in data:
                        arrivalTimeWindowInSec_lower = int(data['time_windows'][depot][0] * 60)
                        arrivalTimeWindowInSec_upper = int(data['time_windows'][depot][1] * 60)

                    # infer payloadType from the next stop (best guess)
                    if n_arr > 1:
                        next_node = arrivals[1][0]
                    else:
                        next_node = node
                    pid_next = node_to_payload_id.get(next_node, next_node)
                    match_comm = df_prob.loc[df_prob['payload_id'] == pid_next, 'commodity']
                    payloadType_val = int(match_comm.iloc[0]) if len(match_comm) > 0 else -1
                    req_type = get_req_type(next_node, df_prob)

                    operationDurationInSec = int(data['service_times'][node] * 60)

                    # depot coords
                    locationZone_x = depot_zone_x
                    locationZone_y = depot_zone_y
                    true_locationZone = true_depot_zone

                    # build tour_row ONCE per tour using departure info
                    # departureTimeInSec = depart depot time (arrival + service)
                    tour_row = {
                        "tourId": tourId,
                        "departureTimeInSec": int(at * 60) + operationDurationInSec,
                        "departureLocation_zone": depot_zone,
                        "departureLocation_x": depot_zone_x,
                        "departureLocation_y": depot_zone_y,
                        "true_depot_zone": true_depot_zone,
                    }

                # -------------------------------------------------
                # End depot (last record in this tour)
                # -------------------------------------------------
                elif node == depot and i == n_arr - 1:
                    weightInlb = 0
                    cummulativeWeightInlb = 0
                    custom_payload_id = f"{count_num}_d{ship_type}{tourId}_"

                    locationZone = depot_zone
                    if 'time_windows' in data:
                        arrivalTimeWindowInSec_lower = int(data['time_windows'][depot][0] * 60)
                        arrivalTimeWindowInSec_upper = int(data['time_windows'][depot][1] * 60)

                    # infer from previous stop
                    if n_arr > 1:
                        prev_node = arrivals[-2][0]
                    else:
                        prev_node = node
                    pid_prev = node_to_payload_id.get(prev_node, prev_node)
                    match_comm = df_prob.loc[df_prob['payload_id'] == pid_prev, 'commodity']
                    payloadType_val = int(match_comm.iloc[0]) if len(match_comm) > 0 else -1
                    req_type = get_req_type(prev_node, df_prob)

                    operationDurationInSec = int(data['service_times'][node] * 60)

                    locationZone_x = depot_zone_x
                    locationZone_y = depot_zone_y
                    true_locationZone = true_depot_zone

                # -------------------------------------------------
                # Customer stop
                # -------------------------------------------------
                else:
                    d = node_to_demand.get(node, 0)
                    req_type = get_req_type(node, df_prob)
                   
                    if req_type == 1:  # delivery
                        weightInlb = -d
                    if req_type == 3:  # pickup and delivery
                        weightInlb = d
                    current_load += weightInlb
                   
                    cummulativeWeightInlb = current_load
                    custom_payload_id = node_to_payload_id.get(node, node)

                    # location and time windows for this customer
                    locationZone = data['loc_zones'][node] if 'loc_zones' in data else None
                    if 'time_windows' in data:
                        arrivalTimeWindowInSec_lower = int(data['time_windows'][node][0] * 60)
                        arrivalTimeWindowInSec_upper = int(data['time_windows'][node][1] * 60)

                    pid = node_to_payload_id.get(node, node)

                    # payloadType -> commodity
                    match_comm = df_prob.loc[df_prob['payload_id'] == pid, 'commodity']
                    payloadType_val = int(match_comm.iloc[0]) if len(match_comm) > 0 else -1

                    req_type = get_req_type(node, df_prob)

                    # service time (EV may reduce)
                    if vbin == 1:
                        stime = data['service_times'][node] - data['EV_time_savings'][node]
                    else:
                        stime = data['service_times'][node]
                    operationDurationInSec = int(stime * 60)

                    # geometry/business attrs from df_prob for this payload
                    match_row = df_prob.loc[df_prob['payload_id'] == pid]
                    if len(match_row) > 0:
                        locationZone_x    = match_row['del_x'].values[0]
                        locationZone_y    = match_row['del_y'].values[0]
                        true_locationZone = match_row['true_del_zone'].values[0]
                        BuyerNAICS        = match_row['BuyerNAICS'].values[0]
                        SellerNAICS       = match_row['SellerNAICS'].values[0]
                        truck_mode        = match_row['truck_mode'].values[0]
                # # -----------------------------
                # # Build payload_row
                # # -----------------------------
                # base_payload_id = node_to_payload_id.get(node, node)

                # # depot rows get special payloadId format: count_num + "d" + ship_type + tourId
                # if node == depot:
                #     custom_payload_id = f"{count_num}_d{ship_type}{tourId}"
                #     if i != 0:
                #         custom_payload_id = f"{count_num}_d{ship_type}{tourId}_"
                # else:
                #     custom_payload_id = base_payload_id

                # build per-stop record for payload_df
                payload_row = {
                    "payloadId": custom_payload_id,
                    "sequenceRank": seq,
                    "tourId": tourId,
                    "payloadType": payloadType_val,
                    "weightInlb": weightInlb,
                    "cummulativeWeightInlb": cummulativeWeightInlb,
                    "requestType": req_type,
                    "locationZone": locationZone,
                    "estimatedTimeOfArrivalInSec": int(at * 60),
                    "arrivalTimeWindowInSec_lower": arrivalTimeWindowInSec_lower,
                    "arrivalTimeWindowInSec_upper": arrivalTimeWindowInSec_upper,
                    "operationDurationInSec": operationDurationInSec,
                    "locationZone_x": locationZone_x,
                    "locationZone_y": locationZone_y,
                    "true_locationZone": true_locationZone,
                    "BuyerNAICS": BuyerNAICS,
                    "SellerNAICS": SellerNAICS,
                    "truck_mode": truck_mode,

                }
                payload_rows.append(payload_row)

            # after finishing this route (one tour):
            # 1. add tour_row (depot-level tour metadata)
            if tour_row is not None:
                tour_rows.append(tour_row)

            # 2. add carrier_row (carrier/vehicle metadata for this tour)
            carrier_row = {
                "carrierId": carrier_id,
                "tourId": tourId,
                "vehicleId": f"{carrier_id}_{veh_idx}",          
                "vehicleTypeId": vlabel,       # "EV" or "ICE"
                "depot_zone": depot_zone,      # text/zone id
                "depot_zone_x": depot_zone_x,
                "depot_zone_y": depot_zone_y,
                "true_depot_zone": true_depot_zone,
            }
            carrier_rows.append(carrier_row)

    # run both fleets
    add_routes(EV_routes,  "EV",  1)
    add_routes(ICE_routes, "ICE", 0)

    # return all three
    return payload_rows, tour_rows, carrier_rows



def main(args=None):
    # print ("at main function")
    """Main function.

    Takes input files names from console specifing the parameters of the vehicle routing problem.

    Args:
        -cy or --county_number: the county number in the scenario of interest
        -t or --travel_time_time: file with travel times between origin and destination census block group id
        -d or --distance_file: file with distance between origin and destination mesozones
        -ct or --freight_centroid_file: file that maps census block group ids to mesozones
        -cr or --carrier_file: file with carriers' information
        -pl or --payload_file: file with payloads' information
        -vt or --vehicle_type_file: file with vehicle type information
        -st or --scenario: specifies the name of the scenario 
        -yt or --analysis_year: year to be simulated in 20XX format
        -ps or --path_to_max_stops_per_commodity_files: path to folder containing csv files for max stops per commodity 
        -mt or --max_time_to_solve_problem: max time in seconds to solve vehicle routing problem
        -fn or --separate_file_index: a separate number to use to save output files (This is an optional parameter)
    """
    try:
        parser = ArgumentParser()
        parser.add_argument("-cy", "--county-number", dest="county_num",
                            help="an integer indicating the county number", required=True, type=int)
        parser.add_argument("-t", "--travel_time_file", dest="travel_file",
                            help="travel time file in gz format", required=True, type=str)
        parser.add_argument("-d", "--distance_file", dest="dist_file",
                            help="distance file in csv format", required=True, type=str)
        parser.add_argument("-ct", "--freight_centroid_file", dest="CBGzone_file",
                            help="file that maps census block group ids to mesozones in geojson format", required=True, type=str)
        parser.add_argument("-cr", "--carrier_file", dest="carrier_file",
                            help="carrier file in csv format", required=True, type=str)
        parser.add_argument("-pl", "--payload_file", dest="payload_file",
                            help="payload file in csv format", required=True, type=str)
        parser.add_argument("-vt", "--vehicle_type_file", dest="vehicleType_file",
                            help="vehicle type file in csv format", required=True, type=str)
        parser.add_argument("-sn", "--scenario", dest="scenario",
                        help="scenario", required=True, type=str)                
        parser.add_argument("-yt", "--analysis_year", dest="target_year",
                    help="20XX", required=True, type=int)  
        parser.add_argument("-ps", "--path_to_max_stops_per_commodity_files", dest="path_stops",
                    help="max stops per commodity file in csv format", required=True, type=str)  
        # max_time parameter added to tune how long we wait to get an answer to a problem
        parser.add_argument("-mt", "--max_time_to_solve_problem", dest="max_time",
                    help="max time in seconds to solve vehicle routing problem", default=900, type=int)
        parser.add_argument("-fn", "--separate_file_index", dest="file_idx",
                            help="an integer", default=9999, type=str)   
        parser.add_argument("-es", "--EV_savings", dest="EV_savings",
                    help="scenario", required=True, type=str)  
        parser.add_argument("-pt", "--powertrain_types", dest="powertrain_types",   
                    help="powertrain types", nargs='+', required=True, type=str)
        parser.add_argument("-fc", "--fixed_cost", nargs='+', 
                    help="fixed cost", required=True, type=int) 
        parser.add_argument("-cu", "--cost_per_unit_time", nargs='+',
                    help="cost per unit time", required=True, type=float)
        parser.add_argument("-ebc", "--EV_battery_capacity", dest="EV_battery_capacity",
                    help="EV battery capacity in kWh", required=True, type=int)
        parser.add_argument("-soc", "--soc_threshold", dest="soc_threshold",
                    help="state of charge threshold in percentage", required=False, type=float)
                  

        args = parser.parse_args()
        file_index=args.file_idx
        count_num = args.county_num     # county number 
        path_stops = args.path_stops    # path to file containing maximum stops per commodity for internal trips
        max_time = args.max_time        # Maximum time in seconds to solve the vehicle routing problem, default is 900 secs
        EV_savings_pct = args.EV_savings  # EV time savings scenario
        veh_pwrtrn_types = args.powertrain_types  # vehicle powertrain types
        fixed_cost = args.fixed_cost      # fixed cost per vehicle type
        cost_per_unit_time = args.cost_per_unit_time  # cost per unit time per vehicle
        EV_battery_capacity = args.EV_battery_capacity  # EV battery capacity in kWh
        soc_threshold = args.soc_threshold  # state of charge threshold in percentage

        # print("fixed_cost:", fixed_cost)
        # print("cosyt_per_unit_time:", cost_per_unit_time)

        # Saving the created data frames
        if "B2B" in args.payload_file:
            ship_type = "B2B"
        elif "B2C" in args.payload_file:
            ship_type = "B2C"

        # TODO: add a try/catch here in case processing files fails
        tt_df, dist_df, CBGzone_df, c_df, p_df, v_df, vc_df= input_files_processing(args.travel_file, args.dist_file, args.CBGzone_file, args.carrier_file, args.payload_file, args.vehicleType_file, veh_pwrtrn_types)

        b_time = time()



        error_list = []
        error_list.append(['carrier', 'veh', 'commodity', 'index','reason'])
        # print('v_df')
        # print(v_df)
        
        # Add another look for commodity: loop by carrier, vehicle type and commodity type
        # The commodity will decide the limit on number of stops per vehicle:
        # randomly select stops limits and fix slack stop limits to maximum stops possible per commodity

        # print('number of carriers is: ', len(p_df['carrier_id'].unique()))
        global tourId
        tourId = -1
        # payload_rows_all collect all carriers' route rows in a list 
        payload_rows_all = []
        tours_rows_all = []
        carrier_rows_all = []
        for carr_id in p_df['carrier_id'].unique():
        # for carr_id in ['B2B_22515151_93hdt_D', 'B2B_22515071_92hdt_D']:  # Temporary for testing
        # for carr_id in ['6383756_1_mdv']:  # Temporary for testing
        # for carr_id in ['7374093_2_hdv']:  # Temporary for testing
        # for carr_id in ['6378083_1_mdv']: #this carrier has 61 payloads and it works well
        # for carr_id in ['7369581_11_hdt']:
        # for carr_id in ['6378083_1_mdv']: #this carrier works well
        # for carr_id in ['8394801_1_hdt']: #this carrier has 28 payloads but not getting solution from google ortools
        # for carr_id in ['6381912_1_mdv']:  # Temporary for testing
        # for carr_id in ['7373504_36_hdt']: #Load is:  417702.1481599999  num of veh:  5  total veh capacity is:  275000
        # for carr_id in ['B2B_22516611_95hdt_D']:
        # for carr_id in ['B2B_21567441_0hdt_D']:
        # for carr_id in ['B2B_22120211_40hdt_D']:
        # for carr_id in ['6382225_5_hdt']:
        # for carr_id in ['8395473_3_hdt']:
        # for carr_id in ['7367308_10_mdv']:  # Temporary for testing
        # for carr_id in ['8395889_2_hdt']:  # Temporary for testing
        # for carr_id in ['8413411_5_hdt']:
        
            print('Solving problem for carrier ', carr_id)
            # print("tourId:", tourId)
     
            # Initialize parameters used for probelm setting
            try:
                comm = -1
                veh = ''
                index= ''
                veh_types = p_df[(p_df['carrier_id'] == carr_id)].veh_type_2.unique()
                c_prob = c_df[c_df['carrier_id'] == carr_id]
                c_prob = c_prob.dropna()
                # print("vc_df")
                # print(vc_df)
                vc_prob = vc_df[vc_df['carrier_id']== carr_id]
                vc_prob = vc_prob.dropna()
                vc_prob = vc_prob.reset_index()

                used_veh = []  # To save a list of used vehicles per carrier 

                for comm in p_df[p_df['carrier_id']==carr_id]['commodity'].unique():
                    for index in p_df[(p_df['carrier_id']==carr_id) & (p_df['commodity']==comm)]['ship_index'].unique():
                        for veh in veh_types:
                            # To simplify the problem, look at a small problem with same carrier and same commodity id and same vehicle type
                            df_prob = p_df[(p_df['carrier_id'] == carr_id) & (p_df['veh_type_2'] == veh) & (p_df['commodity']==comm) & (p_df['ship_index']==index)]
                            df_prob = df_prob.dropna()

                            total_load = sum(df_prob[(df_prob.carrier_id == carr_id) & (df_prob.veh_type_2 == veh)]['weight'])
                            veh_capacity = 0
                            valid = True    # Boolean to indicate if the problem is valid
                            veh_num = 0

                            # print("veh", veh)
                            veh_capacity = int(v_df[v_df['veh_type_id_2'] == veh]['payload_capacity_weight'].values[0])
                            # print(veh.split("_")[0]+"_"+veh.split("_")[1])
                            # print("vc_prob")
                            # print( vc_prob)
                            diesel_col = veh + "_D"
                            # print("diesel_col:", diesel_col)
                            # print("vc_prob")
                            # print(vc_prob)
                            if diesel_col in vc_prob.columns:
                                veh_num = int(vc_prob[diesel_col].values[0])# we need vc_prob[md_E or md_D] so added a new line to add the number of Diesel veh.
                            electric_col = veh +"_E"
                            if electric_col in vc_prob.columns:
                                veh_num = veh_num + int(vc_prob[veh+"_E"].values[0])

                            # temporary QC check
                            # print ("Carrier Id: {}".format(carr_id))    
                            # print ("veh_type: {0} veh_capacity: {1} veh_num: {2}".format(veh,veh_capacity,veh_num))    

                            max_veh_cap = veh_num*veh_capacity  # variable for saving the vehicle capacity

                            # Getting list of commodities carried by vehicle type
                            comm_list = v_df[v_df['veh_type_id_2'] == veh]['commodities'].values[0].split(', ')
                            comm_list[0] = comm_list[0][1:]
                            comm_list[len(comm_list)-1] = comm_list[len(comm_list)-1][:-1]

                            # Checking if problem is well formulated

                            if len(df_prob) == 0:
                                # print('Could not solve problem for carrier ', carr_id, ': NO PAYLOAD INFO')
                                # print('\n')
                                error_list.append([carr_id, veh, comm, index, 'NO PAYLOAD INFO'])
                                valid = False
                            
                            prob_type = str(df_prob.iloc[0]['job'])

                            if prob_type != 'delivery' and prob_type != 'pickup' and prob_type != 'pickup_delivery':
                                print('Could not solve problem for carrier ', carr_id, ': INCORRECT PROBLEM TYPE: ', prob_type)
                                print('\n')
                                error_list.append([carr_id, veh, comm, index, 'INCORRECT PROBLEM TYPE: '+ str(prob_type)])
                                valid = False
                            
                            elif path_stops == '':
                                print('Could not solve problem for carrier ', carr_id, ': NO PATH TO STOPS FILE')
                                print('\n')
                                error_list.append([carr_id, veh, comm, index, 'NO PATH TO STOPS FILE'])
                                valid = False

                            elif not any(str(int(comm)) == x  for x in comm_list):
                                print('Could not solve problem for carrier ', carr_id, ': COMMODITY ', comm, ' NOT CARRIED BY VEHICLE TYPE ', veh)
                                print('\n')
                                error_list.append([carr_id, veh, comm, index, 'COMMODITY DOES NOT MATCH VEHICLE'])
                                valid = False

                            elif len(vc_prob) == 0:
                                print('Could not solve problem for carrier ', carr_id, ': NO VEHICLE TYPE INFO')
                                print('\n')
                                error_list.append([carr_id, veh, comm, index, 'NO VEHICLE TYPE INFO'])
                                valid = False

                            elif len(c_prob) == 0:
                                print('Could not solve problem for carrier ', carr_id, ': NO CARRIER INFO')
                                print('\n')
                                error_list.append([carr_id, veh, comm, index,'NO CARRIER INFO'])
                                valid = False
                            
                            elif total_load > max_veh_cap:
                                df_prob.sort_values(by=['weight'])
                                valid = False
                                print("Load is larger than vehicle capacity")
                                print('Load is: ', total_load, ' num of veh: ', veh_num, ' total veh capacity is: ', max_veh_cap)
                                while valid == False and (len(df_prob) > 0):
                                    message = 'Dropped payload : ', df_prob.iloc[-1]['payload_id'], ' with weight: ', df_prob.iloc[-1]['weight']
                                    error_list.append([carr_id, veh, message])
                                    print(message)
                                    df_prob = df_prob.iloc[:-1 , :]
                                    if  sum(df_prob['weight']) <= max_veh_cap:
                                        valid = True
                                
                                if not valid:
                                    print('Could not solve problem for carrier ', carr_id, ': SINGLE PAYLOAD WEIGHT GREATER THAN VEHICLE CAPACICY')
                                    print('\n')
                                    error_list.append([carr_id, veh, 'SINGLE PAYLOAD WEIGHT GREATER THAN VEHICLE CAPACICY'])
                            
                            if valid:

                                # Depot location
                                depot_loc = c_prob.loc[c_prob['carrier_id'] == carr_id]['depot_zone'].values[0]

                                print(f'\nSolving problem for carrier ', carr_id, ' with prob type', prob_type, ' and veh type ', veh,
                                ' comm: ', comm, ' index: ', index)
                                
                                #saving small files for testing purposes:
                                # df_prob.to_csv('Carrier_Tour_Plan/test_data/df_prob_pickup_delivery.csv', index=False)
                                # v_df.to_csv('Carrier_Tour_Plan/test_data/v_df_pickup_delivery.csv', index=False)
                                # vc_prob.to_csv('Carrier_Tour_Plan/test_data/vc_prob_pickup_delivery.csv', index=False)
                                # c_prob.to_csv('Carrier_Tour_Plan/test_data/c_prob_pickup_delivery.csv', index=False)

                                
                                data = create_data_model(df_prob, depot_loc, prob_type, v_df, vc_prob, c_prob, carr_id,
                                                        CBGzone_df, tt_df, dist_df, veh, comm, index, path_stops, EV_savings_pct, fixed_cost, cost_per_unit_time, EV_battery_capacity, soc_threshold)

                                # print('data:', data)
                                # #print('the model: \\n')
                                # print("problem type is: ", prob_type)

                                # Now solving the problem
                                if not data:
                                    print('model returned was none')
                                    error_list.append([carr_id, veh, comm, index, 'could not create data dictionary'])
                                else:
                                    print('model was formulated correctly')

                                num_customers = len(data['customer_nodes'])
                                print(f"Number of nodes to visit: {num_customers}")

                                    # Step 2: Solve the initial VRP without considering charging stations
                                print("start solving the initial VRP...")
                                # print("data for initial VRP:", data)
                                print("num_customers for initial VRP:", num_customers, "index:", index)
                                manager, routing, solution = solve_initial_vrp(data, index, comm, num_customers, verbose=True)
                                # print("solution:", solution)
                                if solution is None:
                                    print("No solution found for the initial VRP.")
                                    return
                                
                                total_initial_cost = solution.ObjectiveValue()
                                print(f"Total cost of the initial VRP solution: {total_initial_cost}")
                                # Step 3: Separate ICE and EV routes
                                ortools_D_routes = []
                                ortools_G_routes = []
                                ortools_BE_routes = []
                                ortools_H2_routes = []
                                ortools_PD_routes = []
                                ortools_PG_routes = []

                                for vehicle_id in range(data['num_vehicles']):
                                    index = routing.Start(vehicle_id)
                                    # print("index at start:", index)
                                    route = []
                                    while not routing.IsEnd(index):
                                        node_index = manager.IndexToNode(index)
                                        # print("node_index:", node_index)
                                        route.append(node_index)
                                        # print("route so far:", route)
                                        index = solution.Value(routing.NextVar(index))
                                    route.append(data['depot'])  # Return to depot

                                    # Separate based on vehicle type
                                    customer_nodes_in_route = [node for node in route if node in data['customer_nodes']]
                                    if customer_nodes_in_route:
                                        vehicle_type = data['vehicle_types_id'][vehicle_id]
                                        if vehicle_type == 0:
                                            ortools_D_routes.append(route)
                                        elif vehicle_type == 1:
                                            ortools_G_routes.append(route)
                                        elif vehicle_type == 2:
                                            ortools_BE_routes.append(route)
                                        elif vehicle_type == 3:
                                            ortools_H2_routes.append(route)
                                        elif vehicle_type == 4:
                                            ortools_PD_routes.append(route)
                                        elif vehicle_type == 5: # PG
                                            ortools_PG_routes.append(route)

                                print("or_tools_D Routes:", ortools_D_routes)
                                print("or_tools_G Routes:", ortools_G_routes)
                                print("or_tools_BE Routes:", ortools_BE_routes)
                                print("or_tools_H2 Routes:", ortools_H2_routes)
                                print("or_tools_PD Routes:", ortools_PD_routes)
                                print("or_tools_PG Routes:", ortools_PG_routes)

                                #create a dictionary for initial routes from ortools with their vehicle types
                                initial_routes_dict = {}
                                initial_routes_list =[]
                              

                                powertrain_routes = {
                                    'G':  ortools_G_routes,
                                    'D':  ortools_D_routes,
                                    'BE': ortools_BE_routes,
                                    'H2': ortools_H2_routes,
                                    'PD': ortools_PD_routes,
                                    'PG': ortools_PG_routes,
                                }
                                
                                for pt, routes in powertrain_routes.items():
                                    initial_routes_dict[pt] = [route for route in routes]

                                ICE_KEYS = {'G', 'D'}
                                EV_KEYS  = {'BE', 'H2', 'PD', 'PG'}  # treat these as “electric / non-ICE”

                                ice_routes = {k: initial_routes_dict [k] for k in ICE_KEYS if k in initial_routes_dict}
                                ev_routes  = {k: initial_routes_dict[k] for k in EV_KEYS  if k in initial_routes_dict}

                                # print("ICE:", ice_routes)
                                # print("EV :", ev_routes)


                                for pt, routes in initial_routes_dict.items():
                                   initial_routes_list.append({
                                        'powertrain': pt,
                                        'veh_ty_id': data['veh_pt_and_ids'][pt],
                                        'routes': routes
                                    })

                                # print("Initial routes dictionary from OR-Tools with vehicle types:", initial_routes_dict)
                                # print("Initial routes list of dictionary from OR-Tools with vehicle types:", initial_routes_list)
                                EV_initial_routes_list = initial_routes_list[2:]  # BE, H2, PD, PG
                                ICE_initial_routes_list = initial_routes_list[:2]  # G, D

                                # print("Initial EV routes list:", EV_initial_routes_list)
                                # print("Initial ICE routes list:", ICE_initial_routes_list)

                                for pt, route in ev_routes.items():
                                    # print(f"Powertrain: {pt}, Routes: {route}")
                                    if route:
                                        selected_pt = pt
                                        print("Selected electric powertrain for further processing:", selected_pt)

                                        break
                                for pt, route in ice_routes.items():
                                    # print(f"Powertrain: {pt}, Routes: {route}")
                                    if route:
                                        selected_pt_ice = pt
                                    else:    
                                        selected_pt_ice = None
                                        print("Selected electric powertrain for further processing:", selected_pt_ice)
                                        break
                                        


                                initial_routes_from_ortools = ortools_G_routes + ortools_D_routes + ortools_BE_routes + ortools_H2_routes + ortools_PD_routes + ortools_PG_routes
                                ortools_ice_routes = ortools_D_routes + ortools_G_routes 
                                ortools_ev_routes = ortools_BE_routes + ortools_H2_routes + ortools_PD_routes + ortools_PG_routes
                                print("Initial routes from OR-Tools (ICE + EV):", initial_routes_from_ortools)

                                # Step 4: Gather customers served by ICE routes
                                served_by_ice = set(node for route in ortools_ice_routes for node in route if node in data['customer_nodes'])
                                remaining_customers = set(data['customer_nodes']) - served_by_ice

                                # print("Customers served by ICE routes:", served_by_ice)
                                # print("Remaining customers to be processed for EV:", remaining_customers)

                                if prob_type == 'pickup_delivery':

                                    ev_pd_pairs = filter_pd_pairs_for_ev(data, remaining_customers)
                                    updated_ev_routes, unvisited_customers , unserved_pairs = insert_charging_stations_pd(data, ortools_ev_routes, ev_pd_pairs, selected_pt)  #[1]
                                    # print("ev_pd_pairs:", ev_pd_pairs)
                                    # print("unvisited_customers after charging station insertion for PD:", unvisited_customers)
                               

                                else:
                                    # Build EV routes using only remaining customers
                                    # print("remaining_customers before charging station insertion:", remaining_customers)
                                    # print("selected_pt before charging station insertion:", selected_pt)
                                    updated_ev_routes, unvisited_customers = insert_charging_stations(data, ortools_ev_routes, remaining_customers, selected_pt) #[1]

                                # Step 5: Process EV routes for charging station insertion
                                
                                print("Feasible EV Routes after Charging Station Insertion:")
                                for route in updated_ev_routes:
                                    print(route)
                                #TODO:Improve handling of unvisited customers
                                # Handle unvisited customers for EV. This may not give the best solution but ensures all customers are served. later we have to find a better way to optimize this.
                                ICE_routes_extra = []
                                if unvisited_customers:
                                    print(f"Unvisited customers after EV adjustment: {unvisited_customers}")
                                    ICE_routes_extra.append(0)
                                    
                                    for node in unvisited_customers:
                                        ICE_routes_extra.append(node)
                                    ICE_routes_extra.append(0)

                                    ICE_route_extra_cost = cal_total_cost([ICE_routes_extra], data, 0)  #[3]
                                    # print(f"Cost to cover unvisited customers with ICE route: {ICE_route_extra_cost}")
                                    # print("New ICE route to cover unvisited customers:", ICE_routes_extra)

                                    # return  # Stop if not all customers are served

                                    # Add unvisited customers back to remaining_customers
                                    remaining_customers.update(unvisited_customers)

                                # Step 6: Optimize EV routes using VNS
                                print("Starting VNS optimization for EV routes...")

                                # Create a list of (pickup_node, delivery_node) tuples for PD pairs present in updated_ev_routes
                                pd_pairs_in_ev_routes = []
                                if prob_type == 'pickup_delivery' and 'pickups_deliveries' in data:
                                    # Flatten all nodes in updated_ev_routes for fast lookup
                                    ev_nodes = set(node for route in updated_ev_routes for node in route)
                                    for pair in data['pickups_deliveries']:
                                        # Only include pairs where both pickup and delivery are in the EV routes
                                        if pair[0] in ev_nodes and pair[1] in ev_nodes:
                                            pd_pairs_in_ev_routes.append(tuple(pair))
                                    # print("PD pairs in EV routes:", pd_pairs_in_ev_routes)

                                if prob_type == 'pickup_delivery':
                                    # print("Applying VNS to optimize EV routes...", updated_ev_routes)
                                    final_EV_routes = updated_ev_routes
                                    final_ICE_routes = ortools_ice_routes + [ICE_routes_extra]
                                    # print("unserved_pairs:", unserved_pairs)
                                    optimized_ev_routes = variable_neighborhood_search_pd(data, updated_ev_routes, selected_pt, pd_pairs_in_ev_routes , num_customers=num_customers)

                                    print("Optimized EV Routes (after VNS for PD), ", optimized_ev_routes)
                                    # print("Final EV routes:", optimized_ev_routes)
                                    # print("Final ICE routes:", final_ICE_routes)

                                else:
                                    # print("Applying VNS to optimize EV routes...", updated_ev_routes)
                                    optimized_ev_routes = variable_neighborhood_search(data, updated_ev_routes, selected_pt, remaining_customers, num_customers=num_customers) #[4]
                                    print("\nOptimized EV Routes (after VNS):")
                                    for route in optimized_ev_routes:
                                        print(route)

                                    # Step 7: Combine ICE and EV routes
                                    # print("\nFinal ICE Routes:")
                                    for route in ortools_ice_routes:
                                        print(route)


                                # Filter out depot-only routes like [0, 0]
                                filtered_ice_routes = [route for route in ortools_ice_routes if len(route) > 2 or (len(route) == 2 and route[0] != route[1])]
                                filtered_ev_routes_VNS = [route for route in optimized_ev_routes if len(route) > 2 or (len(route) == 2 and route[0] != route[1])]

                                ice_routes_after_VNS = filtered_ice_routes.copy()
                                ev_routes_after_VNS = filtered_ev_routes_VNS.copy()
                                # print("filtered_ice_routes:", filtered_ice_routes)
                                # print("filtered_ev_routes:", filtered_ev_routes_VNS)

                                # Combine ICE and EV routes after filtering
                                final_routes = filtered_ice_routes + filtered_ev_routes_VNS
                                print("final_routes after VNS:", final_routes)
                                total_cost_EV_VNS = cal_total_cost(filtered_ev_routes_VNS, data, selected_pt)
                                print(f"\nTotal cost of the EV solution after VNS: {total_cost_EV_VNS}")
                                total_cost_EV_VNS_1 = calculate_total_cost(data, filtered_ev_routes_VNS, selected_pt, data['charging_rate'])
                                print(f"\nTotal cost of the EV solution after VNS (method 2): {total_cost_EV_VNS_1}")

                                total_cost_ICE_VNS = cal_total_cost(filtered_ice_routes, data, 0)
                                # print(f"\nTotal cost of the ICE solution after VNS: {total_cost_ICE_VNS}")

                                total_cost_VNS_final_routes = total_cost_EV_VNS + total_cost_ICE_VNS
                                # print(f"\nTotal cost after VNS: {total_cost_VNS_final_routes}")
                                # print(f"Total cost of the initial VRP solution: {total_initial_cost}")
                                print("selected_pt for best move:", selected_pt)
                                print("selected_pt_ice for best move:", selected_pt_ice)

                                if prob_type == 'pickup_delivery':
                                
                                    ice_routes_best_move, ev_routes_best_move = find_best_move_pd(filtered_ice_routes, selected_pt_ice, filtered_ev_routes_VNS, selected_pt, data) 
                                else:
                                    ice_routes_best_move, ev_routes_best_move = find_best_move(filtered_ice_routes, selected_pt_ice, filtered_ev_routes_VNS, selected_pt, data)

                                ice_routes_best_move_cost = cal_total_cost(ice_routes_best_move, data, selected_pt_ice)
                                ev_routes_best_move_cost = cal_total_cost(ev_routes_best_move, data, selected_pt)
                                print("\nICE routes after best move:", ice_routes_best_move)
                                print("\nEV routes after best move:", ev_routes_best_move)
                                final_total_best_move_cost = ev_routes_best_move_cost + ice_routes_best_move_cost
                            
                                # print("Final total cost:", final_total_best_move_cost)

                                # print("Final ICE routes after best move:", ice_routes_best_move)
                                # print("Final EV routes after best move:", ev_routes_best_move)

                                cs_ids = get_ch_st_IDS(ev_routes_best_move, data)
                                print("CS_IDS:", cs_ids)

                                if ice_routes_best_move == []:
                                    final_EV_routes = ev_routes_best_move
                                    final_ICE_routes_temp = ice_routes_best_move + ICE_routes_extra
                                    final_ICE_routes = final_ICE_routes_temp
                                else:
                                    best_route_swap_a, best_total_cost_swap_a, best_route_swap_dict_a = swap_veh_type_EtoD(ev_routes_best_move, data, cs_ids, selected_pt, selected_pt_ice)  #this function swaps one EV route to ICE and applicable for both pickup_delivery and delivery onlu
                                    print("Best route plan dict a:", best_route_swap_dict_a)
                                    best_route_swap_cost_a = best_total_cost_swap_a 

                                    best_route_swap_b, best_total_cost_swap_b, best_route_swap_dict_b = swap_veh_type_DtoE(ice_routes_best_move, data,selected_pt,  selected_pt_ice)
                                    print("Best route plan dict b:", best_route_swap_dict_b)
                                    best_route_swap_cost_b = best_total_cost_swap_b

                                    EV_routes_after_swap = []
                                    ICE_routes_after_swap = []

                                    for i in best_route_swap_dict_a:
                                        route_info = best_route_swap_dict_a[i]
                                        if len(route_info['route']) > 2:
                                        
                                            if route_info["tag"] == "ICE":
                                                ICE_routes_after_swap.append(route_info["route"])
                                            else:
                                                EV_routes_after_swap.append(route_info["route"])

                                    for i in best_route_swap_dict_b:
                                        route_info = best_route_swap_dict_b[i]
                                        if len(route_info['route']) > 2:
                                            if route_info["tag"] == "EV":
                                                EV_routes_after_swap.append(route_info["route"])
                                            else:
                                                ICE_routes_after_swap.append(route_info["route"])
                                    # print("EV routes after swap:", EV_routes_after_swap)
                                    # print("ICE routes after swap:", ICE_routes_after_swap )

                                    final_EV_routes = EV_routes_after_swap
                                    final_ICE_routes_temp = ICE_routes_after_swap + ICE_routes_extra
                                    final_ICE_routes = final_ICE_routes_temp



                                    ICE_route_extra_cost = cal_total_cost([ICE_routes_extra], data, 0)

                                    total_cost_swap = best_route_swap_cost_a + best_route_swap_cost_b + ICE_route_extra_cost

                                    # print("Best total cost:", total_cost_swap)
                                print("Final EV routes:", final_EV_routes)
                                print("Final ICE routes:", final_ICE_routes)

                                carrier_id = carr_id
                                customer_nodes=set(data.get('customer_nodes', []))

                                payload_rows, tour_rows, carrier_rows = routes_to_rows( count_num, ship_type, df_prob, c_prob, final_EV_routes, final_ICE_routes, data, carrier_id, tourId, customer_nodes=customer_nodes)
                                # print("rows:", payload_rows)
                                tourId = payload_rows[-1]['tourId']  # update global tourId
                                # print(f"Updated global tourId to: {tourId}")

                                # extend the global list with this carrier's rows
                                payload_rows_all.extend(payload_rows)
                                tours_rows_all.extend(tour_rows)
                                carrier_rows_all.extend(carrier_rows)
                                # print(f"Added {len(payload_rows)} rows for carrier {carrier_id}")

                                # total_cost_routes_D = cal_total_cost(initial_routes_from_ortools, data, 0)
                                # print(f"\nTotal cost if all jobs are served by diesel vehicles: {total_cost_routes_D}") 

                                


            except Exception as e:
                traceback.print_exc()
                print('Could not solve problem for carrier: ', carr_id, ' : ', e)
                error_list.append([carr_id, veh, comm, index, e])
                # print('\n')
        


        run_time = time() - b_time
        # print('Time for the run: ', run_time)
        # print('\n')

        if not os.path.exists(config.fdir_main_output_tour + str(args.target_year)+"/"):
            os.makedirs(config.fdir_main_output_tour + str(args.target_year)+"/")
        dir_out=config.fdir_main_output_tour + str(args.target_year)+"/"     
        #  Saving the carrier ids with errors
        if len(error_list) > 0:
            with open(dir_out+"%s_county%s_error_%s.csv"%(ship_type, str(count_num), str(file_index) ), "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerows(error_list)
        

                # convert accumulated rows into a DataFrame
        payload_df1 = pd.DataFrame(payload_rows_all)
        tour_df1 = pd.DataFrame(tours_rows_all)
        carrier_df1 = pd.DataFrame(carrier_rows_all)

        # print("payload_df1 columns:", payload_df1.columns)

        # print("ship_type:", ship_type, " county:", count_num, " file_index:", file_index)

   
        # The rows from routes_to_rows() currently look like:
        #  payload_id, route_sequence, tourId, weightInlb, cummulativeWeightInlb,
        #  carrier_id, arrival_time, veh_type
        #
  
  

        # now write to disk
        if file_index == 9999: 
            payload_df1.to_csv(dir_out+"{0}_county{1}_payload_s{2}_y{3}.csv".format(ship_type, count_num, args.scenario, args.target_year  ), index=False)
            tour_df1.to_csv(dir_out+"{0}_county{1}_freight_tours_s{2}_y{3}.csv".format(ship_type, count_num, args.scenario, args.target_year ), index=False)
            carrier_df1.to_csv(dir_out+"{0}_county{1}_carrier_s{2}_y{3}.csv".format(ship_type, count_num, args.scenario, args.target_year ), index=False)

        else:
            payload_df1.to_csv(dir_out+"{0}_county{1}_payload{2}_s{3}_y{4}.csv".format(ship_type, count_num, str(file_index), args.scenario, args.target_year),index=False)
            tour_df1.to_csv(dir_out+"{0}_county{1}_freight_tours{2}_s{3}_y{4}.csv".format(ship_type, count_num, str(file_index), args.scenario, args.target_year), index=False)
            carrier_df1.to_csv(dir_out+"{0}_county{1}_carrier{2}_s{3}_y{4}.csv".format(ship_type, count_num, str(file_index), args.scenario, args.target_year), index=False)

        print ('Completed saving tour-plan files for {0} and county {1}'.format(ship_type, count_num), '\n')
    
    except Exception as e:
        traceback.print_exc()
        print('Could not run module, exception: ', e)   


if __name__ == "__main__":
    main()

