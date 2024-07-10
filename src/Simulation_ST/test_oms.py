# %%
import pandas as pd
import openmatrix as omx
# %%
file_dict="../../../Data/"

filename = 'skims.omx'

myfile = omx.open_file(file_dict+filename)
t_name=myfile.list_matrices()

df=pd.DataFrame(t_name)
df.to_csv(file_dict+"table_list.csv")
t_time=myfile['SOV_TIME__AM']
t_dist=myfile['DIST']

# t_time.attrs
# myfile.list_all_attributes()
'''
/data/DRV_COM_WLK_DTIM__AM._v_attrs (AttributeSet), 6 attributes:
   [CLASS := 'CARRAY',
    TITLE := '',
    VERSION := '1.1',
    measure := 'DTIM',
    mode := 'DRV_COM_WLK',
    timePeriod := 'AM']
'''

myfile.list_mappings() # ['zone_id']

zone_id = myfile.mapping('zone_id')  
# %%
# t_dist[zone_id[100]][zone_id[101]]

# t_time[zone_id[100]][zone_id[101]]

'''
Unit of time? min
Dist? Mile

zone_id ? 
Which table?
EA? 

'''
import geopandas as gpd
filename="block_groups_seattle.geojson"
lookup = gpd.read_file(file_dict+filename)

column_names= ["origin","destination","TIME_minutes", "beam_dist_mile"]
tt_df= pd.DataFrame(columns=column_names)
n=0
for orig in zone_id.keys():
    for dest in zone_id.keys():
        temp_df = {"origin": lookup[lookup["OBJECTID"]==orig]["geoid_nm"].values[0] ,
                   "destination": lookup[lookup["OBJECTID"]==dest]["geoid_nm"].values[0],
                   "TIME_minutes": t_time[zone_id[orig]][zone_id[dest]],
                   "beam_dist_mile":  t_dist[zone_id[orig]][zone_id[dest]]
                   }
        tt_df.loc[n]=temp_df
        n=n+1
tt_df.to_csv("../../../FRISM_input_output_ST/Sim_inputs/Geo_data/tt_df_cbg.csv.gz", compression="gzip", index=False)
    
# %%
import geopandas as gpd

df_tomtom = gpd.read_file("/Users/kjeong/KJ_NREL_Work/1_Work/1_5_Xtelligent/Work_folder/Data/Tomtom/jobs_4212275_results_Great_long_beach.geojson")
df_tomtom.head()
df_tomtom.segmentTimeResults
df_tomtom.userPreference[0]
df_tomtom.dateRanges[0]
time_set=df_tomtom.timeSets[0]

# %%
tt_df = pd.read_csv("../../../FRISM_input_output_ST/Sim_inputs/Geo_data/tt_df_cbg.csv.gz", compression='gzip', header=0, sep=',', quotechar='"', on_bad_lines='skip')

tt_df_at = pd.read_csv("../../../FRISM_input_output_AT/Sim_inputs/Geo_data/tt_df_cbg.csv.gz", compression='gzip', header=0, sep=',', quotechar='"', on_bad_lines='skip')

# %%

import geopandas as gpd
fdir_in_out= "../../../FRISM_input_output_ST"
fdir_geo= fdir_in_out+'/Sim_inputs/Geo_data/'
CBG_file= 'Seattle_freight.geojson'
state_id =53

CBGzone_df = gpd.read_file(fdir_geo+CBG_file) # file include, GEOID(12digit), MESOZONE, area
CBGzone_df= CBGzone_df.to_crs({'proj': 'cea'})
CBGzone_df["area"]=CBGzone_df['geometry'].area/(10**6)
CBGzone_df["GEOID"]=CBGzone_df["GEOID"].astype(str)
## Add county id from GEOID
CBGzone_df["County"]=CBGzone_df["GEOID"].apply(lambda x: x[2:5] if (len(x)>=12 and x[0:2]==str(state_id))  else 0)
CBGzone_df["County"]=CBGzone_df["County"].astype(str).astype(int)
CBGzone_df["GEOID"]=CBGzone_df["GEOID"].astype(str).astype(int)
CBGzone_df= CBGzone_df.to_crs('EPSG:4269')

test=CBGzone_df[CBGzone_df["County"]>0]