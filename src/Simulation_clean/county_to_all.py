# %%
from hashlib import shake_128
from re import A
import pandas as pd
import numpy as np
import geopandas as gpd
from argparse import ArgumentParser
import random
import config_SF as config
import glob
from os.path import exists as file_exists
import os
from alive_progress import alive_bar
import time
from shapely.geometry import Point
import math 
import shutil
#%%
f_dir="../../..//Results_from_HPC_sfn_v0/Tour_plan/2018/"
f_dir_2="../../../Results_from_HPC_sfn_v0/Tour_plan/2018_all/"
county_list=[1, 13, 41, 55, 75, 81, 85, 95, 97]
target_year="2018"
s_list=["Base"]
# s_list=["HOP_highp2", "HOP_highp4", "HOP_highp6","HOP_highp8","HOP_highp10",
# "Ref_highp2", "Ref_highp4", "Ref_highp6","Ref_highp8","Ref_highp10"]
for scenario in s_list:
    for ship_type in ["B2B", "B2C"]:
        tour_num=0
        N_df_payload=pd.DataFrame()
        N_df_tour=pd.DataFrame()
        N_df_carrier=pd.DataFrame()    
        for count_num in county_list:
            df_payload = pd.read_csv(f_dir+"{0}_county{1}_payload_s{2}_y{3}.csv".format(ship_type, count_num,scenario,target_year)).reset_index()
            df_tour = pd.read_csv(f_dir+"{0}_county{1}_freight_tours_s{2}_y{3}.csv".format(ship_type, count_num,scenario,target_year)).reset_index()
            df_carrier = pd.read_csv(f_dir+"{0}_county{1}_carrier_s{2}_y{3}.csv".format(ship_type, count_num,scenario,target_year)).reset_index()

            df_carrier["tourId"]=df_carrier["tourId"].apply(lambda x: x+tour_num)
            df_payload["tourId"]=df_payload["tourId"].apply(lambda x: x+tour_num)
            df_tour["tour_id"]=df_tour["tour_id"].apply(lambda x: x+tour_num)
            
            tour_num=df_carrier["tourId"].iloc[-1]+1
            N_df_payload=pd.concat([N_df_payload,df_payload], ignore_index=True).reset_index(drop=True)
            N_df_tour=pd.concat([N_df_tour,df_tour], ignore_index=True).reset_index(drop=True)
            N_df_carrier=pd.concat([N_df_carrier,df_carrier], ignore_index=True).reset_index(drop=True)

        N_df_payload.to_csv(f_dir_2+"{0}_all_payload_s{1}_y{2}.csv".format(ship_type,scenario,target_year), index = False, header=True)
        N_df_tour.to_csv(f_dir_2+"{0}_all_freight_tours_s{1}_y{2}.csv".format(ship_type,scenario,target_year), index = False, header=True)
        N_df_carrier.to_csv(f_dir_2+"{0}_all_carrier_s{1}_y{2}.csv".format(ship_type,scenario,target_year), index = False, header=True)
        print ("{},{}:{}".format(ship_type,scenario,N_df_tour.shape[0]))  
# %%
