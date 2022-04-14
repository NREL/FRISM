
# %%
import pandas as pd
import numpy as np
import geopandas as gpd
from argparse import ArgumentParser
import random
import config
import glob
from os.path import exists as file_exists
from alive_progress import alive_bar
import time
from shapely.geometry import Point
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
# %%
def random_points_in_polygon(polygon):
    temp = polygon.bounds
    finished= False
    while not finished:
        point = Point(random.uniform(temp.minx.values[0], temp.maxx.values[0]), random.uniform(temp.miny, temp.maxy.values[0]))
        finished = polygon.contains(point).values[0]
    return [point.x, point.y]

# %%
county_list=[1, 13, 41, 55, 75, 81, 85, 95, 97]
for county in  county_list:
    print ("processing loctaion allocation for {}county".format(county))
    payload_df=pd.read_csv(fdir_in_out+"/Sim_outputs/Tour_plan/"+"B2C_county{}_payload_xy.csv".format(county))

    print ("**xy allocation job size:", payload_df.shape[0])

    with alive_bar(payload_df.shape[0], force_tty=True) as bar:
        for i in range(0,payload_df.shape[0]):
            if str(county)+"_dB2C" in payload_df.loc[i,'payloadId']:
                continue
            else:      
                [x,y]=random_points_in_polygon(CBGzone_df.geometry[CBGzone_df.MESOZONE==payload_df.loc[i,"locationZone"]])
                payload_df.loc[i,'locationZone_x']=x
                payload_df.loc[i,'locationZone_y']=y
                bar()
    payload_df.to_csv(fdir_in_out+"/Sim_outputs/Tour_plan/"+"B2C_county{}_payload_xy.csv".format(county), index = False, header=True)

print ("complete the job")
# %%
