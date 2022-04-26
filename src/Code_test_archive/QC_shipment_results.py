
# %%
from matplotlib.image import AxesImage
import pandas as pd
import numpy as np
#import geopandas as gpd
#import networkx as nx
import matplotlib.pyplot as plt
from argparse import ArgumentParser
import seaborn as sns
import geopandas as gpd
#import osmnx as ox
#import plotly.graph_objects as gor
# %%
################################# QC V1 #####################
f_dir="/Users/kjeong/NREL/1_Work/1_2_SMART_2_0/Model_development/Results_from_HPC/Tour_plan/"

county_list=[1, 13, 41, 55, 75, 81, 85, 95, 97]
b2b_carrier=0
b2b_veh =0

b2c_carrier=0
b2c_veh =0

for county in county_list:
    df = pd.read_csv(f_dir+"B2B_county{}_carrier_xy.csv".format(county))
    b2b_carrier += df['carrierId'].nunique()
    b2b_veh +=df['tourId'].nunique()

for county in county_list:
    df = pd.read_csv(f_dir+"B2C_county{}_carrier_xy.csv".format(county))
    b2c_carrier += df['carrierId'].nunique()
    b2c_veh +=df['tourId'].nunique()

print ("num_carrier sum: {0}, b2b: {1}, b2c: {2}".format(b2b_carrier+b2c_carrier,b2b_carrier,b2c_carrier))
print ("num_veh sum: {0}, b2b: {1}, b2c: {2}".format(b2b_veh+b2c_veh,b2b_veh,b2c_veh))
# %%
################################# QC V2 #####################
f_dir="/Users/kjeong/NREL/1_Work/1_2_SMART_2_0/Model_development/"

county_list=[1, 13, 41, 55, 75, 81, 85, 95, 97]

df_for_qc=pd.DataFrame(county_list, columns =["county"])
# df_for_qc["B2B_ship_v1"]=0
# df_for_qc["B2B_carr_v1"]=0
# df_for_qc["B2B_veh_v1"]=0
# df_for_qc["B2C_ship_v1"]=0
# df_for_qc["B2C_carr_v1"]=0
# df_for_qc["B2C_veh_v1"]=0

# df_for_qc["B2B_ship_v2"]=0
# df_for_qc["B2B_carr_v2"]=0
# df_for_qc["B2B_veh_v2"]=0
# df_for_qc["B2C_ship_v2"]=0
# df_for_qc["B2C_carr_v2"]=0
# df_for_qc["B2C_veh_v2"]=0

df_for_qc["B2B_ship_v1"]=0
df_for_qc["B2B_ship_v2"]=0
df_for_qc["B2B_carr_v1"]=0
df_for_qc["B2B_carr_v2"]=0
df_for_qc["B2B_veh_v1"]=0
df_for_qc["B2B_veh_v2"]=0
df_for_qc["B2C_ship_v1"]=0
df_for_qc["B2C_ship_v2"]=0
df_for_qc["B2C_carr_v1"]=0
df_for_qc["B2C_carr_v2"]=0
df_for_qc["B2C_veh_v1"]=0
df_for_qc["B2C_veh_v2"]=0

for i in range (0, df_for_qc.shape[0]):
    county=df_for_qc.loc[i,"county"]
    for s_type in ["B2B", "B2C"]:
        try:
            df_ship_v1= pd.read_csv(f_dir+"Results_from_HPC_v5/Shipment2Fleet/"+"{}_payload_county{}_shipall.csv".format(s_type,county))
            df_for_qc.loc[i,s_type+"_ship_v1"]=df_ship_v1.shape[0]
            df_car_v1= pd.read_csv(f_dir+"Results_from_HPC_v5/Tour_plan/"+"{}_county{}_carrier.csv".format(s_type,county))
            df_for_qc.loc[i,s_type+"_carr_v1"]= df_car_v1['carrierId'].nunique()
            df_for_qc.loc[i,s_type+"_veh_v1"]=df_car_v1['tourId'].nunique()
        except:
            print ("no file v1 for {}_county {}".format(s_type,county))
        try: 
            df_ship_v2= pd.read_csv(f_dir+"FRISM_input_output_SF/Sim_outputs/Shipment2Fleet/"+"{}_payload_county{}_shipall.csv".format(s_type,county))
            df_for_qc.loc[i,s_type+"_ship_v2"]=df_ship_v2.shape[0]
            df_car_v2= pd.read_csv(f_dir+"FRISM_input_output_SF/Sim_outputs/Tour_plan/"+"{}_county{}_carrier.csv".format(s_type,county))
            df_for_qc.loc[i,s_type+"_carr_v2"]= df_car_v2['carrierId'].nunique()
            df_for_qc.loc[i,s_type+"_veh_v2"]=df_car_v2['tourId'].nunique()
        except:
            print ("no file v2 for {}_county {}".format(s_type,county))    

df_for_qc.to_csv("/Users/kjeong/NREL/1_Work/1_2_SMART_2_0/Model_development/FRISM_input_output_SF/Validation/Sim_result_QC_0425.csv")

# %%
f_dir="../../../FRISM_input_output_SF/Sim_outputs/Tour_plan/"
v_type= "B2C"
county_list=[1, 13, 41, 55, 75, 81, 85, 95, 97]
for county in county_list:
    print ("checking county {}".format(county))
    df_payload = pd.read_csv(f_dir+"{}_county{}_payload.csv".format(v_type,str(county)))
    for i in range(0,df_payload.shape[0]):
        if pd.isnull(df_payload.loc[i,"locationZone_x"]):
            print("null exist in county {}".format(county))