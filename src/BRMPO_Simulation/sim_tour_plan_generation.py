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
import inspect
from xml.dom import minidom
import math
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from time import time
import numpy as np
from argparse import ArgumentParser
import json
from os.path import exists as file_exists
import os
from frism_untility_tourplan import create_data_model, input_files_processing, form_solve

def create_global_variable(input_setting):
    """
    state_id: state code (e.g., 6: CA)
    """
    global state_id
    global state_abbr
    global county_in_region
    global dic_veh
    global fdir_in_out
    global input_variables

    #folder_path
    fdir_in_out = input_setting['input_variables']['frism_data_folder']
    # variables
    state_id = input_setting['input_variables']['state_code']
    state_abbr = input_setting['input_variables']['state_abbr']
    county_in_region= input_setting['input_variables']['county_list']
    # dictionary
    dic_veh = input_setting['dic_veh']
    input_variables=input_setting['input_variables']



def main(args=None):
    """Main function.

    Takes input files names from console specifing the parameters of the vehicle routing problem.

    Args:
        -sn or -scenario: specifies the name of the scenario 
        -yt or --analysis_year: year to be simulated in 20XX format
        -st or --shipment type: shipment type: B2B or B2C
        -ct or --county_number: the county number in the scenario of interest
        -sr or --sample ratio: sample rate for a daily simulation  0-100 (full sample)
        -sa or --study_area: abbreviation of study region: e.g., ST, SF, BO
        -mt or --max_time_to_solve_problem: max time in seconds to solve vehicle routing problem
    """
    try:
        parser = ArgumentParser()
        parser.add_argument("-sn", "--scenario", dest="scenario",
                        help="scenario", required=True, type=str)                
        parser.add_argument("-yt", "--analysis year", dest="target_year",
                    help="20XX", required=True, type=int)                           
        parser.add_argument("-st", "--shipment type", dest="ship_type",
                            help="B2B or B2C", required=True, type=str)
        parser.add_argument("-ct", "--county", dest="sel_county",
                            help="select county", required=True, type=int)
        parser.add_argument("-sr", "--sample ratio", dest="sample_rate",
                            help="sampeing rate for light run 0-100", default=100, type=int)
        parser.add_argument("-sa", "--study_area ", dest="study_region",
                            help="ST, SF", required=True, type=str)
        parser.add_argument("-mt", "--max_time_to_solve_problem", dest="max_time", 
            help="max time in seconds to solve vehicle routing problem", default=900, type=float) # max_time parameter added to tune how long we wait to get an answer to a problem

        args = parser.parse_args()
        scenario=args.scenario
        year=args.target_year
        ship_type=args.ship_type
        count_num=args.sel_county
        sample_ratio=args.sample_rate
        study_region = args.study_region
        max_time = args.max_time  # Maximum time in seconds to solve the vehicle routing problem, default is 900 secs

        with open("input_setting_{}.json".format(study_region) , 'r') as openfile:
            # Reading from json file
                input_setting = json.load(openfile)
        # Generate global variables
        create_global_variable(input_setting)

        path_stops = fdir_in_out+ input_variables["sub_folder_tour_constraint"]      # path to file containing maximum stops per commodity for internal trips
        travel_file= fdir_in_out+input_variables["sub_folder_network"]+input_variables["network_travel_skim"]
        carrier_file = fdir_in_out+input_variables["sub_folder_ship_output"]+ f"{year}/{ship_type}_carrier_county{count_num}_s{scenario}_y{year}_sr{sample_ratio}.csv"
        payload_file = fdir_in_out+input_variables["sub_folder_ship_output"]+ f"{year}/{ship_type}_payload_county{count_num}_s{scenario}_y{year}_sr{sample_ratio}.csv"
        vehicleType_file = fdir_in_out+input_variables["sub_folder_ship_output"]+f"{year}/vehicle_types_s{scenario}_y{year}.csv" 

        # add a try/catch here in case processing files fails
        tt_df, dist_df, c_df, p_df, v_df, vc_df, dic_taz = input_files_processing(travel_file, carrier_file, payload_file, vehicleType_file)

        b_time = time()

        # data frames for the tour, carrier and payload
        tour_df = pd.DataFrame(columns = ['tour_id', 'departureTimeInSec', 'departureLocation_zone', 'maxTourDurationInSec',
                                        'departureLocation_x','departureLocation_y', 'true_depot_zone'])
        # Format for carrier data frame: carrierId,tourId, vehicleId,vehicleTypeId,depot_zone
        carrier_df = pd.DataFrame(columns = ['carrierId','tourId', 'vehicleId', 'vehicleTypeId','depot_zone', 'depot_zone_x', 'depot_zone_y', 'true_depot_zone'])
        # format for payload format
        # payloadId, sequenceRank, tourId, payloadType, weightInlb, requestType,locationZone,
        # estimatedTimeOfArrivalInSec, arrivalTimeWindowInSec_lower, arrivalTimeWindowInSec_upper,operationDurationInSec
        payload_df = pd.DataFrame(columns = ['payloadId','sequenceRank','tourId','payloadType','weightInlb','cummulativeWeightInlb',
                                            'requestType','locationZone','estimatedTimeOfArrivalInSec','arrivalTimeWindowInSec_lower',
                                            'arrivalTimeWindowInSec_upper','operationDurationInSec', 'locationZone_x', 'locationZone_y', 'true_locationZone','BuyerNAICS','SellerNAICS','truck_mode'])

        error_list = []
        error_list.append(['carrier', 'veh', 'commodity', 'index','reason'])
        
        # Add another look for commodity: loop by carrier, vehicle type and commodity type
        # The commodity will decide the limit on number of stops per vehicle:
        # randomly select stops limits and fix slack stop limits to maximum stops possible per commodity
        print('number of carriers is: ', len(p_df['carrier_id'].unique()))
        for carr_id in p_df['carrier_id'].unique():
        #for carr_id in ['B2B_26305351_5hdt_D']:
            # Initialize parameters used for probelm setting
            try:
                comm = -1
                veh = ''
                index= ''
                veh_types = p_df[(p_df['carrier_id'] == carr_id)].veh_type.unique()
                c_prob = c_df[c_df['carrier_id'] == carr_id]
                c_prob = c_prob.dropna()
                vc_prob = vc_df[vc_df['carrier_id']== carr_id]
                vc_prob = vc_prob.dropna()
                vc_prob = vc_prob.reset_index()

                used_veh = []  # To save a list of used vehicles per carrier

                for comm in p_df[p_df['carrier_id']==carr_id]['commodity'].unique():
                    for index in p_df[(p_df['carrier_id']==carr_id) & (p_df['commodity']==comm)]['ship_index'].unique():
                        for veh in veh_types:
                            # To simplify the problem, look at a small problem with same carrier and same commodity id and same vehicle type
                            df_prob = p_df[(p_df['carrier_id'] == carr_id) & (p_df['veh_type'] == veh) & (p_df['commodity']==comm) & (p_df['ship_index']==index)]
                            df_prob = df_prob.dropna()

                            total_load = sum(df_prob[(df_prob.carrier_id == carr_id) & (df_prob.veh_type == veh)]['weight'])
                            veh_capacity = 0
                            valid = True    # Boolean to indicate if the problem is valid
                            veh_num = 0
                            veh_capacity = int(v_df[v_df['veh_type_id'] == veh]['payload_capacity_weight'].values[0])
                            veh_num = int(vc_prob[veh.split("_")[0]+"_"+veh.split("_")[1]].values[0])

                            # temporary QC check
                            # print ("Carrier Id: {}".format(carr_id))    
                            # print ("veh_type: {0} veh_capacity: {1} veh_num: {2}".format(veh,veh_capacity,veh_num))    

                            max_veh_cap = veh_num*veh_capacity  # variable for saving the vehicle capacity

                            # Getting list of commodities carried by vehicle type
                            comm_list = v_df[v_df['veh_type_id'] == veh]['commodities'].values[0].split(', ')
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

                                #print('Solvign problem for carrier ', carr_id, ' with prob type', prob_type, ' and veh type ', veh,' comm: ', comm, ' index: ', index)
                                
                                #saving small files for testing purposes:
                                # df_prob.to_csv('Carrier_Tour_Plan/test_data/df_prob_pickup_delivery.csv', index=False)
                                # v_df.to_csv('Carrier_Tour_Plan/test_data/v_df_pickup_delivery.csv', index=False)
                                # vc_prob.to_csv('Carrier_Tour_Plan/test_data/vc_prob_pickup_delivery.csv', index=False)
                                # c_prob.to_csv('Carrier_Tour_Plan/test_data/c_prob_pickup_delivery.csv', index=False)
                                
                                data = create_data_model(df_prob, depot_loc, prob_type, v_df, vc_prob, c_prob, carr_id,
                                                         tt_df, dist_df, veh, comm, index, path_stops, dic_taz)
                                #print('the model: \\n')
                                #print(data)
                                # Now solving the problem
                                if not data:
                                    print('model returned was none')
                                    error_list.append([carr_id, veh, comm, index, 'could not create data dictionary'])
                                else:
                                    #print('model was formulated correctly')
                                    used_veh = form_solve(data, tour_df, carr_id, carrier_df, payload_df, 
                                                            prob_type, count_num, ship_type, c_prob, df_prob, max_time, index, comm, error_list)
                                    #print('used veh: ', used_veh)
                                    # Saving small output files for testing purposes
                                    # tour_df.to_csv('test_data/tour_df_pickup_delivery_internal.csv', index=False)
                                    # carrier_df.to_csv('test_data/carrier_df_pickup_delivery_internal.csv', index=False)
                                    # payload_df.to_csv('test_data/payload_df_pickup_delivery_internal.csv', index=False)

                                    # Reduce number of vehicles depending on those useds
                                    if len(used_veh) > 0:
                                        veh_id = veh.split("_")[0]+"_"+veh.split("_")[1]
                                        vc_prob.loc[0,veh_id] = vc_prob.loc[0,veh_id]-len(used_veh)

            except Exception as e:
                print('Could not solve problem for carrier: ', carr_id, ' : ', e)
                error_list.append([carr_id, veh, comm, index, e])
                # print('\n')

        run_time = time() - b_time
        print('Time for the run: ', run_time)
        # print('\n')
        dir_out= input_variables["frism_data_folder"]+input_variables["sub_folder_tour_output"]+f"{year}/"
        if not file_exists(dir_out):
            os.makedirs(dir_out)    
        #  Saving the carrier ids with errors
        if len(error_list) > 0:
            with open(dir_out+f"{ship_type}_county{count_num}_error.csv", "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerows(error_list)

        tour_df.to_csv(dir_out+f"{ship_type}_county{count_num}_freight_tours_s{scenario}_y{year}_sr{sample_ratio}.csv", index=False)
        carrier_df.to_csv(dir_out+f"{ship_type}_county{count_num}_carrier_s{scenario}_y{year}_sr{sample_ratio}.csv", index=False)
        payload_df.to_csv(dir_out+f"{ship_type}_county{count_num}_payload_s{scenario}_y{year}_sr{sample_ratio}.csv", index=False)
        print ('Completed saving tour-plan files for {0} and county {1}'.format(ship_type, count_num), '\n')
        
    except Exception as e:
        print('Could not run module, exception: ', e)   


if __name__ == "__main__":
    main()
