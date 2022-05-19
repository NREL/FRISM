
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
#import plotly.graph_objects as go

'''
Plot stop locations on the map 
'''
# %%
parser = ArgumentParser()
parser.add_argument("-st", "--shipment type", dest="ship_type",
                    help="B2B or B2C", required=True, type=str)
args = parser.parse_args()

# %%
county_list=[1, 13, 41, 55, 75, 81, 85, 95, 97]
sf_map = plt.imread('../../../FRISM_input_output_SF/Sim_inputs/Geo_data/SF_map.png')
BBox= (-123.655,-121.524,36.869,38.852)
#BBox= (-122.9,-121.6,37.0,38.5)
# %%
#
# ship_type=args.ship_type
ship_type="B2B"
#ship_type="B2B"
for count_num in county_list:

    payload_df=pd.read_csv("../../../FRISM_input_output/Sim_outputs/Tour_plan/{0}_county{1}_payload_xy.csv" .format(ship_type, count_num))
    #'locationZone_x':long, 'locationZone_y':lat
    fig, ax = plt.subplots(figsize = (9.68,11.45))
    ax.scatter(payload_df.locationZone_x, payload_df.locationZone_y, zorder=1, alpha= 0.2, c='b', s=10)
    ax.set_title('Plotting payload points for county{0}'.format(count_num))
    ax.set_xlim(BBox[0],BBox[1])
    ax.set_ylim(BBox[2],BBox[3])
    ax.imshow(sf_map, zorder=0, extent = BBox, aspect= 'equal')
    fig.savefig('../../../FRISM_input_output/Sim_outputs/{0}payload_plot_county{1}.png'.format(ship_type, count_num))

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
sf_shape_file=CBGzone_df[CBGzone_df["County"].isin(county_list)]

# %%

ship_type="B2B"
#ship_type="B2B"
payload_df=pd.DataFrame()
for count_num in county_list:
    temp=pd.read_csv("../../../Results_from_HPC_v2/Shipment2Fleet/{0}_payload_county{1}_shipall.csv" .format(ship_type, count_num))
    payload_df=pd.concat([payload_df,temp],ignore_index=True)

payload_by_meso=payload_df.groupby(['del_zone'])['del_zone'].agg(agg_ship="count").reset_index()
payload_by_meso['agg_ship']=payload_by_meso['agg_ship']*10
sf_shape_file=sf_shape_file.merge(payload_by_meso,  left_on="MESOZONE",  right_on="del_zone", how="left" )
sf_shape_file.to_file(fdir_geo+"{}_aggregated_demand.geojson".format(ship_type), driver='GeoJSON')

'''
https://api.mapbox.com/styles/v1/ksjeong/cl1y7ojor001314o5mg62wtd7/wmts?access_token=pk.eyJ1Ijoia3NqZW9uZyIsImEiOiJjbDF5N3p4amcwN2ltM2ptZjl2cnQ5YW42In0.hj4c3SVS9YLVe5YTiDdJDw
'''
################################################################################################################

# %%

'''
Plot web-based results by income-group
'''
study_region= "SF" #"AT" 
web_obs=pd.read_csv('../../../FRISM_input_output_{}/Sim_outputs/Generation/{}_webuse_by_income_observed.csv'.format(study_region,study_region))
online_bi_obs=pd.read_csv('../../../FRISM_input_output_{}/Sim_outputs/Generation/{}_online_by_income_observed.csv'.format(study_region,study_region))

df_hh_obs=pd.read_csv('../../../FRISM_input_output_{}/Model_inputs/NHTS/{}_hh.csv'.format(study_region,study_region))
df_per_obs=pd.read_csv('../../../FRISM_input_output_{}/Model_inputs/NHTS/{}_per.csv'.format(study_region,study_region))
df_per_obs_hh=df_per_obs.groupby(['HOUSEID'])['DELIVER'].agg(delivery_f='sum').reset_index()
df_hh_obs=df_hh_obs.merge(df_per_obs_hh, on='HOUSEID', how='left')

df_hh_model=pd.read_csv('../../../FRISM_input_output_{}/Sim_outputs/Generation/households_del.csv'.format(study_region))


df_hh_obs['delivery_f'] =df_hh_obs['delivery_f'].apply(lambda x: 0 if np.isnan(x) else int(x))
df_hh_model['delivery_f'] =df_hh_model['delivery_f'].apply(lambda x: 0 if np.isnan(x) else int(x))


list_income=["income_cls_0","income_cls_1","income_cls_2","income_cls_3"]
dic_income={"income_cls_0": "income <$35k",
            "income_cls_1": "income $35k-$75k",
            "income_cls_2": "income $75k-125k",
            "income_cls_3": "income >$125k"}
     
for ic_nm in list_income:
    plt.figure(figsize = (8,6))
    #plt.hist(df_hh_obs[df_hh_obs[ic_nm]==1]['delivery_f'], color ="blue", density=True, bins=df_hh_obs[df_hh_obs[ic_nm]==1]['delivery_f'].max(), alpha = 0.3, label="observed")
    #plt.hist(df_hh_model[(df_hh_model[ic_nm]==1) & (df_hh_model['delivery_f']<=30)]['delivery_f'], color ="red", density=True, bins=80, alpha = 0.3, label="modeled")
    #plt.hist(df_hh_model[(df_hh_model[ic_nm]==1)]['delivery_f'], color ="red", density=True, bins=df_hh_model[(df_hh_model[ic_nm]==1)]['delivery_f'].max(), alpha = 0.3, label="modeled")
    plt.hist(df_hh_obs[(df_hh_obs[ic_nm]==1) & (df_hh_obs['delivery_f']<=60)]['delivery_f'], color ="blue", density=True, bins=df_hh_obs[(df_hh_obs[ic_nm]==1) & (df_hh_obs['delivery_f']<=60)]['delivery_f'].max(), alpha = 0.3, label="observed")
    plt.hist(df_hh_model[(df_hh_model[ic_nm]==1)& (df_hh_model['delivery_f']<=60)]['delivery_f'], color ="red", density=True, bins=df_hh_model[(df_hh_model[ic_nm]==1)& (df_hh_model['delivery_f']<=60)]['delivery_f'].max(), alpha = 0.3, label="modeled")
    plt.title("Density of Delivery Frequency in {0}, {1}".format(dic_income[ic_nm], study_region))
    plt.legend(loc="upper right")
    plt.savefig('../../../FRISM_input_output_{0}/Sim_outputs/Generation/B2C_delivery_val_{1}.png'.format(study_region, ic_nm))


################################################################################################################    


# %%
############################################# Validation TOD distribution against INRIX #####################
'''
Plot INRIX vs Simulated stop activities 
'''
s_region="AT"
CBG_file= 'Austin_freight.geojson' #'freight_centroids.geojson'
# SF
#county_list=[1, 13, 41, 55, 75, 81, 85, 95, 97]
# AT
county_list=[21,55,209.453,491]
## INRIX data
fdir_truck='../../../FRISM_input_output_{}/Model_carrier_op/INRIX_processing/'.format(s_region)
df_dpt_dist_MD=pd.read_csv(fdir_truck+'depature_dist_by_cbg_MD.csv', header=0, sep=',')
df_dpt_dist_HD=pd.read_csv(fdir_truck+'depature_dist_by_cbg_HD.csv', header=0, sep=',')

fdir_geo='../../../FRISM_input_output_{}/Sim_inputs/Geo_data/'.format(s_region)

CBGzone_df = gpd.read_file(fdir_geo+CBG_file)

CBGzone_df["GEOID"]=CBGzone_df["GEOID"].astype(str)
## Add county id from GEOID
CBGzone_df["County"]=CBGzone_df["GEOID"].apply(lambda x: x[2:5] if len(x)>=12 else 0)
CBGzone_df["County"]=CBGzone_df["County"].astype(str).astype(int)
CBGzone_df["GEOID"]=CBGzone_df["GEOID"].astype(str).astype(int)
CBGzone_df=CBGzone_df[CBGzone_df["County"]!=0].reset_index()


df_dpt_dist_MD=df_dpt_dist_MD.merge(CBGzone_df[["GEOID",'MESOZONE',"County"]], left_on="cbg_id", right_on="GEOID", how='left')
df_dpt_dist_HD=df_dpt_dist_HD.merge(CBGzone_df[["GEOID",'MESOZONE',"County"]], left_on="cbg_id", right_on="GEOID", how='left')
# sel_zone= pd.read_csv(fdir_geo+'selected zone.csv')
# sel_zone=sel_zone.rename({'blkgrpid':'GEOID'}, axis=1)
# sel_zone = sel_zone.merge(CBGzone_df[['GEOID','MESOZONE']], on='GEOID', how='left')

df_dpt_dist_MD=df_dpt_dist_MD[df_dpt_dist_MD['County'].isin(county_list)].reset_index()
df_dpt_dist_HD=df_dpt_dist_HD[df_dpt_dist_HD['County'].isin(county_list)].reset_index()

MD_dpt= df_dpt_dist_MD.groupby(['start_hour'])['Trip'].sum()
MD_dpt=MD_dpt.to_frame()
MD_dpt.reset_index(level=(0), inplace=True)
MD_dpt['Trip_rate']=MD_dpt['Trip']/MD_dpt['Trip'].sum()

HD_dpt= df_dpt_dist_HD.groupby(['start_hour'])['Trip'].sum()
HD_dpt=HD_dpt.to_frame()
HD_dpt.reset_index(level=(0), inplace=True)
HD_dpt['Trip_rate']=HD_dpt['Trip']/HD_dpt['Trip'].sum()

f_dir_val= "../../../FRISM_input_output_{}/Validation/".format(s_region)
MD_dpt.to_csv(f_dir_val+"md_tod_inrix_observed.csv", index = False, header=True )
HD_dpt.to_csv(f_dir_val+"hd_tod_inrix_observed.csv", index = False, header=True )
# %%
## Result data
f_dir="../../../FRISM_input_output_{}/Sim_outputs/Tour_plan/".format(s_region)
#f_dir="../../../Results_from_HPC_v5/Tour_plan/"

MD_df_b2c=pd.DataFrame()
v_type= "B2C"
for county in county_list:
    df_payload = pd.read_csv(f_dir+"{}_county{}_payload.csv".format(v_type,str(county)))
    df_payload["end_depot"] = df_payload["payloadId"].apply(lambda x: 1 if x.endswith("_") else 0 )
    df_payload= df_payload[df_payload["end_depot"]==0].reset_index()
    df_payload['start_hour'] = df_payload['estimatedTimeOfArrivalInSec'].apply(lambda x: int(x/3600))
    MD_df_b2c=pd.concat([MD_df_b2c,df_payload], ignore_index=True).reset_index(drop=True)


MD_df_b2b=pd.DataFrame()
HD_df_b2b=pd.DataFrame()
v_type= "B2B"
for county in county_list:
    df_payload = pd.read_csv(f_dir+"{}_county{}_payload.csv".format(v_type,str(county)))
    df_carr =pd.read_csv(f_dir+"{}_county{}_carrier.csv".format(v_type,str(county)))
    df_payload["end_depot"] = df_payload["payloadId"].apply(lambda x: 1 if x.endswith("_") else 0 )
    df_payload= df_payload[df_payload["end_depot"]==0].reset_index()
    df_payload['start_hour'] = df_payload['estimatedTimeOfArrivalInSec'].apply(lambda x: int(x/3600))
    df_payload['start_hour'] = df_payload['start_hour'].apply(lambda x: x-24 if x >=24 else x)
    df_payload_md = df_payload[df_payload["tourId"].isin(df_carr[df_carr["vehicleTypeId"]==1]["tourId"].unique())]#.reset_index()
    df_payload_hd = df_payload[df_payload["tourId"].isin(df_carr[df_carr["vehicleTypeId"]==2]["tourId"].unique())]#.reset_index()
    MD_df_b2b=pd.concat([MD_df_b2b,df_payload_md], ignore_index=True).reset_index(drop=True)
    HD_df_b2b=pd.concat([HD_df_b2b,df_payload_hd], ignore_index=True).reset_index(drop=True)
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

MD_dpt_B2BC.to_csv(f_dir_val+"md_tod_frism_simulated.csv", index = False, header=True )
HD_dpt_B2B.to_csv(f_dir_val+"hd_tod_frism_simulated.csv", index = False, header=True )

from scipy.interpolate import make_interp_spline

md_sim_trip = MD_dpt_B2BC['Trip_rate'].to_numpy()
md_sim_hour = MD_dpt_B2BC['start_hour'].to_numpy()
hd_sim_trip = HD_dpt_B2B['Trip_rate'].to_numpy()
hd_sim_hour = HD_dpt_B2B['start_hour'].to_numpy()

md2b_sim_trip = MD_dpt_B2B['Trip_rate'].to_numpy()
md2b_sim_hour = MD_dpt_B2B['start_hour'].to_numpy()
md2c_sim_trip = MD_dpt_B2C['Trip_rate'].to_numpy()
md2c_sim_hour = MD_dpt_B2C['start_hour'].to_numpy()

md_inrix_trip = MD_dpt['Trip_rate'].to_numpy()
md_inrix_hour = MD_dpt['start_hour'].to_numpy()
hd_inrix_trip = HD_dpt['Trip_rate'].to_numpy()
hd_inrix_hour = HD_dpt['start_hour'].to_numpy()

md_sim_Spline = make_interp_spline(md_sim_hour, md_sim_trip)
hd_sim_Spline = make_interp_spline(hd_sim_hour, hd_sim_trip)
md_inrix_Spline = make_interp_spline(md_inrix_hour, md_inrix_trip)
hd_inrix_Spline = make_interp_spline(hd_inrix_hour, hd_inrix_trip)


md2b_sim_Spline = make_interp_spline(md2b_sim_hour, md2b_sim_trip)
md2c_sim_Spline = make_interp_spline(md2c_sim_hour, md2c_sim_trip)

md_sim_hour = np.linspace(md_sim_hour.min(), md_sim_hour.max(), 24*10)
md_sim_trip = md_sim_Spline(md_sim_hour)
hd_sim_hour = np.linspace(hd_sim_hour.min(), hd_sim_hour.max(), 24*10)
hd_sim_trip = hd_sim_Spline(hd_sim_hour)

md2b_sim_hour = np.linspace(md2b_sim_hour.min(), md2b_sim_hour.max(), 24*10)
md2b_sim_trip = md2b_sim_Spline(md2b_sim_hour)
md2c_sim_hour = np.linspace(md2c_sim_hour.min(), md2c_sim_hour.max(), 24*10)
md2c_sim_trip = md2c_sim_Spline(md2c_sim_hour)
 
md_inrix_hour = np.linspace(md_inrix_hour.min(), md_inrix_hour.max(), 24*10)
md_inrix_trip = md_inrix_Spline(md_inrix_hour)
hd_inrix_hour = np.linspace(hd_inrix_hour.min(), hd_inrix_hour.max(), 24*10)
hd_inrix_trip = hd_inrix_Spline(hd_inrix_hour)

plt.figure(figsize = (8,6))
plt.plot(md_inrix_hour,md_inrix_trip,color ="blue", alpha = 0.2,)
plt.plot(md_sim_hour,md_sim_trip , color ="red", alpha = 0.2,)
plt.fill_between(md_inrix_hour,md_inrix_trip,color ="blue", label="Observed (INRIX)", alpha = 0.2,)
plt.fill_between(md_sim_hour,md_sim_trip , color ="red", label="Simulated (FRISM)", alpha = 0.2,)
plt.title("Distrubtion of MD stop activities  by time of day")
plt.legend(loc="upper right")
plt.savefig('../../../FRISM_input_output_{}/Sim_outputs/Val_truck_dist_MD.png'.format(s_region))

plt.figure(figsize = (8,6))
plt.plot(hd_inrix_hour,hd_inrix_trip,color ="blue", alpha = 0.2,)
plt.plot(hd_sim_hour,hd_sim_trip , color ="red", alpha = 0.2,)
plt.fill_between(hd_inrix_hour,hd_inrix_trip,color ="blue", alpha = 0.2,label="Observed (INRIX)")
plt.fill_between(hd_sim_hour,hd_sim_trip , color ="red", alpha = 0.2,label="Simulated (FRISM)")
plt.title("Distrubtion of HD stop activities by time of day")
plt.legend(loc="upper right")
plt.savefig('../../../FRISM_input_output_{}/Sim_outputs/Val_truck_dist_HD.png'.format(s_region))

plt.figure(figsize = (8,6))
plt.plot(md2b_sim_hour,md2b_sim_trip , color ="blue", alpha = 0.3,)
plt.plot(md2c_sim_hour,md2c_sim_trip , color ="red", alpha = 0.3,)
plt.fill_between(md2b_sim_hour,md2b_sim_trip , color ="blue", label="B2B Simulated (FRISM)", alpha = 0.3,)
plt.fill_between(md2c_sim_hour,md2c_sim_trip , color ="red", label="B2C Simulated (FRISM)", alpha = 0.3,)
plt.title("Distrubtion of MD stop activities  by time of day")
plt.legend(loc="upper right")
plt.savefig('../../../FRISM_input_output_{}/Sim_outputs/Val_truck_dist_MD_by_type.png'.format(s_region))


# plt.figure(figsize = (8,6))
# plt.plot("start_hour", "Trip_rate", data=MD_dpt,color ="blue", label="Observed (INRIX)", alpha = 0.3,)
# plt.plot("start_hour", "Trip_rate", data=MD_dpt_B2BC, color ="red", label="Simulated (FRISM)", alpha = 0.3,)
# plt.title("Distrubtion of MD stop activities  by time of day")
# plt.legend(loc="upper right")
# plt.savefig('../../../FRISM_input_output_SF/Sim_outputs/Val_truck_dist_MD.png')

# plt.figure(figsize = (8,6))
# plt.plot("start_hour", "Trip_rate", data=HD_dpt,color ="blue", label="Observed (INRIX)", alpha = 0.3,)
# plt.plot("start_hour", "Trip_rate", data=HD_dpt_B2B, color ="red", label="Simulated (FRISM)", alpha = 0.3,)
# plt.title("Distrubtion of HD stop activities by time of day")
# plt.legend(loc="upper right")
# plt.savefig('../../../FRISM_input_output_SF/Sim_outputs/Val_truck_dist_HD.png')

# # %% 
# ####################### temp solution adjust time in B2C shifting
# county_list=[1, 13, 41, 55, 75, 81, 85, 95, 97]
# f_dir="../../../FRISM_input_output_SF/Sim_outputs/Tour_plan/"
# v_type= "B2C"
# for county in county_list:
#     df_payload = pd.read_csv(f_dir+"{}_county{}_payload.csv".format(v_type,str(county)))
#     df_tour = pd.read_csv(f_dir+"{}_county{}_freight_tours.csv".format(v_type,str(county)))
#     df_payload["estimatedTimeOfArrivalInSec"] = df_payload["estimatedTimeOfArrivalInSec"].apply(lambda x: x -2.5*3600)
#     df_tour["departureTimeInSec"] =df_tour["departureTimeInSec"].apply(lambda x: x -2.5 *3600)
#     df_payload.to_csv(f_dir+"{}_county{}_payload.csv".format(v_type,str(county)), index = False, header=True)
#     df_tour.to_csv(f_dir+"{}_county{}_freight_tours.csv".format(v_type,str(county)), index = False, header=True)


# %%
'''
Coordinate check if it's properly assigned? 
'''
county_list=[1, 13, 41, 55, 75, 81, 85, 95, 97]
f_dir="../../../FRISM_input_output_SF/Sim_outputs/Tour_plan_inputs/"
for s in ["B2B", "B2C"]:
    for county in county_list:
        df_carr=pd.read_csv(f_dir+"{}_county{}_carrier.csv".format(s,str(county)))
        df_pay=pd.read_csv(f_dir+"{}_county{}_payload.csv".format(s,str(county)))
        df_tour=pd.read_csv(f_dir+"{}_county{}_freight_tours.csv".format(s,str(county)))

        if df_carr[df_carr["depot_zone_x"]<-150.0].shape[0] >0:
            print ("{} carrier county {}".format(s,str(county)))

        if df_pay[df_pay["locationZone_x"]<-150.0].shape[0]>0:
            print ("{} payload county {}".format(s,str(county)))

        if df_tour[df_tour["departureLocation_x"]<-150.0].shape[0]>0:
            print ("{} tour county {}".format(s,str(county)))

# %%
'''
Draw stop ditribution by shipment type
'''

county_list=[1, 13, 41, 55, 75, 81, 85, 95, 97]
f_dir="../../../FRISM_input_output_{}/Sim_outputs/Tour_plan_inputs/".format(s_region)
for s in ["B2B", "B2C"]:
    df_pay_agg= pd.DataFrame()
    for county in county_list:
        df_pay=pd.read_csv(f_dir+"{}_county{}_payload.csv".format(s,str(county)))
        df_pay["end_depot"] = df_pay["payloadId"].apply(lambda x: 1 if x.endswith("_") else 0 )
        df_pay= df_pay[df_pay["end_depot"]==1].reset_index(drop=True)
        df_pay["sequenceRank"]=df_pay["sequenceRank"].apply(lambda x: x-2)
        df_pay_agg=pd.concat([df_pay_agg,df_pay], ignore_index=True).reset_index(drop=True)
    #df_stop_activity=df_pay_agg.groupby(['sequenceRank'])['sequenceRank'].agg(Stops="sum").reset_index()
    plt.figure(figsize = (8,6))
    plt.hist(df_pay_agg['sequenceRank'], color ="blue", density=True, bins=df_pay_agg['sequenceRank'].max(), alpha = 0.5)
    #sns.distplot(df_pay_agg['sequenceRank'], color ="blue", kde=True, bins=df_pay_agg['sequenceRank'].max())
    plt.title("# Stops in a tour for {0} shipments".format(s))
    plt.savefig('../../../FRISM_input_output_{}/Sim_outputs/Stop_hist_for_{}.png'.format(s_region,s))

# %%
## Result data
f_dir="../../../FRISM_input_output_{}/Sim_outputs/Tour_plan/".format(s_region)
#f_dir="../../../Results_from_HPC_v5/Tour_plan/"
# county_list=[1, 13, 41, 55, 75, 81, 85, 95, 97]
county_list=[1]
MD_df_b2c=pd.DataFrame()
MD_df_b2c_sdepot=pd.DataFrame()
v_type= "B2C"
for county in county_list:
    df_payload = pd.read_csv(f_dir+"{}_county{}_payload.csv".format(v_type,str(county)))
    df_payload["end_depot"] = df_payload["payloadId"].apply(lambda x: 1 if x.endswith("_") else 0 )
    df_payload= df_payload[df_payload["end_depot"]==0].reset_index()
    df_payload['start_hour'] = df_payload['estimatedTimeOfArrivalInSec'].apply(lambda x: int(x/3600))
    MD_df_b2c=pd.concat([MD_df_b2c,df_payload], ignore_index=True).reset_index(drop=True)
    df_tour = pd.read_csv(f_dir+"{}_county{}_freight_tours.csv".format(v_type,str(county)))
    df_tour['start_hour'] = df_tour['departureTimeInSec'].apply(lambda x: int(x/3600))
    MD_df_b2c_sdepot=pd.concat([MD_df_b2c_sdepot,df_tour], ignore_index=True).reset_index(drop=True)

MD_df_b2b=pd.DataFrame()
HD_df_b2b=pd.DataFrame()
MD_df_b2b_sdepot=pd.DataFrame()
HD_df_b2b_sdepot=pd.DataFrame()
v_type= "B2B"
for county in county_list:
    df_payload = pd.read_csv(f_dir+"{}_county{}_payload.csv".format(v_type,str(county)))
    df_carr =pd.read_csv(f_dir+"{}_county{}_carrier.csv".format(v_type,str(county)))
    df_payload["end_depot"] = df_payload["payloadId"].apply(lambda x: 1 if x.endswith("_") else 0 )
    df_payload= df_payload[df_payload["end_depot"]==0].reset_index()
    df_payload['start_hour'] = df_payload['estimatedTimeOfArrivalInSec'].apply(lambda x: int(x/3600))
    df_payload['start_hour'] = df_payload['start_hour'].apply(lambda x: x-24 if x >=24 else x)
    df_payload_md = df_payload[df_payload["tourId"].isin(df_carr[df_carr["vehicleTypeId"]==1]["tourId"].unique())]#.reset_index()
    df_payload_hd = df_payload[df_payload["tourId"].isin(df_carr[df_carr["vehicleTypeId"]==2]["tourId"].unique())]#.reset_index()
    MD_df_b2b=pd.concat([MD_df_b2b,df_payload_md], ignore_index=True).reset_index(drop=True)
    HD_df_b2b=pd.concat([HD_df_b2b,df_payload_hd], ignore_index=True).reset_index(drop=True)
    df_tour = pd.read_csv(f_dir+"{}_county{}_freight_tours.csv".format(v_type,str(county)))
    df_tour['start_hour'] = df_tour['departureTimeInSec'].apply(lambda x: int(x/3600))
    df_tour_md = df_tour[df_tour["tour_id"].isin(df_carr[df_carr["vehicleTypeId"]==1]["tourId"].unique())]#.reset_index()
    df_tour_hd = df_tour[df_tour["tour_id"].isin(df_carr[df_carr["vehicleTypeId"]==2]["tourId"].unique())]
    MD_df_b2b_sdepot=pd.concat([MD_df_b2b_sdepot,df_tour_md], ignore_index=True).reset_index(drop=True)
    HD_df_b2b_sdepot=pd.concat([HD_df_b2b_sdepot,df_tour_hd], ignore_index=True).reset_index(drop=True)


MD_df_b2bC = pd.concat([MD_df_b2b,MD_df_b2c], ignore_index=True).reset_index(drop=True)
#MD_df_b2bC = MD_df_b2c
MD_dpt_B2B=  MD_df_b2b.groupby(['start_hour'])['start_hour'].agg(Trip="count").reset_index()
MD_dpt_B2C=  MD_df_b2c.groupby(['start_hour'])['start_hour'].agg(Trip="count").reset_index()
MD_dpt_B2BC=  MD_df_b2bC.groupby(['start_hour'])['start_hour'].agg(Trip="count").reset_index()
HD_dpt_B2B=  HD_df_b2b.groupby(['start_hour'])['start_hour'].agg(Trip="count").reset_index()

MD_dpt_B2B_sdepot=  MD_df_b2b_sdepot.groupby(['start_hour'])['start_hour'].agg(Trip="count").reset_index()
MD_dpt_B2C_sdepot=  MD_df_b2c_sdepot.groupby(['start_hour'])['start_hour'].agg(Trip="count").reset_index()
HD_dpt_B2B_sdepot=  HD_df_b2b_sdepot.groupby(['start_hour'])['start_hour'].agg(Trip="count").reset_index()

MD_dpt_B2B['Trip_rate']=MD_dpt_B2B['Trip']/MD_dpt_B2B['Trip'].sum()
MD_dpt_B2C['Trip_rate']=MD_dpt_B2C['Trip']/MD_dpt_B2C['Trip'].sum()
MD_dpt_B2BC['Trip_rate']=MD_dpt_B2BC['Trip']/MD_dpt_B2BC['Trip'].sum()
HD_dpt_B2B['Trip_rate']=HD_dpt_B2B['Trip']/HD_dpt_B2B['Trip'].sum()

MD_dpt_B2B_sdepot['Trip_rate']=MD_dpt_B2B_sdepot['Trip']/MD_dpt_B2B_sdepot['Trip'].sum()
MD_dpt_B2C_sdepot['Trip_rate']=MD_dpt_B2C_sdepot['Trip']/MD_dpt_B2C_sdepot['Trip'].sum()
HD_dpt_B2B_sdepot['Trip_rate']=HD_dpt_B2B_sdepot['Trip']/HD_dpt_B2B_sdepot['Trip'].sum()

plt.figure(figsize = (8,6))
plt.plot("start_hour", "Trip_rate", data=MD_dpt_B2B,color ="blue", label="all activity", alpha = 0.3,)
plt.plot("start_hour", "Trip_rate", data=MD_dpt_B2B_sdepot, color ="red", label="starting depot", alpha = 0.3,)
plt.title("B2B MD")
plt.legend(loc="upper right")
#plt.savefig('../../../FRISM_input_output_SF/Sim_outputs/Val_truck_dist_MD.png')

plt.figure(figsize = (8,6))
plt.plot("start_hour", "Trip_rate", data=HD_dpt_B2B,color ="blue", label="all activity", alpha = 0.3,)
plt.plot("start_hour", "Trip_rate", data=HD_dpt_B2B_sdepot, color ="red", label="starting depot", alpha = 0.3,)
plt.title("B2B HD")
plt.legend(loc="upper right")
#plt.savefig('../../../FRISM_input_output_SF/Sim_outputs/Val_truck_dist_MD.png')

plt.figure(figsize = (8,6))
plt.plot("start_hour", "Trip_rate", data=MD_dpt_B2C,color ="blue", label="all activity", alpha = 0.3,)
plt.plot("start_hour", "Trip_rate", data=MD_dpt_B2C_sdepot, color ="red", label="starting depot", alpha = 0.3,)
plt.title("B2C MD")
plt.legend(loc="upper right")
plt.savefig('../../../FRISM_input_output_{}/Sim_outputs/Val_truck_dist_MD.png'.format(s_region))

# %%
'''
Check start time distribution
'''
f_dir="../../../FRISM_input_output_{}/Sim_outputs/Shipment2Fleet/".format(s_region)
#f_dir="../../../Results_from_HPC_v5/Tour_plan/"
# county_list=[1, 13, 41, 55, 75, 81, 85, 95, 97]
county=1
#v_type= "B2C" # "B2B"
for v_type in ["B2C", "B2B"]:
    df_carr =pd.read_csv(f_dir+"{}_carrier_county{}_shipall.csv".format(v_type,str(county)))
    df_carr['start_hour'] = df_carr['depot_lower'].apply(lambda x: int(x/60))
    df_carr_dpt=  df_carr.groupby(['start_hour'])['start_hour'].agg(Trip="count").reset_index()

    plt.figure(figsize = (8,6))
    plt.plot("start_hour", "Trip", data=df_carr_dpt, color ="blue", label="all activity", alpha = 0.3,)





# %%
'''
AT travel time skim processing  
'''
travel_file="/Users/kjeong/NREL/1_Work/1_2_SMART_2_0/Model_development/FRISM_input_output_SF/Sim_inputs/Geo_data/tt_df_cbg.csv.gz"
tt_df_sf = pd.read_csv(travel_file, compression='gzip', header=0, sep=',', quotechar='"', error_bad_lines=False)
#travel_file="/Users/kjeong/NREL/1_Work/1_2_SMART_2_0/Model_development/FRISM_input_output_AT/Sim_inputs/Geo_data/austin-skims-res-full-new.csv.gz"
travel_file="/Users/kjeong/NREL/1_Work/1_2_SMART_2_0/Model_development/FRISM_input_output_AT/Sim_inputs/Geo_data/tt_df_cbg.csv.gz"
tt_df_at = pd.read_csv(travel_file, compression='gzip', header=0, sep=',', quotechar='"', error_bad_lines=False)

tt_df_at=tt_df_at[tt_df_at["pathType"]=="SOV"]
tt_df_at=tt_df_at[tt_df_at["timePeriod"].isin(['AM', 'MD', 'PM'])]
new_tt_df= tt_df_at.groupby(["origin", "destination"])['TIME_minutes'].mean().reset_index(name='TIME_minutes')

new_tt_df.to_csv('/Users/kjeong/NREL/1_Work/1_2_SMART_2_0/Model_development/FRISM_input_output_AT/Sim_inputs/Geo_data/tt_df_cbg.csv.gz', compression='gzip')