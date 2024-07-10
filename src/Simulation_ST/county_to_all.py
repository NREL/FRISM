# %%

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
county_list=[61,33,53,35]
target_year="2018"
f_dir="../../../FRISM_input_output_ST/result_0423/Tour_plan/{}/".format(target_year)
f_dir_2="../../../FRISM_input_output_ST/result_0423/Tour_plan/{}_all/".format(target_year)
s_list=["Base"]
#s_list=["HOP_highp2", "HOP_highp6","Ref_highp2", "Ref_highp6"]
#s_list=["Dmd_G"]
# s_list=["Dmd_G", "Dmd_G120", "Dmd_G140", "Dmd_G160","Dmd_G180"]
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
#%%

county_list=[1, 13, 41, 55, 75, 81, 85, 95, 97]
target_year="2050"
f_dir="../../../FRISM_input_output_SF/R_HPC_0102_24/Tour_plan/{}/".format(target_year)
f_dir_2="../../../FRISM_input_output_SF/R_HPC_0102_24/Tour_plan/{}_all/".format(target_year)
#s_list=["Base"]
s_list=["HOP_highp2", "HOP_highp6","Ref_highp2", "Ref_highp6"]
#s_list=["Dmd_G"]
# s_list=["Dmd_G", "Dmd_G120", "Dmd_G140", "Dmd_G160","Dmd_G180"]
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

county_list=[1, 13, 41, 55, 75, 81, 85, 95, 97]
target_year="2040"
f_dir="../../..//Results_from_HPC_sfn_v2/Tour_plan/{}/".format(target_year)
f_dir_2="../../../Results_from_HPC_sfn_v2/Tour_plan/{}_all/".format(target_year)
#s_list=["Base"]
#s_list=["HOP_highp2", "HOP_highp6","Ref_highp2", "Ref_highp6"]
#s_list=["Dmd_G"]
s_list=["Dmd_G", "Dmd_G120", "Dmd_G140", "Dmd_G160","Dmd_G180"]
# s_list=["HOP_highp2", "HOP_highp4", "HOP_highp6","HOP_highp8","HOP_highp10",
# "Ref_highp2", "Ref_highp4", "Ref_highp6","Ref_highp8","Ref_highp10"]
for scenario in s_list:
    for ship_type in ["B2B", "B2C"]:
    #for ship_type in ["B2C"]:    
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
f_dir="../../..//Results_from_HPC_sfn_v2/Shipment2Fleet/{}/".format(target_year)
for scenario in s_list:
    #for ship_type in ["B2B", "B2C"]:
    for ship_type in ["B2C"]:    
        N_df_payload=pd.DataFrame()
        for count_num in county_list:
            df_payload = pd.read_csv(f_dir+"{0}_payload_county{1}_shipall_s{2}_y{3}_sr13.csv".format(ship_type, count_num,scenario,target_year)).reset_index()
            N_df_payload=pd.concat([N_df_payload,df_payload], ignore_index=True).reset_index(drop=True)
  
        print ("{},{}:{}".format(ship_type,scenario,N_df_payload.shape[0]))  
# %%
f_dir="../../../Results_from_HPC_sfn_v1/Tour_plan/{}_all/".format(target_year)
f_dir_2= "../../../Results_from_HPC_sfn_v1/Tour_plan/{}_all/".format(target_year)

sample_target={"B2B":6950, 
                "B2C":1040}
y="2050"
for ship_type in ["B2B", "B2C"]:
    for s in s_list:
        df_payload = pd.read_csv(f_dir+"{0}_all_payload_s{1}_y{2}.csv".format(ship_type,s,y)).reset_index()
        df_tour = pd.read_csv(f_dir+"{0}_all_freight_tours_s{1}_y{2}.csv".format(ship_type,s,y)).reset_index()
        df_carrier = pd.read_csv(f_dir+"{0}_all_carrier_s{1}_y{2}.csv".format(ship_type,s,y)).reset_index()
        list_tour=random.sample(list(df_carrier["tourId"].unique()),sample_target[ship_type])
        df_payload = df_payload[df_payload["tourId"].isin(list_tour)]
        df_tour = df_tour[df_tour["tour_id"].isin(list_tour)]
        df_carrier = df_carrier[df_carrier["tourId"].isin(list_tour)]
        df_payload.to_csv(f_dir_2+"{0}_all_payload_s{1}_y{2}.csv".format(ship_type,s,y), index = False, header=True)
        df_tour.to_csv(f_dir_2+"{0}_all_freight_tours_s{1}_y{2}.csv".format(ship_type,s,y), index = False, header=True)
        df_carrier.to_csv(f_dir_2+"{0}_all_carrier_s{1}_y{2}.csv".format(ship_type,s,y), index = False, header=True)  
#%%
for ship_type in ["B2B", "B2C"]:
    for s in s_list:
        df_payload = pd.read_csv(f_dir+"{0}_all_payload_s{1}_y{2}.csv".format(ship_type,s,y))
        df_tour = pd.read_csv(f_dir+"{0}_all_freight_tours_s{1}_y{2}.csv".format(ship_type,s,y))
        df_carrier = pd.read_csv(f_dir+"{0}_all_carrier_s{1}_y{2}.csv".format(ship_type,s,y))
        
        df_payload  = df_payload.drop(["level_0","index"], axis=1)
        df_tour     = df_tour.drop(["level_0","index"], axis=1)   
        df_carrier  = df_carrier.drop(["level_0","index"], axis=1) 
        
        df_payload.to_csv(f_dir_2+"{0}_all_payload_s{1}_y{2}.csv".format(ship_type,s,y), index = False, header=True)
        df_tour.to_csv(f_dir_2+"{0}_all_freight_tours_s{1}_y{2}.csv".format(ship_type,s,y), index = False, header=True)
        df_carrier.to_csv(f_dir_2+"{0}_all_carrier_s{1}_y{2}.csv".format(ship_type,s,y), index = False, header=True)
# %%
# check the file:
ship_type="B2B"
scenario="Dmd_G"
target_year="2018"
f_dir="/Users/kjeong/KJ_NREL_Work/1_Work/1_2_SMART_2_0/Model_development/Results_dmd_v1/Tour_plan/2018_base/"
df_payload = pd.read_csv(f_dir+"{0}_all_payload_s{1}_y{2}.csv".format(ship_type,scenario,target_year)).reset_index()
df_tour = pd.read_csv(f_dir+"{0}_all_freight_tours_s{1}_y{2}.csv".format(ship_type,scenario,target_year)).reset_index()
df_carrier = pd.read_csv(f_dir+"{0}_all_carrier_s{1}_y{2}.csv".format(ship_type,scenario,target_year)).reset_index()

df_tour_length=df_payload.groupby(['tourId'])['tourId'].count().reset_index(name='tour_leng')

df_carrier['tour_length'] = df_tour_length['tour_leng']-2

df_tour_results=df_carrier.groupby(['vehicleTypeId']).aggregate(max= ("tour_length",'max'),mdeian= ("tour_length",'median'),mean= ("tour_length",'mean')) 


df_tour_results=df_carrier.groupby(['vehicleTypeId'])['tour_length'].quantile(q=0.95)