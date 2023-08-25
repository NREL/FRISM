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
import geopy.distance
from statistics import mode
# %%

f_dir="../../../FRISM_input_output_AT/Sim_inputs/"
f_dir_2="../../../Results_dmd_v1/Shipment2Fleet/2040/"
f_dir_out="../../../Results_dmd_v1/Shipment2Fleet/2040_loc_v2/"
county_list=["453", "491", "209", "55", "21", "53"]
hh_participation= [20,40,60]
loc_expansion=[30,60,90]
vist_cap =15
dist_limit =6

df_elock= pd.read_csv(f_dir+"amazon locker.csv")
df_plock= pd.read_csv(f_dir+"Grocery store.csv")
df_plock["GID"]=df_plock["GID"].apply(lambda x: "G"+x)
df_plock2= pd.read_csv(f_dir+"phamacy.csv")
df_plock2["GID"]=df_plock2["GID"].apply(lambda x: "P"+x)
df_plock=pd.concat([df_plock, df_plock2], ignore_index=True).reset_index(drop=True)
# %%
def find_loc(ship_coor,df_loc, dist_limit):
    df_loc["dist"]=df_loc.apply(lambda x:geopy.distance.geodesic(ship_coor, (x["lat"],x["lng"])).miles, axis=1)
    #df_loc= df_loc.sort_values('dist',ascending=True).head(20)
    list_gid= df_loc[df_loc["dist"]<=dist_limit]["GID"].unique().tolist()
    return list_gid

def unpack_list(two_lv_list):
    new_list=[]
    for i in range(0,len(two_lv_list)):
        for j in range(0,len(two_lv_list[i])):
            new_list.append(two_lv_list[i][j])
    return new_list 


'''
df_payload["carrier_id"] code
0: no locker delivery
1: selected for participation
2: can be combined within the tour 

'''

for par_rate in hh_participation:
     loc_rate =0
     df_loc=df_elock
     df_loc["num_use"] =0 
     for county in county_list:
          df_payload= pd.read_csv(f_dir_2+"B2C_payload_county{}_shipall_sDmd_G140_y2040.csv".format(county))
          col_list= df_payload.columns
          
          df_payload['list_loc']=df_payload.apply(lambda x: find_loc((x["del_y"], x["del_x"]),df_elock, dist_limit), axis=1)
          df_payload['num_loc']=df_payload['list_loc'].apply(lambda x: len(x))
          df_payload['ship_id']=df_payload.index
          list_potential_loc= df_payload[df_payload['num_loc']>0]['ship_id'].unique().tolist()
          list_sel_loc= random.sample(list_potential_loc,int(len(list_potential_loc)*par_rate/100)) 
          df_payload['sel_payload']= df_payload['ship_id'].apply(lambda x: 1 if x in list_sel_loc else 0)

          new_payload=pd.DataFrame()
          for c_id in df_payload["carrier_id"].unique():
              temp_df= df_payload[df_payload['carrier_id'] == c_id]
              temp_df.loc[:,"sel_loc"] ="no_id"
              temp_df_reg= temp_df[temp_df['sel_payload']==0]
              temp_df_loc= temp_df[temp_df['sel_payload']==1]
              new_payload=pd.concat([new_payload, temp_df_reg], ignore_index=True).reset_index(drop=True)
              if temp_df_loc['sel_payload'].sum()>1:
                    list_loc = temp_df_loc["list_loc"].tolist()
                    list_loc= unpack_list(list_loc)
                    over_cap_loc = df_loc[df_loc["num_use"]> vist_cap]["GID"].unique().tolist()  
                    list_loc =  list(set(list_loc) - set(over_cap_loc))
              else: list_loc=[]          
              if len(list_loc) ==0:
                      new_payload=pd.concat([new_payload, temp_df_loc], ignore_index=True).reset_index(drop=True)    
              else:     
                      top_loc =mode(list_loc)
                      temp_df_loc[["sel_loc", "sel_payload"]] = temp_df_loc["list_loc"].apply(lambda x: [top_loc,2] if top_loc in x else [random.sample(x,1)[0],1]).to_list()
                      if 1 in temp_df_loc['sel_payload'].unique():     
                              temp_df_loc_g1=temp_df_loc[temp_df_loc['sel_payload']==1]
                              temp_df_loc_g1["del_stop_duration"] = np.random.randint(5,20, size=len(temp_df_loc_g1))
                              temp_df_loc_g1["del_y"] = temp_df_loc_g1["sel_loc"].apply(lambda x: df_loc[df_loc["GID"]==x]["lat"].values[0])
                              temp_df_loc_g1["del_x"] = temp_df_loc_g1["sel_loc"].apply(lambda x: df_loc[df_loc["GID"]==x]["lng"].values[0])
                              list_temp_g1= temp_df_loc_g1["sel_loc"].unique().tolist()
                              df_loc["num_use"] = df_loc.apply(lambda x: x["num_use"] +1 if x["GID"] in list_temp_g1 else x["num_use"], axis=1)
                              new_payload=pd.concat([new_payload, temp_df_loc_g1], ignore_index=True).reset_index(drop=True)
                      if 2 in temp_df_loc['sel_payload'].unique():     
                              temp_df_loc_g2=temp_df_loc[temp_df_loc['sel_payload']==2].reset_index(drop=True)
                              temp_df_loc_g2= temp_df_loc_g2.iloc[[0]]
                              temp_df_loc_g2["weight"] = temp_df_loc[temp_df_loc['sel_payload']==2]["weight"].sum()
                              temp_df_loc_g2["del_stop_duration"] = np.random.randint(10,30, size=len(temp_df_loc_g2))
                              temp_df_loc_g2["del_y"] = temp_df_loc_g2["sel_loc"].apply(lambda x: df_loc[df_loc["GID"]==x]["lat"].values[0])
                              temp_df_loc_g2["del_x"] = temp_df_loc_g2["sel_loc"].apply(lambda x: df_loc[df_loc["GID"]==x]["lng"].values[0])
                              list_temp_g2= temp_df_loc_g2["sel_loc"].unique().tolist()
                              df_loc["num_use"] = df_loc.apply(lambda x: x["num_use"] +1 if x["GID"] in list_temp_g2 else x["num_use"], axis=1)
                              new_payload=pd.concat([new_payload, temp_df_loc_g2], ignore_index=True).reset_index(drop=True)
          new_payload=new_payload[col_list]
          new_payload.to_csv(f_dir_out+"B2C_payload_county{}_shipall_sCon_p{}_e{}_y2040.csv".format(county,par_rate,loc_rate), index = False, header=True)
          with open(f_dir_out+'B2C_col_participation.txt', 'a') as f:
              print("****** sencario: participation {} and expansion {} ******".format(par_rate,loc_rate), file=f)
              print("county, {}, base size, {}, con_size, {}".format(county,df_payload.shape[0],new_payload.shape[0]), file=f)

# %%
for loc_rate in loc_expansion:
     par_rate =40
     df_loc=df_elock
     list_ex_loc= df_plock['GID'].unique().tolist()
     list_ex_loc= random.sample(list_ex_loc,int(len(list_ex_loc)*loc_rate/100)) 
     df_plock=df_plock[df_plock['GID'].isin(list_ex_loc)]   
     df_loc=pd.concat([df_elock,df_plock], ignore_index=True).reset_index(drop=True)
     df_loc["num_use"] =0 
     for county in county_list:
          df_payload= pd.read_csv(f_dir_2+"B2C_payload_county{}_shipall_sDmd_G140_y2040.csv".format(county))
          col_list= df_payload.columns
          
          df_payload['list_loc']=df_payload.apply(lambda x: find_loc((x["del_y"], x["del_x"]),df_elock, dist_limit), axis=1)
          df_payload['num_loc']=df_payload['list_loc'].apply(lambda x: len(x))
          df_payload['ship_id']=df_payload.index
          list_potential_loc= df_payload[df_payload['num_loc']>0]['ship_id'].unique().tolist()
          list_sel_loc= random.sample(list_potential_loc,int(len(list_potential_loc)*par_rate/100)) 
          df_payload['sel_payload']= df_payload['ship_id'].apply(lambda x: 1 if x in list_sel_loc else 0)

          new_payload=pd.DataFrame()
          #c_id="B2C_2867688_3"
          for c_id in df_payload["carrier_id"].unique():
              temp_df= df_payload[df_payload['carrier_id'] == c_id]
              temp_df.loc[:,"sel_loc"] ="no_id"
              temp_df_reg= temp_df[temp_df['sel_payload']==0]
              temp_df_loc= temp_df[temp_df['sel_payload']==1]
              new_payload=pd.concat([new_payload, temp_df_reg], ignore_index=True).reset_index(drop=True)
              if temp_df_loc['sel_payload'].sum()>1:
                    list_loc = temp_df_loc["list_loc"].tolist()
                    list_loc= unpack_list(list_loc)
                    over_cap_loc = df_loc[df_loc["num_use"]> vist_cap]["GID"].unique().tolist()  
                    list_loc =  list(set(list_loc) - set(over_cap_loc))
              else: list_loc=[]       
              if len(list_loc) ==0:
                      new_payload=pd.concat([new_payload, temp_df_loc], ignore_index=True).reset_index(drop=True)    
              else:     
                      top_loc =mode(list_loc)
                      temp_df_loc[["sel_loc", "sel_payload"]] = temp_df_loc["list_loc"].apply(lambda x: [top_loc,2] if top_loc in x else [random.sample(x,1)[0],1]).to_list()
                      if 1 in temp_df_loc['sel_payload'].unique():     
                              temp_df_loc_g1=temp_df_loc[temp_df_loc['sel_payload']==1]
                              temp_df_loc_g1["del_stop_duration"] = np.random.randint(5,20, size=len(temp_df_loc_g1))
                              temp_df_loc_g1["del_y"] = temp_df_loc_g1["sel_loc"].apply(lambda x: df_loc[df_loc["GID"]==x]["lat"].values[0])
                              temp_df_loc_g1["del_x"] = temp_df_loc_g1["sel_loc"].apply(lambda x: df_loc[df_loc["GID"]==x]["lng"].values[0])
                              list_temp_g1= temp_df_loc_g1["sel_loc"].unique().tolist()
                              df_loc["num_use"] = df_loc.apply(lambda x: x["num_use"] +1 if x["GID"] in list_temp_g1 else x["num_use"], axis=1)
                              new_payload=pd.concat([new_payload, temp_df_loc_g1], ignore_index=True).reset_index(drop=True)
                      if 2 in temp_df_loc['sel_payload'].unique():     
                              temp_df_loc_g2=temp_df_loc[temp_df_loc['sel_payload']==2].reset_index(drop=True)
                              temp_df_loc_g2= temp_df_loc_g2.iloc[[0]]
                              temp_df_loc_g2["weight"] = temp_df_loc[temp_df_loc['sel_payload']==2]["weight"].sum()
                              temp_df_loc_g2["del_stop_duration"] = np.random.randint(10,30, size=len(temp_df_loc_g2))
                              temp_df_loc_g2["del_y"] = temp_df_loc_g2["sel_loc"].apply(lambda x: df_loc[df_loc["GID"]==x]["lat"].values[0])
                              temp_df_loc_g2["del_x"] = temp_df_loc_g2["sel_loc"].apply(lambda x: df_loc[df_loc["GID"]==x]["lng"].values[0])
                              list_temp_g2= temp_df_loc_g2["sel_loc"].unique().tolist()
                              df_loc["num_use"] = df_loc.apply(lambda x: x["num_use"] +1 if x["GID"] in list_temp_g2 else x["num_use"], axis=1)
                              new_payload=pd.concat([new_payload, temp_df_loc_g2], ignore_index=True).reset_index(drop=True)
          new_payload=new_payload[col_list]
          new_payload.to_csv(f_dir_out+"B2C_payload_county{}_shipall_sCon_p{}_e{}_y2040.csv".format(county,par_rate,loc_rate), index = False, header=True)
          with open(f_dir_out+'B2C_con_expansion.txt', 'a') as f:
              print("****** sencario: participation {} and expansion {} ******".format(par_rate,loc_rate), file=f)
              print("county, {}, base size, {}, con_size, {}".format(county,df_payload.shape[0],new_payload.shape[0]), file=f)          

# %%

for par_rate in hh_participation:
     loc_rate =0
     df_veh= pd.read_csv(f_dir_2+"vehicle_types_sDmd_G140_y2040.csv")
     df_veh.to_csv(f_dir_out+"vehicle_types_sCon_p{}_e{}_y2040.csv".format(par_rate,loc_rate), index = False, header=True)
     for county in county_list:
          df_payload= pd.read_csv(f_dir_2+"B2C_carrier_county{}_shipall_sDmd_G140_y2040.csv".format(county))
          df_payload.to_csv(f_dir_out+"B2C_carrier_county{}_shipall_sCon_p{}_e{}_y2040.csv".format(county,par_rate,loc_rate), index = False, header=True)

# %%
for loc_rate in loc_expansion:
     par_rate =40
     df_veh= pd.read_csv(f_dir_2+"vehicle_types_sDmd_G140_y2040.csv")
     df_veh.to_csv(f_dir_out+"vehicle_types_sCon_p{}_e{}_y2040.csv".format(par_rate,loc_rate), index = False, header=True)
     for county in county_list:
          df_payload= pd.read_csv(f_dir_2+"B2C_carrier_county{}_shipall_sDmd_G140_y2040.csv".format(county))
          df_payload.to_csv(f_dir_out+"B2C_carrier_county{}_shipall_sCon_p{}_e{}_y2040.csv".format(county,par_rate,loc_rate), index = False, header=True) 