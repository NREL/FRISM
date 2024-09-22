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
def int_d_select_with_ship_size(TruckLoad, Shipment, w_th, b2b_day_factor):
    n_shipment_sel=0
    for i in range(0,int(Shipment)):
        if TruckLoad <= w_th*1:
                if random.uniform(0,1) <=(b2b_day_factor/52.15):
                    n_shipment_sel= n_shipment_sel+1
                else: n_shipment_sel= n_shipment_sel+0  
        else:
                if random.uniform(0,1) <=(b2b_day_factor/52.15):
                    n_shipment_sel= n_shipment_sel+1
                else: n_shipment_sel= n_shipment_sel+0
    if n_shipment_sel >0:
         sel_index=1
    else: sel_index=0

    return [sel_index, n_shipment_sel]                    

def sampling_int_ship(temp, sample_ratio, bin_size):
    # temp_1 = temp.groupby(['SellerID'])['SellerID'].count().reset_index(name='num_shipment')
    total_size=temp.shape[0]
    if (total_size*sample_ratio)/(100) < bin_size:
        bin_size = int((total_size*sample_ratio)/(100))
    try:    
        temp["binned_volume"] =pd.qcut(temp['num_shipment'], q=bin_size, labels=False)
    except:
        temp["binned_volume"]=temp['num_shipment'].apply(lambda x:lable_creater(x))

    list_bin_labels = temp["binned_volume"].unique().tolist()
    list_shipper_sample=[]
    for bin_id in list_bin_labels:
        temp_2=temp[(temp['binned_volume']==bin_id)]
        list_shipper = temp_2['bundle_id'].unique().tolist()
        if (len(list_shipper)*sample_ratio/100 >0) & (len(list_shipper)*sample_ratio/100 <0.5):
            list_shipper= random.sample(list_shipper, int(len(list_shipper)*sample_ratio/100+0.5))
            list_shipper_sample=list_shipper_sample+list_shipper
        elif (len(list_shipper)*sample_ratio/100 >=0.5):     
            list_shipper= random.sample(list_shipper, int(len(list_shipper)*sample_ratio/100+0.5))
            list_shipper_sample=list_shipper_sample+list_shipper  
    df_sample=temp[temp['bundle_id'].isin(list_shipper_sample)].reset_index(drop=True)

    return df_sample
def lable_creater(value):
    if value <=1:
        return 0
    elif value>1 and value<4:
        return 1
    elif value >=4 and value <8:
        return 2
    elif value >=8 and value <16:
        return 3    
    elif value >=16 and value <64:
        return 4 
    elif value >=64 and value <128:
        return 5
    elif value >=128 and value <256:
        return 6
    elif value >=256:
        return 7 


# %%
fdir_geo = "../../../FRISM_input_output_SF/Sim_inputs/Geo_data/"
CBG_file = 'SFBay_freight.geojson'
state_id="06"
CBGzone_df = gpd.read_file(fdir_geo+CBG_file) # file include, GEOID(12digit), MESOZONE, area
CBGzone_df= CBGzone_df.to_crs({'proj': 'cea'})
CBGzone_df["GEOID"]=CBGzone_df["GEOID"].astype(str)
## Add county id from GEOID
CBGzone_df["County"]=CBGzone_df["GEOID"].apply(lambda x: x[2:5] if (len(x)>=12 and x[0:2]==str(state_id))  else 0)
CBGzone_df["County"]=CBGzone_df["County"].astype(str).astype(int)
CBGzone_df["GEOID"]=CBGzone_df["GEOID"].astype(str).astype(int)
CBGzone_df=CBGzone_df[CBGzone_df["County"]!=0]
CBGzone_df= CBGzone_df.to_crs('EPSG:4269')
#%%
filename = "/Users/kjeong/KJ_NREL_Work/1_Work/1_2_SMART_2_0/Model_development/FRISM_input_output_SF/New_base_input/import_OD_with_buyer.csv"
temp= pd.read_csv(filename, header=0, sep=',')
B2BF=pd.DataFrame()
# %%
temp["BuyerID"]=temp["BuyerID"].astype("int")
temp["BuyerID"]=temp["BuyerID"].apply(lambda x: str(x)+ "_1")
temp["BuyerID"]=temp["BuyerID"].astype("str")
temp=temp.rename({'PORTID':'SellerID'}, axis=1)
temp=temp.rename({'PORTZONE':'SellerZone'}, axis=1)
   # Add SellerCounty and BuyerCounty for filering 
temp = temp.merge(CBGzone_df[['MESOZONE','County']], left_on="SellerZone", right_on='MESOZONE', how='left')
temp=temp.rename({'County':'SellerCounty'}, axis=1)
temp = temp.merge(CBGzone_df[['MESOZONE','County']], left_on="BuyerZone", right_on='MESOZONE', how='left')
temp=temp.rename({'County':'BuyerCounty'}, axis=1)

temp['TruckLoad']=temp['TruckLoad']*2000
temp["D_truckload"]=0
temp["D_selection"]=0
temp["num_shipment"]=0
temp["D_truckload"]=temp['TruckLoad']
temp[["D_selection","num_shipment"]]=temp.apply(lambda x: int_d_select_with_ship_size(x["TruckLoad"],x["shipments"],weight_theshold, b2b_day_factor),axis=1).to_list()

temp=temp.query('D_selection ==1')
if sample_ratio <100: 
    temp_import=sampling_int_ship(temp, sample_ratio, bin_size) 

temp_int = pd.DataFrame(columns =['BuyerID',
            "BuyerZone",
            "BuyerNAICS",
            "SellerID",
            "SellerZone",
            "SellerNAICS",
            "TruckLoad",
            "SCTG_Group",
            "shipment_id",
            "orig_FAFID",
            "dest_FAFID",
            "mode_choice",
            "probability",
            "Distance",
            "Travel_time",
            "D_truckload",
            "D_selection",
            "ship_category"])

#dtype=['string',"int64","string","string","int64","string","float64","int64","int64","int64","int64","string","float64","float64","float64","float64","int64"]

temp_import=temp_import.reset_index(drop=True)
for i in range(0,temp_import.shape[0]):
    temp_line=pd.DataFrame(data= {'BuyerID': [temp_import.loc[i,"BuyerID"]] ,
            "BuyerZone": [temp_import.loc[i,"BuyerZone"]],
            "BuyerNAICS":[temp_import.loc[i,"BuyerNAICS"]],
            "SellerID":[temp_import.loc[i,"SellerID"]],
            "SellerZone":[temp_import.loc[i,"SellerZone"]],
            "SellerNAICS":["NA"],
            "TruckLoad":[temp_import.loc[i,"TruckLoad"]],
            "SCTG_Group":[temp_import.loc[i,"SCTG_Group"]],
            "shipment_id":[temp_import.loc[i,"bundle_id"]],
            "orig_FAFID":[temp_import.loc[i,"FAF"]],
            "dest_FAFID":[temp_import.loc[i,"dms_dest"]],
            "mode_choice":[temp_import.loc[i,"mode_choice"]],
            "probability":[1],
            "Distance":[temp_import.loc[i,"Distance"]],
            "Travel_time":[0],
            "D_truckload":[temp_import.loc[i,"D_truckload"]],
            "D_selection":[temp_import.loc[i,"D_truckload"]],
            "ship_category": ["import"]})
    num_shipment= temp_import.loc[i,"num_shipment"]
    temp_line =pd.concat([temp_line]*num_shipment, ignore_index=True)
    B2BF=pd.concat([B2BF,temp_line],ignore_index=True)



weight_theshold= 10
b2b_day_factor=0.15
sample_ratio=10
bin_size = 10
# %%
temp["SellerID"]=temp["SellerID"].apply(lambda x: int(x))
temp["SellerID"]=temp["SellerID"].astype("str")
temp=temp.rename({'PORTID':'BuyerID'}, axis=1)
temp=temp.rename({'PORTZONE':'BuyerZone'}, axis=1)
   # Add SellerCounty and BuyerCounty for filering 
temp = temp.merge(CBGzone_df[['MESOZONE','County']], left_on="SellerZone", right_on='MESOZONE', how='left')
temp=temp.rename({'County':'SellerCounty'}, axis=1)
temp = temp.merge(CBGzone_df[['MESOZONE','County']], left_on="BuyerZone", right_on='MESOZONE', how='left')
temp=temp.rename({'County':'BuyerCounty'}, axis=1)

temp['TruckLoad']=temp['TruckLoad']*2000
temp["D_truckload"]=0
temp["D_selection"]=0
temp["num_shipment"]=0
temp["D_truckload"]=temp['TruckLoad']
temp[["D_selection","num_shipment"]]=temp.apply(lambda x: int_d_select_with_ship_size(x["TruckLoad"],x["shipments"],weight_theshold, b2b_day_factor),axis=1).to_list()

temp=temp.query('D_selection ==1')
if sample_ratio <100: 
    temp_import=sampling_int_ship(temp, sample_ratio, bin_size) 
B2BF=pd.DataFrame()
temp_int = pd.DataFrame(columns =['BuyerID',
            "BuyerZone",
            "BuyerNAICS",
            "SellerID",
            "SellerZone",
            "SellerNAICS",
            "TruckLoad",
            "SCTG_Group",
            "shipment_id",
            "orig_FAFID",
            "dest_FAFID",
            "mode_choice",
            "probability",
            "Distance",
            "Travel_time",
            "D_truckload",
            "D_selection",
            "ship_category"])

#dtype=['string',"int64","string","string","int64","string","float64","int64","int64","int64","int64","string","float64","float64","float64","float64","int64"]

temp_import=temp_import.reset_index(drop=True)
for i in range(0,temp_import.shape[0]):
    temp_line=pd.DataFrame(data= {'BuyerID': [temp_import.loc[i,"BuyerID"]] ,
            "BuyerZone": [temp_import.loc[i,"BuyerZone"]],
            "BuyerNAICS":[temp_import.loc[i,"BuyerNAICS"]],
            "SellerID":[temp_import.loc[i,"SellerID"]],
            "SellerZone":[temp_import.loc[i,"SellerZone"]],
            "SellerNAICS":["NA"],
            "TruckLoad":[temp_import.loc[i,"TruckLoad"]],
            "SCTG_Group":[temp_import.loc[i,"SCTG_Group"]],
            "shipment_id":[temp_import.loc[i,"bundle_id"]],
            "orig_FAFID":[temp_import.loc[i,"FAF"]],
            "dest_FAFID":[temp_import.loc[i,"dms_dest"]],
            "mode_choice":[temp_import.loc[i,"mode_choice"]],
            "probability":[1],
            "Distance":[temp_import.loc[i,"Distance"]],
            "Travel_time":[0],
            "D_truckload":[temp_import.loc[i,"D_truckload"]],
            "D_selection":[temp_import.loc[i,"D_truckload"]],
            "ship_category": ["export"]})
    num_shipment= temp_import.loc[i,"num_shipment"]
    temp_line =pd.concat([temp_line]*num_shipment, ignore_index=True)
    B2BF=pd.concat([B2BF,temp_line],ignore_index=True)


# %%
filename = "/Users/kjeong/KJ_NREL_Work/1_Work/1_2_SMART_2_0/Model_development/FRISM_input_output_SF/New_base_input/synthetic_firms_with_fleet_mc_adjusted.csv"
temp= pd.read_csv(filename, header=0, sep=',')
# %%
temp[temp["BusID"]==8392394] 
# %%
filename = "/Users/kjeong/KJ_NREL_Work/1_Work/1_2_SMART_2_0/Model_development/FRISM_input_output_SF/New_base_input/port_location_in_region.geojson"
temp_2=gpd.read_file(filename)
# %%

dist_file= "/Users/kjeong/KJ_NREL_Work/1_Work/1_2_SMART_2_0/Model_development/FRISM_input_output_SF/Sim_inputs/Geo_data/BayArea_od_dist.csv"
dist=pd.read_csv(dist_file)
tt_file= "/Users/kjeong/KJ_NREL_Work/1_Work/1_2_SMART_2_0/Model_development/FRISM_input_output_SF/Sim_inputs/Geo_data/tt_df_cbg_v2.csv.gz"
tt= pd.read_csv(tt_file, compression='gzip', header=0, sep=',', quotechar='"')
# %%
