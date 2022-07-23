# %%
from sys import platform
from matplotlib.image import AxesImage
import pandas as pd
import numpy as np
#import geopandas as gpd
#import networkx as nx
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline

# %%
# Define the directory 
f_dir_val= "../../../FRISM_input_output_SF/Validation/"
# %%
# Read TOD from INRIX  
MD_dpt=pd.read_csv(f_dir_val+"md_tod_inrix_observed.csv")
HD_dpt=pd.read_csv(f_dir_val+"hd_tod_inrix_observed.csv" )
# Read TOD from Simulation
MD_dpt_B2BC=pd.read_csv(f_dir_val+"md_tod_frism_simulated.csv")
HD_dpt_B2B=pd.read_csv(f_dir_val+"hd_tod_frism_simulated.csv")

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
plt.plot(md_inrix_hour,md_inrix_trip,color ="blue", label="Observed (INRIX)", alpha = 0.3,)
plt.plot(md_sim_hour,md_sim_trip , color ="red", label="Simulated (FRISM)", alpha = 0.3,)
plt.title("Distrubtion of MD stop activities  by time of day")
plt.legend(loc="upper right")
plt.savefig(f_dir_val+'Val_truck_dist_MD.png')
# Plot for HD
plt.figure(figsize = (8,6))
plt.plot(hd_inrix_hour,hd_inrix_trip,color ="blue", label="Observed (INRIX)", alpha = 0.3,)
plt.plot(hd_sim_hour,hd_sim_trip , color ="red", label="Simulated (FRISM)", alpha = 0.3,)
plt.title("Distrubtion of HD stop activities by time of day")
plt.legend(loc="upper right")
plt.savefig(f_dir_val+'Val_truck_dist_HD.png')

'''
############################# SF vs AT ######################################
'''
# %%
fdir_sf="../../../FRISM_input_output_SF/Sim_outputs/"
fdir_at="../../../FRISM_input_output_AT/Sim_outputs/"
'''
"Shipment2Fleet/B2B_carrier_county{}_shipall_A.csv".format(county)
"Shipment2Fleet/B2B_payload_county{}_shipall_A.csv".format(county)
"Tour_plan/B2B_county{}_payload.csv".format(county)
"Tour_plan/B2B_county{}_freight_tours.csv".format(county)
"Tour_plan/B2B_county{]_carrier.csv".format(county)
'''


county_list_sf=[1, 13, 41, 55, 75, 81, 85, 95, 97]
county_list_at=[453, 491, 209, 55, 21, 53]

num_stat_df=pd.DataFrame({'type': ["SF_B2B","AT_B2B", "SF_B2C", "AT_B2C"], 'num_tour': [0, 0,0,0], 'num_shipment': [0, 0,0,0]})
for county in county_list_sf:
    df=pd.read_csv(fdir_sf+"Tour_plan/B2B_county{}_freight_tours.csv".format(county))
    num_stat_df.loc[num_stat_df['type']=="SF_B2B","num_tour"]=num_stat_df.loc[num_stat_df['type']=="SF_B2B","num_tour"]+df.shape[0]
    df=pd.read_csv(fdir_sf+"Tour_plan/B2C_county{}_freight_tours.csv".format(county))
    num_stat_df.loc[num_stat_df['type']=="SF_B2C","num_tour"]=num_stat_df.loc[num_stat_df['type']=="SF_B2C","num_tour"]+df.shape[0]

    df=pd.read_csv(fdir_sf+"Shipment2Fleet/B2B_payload_county{}_shipall_A.csv".format(county))
    num_stat_df.loc[num_stat_df['type']=="SF_B2B","num_shipment"]=num_stat_df.loc[num_stat_df['type']=="SF_B2B","num_shipment"]+df.shape[0]
    df=pd.read_csv(fdir_sf+"Shipment2Fleet/B2C_payload_county{}_shipall.csv".format(county))
    num_stat_df.loc[num_stat_df['type']=="SF_B2C","num_shipment"]=num_stat_df.loc[num_stat_df['type']=="SF_B2C","num_shipment"]+df.shape[0]

for county in county_list_at:
    df=pd.read_csv(fdir_at+"Tour_plan/B2B_county{}_freight_tours.csv".format(county))
    num_stat_df.loc[num_stat_df['type']=="AT_B2B","num_tour"]=num_stat_df.loc[num_stat_df['type']=="AT_B2B","num_tour"]+df.shape[0]
    df=pd.read_csv(fdir_at+"Tour_plan/B2C_county{}_freight_tours.csv".format(county))
    num_stat_df.loc[num_stat_df['type']=="AT_B2C","num_tour"]=num_stat_df.loc[num_stat_df['type']=="AT_B2C","num_tour"]+df.shape[0]

    df=pd.read_csv(fdir_at+"Shipment2Fleet/B2B_payload_county{}_shipall_A.csv".format(county))
    num_stat_df.loc[num_stat_df['type']=="AT_B2B","num_shipment"]=num_stat_df.loc[num_stat_df['type']=="AT_B2B","num_shipment"]+df.shape[0]
    df=pd.read_csv(fdir_at+"Shipment2Fleet/B2C_payload_county{}_shipall.csv".format(county))
    num_stat_df.loc[num_stat_df['type']=="AT_B2C","num_shipment"]=num_stat_df.loc[num_stat_df['type']=="AT_B2C","num_shipment"]+df.shape[0]   
# %%
ax=num_stat_df.plot.barh(x='type', y='num_tour', title="Number of tours")
ax.figure.savefig("../../../total_tours.png")

ax=num_stat_df.plot.barh(x='type', y='num_shipment', title="Number of shipments")
ax.figure.savefig("../../../total_shipments.png")

# %%
num_stop_sf=pd.DataFrame()
for county in county_list_sf:
    df=pd.read_csv(fdir_sf+"Tour_plan/B2B_county{}_payload.csv".format(county))
    df_group=df.groupby(['tourId'])['tourId'].count().reset_index(name='num_stop')
    df_group['num_stop']=df_group['num_stop']-2
    num_stop_sf=pd.concat([num_stop_sf,df_group], ignore_index=True).reset_index(drop=True)
    
num_stop_at=pd.DataFrame()
for county in county_list_at:
    df=pd.read_csv(fdir_at+"Tour_plan/B2B_county{}_payload.csv".format(county))
    df_group=df.groupby(['tourId'])['tourId'].count().reset_index(name='num_stop')
    df_group['num_stop']=df_group['num_stop']-2
    num_stop_at=pd.concat([num_stop_at,df_group], ignore_index=True).reset_index(drop=True)
    
plt.figure(figsize = (8,6))
plt.hist(num_stop_sf['num_stop'], density=True, color ="blue", alpha = 0.3, label="B2B_SF", bins=np.arange(min(num_stop_sf['num_stop']), max(num_stop_sf['num_stop']) + 1, 1))
plt.hist(num_stop_at['num_stop'], density=True, color ="red", alpha = 0.3, label="B2B_AT", bins=np.arange(min(num_stop_sf['num_stop']), max(num_stop_sf['num_stop']) + 1, 1))
plt.title("B2B Number of Stops")
plt.legend(loc="upper right")
plt.savefig("../../../num_stop_b2b.png")
# %%
num_stop_sf=pd.DataFrame()
for county in county_list_sf:
    df=pd.read_csv(fdir_sf+"Tour_plan/B2C_county{}_payload.csv".format(county))
    df_group=df.groupby(['tourId'])['tourId'].count().reset_index(name='num_stop')
    df_group['num_stop']=df_group['num_stop']-2
    num_stop_sf=pd.concat([num_stop_sf,df_group], ignore_index=True).reset_index(drop=True)
    
num_stop_at=pd.DataFrame()
for county in county_list_at:
    df=pd.read_csv(fdir_at+"Tour_plan/B2C_county{}_payload.csv".format(county))
    df_group=df.groupby(['tourId'])['tourId'].count().reset_index(name='num_stop')
    df_group['num_stop']=df_group['num_stop']-2
    num_stop_at=pd.concat([num_stop_at,df_group], ignore_index=True).reset_index(drop=True)
    
plt.figure(figsize = (8,6))
plt.hist(num_stop_sf['num_stop'], density=True, color ="blue", alpha = 0.3, label="B2C_SF", bins=np.arange(min(num_stop_sf['num_stop']), max(num_stop_sf['num_stop']) + 1, 1))
plt.hist(num_stop_at['num_stop'], density=True, color ="red", alpha = 0.3, label="B2C_AT", bins=np.arange(min(num_stop_sf['num_stop']), max(num_stop_sf['num_stop']) + 1, 1))
plt.title("B2C Number of Stops")
plt.legend(loc="upper right")
plt.savefig("../../../num_stop_b2c.png")


# %%
stop_time_sf=pd.DataFrame()
for county in county_list_sf:
    df=pd.read_csv(fdir_sf+"Tour_plan/B2B_county{}_payload.csv".format(county))
    df=df[['operationDurationInSec']]
    df=df[df['operationDurationInSec']>0]
    df['op_min']=df['operationDurationInSec'].apply(lambda x: round(x/60))
    stop_time_sf=pd.concat([stop_time_sf,df], ignore_index=True).reset_index(drop=True)
    
stop_time_at=pd.DataFrame()
for county in county_list_at:
    df=pd.read_csv(fdir_at+"Tour_plan/B2B_county{}_payload.csv".format(county))
    df=df[['operationDurationInSec']]
    df=df[df['operationDurationInSec']>0]
    df['op_min']=df['operationDurationInSec'].apply(lambda x: round(x/60))
    stop_time_at=pd.concat([stop_time_at,df], ignore_index=True).reset_index(drop=True)
    
plt.figure(figsize = (8,6))
plt.hist(stop_time_sf['op_min'], density=True, color ="blue", alpha = 0.3, label="B2B_SF", bins=np.arange(min(stop_time_sf['op_min']), max(stop_time_sf['op_min']) + 10, 10))
plt.hist(stop_time_at['op_min'], density=True, color ="red", alpha = 0.3, label="B2B_AT", bins=np.arange(min(stop_time_sf['op_min']), max(stop_time_sf['op_min']) + 10, 10))
plt.title("B2B stop duration")
plt.legend(loc="upper right")
plt.savefig("../../../stop_duration_b2b.png")
print ("B2B avg stop SF: {}". format(stop_time_sf['op_min'].mean()))
print ("B2B avg stop AT: {}". format(stop_time_at['op_min'].mean()))

stop_time_sf=pd.DataFrame()
for county in county_list_sf:
    df=pd.read_csv(fdir_sf+"Tour_plan/B2C_county{}_payload.csv".format(county))
    df=df[['operationDurationInSec']]
    df=df[df['operationDurationInSec']>0]
    df['op_min']=df['operationDurationInSec'].apply(lambda x: round(x/60))
    stop_time_sf=pd.concat([stop_time_sf,df], ignore_index=True).reset_index(drop=True)
    
stop_time_at=pd.DataFrame()
for county in county_list_at:
    df=pd.read_csv(fdir_at+"Tour_plan/B2C_county{}_payload.csv".format(county))
    df=df[['operationDurationInSec']]
    df=df[df['operationDurationInSec']>0]
    df['op_min']=df['operationDurationInSec'].apply(lambda x: round(x/60))
    stop_time_at=pd.concat([stop_time_at,df], ignore_index=True).reset_index(drop=True)
    
plt.figure(figsize = (8,6))
plt.hist(stop_time_sf['op_min'], density=True, color ="blue", alpha = 0.3, label="B2C_SF", bins=np.arange(min(stop_time_sf['op_min']), max(stop_time_sf['op_min']) + 10, 10))
plt.hist(stop_time_at['op_min'], density=True, color ="red", alpha = 0.3, label="B2C_AT", bins=np.arange(min(stop_time_sf['op_min']), max(stop_time_sf['op_min']) + 10, 10))
plt.title("B2C stop duration")
plt.legend(loc="upper right")
plt.savefig("../../../stop_duration_b2c.png")
print ("B2C avg stop SF: {}". format(stop_time_sf['op_min'].mean()))
print ("B2C avg stop AT: {}". format(stop_time_at['op_min'].mean()))
# %%
# %%
stop_time_sf=pd.DataFrame()
for county in county_list_sf:
    df=pd.read_csv(fdir_sf+"Tour_plan/B2B_county{}_payload.csv".format(county))
    df['t_time']=0
    for i in range (1,df.shape[0]):
        if df['sequenceRank'].loc[i] == 0:
            df['t_time'].loc[i] =0
        else:     
            df['t_time'].loc[i]=df['estimatedTimeOfArrivalInSec'].loc[i]-df['estimatedTimeOfArrivalInSec'].loc[i-1] - df['operationDurationInSec'].loc[i-1] 
    df=df[['t_time']]
    df=df[df['t_time']>0]
    df['t_time']=df['t_time'].apply(lambda x: round(x/60))
    stop_time_sf=pd.concat([stop_time_sf,df], ignore_index=True).reset_index(drop=True)
    
stop_time_at=pd.DataFrame()
for county in county_list_at:
    df=pd.read_csv(fdir_at+"Tour_plan/B2B_county{}_payload.csv".format(county))
    df['t_time']=0
    for i in range (1,df.shape[0]):
        if df['sequenceRank'].loc[i] == 0:
            df['t_time'].loc[i] =0
        else:     
            df['t_time'].loc[i]=df['estimatedTimeOfArrivalInSec'].loc[i]-df['estimatedTimeOfArrivalInSec'].loc[i-1] - df['operationDurationInSec'].loc[i-1] 
    df=df[['t_time']]
    df=df[df['t_time']>0]
    df['t_time']=df['t_time'].apply(lambda x: round(x/60))
    stop_time_at=pd.concat([stop_time_at,df], ignore_index=True).reset_index(drop=True)
    
plt.figure(figsize = (8,6))
plt.hist(stop_time_sf['t_time'], density=True, color ="blue", alpha = 0.3, label="B2B_SF", bins=np.arange(min(stop_time_sf['t_time']), max(stop_time_sf['t_time']) + 10, 10))
plt.hist(stop_time_at['t_time'], density=True, color ="red", alpha = 0.3, label="B2B_AT", bins=np.arange(min(stop_time_sf['t_time']), max(stop_time_sf['t_time']) + 10, 10))
plt.title("B2B travel time")
plt.legend(loc="upper right")
plt.savefig("../../../travel time_b2b.png")
print ("B2B avg travel SF: {}". format(stop_time_sf['t_time'].mean()))
print ("B2B avg travel AT: {}". format(stop_time_at['t_time'].mean()))

stop_time_sf=pd.DataFrame()
for county in county_list_sf:
    df=pd.read_csv(fdir_sf+"Tour_plan/B2C_county{}_payload.csv".format(county))
    df['t_time']=0
    for i in range (1,df.shape[0]):
        if df['sequenceRank'].loc[i] == 0:
            df['t_time'].loc[i] =0
        else:     
            df['t_time'].loc[i]=df['estimatedTimeOfArrivalInSec'].loc[i]-df['estimatedTimeOfArrivalInSec'].loc[i-1] - df['operationDurationInSec'].loc[i-1] 
    df=df[['t_time']]
    df=df[df['t_time']>0]
    df['t_time']=df['t_time'].apply(lambda x: round(x/60))
    stop_time_sf=pd.concat([stop_time_sf,df], ignore_index=True).reset_index(drop=True)
    
stop_time_at=pd.DataFrame()
for county in county_list_at:
    df=pd.read_csv(fdir_at+"Tour_plan/B2C_county{}_payload.csv".format(county))
    df['t_time']=0
    for i in range (1,df.shape[0]):
        if df['sequenceRank'].loc[i] == 0:
            df['t_time'].loc[i] =0
        else:     
            df['t_time'].loc[i]=df['estimatedTimeOfArrivalInSec'].loc[i]-df['estimatedTimeOfArrivalInSec'].loc[i-1] - df['operationDurationInSec'].loc[i-1] 
    df=df[['t_time']]
    df=df[df['t_time']>0]
    df['t_time']=df['t_time'].apply(lambda x: round(x/60))
    stop_time_at=pd.concat([stop_time_at,df], ignore_index=True).reset_index(drop=True)
    
plt.figure(figsize = (8,6))
plt.hist(stop_time_sf['t_time'], density=True, color ="blue", alpha = 0.3, label="B2C_SF", bins=np.arange(min(stop_time_sf['t_time']), max(stop_time_sf['t_time']) + 10, 10))
plt.hist(stop_time_at['t_time'], density=True, color ="red", alpha = 0.3, label="B2C_AT", bins=np.arange(min(stop_time_sf['t_time']), max(stop_time_sf['t_time']) + 10, 10))
plt.title("B2C travel time ")
plt.legend(loc="upper right")
plt.savefig("../../../travel time_b2c.png")
print ("B2C avg travel SF: {}". format(stop_time_sf['t_time'].mean()))
print ("B2C avg travel AT: {}". format(stop_time_at['t_time'].mean()))


# %%
'''
############################# SF vs AT ######################################
'''
# Define the directory 
f_dir_val= "../../../FRISM_input_output_AT/Validation/"
# %%
# Read TOD from INRIX  
MD_dpt=pd.read_csv(f_dir_val+"md_tod_inrix_observed.csv")
HD_dpt=pd.read_csv(f_dir_val+"hd_tod_inrix_observed.csv" )
# Read TOD from Simulation
MD_dpt_B2BC=pd.read_csv(f_dir_val+"md_tod_frism_simulated.csv")
HD_dpt_B2B=pd.read_csv(f_dir_val+"hd_tod_frism_simulated.csv")

# %% 
# Austin Validation 
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
plt.plot(md_inrix_hour,md_inrix_trip,color ="blue", label="Observed (INRIX)", alpha = 0.3,)
plt.plot(md_sim_hour,md_sim_trip , color ="red", label="Simulated (FRISM)", alpha = 0.3,)
plt.title("Distrubtion of MD stop activities  by time of day")
plt.legend(loc="upper right")
plt.savefig(f_dir_val+'Val_truck_dist_MD.png')
# Plot for HD
plt.figure(figsize = (8,6))
plt.plot(hd_inrix_hour,hd_inrix_trip,color ="blue", label="Observed (INRIX)", alpha = 0.3,)
plt.plot(hd_sim_hour,hd_sim_trip , color ="red", label="Simulated (FRISM)", alpha = 0.3,)
plt.title("Distrubtion of HD stop activities by time of day")
plt.legend(loc="upper right")
plt.savefig(f_dir_val+'Val_truck_dist_HD.png')

# %%
