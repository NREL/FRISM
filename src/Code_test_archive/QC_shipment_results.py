
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
            df_ship_v1= pd.read_csv(f_dir+"Results_from_HPC_v8/Shipment2Fleet/"+"{}_payload_county{}_shipall.csv".format(s_type,county))
            df_for_qc.loc[i,s_type+"_ship_v1"]=df_ship_v1.shape[0]
            # df_car_v1= pd.read_csv(f_dir+"Results_from_HPC_v5/Tour_plan/"+"{}_county{}_carrier.csv".format(s_type,county))
            # df_for_qc.loc[i,s_type+"_carr_v1"]= df_car_v1['carrierId'].nunique()
            # df_for_qc.loc[i,s_type+"_veh_v1"]=df_car_v1['tourId'].nunique()
        except:
            print ("no file v1 for {}_county {}".format(s_type,county))
        try: 
            df_ship_v2= pd.read_csv(f_dir+"Results_from_HPC_v9/Shipment2Fleet/"+"{}_payload_county{}_shipall.csv".format(s_type,county))
            df_for_qc.loc[i,s_type+"_ship_v2"]=df_ship_v2.shape[0]
            # df_car_v2= pd.read_csv(f_dir+"FRISM_input_output_SF/Sim_outputs/Tour_plan/"+"{}_county{}_carrier.csv".format(s_type,county))
            # df_for_qc.loc[i,s_type+"_carr_v2"]= df_car_v2['carrierId'].nunique()
            # df_for_qc.loc[i,s_type+"_veh_v2"]=df_car_v2['tourId'].nunique()
        except:
            print ("no file v2 for {}_county {}".format(s_type,county))    

df_for_qc.to_csv("/Users/kjeong/NREL/1_Work/1_2_SMART_2_0/Model_development/FRISM_input_output_SF/Validation/Sim_result_QC_0929.csv")

# %%
f_dir="../../../FRISM_input_output_SF/Sim_outputs/Tour_plan/"
v_type= "B2B"
county_list=[1, 13, 41, 55, 75, 81, 85, 95, 97]
for county in county_list:
    print ("checking county {}".format(county))
    df_payload = pd.read_csv(f_dir+"{}_county{}_payload.csv".format(v_type,str(county)))
    for i in range(0,df_payload.shape[0]):
        if pd.isnull(df_payload.loc[i,"locationZone_x"]):
            print("null exist in county {}".format(county))
# %%
# AT check 

f_dir="../../../FRISM_input_output_AT/Sim_outputs/"
#f_dir="/Users/kjeong/NREL/1_Work/1_2_SMART_2_0/Model_development/FRISM_input_output_AT/Sim_outputs/"

county_list=[453, 491, 209, 55, 21, 53]
b2b_shipment=0
b2b_carrier=0
b2b_veh =0

b2c_shipment=0
b2c_carrier=0
b2c_veh =0


for county in county_list:
    df = pd.read_csv(f_dir+"Shipment2Fleet/B2B_payload_county{}_shipall_A.csv".format(county))
    b2b_shipment += df['payload_id'].nunique()

for county in county_list:
    df = pd.read_csv(f_dir+"Shipment2Fleet/B2C_payload_county{}_shipall.csv".format(county))
    b2c_shipment += df['payload_id'].nunique()


for county in county_list:
    df = pd.read_csv(f_dir+"Tour_plan/B2B_county{}_carrier.csv".format(county))
    b2b_carrier += df['carrierId'].nunique()
    b2b_veh +=df['tourId'].nunique()

for county in county_list:
    df = pd.read_csv(f_dir+"Tour_plan/B2C_county{}_carrier.csv".format(county))
    b2c_carrier += df['carrierId'].nunique()
    b2c_veh +=df['tourId'].nunique()

print ("num_shipment sum: {0}, b2b: {1}, b2c: {2}".format(b2b_shipment+b2c_shipment,b2b_shipment,b2c_shipment))
print ("num_carrier sum: {0}, b2b: {1}, b2c: {2}".format(b2b_carrier+b2c_carrier,b2b_carrier,b2c_carrier))
print ("num_veh sum: {0}, b2b: {1}, b2c: {2}".format(b2b_veh+b2c_veh,b2b_veh,b2c_veh))
# %%
import glob
import matplotlib.pyplot as plt
commodity_list=[1,2,3,4,5]
df_for_qc=pd.DataFrame(commodity_list, columns =["comodity"])
df_for_qc["num_shipment_v1"]=0
df_for_qc["num_shipment_v2"]=0
df_for_qc["avg_load_v1"]=0
df_for_qc["avg_load_v2"]=0
df_for_qc["min_load_v1"]=0
df_for_qc["min_load_v2"]=0
df_for_qc["max_load_v1"]=0
df_for_qc["max_load_v2"]=0
df_for_qc["sum_load_v1"]=0
df_for_qc["sum_load_v2"]=0

fdir_in_out="/Users/kjeong/NREL/1_Work/1_2_SMART_2_0/Model_development/FRISM_input_output_SF"
fdir=fdir_in_out+'/Sim_inputs/Synth_firm_results/'
B2BF=pd.DataFrame()
for com in commodity_list:
    sub_fdir="sctg%s_truck/" %com
    for filename in glob.glob(fdir+sub_fdir+'*.csv'):
        temp= pd.read_csv(filename, header=0, sep=',')
        temp=temp.astype({'BuyerID': 'int64',
        "BuyerZone":"int64",
        "BuyerNAICS":"string",
        "SellerID":"int64",
        "SellerZone":"int64",
        "SellerNAICS":"string",
        "TruckLoad": "float64",
        "SCTG_Group": "int64",
        "shipment_id":"int64",
        "orig_FAFID":"int64",
        "dest_FAFID":"int64",
        "mode_choice":"string",
        "probability":"float64",
        "Distance":"float64",
        "Travel_time":"float64" 
        })
        B2BF=pd.concat([B2BF,temp],ignore_index=True)
    plt.figure(figsize = (8,6))
    plt.hist(B2BF["TruckLoad"], color ="blue", density=True, bins=50, alpha = 0.3, label="v2_commodity_{}".format(com))
    plt.savefig('/Users/kjeong/NREL/1_Work/1_2_SMART_2_0/Model_development/FRISM_input_output_SF/Validation/v2_commodity_{}.png'.format(com))    
    df_for_qc.loc[com-1,"num_shipment_v2"]=B2BF.shape[0]
    df_for_qc.loc[com-1,"avg_load_v2"]=B2BF.TruckLoad.mean()
    df_for_qc.loc[com-1,"min_load_v2"]=B2BF.TruckLoad.min()
    df_for_qc.loc[com-1,"max_load_v2"]=B2BF.TruckLoad.max()
    df_for_qc.loc[com-1,"sum_load_v2"]=B2BF.TruckLoad.sum()

fdir_in_out="/Users/kjeong/NREL/1_Work/1_2_SMART_2_0/Model_development/FRISM_input_output_SF"
fdir=fdir_in_out+'/Sim_inputs/Synth_firm_results_Archived/Archived_Sep_2022/'
B2BF=pd.DataFrame()
for com in commodity_list:
    sub_fdir="sctg%s_truck/" %com
    for filename in glob.glob(fdir+sub_fdir+'*.csv'):
        temp= pd.read_csv(filename, header=0, sep=',')
        temp=temp.astype({'BuyerID': 'int64',
        "BuyerZone":"int64",
        "BuyerNAICS":"string",
        "SellerID":"int64",
        "SellerZone":"int64",
        "SellerNAICS":"string",
        "TruckLoad": "float64",
        "SCTG_Group": "int64",
        "shipment_id":"int64",
        "orig_FAFID":"int64",
        "dest_FAFID":"int64",
        "mode_choice":"string",
        "probability":"float64",
        "Distance":"float64",
        "Travel_time":"float64" 
        })
        B2BF=pd.concat([B2BF,temp],ignore_index=True)
    plt.figure(figsize = (8,6))
    plt.hist(B2BF["TruckLoad"], color ="blue", density=True, bins=50, alpha = 0.3, label="v1_commodity_{}".format(com))
    plt.savefig('/Users/kjeong/NREL/1_Work/1_2_SMART_2_0/Model_development/FRISM_input_output_SF/Validation/v1_commodity_{}.png'.format(com))          
    df_for_qc.loc[com-1,"num_shipment_v1"]=B2BF.shape[0]
    df_for_qc.loc[com-1,"avg_load_v1"]=B2BF.TruckLoad.mean()
    df_for_qc.loc[com-1,"min_load_v1"]=B2BF.TruckLoad.min()
    df_for_qc.loc[com-1,"max_load_v1"]=B2BF.TruckLoad.max()
    df_for_qc.loc[com-1,"sum_load_v1"]=B2BF.TruckLoad.sum()
df_for_qc.to_csv("/Users/kjeong/NREL/1_Work/1_2_SMART_2_0/Model_development/FRISM_input_output_SF/Validation/Synth_firm_input_QC_0929.csv")        
# %%
