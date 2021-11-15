#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd


# In[2]:


import geopandas as gp


# In[3]:


import numpy as np


# In[4]:


import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
# from lxml import etree
from copy import copy
import os
import inspect
from xml.dom import minidom


# In[5]:


import math


# In[6]:


import networkx as nx


# In[7]:


from networkx import DiGraph


# In[8]:


from vrpy import VehicleRoutingProblem


# In[9]:


import matplotlib.pyplot as plt


# In[10]:


from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp


# In[11]:


from time import time


# In[12]:


import gc


# In[13]:


# TODO: What if source and destination block zone are in the same TAZ?
# Handle case when block-level zone cannot be mapped to correct TAZ
# TODO: Handle multiple shipments/routes per carrier, having multiple sequence ids


# In[14]:


# Function to get travel time using mesozone ID refering CBGID in tt_df
def tt_cal(org_meso, dest_meso, org_geoID, dest_geoID):
    #Added sel_tt_df for selected tt_df data frame and sel_dist_df for selected dist_df
    travel_time = 0
    try:
#         org_geoID= int(CBGzone_df[CBGzone_df['MESOZONE']==org_meso].GEOID.values[0])
#         dest_geoID= int(CBGzone_df[CBGzone_df['MESOZONE']==dest_meso].GEOID.values[0])
#         print('using tt_df')
        print('tt info: ', tt_df.info(memory_usage="deep"))
        travel_time = tt_df[(tt_df['origin']==org_geoID) & (tt_df['destination']==dest_geoID)].TIME_minutes.values[0]
    except:
        try:
            print( 'dist info: ', dist_df.info(memory_usage="deep"))
            dist = dist_df[(dist_df['Origin']==org_meso) &
                           (dist_df['Destination']==dest_meso)].dist.values[0]
            travel_time= dist/40*60
#             print('using dist_df')
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


# ### Running the VRP Problems

# In[15]:


# KJ: read travel time, distance, zonal file as inputs  # Slow step
tt_df = pd.read_csv('input_file/tt_df_cbg.csv.gz', compression='gzip', header=0, sep=',', quotechar='"', error_bad_lines=False)
dist_df = pd.read_csv('input_file/od_distance.csv')  # Slow step


# In[16]:


#zone 20117  and  305 geo  500  and  60014096003
# travel_time = 0
# try:
#     travel_time = tt_df[(tt_df['origin']==500) &
#                      (tt_df['destination']==60014096003)].TIME_minutes.values[0]
#     print('using tt')
# except:
#     try:
#         dist = dist_df[(dist_df['Origin']==20117) &
#                        (dist_df['Destination']==305)].dist.values[0]
#         travel_time= dist/40*60
#         print('using dist ', dist)
#     except:
#         travel_time = 60*3
#         print('did not find anything')
# print(travel_time)

# print(tt_cal(20117,305,500,60014096003))


# In[17]:


len(tt_df)


# In[18]:


len(dist_df)


# In[19]:


CBGzone_df = gp.read_file('input_file/freight_centroids.geojson')


# In[20]:


# We need to know the depot using the carrier file
c_df = pd.read_csv('input_file/carriers.csv')
### KJ: TO DO: 1 need to add lower and upper timewindow and servicetime in the carrier file:
###            'depot_lower', "depot_upper", "depot_time_before", "depot_time_after"
### KJ: lower will be used for Source's departure time, and upper will be used for sink's arrival time
### KJ: need to include service time at depot? How to define the service time? Based on commodity and load?
c_df = c_df.dropna(axis=1, how='all')   # Removing all nan

# reading payload definition
p_df = pd.read_csv('input_file/payloads.csv')
p_df = p_df.dropna(axis=1, how='all')   # Removing all nan


# In[21]:


# # Example files to test time limit and search limit
# c_df = pd.read_csv('input_file/carriers_B2C_V2.csv')
# p_df = pd.read_csv('input_file/payloads_B2C_V2.csv')
# c_df = c_df.dropna(axis=1, how='all')   # Removing all nan
# p_df = p_df.dropna(axis=1, how='all')   # Removing all nan


# In[22]:


# just relax upper time window because of outside of region destination
c_df['depot_upper']=50000
p_df['del_tw_upper']=50000


# In[23]:


c_df.head()


# In[24]:


# Adding in additional colums for vehicle tours


# In[25]:


p_df['carrier_id'] = p_df['carrier_id'].astype(int)


# In[26]:


p_df['sequence_id'] = np.nan


# In[27]:


p_df['tour_id'] = np.nan


# In[28]:


p_df['pu_arrival_time'] = np.nan


# In[29]:


p_df['del_arrival_time'] = np.nan


# In[30]:


p_df = p_df.fillna(int(0));


# In[31]:


p_df.head()


# In[32]:


# Changing tour id and sequence id into ints
p_df['tour_id'] = p_df['tour_id'].astype(int)
p_df['sequence_id'] = p_df['sequence_id'].astype(int)


# In[33]:


p_df.head()


# In[34]:


x = p_df[(p_df['job'] == 'pickup_delivery')]


# In[35]:


# Reading in vehicle information
v_df = pd.read_csv('input_file/vehicle_types.csv')
v_df = v_df.dropna(axis=1, how='all')   # Removing all nan


# In[36]:


v_df.head()


# In[37]:


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


# In[38]:


vc_df = pd.read_csv('input_file/vehicles_by_carrier.csv')


# In[39]:


vc_df.head()


# In[40]:


vc_df.columns


# In[41]:


c_df = c_df.fillna(0); # Fill all nan with zeros


# In[42]:


# p_df['carrier_id'].unique()


# ### Creating the output dataframe to save as csv

# In[43]:


## Allowign Duplication of zone ids is easier


# In[44]:


def get_geoId(zone, CBGzone_df):
    try:
        org_geoID= int(CBGzone_df[CBGzone_df['MESOZONE']==zone].GEOID.values[0])
    except:
        org_geoID = -1
    return int(org_geoID)


# In[45]:


# Receives a data frame for a problem for a particular carrier id
# To account for service time, we add service time of destination to regular travel time
def create_data_model(df_prob, depot_loc, prob_type, v_df, f_prob, c_prob, carrier_id,
                     md_start_id, hd_start_id, CBGzone_df):
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
    depot_service_time = float(c_prob.loc[c_prob['carrier_id'] == carr_id]['depot_time_before'].values[0])
    data['stop_durations'].append(depot_service_time)

    data['time_windows'] = []
    # Add time window for depot
    data['time_windows'].append((int(c_prob.loc[c_prob['carrier_id'] == carr_id]['depot_lower'].values[0]),
                                int(c_prob.loc[c_prob['carrier_id'] == carr_id]['depot_upper'].values[0])))
    data['demands'] = []
    data['demands'].append(0.0) # Adding demand for depot

    data['geo_ids'] = []
    data['geo_ids'].append(get_geoId(depot_loc, CBGzone_df))

    index = 0
    for i in df_prob['payload_id'].unique():
        if prob_type == 'delivery':
            temp_zone = (int(df_prob.loc[df_prob['payload_id'] == i]['del_zone'].values[0])) # find zone
            data['loc_zones'].append(copy(temp_zone))     # saving zone
            data['geo_ids'].append(get_geoId(temp_zone, CBGzone_df))

            # Adding time window
            data['time_windows'].append((int(df_prob.loc[df_prob['payload_id'] == i]['del_tw_lower'].values[0]),
                                int(df_prob.loc[df_prob['payload_id'] == i]['del_tw_upper'].values[0])))
#             # Adding travel time from depot
#             time_l.append(int(tt_cal(depot_loc, temp_zone)))

            data['payload_ids'].append(copy(i))

            demand = math.ceil(df_prob.loc[df_prob['payload_id'] == i]['weight'].values[0])
            data['demands'].append(copy(demand))

            service_time = float(df_prob.loc[df_prob['payload_id'] == i]['del_stop_duration'].values[0])
            data['stop_durations'].append(copy(service_time))

            index += 1

        elif prob_type =='pickup':
            temp_zone = int(df_prob.loc[df_prob['payload_id'] == i]['pu_zone'].values[0]) # find zone
            data['loc_zones'].append(copy(temp_zone))   # saving zone
            data['geo_ids'].append(get_geoId(temp_zone, CBGzone_df))

            # Adding time window
            data['time_windows'].append((int(df_prob.loc[df_prob['payload_id'] == i]['pu_tw_lower'].values[0]),
                                int(df_prob.loc[df_prob['payload_id'] == i]['pu_tw_upper'].values[0])))
#             # Adding travel time from depot
#             time_l.append(int(tt_cal(depot_loc, temp_zone)))

            data['payload_ids'].append(copy(i))

            demand = math.ceil(df_prob.loc[df_prob['payload_id'] == i]['weight'].values[0])
            data['demands'].append(copy(demand))

            service_time = float(df_prob.loc[df_prob['payload_id'] == i]['pu_stop_duration'].values[0])
            data['stop_durations'].append(copy(service_time))

            index += 1

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

#             # Adding travel time from depot to pickup
#             time_l.append(int(tt_cal(depot_loc, temp_zone_p)))
#             # Adding travel time from depot to delivery
#             time_l.append(int(tt_cal(depot_loc, temp_zone_d)))

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

#     print('length of zones : ', len(data['loc_zones']))
    print(data['loc_zones'])

    # Adding travel time for rest of locations
    print("Beginning to get time matrix")

#     tt_chunks = pd.read_csv('input_file/tt_df_cbg.csv.gz', compression='gzip', chunksize=100000, header=0, sep=',', quotechar='"', error_bad_lines=False)
#     dist_chunks = pd.read_csv('input_file/od_distance.csv', chunksize=100000)  # Slow step

#     cols = ['origin', 'destination', 'TIME_minutes']
#     sel_tt_df = pd.DataFrame(columns = cols)
#     for tt_df in tt_chunks:
#         temp = tt_df[(tt_df['origin'].isin(data['geo_ids'])) &
#                      (tt_df['destination'].isin(data['geo_ids']))][cols]
# #         print(len(temp))
#         if len(temp) > 0:
#             sel_tt_df = sel_tt_df.append(temp, ignore_index=True)
#         del temp
#         del tt_df
#         gc.collect()
#     print('length of tt: ', len(sel_tt_df))
#     del tt_chunks
#     gc.collect()


#     cols = ['Origin', 'Destination', 'dist']
#     sel_dist_df = pd.DataFrame(columns = cols)
#     for dist_df in dist_chunks:
#         temp = dist_df[(dist_df['Origin'].isin(data['loc_zones'])) &
#                        (dist_df['Destination'].isin(data['loc_zones']))][cols]
# #         print(len(temp))
#         if len(temp) > 0:
#             sel_dist_df = sel_dist_df.append(temp, ignore_index=True)
#         del temp
#         del dist_df
#         gc.collect()
#     del dist_chunks
#     gc.collect()

#     print("length of dist ", len(sel_dist_df), " len of tt ", len(sel_tt_df))

    b_timing = time()

    for i in range(len(data['loc_zones'])):
        time_l = []
        travel_time = 0

#         if prob_type == 'delivery':
#             i_zone = (int(df_prob.loc[df_prob['payload_id'] == i]['del_zone'].values[0]))
#             service_time = float(df_prob.loc[df_prob['payload_id'] == i]['del_stop_duration'].values[0])
#         elif prob_type =='pickup':
#             i_zone = (int(df_prob.loc[df_prob['payload_id'] == i]['pu_zone'].values[0]))
#             service_time = float(df_prob.loc[df_prob['payload_id'] == i]['pu_stop_duration'].values[0])
#         # saving service times
#         data['stop_durations'].append(copy(service_time))

#         # TO DO : need to handle pickup_delivery service time

#         time_l.append(int(tt_cal(i_zone, depot_loc)))

        for j in range(len(data['loc_zones'])):
            if i == j or data['loc_zones'][i] == data['loc_zones'][j]:
                time_l.append(0)
            else:
                try:
                    print('zone', data['loc_zones'][i], ' and ', data['loc_zones'][j], 'geo ',
                          data['geo_ids'][i], ' and ', data['geo_ids'][j])
                    travel_time = tt_cal(data['loc_zones'][i], data['loc_zones'][j],
                                     data['geo_ids'][i], data['geo_ids'][j])
                except:
                    print('I get here')

#                 print('found travel time')
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



# In[46]:


# Create and register a transit callback.
def time_callback(from_index, to_index):
    """Returns the travel time between the two nodes."""
    # Convert from routing variable Index to time matrix NodeIndex.
    from_node = manager.IndexToNode(from_index)
    to_node = manager.IndexToNode(to_index)
    return data['time_matrix'][from_node][to_node] + data['stop_durations'][to_node]


# In[47]:


# Add Capacity constraint.
def demand_callback(from_index):
    """Returns the demand of the node."""
    # Convert from routing variable Index to demands NodeIndex.
    from_node = manager.IndexToNode(from_index)
    return data['demands'][from_node]


# In[48]:


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

                #'payloadId','sequenceRank','tourId','payloadType','weightInlb','requestType',
                #'locationZone','estimatedTimeOfArrivalInSec','arrivalTimeWindowInSec_lower',
                #'arrivalTimeWindowInSec_upper','operationDurationInSec'])
#                 print('node index is now ', node_index)
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


# In[49]:


# p_df.head()


# In[50]:


pick_del_df = p_df[(p_df['job'] == 'pickup_delivery')]


# In[52]:


# pick_del_df['carrier_id'].unique()


# In[55]:


for i in pick_del_df['carrier_id'].unique():
    if len(p_df[(p_df['carrier_id'] == i)]) == 1:
        print( 'carrier ', i)


# In[53]:


# pick_del_df.head()


# In[54]:


p_df[(p_df['carrier_id'] == 2248404)]


# ## To run the code start from here

# In[49]:
print('About to start solving problem')

b_time = time()
tour_id = 0
tour_df = pd.DataFrame(columns = ['tour_id', 'departureTimeInSec', 'departureLocation_zone', 'maxTourDurationInSec'])
# Format for carrier data frame: carrierId,tourId, vehicleId,vehicleTypeId,depot_zone
carrier_df = pd.DataFrame(columns = ['carrierId','tourId', 'vehicleId', 'vehicleTypeId','depot_zone'])
# format for payload format
# payloadId, sequenceRank, tourId, payloadType, weightInlb, requestType,locationZone,
# estimatedTimeOfArrivalInSec, arrivalTimeWindowInSec_lower, arrivalTimeWindowInSec_upper,operationDurationInSec
payload_df = pd.DataFrame(columns = ['payloadId','sequenceRank','tourId','payloadType','weightInlb','requestType',
                                     'locationZone','estimatedTimeOfArrivalInSec','arrivalTimeWindowInSec_lower',
                                     'arrivalTimeWindowInSec_upper','operationDurationInSec'])
payload_i = 0

# for carr_id in [6541910]:
for carr_id in [2248484]:
# for carr_id in c_df['carrier_id'].unique():
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
        s_time = time()
        try:
            data = create_data_model(df_prob, depot_loc, prob_type, v_df, f_prob, c_prob, carr_id,
                                md_start_id, hd_start_id, CBGzone_df)
        except Exception as e:
                print(e)
        data_time = time() - s_time
        print('Time to create data is: ', data_time)

        # Create the routing index manager.
        manager = pywrapcp.RoutingIndexManager(len(data['time_matrix']),
                                               data['num_vehicles'], data['depot'])

        # Create Routing Model.
        routing = pywrapcp.RoutingModel(manager)

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

        print(tour_id)

run_time = time() - b_time
print('Time for the run: ', run_time)


# In[ ]:


[9045, 305, 20117]


# In[54]:


data


# In[193]:


# df_prob


# In[194]:


# tour_df


# In[ ]:


# Remove service time from arrival time


# In[168]:


# tour_df.head()


# In[169]:


# carrier_df.head()


# In[232]:


# payload_df[payload_df['tourId'] == 56]


# In[230]:


# payload_df.tail()


# In[171]:


# Saving the files to csv
# tour_df.to_csv("freight-tours_F.csv.csv", index=False)
# carrier_df.to_csv("freight-carriers_F.csv", index=False)
# payload_df.to_csv("payload-plans_F.csv", index=False)


# In[172]:


# df_prob


# In[ ]:
