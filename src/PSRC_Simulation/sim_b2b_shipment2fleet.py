
# %%
from re import A
import pandas as pd
import numpy as np
from argparse import ArgumentParser
import random
import os
import time
import json
from frism_utility_distributionchannel import b2b_private_distribution_channel, b2b_forhire_distribution_channel, b2b_create_output, veh_type_create
from frism_pop_shipment import Network, Carriers, B2C_DailyShipment, Firms, DailyShipment
from frism_vehicle_pattern import Departure_distribution, Vehicle_energy, Vius_truck_distribution
import sys
import warnings
from os.path import exists as file_exists
warnings.filterwarnings('ignore')

# create global variables
def create_global_variable(input_setting):
    global state_id # state_code e.g. WA: 53 CA: 6
    global state_abbr # state abbr e.g. WA
    global county_in_region # list of county id 
    global dic_veh # relation ship vehicle type between FRISM and SynthFirm with payload capacity, speed, curb out weight
    global fdir_in_out # upper folder 
    global input_variables # various input files and folders identified in create_input_variable.py

    #folder_path
    fdir_in_out = input_setting['input_variables']['frism_data_folder']
    # variables
    state_id = input_setting['input_variables']['state_code']
    state_abbr = input_setting['input_variables']['state_abbr']
    county_in_region= input_setting['input_variables']['county_list']
    # dictionary
    dic_veh = input_setting['dic_veh']
    input_variables=input_setting['input_variables']
# generate file path information
def sythfirm_file_path(input_variables,year, scenario):
    file_path = input_variables["frism_data_folder"]+input_variables["sub_folder_synthfirm_population"] +str(year)+"_"+str(scenario)+"/"
    for filename in os.listdir(file_path):
        if "firms" in filename:
            firm_file= file_path+filename
        if "carriers" in filename:
            carrier_file= file_path+filename    
        if "leasing" in file_path+filename:
            leasing_file= file_path+filename  
        if "port" in filename:
            port_file= file_path+filename
        if "TDA" in filename:
            stock_file= file_path+filename
    zone_file= input_variables["frism_data_folder"]+input_variables['sub_folder_network']+input_variables['zone_file']
    od_distance_file= input_variables["frism_data_folder"]+input_variables['sub_folder_network']+input_variables['od_distance_file']
    try:
        extnernal_zone_file = input_variables["frism_data_folder"]+input_variables['sub_folder_network']+input_variables['extnernal_zone_file']
    except:
        extnernal_zone_file =None
    try:        
        ondemand_location_file = input_variables["frism_data_folder"]+input_variables['sub_folder_network']+input_variables['ondemand_file']
    except:
        ondemand_location_file = None
    try:        
        local_zone_file = input_variables["frism_data_folder"]+input_variables['sub_folder_network']+input_variables['local_taz_file']
    except:
        local_zone_file = None           
    try:        
        local_ex_zone_file = input_variables["frism_data_folder"]+input_variables['sub_folder_network']+input_variables['local_external_zone_file']
    except:
        local_ex_zone_file = None    
    return firm_file, carrier_file, leasing_file, stock_file, port_file,zone_file, od_distance_file, extnernal_zone_file, ondemand_location_file, local_zone_file, local_ex_zone_file

def main(args=None):
    # read input files
    parser = ArgumentParser()
    parser.add_argument("-sn", "--scenario", dest="scenario",
                    help="scenario", required=True, type=str)                
    parser.add_argument("-yt", "--analysis year", dest="target_year",
                help="20XX", required=True, type=int)                           
    parser.add_argument("-st", "--shipment type", dest="ship_type",
                        help="B2B or B2C", required=True, type=str)
    parser.add_argument("-ct", "--county", dest="sel_county",
                        help="select county; for all area run, put 9999", required=True, type=int)
    parser.add_argument("-gf", "--b2c growth", dest="growth_factor",
                        help="b2 growth 0,20,50 (percent)", default=0, type=int)
    parser.add_argument("-sr", "--sample ratio", dest="sample_rate",
                        help="sampeing rate for light run 0-100", default=100, type=int)
    parser.add_argument("-bct", "--b2c type ", dest="b2c_type",
                        help="all, goods or ondemand",  default="goods", type=str)
    parser.add_argument("-int", "--internatioal flow included ", dest="international_flag",
                        help="Y or N",  default="Y", type=str)
    parser.add_argument("-sa", "--Study_area ", dest="study_region",
                        help="ST, SF", required=True, type=str)
    parser.add_argument("-va", "--vehicle choice adjustemnt ", dest="mdhdv_adjustment",
                        help="0.10", default=0, type=float)                                                                                                              
    args = parser.parse_args()
    scenario=args.scenario
    year=args.target_year
    ship_type=args.ship_type
    sel_county=args.sel_county
    sample_ratio=args.sample_rate
    international_flag = args.international_flag
    study_region = args.study_region
    mdhdv_adjustment = args.mdhdv_adjustment

    # Read input_setting. Before this need to run create_input_variable.py that will create input_setting_{region}.json file 
    with open("input_setting_{}.json".format(study_region) , 'r') as openfile:
        # Reading from json file
            input_setting = json.load(openfile)
    # create dictionary by name in input_setting        
    input_variables=input_setting['input_variables']
    input_dic_crosswalk_TDA_class=input_setting['dic_crosswalk_TDA_class']
    input_dic_crosswalk_TDA_Powertrain=input_setting['dic_crosswalk_TDA_Powertrain']

    # Generate global variables
    create_global_variable(input_setting)

    # Create the file path for input data processing
    firm_file, carrier_file, leasing_file, stock_file, port_file, zone_file, od_distance_file, extnernal_zone_file, ondemand_location_file,local_zone_file,local_ex_zone_file =sythfirm_file_path(input_variables,year, scenario)    
    # Input data processing
    """
    network: same file for B2B and B2C
    carriers: file for B2B and B2C, respectively 
    firms: same file for B2B and B2C
    departure_distribution: file for B2B and B2C, respectively 
    vehicle_energy: same file for B2B and B2C
    """
    print ("Creating networks")
    network = Network(zone_file= zone_file,
                    od_distance_file= od_distance_file,
                    ondemand_location_file=ondemand_location_file,
                    local_zone_file=local_zone_file,
                    local_external_zone_file=local_ex_zone_file,
                    extnernal_zone_file= extnernal_zone_file ,
                    state_id= state_id,
                    county_in_region= county_in_region)
    print ("Creating carriers")
    carriers = Carriers(carrier_file= carrier_file,
                        shipment_type= ship_type ,
                        state_id= state_id,
                        county_in_region= county_in_region ,
                        dic_veh= dic_veh )
    print ("Creating firms")
    firms=Firms(firm_file= firm_file,
                port_file= port_file,
                leasing_file=leasing_file,
                carrier_file=carrier_file, 
                state_id=state_id )
    print ("Creating departure distribution")
    departure_distribution=Departure_distribution(file_path= input_variables["frism_data_folder"]+input_variables['sub_folder_veh'],
        shipment_type= ship_type,
        dic_veh= dic_veh)
    print ("Creating vehicle energy profile")
    vehicle_energy= Vehicle_energy(
        stock_file= stock_file,
        target_year= year,
        dic_crosswalk_TDA_class= input_dic_crosswalk_TDA_class,
        dic_crosswalk_TDA_Powertrain= input_dic_crosswalk_TDA_Powertrain,
        dic_veh=dic_veh)
    print ("Read the distribution of vehicle types")
    vius = Vius_truck_distribution(vius_file= input_variables["frism_data_folder"]+input_variables['sub_folder_veh']+input_variables['vius_file'])

    ############ B2B specific operation ############### 
    print ("Generating county {}".format(sel_county))
    print ("Creating B2B shipments")
    shipment_file_path = input_variables["frism_data_folder"]+input_variables['sub_folder_b2b_demand']+"{0}_{1}/".format(year, scenario)
    daily_shipment = DailyShipment(shipment_file_path= shipment_file_path,
        annual_to_day_factor=input_variables["b2b_annual_to_day_factor"],
        sample_ratio= sample_ratio,
        sel_county= sel_county,
        state_id= state_id ,
        county_in_region= county_in_region,
        international_flag= international_flag)
    print ("B2B private processing")
    selected_leasings = firms.leasings_agg[firms.leasings_agg["st"]==state_abbr].reset_index(drop=True)
    b2b_private = daily_shipment.shipments_record[daily_shipment.shipments_record['mode_choice']=="Private Truck"].reset_index(drop=True)
    final_b2b_private, selected_firms, selected_leasings= b2b_private_distribution_channel(b2b_private, firms.firms, selected_leasings, vius.vius, vehicle_energy.dic_energy, input_variables, dic_veh, county_in_region, mdhdv_adjustment) 
    print ("B2B for-hire processing")
    b2b_forhire = daily_shipment.shipments_record[(daily_shipment.shipments_record['mode_choice']=="For-hire Truck")].reset_index(drop=True)
    final_b2b_forhire, selected_carrier, selected_leasings = b2b_forhire_distribution_channel(carriers.carrier,firms.firms, b2b_forhire, vius.vius, network.od_distance, vehicle_energy.dic_energy, selected_leasings, input_variables, dic_veh, county_in_region, mdhdv_adjustment)
    print ("Processing B2B shipment to fleet format")
    carrier_out, payloads_out = b2b_create_output(final_b2b_private,
                                                final_b2b_forhire, 
                                                selected_firms, 
                                                selected_carrier, 
                                                ship_type, 
                                                network.external_zone, 
                                                departure_distribution.departure_distribution, 
                                                input_variables, 
                                                dic_veh,
                                                network.dic_exteranl_coordinate, 
                                                network.local_zone)
    vehicle_types = veh_type_create(vehicle_energy.dic_energy, dic_veh)
    print ("Write the result in the folder")
    if not file_exists(input_variables["frism_data_folder"]+input_variables["sub_folder_ship_output"]+f"{year}/"):
        os.makedirs(input_variables["frism_data_folder"]+input_variables["sub_folder_ship_output"]+f"{year}/")

    carrier_out.to_csv(input_variables["frism_data_folder"]+input_variables["sub_folder_ship_output"]+f"{year}/{ship_type}_carrier_county{sel_county}_s{scenario}_y{year}_sr{sample_ratio}.csv")
    payloads_out.to_csv(input_variables["frism_data_folder"]+input_variables["sub_folder_ship_output"]+f"{year}/{ship_type}_payload_county{sel_county}_s{scenario}_y{year}_sr{sample_ratio}.csv")
    vehicle_types.to_csv(input_variables["frism_data_folder"]+input_variables["sub_folder_ship_output"]+f"{year}/vehicle_types_s{scenario}_y{year}.csv")


