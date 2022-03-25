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

# %%
parser = ArgumentParser()
parser.add_argument("-st", "--shipment type", dest="ship_type",
                    help="B2B or B2C", required=True, type=str)
args = parser.parse_args()

# %%
county_list=[1, 13, 41, 55, 75, 81, 85, 95, 97]
sf_map = plt.imread('../../../FRISM_input_output/Sim_inputs/Geo_data/SF_map.png')
BBox= (-123.655,-121.524,36.869,38.852)

# %%
ship_type=args.ship_type
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

################################################################################################################
# %%

study_region="AT"
web_obs=pd.read_csv('../../../FRISM_input_output_{}/Sim_outputs/Generation/{}_webuse_by_income_observed.csv'.format(study_region,study_region))
online_bi_obs=pd.read_csv('../../../FRISM_input_output_{}/Sim_outputs/Generation/{}_online_by_income_observed.csv'.format(study_region,study_region))

df_hh_obs=pd.read_csv('../../../FRISM_input_output_{}/Model_inputs/NHTS/{}_hh.csv'.format(study_region,study_region))
df_per_obs=pd.read_csv('../../../FRISM_input_output_{}/Model_inputs/NHTS/{}_per.csv'.format(study_region,study_region))
df_per_obs_hh=df_per_obs.groupby(['HOUSEID'])['DELIVER'].agg(delivery_f='sum').reset_index()
df_hh_obs=df_hh_obs.merge(df_per_obs_hh, on='HOUSEID', how='left')

df_hh_model=pd.read_csv('../../../FRISM_input_output_{}/Sim_outputs/Generation/households_del.csv'.format(study_region))

# %%
df_hh_obs['delivery_f'] =df_hh_obs['delivery_f'].apply(lambda x: 0 if np.isnan(x) else int(x))
df_hh_model['delivery_f'] =df_hh_model['delivery_f'].apply(lambda x: 1 if np.isnan(x) else int(x))

# %%
list_income=["income_cls_0","income_cls_1","income_cls_2","income_cls_3"]
dic_income={"income_cls_0": "income <$35k",
            "income_cls_1": "income $35k-$75k",
            "income_cls_2": "income $75k-125k",
            "income_cls_3": "income >$125k"}
     
for ic_nm in list_income:
    plt.figure(figsize = (8,6))
    plt.hist(df_hh_obs[df_hh_obs[ic_nm]==1]['delivery_f'], color ="blue", density=True, bins=30, alpha = 0.3, label="observed")
    plt.hist(df_hh_model[(df_hh_model[ic_nm]==1) & (df_hh_model['delivery_f']<=30)]['delivery_f'], color ="red", density=True, bins=30, alpha = 0.3, label="modeled")
    plt.title("Density of Delivery Frequency in {0}, {1}".format(dic_income[ic_nm], study_region))
    plt.legend(loc="upper right")
    plt.savefig('../../../FRISM_input_output_{0}/Sim_outputs/Generation/B2C_delivery_val_{1}.png'.format(study_region, ic_nm))


################################################################################################################    
# %%

fdir_truck='../../../FRISM_input_output/Model_carrier_op/INRIX_processing/'
df_dpt_dist_MD=pd.read_csv(fdir_truck+'depature_dist_by_cbg_MD.csv', header=0, sep=',')
df_dpt_dist_HD=pd.read_csv(fdir_truck+'depature_dist_by_cbg_HD.csv', header=0, sep=',')

fdir_geo='../../../FRISM_input_output/Sim_inputs/Geo_data/'
CBGzone_df = gpd.read_file(fdir_geo+'freight_centroids.geojson')
CBGzone_df.GEOID=CBGzone_df.GEOID.astype(str).astype(int)
df_dpt_dist_MD=df_dpt_dist_MD.merge(CBGzone_df[["GEOID",'MESOZONE']], left_on="cbg_id", right_on="GEOID", how='left')
df_dpt_dist_HD=df_dpt_dist_HD.merge(CBGzone_df[["GEOID",'MESOZONE']], left_on="cbg_id", right_on="GEOID", how='left')
sel_zone= pd.read_csv(fdir_geo+'selected zone.csv')
sel_zone=sel_zone.rename({'blkgrpid':'GEOID'}, axis=1)
sel_zone = sel_zone.merge(CBGzone_df[['GEOID','MESOZONE']], on='GEOID', how='left')

df_dpt_dist_MD=df_dpt_dist_MD[df_dpt_dist_MD['MESOZONE'].isin(sel_zone['MESOZONE'])].reset_index()
df_dpt_dist_HD=df_dpt_dist_HD[df_dpt_dist_HD['MESOZONE'].isin(sel_zone['MESOZONE'])].reset_index()

MD_dpt= df_dpt_dist_MD.groupby(['start_hour'])['Trip'].sum()
MD_dpt=MD_dpt.to_frame()
MD_dpt.reset_index(level=(0), inplace=True)
MD_dpt['Trip_rate']=MD_dpt['Trip']/MD_dpt['Trip'].sum()

HD_dpt= df_dpt_dist_HD.groupby(['start_hour'])['Trip'].sum()
HD_dpt=HD_dpt.to_frame()
HD_dpt.reset_index(level=(0), inplace=True)
HD_dpt['Trip_rate']=HD_dpt['Trip']/HD_dpt['Trip'].sum()

plt.figure(figsize = (8,6))
plt.plot("start_hour", "Trip", data=MD_dpt,color ="blue", label="MD")
plt.plot("start_hour", "Trip", data=HD_dpt, color ="red", label="HD")
plt.title("Distrubtion of stop activities  by time of day (INRIX)")
plt.legend(loc="upper right")
plt.savefig('../../../FRISM_input_output/Sim_outputs/INRIX_truck_dist.png')
# %%
