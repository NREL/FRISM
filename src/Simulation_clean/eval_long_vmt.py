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
# %%
import seaborn as sns
import matplotlib.pyplot as plt
# %%
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth's radius in kilometers

    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))

    distance = R * c
    return distance

# %%
target_year="2018"
ship_type="B2B"
count_num=55
scenario="Base"
f_dir="../../../FRISM_input_output_SF/result_0102/Tour_plan/{}/".format(target_year)
df_payload = pd.read_csv(f_dir+"{0}_county{1}_payload_s{2}_y{3}.csv".format(ship_type, count_num,scenario,target_year))


df_payload["distance"]=0
for i in range(0,df_payload.shape[0]):
    if df_payload["sequenceRank"].iloc[i] !=0:
        df_payload["distance"].iloc[i]=haversine_distance(df_payload['locationZone_y'].iloc[i-1], df_payload['locationZone_x'].iloc[i-1],
                                                        df_payload['locationZone_y'].iloc[i], df_payload['locationZone_x'].iloc[i]
                                                            )/1.609
df_carrier = pd.read_csv(f_dir+"{0}_county{1}_carrier_s{2}_y{3}.csv".format(ship_type, count_num,scenario,target_year))
df_carrier["distance"]=0
for i in range(0,df_carrier.shape[0]):
    tourId=df_carrier["tourId"].iloc[i]
    df_carrier["distance"].iloc[i]= df_payload[df_payload["tourId"]==tourId]["distance"].sum()

df_payload.to_csv(f_dir+"{0}_county{1}_payload_s{2}_y{3}.csv".format(ship_type, count_num,scenario,target_year), index = False, header=True)
df_carrier.to_csv(f_dir+"{0}_county{1}_carrier_s{2}_y{3}.csv".format(ship_type, count_num,scenario,target_year), index = False, header=True)
df_payload_old=df_payload
df_carrier_old=df_carrier
# %%
target_year="2018"
ship_type="B2B"
count_num=55
scenario="Base"
f_dir="../../../FRISM_input_output_SF/result_1023/Tour_plan/{}/".format(target_year)

df_payload = pd.read_csv(f_dir+"{0}_county{1}_payload_s{2}_y{3}.csv".format(ship_type, count_num,scenario,target_year))

df_payload["distance"]=0
for i in range(0,df_payload.shape[0]):
    if df_payload["sequenceRank"].iloc[i] !=0:
        df_payload["distance"].iloc[i]=haversine_distance(df_payload['locationZone_y'].iloc[i-1], df_payload['locationZone_x'].iloc[i-1],
                                                        df_payload['locationZone_y'].iloc[i], df_payload['locationZone_x'].iloc[i]
                                                            )/1.609
df_carrier = pd.read_csv(f_dir+"{0}_county{1}_carrier_s{2}_y{3}.csv".format(ship_type, count_num,scenario,target_year))
df_carrier["distance"]=0
for i in range(0,df_carrier.shape[0]):
    tourId=df_carrier["tourId"].iloc[i]
    df_carrier["distance"].iloc[i]= df_payload[df_payload["tourId"]==tourId]["distance"].sum()

df_payload.to_csv(f_dir+"{0}_county{1}_payload_s{2}_y{3}.csv".format(ship_type, count_num,scenario,target_year), index = False, header=True)
df_carrier.to_csv(f_dir+"{0}_county{1}_carrier_s{2}_y{3}.csv".format(ship_type, count_num,scenario,target_year), index = False, header=True)
# %%
target_year="2018"
ship_type="B2B"
count_num=55
scenario="Base"
f_dir="../../../FRISM_input_output_SF/result_0922/Tour_plan/{}/".format(target_year)

df_payload = pd.read_csv(f_dir+"{0}_county{1}_payload_s{2}_y{3}.csv".format(ship_type, count_num,scenario,target_year))

df_payload["distance"]=0
for i in range(0,df_payload.shape[0]):
    if df_payload["sequenceRank"].iloc[i] !=0:
        df_payload["distance"].iloc[i]=haversine_distance(df_payload['locationZone_y'].iloc[i-1], df_payload['locationZone_x'].iloc[i-1],
                                                        df_payload['locationZone_y'].iloc[i], df_payload['locationZone_x'].iloc[i]
                                                            )/1.609
df_carrier = pd.read_csv(f_dir+"{0}_county{1}_carrier_s{2}_y{3}.csv".format(ship_type, count_num,scenario,target_year))
df_carrier["distance"]=0
for i in range(0,df_carrier.shape[0]):
    tourId=df_carrier["tourId"].iloc[i]
    df_carrier["distance"].iloc[i]= df_payload[df_payload["tourId"]==tourId]["distance"].sum()

df_payload.to_csv(f_dir+"{0}_county{1}_payload_s{2}_y{3}.csv".format(ship_type, count_num,scenario,target_year), index = False, header=True)
df_carrier.to_csv(f_dir+"{0}_county{1}_carrier_s{2}_y{3}.csv".format(ship_type, count_num,scenario,target_year), index = False, header=True)
df_carrier.groupby(['vehicleTypeId'])['vehicleTypeId'].count()
# %%
print(df_carrier_old["distance"].min(), df_carrier["distance"].min())
# %%
print(df_carrier_old["distance"].max(), df_carrier["distance"].max())

# %%
print(df_carrier_old["distance"].sum(), df_carrier["distance"].sum())
# %%
print(df_carrier_old.shape[0], df_carrier["distance"].shape[0])
# %%
print(df_carrier_old["distance"].median(), df_carrier["distance"].median())

temp=df_carrier[df_carrier["distance"]>250]
# %%
# %%
temp=df_carrier[df_carrier["distance"]>0]
# %%
target_year="2018"
ship_type="B2B"
count_num=55
scenario="Base"
f_dir="../../../FRISM_input_output_SF/result_0102/Tour_plan/{}/".format(target_year)
df_payload_old = pd.read_csv(f_dir+"{0}_county{1}_payload_s{2}_y{3}.csv".format(ship_type, count_num,scenario,target_year))
f_dir="../../../FRISM_input_output_SF/result_0922/Tour_plan/{}/".format(target_year)
df_payload = pd.read_csv(f_dir+"{0}_county{1}_payload_s{2}_y{3}.csv".format(ship_type, count_num,scenario,target_year))

fig, ax = plt.subplots()
sns.kdeplot(data=df_payload[(df_payload["distance"]>0) & (df_payload["tourId"]<74)], x="distance", label="new", ax=ax)
sns.kdeplot(data=df_payload_old[(df_payload["distance"]>0) & (df_payload["tourId"]<76)], x="distance", label="old", ax=ax)
plt.legend()
plt.show()
# %%
# fig, ax = plt.subplots()
# sns.kdeplot(data=df_payload[(df_payload["distance"]>0) & (df_payload["truck_mode"]=="Private Truck")], x="distance", label="new", ax=ax)
# sns.kdeplot(data=df_payload_old[df_payload_old["distance"]>0], x="distance", label="old", ax=ax)
# plt.legend()
# plt.show()
# %%

for ship_type in ["B2B", "B2C"]:
    for count_num in [1, 13, 41, 55, 75, 81, 85, 95, 97]:

        target_year="2018"
        scenario="Base"
        f_dir="../../../FRISM_input_output_SF/result_0102/Tour_plan/{}/".format(target_year)
        df_payload = pd.read_csv(f_dir+"{0}_county{1}_payload_s{2}_y{3}.csv".format(ship_type, count_num,scenario,target_year)).reset_index()


        df_payload["distance"]=0
        for i in range(0,df_payload.shape[0]):
            if df_payload["sequenceRank"].iloc[i] !=0:
                df_payload["distance"].iloc[i]=haversine_distance(df_payload['locationZone_y'].iloc[i-1], df_payload['locationZone_x'].iloc[i-1],
                                                                df_payload['locationZone_y'].iloc[i], df_payload['locationZone_x'].iloc[i]
                                                                    )/1.609
        df_carrier = pd.read_csv(f_dir+"{0}_county{1}_carrier_s{2}_y{3}.csv".format(ship_type, count_num,scenario,target_year)).reset_index()
        df_carrier["distance"]=0
        for i in range(0,df_carrier.shape[0]):
            tourId=df_carrier["tourId"].iloc[i]
            df_carrier["distance"].iloc[i]= df_payload[df_payload["tourId"]==tourId]["distance"].sum()

        df_payload.to_csv(f_dir+"{0}_county{1}_payload_s{2}_y{3}.csv".format(ship_type, count_num,scenario,target_year), index = False, header=True)
        df_carrier.to_csv(f_dir+"{0}_county{1}_carrier_s{2}_y{3}.csv".format(ship_type, count_num,scenario,target_year), index = False, header=True)
        df_payload_old=df_payload
        df_carrier_old=df_carrier
        #########
        target_year="2018"

        scenario="Base"
        f_dir="../../../FRISM_input_output_SF/result_0922/Tour_plan/{}/".format(target_year)

        df_payload = pd.read_csv(f_dir+"{0}_county{1}_payload_s{2}_y{3}.csv".format(ship_type, count_num,scenario,target_year)).reset_index()

        df_payload["distance"]=0
        for i in range(0,df_payload.shape[0]):
            if df_payload["sequenceRank"].iloc[i] !=0:
                df_payload["distance"].iloc[i]=haversine_distance(df_payload['locationZone_y'].iloc[i-1], df_payload['locationZone_x'].iloc[i-1],
                                                                df_payload['locationZone_y'].iloc[i], df_payload['locationZone_x'].iloc[i]
                                                                    )/1.609
        df_carrier = pd.read_csv(f_dir+"{0}_county{1}_carrier_s{2}_y{3}.csv".format(ship_type, count_num,scenario,target_year)).reset_index()
        df_carrier["distance"]=0
        for i in range(0,df_carrier.shape[0]):
            tourId=df_carrier["tourId"].iloc[i]
            df_carrier["distance"].iloc[i]= df_payload[df_payload["tourId"]==tourId]["distance"].sum()

        df_payload.to_csv(f_dir+"{0}_county{1}_payload_s{2}_y{3}.csv".format(ship_type, count_num,scenario,target_year), index = False, header=True)
        df_carrier.to_csv(f_dir+"{0}_county{1}_carrier_s{2}_y{3}.csv".format(ship_type, count_num,scenario,target_year), index = False, header=True)

        fig, ax = plt.subplots()
        sns.kdeplot(data=df_carrier[df_carrier["distance"]>0], x="distance", label="new", ax=ax)
        sns.kdeplot(data=df_carrier_old[df_carrier_old["distance"]>0], x="distance", label="old", ax=ax)
        plt.title("Density Plots {}_county{}".format(ship_type, count_num))
        plt.legend()
        plt.savefig("../../../FRISM_input_output_SF/result_test/'dist_dist_{0}_county{1}.png".format(ship_type, count_num))
# %%
