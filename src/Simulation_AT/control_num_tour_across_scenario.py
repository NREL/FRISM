## Note: To test the codes: In def main(), put for loop is restricted:
### please comment out the followings for the entire run. 
### if args.ship_type == "B2C": ... #for i in range(0,df_hh_D_GrID.shape[0]):
### elif args.ship_type == "B2B": ...#for i in range(0,FH_Seller.shape[0]): 
# %%
from hashlib import shake_128
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
#%%
f_dir="../../../Results_veh_tech_v2/Tour_plan/2050/"
f_dir_2="../../../Results_veh_tech_v2/Tour_plan/2050_all/"
county_list=["453", "491", "209", "55", "21", "53"]
target_year="2050"
s_list=["HOP_highp2", "HOP_highp4", "HOP_highp6","HOP_highp8","HOP_highp10",
"Ref_highp2", "Ref_highp4", "Ref_highp6","Ref_highp8","Ref_highp10"]
for ship_type in ["B2B", "B2C"]:
    for scenario in s_list:
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
f_dir="../../../Results_veh_tech_v2/Tour_plan/2050_all/"
f_dir_2= "../../../Results_veh_tech_v2/Tour_plan/2050_all/"
s_list=["HOP_highp2", "HOP_highp4", "HOP_highp6","HOP_highp8","HOP_highp10",
"Ref_highp2", "Ref_highp4", "Ref_highp6","Ref_highp8","Ref_highp10"]
county_list=["453", "491", "209", "55", "21", "53"]
sample_target={"B2B":31795, 
                "B2C":2522}
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
# f_dir="../../../Results_veh_tech_v2/"
# f_dir_2= "../../../Results_veh_tech_v2/"
# year_list=["2050"]
# s_list=["HOP_highp2", "HOP_highp4", "HOP_highp6","HOP_highp8","HOP_highp10",
# "Ref_highp2", "Ref_highp4", "Ref_highp6","Ref_highp8","Ref_highp10"]
# county_list=["453", "491", "209", "55", "21", "53"]
# sample_target={"B2B":{"21": 0, "53": 4500, "55": 930, "209":0, "453":16000 , "491":6800}, 
#                 "B2C":{"21": 0, "53": 0, "55": 0, "209":0, "453":1050, "491":500} }

# for ship_type in ["B2B", "B2C"]:
#     for y in year_list:
#         for s in s_list:
#             for c in county_list:
#                 df_payload = pd.read_csv(f_dir+"{0}_county{1}_payload_s{2}_y{3}.csv".format(ship_type, c,s,y)).reset_index()
#                 df_tour = pd.read_csv(f_dir+"{0}_county{1}_freight_tours_s{2}_y{3}.csv".format(ship_type, c,s,y)).reset_index()
#                 df_carrier = pd.read_csv(f_dir+"{0}_county{1}_carrier_s{2}_y{3}.csv".format(ship_type, c,s,y)).reset_index()
#                 list_tour=random.sample(list(df_carrier["tourId"].unique),sample_target[ship_type][s])
#                 df_payload = df_payload[df_payload["tourId"].isin(list_tour)]
#                 df_tour = df_tour[df_tour["tour_id"].isin(list_tour)]  
#                 df_carrier = df_carrier[df_carrier["tourId"].isin(list_tour)]
#                 df_payload.to_csv(f_dir_2+"{0}_county{1}_payload_s{2}_y{3}.csv".format(ship_type, c,s,y), index = False, header=True)
#                 df_tour.to_csv(f_dir_2+"{0}_county{1}_freight_tours_s{2}_y{3}.csv".format(ship_type, c,s,y), index = False, header=True)
#                 df_carrier.to_csv(f_dir_2+"{0}_county{1}_carrier_s{2}_y{3}.csv".format(ship_type, c,s,y), index = False, header=True)               
#%
# %
## file move
import shutil 
f_dir="../../../Results_veh_tech_v2/Tour_plan/"
year= "2050"
s_list=["HOP_highp2", "HOP_highp4", "HOP_highp6","HOP_highp8","HOP_highp10",
"Ref_highp2", "Ref_highp4", "Ref_highp6","Ref_highp8","Ref_highp10"]
for s in s_list:
    target_dir=f_dir + year+"_"+s+"/"
    if not file_exists(target_dir):
        os.makedirs(target_dir)
    for ship_type in ["B2B", "B2C"]:
        s1= f_dir+"2050_all/{0}_all_payload_s{1}_y{2}.csv".format(ship_type,s,year)
        s2=f_dir+"2050_all/{0}_all_freight_tours_s{1}_y{2}.csv".format(ship_type,s,year)
        s3=f_dir+"2050_all/{0}_all_carrier_s{1}_y{2}.csv".format(ship_type,s,year)    
        shutil.move(s1,target_dir)  
        shutil.move(s2,target_dir)
        shutil.move(s3,target_dir)        
#%%
f_dir="../../../Results_veh_tech_v2/Tour_plan/"
f_dir_veh= "../../../Results_veh_tech_v2/Shipment2Fleet/"
year= "2050"
s_list=["HOP_highp2", "HOP_highp4", "HOP_highp6","HOP_highp8","HOP_highp10",
"Ref_highp2", "Ref_highp4", "Ref_highp6","Ref_highp8","Ref_highp10"]
for s in s_list:
    target_dir=f_dir + year+"_"+s+"/"
    if not file_exists(target_dir):
        os.makedirs(target_dir)
    s1= f_dir_veh+"2050/vehicle_types_s{}_y{}.csv".format(s,year)
    shutil.copy(s1,target_dir)  
     
# %%
