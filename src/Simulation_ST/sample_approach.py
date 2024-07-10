# %%
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

'''
# how to create multiple files for parrerall run
1. Location based cluster
2. After running all area with shipment 2 fleet, and then create files based on carrier ID? 

'''

 
'''
# sample B2B shipment
Annual flow - shipment size -> select days using 265
1. select daily flow and then x % sample vs select annual flow and then x sample, apply selection
2. Consideration
 * commodity type
 * payload weight
 * Origin
 * Destination
 * OD pair? 
3. Select shippers or reciver sample 
4.  

'''
'''
# How to reduce the capacity of carrier file
1. Sample of carrier vs reduced number of vehicle... 
2. consideration
* bigger fleet -> reduced number of vehicle 
* locations
* 

'''
# %%
def random_points_in_polygon(polygon):
    temp = polygon.bounds
    finished= False
    while not finished:
        point = Point(random.uniform(temp.minx.values[0], temp.maxx.values[0]), random.uniform(temp.miny.values[0], temp.maxy.values[0]))
        finished = polygon.contains(point).values[0]
    return [point.x, point.y]


fdir_in_out="../../../FRISM_input_output_SF"
fdir_geo= fdir_in_out+'/Sim_inputs/Geo_data/'
CBG_file='SFBay_freight.geojson'
CBGzone_df = gpd.read_file(fdir_geo+CBG_file) # file include, GEOID(12digit), MESOZONE, area
#CBGzone_df=CBGzone_df[['GEOID','CBPZONE','MESOZONE','area']]
CBGzone_df= CBGzone_df.to_crs({'proj': 'cea'})
CBGzone_df["area"]=CBGzone_df['geometry'].area/(10**6)
CBGzone_df["GEOID"]=CBGzone_df["GEOID"].astype(str)
## Add county id from GEOID
CBGzone_df["County"]=CBGzone_df["GEOID"].apply(lambda x: x[2:5] if len(x)>=12 else 0)
CBGzone_df["County"]=CBGzone_df["County"].astype(str).astype(int)
CBGzone_df["GEOID"]=CBGzone_df["GEOID"].astype(str).astype(int)
CBGzone_df= CBGzone_df.to_crs('EPSG:4269')
county_list=[1, 13, 41, 55, 75, 81, 85, 95, 97]


ex_zone=CBGzone_df[~CBGzone_df["County"].isin(county_list)][['MESOZONE','geometry']].reset_index(drop=True)
ex_zone["BoundaryZONE"]=0
in_zones= CBGzone_df[CBGzone_df["County"].isin(county_list)].reset_index(drop=True)
for index, row in ex_zone.iterrows():
    D = 999999
    Id = None 
    p = row['geometry'].centroid
    for i,z in enumerate(in_zones['geometry']):
        distance = p.distance(z)
        ID = in_zones.iloc[i]['MESOZONE']
        if distance <= D:
            D = distance
            Id = ID
    ex_zone.at[index, "BoundaryZONE"] =Id
#ex_zone= pd.read_csv(fdir_geo+"External_Zones_Mapping.csv")
#ex_zone=ex_zone[~ex_zone['BoundaryZONE'].isin(list_error_zone)]
temp_ex_zone=ex_zone.drop_duplicates(subset=['BoundaryZONE'])
temp_ex_zone=temp_ex_zone.reset_index()
temp_ex_zone['x']=0
temp_ex_zone['y']=0
with alive_bar(temp_ex_zone.shape[0], force_tty=True) as bar:
    for i in range(0,temp_ex_zone.shape[0]):
        [x,y]=random_points_in_polygon(CBGzone_df.geometry[CBGzone_df.MESOZONE==temp_ex_zone.loc[i,"BoundaryZONE"]])
        temp_ex_zone.loc[i,'x']=x
        temp_ex_zone.loc[i,'y']=y
        bar()  
ex_zone=ex_zone.merge(temp_ex_zone[["BoundaryZONE", "x", "y"]], on="BoundaryZONE", how='left')
ex_zone=ex_zone.drop('geometry', axis=1)
#ex_zone.to_csv(ex_zone_file_xy, index = False, header=True)





# %%
filename= "../../../FRISM_input_output_SF/Sim_inputs/Synth_firm_results/2018_Base/private_truck_shipment_sctg1.csv"
filename= "../../../FRISM_input_output_SF/Sim_inputs/Synth_firm_pop/2018_Base/synthetic_carriers.csv"


truckings= pd.read_csv(filename, header=0, sep=',')
truckings["BusID"] = temp.apply(lambda x: str(x["BusID"]) + "_" + str(x["fleet_id"]), axis=1)
truckings = truckings.merge(CBGzone_df[['MESOZONE','County']], on='MESOZONE', how='left')  
truckings["BusID"]=truckings["BusID"].apply(lambda x: str(x))
county_list=[1, 13, 41, 55, 75, 81, 85, 95, 97]
temp =truckings[truckings['County'].isin(county_list)].reset_index(drop=True)
truckings_out =truckings[~truckings['County'].isin(county_list)].reset_index(drop=True)

# %%
sample_ratio=10
bin_size=10

def sampling_carrier(temp, sample_ratio, bin_size):
    temp_1=temp
    total_size=temp_1.shape[0]
    if (total_size*sample_ratio)/(100) < bin_size:
        bin_size = int((total_size*sample_ratio)/(100))
    try:    
        temp_1["binned_volume"] =pd.qcut(temp_1['n_trucks'], q=bin_size, labels=False)
    except:
        temp_1["binned_volume"]=temp_1['n_trucks'].apply(lambda x:lable_creater(x))
    list_bin_labels = temp_1["binned_volume"].unique().tolist()
    list_shipper_sample=[]
    for bin_id in list_bin_labels:
        temp_2=temp_1[(temp_1['binned_volume']==bin_id)]
        list_shipper = temp_2['BusID'].unique().tolist()
        if (len(list_shipper)*sample_ratio/100 >0) & (len(list_shipper)*sample_ratio/100 <0.5):
            list_shipper= random.sample(list_shipper, int(len(list_shipper)*sample_ratio/100+0.5))
            list_shipper_sample=list_shipper_sample+list_shipper
        elif (len(list_shipper)*sample_ratio/100 >=0.5):     
            list_shipper= random.sample(list_shipper, int(len(list_shipper)*sample_ratio/100+0.5))
            list_shipper_sample=list_shipper_sample+list_shipper             
    df_sample=temp[temp["BusID"].isin(list_shipper_sample)].reset_index(drop=True)

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
        
test= temp.groupby(['n_trucks'])['n_trucks'].count()



def sampling_shipper(temp, sample_ratio, bin_size):
    temp_1 = temp.groupby(['SellerID'])['SellerID'].count().reset_index(name='num_shipment')
    total_size=temp_1.shape[0]
    if (total_size*sample_ratio)/(100) < bin_size:
        bin_size = int((total_size*sample_ratio)/(100))
    temp_1["binned_volume"] =pd.qcut(temp_1['num_shipment'], q=bin_size, labels=False)
    list_bin_labels = temp_1["binned_volume"].unique().tolist()
    list_shipper_sample=[]
    for bin_id in list_bin_labels:
        temp_2=temp_1[(temp_1['binned_volume']==bin_id)]
        list_shipper = temp_2['SellerID'].unique().tolist()
        list_shipper= random.sample(list_shipper, int(len(list_shipper)*sample_ratio/100+0.5))
        list_shipper_sample=list_shipper_sample+list_shipper 
    df_sample=temp[temp['SellerID'].isin(list_shipper_sample)]

    return df_sample
# %%
# %%
def b2b_d_select_with_ship_size(TruckLoad,w_th, b2b_day_factor):
    if TruckLoad <= w_th*1:
         if random.uniform(0,1) <=1/(b2b_day_factor*52):
            return 1
         else: return 0   
    else:
         if random.uniform(0,1) <=1/(b2b_day_factor*52):
            return 1
         else: return 0 
# %%
def b2b_d_shipment_by_commodity(fdir, weight_theshold, CBGzone_df,sel_county,ship_direction, county_wo_sel, b2b_day_factor,year, scenario):
  
    B2BF=pd.DataFrame()
    sub_fdir="{}_{}/".format(year,scenario)
    for filename in glob.glob(fdir+sub_fdir+'*.csv'):
        #print (filename)
        filename= "../../../FRISM_input_output_SF/Sim_inputs/Synth_firm_results/2018_Base/private_truck_shipment_sctg1.csv" ### Need to delete 
        temp= pd.read_csv(filename, header=0, sep=',')
        if temp.shape[0] >0:
            temp["SellerID"]=temp["SellerID"].astype("int") 
            if "fleet_id" in temp.columns:
                temp["fleet_id"]=temp["fleet_id"].astype("int") 
                temp["SellerID"] = temp.apply(lambda x: str(x["SellerID"]) + "_" + str(x["fleet_id"]), axis=1)
                temp = temp.drop("fleet_id", axis=1)
            else:
                temp["SellerID"] = temp.apply(lambda x: str(x["SellerID"]) + "_1", axis=1)
            temp["BuyerID"] = temp.apply(lambda x: str(x["BuyerID"]) + "_1", axis=1)        
            temp=temp.astype({'BuyerID': 'string',
            "BuyerZone":"int64",
            "BuyerNAICS":"string",
            "SellerID":"string",
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
            # Add SellerCounty and BuyerCounty for filering 
            temp = temp.merge(CBGzone_df[['MESOZONE','County']], left_on="SellerZone", right_on='MESOZONE', how='left')
            temp=temp.rename({'County':'SellerCounty'}, axis=1)
            temp = temp.merge(CBGzone_df[['MESOZONE','County']], left_on="BuyerZone", right_on='MESOZONE', how='left')
            temp=temp.rename({'County':'BuyerCounty'}, axis=1)
            if sel_county != 9999:
                if ship_direction == "out":
                    temp= temp[temp['SellerCounty']==sel_county].reset_index(drop=True)
                elif ship_direction == "in":
                    temp= temp[(temp['BuyerCounty']==sel_county) & (temp['SellerCounty']!=sel_county)].reset_index(drop=True)
                elif ship_direction == "all":
                    temp= temp[(temp['BuyerCounty']==sel_county) | (temp['SellerCounty']==sel_county)].reset_index(drop=True)
                    temp= temp[~temp['SellerCounty'].isin(county_wo_sel)].reset_index(drop=True)
            temp['TruckLoad']=temp['TruckLoad']*2000
            temp["D_truckload"]=0
            temp["D_selection"]=0
            temp["D_truckload"]=temp['TruckLoad']
            #temp["D_truckload"]=temp['TruckLoad'].apply(lambda x: b2b_d_truckload(x, weight_theshold))
            temp["D_selection"]=temp['TruckLoad'].apply(lambda x: b2b_d_select_with_ship_size(x, weight_theshold, b2b_day_factor))
            #temp["D_selection"]=temp['TruckLoad'].apply(lambda x: b2b_d_select(x, weight_theshold))
            temp=temp.query('D_selection ==1')
            B2BF=pd.concat([B2BF,temp],ignore_index=True)
    #B2BF.to_csv(fdir+'Daily_sctg%s_OD_%s_%s.csv' % (commoidty, sel_county,ship_direction), index = False, header=True)
    return B2BF