## Note: To test the codes: In def main(), put for loop is restricted:
### please comment out the followings for the entire run. 
### if args.ship_type == "B2C": ... #for i in range(0,df_hh_D_GrID.shape[0]):
### elif args.ship_type == "B2B": ...#for i in range(0,FH_Seller.shape[0]): 
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
# %%
f_dir="../../../Results_veh_tech_v1/"
f_dir_2= "../../../Results_veh_tech_v1/"
year_list=["2050"]
s_list=["HOP_highp2", "HOP_highp4", "HOP_highp6","HOP_highp8","HOP_highp10",
"Ref_highp2", "Ref_highp4", "Ref_highp6","Ref_highp8","Ref_highp10"]
county_list=["453", "491", "209", "55", "21", "53"]
sample_target={"B2B":{"21": 500, "53": 500, "55": 500, "209":500, "453":500, "491":500}, 
                "B2C":{"21": 500, "53": 500, "55": 500, "209":500, "453":500, "491":500} }

for ship_type in ["B2B", "B2C"]:
    for y in year_list:
        for s in s_list:
            for c in county_list:
                df_payload = pd.read_csv(f_dir+"{0}_county{1}_payload_s{2}_y{3}.csv".format(ship_type, c,s,y)).reset_index()
                df_tour = pd.read_csv(f_dir+"{0}_county{1}_freight_tours_s{2}_y{3}.csv".format(ship_type, c,s,y)).reset_index()
                df_carrier = pd.read_csv(f_dir+"{0}_county{1}_carrier_s{2}_y{3}.csv".format(ship_type, c,s,y)).reset_index()
                list_tour=random.sample(list(df_carrier["tourId"].unique),sample_target[ship_type][s])
                df_payload = df_payload[df_payload["tourId"].isin(list_tour)]
                df_tour = df_tour[df_tour["tour_id"].isin(list_tour)]  
                df_carrier = df_carrier[df_carrier["tourId"].isin(list_tour)]
                df_payload.to_csv(f_dir_2+"{0}_county{1}_payload_s{2}_y{3}.csv".format(ship_type, c,s,y), index = False, header=True)
                df_tour.to_csv(f_dir_2+"{0}_county{1}_freight_tours_s{2}_y{3}.csv".format(ship_type, c,s,y), index = False, header=True)
                df_carrier.to_csv(f_dir_2+"{0}_county{1}_carrier_s{2}_y{3}.csv".format(ship_type, c,s,y), index = False, header=True)               
#%