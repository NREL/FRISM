# %%
from tkinter import X
import pandas as pd
import numpy as np
import joblib
from argparse import ArgumentParser
import config
import random

import statsmodels.api as sm
from sklearn.linear_model import LogisticRegression
import seaborn as sns
import matplotlib.pyplot as plt 
# %%
study_region="SF"

df_hh_model=pd.read_csv('../../../FRISM_input_output_{}/Sim_outputs/Generation/households_del.csv'.format(study_region))


df_hh_obs=pd.read_csv('../../../FRISM_input_output_{}/Model_inputs/NHTS/{}_hh.csv'.format(study_region,study_region))
df_per_obs=pd.read_csv('../../../FRISM_input_output_{}/Model_inputs/NHTS/{}_per.csv'.format(study_region,study_region))
df_per_obs_hh=df_per_obs.groupby(['HOUSEID'])['DELIVER'].agg(delivery_f='sum').reset_index()
df_hh_obs=df_hh_obs.merge(df_per_obs_hh, on='HOUSEID', how='left')

#df_hh_model=pd.read_csv('../../../FRISM_input_output_{}/Sim_outputs/Generation/households_del.csv'.format(study_region))


df_hh_obs['delivery_f'] =df_hh_obs['delivery_f'].apply(lambda x: 0 if np.isnan(x) else int(x))
df_hh_model['delivery_f'] =df_hh_model['delivery_f'].apply(lambda x: 0 if np.isnan(x) else int(x))


list_income=["income_cls_0","Income_cls_1","income_cls_2","income_cls_3"]
dic_income={"income_cls_0": "INCOME <$35k",
            "income_cls_1": "INCOME $35k-$75k",
            "income_cls_2": "INCOME $75k-125k",
            "income_cls_3": "INCOME >$125k"}
    
# for ic_nm in list_income:
#     plt.figure(figsize = (8,6))
#     #plt.hist(df_hh_obs[df_hh_obs[ic_nm]==1]['delivery_f'], color ="blue", density=True, bins=df_hh_obs[df_hh_obs[ic_nm]==1]['delivery_f'].max(), alpha = 0.3, label="observed")
#     #plt.hist(df_hh_model[(df_hh_model[ic_nm]==1) & (df_hh_model['delivery_f']<=30)]['delivery_f'], color ="red", density=True, bins=80, alpha = 0.3, label="modeled")
#     #plt.hist(df_hh_model[(df_hh_model[ic_nm]==1)]['delivery_f'], color ="red", density=True, bins=df_hh_model[(df_hh_model[ic_nm]==1)]['delivery_f'].max(), alpha = 0.3, label="modeled")
#     plt.hist(df_hh_obs[(df_hh_obs[ic_nm]==1) & (df_hh_obs['delivery_f']<=60)]['delivery_f'], color ="blue", density=True, bins=df_hh_obs[(df_hh_obs[ic_nm]==1) & (df_hh_obs['delivery_f']<=60)]['delivery_f'].max(), alpha = 0.3, label="Observed")
#     plt.hist(df_hh_model[(df_hh_model[ic_nm]==1)& (df_hh_model['delivery_f']<=60)]['delivery_f'], color ="red", density=True, bins=df_hh_model[(df_hh_model[ic_nm]==1)& (df_hh_model['delivery_f']<=60)]['delivery_f'].max(), alpha = 0.3, label="Modeled")
#     plt.title("Density of Delivery Frequency in {0}, {1}".format(dic_income[ic_nm], study_region))
#     plt.legend(loc="upper right")
#     plt.savefig('../../../FRISM_input_output_{0}/Sim_outputs/Generation/B2C_delivery_val_{1}.png'.format(study_region, ic_nm))

for ic_nm in list_income:
    plt.figure(figsize = (8,6))
        # creating a dictionary
    font = {'size': 12}
    
    # using rc function
    plt.rc('font', **font)
    binsize=max(df_hh_obs[(df_hh_obs[ic_nm]==1) & (df_hh_obs['delivery_f']<=60)]['delivery_f'].max(), df_hh_model[(df_hh_model[ic_nm]==1)& (df_hh_model['delivery_f']<=60)]['delivery_f'].max())
    x= df_hh_obs[(df_hh_obs[ic_nm]==1) & (df_hh_obs['delivery_f']<=60)]['delivery_f'].to_numpy()
    y= df_hh_model[(df_hh_model[ic_nm]==1)& (df_hh_model['delivery_f']<=60)]['delivery_f'].to_numpy()
    plt.hist([x,y], bins=binsize, color=['dodgerblue','darkorange'], label=["OBSERVED", "MODELED"], density=True)     
    plt.title("DENSITY OF DELIVERY FREQUENCY IN {0}, {1}".format(dic_income[ic_nm], study_region), fontsize=15)
    plt.legend(loc="upper right")
    plt.xlabel('NUMBER OF DELIVERY')
    plt.ylabel('DENSITY')
    plt.savefig('../../../FRISM_input_output_{0}/Sim_outputs/Generation/B2C_delivery_val_{1}.png'.format(study_region, ic_nm))

# %% 

# %%
## Result data
f_dir="../../../Results_from_HPC_sfn_v1/Tour_plan/2018_all/"
#f_dir="../../../Results_from_HPC_v5/Tour_plan/"

MD_df_b2c=pd.DataFrame()

df_payload = pd.read_csv(f_dir+"B2C_all_payload_sBase_y2018.csv")   
df_payload["end_depot"] = df_payload["payloadId"].apply(lambda x: 1 if x.endswith("_") else 0 )
df_payload= df_payload[df_payload["end_depot"]==0].reset_index()
df_payload['start_hour'] = df_payload['estimatedTimeOfArrivalInSec'].apply(lambda x: int(x/3600))
MD_df_b2c= df_payload


MD_df_b2b=pd.DataFrame()
HD_df_b2b=pd.DataFrame()
df_payload = pd.read_csv(f_dir+"B2B_all_payload_sBase_y2018.csv")
df_carr =pd.read_csv(f_dir+"B2B_all_carrier_sBase_y2018.csv")
df_payload["end_depot"] = df_payload["payloadId"].apply(lambda x: 1 if x.endswith("_") else 0 )
df_payload= df_payload[df_payload["end_depot"]==0].reset_index()
df_payload['start_hour'] = df_payload['estimatedTimeOfArrivalInSec'].apply(lambda x: int(x/3600))
df_payload['start_hour'] = df_payload['start_hour'].apply(lambda x: x-24 if x >=24 else x)
df_payload_md = df_payload[df_payload["tourId"].isin(df_carr[df_carr["vehicleTypeId"].str.contains('md')]["tourId"].unique())]#.reset_index()
df_payload_hd = df_payload[df_payload["tourId"].isin(df_carr[df_carr["vehicleTypeId"].str.contains('hd')]["tourId"].unique())]#.reset_index()
MD_df_b2b=df_payload_md
HD_df_b2b=df_payload_hd
MD_df_b2bC = pd.concat([MD_df_b2b,MD_df_b2c], ignore_index=True).reset_index(drop=True)
#MD_df_b2bC = MD_df_b2c
MD_dpt_B2B=  MD_df_b2b.groupby(['start_hour'])['start_hour'].agg(Trip="count").reset_index()
MD_dpt_B2C=  MD_df_b2c.groupby(['start_hour'])['start_hour'].agg(Trip="count").reset_index()
MD_dpt_B2BC=  MD_df_b2bC.groupby(['start_hour'])['start_hour'].agg(Trip="count").reset_index()
HD_dpt_B2B=  HD_df_b2b.groupby(['start_hour'])['start_hour'].agg(Trip="count").reset_index()

MD_dpt_B2B['Trip_rate']=MD_dpt_B2B['Trip']/MD_dpt_B2B['Trip'].sum()
MD_dpt_B2C['Trip_rate']=MD_dpt_B2C['Trip']/MD_dpt_B2C['Trip'].sum()
MD_dpt_B2BC['Trip_rate']=MD_dpt_B2BC['Trip']/MD_dpt_B2BC['Trip'].sum()
HD_dpt_B2B['Trip_rate']=HD_dpt_B2B['Trip']/HD_dpt_B2B['Trip'].sum()

# MD_dpt_B2BC.to_csv(f_dir_val+"md_tod_frism_simulated.csv", index = False, header=True )
# HD_dpt_B2B.to_csv(f_dir_val+"hd_tod_frism_simulated.csv", index = False, header=True )

# %%
from scipy.interpolate import make_interp_spline

# %%
# Define the directory 
f_dir_val= "../../../FRISM_input_output_SF/Validation/"
# %%
# Read TOD from INRIX  
MD_dpt=pd.read_csv(f_dir_val+"md_tod_inrix_observed.csv")
HD_dpt=pd.read_csv(f_dir_val+"hd_tod_inrix_observed.csv" )
# Read TOD from Simulation
# MD_dpt_B2BC=pd.read_csv(f_dir_val+"md_tod_frism_simulated.csv")
# HD_dpt_B2B=pd.read_csv(f_dir_val+"hd_tod_frism_simulated.csv")

# %%
# To convert 24 hour aggregation to spline for smooth plots
md_sim_trip = MD_dpt_B2BC['Trip_rate'].to_numpy()
md_sim_hour = MD_dpt_B2BC['start_hour'].to_numpy()
hd_sim_trip = HD_dpt_B2B['Trip_rate'].to_numpy()
hd_sim_hour = HD_dpt_B2B['start_hour'].to_numpy()

md_inrix_trip = MD_dpt['Trip_rate'].to_numpy()
md_inrix_hour = MD_dpt['start_hour'].to_numpy()
hd_inrix_trip = HD_dpt['Trip_rate'].to_numpy()
hd_inrix_hour = HD_dpt['start_hour'].to_numpy()

md_sim_Spline = make_interp_spline(md_sim_hour, md_sim_trip)
hd_sim_Spline = make_interp_spline(hd_sim_hour, hd_sim_trip)
md_inrix_Spline = make_interp_spline(md_inrix_hour, md_inrix_trip)
hd_inrix_Spline = make_interp_spline(md_inrix_hour, md_inrix_trip)


md_sim_hour = np.linspace(md_sim_hour.min(), md_sim_hour.max(), 24*10)
md_sim_trip = md_sim_Spline(md_sim_hour)
hd_sim_hour = np.linspace(hd_sim_hour.min(), hd_sim_hour.max(), 24*10)
hd_sim_trip = hd_sim_Spline(hd_sim_hour)

 
md_inrix_hour = np.linspace(md_inrix_hour.min(), hd_inrix_hour.max(), 24*10)
md_inrix_trip = md_inrix_Spline(md_inrix_hour)
hd_inrix_hour = np.linspace(hd_inrix_hour.min(), hd_inrix_hour.max(), 24*10)
hd_inrix_trip = hd_inrix_Spline(hd_inrix_hour)

# Plot for MD
  
plt.figure(figsize = (8,6))
font = {'size': 12}

# using rc function
plt.rc('font', **font)
plt.plot(md_inrix_hour,md_inrix_trip,color ="dodgerblue", label="OBSERVED (INRIX)")
plt.plot(md_sim_hour,md_sim_trip , color ="darkorange", label="SIMULATED (FRISM)")
plt.title("DISTRIBUTION OF MD TIME OF DAY STOP ACTIVITY")
plt.legend(loc="upper right")
plt.xlabel('TIME OF DAY')
plt.ylabel('DENSITY')
plt.savefig(f_dir_val+'Val_truck_dist_MD.png')
# Plot for HD
plt.figure(figsize = (8,6))
plt.plot(hd_inrix_hour,hd_inrix_trip,color ="dodgerblue", label="OBSERVED (INRIX)")
plt.plot(hd_sim_hour,hd_sim_trip , color ="darkorange", label="SIMULATED (FRISM)")
plt.title("DISTRIBUTION OF MD TIME OF DAY STOP ACTIVITY")
plt.legend(loc="upper right")
plt.xlabel('TIME OF DAY')
plt.ylabel('DENSITY')
plt.savefig(f_dir_val+'Val_truck_dist_HD.png')
# %%
tour_length_B2C = MD_df_b2c.groupby(['tourId'])['tourId'].agg(Trip="count").reset_index()
tour_length_B2B = df_payload.groupby(['tourId'])['tourId'].agg(Trip="count").reset_index()
tour_length_B2B["tourId"]=tour_length_B2B["tourId"].apply(lambda x: x+1040)
tour_length_all = pd.concat([tour_length_B2C,tour_length_B2B], ignore_index=True).reset_index(drop=True)
tour_length_all["Trip"]=tour_length_all["Trip"].apply(lambda x: x-1)
sim_rate = tour_length_all.groupby(["Trip"])['Trip'].agg(num="count").reset_index()
sim_rate=sim_rate[sim_rate["Trip"]<=20]
sim_rate["stop_rate"] = sim_rate['num']/sim_rate['num'].sum()

# %%
observed= pd.read_csv("/Users/kjeong/KJ_NREL_Work/1_Work/1_2_SMART_2_0/Model_development/FRISM_input_output_SF/Sim_inputs/Tour_constraint/all.csv")
O=observed['Rate'].to_numpy()
S=sim_rate["stop_rate"].to_numpy()
r=sim_rate["Trip"].to_numpy()
width=0.5

plt.bar (r, O, color= "dodgerblue", width=width, label="OBSERVED")
plt.bar (r+width, S, color= "darkorange", width=width, label="SIMULATED")
plt.title("DISTRIBUTION OF TRIPS PER TOUR")
plt.legend(loc="upper right")
plt.xlabel('NUMBER OF TRIPS')
plt.ylabel('DENSITY')
plt.xticks(r + width/2,r)
plt.savefig(f_dir_val+'stops.png')
# %%
sim_rate[sim_rate["Trip"]<=4]['stop_rate'].sum()
# %%
observed[observed["Trips"]<=4]['Rate'].sum()