## Note: To test the codes: In def main(), put for loop is restricted:
### please comment out the followings for the entire run. 
### if args.ship_type == "B2C": ... #for i in range(0,df_hh_D_GrID.shape[0]):
### elif args.ship_type == "B2B": ...#for i in range(0,FH_Seller.shape[0]): 
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
# %%
def create_global_variable(md_max, hd_max, fdir, state,max_tour_for_b2b ):
    global md_max_load
    global hd_max_load
    global fdir_in_out
    global state_id
    global max_tour
    global input_veh_list
    global output_veh_list
    global dic_fuel
    global dic_veh
    md_max_load= md_max
    hd_max_load= hd_max
    fdir_in_out = fdir
    state_id =state
    max_tour=max_tour_for_b2b
    
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
def random_points_in_polygon(polygon):
    temp = polygon.bounds
    finished= False
    while not finished:
        point = Point(random.uniform(temp.minx.values[0], temp.maxx.values[0]), random.uniform(temp.miny, temp.maxy.values[0]))
        finished = polygon.contains(point).values[0]
    return [point.x, point.y]
def sythfirm_fleet_file(fdir,year, scenario):
    dir = fdir+"/Sim_inputs/Synth_firm_pop/"+str(year)+"_"+str(scenario)+"/"
    for filename in os.listdir(dir):
        if "firms" in filename:
            firm_file= filename
        if "carriers" in filename:
            warehouse_file= filename    
        if "leasing" in filename:
            leasing_file= filename       
    stock_file = 'TDA_{}.csv'.format(scenario)
    return firm_file, warehouse_file, leasing_file, stock_file 
# %%    
######################### General CODES ############################
def genral_input_files_processing(firm_file, warehouse_file, leasing_file, stock_file, target_year, scenario, dist_file,CBG_file, ship_type,list_error_zone, county_list):
    global dic_energy

    #list_error_zone=[1047.0, 1959.0, 1979.0, 2824.0, 3801.0, 3897.0, 4303.0, 6252.0, 6810.0, 7273.0, 8857.0, 9702.0]
    # Geo data including distance, CBGzone,
    fdir_geo= fdir_in_out+'/Sim_inputs/Geo_data/'

    dist_df=pd.read_csv(fdir_geo+dist_file, header=0, sep=',')
    dist_df.columns=['Origin','Destination','dist']
    #dist_df.to_csv(fdir_geo+dist_file, index = False, header=True)
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

    fdir_firms=fdir_in_out+'/Sim_inputs/Synth_firm_pop/'+str(target_year)+"_"+str(scenario)+'/'
    if ship_type == 'B2B':
        # firm and warehouse(for-hire carrier)
        firm_file_xy=fdir_firms+firm_file
        if file_exists(firm_file_xy):
            firms=pd.read_csv(firm_file_xy, header=0, sep=',')
            if "BusID" in firms.columns:
                firms=firms.rename({'BusID':'SellerID'}, axis='columns')
            if "lat" in firms.columns:
                firms=firms.rename({'lat':'y', 'lon': 'x'}, axis='columns')
            if "mdt" in firms.columns:
                firms=firms.rename({'mdt':'md_veh', 'hdt':'hd_veh'}, axis='columns')
            if "fleet_id" in firms.columns:
                firms["SellerID"] = firms.apply(lambda x: str(x["SellerID"]) + "_" + str(x["fleet_id"]), axis=1)
        else:
            print ("No firm input file")        

        leasing_file_xy=fdir_firms+leasing_file
        if file_exists(leasing_file_xy):
            leasings=pd.read_csv(leasing_file_xy, header=0, sep=',')
            if "BusID" in leasings.columns:
                leasings=leasings.rename({'BusID':'SellerID'}, axis='columns')
            if "lat" in leasings.columns:
                leasings=leasings.rename({'lat':'y', 'lon': 'x'}, axis='columns')
            if "mdt" in leasings.columns:
                leasings=leasings.rename({'mdt':'md_veh', 'hdt':'hd_veh'}, axis='columns')
            if "fleet_id" in leasings.columns:
                leasings["SellerID"] = leasings.apply(lambda x: str(x["SellerID"]) + "_" + str(x["fleet_id"]), axis=1)    
        else:
            print ("No leasing input file")          
    elif ship_type == 'B2C':
        firms=pd.DataFrame()
        leasings=pd.DataFrame()
    else: 
        print ("Please define shipment type: B2B or B2C")

    wh_file_xy=fdir_firms+warehouse_file
    if file_exists(wh_file_xy):
        warehouses=pd.read_csv(wh_file_xy, header=0, sep=',')
        if "lat" in warehouses.columns:
            warehouses=warehouses.rename({'lat':'y', 'lon': 'x', "Industry_NAICS6_Use": "Industry_NAICS6_Make", 'mdt':'md_veh', 'hdt':'hd_veh'}, axis='columns')
        if "fleet_id" in warehouses.columns:
            warehouses["BusID"] = warehouses.apply(lambda x: str(x["BusID"]) + "_" + str(x["fleet_id"]), axis=1)     

    else:
        print ("**** No warehouse input file")         
    ## Seperate B2B and B2C trucking: Currently use NAICS code for this process; need to update later
    if ship_type == 'B2C':
        truckings=warehouses[warehouses['Industry_NAICS6_Make']==492000].reset_index(drop=True)
        # truckings['md_veh']=truckings['md_veh']+truckings['hd_veh']
        # truckings['hd_veh']=0
        # truckings['md_capacity']=truckings['md_veh'].apply(lambda x: x *md_max_load)
        # truckings['hd_capacity']=truckings['hd_veh'].apply(lambda x: x *hd_max_load)
        # truckings['time_cap'] = truckings.apply(lambda x: (x['md_veh'] + x['hd_veh'])* 60*5, axis=1)        
        truckings['Diesel Class 4-6 Vocational']=truckings['Diesel Class 4-6 Vocational'] \
                                                    + truckings['Diesel Class 7&8 Tractor'] \
                                                    + truckings['Diesel Class 7&8 Vocational'] \
                                                    + truckings['Gasoline Class 4-6 Vocational'] # temporary solution since lack of md in delivery trucking 
        truckings['Electric Class 4-6 Vocational']=truckings['Electric Class 4-6 Vocational'] \
                                                    + truckings['Electric Class 7&8 Tractor'] \
                                                    + truckings['Electric Class 7&8 Vocational'] # temporary solution since lack of md in delivery trucking
        truckings['Diesel Class 7&8 Tractor'] = 0
        truckings['Diesel Class 7&8 Vocational']=0
        truckings['Electric Class 7&8 Tractor'] =0
        truckings['Electric Class 7&8 Vocational'] =0

        truckings['md_capacity']=truckings.apply(lambda x: (x['Diesel Class 4-6 Vocational'] + x['Electric Class 4-6 Vocational'])*md_max_load, axis=1)
        truckings['hdt_capacity']=truckings.apply(lambda x: (x['Diesel Class 7&8 Tractor'] + x['Electric Class 7&8 Tractor']) *hd_max_load, axis=1)
        truckings['hdv_capacity']=truckings.apply(lambda x: (x['Diesel Class 7&8 Vocational'] + x['Electric Class 7&8 Vocational']) *hd_max_load, axis=1)

        truckings['md_time_cap'] = truckings.apply(lambda x: (x['Diesel Class 4-6 Vocational'] +x['Electric Class 4-6 Vocational']) * 60*5, axis=1)
        truckings['hdt_time_cap']=truckings.apply(lambda x: (x['Diesel Class 7&8 Tractor'] + x['Electric Class 7&8 Tractor']) * 60*5, axis=1)
        truckings['hdv_time_cap']=truckings.apply(lambda x: (x['Diesel Class 7&8 Vocational'] + x['Electric Class 7&8 Vocational']) * 60*5, axis=1)
        truckings = truckings.merge(CBGzone_df[['MESOZONE','County']], on='MESOZONE', how='left')
        truckings =truckings[truckings['County'].isin(county_list)].reset_index(drop=True)
        leasings=pd.DataFrame()
                                                                                    
    elif ship_type == 'B2B':
        truckings=warehouses[warehouses['Industry_NAICS6_Make']==484000].reset_index(drop=True)
        #truckings_du=warehouses[warehouses['Industry_NAICS6_Make']==484000].reset_index(drop=True)
        truckings["BusID"]=truckings["BusID"].apply(lambda x: str(x))
        #truckings_du["BusID"]=truckings_du["BusID"].apply(lambda x: str(x)+"d")
        # # temporary for increase cap
        # truckings['md_veh']=truckings['hd_veh'].apply(lambda x: int(x*2))
        # truckings['hd_veh']=truckings['hd_veh'].apply(lambda x: int(x*2))
        # truckings=pd.concat([truckings,truckings_du], ignore_index=True).reset_index(drop=True)
        # #
        # truckings['md_capacity']=truckings['md_veh'].apply(lambda x: x *md_max_load)
        # truckings['hd_capacity']=truckings['hd_veh'].apply(lambda x: x *hd_max_load)
        # truckings['time_cap'] = truckings.apply(lambda x: (x['md_veh'] + x['hd_veh'])* 60*8, axis=1)
        
        #truckings=pd.concat([truckings,truckings_du], ignore_index=True).reset_index(drop=True)
        for veh_type in input_veh_list[:-1]:
            truckings[veh_type]=truckings[veh_type].apply(lambda x: x*3)
        truckings['md_capacity']=truckings.apply(lambda x: (x['Diesel Class 4-6 Vocational'] + x['Electric Class 4-6 Vocational'])*md_max_load, axis=1)
        truckings['hdt_capacity']=truckings.apply(lambda x: (x['Diesel Class 7&8 Tractor'] + x['Electric Class 7&8 Tractor']) *hd_max_load, axis=1)
        truckings['hdv_capacity']=truckings.apply(lambda x: (x['Diesel Class 7&8 Vocational'] + x['Electric Class 7&8 Vocational']) *hd_max_load, axis=1)

        truckings['md_time_cap'] = truckings.apply(lambda x: (x['Diesel Class 4-6 Vocational'] +x['Electric Class 4-6 Vocational']) * 60*8, axis=1)
        truckings['hdt_time_cap']=truckings.apply(lambda x: (x['Diesel Class 7&8 Tractor'] + x['Electric Class 7&8 Tractor']) * 60*8, axis=1)
        truckings['hdv_time_cap']=truckings.apply(lambda x: (x['Diesel Class 7&8 Vocational'] + x['Electric Class 7&8 Vocational']) * 60*8, axis=1)

        truckings = truckings.merge(CBGzone_df[['MESOZONE','County']], on='MESOZONE', how='left')
        # leasing process
        leasings_D= leasings.groupby(['st']).agg(md=("Diesel Class 4-6 Vocational",'sum'),
                                                hdv=("Diesel Class 7&8 Tractor",'sum'),
                                                hdt=("Diesel Class 7&8 Vocational",'sum') 
                                                    ).reset_index()
        leasings_D["powertrain"]="Diesel"                                            
        leasings_E= leasings.groupby(['st', 'EV_powertrain (if any)']).agg(md=("Electric Class 4-6 Vocational",'sum'),
                                                hdv=("Electric Class 7&8 Tractor",'sum'),
                                                hdt=("Electric Class 7&8 Vocational",'sum') 
                                                    ).reset_index()
        leasings_E=leasings_E.rename({'EV_powertrain (if any)':'powertrain'}, axis='columns')
        leasings= pd.concat([leasings_D,leasings_E], ignore_index=True).reset_index(drop=True)           
    else:
        print ("Please define shipment type: B2B or B2C")
    
    
    # externalZone
    ex_zone_file_xy = fdir_geo+"xy"+"External_Zones_Mapping.csv"
    if file_exists(ex_zone_file_xy):
        ex_zone=pd.read_csv(ex_zone_file_xy, header=0, sep=',')
    else:
        print ("**** Generating x_y to ex_zone files")
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
        ex_zone=ex_zone[~ex_zone['BoundaryZONE'].isin(list_error_zone)]
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
        ex_zone.to_csv(ex_zone_file_xy, index = False, header=True)
    ex_zone_list=list(ex_zone["MESOZONE"].unique())

    # Truck activity distribution
    fdir_truck=fdir_in_out+'/Model_carrier_op/INRIX_processing/'
    if ship_type == 'B2C':
        df_dpt_dist=pd.read_csv(fdir_truck+'depature_dist_by_cbg_MD.csv', header=0, sep=',')
    elif ship_type == 'B2B':
        df_dpt_dist=pd.read_csv(fdir_truck+'depature_dist_by_cbg_HD.csv', header=0, sep=',')
    else:
        print ("Please define shipment type: B2B or B2C")
    df_dpt_dist=df_dpt_dist.merge(CBGzone_df[["GEOID",'MESOZONE']], left_on="cbg_id", right_on="GEOID", how='left')    




    fdir_truck=fdir_in_out+'/Sim_inputs/Synth_firm_pop/'
    stocks=pd.read_csv(fdir_truck+stock_file, header=0, sep=',')
    stocks["Class"]=stocks["Class"].str.replace(" Sleeper ", " ")
    stocks["Class"]=stocks["Class"].str.replace(" Day Cab ", " ")

    dic_energy={dic_veh[veh_classs]: {veh_fuel: 1 for veh_fuel in dic_fuel.keys()}  for veh_classs in dic_veh.keys()}
    for veh_class in dic_veh.keys():
        for veh_fuel in dic_fuel.keys():
            if veh_fuel == "PHEV":
                temp_veh_fuel= veh_fuel+" Diesel"
            else:
                temp_veh_fuel= veh_fuel

            temp= stocks[(stocks["Year"] == target_year) &
                (stocks["Powertrain"].str.contains(temp_veh_fuel)) &
                (stocks["Class"].str.contains(dic_veh[veh_class])) & 
                (stocks["mpgge"] >1)]
            mpg= temp["mpgge"].mean()
            if pd.isna(mpg):
                dic_energy[dic_veh[veh_class]][veh_fuel]= 0.1
            else: 
                dic_energy[dic_veh[veh_class]][veh_fuel]= mpg
    return firms, truckings, leasings, dist_df, CBGzone_df, df_dpt_dist, ex_zone_list, ex_zone       

f_dir="../../../Results_veh_tech_v2/"
year_list=[2050]
s_list=["HOP_highp2", "HOP_highp4", "HOP_highp6","HOP_highp8","HOP_highp10",
 "Ref_highp2", "Ref_highp4", "Ref_highp6","Ref_highp8","Ref_highp10"]
#s_list=["Ref_highp2"]
#s_list=["Ref_highp4", "Ref_highp6","Ref_highp8","Ref_highp10"]
county_list=[453, 491, 209, 55, 21, 53]
for y in year_list:
    for s in s_list:
        firm_file, warehouse_file, leasing_file, stock_file =sythfirm_fleet_file(config.fdir_in_out,y, s)
        create_global_variable(config.md_cap,config.hd_cap,config.fdir_in_out ,config.state_id,config.max_tour_for_b2b)
        firms, truckings,leasings, dist_df, CBGzone_df, df_dpt_dist, ex_zone_list, ex_zone= genral_input_files_processing(firm_file,
                                                                                        warehouse_file,
                                                                                        leasing_file,
                                                                                        stock_file,
                                                                                        y,
                                                                                        s, 
                                                                                        config.dist_file,
                                                                                        config.CBG_file, 
                                                                                        "B2B",
                                                                                        config.list_error_zone, 
                                                                                        config.county_list)
        for c in county_list:
            payloads=  pd.read_csv(f_dir+"Tour_plan/{0}/B2B_county{1}_payload_s{2}_y{3}.csv".format(y,c,s,y))
            for i in range(payloads.shape[0]):
                if payloads["locationZone_x"].iloc[i]==0:
                    zone_id=payloads["locationZone"].iloc[i]
                    [[a,b]]=firms[firms.MESOZONE==zone_id].sample(n=1)[['x','y']].values.tolist()
                    payloads["locationZone_x"].iloc[i]=a
                    payloads["locationZone_y"].iloc[i]=b
            payloads.to_csv(f_dir+"Tour_plan/{0}/B2B_county{1}_payload_s{2}_y{3}.csv".format(y,c,s,y), index = False, header=True)