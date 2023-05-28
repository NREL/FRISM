# %%
from re import A
import pandas as pd
import numpy as np
import geopandas as gpd
from argparse import ArgumentParser
import random
import config
import glob
from os.path import exists as file_exists
import os
from alive_progress import alive_bar
import time
from shapely.geometry import Point
import math 

def create_global_variable(md_max, hd_max, fdir, state,max_tour_for_b2b ):
    global md_max_load
    global hd_max_load
    global fdir_in_out
    global state_id
    global max_tour
    global input_veh_list
    global output_veh_list
    global dic_fuel
    global dic_veh
    md_max_load= md_max
    hd_max_load= hd_max
    fdir_in_out = fdir
    state_id =state
    max_tour=max_tour_for_b2b
    
    dic_veh={'md': "Class 4-6 Vocational",
    'hdt':"Class 7&8 Tractor",
    'hdv':"Class 7&8 Vocational"
    }
    dic_fuel={"Diesel": "Diesel", "Battery Electric": "Electricity", "H2 Fuel Cell": "Hydrogen" , "PHEV": "Diesel"}
    input_veh_list= ['Diesel Class 4-6 Vocational','Electric Class 4-6 Vocational',
                        'Diesel Class 7&8 Tractor','Electric Class 7&8 Tractor',
                        'Diesel Class 7&8 Vocational','Electric Class 7&8 Vocational',
                        'EV_powertrain (if any)' ]
    output_veh_list=["md_D","md_E", "hdt_D", "hdt_E", "hdv_D", "hdv_E"]                    
# %% 
def veh_type_create():
    vehicle_types= pd.DataFrame()

    for veh_class in dic_veh.keys():
        for veh_fuel in dic_fuel.keys():
            if veh_fuel == "Diesel":
                mid_fuel="D"
            else:
                mid_fuel="E"

            if veh_class=="md":
                max_load= md_max_load
                veh_weight=10000
                speed=80
            else: 
                max_load= hd_max_load
                veh_weight=15000
                speed=65     
            
            temp= pd.DataFrame(data={'veh_type_id': [veh_class+"_"+mid_fuel+"_"+veh_fuel],
                                'veh_category': [veh_fuel+" "+dic_veh[veh_class]],
                                'veh_class':[dic_veh[veh_class]],
                                'body_type':['NA'],
                                'commodities':[[1,2,3,4,5]],
                                'weight':[veh_weight], 
                                'length':['NA'],
                                'payload_capacity_weight':[max_load],
                                'payload_capacity_cbf':['NA'],
                                'max_speed(mph)':[speed],
                                'primary_fuel_type':[dic_fuel[veh_fuel]],
                                'secondary_fuel_type':['NA'],
                                'primary_fuel_rate':[dic_energy[dic_veh[veh_class]][veh_fuel]],
                                'secondary_fuel_rate':['NA'],
                                'Automation level':['NA'],
                                'monetary cost':['NA']})
            vehicle_types=pd.concat([vehicle_types,temp], ignore_index=True).reset_index(drop=True)                       

    return vehicle_types

create_global_variable(config.md_cap,config.hd_cap,config.fdir_in_out ,config.state_id,config.max_tour_for_b2b)
s_list=["HOP_highp2", "HOP_highp4", "HOP_highp6","HOP_highp8","HOP_highp10",
"Ref_highp2", "Ref_highp4", "Ref_highp6","Ref_highp8","Ref_highp10"]

dir_out= "/Users/kjeong/NREL/1_Work/1_2_SMART_2_0/Model_development/Results_veh_tech_v2/"
for scenario in s_list:
    #scenario =s_list[0]
    target_year =2050
    stock_file= 'TDA_{}.csv'.format(scenario)

    fdir_truck=fdir_in_out+'/Sim_inputs/Synth_firm_pop/'
    stocks=pd.read_csv(fdir_truck+stock_file, header=0, sep=',')
    stocks["Class"]=stocks["Class"].str.replace(" Sleeper ", " ")
    stocks["Class"]=stocks["Class"].str.replace(" Day Cab ", " ")


    dic_energy={dic_veh[veh_classs]: {veh_fuel: 1 for veh_fuel in dic_fuel.keys()}  for veh_classs in dic_veh.keys()}
    for veh_class in dic_veh.keys():
        for veh_fuel in dic_fuel.keys():
            if veh_fuel == "PHEV":
                temp_veh_fuel= veh_fuel+" Diesel"
            elif veh_fuel == "Diesel" :
                temp_veh_fuel= veh_fuel+" CI"
            else:    
                temp_veh_fuel= veh_fuel

            temp= stocks[(stocks["Year"] == target_year) &
                (stocks["Powertrain"].str.contains(temp_veh_fuel)) &
                (stocks["Class"].str.contains(dic_veh[veh_class])) & 
                (stocks["mpgge"] >1) & 
                (stocks["Stock"] >0)]
            temp['w_mpgge']= temp.apply(lambda x: x["mpgge"]*x["Stock"], axis=1)
            mpg= temp["w_mpgge"].sum()/temp["Stock"].sum()
            if pd.isna(mpg):
                dic_energy[dic_veh[veh_class]][veh_fuel]= 0.1
            else: 
                dic_energy[dic_veh[veh_class]][veh_fuel]= mpg   

    vehicle_types = veh_type_create()
    vehicle_types.to_csv (dir_out+config.fnm_vtype+"_s{}_y{}.csv".format(scenario,target_year), index = False, header=True)             
# %%
