        
# %%
import geopandas as gpd
import pandas as pd
# %%

IN_DIR = "../../../FRISM_input_output_BO/CTPS_Data/zoning/"
OUT_DIR = "../../../FRISM_input_output_BO/Sim_inputs/Geo_data/"
ctps_taz = gpd.read_file(IN_DIR+ "CTPS_TDM23_TAZ_2017g_v202303.shp")
ctps_taz = ctps_taz.rename(columns={'taz_id': 'taz'})
ctps_taz= ctps_taz.to_crs('EPSG:4269') 
ctps_taz_internal=ctps_taz[ctps_taz["type"]=="I"].reset_index()
ctps_taz_external=ctps_taz[ctps_taz["type"]=="E"].reset_index()    
ctps_taz_internal.to_file(OUT_DIR+"CTPS_TAZ_2023.geojson", driver="GeoJSON")
# 2. Copy the layer to preserve the original structure
points_gdf = ctps_taz_external.copy()

# 3. Calculate and reassign the geometry to centroids
points_gdf["geometry"] = points_gdf.geometry.centroid
# %%
points_gdf= points_gdf[["taz","geometry"]]
list_active_external_point= [209003,
209004,
209010,
209030,
209046,
209069,
209082,
209089,
209099]

points_gdf=points_gdf[points_gdf["taz"].isin(list_active_external_point)]
points_gdf.to_file(OUT_DIR+"CTPS_TAZ_Active_External_2023.geojson", driver="GeoJSON")



# %%
def countyid_from_cbgid (cbgid):
    cbgid_str = str(int(cbgid))
    if (len(cbgid_str)==12):
        return int(cbgid_str[0:5])
    elif (len(cbgid_str)==11):
        return int(cbgid_str[1:4])
    else:
        return 0
# %%
# read the zone file from original 
file_path="../../../FRISM_input_output_BO/Sim_inputs/Geo_data/Boston_freight.geojson"  
zone = gpd.read_file(file_path) 
zone= zone.to_crs({'proj': 'cea'})
zone["County"]=zone["GEOID"].apply(lambda x: countyid_from_cbgid (x))
zone= zone.to_crs('EPSG:4269')    
county_in_region=[25001,25003,25005,25007,25009,25011, 25013, 25015,25017, 25019,
                    25021,25023, 25025,25027,33015,33011, 44001, 44003,44005,44007,44009]
external_zone=zone[~zone["County"].isin(county_in_region)][['MESOZONE','geometry']].reset_index(drop=True)
external_zone["BoundaryZONE"]=0
in_zones= points_gdf
# %%
for index, row in external_zone.iterrows():
    D = 999999
    Id = None 
    p = row['geometry'].centroid
    for i,z in enumerate(in_zones['geometry']):
        distance = p.distance(z)
        ID = int(in_zones.iloc[i]['taz'])
        if distance <= D:
            D = distance
            Id = ID
    external_zone.at[index, "BoundaryZONE"] =Id

external_zone=external_zone[['MESOZONE', "BoundaryZONE"]]

group_external_zone = {209003:1,
209004:1,
209010:2,
209030:2,
209046:3,
209069:4,
209082:4,
209089:4,
209099:4}

external_zone["Boundary_group"]=external_zone["BoundaryZONE"].apply(lambda x: group_external_zone[x])
external_zone[['MESOZONE', "BoundaryZONE","Boundary_group"]].to_csv("../../../FRISM_input_output_BO/Sim_inputs/Geo_data/brmpo_external.csv")
# %%
