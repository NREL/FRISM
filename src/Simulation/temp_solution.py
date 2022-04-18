# %%
import pandas as pd
import numpy as np
import geopandas as gpd
from argparse import ArgumentParser
import random
import config
import glob
from os.path import exists as file_exists
from alive_progress import alive_bar
import time
from shapely.geometry import Point
import sys
county = sys.argv[1]
#county =41
print ("Processing {} county shipment data".format(county))
# %%
fdir_in_out= "../../../FRISM_input_output_SF"
fdir_geo= fdir_in_out+'/Sim_inputs/Geo_data/'
CBG_file= 'sfbay_freight.geojson'

CBGzone_df = gpd.read_file(fdir_geo+CBG_file)
CBGzone_df["GEOID"]=CBGzone_df["GEOID"].astype(str)
## Add county id from GEOID
CBGzone_df["County"]=CBGzone_df["GEOID"].apply(lambda x: x[2:5] if len(x)>=12 else 0)
CBGzone_df["County"]=CBGzone_df["County"].astype(str).astype(int)
CBGzone_df["GEOID"]=CBGzone_df["GEOID"].astype(str).astype(int)
# %%
def random_points_in_polygon(polygon):
    temp = polygon.bounds
    finished= False
    while not finished:
        point = Point(random.uniform(temp.minx.values[0], temp.maxx.values[0]), random.uniform(temp.miny, temp.maxy.values[0]))
        finished = polygon.contains(point).values[0]
    return [point.x, point.y]

# %%
f_dir="../../../FRISM_input_output_SF/Sim_outputs/Shipment2Fleet/"
#f_dir="../../../Results_from_HPC_v3/Shipment2Fleet/"

df_carr=pd.read_csv(f_dir+"B2B_carrier_county{}_shipall.csv".format(county))
df_pay=pd.read_csv(f_dir+"B2B_payload_county{}_shipall.csv".format(county))

# %%
new_df_pay=pd.DataFrame()
new_df_carr=pd.DataFrame()
for c_id in df_carr["carrier_id"].unique():
#for c_id in ["B2B_1006810_4976","B2B_1006812_4977"]:    
    temp_pay_md= df_pay[(df_pay["carrier_id"]==c_id) & (df_pay["veh_type"]=="md")].reset_index(drop=True)
    temp_pay_hd= df_pay[(df_pay["carrier_id"]==c_id) & (df_pay["veh_type"]=="hd")].reset_index(drop=True)
    temp_carr_md = df_carr[df_carr["carrier_id"]==c_id].reset_index(drop=True)
    temp_carr_hd = df_carr[df_carr["carrier_id"]==c_id].reset_index(drop=True)
    num_md = temp_pay_md.shape[0]
    num_hd = temp_pay_hd.shape[0]

    if num_md ==0:
        temp_carr_md = pd.DataFrame()
    elif num_md <= 30 and num_md >0:
        new_c_id=c_id+"m"
        temp_pay_md["carrier_id"] = new_c_id
        temp_carr_md["carrier_id"] = new_c_id
        temp_carr_md["num_veh_type_1"] =num_md
        temp_carr_md["num_veh_type_2"] =0
    else: 
        for i in range(0,temp_pay_md.shape[0]):
            new_c_id=c_id+"m{}".format(str(int(i/30)))
            temp_pay_md.loc[i,"carrier_id"] = new_c_id
        break_num=int(num_md/30)+1
        temp_carr_md=pd.concat([temp_carr_md]*break_num, ignore_index=True).reset_index(drop=True)
        for i in range(0,temp_carr_md.shape[0]):
            new_c_id=c_id+"m{}".format(str(i))
            temp_carr_md.loc[i,"carrier_id"] = new_c_id
            temp_carr_md["num_veh_type_1"] =30
            temp_carr_md["num_veh_type_2"] =0                    
    if num_hd ==0:
        temp_carr_hd = pd.DataFrame()
    elif num_hd <= 30 and num_hd >0:
        new_c_id=c_id+"h"
        temp_pay_hd["carrier_id"] = new_c_id
        temp_carr_hd["carrier_id"] = new_c_id
        temp_carr_hd["num_veh_type_1"] =0
        temp_carr_hd["num_veh_type_2"] =num_hd
    else: 
        for i in range(0,temp_pay_hd.shape[0]):
            new_c_id=c_id+"h{}".format(str(int(i/30)))
            temp_pay_hd.loc[i,"carrier_id"] = new_c_id
        break_num=int(num_hd/30)+1
        temp_carr_hd=pd.concat([temp_carr_hd]*break_num, ignore_index=True).reset_index(drop=True)
        for i in range(0,temp_carr_hd.shape[0]):
            new_c_id=c_id+"h{}".format(str(i))
            temp_carr_hd.loc[i,"carrier_id"] = new_c_id
            temp_carr_hd["num_veh_type_1"] =0
            temp_carr_hd["num_veh_type_2"] =30
    new_df_pay=pd.concat([new_df_pay,temp_pay_md, temp_pay_hd], ignore_index=True).reset_index(drop=True)
    new_df_carr=pd.concat([new_df_carr,temp_carr_md, temp_carr_hd ], ignore_index=True).reset_index(drop=True) 

print ("missing x,y locations")
# %%
with alive_bar(new_df_pay.shape[0], force_tty=True) as bar:
    for i in range(0,new_df_pay.shape[0]):
        if new_df_pay.loc[i,"job"] =="delivery":
            if pd.isnull(new_df_pay.loc[i,"del_x"]):
                [x,y]=random_points_in_polygon(CBGzone_df.geometry[CBGzone_df.MESOZONE==new_df_pay.loc[i,"del_zone"]])
                new_df_pay.loc[i,'del_x']=x
                new_df_pay.loc[i,'del_y']=y 
        elif new_df_pay.loc[i,"job"] =="pickup_delivery":
            if pd.isnull(new_df_pay.loc[i,"del_x"]):
                [x,y]=random_points_in_polygon(CBGzone_df.geometry[CBGzone_df.MESOZONE==new_df_pay.loc[i,"del_zone"]])
                new_df_pay.loc[i,'del_x']=x
                new_df_pay.loc[i,'del_y']=y
            if pd.isnull(new_df_pay.loc[i,"pu_x"]):
                [x,y]=random_points_in_polygon(CBGzone_df.geometry[CBGzone_df.MESOZONE==new_df_pay.loc[i,"pu_zone"]])
                new_df_pay.loc[i,'pu_x']=x
                new_df_pay.loc[i,'pu_y']=y      
        bar()

file_num=10
new_df_carr.to_csv(f_dir+"B2B_carrier_county{}_shipall_A.csv".format(county), index = False, header=True)
new_df_pay.to_csv(f_dir+"B2B_payload_county{}_shipall_A.csv".format(county), index = False, header=True)
carrier_list=new_df_pay["carrier_id"].unique()

for i in range(0, file_num):
    new_df_pay_break= new_df_pay[new_df_pay["carrier_id"].isin(carrier_list[i::file_num])]
    new_df_pay_break.to_csv(f_dir+"B2B_payload_county{}_shipall_{}.csv".format(county,i), index = False, header=True)

print ("complete the job")
# %%
# num=0
# for i in range(0, file_num):
#     new_df_pay_break=pd.read_csv(f_dir+"B2B_payload_county{}_shipall_{}.csv".format(county,i))
#     num +=new_df_pay_break.shape[0]
