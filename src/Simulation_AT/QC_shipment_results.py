
# %%
from re import A
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
# %%
# AT check 

f_dir="../../../Results_veh_tech_v1/"
#f_dir="/Users/kjeong/NREL/1_Work/1_2_SMART_2_0/Model_development/FRISM_input_output_AT/Sim_outputs/"


year_list=[2030,2040,2050]
s_list=["low", "central", "high"]
county_list=[453, 491, 209, 55, 21, 53]
stype_list=["B2B","B2C"]
df_ship=pd.DataFrame(county_list, columns =["county"])
df_tour=pd.DataFrame(county_list, columns =["county"])

dic_veh={'md': "Class 4-6 Vocational",
'hdt':"Class 7&8 Tractor",
'hdv':"Class 7&8 Vocational"
}
dic_fuel={"Diesel": "Diesel", "Battery Electric": "Electricity", "H2 Fuel Cell": "Hydrogen" , "PHEV": "Diesel"}
input_veh_list= ['Diesel Class 4-6 Vocational','Electric Class 4-6 Vocational',
                    'Diesel Class 7&8 Tractor','Electric Class 7&8 Tractor',
                    'Diesel Class 7&8 Vocational','Electric Class 7&8 Vocational',
                    'EV_powertrain (if any)' ]
output_veh_list=["md_D","md_E", "hdt_D", "hdt_E", "hdv_D", "hdv_E"]
y_s_list=[]
for y in year_list:
    for s in s_list:
        y_s_list.append(str(y)+s)
df_veh_agg=pd.DataFrame(y_s_list, columns =["scenario"])
df_veh_disagg=pd.DataFrame(y_s_list, columns =["scenario"])        
veh_disagg_list=[]

for veh_class in output_veh_list:
    for veh_fuel in dic_fuel.keys():
        df_veh_disagg[veh_class+"_"+veh_fuel]=0
        veh_disagg_list.append(veh_class+"_"+veh_fuel)

for veh_class in output_veh_list:
    df_veh_agg[veh_class]=0


for t in  stype_list:
    for y in year_list:
        for s in s_list:
            df_ship[t+str(y)+s]=0
            df_tour[t+str(y)+s]=0

for t in  stype_list:
    for y in year_list:
        for s in s_list:
            for c in county_list:
                try: 
                    i= df_ship.index[df_ship["county"]==c].values[0]
                    if t == "B2C":
                        ship=  pd.read_csv(f_dir+"Shipment2Fleet/{0}/{1}_payload_county{2}_shipall_s{3}_y{4}.csv". format(y,t,c,s,y))
                    else:
                        ship=  pd.read_csv(f_dir+"Shipment2Fleet/{0}/{1}_payload_county{2}_shipall_A_s{3}_y{4}.csv". format(y,t,c,s,y))

                    tour=  pd.read_csv(f_dir+"Tour_plan/{0}/{1}_county{2}_freight_tours_s{3}_y{4}.csv".format(y,t,c,s,y))
                    df_ship[t+str(y)+s].iloc[i]=ship.shape[0]
                    df_tour[t+str(y)+s].iloc[i]=tour.shape[0]
                except:
                    print ("No data for type: {0}; County: {1}; Scenario: {2}; Year: {3}".format(t,c,s,y))

for y in year_list:
    for s in s_list:
        i= df_veh_disagg.index[df_veh_disagg["scenario"]==str(y)+s].values[0]
        for c in county_list:
            for t in  stype_list:
                tour=  pd.read_csv(f_dir+"Tour_plan/{0}/{1}_county{2}_carrier_s{3}_y{4}.csv".format(y,t,c,s,y))
                for veh in veh_disagg_list:
                    try:
                        df_veh_disagg[veh].iloc[i] += len(tour[tour["vehicleTypeId"]==veh])
                    except:
                        pass    

                for veh_class in output_veh_list:
                    try:
                        df_veh_agg[veh_class].iloc[i] += len(tour[tour["vehicleTypeId"].str.contains(veh_class)])  
                    except:
                        pass

df_ship.loc['Total']= df_ship.sum(numeric_only=True, axis=0)
df_tour.loc['Total']= df_tour.sum(numeric_only=True, axis=0)

df_ship.to_csv(f_dir+"ship_summary.csv")
df_tour.to_csv(f_dir+"tour_summary.csv")
df_veh_disagg.to_csv(f_dir+"veh_type_disagg.csv")
df_veh_agg.to_csv(f_dir+"veh_type_agg.csv")

for t in  stype_list:
    for y in year_list:
        for s in s_list:
            for c in county_list:
                try:
                    tour=  pd.read_csv(f_dir+"Tour_plan/{0}/{1}_county{2}_freight_tours_s{3}_y{4}.csv".format(y,t,c,s,y))
                except:
                    print ("No data for type: {0}; County: {1}; Scenario: {2}; Year: {3}".format(t,c,s,y))                    
# %%
import shutil
import os

file_list=["carrier", "freight_tours", "payload"]

for y in year_list:
    for s in s_list:
        if not os.path.exists(f_dir+"Tour_plan/"+"{0}_{1}/".format(str(y),s)):
            os.makedirs(f_dir+"Tour_plan/"+"{0}_{1}/".format(str(y),s))
        origin=f_dir+"Shipment2Fleet/"+"{0}/vehicle_types_s{1}_y{0}.csv".format(y,s)
        target=f_dir+"Tour_plan/"+"{0}_{1}/vehicle_types_s{1}_y{0}.csv".format(y,s)    
        shutil.copy(origin, target)    
        for t in  stype_list:
            for c in county_list:
                for f in file_list:    
                    origin=f_dir+"Tour_plan/"+"{0}/{1}_county{2}_{3}_s{4}_y{5}.csv".format(y,t,c,f,s,y)
                    target=f_dir+"Tour_plan/"+"{0}_{4}/{1}_county{2}_{3}_s{4}_y{5}.csv".format(y,t,c,f,s,y)    
                    shutil.copy(origin, target)
 


# %%
# %% ####################################################
# AT check 

f_dir="../../../Results_veh_tech_v1/"
#f_dir="/Users/kjeong/NREL/1_Work/1_2_SMART_2_0/Model_development/FRISM_input_output_AT/Sim_outputs/"


year_list=[2050]
s_list=["HOP_highp2", "HOP_highp4", "HOP_highp6","HOP_highp8","HOP_highp10",
"Ref_highp2", "Ref_highp4", "Ref_highp6","Ref_highp8","Ref_highp10"]
county_list=[453, 491, 209, 55, 21, 53]
stype_list=["B2B","B2C"]
df_ship=pd.DataFrame(county_list, columns =["county"])
df_tour=pd.DataFrame(county_list, columns =["county"])

dic_veh={'md': "Class 4-6 Vocational",
'hdt':"Class 7&8 Tractor",
'hdv':"Class 7&8 Vocational"
}
dic_fuel={"Diesel": "Diesel", "Battery Electric": "Electricity", "H2 Fuel Cell": "Hydrogen" , "PHEV": "Diesel"}
input_veh_list= ['Diesel Class 4-6 Vocational','Electric Class 4-6 Vocational',
                    'Diesel Class 7&8 Tractor','Electric Class 7&8 Tractor',
                    'Diesel Class 7&8 Vocational','Electric Class 7&8 Vocational',
                    'EV_powertrain (if any)' ]
output_veh_list=["md_D","md_E", "hdt_D", "hdt_E", "hdv_D", "hdv_E"]
y_s_list=[]
for y in year_list:
    for s in s_list:
        y_s_list.append(str(y)+s)
df_veh_agg=pd.DataFrame(y_s_list, columns =["scenario"])
df_veh_disagg=pd.DataFrame(y_s_list, columns =["scenario"])        
veh_disagg_list=[]

for veh_class in output_veh_list:
    for veh_fuel in dic_fuel.keys():
        df_veh_disagg[veh_class+"_"+veh_fuel]=0
        veh_disagg_list.append(veh_class+"_"+veh_fuel)

for veh_class in output_veh_list:
    df_veh_agg[veh_class]=0


for t in  stype_list:
    for y in year_list:
        for s in s_list:
            df_ship[t+str(y)+s]=0
            df_tour[t+str(y)+s]=0

for t in  stype_list:
    for y in year_list:
        for s in s_list:
            for c in county_list:
                try: 
                    i= df_ship.index[df_ship["county"]==c].values[0]
                    if t == "B2C":
                        ship=  pd.read_csv(f_dir+"Shipment2Fleet/{0}/{1}_payload_county{2}_shipall_s{3}_y{4}.csv". format(y,t,c,s,y))
                    else:
                        ship=  pd.read_csv(f_dir+"Shipment2Fleet/{0}/{1}_payload_county{2}_shipall_A_s{3}_y{4}.csv". format(y,t,c,s,y))

                    tour=  pd.read_csv(f_dir+"Tour_plan/{0}/{1}_county{2}_freight_tours_s{3}_y{4}.csv".format(y,t,c,s,y))
                    df_ship[t+str(y)+s].iloc[i]=ship.shape[0]
                    df_tour[t+str(y)+s].iloc[i]=tour.shape[0]
                except:
                    print ("No data for type: {0}; County: {1}; Scenario: {2}; Year: {3}".format(t,c,s,y))

for y in year_list:
    for s in s_list:
        i= df_veh_disagg.index[df_veh_disagg["scenario"]==str(y)+s].values[0]
        for c in county_list:
            for t in  stype_list:
                tour=  pd.read_csv(f_dir+"Tour_plan/{0}/{1}_county{2}_carrier_s{3}_y{4}.csv".format(y,t,c,s,y))
                for veh in veh_disagg_list:
                    try:
                        df_veh_disagg[veh].iloc[i] += len(tour[tour["vehicleTypeId"]==veh])
                    except:
                        pass    

                for veh_class in output_veh_list:
                    try:
                        df_veh_agg[veh_class].iloc[i] += len(tour[tour["vehicleTypeId"].str.contains(veh_class)])  
                    except:
                        pass

df_ship.loc['Total']= df_ship.sum(numeric_only=True, axis=0)
df_tour.loc['Total']= df_tour.sum(numeric_only=True, axis=0)

df_ship.to_csv(f_dir+"ship_summary.csv")
df_tour.to_csv(f_dir+"tour_summary.csv")
df_veh_disagg.to_csv(f_dir+"veh_type_disagg.csv")
df_veh_agg.to_csv(f_dir+"veh_type_agg.csv")

for t in  stype_list:
    for y in year_list:
        for s in s_list:
            for c in county_list:
                try:
                    tour=  pd.read_csv(f_dir+"Tour_plan/{0}/{1}_county{2}_freight_tours_s{3}_y{4}.csv".format(y,t,c,s,y))
                except:
                    print ("No data for type: {0}; County: {1}; Scenario: {2}; Year: {3}".format(t,c,s,y))