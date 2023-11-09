
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
def create_global_variable(md_max, hd_max, fdir, state,max_tour_for_b2b,sample_ratio_input):
    global md_max_load
    global hd_max_load
    global fdir_in_out
    global state_id
    global max_tour
    global input_veh_list
    global output_veh_list
    global dic_fuel
    global dic_veh
    global sample_ratio
    global bin_size
    md_max_load= md_max
    hd_max_load= hd_max
    fdir_in_out = fdir
    state_id =state
    max_tour=max_tour_for_b2b
    bin_size=10
    sample_ratio=sample_ratio_input
    
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
# %%    
######################### General CODES ############################
def genral_input_files_processing(firm_file, warehouse_file, leasing_file, stock_file, target_year, scenario, dist_file,CBG_file, ship_type,list_error_zone, county_list):
    global dic_energy
    # Geo data including distance, CBGzone,
    fdir_geo= fdir_in_out+'/Sim_inputs/Geo_data/'

    dist_df=pd.read_csv(fdir_geo+dist_file, header=0, sep=',')
    dist_df.columns=['Origin','Destination','dist']

    CBGzone_df = gpd.read_file(fdir_geo+CBG_file) # file include, GEOID(12digit), MESOZONE, area
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
        warehouses = warehouses.merge(CBGzone_df[['MESOZONE','County']], on='MESOZONE', how='left')       

    else:
        print ("**** No warehouse input file")         
    if ship_type == 'B2C':
        truckings=warehouses[warehouses['Industry_NAICS6_Make']==492000].reset_index(drop=True)
        truckings =truckings[truckings['County'].isin(county_list)].reset_index(drop=True)
        if sample_ratio <100:
           truckings = sampling_carrier(truckings, sample_ratio, bin_size)     
     
        truckings['Diesel Class 4-6 Vocational']=truckings['Diesel Class 4-6 Vocational'] \
                                                    + truckings['Diesel Class 7&8 Tractor'] \
                                                    + truckings['Diesel Class 7&8 Vocational'] \
                                                    + truckings['Gasoline Class 4-6 Vocational'] 
        truckings['Electric Class 4-6 Vocational']=truckings['Electric Class 4-6 Vocational'] \
                                                    + truckings['Electric Class 7&8 Tractor'] \
                                                    + truckings['Electric Class 7&8 Vocational'] 
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
        
        leasings=pd.DataFrame()
                                                                                    
    elif ship_type == 'B2B':
        truckings=warehouses[warehouses['Industry_NAICS6_Make']==484000].reset_index(drop=True)
        truckings["BusID"]=truckings["BusID"].apply(lambda x: str(x))
        truckings_with =truckings[truckings['County'].isin(county_list)].reset_index(drop=True)
        truckings_out =truckings[~truckings['County'].isin(county_list)].reset_index(drop=True)
        if sample_ratio <100:
           truckings_with = sampling_carrier(truckings_with, sample_ratio, bin_size) 
        truckings=pd.concat([truckings_with,truckings_out], ignore_index=True).reset_index(drop=True)

        for veh_type in input_veh_list[:-1]:
            truckings[veh_type]=truckings[veh_type].apply(lambda x: x*3)
        truckings['md_capacity']=truckings.apply(lambda x: (x['Diesel Class 4-6 Vocational'] + x['Electric Class 4-6 Vocational'])*md_max_load, axis=1)
        truckings['hdt_capacity']=truckings.apply(lambda x: (x['Diesel Class 7&8 Tractor'] + x['Electric Class 7&8 Tractor']) *hd_max_load, axis=1)
        truckings['hdv_capacity']=truckings.apply(lambda x: (x['Diesel Class 7&8 Vocational'] + x['Electric Class 7&8 Vocational']) *hd_max_load, axis=1)

        truckings['md_time_cap'] = truckings.apply(lambda x: (x['Diesel Class 4-6 Vocational'] +x['Electric Class 4-6 Vocational']) * 60*8, axis=1)
        truckings['hdt_time_cap']=truckings.apply(lambda x: (x['Diesel Class 7&8 Tractor'] + x['Electric Class 7&8 Tractor']) * 60*8, axis=1)
        truckings['hdv_time_cap']=truckings.apply(lambda x: (x['Diesel Class 7&8 Vocational'] + x['Electric Class 7&8 Vocational']) * 60*8, axis=1)

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
            elif veh_fuel == "Diesel" :
                temp_veh_fuel= veh_fuel+" CI"
            else:    
                temp_veh_fuel= veh_fuel

            temp= stocks[(stocks["Year"] == target_year) &
                (stocks["Powertrain"].str.contains(temp_veh_fuel)) &
                (stocks["Class"].str.contains(dic_veh[veh_class])) & 
                (stocks["mpgge"] >1) & 
                (stocks["Stock"] >0)]
            try: 
                temp['w_mpgge']= temp.apply(lambda x: x["mpgge"]*x["Stock"], axis=1)
                mpg= temp["w_mpgge"].sum()/temp["Stock"].sum()
            except:
                mpg=0.1    
            if pd.isna(mpg):
                dic_energy[dic_veh[veh_class]][veh_fuel]= 0.1
            else: 
                dic_energy[dic_veh[veh_class]][veh_fuel]= mpg   
    return firms, truckings, leasings, dist_df, CBGzone_df, df_dpt_dist, ex_zone_list, ex_zone       

###  Calculate distance between two meso zone: currenlty Euclidian dist
#####  Update requried: Need to get network distance? -> please update "dist_df=pd.read_csv(...)"" 
# 
def sampling_carrier(temp, sample_ratio, bin_size):
    temp_1=temp
    total_size=temp_1.shape[0]
    if (total_size*sample_ratio)/(100) < bin_size:
        bin_size = int((total_size*sample_ratio)/(100))
    try:    
        temp_1["binned_volume"] =pd.qcut(temp_1['n_trucks'], q=bin_size, labels=False)
    except:
        temp_1["binned_volume"]=temp_1['n_trucks'].apply(lambda x:lable_creater(x))
    list_bin_labels = temp_1["binned_volume"].unique().tolist()
    list_shipper_sample=[]
    for bin_id in list_bin_labels:
        temp_2=temp_1[(temp_1['binned_volume']==bin_id)]
        list_shipper = temp_2['BusID'].unique().tolist()
        if (len(list_shipper)*sample_ratio/100 >0) & (len(list_shipper)*sample_ratio/100 <0.5):
            list_shipper= random.sample(list_shipper, int(len(list_shipper)*sample_ratio/100+0.5))
            list_shipper_sample=list_shipper_sample+list_shipper
        elif (len(list_shipper)*sample_ratio/100 >=0.5):     
            list_shipper= random.sample(list_shipper, int(len(list_shipper)*sample_ratio/100+0.5))
            list_shipper_sample=list_shipper_sample+list_shipper             
    df_sample=temp[temp["BusID"].isin(list_shipper_sample)].reset_index(drop=True)

    return df_sample 

def lable_creater(value):
    if value <=1:
        return 0
    elif value>1 and value<4:
        return 1
    elif value >=4 and value <8:
        return 2
    elif value >=8 and value <16:
        return 3    
    elif value >=16 and value <64:
        return 4 
    elif value >=64 and value <128:
        return 5
    elif value >=128 and value <256:
        return 6
    elif value >=256:
        return 7  

def dist_cal(org_meso, dest_meso, dist_df):
    dist = dist_df[(dist_df['Origin']==org_meso) & (dist_df['Destination']==dest_meso)].dist.values[0]
    if (dist == 0):
        dist =random.uniform(1,10)
    return dist

def carrier_sel(SellerZone, D_truckload, tt_time, cap_index, time_index, dist_df, truckings, ship_type, sctg):

    if ship_type=="B2B":
        col_name="SCTG"+str(sctg)
        truckings =truckings[truckings[col_name]==1]

    sel_dist_df = dist_df[(dist_df.Origin==SellerZone) & (dist_df.dist<25)]
    candidate_busid= truckings[(truckings['MESOZONE'].isin(sel_dist_df.Destination.unique())) &
                               (truckings[cap_index] >=D_truckload) &  
                               (truckings[time_index] >=tt_time)][['BusID','MESOZONE']] 
    
    if (candidate_busid.shape[0]  < 5):
        sel_dist_df = dist_df[(dist_df.Origin==SellerZone) & (dist_df.dist<50)]
        candidate_busid= truckings[(truckings['MESOZONE'].isin(sel_dist_df.Destination.unique())) &
                               (truckings[cap_index] >=D_truckload) &  
                               (truckings[time_index] >=tt_time)][['BusID','MESOZONE']] 
    if (candidate_busid.shape[0]  < 5):
        sel_dist_df = dist_df[(dist_df.Origin==SellerZone) & (dist_df.dist<100)]
        candidate_busid= truckings[(truckings['MESOZONE'].isin(sel_dist_df.Destination.unique())) & 
                               (truckings[cap_index] >=D_truckload) &  
                               (truckings[time_index] >=tt_time)][['BusID','MESOZONE']]
    if (candidate_busid.shape[0]  < 5):
        sel_dist_df = dist_df[(dist_df.Origin==SellerZone) & (dist_df.dist<200)]
        candidate_busid= truckings[(truckings['MESOZONE'].isin(sel_dist_df.Destination.unique())) & 
                                (truckings[cap_index] >=D_truckload) &  
                                (truckings[time_index] >=tt_time)][['BusID','MESOZONE']]
    if (candidate_busid.shape[0]  < 5):
        sel_dist_df = dist_df[(dist_df.Origin==SellerZone) & (dist_df.dist<300)]
        candidate_busid= truckings[(truckings['MESOZONE'].isin(sel_dist_df.Destination.unique())) & 
                                (truckings[cap_index] >=D_truckload) &  
                                (truckings[time_index] >=tt_time)][['BusID','MESOZONE']]                                                         
    try: 
        if candidate_busid.shape[0] >=5: 
            candidate_busid=candidate_busid.sample(5)
  
        candidate_busid["org_CBG"]=SellerZone
        candidate_busid= candidate_busid.reset_index(drop=True)

        candidate_busid['ttime']=candidate_busid.apply(lambda x: dist_cal(x['org_CBG'], x['MESOZONE'], dist_df), axis=1)
        candidate_busid['inv_sqr_tt']=candidate_busid.apply(lambda x: 1/x['ttime'], axis=1)
        sum_pro=np.sum(candidate_busid['inv_sqr_tt'])
        candidate_busid['prob']=candidate_busid.apply(lambda x: x['inv_sqr_tt']/sum_pro, axis=1)
        candidate_busid['cum_prob_ub']=candidate_busid['prob'].cumsum()
        candidate_busid['cum_prob_lb']=np.nan_to_num(candidate_busid['cum_prob_ub'].shift())
        candidate_busid.loc[candidate_busid.shape[0],'cum_prob_ub'] = 1.0001
        r_num = random.uniform(0,1)
        sel_busID=candidate_busid[(candidate_busid['cum_prob_ub'] > r_num) & (candidate_busid['cum_prob_lb'] <= r_num)].BusID.values[0]
    except:
        sel_busID ="no"
    return sel_busID

def depot_time_depart(zone_id,df_dpt_dist,ship_type):
    if ship_type == 'B2C':     

        if random.uniform(0, 1) <= 0.65:
            d_time =time_normal(8, 2, 5, 12)
        else:     
            d_time =time_normal(13, 2, 10, 16)
    elif ship_type == 'B2B':
        if random.uniform(0, 1) <= 0.5:
            d_time =time_normal(7, 2, 3, 12)
        else:     
            d_time =time_normal(13, 3, 9, 16)
    else:
        print ("Please define shipment type: B2B or B2C")        
    return d_time   

def depot_time_close(d_time):
    c_time = d_time+10*60
    if c_time >=23*60: 
        c_time = 23*60
    elif c_time <= 15*60:
        c_time= random.randrange(15*60, 20*60, 20)
    else:     
        c_time=c_time
    return c_time

def random_points_in_polygon(polygon):
    temp = polygon.bounds
    finished= False
    while not finished:
        point = Point(random.uniform(temp.minx.values[0], temp.maxx.values[0]), random.uniform(temp.miny.values[0], temp.maxy.values[0]))
        finished = polygon.contains(point).values[0]
    return [point.x, point.y]

def time_normal(mean, std, min_time,max_time):
    time = (np.random.normal(0,std)+mean)*60
    if time < min_time*60 or time > max_time*60 :
        time= random.randrange((mean)*60,max_time*60, 10)
    return int(time)        

def veh_type_create():
    vehicle_types= pd.DataFrame()

    for veh_class in dic_veh.keys():
        for veh_fuel in dic_fuel.keys():
            if veh_fuel == "Diesel":
                mid_fuel="D"
            else:
                mid_fuel="E"

            if veh_class=="md":
                max_load= md_max_load
                veh_weight=10000
                speed=80
            else: 
                max_load= hd_max_load
                veh_weight=15000
                speed=65     
            
            temp= pd.DataFrame(data={'veh_type_id': [veh_class+"_"+mid_fuel+"_"+veh_fuel],
                                'veh_category': [veh_fuel+" "+dic_veh[veh_class]],
                                'veh_class':[dic_veh[veh_class]],
                                'body_type':['NA'],
                                'commodities':[[1,2,3,4,5]],
                                'weight':[veh_weight], 
                                'length':['NA'],
                                'payload_capacity_weight':[max_load],
                                'payload_capacity_cbf':['NA'],
                                'max_speed(mph)':[speed],
                                'primary_fuel_type':[dic_fuel[veh_fuel]],
                                'secondary_fuel_type':['NA'],
                                'primary_fuel_rate':[dic_energy[dic_veh[veh_class]][veh_fuel]],
                                'secondary_fuel_rate':['NA'],
                                'Automation level':['NA'],
                                'monetary cost':['NA']})
            vehicle_types=pd.concat([vehicle_types,temp], ignore_index=True).reset_index(drop=True)                       

    return vehicle_types

def util_powertrain(num_D, num_E, dic_E, distance,veh_class, ev_class, coef_num_D): # coef_num_D: 0~1
    if distance ==0:
        distance =10
    u_D= coef_num_D*num_D*math.exp(1/((1/dic_E[veh_class]["Diesel"])*distance))
    u_E= num_E*math.exp(1/((1/dic_E[veh_class][ev_class])*(distance+int(distance/350)*250)))
    pro_D = u_D/(u_D+u_E)
    prob_gen = random.uniform(0,1)
    if prob_gen < pro_D:
        powerT = "D"
    else:
        powerT = "E"        
    return powerT
###################################################################

########################### B2C CODES #############################
def b2c_input_files_processing(CBGzone_df, possilbe_delivey_days, sel_county, list_error_zone,growth_factor, year):
    # read household delivery file from 
    df_hh = pd.read_csv(fdir_in_out+'/Sim_outputs/Generation/households_del_{}.csv'.format(str(year)), header=0, sep=',')
    df_hh= df_hh[['household_id','delivery_f', 'block_id']]
    df_hh['GEOID'] =df_hh['block_id'].apply(lambda x: np.floor(x/1000))
    df_hh = df_hh.merge(CBGzone_df[['GEOID','MESOZONE','County']], on='GEOID', how='left')
    df_hh= df_hh[~df_hh['MESOZONE'].isin(list_error_zone)]

    # select data in a county
    if sel_county != 9999:
        df_hh= df_hh[df_hh['County']==sel_county]
    df_hh = df_hh.reset_index()
    df_hh[['D_selection', 'D_packages']] = df_hh['delivery_f'].apply(lambda x: b2c_d_select(x, possilbe_delivey_days,growth_factor)).to_list()
    # Select B2C shipment for a certain day
    df_hh=df_hh[df_hh['D_selection']==1].reset_index(drop=True)
    # Create Shipments using D_packages, which means a household can have more than one shipment
    df_hh_D =pd.DataFrame()
    for i in range (0, df_hh.shape[0]):
        num_package=df_hh['D_packages'].iloc[i]
        for j in range(0,num_package):
            df_hh_D=pd.concat([df_hh_D,df_hh.iloc[[i]]], ignore_index=True)
    df_hh_D["D_truckload"]=1        
    df_hh_D["shipment_id"] =np.arange(df_hh_D.shape[0])       
    df_hh_D["D_truckload"]=df_hh_D["D_packages"].apply(b2c_d_truckload)


    return df_hh_D

def b2c_household_aggregation (df_hh_D, zone_df,hh_aggregation_num, county, ship_type):
    
    df_hh_D_Group_hhcount=df_hh_D.groupby(['MESOZONE'])['household_id'].count().reset_index(name='num_hh')
    # Calculate how many shipments-households in a CBG
    df_hh_D_Group_hhcount['group_size']=df_hh_D_Group_hhcount['num_hh'].apply(lambda x: int(x/hh_aggregation_num)+1)
    # Assign the aggregate household_id 
    df_hh_D['household_gr_id']=df_hh_D['MESOZONE'].apply(lambda x: b2c_hh_group_id_gen (df_hh_D_Group_hhcount,x, county, ship_type))
    # Save household_id and household_gr_id 
    payload_household_lookup=df_hh_D[['household_gr_id','household_id']]
    df_hh_D_GrID= df_hh_D.groupby(['household_gr_id', 'MESOZONE'])['D_truckload'].agg(D_truckload='sum', num_hh='count').reset_index()
    ##df_hh_D_GrID['MESOZONE']=df_hh_D_GrID['household_gr_id'].apply(lambda x: int(x/100))
    df_hh_D_GrID=df_hh_D_GrID.merge(df_hh_D_Group_hhcount[['MESOZONE','group_size']], on='MESOZONE', how='left')
    # Create approximate tour travel time to serve aggregated household-shipments
    df_hh_D_GrID['tour_tt']=df_hh_D_GrID.apply(lambda x: b2c_apro_tour_time(x['MESOZONE'], x['num_hh'], x['group_size'],hh_aggregation_num,zone_df), axis=1)
    print ("A total of aggregated B2C shipments:", df_hh_D_GrID.shape[0])

    df_hh_D_GrID.to_csv (fdir_in_out+'/Sim_outputs/Generation/B2C_daily_aggregation_%s.csv' %county, index = False, header=True)
    df_hh_D_GrID= df_hh_D_GrID.reset_index()
    return df_hh_D_GrID, payload_household_lookup

def b2c_sampling_household (df_hh_D, county,ship_type,sample_ratio):
    list_hh = df_hh_D['household_id'].unique().tolist()
    list_hh= random.sample(list_hh, int(len(list_hh)*sample_ratio/100+0.5))
    df_sample=df_hh_D[df_hh_D['household_id'].isin(list_hh)].reset_index(drop=True)    
    df_sample['household_gr_id'] = df_sample['household_id'].apply(lambda x: str(county) + "_"+ship_type + str(x))
    df_sample['tour_tt']=[int(np.random.gamma(5, 1.2, 1)[0] +0.5)  for j in df_sample.index]

    return df_sample

def b2c_sampling_household_agg (df_hh_D,sample_ratio):
    list_hh = df_hh_D['household_gr_id'].unique().tolist()
    list_hh= random.sample(list_hh, int(len(list_hh)*sample_ratio/100+0.5))
    df_sample=df_hh_D[df_hh_D['household_gr_id'].isin(list_hh)].reset_index(drop=True)    

    return df_sample


# function for B2C delivery selection and number of packages for a day 
def b2c_d_select (delivery_f, fq_factor, growth_factor):
    # maximum delivery in the data set
    # fq_factor is the number of possible delivery days in a month: 20 days, 25 days, 30 days..
    growth_factor=growth_factor+(growth_factor/100)**6
    pro=delivery_f/fq_factor
    if pro >=1:
        select =1 
        num_package=round(np.random.gamma(pro*0.8, 1)) # using gamma distribution assinge the number of delivery
        if num_package == 0:
            num_package =1
    else:
        r= random.uniform(0,1)*(100/growth_factor)
        if r < pro:
            select =1
            num_package=1
        else:
            select =0
            num_package=0
    return [select, num_package]
# B2C package load generation 
def b2c_d_truckload (packages):
    if packages >=1:
        load_one= round(np.random.gamma(0.7, 15))
        if load_one ==0:
            load_one =1
    else: 
        load_one =0            
    return load_one    
# B2C Aggregate household id generation 
def b2c_hh_group_id_gen (df,MESOZONE, county, ship_type):
    group_size = df[df['MESOZONE']==MESOZONE]['group_size'].values[0]
    group_num= MESOZONE*100+random.randint(1,group_size)
    id_gen = str(county) + "_"+ship_type + str(int(group_num))
    return id_gen
# B2C travel time and operation time generation, which is used for operational time  
def b2c_apro_tour_time(zone, num_visit,size, hh_aggregation_num, zone_df):
    try:
        if num_visit >1:
            area= zone_df[zone_df['MESOZONE']==zone]['area'].values[0]
            time = int(0.57*np.sqrt(area/size*num_visit*100)/10*60) + 2*num_visit
            if time > hh_aggregation_num*7.5: # 8 minutes thresholds
                time = int(num_visit * 7.5) # 8 minutes thresholds
        else:
            time = int(np.random.gamma(3, 1, 1)[0] +0.5) 
    except:
        time = 30 
    return time 

def b2c_create_output(df_del,truckings,df_dpt_dist, ship_type):
    # Create Payload file 
    payloads = pd.DataFrame(columns = ['payload_id', 
    'carrier_id',
    'sequence_id',
    'tour_id',
    'commodity',
    'weight',
    'job',
    'pu_zone',
    'del_zone',
    'pu_stop_duration',
    'del_stop_duration',
    'pu_tw_lower',
    'pu_tw_upper',
    'del_tw_lower',
    'del_tw_upper',
    'pu_arrival_time',
    'del_arrival_time',
    'veh_type',
    'del_x',
    'del_y',
    'pu_x',
    'pu_y',
    'ship_index'])

    payloads['payload_id']= df_del['household_gr_id']
    payloads['carrier_id']= df_del['assigned_carrier'].apply(lambda x: 'B2C_'+str(x))
    payloads['commodity']=5
    payloads['weight']=df_del['D_truckload']
    payloads['job']= 'delivery'
    payloads['del_zone']=df_del['MESOZONE']
    payloads['del_stop_duration'] =df_del['tour_tt']
    payloads['del_tw_lower']=60*8
    payloads['del_tw_upper']=60*20
    payloads['veh_type']=df_del['veh_type']
    payloads['del_x'] = df_del['del_x']
    payloads['del_y'] = df_del['del_y']
    payloads['ship_index'] = "internal"  
    ### End Create Payload file
    
    # Create carrier files 
    carriers = pd.DataFrame(columns = ['carrier_id',
    'firm_id',
    'depot_zone',
    'contract_firms',
    'depot_lower',
    'depot_upper',
    'depot_time_before',
    'depot_time_after','c_x','c_y'] + output_veh_list +["ev_type"])

    truckings=truckings.rename(columns={'BusID': 'assigned_carrier'})
    carrier_input=pd.DataFrame(df_del.assigned_carrier.unique(), columns=['assigned_carrier'])

    carrier_input=carrier_input.merge(truckings[['assigned_carrier','MESOZONE','x','y']+input_veh_list], on = 'assigned_carrier', how='left')

    carriers['carrier_id']=carrier_input['assigned_carrier'].apply(lambda x: 'B2C_'+str(x))
    carriers['firm_id']=carrier_input['assigned_carrier'].apply(lambda x: 'B2C_'+str(x))
    carriers['depot_zone']=carrier_input['MESOZONE']
    carriers['contract_firms']='Nan'
    carriers['depot_lower']= carriers['depot_zone'].apply(lambda x: depot_time_depart(x,df_dpt_dist,ship_type))
    carriers['depot_upper']= carriers['depot_lower'].apply(depot_time_close)
    carriers['depot_time_before']= [random.randrange(0,30, 5) for j in carriers.index]
    carriers['depot_time_after']= [random.randrange(0,30, 5) for j in carriers.index]
    carriers['c_x']=carrier_input['x']
    carriers['c_y']=carrier_input['y']
    for i in range(0,len(output_veh_list)):
        if "md" in output_veh_list[0]:
            carriers[output_veh_list[i]]=carrier_input[input_veh_list[i]].apply(lambda x: x+10)
        else:    
            carriers[output_veh_list[i]]=carrier_input[input_veh_list[i]]
    carriers["ev_type"] = carrier_input[input_veh_list[-1]]        
    ### End Create Carrier file
    return payloads, carriers
##################################################################
# %%
########################### B2B CODES ############################
# c1: bulk, c2:fuel_fert, c3:interm_food, c4:mfr_goods, c5:others 
def b2b_input_files_processing(firms, leasings, truckings, dist_df, CBGzone_df, sel_county, ship_direction, commodity_list, weight_theshold, list_error_zone, county_list, df_vius, b2b_day_factor,year, scenario,daily_demand_creator):
    # read household delivery file from
    fdir_synth_firm=fdir_in_out+'/Sim_inputs/Synth_firm_results/'
    county_wo_sel= [i for i in county_list if i != sel_county]
    if daily_demand_creator == "Y":
        print ("**** Generating new shipment sample")
        B2BF_T_D=b2b_d_shipment_by_commodity(fdir_synth_firm, weight_theshold,CBGzone_df,sel_county,ship_direction, county_wo_sel, b2b_day_factor,year, scenario)
        B2BF_T_D= B2BF_T_D[~B2BF_T_D['SellerZone'].isin(list_error_zone)]
        B2BF_T_D= B2BF_T_D[~B2BF_T_D['BuyerZone'].isin(list_error_zone)]
        B2BF_T_D=B2BF_T_D.dropna(axis=0, how="any").reset_index()
        B2BF_T_D.to_csv(fdir_in_out+'/Sim_outputs/Generation/B2B_daily_%s_%s.csv' % (sel_county,ship_direction), index = False, header=True)
    else: 
        print ("**** Reading existing shipment sample")
        B2BF_T_D =pd.read_csv(fdir_in_out+'/Sim_outputs/Generation/B2B_daily_%s_%s.csv' % (sel_county,ship_direction), header=0, sep=',')   

    FH_B2B= B2BF_T_D[B2BF_T_D['mode_choice']=="For-hire Truck"].reset_index(drop=True)
    PV_B2B= B2BF_T_D[B2BF_T_D['mode_choice']=="Private Truck"].reset_index(drop=True)

    # firm processing---? 
    firms_rest=firms[~firms["SellerID"].isin(PV_B2B["SellerID"])].reset_index(drop=True)
    firms=firms[firms["SellerID"].isin(PV_B2B["SellerID"])].reset_index(drop=True)
    #firms=firms.drop(columns=['md_veh', 'hd_veh'])
    leasings_orig=leasings.copy(deep=True)     

    ####
    # Private shipment processing    
    ## Assignment md, hd_voc, hd_trac using VIUS
    ## Assign vehicle type and vehicles into firms from leasing firms
    print ("**** Start private-carrier processing ****") 
    PV_B2B_ship=pd.DataFrame()
    for seller_id in PV_B2B['SellerID'].unique():
        PV_sel = PV_B2B[PV_B2B['SellerID'] == seller_id].reset_index()
        PV_sel =PV_sel.sort_values(by=['Distance','TruckLoad'])
        [[md_D_num,md_E_num, hdt_D_num, hdt_E_num, hdv_D_num, hdv_E_num, ev_class]]=firms[firms['SellerID'] == seller_id]\
                                                                                    [['Diesel Class 4-6 Vocational','Electric Class 4-6 Vocational',
                                                                                    'Diesel Class 7&8 Tractor','Electric Class 7&8 Tractor',
                                                                                    'Diesel Class 7&8 Vocational','Electric Class 7&8 Vocational',
                                                                                    'EV_powertrain (if any)']].values.tolist()
        if pd.isnull(ev_class):
            ev_class="Battery Electric"   

        dic_firm_stock={"md_D_num":md_D_num,
                        "md_E_num":md_E_num, 
                        "hdt_D_num":hdt_D_num, 
                        "hdt_E_num": hdt_E_num, 
                        "hdv_D_num":hdv_D_num, 
                        "hdv_E_num":hdv_E_num}
        dic_leasing_stock={"md_D_num":leasings[(leasings["st"]==state_id) & (leasings["powertrain"]=="Diesel")]["md"].values[0],
                "md_E_num":leasings[(leasings["st"]==state_id) & (leasings["powertrain"]==ev_class)]["md"].values[0], 
                "hdt_D_num":leasings[(leasings["st"]==state_id) & (leasings["powertrain"]=="Diesel")]["hdt"].values[0], 
                "hdt_E_num": leasings[(leasings["st"]==state_id) & (leasings["powertrain"]==ev_class)]["hdt"].values[0], 
                "hdv_D_num":leasings[(leasings["st"]==state_id) & (leasings["powertrain"]=="Diesel")]["hdv"].values[0], 
                "hdv_E_num":leasings[(leasings["st"]==state_id) & (leasings["powertrain"]==ev_class)]["hdv"].values[0]}
        dic_leased={"md_D_num":0,
        "md_E_num":0, 
        "hdt_D_num":0, 
        "hdt_E_num":0,
        "hdv_D_num":0,
        "hdv_E_num":0}                         
        PV_sel_ship=pd.DataFrame()
        for i in range(0,PV_sel.shape[0]):
            [md_load, hdv_load, hdt_load, v_type, d_range]= b2b_veh_type_truckload_prior(PV_sel["SCTG_Group"].iloc[i],PV_sel["Distance"].iloc[i], PV_sel["D_truckload"].iloc[i], df_vius, dic_firm_stock)
            if v_type=="md":
                max_load= md_max_load
            else: 
                max_load= hd_max_load    
            load=PV_sel["D_truckload"].iloc[i]
            num_shipment=int(load/max_load)+1
            temp=pd.concat([PV_sel.iloc[[i]]]*num_shipment, ignore_index=True)
            if num_shipment ==1:
                temp["D_truckload"]= load
            else:    
                temp["D_truckload"]=max_load
                temp["D_truckload"].iloc[-1]=load-max_load*(num_shipment-1)
            temp["payload_rate"]= temp["D_truckload"].apply(lambda x: 0 if x < max_load else 1).reset_index(drop=True) # 1:full 0:partial
            temp["veh_type_agg"]= v_type
            temp["veh_type"] = "U" # unassigned
            for j in range(0, temp.shape[0]):
                if temp["payload_rate"].iloc[j] == 1:
                    if v_type=="md":
                        D_num_firm = dic_firm_stock["md_D_num"]
                        E_num_firm = dic_firm_stock["md_E_num"]
                        D_num_leasing = dic_leasing_stock["md_D_num"]
                        E_num_leasing = dic_leasing_stock["md_E_num"]
                    elif v_type=="hdt":
                        D_num_firm = dic_firm_stock["hdt_D_num"]
                        E_num_firm = dic_firm_stock["hdt_E_num"]
                        D_num_leasing = dic_leasing_stock["hdt_D_num"]
                        E_num_leasing = dic_leasing_stock["hdt_E_num"]                    
                    elif v_type=="hdv":
                        D_num_firm = dic_firm_stock["hdv_D_num"]
                        E_num_firm = dic_firm_stock["hdv_E_num"]
                        D_num_leasing = dic_leasing_stock["hdv_D_num"]
                        E_num_leasing = dic_leasing_stock["hdv_E_num"]                    
                    if  D_num_firm+E_num_firm ==0:
                        if D_num_leasing+E_num_leasing ==0:
                            D_num_leasing=leasings_orig[(leasings_orig["st"]==state_id) & (leasings_orig["powertrain"]=="Diesel")][v_type].values[0]
                            E_num_leasing=leasings_orig[(leasings_orig["st"]==state_id) & (leasings_orig["powertrain"]==ev_class)][v_type].values[0]
                            powerT=util_powertrain(D_num_leasing, E_num_leasing, dic_energy, temp['Distance'].iloc[j], dic_veh[v_type], ev_class, 0.8)
                        else:
                            powerT=util_powertrain(D_num_leasing, E_num_leasing, dic_energy, temp['Distance'].iloc[j], dic_veh[v_type], ev_class, 0.8)
                            dic_leasing_stock[v_type+"_"+powerT+"_num"] = dic_leasing_stock[v_type+"_"+powerT+"_num"]-1
                        dic_leased[v_type+"_"+powerT+"_num"]= dic_leased[v_type+"_"+powerT+"_num"] +1    
                    else:       
                        powerT=util_powertrain(D_num_firm, E_num_firm, dic_energy, temp['Distance'].iloc[j], dic_veh[v_type], ev_class, 0.5)
                        dic_firm_stock[v_type+"_"+powerT+"_num"] = dic_firm_stock[v_type+"_"+powerT+"_num"]-1
                    if powerT == "D":
                        p_lable="Diesel"
                    else:
                        p_lable=ev_class          
                    temp["veh_type"].iloc[j]=v_type+"_"+powerT+"_"+p_lable    
            PV_sel_ship= pd.concat([PV_sel_ship,temp], ignore_index=True).reset_index(drop=True)
            del temp
        PV_sel_ship_A =PV_sel_ship[PV_sel_ship["veh_type"]!="U"]
        PV_sel_ship_U =PV_sel_ship[PV_sel_ship["veh_type"]=="U"]
        PV_sel_ship_U=PV_sel_ship_U.sort_values(by=['D_truckload','Distance'])
        dic_tour={"md_D":max_tour,
            "md_E":max_tour, 
            "hdt_D":max_tour, 
            "hdt_E":max_tour, 
            "hdv_D":max_tour, 
            "hdv_E":max_tour} 
        # initialization
        max_load=hd_max_load
        cum_payload=1
        v_type="hdt"
        powerT="E"
        for i in range(0,PV_sel_ship_U.shape[0]):
            if (cum_payload+ PV_sel_ship_U["D_truckload"].iloc[i]/max_load) >1 or (dic_tour[v_type+"_"+powerT] ==0):
                dic_tour[v_type+"_"+powerT]=max_tour
                cum_payload=0
                v_type= PV_sel_ship_U["veh_type_agg"].iloc[i] 
                if v_type=="md":
                    D_num_firm = dic_firm_stock["md_D_num"]
                    E_num_firm = dic_firm_stock["md_E_num"]
                    D_num_leasing = dic_leasing_stock["md_D_num"]
                    E_num_leasing = dic_leasing_stock["md_E_num"]
                    max_load= md_max_load
                elif v_type=="hdt":
                    D_num_firm = dic_firm_stock["hdt_D_num"]
                    E_num_firm = dic_firm_stock["hdt_E_num"]
                    D_num_leasing = dic_leasing_stock["hdt_D_num"]
                    E_num_leasing = dic_leasing_stock["hdt_E_num"]
                    max_load= hd_max_load                    
                elif v_type=="hdv":
                    D_num_firm = dic_firm_stock["hdv_D_num"]
                    E_num_firm = dic_firm_stock["hdv_E_num"]
                    D_num_leasing = dic_leasing_stock["hdv_D_num"]
                    E_num_leasing = dic_leasing_stock["hdv_E_num"]
                    max_load= hd_max_load
                payload_rate =PV_sel_ship_U["D_truckload"].iloc[i]/max_load                     
                if  D_num_firm+E_num_firm <=0:
                    if D_num_leasing+E_num_leasing <=0:
                        D_num_leasing=leasings_orig[(leasings_orig["st"]==state_id) & (leasings_orig["powertrain"]=="Diesel")][v_type].values[0]
                        E_num_leasing=leasings_orig[(leasings_orig["st"]==state_id) & (leasings_orig["powertrain"]==ev_class)][v_type].values[0]
                        powerT=util_powertrain(D_num_leasing, E_num_leasing, dic_energy, PV_sel_ship_U['Distance'].iloc[i], dic_veh[v_type], ev_class, 0.8)
                        leasing_flag="add_leasing"
                    else:
                        powerT=util_powertrain(D_num_leasing, E_num_leasing, dic_energy, PV_sel_ship_U['Distance'].iloc[i], dic_veh[v_type], ev_class, 0.8)
                        dic_leasing_stock[v_type+"_"+powerT+"_num"] = dic_leasing_stock[v_type+"_"+powerT+"_num"]- payload_rate
                        leasing_flag="use_leasing"
                    dic_leased[v_type+"_"+powerT+"_num"]= dic_leased[v_type+"_"+powerT+"_num"] + payload_rate    
                else:       
                    powerT=util_powertrain(D_num_firm, E_num_firm, dic_energy, PV_sel_ship_U['Distance'].iloc[i], dic_veh[v_type], ev_class, 0.5)
                    dic_firm_stock[v_type+"_"+powerT+"_num"] = dic_firm_stock[v_type+"_"+powerT+"_num"]-payload_rate
                    leasing_flag="no_leasing"
                cum_payload=cum_payload+ payload_rate
                dic_tour[v_type+"_"+powerT]=dic_tour[v_type+"_"+powerT]-1
                if powerT == "D":
                    p_lable="Diesel"
                else:
                    p_lable=ev_class 
                PV_sel_ship_U["veh_type"].iloc[i]=v_type+"_"+powerT+"_"+p_lable
            else: 
                payload_rate =PV_sel_ship_U["D_truckload"].iloc[i]/max_load 
                if leasing_flag=="add_leasing":
                    dic_leased[v_type+"_"+powerT+"_num"]= dic_leased[v_type+"_"+powerT+"_num"] + payload_rate
                elif leasing_flag=="use_leasing":
                    dic_leasing_stock[v_type+"_"+powerT+"_num"] = dic_leasing_stock[v_type+"_"+powerT+"_num"]- payload_rate
                    dic_leased[v_type+"_"+powerT+"_num"]= dic_leased[v_type+"_"+powerT+"_num"] + payload_rate
                elif leasing_flag=="no_leasing":
                    dic_firm_stock[v_type+"_"+powerT+"_num"] = dic_firm_stock[v_type+"_"+powerT+"_num"]-payload_rate          
                cum_payload=cum_payload+ payload_rate
                dic_tour[v_type+"_"+powerT]=dic_tour[v_type+"_"+powerT]-1
                if powerT == "D":
                    p_lable="Diesel"
                else:
                    p_lable=ev_class 
                PV_sel_ship_U["veh_type"].iloc[i]=v_type+"_"+powerT+"_"+p_lable               

        PV_B2B_ship=pd.concat([PV_B2B_ship,PV_sel_ship_A,PV_sel_ship_U], ignore_index=True).reset_index(drop=True)
        # update stock
        firm_index= firms[firms['SellerID'] == seller_id].index.item()
        for key in dic_leased.keys():
            if dic_leased[key]>0:
               add_to_firm=int(dic_leased[key]+1) + 4
            else:
               add_to_firm =0    
            if key ==  "md_D_num":
                firms['Diesel Class 4-6 Vocational'].iloc[firm_index] =firms['Diesel Class 4-6 Vocational'].iloc[firm_index]  +add_to_firm   
            elif key == "md_E_num":
                firms['Electric Class 4-6 Vocational'].iloc[firm_index] =firms['Electric Class 4-6 Vocational'].iloc[firm_index]  +add_to_firm 
            elif key == "hdt_D_num": 
                firms['Diesel Class 7&8 Tractor'].iloc[firm_index] =firms['Diesel Class 7&8 Tractor'].iloc[firm_index]  +add_to_firm 
            elif key == "hdt_E_num":
                firms['Electric Class 7&8 Tractor'].iloc[firm_index] =firms['Electric Class 7&8 Tractor'].iloc[firm_index]  +add_to_firm 
            elif key == "hdv_D_num":
                firms['Diesel Class 7&8 Vocational'].iloc[firm_index] =firms['Diesel Class 7&8 Vocational'].iloc[firm_index]  +add_to_firm 
            elif key == "hdv_E_num": 
                firms['Electric Class 7&8 Vocational'].iloc[firm_index] =firms['Electric Class 7&8 Vocational'].iloc[firm_index]  +add_to_firm  
        firms['EV_powertrain (if any)'].iloc[firm_index] =ev_class
        for key in dic_leasing_stock.keys():

            update_to_leasings= int(dic_leasing_stock[key])
            if key ==  "md_D_num":
                leasing_index=leasings[(leasings["st"]==state_id) & (leasings["powertrain"]=="Diesel")].index.item()
                leasings['md'].iloc[leasing_index] = update_to_leasings   
            elif key == "md_E_num":
                leasing_index=leasings[(leasings["st"]==state_id) & (leasings["powertrain"]==ev_class)].index.item()
                leasings['md'].iloc[leasing_index] = update_to_leasings  
            elif key == "hdt_D_num": 
                leasing_index=leasings[(leasings["st"]==state_id) & (leasings["powertrain"]=="Diesel")].index.item()
                leasings['hdt'].iloc[leasing_index] = update_to_leasings  
            elif key == "hdt_E_num":
                leasing_index=leasings[(leasings["st"]==state_id) & (leasings["powertrain"]==ev_class)].index.item()
                leasings['hdt'].iloc[leasing_index] = update_to_leasings  
            elif key == "hdv_D_num":
                leasing_index=leasings[(leasings["st"]==state_id) & (leasings["powertrain"]=="Diesel")].index.item()
                leasings['hdv'].iloc[leasing_index] = update_to_leasings  
            elif key == "hdv_E_num": 
                leasing_index=leasings[(leasings["st"]==state_id) & (leasings["powertrain"]==ev_class)].index.item()
                leasings['hdv'].iloc[leasing_index] = update_to_leasings
    print ("**** Complete private-carrier processing ****")    
    ################################################################

    ###########################################################
    # For-hire processing
    truckings_B=truckings.copy(deep=True) 
    md_D_num =truckings["Diesel Class 4-6 Vocational"].sum()
    md_E_num =truckings["Electric Class 4-6 Vocational"].sum()
    hdt_D_num=truckings["Diesel Class 7&8 Tractor"].sum()
    hdt_E_num=truckings["Electric Class 7&8 Tractor"].sum()
    hdv_D_num=truckings["Diesel Class 7&8 Vocational"].sum()
    hdv_E_num=truckings["Electric Class 7&8 Vocational"].sum()
    dic_trucking_stock={"md_D_num":md_D_num,
        "md_E_num":md_E_num, 
        "hdt_D_num":hdt_D_num, 
        "hdt_E_num": hdt_E_num, 
        "hdv_D_num":hdv_D_num, 
        "hdv_E_num":hdv_E_num}    
    print ("**** Start for-hire-carrier processing ****") 
    FH_B2B_ship=pd.DataFrame()
    for seller_id in FH_B2B['SellerID'].unique():
    #for seller_id in [919143, 908126, 907957, 906687]:
        # seller_id= 98420   
        FH_sel = FH_B2B[FH_B2B['SellerID'] == seller_id].reset_index()

        def dist_group(Distance):
            if Distance <=50:
                return 50
            elif Distance >50 and Distance <=100:
                return 100
            elif Distance >100 and Distance <=200: 
                return 200
            elif Distance >200 and Distance <=500:
                return 500
            else:                   
                return 1000
        FH_sel["Dist_group"]= FH_sel["Distance"].apply(lambda x: dist_group(x))
        FH_Seller= FH_sel.groupby(['SellerZone','SCTG_Group','Dist_group'])['D_truckload'].agg(agg_truckload='sum', num_ship='count').reset_index()
        FH_Seller.loc[:,'assigned_carrier']="no"
        FH_Seller.loc[:,'veh_type_agg']="U"
        for i in range(0,FH_Seller.shape[0]):
            [md_load, hdv_load, hdt_load, v_type, d_range]= b2b_veh_type_truckload_prior(FH_Seller["SCTG_Group"].iloc[i],FH_Seller["Dist_group"].iloc[i], FH_Seller["agg_truckload"].iloc[i], df_vius, dic_trucking_stock)
            if v_type=="md":
                max_load= md_max_load
            else: 
                max_load= hd_max_load    
            cap_index = v_type+"_capacity"
            time_index= v_type+"_time_cap"
          
            # find a carrier who can hand a shipment at row i   
            sel_busID=carrier_sel(FH_Seller['SellerZone'].iloc[i], FH_Seller['agg_truckload'].iloc[i], FH_Seller['num_ship'].iloc[i]*60, cap_index,time_index, dist_df, truckings,"B2B", FH_Seller['SCTG_Group'].iloc[i])
            # put the carrier into df

            if sel_busID != "no":

                FH_Seller['assigned_carrier'].iloc[i]=sel_busID
                FH_Seller['veh_type_agg'].iloc[i]=v_type
                # print (sel_busID,seller_id)
                # Calculate the reduce the capacity and time capacity that can reflect after a row assignment
                trucking_index = truckings.index[truckings["BusID"]==sel_busID].values[0]
                truckings.loc[trucking_index,cap_index] = truckings.loc[trucking_index,cap_index] - FH_Seller.loc[i,'agg_truckload']
                truckings.loc[trucking_index,time_index] = truckings.loc[trucking_index,time_index] - FH_Seller['num_ship'].iloc[i]*60

        FH_sel=FH_sel.merge(FH_Seller[['SellerZone','SCTG_Group','Dist_group','assigned_carrier','veh_type_agg']], on=['SellerZone','SCTG_Group','Dist_group'], how='left')
        for i in range(0,FH_sel.shape[0]):
            if FH_sel['assigned_carrier'].iloc[i]=="no":
                [md_load, hdv_load, hdt_load, v_type, d_range]= b2b_veh_type_truckload_prior(FH_sel["SCTG_Group"].iloc[i],FH_sel["Distance"].iloc[i], FH_sel["D_truckload"].iloc[i], df_vius, dic_trucking_stock)
                if v_type=="md":
                    max_load= md_max_load
                else: 
                    max_load= hd_max_load    
                cap_index = v_type+"_capacity"
                time_index= v_type+"_time_cap"
            
                # find a carrier who can hand a shipment at row i   
                sel_busID=carrier_sel(FH_sel['SellerZone'].iloc[i], FH_sel['D_truckload'].iloc[i], 60, cap_index, time_index, dist_df, truckings,"B2B", FH_sel['SCTG_Group'].iloc[i])
                # put the carrier into df
                if sel_busID != "no":
                    FH_sel['assigned_carrier'].iloc[i]=sel_busID
                    FH_sel['veh_type_agg'].iloc[i]=v_type
                    # Calculate the reduce the capacity and time capacity that can reflect after a row assignment
                    trucking_index = truckings.index[truckings["BusID"]==sel_busID].values[0]
                    truckings.loc[trucking_index,cap_index] = truckings.loc[trucking_index,cap_index] - FH_sel.loc[i,'D_truckload']
                    truckings.loc[trucking_index,time_index] = truckings.loc[trucking_index,time_index] - 60
                else:
                    load=FH_sel["D_truckload"].iloc[i]
                    num_shipment=int(load/max_load)+1
                    temp=pd.concat([FH_sel.iloc[[i]]]*num_shipment, ignore_index=True)
                    if num_shipment ==1:
                        temp["D_truckload"]= load
                    else:    
                        temp["D_truckload"]=max_load
                        temp["D_truckload"].iloc[-1]=load-max_load*(num_shipment-1)
                    for j in range(0, temp.shape[0]):
                        sel_busID=carrier_sel(temp['SellerZone'].iloc[j], temp['D_truckload'].iloc[j], 60, cap_index, time_index, dist_df, truckings,"B2B", temp['SCTG_Group'].iloc[j])
                        if sel_busID != "no":
                            temp['assigned_carrier'].iloc[j]=sel_busID
                            temp['veh_type_agg'].iloc[j]=v_type
                            # Calculate the reduce the capacity and time capacity that can reflect after a row assignment
                            trucking_index = truckings.index[truckings["BusID"]==sel_busID].values[0]
                            truckings.loc[trucking_index,cap_index] = truckings.loc[trucking_index,cap_index] - temp.loc[j,'D_truckload']
                            truckings.loc[trucking_index,time_index] = truckings.loc[trucking_index,time_index] - 60
                        else:
                            temp['assigned_carrier'].iloc[j]=sel_busID
                            temp['veh_type_agg'].iloc[j]=v_type
                    FH_sel.iloc[i]=temp.iloc[0]
                    if num_shipment >1:                                     
                        FH_sel=pd.concat([FH_sel,temp.iloc[1:]], ignore_index=True).reset_index(drop=True)   

        FH_sel=FH_sel[FH_sel['assigned_carrier'] !="no"].reset_index(drop=True)

        FH_sel_ship=pd.DataFrame()
        for i in range(0,FH_sel.shape[0]):
            v_type= FH_sel['veh_type_agg'].iloc[i]
            carr_id= FH_sel['assigned_carrier'].iloc[i]
            [[md_D_num,md_E_num, hdt_D_num, hdt_E_num, hdv_D_num, hdv_E_num, ev_class]]=truckings_B[truckings_B["BusID"] == carr_id]\
                                                                                    [['Diesel Class 4-6 Vocational','Electric Class 4-6 Vocational',
                                                                                    'Diesel Class 7&8 Tractor','Electric Class 7&8 Tractor',
                                                                                    'Diesel Class 7&8 Vocational','Electric Class 7&8 Vocational',
                                                                                    'EV_powertrain (if any)']].values.tolist()
            
            if pd.isnull(ev_class):
                ev_class="Battery Electric"   
    
            dic_firm_stock={"md_D_num":md_D_num,
                            "md_E_num":md_E_num, 
                            "hdt_D_num":hdt_D_num, 
                            "hdt_E_num": hdt_E_num, 
                            "hdv_D_num":hdv_D_num, 
                            "hdv_E_num":hdv_E_num}                

            if v_type=="md":
                max_load= md_max_load
            else: 
                max_load= hd_max_load    
            load=FH_sel["D_truckload"].iloc[i]
            num_shipment=int(load/max_load)+1
            temp=pd.concat([FH_sel.iloc[[i]]]*num_shipment, ignore_index=True)
            if num_shipment ==1:
                temp["D_truckload"]= load
            else:    
                temp["D_truckload"]=max_load
                temp["D_truckload"].iloc[-1]=load-max_load*(num_shipment-1)
            temp["payload_rate"]= temp["D_truckload"].apply(lambda x: x/max_load).reset_index(drop=True) # 1:full 0:partial
            temp["veh_type_agg"]= v_type
            temp["veh_type"] = "U" # unassigned
            for j in range(0, temp.shape[0]):
                D_num_firm = dic_firm_stock[v_type+"_D_num"]
                E_num_firm = dic_firm_stock[v_type+"_E_num"]
                if D_num_firm -temp['payload_rate'].iloc[j] <0:
                   D_num_firm =0 
                if E_num_firm -temp['payload_rate'].iloc[j] <0:
                   E_num_firm =0 
                if D_num_firm+E_num_firm -temp['payload_rate'].iloc[j] <0:
                   D_num_firm=1
                   E_num_firm=1                 
                powerT=util_powertrain(D_num_firm, E_num_firm, dic_energy, temp['Distance'].iloc[j], dic_veh[v_type], ev_class, 0.5)
                dic_firm_stock[v_type+"_"+powerT+"_num"] = dic_firm_stock[v_type+"_"+powerT+"_num"]-temp['payload_rate'].iloc[j]
                if powerT == "D":
                    p_lable="Diesel"
                else:
                    p_lable=ev_class          
                temp["veh_type"].iloc[j]=v_type+"_"+powerT+"_"+p_lable
            firm_index= truckings_B[truckings_B["BusID"] == carr_id].index.item()
            for key in dic_firm_stock.keys():   
                if key ==  "md_D_num":
                    truckings_B['Diesel Class 4-6 Vocational'].iloc[firm_index] =  max (dic_firm_stock[key],0) 
                elif key == "md_E_num":
                    truckings_B['Electric Class 4-6 Vocational'].iloc[firm_index] =max(dic_firm_stock[key],0) 
                elif key == "hdt_D_num": 
                    truckings_B['Diesel Class 7&8 Tractor'].iloc[firm_index] =max(dic_firm_stock[key],0)  
                elif key == "hdt_E_num":
                    truckings_B['Electric Class 7&8 Tractor'].iloc[firm_index] =max(dic_firm_stock[key],0)  
                elif key == "hdv_D_num":
                    truckings_B['Diesel Class 7&8 Vocational'].iloc[firm_index] =max(dic_firm_stock[key],0) 
                elif key == "hdv_E_num": 
                    truckings_B['Electric Class 7&8 Vocational'].iloc[firm_index] =max(dic_firm_stock[key],0)   
            truckings_B['EV_powertrain (if any)'].iloc[firm_index] =ev_class
            FH_sel_ship= pd.concat([FH_sel_ship,temp], ignore_index=True).reset_index(drop=True)
            del temp              
            
        FH_B2B_ship=pd.concat([FH_B2B_ship,FH_sel_ship], ignore_index=True).reset_index(drop=True)
        # update stock
    print ("**** Completed for-hire-carrier processing ****")    
    firms=pd.concat([firms,firms_rest], ignore_index=True).reset_index(drop=True)
    return FH_B2B_ship, PV_B2B_ship, firms
def sampling_shipper(temp, sample_ratio, bin_size):
    temp_1 = temp.groupby(['SellerID'])['SellerID'].count().reset_index(name='num_shipment')
    total_size=temp_1.shape[0]
    if (total_size*sample_ratio)/(100) < bin_size:
        bin_size = int((total_size*sample_ratio)/(100))
    try:    
        temp_1["binned_volume"] =pd.qcut(temp_1['num_shipment'], q=bin_size, labels=False)
    except:
        temp_1["binned_volume"]=temp_1['num_shipment'].apply(lambda x:lable_creater(x))

    list_bin_labels = temp_1["binned_volume"].unique().tolist()
    list_shipper_sample=[]
    for bin_id in list_bin_labels:
        temp_2=temp_1[(temp_1['binned_volume']==bin_id)]
        list_shipper = temp_2['SellerID'].unique().tolist()
        if (len(list_shipper)*sample_ratio/100 >0) & (len(list_shipper)*sample_ratio/100 <0.5):
            list_shipper= random.sample(list_shipper, int(len(list_shipper)*sample_ratio/100+0.5))
            list_shipper_sample=list_shipper_sample+list_shipper
        elif (len(list_shipper)*sample_ratio/100 >=0.5):     
            list_shipper= random.sample(list_shipper, int(len(list_shipper)*sample_ratio/100+0.5))
            list_shipper_sample=list_shipper_sample+list_shipper  
    df_sample=temp[temp['SellerID'].isin(list_shipper_sample)].reset_index(drop=True)

    return df_sample

def b2b_d_truckload(TruckLoad, w_th):
    if TruckLoad <= w_th*1:
        return float(TruckLoad)
    elif TruckLoad <= w_th*12 and TruckLoad > w_th*1:
        return float(TruckLoad/3)
    elif TruckLoad <= w_th*48 and TruckLoad > w_th*12:
        return float(TruckLoad/6)          
    elif TruckLoad <= w_th*144 and TruckLoad > w_th*48:
        return float(TruckLoad/10)            
    elif TruckLoad <= w_th*288 and TruckLoad > w_th*144:
        return float(TruckLoad/15)
    elif TruckLoad <= w_th*576 and TruckLoad > w_th*288:
        return float(TruckLoad/21)
    elif TruckLoad <= w_th*1152 and TruckLoad > w_th*2304:
        return float(TruckLoad/28)
    elif TruckLoad <= w_th*4608 and TruckLoad > w_th*1152:
        return float(TruckLoad/36)
    elif TruckLoad <= w_th*9216 and TruckLoad > w_th*4608:
        return float(TruckLoad/45)
    elif TruckLoad > w_th*9216:
        return float(TruckLoad/60)    
def b2b_d_select(TruckLoad,w_th):
    if TruckLoad <= w_th*1:
         if random.uniform(0,1) <=1/365:
            return 1
         else: return 0   
    elif TruckLoad <= w_th*12 and TruckLoad > w_th*1:
         if random.uniform(0,1) <=2/365:
            return 1
         else: return 0  
    elif TruckLoad <= w_th*48 and TruckLoad > w_th*12:
         if random.uniform(0,1) <=5/365:
            return 1
         else: return 0           
    elif TruckLoad <= w_th*144 and TruckLoad > w_th*48:
         if random.uniform(0,1) <=10/365:
            return 1
         else: return 0              
    elif TruckLoad <= w_th*288 and TruckLoad > w_th*144:
         if random.uniform(0,1) <=15/365:
            return 1
         else: return 0  
    elif TruckLoad <= w_th*576 and TruckLoad > w_th*288:
         if random.uniform(0,1) <=21/365:
            return 1
         else: return 0  
    elif TruckLoad <= w_th*1152 and TruckLoad > w_th*2304:
         if random.uniform(0,1) <=30/365:
            return 1
         else: return 0  
    elif TruckLoad <= w_th*4608 and TruckLoad > w_th*1152:
         if random.uniform(0,1) <=48/365:
            return 1
         else: return 0  
    elif TruckLoad <= w_th*9216 and TruckLoad > w_th*4608:
         if random.uniform(0,1) <=77/365:
            return 1
         else: return 0  
    elif TruckLoad > w_th*9216:
         if random.uniform(0,1) <=126/365:
            return 1
         else: return 0   
    else: return 0
def b2b_d_select_with_ship_size(TruckLoad,w_th, b2b_day_factor):
    if TruckLoad <= w_th*1:
         if random.uniform(0,1) <=(b2b_day_factor/52.15):
            return 1
         else: return 0   
    else:
         if random.uniform(0,1) <=(b2b_day_factor/52.15):
            return 1
         else: return 0 

def b2b_d_shipment_by_commodity(fdir, weight_theshold, CBGzone_df,sel_county,ship_direction, county_wo_sel, b2b_day_factor,year, scenario): 
    B2BF=pd.DataFrame()
    sub_fdir="{}_{}/".format(year,scenario)
    for filename in glob.glob(fdir+sub_fdir+'*.csv'):
        temp= pd.read_csv(filename, header=0, sep=',')
        if temp.shape[0] >0:
            temp["SellerID"]=temp["SellerID"].astype("int") 
            if "fleet_id" in temp.columns:
                temp["fleet_id"]=temp["fleet_id"].astype("int") 
                temp["SellerID"] = temp.apply(lambda x: str(x["SellerID"]) + "_" + str(x["fleet_id"]), axis=1)
                temp = temp.drop("fleet_id", axis=1)
            else:
                temp["SellerID"] = temp.apply(lambda x: str(x["SellerID"]) + "_1", axis=1)
            temp["BuyerID"] = temp.apply(lambda x: str(x["BuyerID"]) + "_1", axis=1)        
            temp=temp.astype({'BuyerID': 'string',
            "BuyerZone":"int64",
            "BuyerNAICS":"string",
            "SellerID":"string",
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
            # Add SellerCounty and BuyerCounty for filering 
            temp = temp.merge(CBGzone_df[['MESOZONE','County']], left_on="SellerZone", right_on='MESOZONE', how='left')
            temp=temp.rename({'County':'SellerCounty'}, axis=1)
            temp = temp.merge(CBGzone_df[['MESOZONE','County']], left_on="BuyerZone", right_on='MESOZONE', how='left')
            temp=temp.rename({'County':'BuyerCounty'}, axis=1)
            if sel_county != 9999:
                if ship_direction == "out":
                    temp= temp[temp['SellerCounty']==sel_county].reset_index(drop=True)
                elif ship_direction == "in":
                    temp= temp[(temp['BuyerCounty']==sel_county) & (temp['SellerCounty']!=sel_county)].reset_index(drop=True)
                elif ship_direction == "all":
                    temp= temp[(temp['BuyerCounty']==sel_county) | (temp['SellerCounty']==sel_county)].reset_index(drop=True)
                    temp= temp[~temp['SellerCounty'].isin(county_wo_sel)].reset_index(drop=True)
            temp['TruckLoad']=temp['TruckLoad']*2000
            temp["D_truckload"]=0
            temp["D_selection"]=0
            temp["D_truckload"]=temp['TruckLoad']
            temp["D_selection"]=temp['TruckLoad'].apply(lambda x: b2b_d_select_with_ship_size(x, weight_theshold, b2b_day_factor))
            temp=temp.query('D_selection ==1')
            if sample_ratio <100: 
                temp=sampling_shipper(temp, sample_ratio, bin_size)

            B2BF=pd.concat([B2BF,temp],ignore_index=True)
    return B2BF

def b2b_veh_type_truckload_prior(SCTG_Group,Distance, D_truckload, df_vius,dic_firm_stock):

    md_num = dic_firm_stock["md_D_num"]  + dic_firm_stock["md_E_num"]
    hdt_num= dic_firm_stock["hdt_D_num"] + dic_firm_stock["hdt_E_num"]
    hdv_num= dic_firm_stock["hdv_D_num"] + dic_firm_stock["hdv_E_num"]
    if md_num+hdt_num+hdv_num==0:
        md_prior=1
        hdt_prior=1
        hdv_prior=1
    else:
        md_prior=md_num/(md_num+hdt_num+hdv_num)
        hdt_prior=hdt_num/(md_num+hdt_num+hdv_num)
        hdv_prior=hdv_num/(md_num+hdt_num+hdv_num)   

    if Distance <=50:
        col_name="TRIP0_50"
    elif Distance >50 and Distance <=100:
        col_name='TRIP051_100'
    elif Distance >100 and Distance <=200: 
        col_name='TRIP101_200'
    elif Distance >200 and Distance <=500:
        col_name='TRIP201_500'
    else:                   
        col_name='TRIP500MORE'
    
    hdt_val=df_vius[(df_vius["sctg"]==SCTG_Group) & (df_vius['veh_type']=='hd_tractor')][col_name].values[0]
    hdv_val=df_vius[(df_vius["sctg"]==SCTG_Group) & (df_vius['veh_type']=='hd_voc')][col_name].values[0]
    md_val=df_vius[(df_vius["sctg"]==SCTG_Group) & (df_vius['veh_type']=='md')][col_name].values[0]
    if md_val+hdt_val+hdv_val==0:
        md_vius =1
        hdt_vius=1
        hdv_vius=1
    else:
        md_vius=md_val/(md_val+hdt_val+hdv_val)
        hdt_vius=hdt_val/(md_val+hdt_val+hdv_val)
        hdv_vius=hdv_val/(md_val+hdt_val+hdv_val)

    md_pro  = md_prior*md_vius/(md_prior*md_vius+ hdt_prior*hdt_vius+hdv_prior*hdv_vius)
    hdt_pro = hdt_prior*hdt_vius/(md_prior*md_vius+ hdt_prior*hdt_vius+hdv_prior*hdv_vius)    
    hdv_pro = hdv_prior*hdv_vius/(md_prior*md_vius+ hdt_prior*hdt_vius+hdv_prior*hdv_vius)

    cum_md_pro=md_pro
    cum_hdt_pro=cum_md_pro+hdt_pro
    cum_hdv_pro=cum_hdt_pro+hdv_pro
    prob_veh = random.uniform(0,1)
    if prob_veh < cum_md_pro: # MD
        v_type ="md"
        md_load = D_truckload
        hd_trac_load = 0
        hd_voc_load = 0
    elif prob_veh >= cum_md_pro and prob_veh < cum_hdt_pro: # hd_voc
        v_type ="hdt"
        md_load = 0
        hd_trac_load = D_truckload
        hd_voc_load = 0
    elif prob_veh >= cum_hdt_pro: # hd_trac
        v_type ="hdv"
        md_load = 0
        hd_trac_load =  0
        hd_voc_load = D_truckload   
    return [md_load, hd_voc_load, hd_trac_load, v_type, col_name]

def b2b_veh_type_truckload(SCTG_Group,Distance, D_truckload, df_vius):

    if Distance <=50:
        col_name="TRIP0_50"
    elif Distance >50 and Distance <=100:
        col_name='TRIP051_100'
    elif Distance >100 and Distance <=200: 
        col_name='TRIP101_200'
    elif Distance >200 and Distance <=500:
        col_name='TRIP201_500'
    else:                   
        col_name='TRIP500MORE'
    
    hd_tractor_val=df_vius[(df_vius["sctg"]==SCTG_Group) & (df_vius['veh_type']=='hd_tractor')][col_name].values[0]
    hd_voc_val=df_vius[(df_vius["sctg"]==SCTG_Group) & (df_vius['veh_type']=='hd_voc')][col_name].values[0]
    md_val=df_vius[(df_vius["sctg"]==SCTG_Group) & (df_vius['veh_type']=='md')][col_name].values[0]
    prob_veh = random.uniform(0,1)
    if prob_veh < md_val/(hd_tractor_val+hd_voc_val+md_val): # MD
        v_type ="md"
        md_load = D_truckload
        hd_trac_load = 0
        hd_voc_load = 0
    elif prob_veh >= md_val/(hd_tractor_val+hd_voc_val+md_val) and prob_veh < (md_val+hd_voc_val)/(hd_tractor_val+hd_voc_val+md_val): # hd_voc
        v_type ="hd_voc"
        md_load = 0
        hd_trac_load = 0
        hd_voc_load = D_truckload
    else: # hd_trac
        v_type ="hd_trac"
        md_load = 0
        hd_trac_load =  D_truckload
        hd_voc_load = 0    
    return [md_load, hd_voc_load, hd_trac_load, v_type, col_name]
def b2b_apro_tour_time(zone, num_visit,size, zone_df):
    try:
        if num_visit >1:
            area= zone_df[zone_df['MESOZONE']==zone]['area'].values[0]
            time = int(0.57*np.sqrt(area/size*num_visit*100)/10*60+0.5)
            if time >60*3:
                time = int(num_visit * 2.5) 
        else:
            time = int(np.random.gamma(3, 1, 1)[0] +0.5) 
    except:
        time = 90 
    return time
def ex_seller_zone_to_boundary(sellerzone, inbound_index, df_ex):
    if inbound_index ==1:
        return df_ex[df_ex['MESOZONE']==sellerzone]['BoundaryZONE'].values[0] 
    else:
        return sellerzone  
def ex_coordinate(x,y,sellerzone, inbound_index, df_ex):
    if inbound_index ==1:
        [[new_x, new_y]]=df_ex[df_ex['MESOZONE']==sellerzone][['x','y']].values.tolist()
        return new_x, new_y 
    else:
        return x, y        
def b2b_create_output(B2BF_PV,B2BF_FH,truckings,df_dpt_dist, ship_type, ex_zone_list, firms,ex_zone):

    PV_T_D =B2BF_PV.groupby(['SellerID', 'SellerZone', 'inbound_index','outbound_index'])['D_truckload'].agg(D_truckload="sum").reset_index()

    firms=firms[['SellerID','MESOZONE','x','y']+input_veh_list]
    PV_T_D = PV_T_D.merge(firms, on='SellerID', how='left').reset_index()
    num =0    
    for i in range(0, PV_T_D.shape[0]):
        PV_T_D.loc[i,"Bus_ID"]=str(PV_T_D.loc[i,"SellerID"])+ "_"+str(num)
        num +=1

    B2BF_PV =B2BF_PV.merge(PV_T_D[['SellerID', 'SellerZone', 'inbound_index','outbound_index',"Bus_ID"]], on=['SellerID', 'SellerZone', 'inbound_index','outbound_index'], how="left")

    carriers = pd.DataFrame(columns = ['carrier_id',
    'firm_id',
    'depot_zone',
    'contract_firms',
    'depot_lower',
    'depot_upper',
    'depot_time_before',
    'depot_time_after',
    'c_x','c_y']+ output_veh_list +["ev_type"])

            
    carriers['carrier_id']=PV_T_D['Bus_ID'].apply(lambda x: 'B2B_'+str(x))
    carriers['firm_id']=PV_T_D['Bus_ID'].apply(lambda x: 'B2B_'+str(x))
    carriers['depot_zone']=PV_T_D.apply(lambda x: ex_seller_zone_to_boundary(x['SellerZone'], x['inbound_index'], ex_zone), axis=1)
    carriers['contract_firms']=PV_T_D['Bus_ID'].apply(lambda x: [x])
    carriers['depot_lower']= PV_T_D.apply(lambda x: depot_time_depart(x['MESOZONE'],df_dpt_dist,ship_type) if x['inbound_index']==0 else time_normal(5, 3, 1,12), axis=1)
    carriers['depot_upper']= PV_T_D['outbound_index'].apply(lambda x: 2*24*60 if x ==1 else time_normal(24, 3, 21,28))#carriers['depot_lower'].apply(depot_time_close)
    carriers['depot_time_before']= [random.randrange(5,30, 5) for j in carriers.index]
    carriers['depot_time_after']= [random.randrange(5,30, 5) for j in carriers.index]
    carriers['c_x'], carriers['c_y'] =zip(*PV_T_D.apply(lambda x: ex_coordinate(x['x'],x['y'], x['SellerZone'], x['inbound_index'], ex_zone), axis=1))
    for i in range(0,len(output_veh_list)):
        if "md" in output_veh_list[0]:
            carriers[output_veh_list[i]]=PV_T_D[input_veh_list[i]].apply(lambda x: x+5)
        else:    
            carriers[output_veh_list[i]]=PV_T_D[input_veh_list[i]].apply(lambda x: x+5)
    carriers["ev_type"] = PV_T_D[input_veh_list[-1]] 

    temp_FH_T_D = B2BF_FH.groupby(['assigned_carrier','outbound_index'])['SellerID'].apply(list).reset_index(name='contract_firms')
    firms_sub=truckings[['BusID','MESOZONE', 'inbound_index','x','y']+input_veh_list]
    firms_sub=firms_sub.rename({'BusID':'assigned_carrier'}, axis='columns')
    firms_sub['assigned_carrier']=firms_sub['assigned_carrier'].astype(int)
    temp_FH_T_D = temp_FH_T_D.merge(firms_sub, on='assigned_carrier', how='left').reset_index()
    num =0    
    for i in range(0, temp_FH_T_D.shape[0]):
        temp_FH_T_D.loc[i,"new_id"]=str(temp_FH_T_D.loc[i,"assigned_carrier"])+ "_"+str(num)
        num +=1
    B2BF_FH=B2BF_FH.merge(temp_FH_T_D[["new_id",'assigned_carrier','outbound_index']], on=['assigned_carrier','outbound_index'], how="left")
    temp = pd.DataFrame(columns = ['carrier_id',
    'firm_id',
    'depot_zone',
    'contract_firms',
    'depot_lower',
    'depot_upper',
    'depot_time_before',
    'depot_time_after',
    'c_x','c_y']+ output_veh_list +["ev_type"])

    temp['carrier_id']=temp_FH_T_D['new_id'].apply(lambda x: 'B2B_'+str(x))
    temp['firm_id']=temp_FH_T_D['new_id'].apply(lambda x: 'B2B_'+str(x))
    temp['depot_zone']=temp_FH_T_D.apply(lambda x: ex_seller_zone_to_boundary(x['MESOZONE'], x['inbound_index'], ex_zone), axis=1)
    temp['contract_firms']=temp_FH_T_D['contract_firms']
    temp['depot_lower']= temp_FH_T_D.apply(lambda x: depot_time_depart(x['MESOZONE'],df_dpt_dist,ship_type) if x['inbound_index']==0 else time_normal(5, 3, 1,11), axis=1)
    temp['depot_upper']= temp_FH_T_D['outbound_index'].apply(lambda x: 2*24*60 if x ==1 else time_normal(24, 3, 21,28))
    temp['depot_time_before']= [random.randrange(5,40, 5) for j in temp.index]
    temp['depot_time_after']= [random.randrange(5,40, 5) for j in temp.index]
    temp['c_x'], temp['c_y'] =zip(*temp_FH_T_D.apply(lambda x: ex_coordinate(x['x'],x['y'], x['MESOZONE'], x['inbound_index'], ex_zone), axis=1))
    for i in range(0,len(output_veh_list)):
        if "md" in output_veh_list[0]:
            temp[output_veh_list[i]]=temp_FH_T_D[input_veh_list[i]].apply(lambda x: x+5)
        else:    
            temp[output_veh_list[i]]=temp_FH_T_D[input_veh_list[i]].apply(lambda x: x+5)
    temp["ev_type"] = temp_FH_T_D[input_veh_list[-1]] 

    carriers=pd.concat([carriers, temp], ignore_index=True)

        
    payloads = pd.DataFrame(columns = ['payload_id', 
    'carrier_id',
    'sequence_id',
    'tour_id',
    'commodity',
    'weight',
    'job',
    'pu_zone',
    'del_zone',
    'pu_stop_duration',
    'del_stop_duration',
    'pu_tw_lower',
    'pu_tw_upper',
    'del_tw_lower',
    'del_tw_upper',
    'pu_arrival_time',
    'del_arrival_time',
    'veh_type',
    'del_x',
    'del_y',
    'pu_x',
    'pu_y',
    'ship_index'])
    payloads['payload_id']= B2BF_PV['payload_id']
    payloads['carrier_id']= B2BF_PV['Bus_ID'].apply(lambda x: 'B2B_'+str(x))
    payloads['commodity']=B2BF_PV['SCTG_Group']
    payloads['weight']=B2BF_PV['D_truckload']
    payloads['job']= 'delivery'
    payloads['del_zone']=B2BF_PV.apply(lambda x: ex_seller_zone_to_boundary(x['BuyerZone'], x['outbound_index'], ex_zone), axis=1)
    load_min =B2BF_PV.D_truckload.min()
    load_max = B2BF_PV.D_truckload.max()
    payloads['del_stop_duration']=B2BF_PV.apply(lambda x: int(np.random.gamma(2, 1, 1)[0]*((x['D_truckload'] -load_min)/(load_max-load_min))*120) if x['outbound_index'] ==0 else 60*10, axis=1)
    payloads['del_stop_duration'] =payloads['del_stop_duration'].apply(lambda x: random.randint(5,20) if x <5 else x)  
    payloads['del_tw_lower']=1
    payloads['del_tw_lower']=payloads['del_tw_lower'].apply(lambda x: x*time_normal(7, 3, 5,11))
    payloads['del_tw_upper']=B2BF_PV['outbound_index'].apply(lambda x:(24+4)*60 if x ==1 else 24*60) 
    payloads['veh_type']=B2BF_PV['veh_type']
    payloads['del_x'],payloads['del_y']=zip(*B2BF_PV.apply(lambda x: ex_coordinate(x['del_x'],x['del_y'], x['BuyerZone'], x['outbound_index'], ex_zone), axis=1)) 
    payloads['ship_index']= B2BF_PV['outbound_index'].apply(lambda x:"external" if x ==1 else "internal")
    
    payloads_FH = pd.DataFrame(columns = ['payload_id', 
    'carrier_id',
    'sequence_id',
    'tour_id',
    'commodity',
    'weight',
    'job',
    'pu_zone',
    'del_zone',
    'pu_stop_duration',
    'del_stop_duration',
    'pu_tw_lower',
    'pu_tw_upper',
    'del_tw_lower',
    'del_tw_upper',
    'pu_arrival_time',
    'del_arrival_time',
    'veh_type',
    'del_x',
    'del_y',
    'pu_x',
    'pu_y',
    'ship_index'])

    payloads_FH['payload_id']= B2BF_FH['payload_id']
    payloads_FH['carrier_id']= B2BF_FH['new_id'].apply(lambda x: 'B2B_'+str(x))
    payloads_FH['commodity']=B2BF_FH['SCTG_Group']
    payloads_FH['weight']=B2BF_FH['D_truckload']
    payloads_FH['job']= 'pickup_delivery'
    payloads_FH['pu_zone']=B2BF_FH.apply(lambda x: ex_seller_zone_to_boundary(x['SellerZone'], x['inbound_index'], ex_zone), axis=1)
    payloads_FH['del_zone']=B2BF_FH.apply(lambda x: ex_seller_zone_to_boundary(x['BuyerZone'], x['outbound_index'], ex_zone), axis=1)
    load_min =B2BF_FH.D_truckload.min()
    load_max = B2BF_FH.D_truckload.max()
    payloads_FH['pu_stop_duration']= B2BF_FH.apply(lambda x: int(np.random.gamma(2, 1, 1)[0]*((x['D_truckload'] -load_min)/(load_max-load_min))*120), axis=1)
    payloads_FH['pu_stop_duration'] =payloads_FH['pu_stop_duration'].apply(lambda x: random.randint(5,20) if x <5 else x)   
    payloads_FH['pu_stop_duration']=payloads_FH['pu_stop_duration'].apply(lambda x: 90 if x >90 else x)
    payloads_FH['del_stop_duration']=B2BF_FH.apply(lambda x: int(np.random.gamma(2, 1, 1)[0]*((x['D_truckload'] -load_min)/(load_max-load_min))*120) if x['outbound_index'] ==0 else 60*10, axis=1)
    payloads_FH['del_stop_duration'] =payloads_FH['del_stop_duration'].apply(lambda x: random.randint(5,20) if x <5 else x)                                           
    payloads_FH['pu_tw_lower']=B2BF_FH['inbound_index'].apply(lambda x: random.randrange(0*60,6*60, 10) if x==1 else time_normal(7, 3, 5,11))
    payloads_FH['pu_tw_upper']=B2BF_FH['inbound_index'].apply(lambda x: 24*60 if x==1 else 22*60)
    payloads_FH['del_tw_lower']=B2BF_FH['outbound_index'].apply(lambda x: random.randrange(0*60,6*60, 10) if x==1 else time_normal(8, 3, 5,12))
    payloads_FH['del_tw_upper']=B2BF_FH['outbound_index'].apply(lambda x: (24+4)*60 if x==1 else 24*60)
    payloads_FH['veh_type']=B2BF_FH['veh_type']
    payloads_FH['pu_x'],payloads_FH['pu_y'] =zip(*B2BF_FH.apply(lambda x: ex_coordinate(x['pu_x'],x['pu_y'], x['SellerZone'], x['inbound_index'], ex_zone), axis=1))
    payloads_FH['del_x'],payloads_FH['del_y']=zip(*B2BF_FH.apply(lambda x: ex_coordinate(x['del_x'],x['del_y'], x['BuyerZone'], x['outbound_index'], ex_zone), axis=1))
    payloads_FH['ship_index']= B2BF_FH['outbound_index'].apply(lambda x:"external" if x ==1 else "internal") 

    payloads=pd.concat([payloads, payloads_FH],ignore_index=True)
    ### End Create Payload file 
    ### Create Carrier file
    # temp increase vehicles 
    return payloads, carriers
    ### End Create Carrier file    
##################################################################
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
def main(args=None):
    # read input files
    parser = ArgumentParser()
    parser.add_argument("-sn", "--scenario", dest="scenario",
                    help="scenario", required=True, type=str)                
    parser.add_argument("-yt", "--analysis year", dest="target_year",
                help="20XX", required=True, type=int)                           
    parser.add_argument("-st", "--shipment type", dest="ship_type",
                        help="B2B or B2C", required=True, type=str)
    parser.add_argument("-ct", "--county", dest="sel_county",
                        help="select county; for all area run, put 9999", required=True, type=int)
    parser.add_argument("-sd", "--direction", dest="ship_direction",
                        help="select 'out', 'in', 'all' for B2B, all for B2C ", required=True, type=str)
    parser.add_argument("-rt", "--run type", dest="run_type",
                        help="select 'Test' or 'RunSim", required=True, type=str)  
    parser.add_argument("-gf", "--b2c growth", dest="growth_factor",
                        help="b2 growth 100,120,150", default=100, type=int)
    parser.add_argument("-sr", "--sample ratio", dest="sample_rate",
                        help="sampeing rate for light run 0-100", default=100, type=int)
    parser.add_argument("-dc", "--condition for daily demand generation", dest="daily_demand_creator",
                        help="Y:create new one, N: use existing one", required=True, type=str)                                                                                                        
    args = parser.parse_args()
    
    start_time=time.time()
    growth_factor=args.growth_factor
    firm_file, warehouse_file, leasing_file, stock_file =sythfirm_fleet_file(config.fdir_in_out,args.target_year, args.scenario)
    create_global_variable(config.md_cap,config.hd_cap,config.fdir_in_out ,config.state_id,config.max_tour_for_b2b, args.sample_rate)
    # Read general files including geo data, firm and trukcing population data
    if args.ship_type == "B2C":
        print("* Runing %s Distribution Channel Module with Tour type in Carrier Operation *" % args.ship_type)
        print( "** This run deals with %s-bound shipment from/to %s county for %s **" % (args.ship_direction, args.sel_county,args.ship_type))
        if args.ship_direction != "all":
            print("** You didn't select 'all' for ship direction. It doesn't matther, but don't run it multiple time for three shipdirections**")
    elif args.ship_type == "B2B":
        print("* Runing %s Distribution Channel Module with Tour type in Carrier Operation *" % args.ship_type)
        print( "** This run deals with %s-bound shipment from/to %s county for %s **" % (args.ship_direction, args.sel_county,args.ship_type))

    print ("**** Processing general data sets ****")
    firms, truckings,leasings, dist_df, CBGzone_df, df_dpt_dist, ex_zone_list, ex_zone= genral_input_files_processing(firm_file,
                                                                                     warehouse_file,
                                                                                     leasing_file,
                                                                                     stock_file,
                                                                                     args.target_year,
                                                                                     args.scenario, 
                                                                                     config.dist_file,
                                                                                     config.CBG_file, 
                                                                                     args.ship_type,
                                                                                     config.list_error_zone, 
                                                                                     config.county_list)

    # Read and generate daily shipment file
    if args.ship_type == "B2C":
        truckings_org= truckings.copy()
        sel_county= args.sel_county
        ship_type=args.ship_type 
        ship_direction=args.ship_direction
        print ("**** Start processing daily B2C shipment")
        if args.daily_demand_creator == "Y": 
            df_hh_D= b2c_input_files_processing(CBGzone_df, 
                                                config.b2c_delivery_frequency, sel_county, config.list_error_zone, growth_factor, args.target_year)

            print ("**** Completed initial daily generation and Start processing aggregation")
            # option 1
            # if sample_ratio==100:
            #     df_hh_D_GrID, id_lookup =b2c_household_aggregation (df_hh_D, CBGzone_df, config.hh_aggregation_size, sel_county, ship_type)
            # else: 
            #     df_hh_D_GrID= b2c_sampling_household (df_hh_D, sel_county,ship_type,sample_ratio)

            # option 2
            df_hh_D_GrID, id_lookup =b2c_household_aggregation (df_hh_D, CBGzone_df, config.hh_aggregation_size, sel_county, ship_type)
            if sample_ratio <100: 
                df_hh_D_GrID= b2c_sampling_household_agg (df_hh_D_GrID,sample_ratio)

            df_hh_D_GrID.to_csv(fdir_in_out+'/Sim_outputs/Generation/B2C_daily_%s.csv' %sel_county, index = False, header=True)    
        else: 
            df_hh_D_GrID= pd.read_csv(fdir_in_out+'/Sim_outputs/Generation/B2C_daily_%s.csv' %sel_county, header=0, sep=',')        
 
        df_hh_D_GrID.loc[:,'veh_type_agg'] ="md"
        df_hh_D_GrID.loc[:,'assigned_carrier']="no"
        df_hh_D_GrID=df_hh_D_GrID.reset_index(drop=True)
        # Assigned the carrirer to shipment!: 
        ## This part is time consuming which is associated to the function "carrier_sel()"
        print ("**** Complete aggregation and Starting carrier assignement ****")
        print ("size of shipment:", df_hh_D_GrID.shape[0])
        non_sel_seller=pd.DataFrame()
        if args.run_type =="Test":
            run_size=20
        elif args.run_type =="RunSim":
            run_size=df_hh_D_GrID.shape[0]
        else: 
            print ("Please put a correct run type")       
        with alive_bar(run_size, force_tty=True) as bar:
            for i in range(0,run_size): #***************** need to comment out and comment the line below *************************************
                v_type=df_hh_D_GrID.loc[i,'veh_type_agg']
                
                cap_index = v_type+"_capacity"
                time_index= v_type+"_time_cap"            
                # find a carrier who can hand a shipment at row i 
                sel_busID=carrier_sel(df_hh_D_GrID.loc[i,'MESOZONE'], df_hh_D_GrID.loc[i,'D_truckload'],
                                    df_hh_D_GrID.loc[i,'tour_tt'],cap_index,time_index, dist_df, truckings,ship_type, 0)
                # put the carrier into df
                if sel_busID == "no":
                    non_sel_seller=pd.concat([non_sel_seller,df_hh_D_GrID.iloc[[i]]], ignore_index=True).reset_index(drop=True)
                else: 
                    df_hh_D_GrID.loc[i,'assigned_carrier']=sel_busID
                    # Calculate the reduce the capacity and time capacity that can reflect after a row assignment
                    trucking_index = truckings.index[truckings["BusID"]==sel_busID].values[0]
                    truckings.loc[trucking_index,cap_index] = truckings.loc[trucking_index,cap_index] - df_hh_D_GrID.loc[i,'D_truckload']
                    truckings.loc[trucking_index,time_index] = truckings.loc[trucking_index,time_index] - df_hh_D_GrID.loc[i,'tour_tt']
                bar()
                
        print ("**** Completed carrier assignement and Generating results ****")    
        df_hh_D_GrID=df_hh_D_GrID[df_hh_D_GrID['assigned_carrier'] !="no"].reset_index(drop=True)
        df_hh_D_GrID=df_hh_D_GrID[~df_hh_D_GrID['MESOZONE'].isin(config.list_error_zone)]
        df_hh_D_GrID.to_csv(fdir_in_out+'/Sim_outputs/temp_save/df_hh_D_GrID_carrier_assigned_county%s_%s.csv' %(sel_county, args.run_type), index = False, header=True)
        # vehicle type assign
        def payload_cal (load, v_type):
            if v_type=="md":
                max_load= md_max_load
            else: 
                max_load= hd_max_load
            return load/max_load                     

        df_hh_D_GrID['payload_rate']=df_hh_D_GrID.apply(lambda x: payload_cal(x['D_truckload'],x['veh_type_agg'] ), axis=1)
        df_hh_D_GrID_new=pd.DataFrame()
        for carr_id in df_hh_D_GrID['assigned_carrier'].unique():
            temp = df_hh_D_GrID[df_hh_D_GrID['assigned_carrier'] == carr_id].reset_index()
            temp =temp.sort_values(by=['veh_type_agg', 'tour_tt'])
            temp["veh_type"]="u"
            [[md_D_num,md_E_num, hdt_D_num, hdt_E_num, hdv_D_num, hdv_E_num, ev_class]]=truckings[truckings['BusID'] == carr_id]\
                                                                                        [['Diesel Class 4-6 Vocational','Electric Class 4-6 Vocational',
                                                                                        'Diesel Class 7&8 Tractor','Electric Class 7&8 Tractor',
                                                                                        'Diesel Class 7&8 Vocational','Electric Class 7&8 Vocational',
                                                                                        'EV_powertrain (if any)']].values.tolist()
            if pd.isnull(ev_class):
                ev_class="Battery Electric"   
    
            dic_firm_stock={"md_D_num":md_D_num,
                            "md_E_num":md_E_num, 
                            "hdt_D_num":hdt_D_num, 
                            "hdt_E_num": hdt_E_num, 
                            "hdv_D_num":hdv_D_num, 
                            "hdv_E_num":hdv_E_num}
            cum_time =60*(6+1)
            cum_payload=1.1
            v_type="md"
            powerT="D"
            for j in range(0, temp.shape[0]):
                if (cum_time + temp['tour_tt'].iloc[j]  > 60*6) or  (cum_payload + temp['payload_rate'].iloc[j] >=1) or (v_type !=temp['veh_type_agg'].iloc[j]):
                    cum_time =0
                    cum_payload=0
                    dic_firm_stock[v_type+"_"+powerT+"_num"] = int (dic_firm_stock[v_type+"_"+powerT+"_num"])
                    v_type= temp['veh_type_agg'].iloc[j]
                    D_num_firm = dic_firm_stock[v_type+"_D_num"]
                    E_num_firm = dic_firm_stock[v_type+"_E_num"]
                    if D_num_firm -temp['payload_rate'].iloc[j] <0:
                        D_num_firm =0 
                    if E_num_firm -temp['payload_rate'].iloc[j] <0:
                        E_num_firm =0 
                    if D_num_firm+E_num_firm -temp['payload_rate'].iloc[j] <0:
                        D_num_firm=1
                        E_num_firm=1                 
                    powerT=util_powertrain(D_num_firm, E_num_firm, dic_energy, 50, dic_veh[v_type], ev_class, 0.5)
                    dic_firm_stock[v_type+"_"+powerT+"_num"] = dic_firm_stock[v_type+"_"+powerT+"_num"]-temp['payload_rate'].iloc[j]
                    if powerT == "D":
                        p_lable="Diesel"
                    else:
                        p_lable=ev_class          
                    temp["veh_type"].iloc[j]=v_type+"_"+powerT+"_"+p_lable
                    cum_time =cum_time + temp['tour_tt'].iloc[j]
                    cum_payload=cum_payload + temp['payload_rate'].iloc[j]
                else:
                    dic_firm_stock[v_type+"_"+powerT+"_num"] = dic_firm_stock[v_type+"_"+powerT+"_num"]-temp['payload_rate'].iloc[j]
                    if powerT == "D":
                        p_lable="Diesel"
                    else:
                        p_lable=ev_class          
                    temp["veh_type"].iloc[j]=v_type+"_"+powerT+"_"+p_lable
                    cum_time =cum_time + temp['tour_tt'].iloc[j]
                    cum_payload=cum_payload + temp['payload_rate'].iloc[j]   
            df_hh_D_GrID_new=pd.concat([df_hh_D_GrID_new,temp], ignore_index=True).reset_index(drop=True)
        ########################## end if-caluse if needed ###################    
        # x_y assignment
        df_hh_D_GrID_new=df_hh_D_GrID_new.reset_index(drop=True)
        df_hh_D_GrID_new['del_x']=0
        df_hh_D_GrID_new['del_y']=0
        print ("**xy allocation job size:", df_hh_D_GrID_new.shape[0])
        with alive_bar(df_hh_D_GrID_new.shape[0], force_tty=True) as bar:
            for i in range(0,df_hh_D_GrID_new.shape[0]):
                [x,y]=random_points_in_polygon(CBGzone_df.geometry[CBGzone_df.MESOZONE==df_hh_D_GrID_new.loc[i,"MESOZONE"]])
                df_hh_D_GrID_new.loc[i,'del_x']=x
                df_hh_D_GrID_new.loc[i,'del_y']=y
                bar()
        df_hh_D_GrID_new.to_csv(fdir_in_out+'/Sim_outputs/temp_save/xydf_hh_D_GrID_carrier_assigned_county%s.csv' %sel_county, index = False, header=True)
        

        payloads, carriers=b2c_create_output(df_hh_D_GrID_new,truckings_org,df_dpt_dist, ship_type)
        if not file_exists(config.fdir_main_output + str(args.target_year)+"/"):
            os.makedirs(config.fdir_main_output + str(args.target_year)+"/")
        dir_out= config.fdir_main_output + str(args.target_year)+"/"   
        payloads.to_csv (dir_out+config.fnm_B2C_payload+"_county{}_ship{}_s{}_y{}_sr{}.csv".format(sel_county, ship_direction,args.scenario, args.target_year,sample_ratio), index = False, header=True)
        carriers.to_csv (dir_out+config.fnm_B2C_carrier+"_county{}_ship{}_s{}_y{}_sr{}.csv".format(sel_county, ship_direction,args.scenario, args.target_year,sample_ratio), index = False, header=True)
        

        print ("**** Completed generating B2C payload/carrier file ****")

    elif args.ship_type == "B2B":    
        print ("**** Start processing daily B2B shipment")
        truckings_org= truckings.copy()
        df_vius= pd.read_csv(fdir_in_out+"/Model_carrier_op/VIUS/vehicle_proportion_by_sctg_dist.csv", header=0, sep=',')
        FH_B2B, PV_B2B, firms = b2b_input_files_processing(firms,leasings,truckings,dist_df, CBGzone_df, args.sel_county, args.ship_direction, 
        config.commodity_list, config.weight_theshold, config.list_error_zone,config.county_list,df_vius, config.b2b_day_factor, 
        args.target_year, args.scenario, args.daily_demand_creator)
        FH_B2B.to_csv(fdir_in_out+'/Sim_outputs/temp_save/FH_B2B_county%s_ship%s.csv' %(args.sel_county, args.ship_direction), index = False, header=True)
        PV_B2B.to_csv(fdir_in_out+'/Sim_outputs/temp_save/PV_B2B_county%s_ship%s.csv' %(args.sel_county, args.ship_direction), index = False, header=True)
        firms.to_csv(fdir_in_out+'/Sim_outputs/temp_save/B2B_firms%s_ship%s.csv' %(args.sel_county, args.ship_direction), index = False, header=True)

        PV_B2B=PV_B2B[PV_B2B["D_truckload"]>0].reset_index(drop=True)
        FH_B2B=FH_B2B[FH_B2B["D_truckload"]>0].reset_index(drop=True)
        FH_B2B=FH_B2B.dropna(subset=["assigned_carrier"]).reset_index(drop=True)
        PV_B2B['payload_id']=PV_B2B.index
        FH_B2B['payload_id']=FH_B2B.index + PV_B2B.shape[0]
        PV_B2B['payload_id']=PV_B2B['payload_id'].apply(lambda x: str(args.sel_county) + '_' + args.ship_type + str(int(x)))
        FH_B2B['payload_id']=FH_B2B['payload_id'].apply(lambda x: str(args.sel_county) + '_' + args.ship_type + str(int(x)))
        id_lookup=pd.concat([PV_B2B[['payload_id','shipment_id']],FH_B2B[['payload_id','shipment_id']]], ignore_index=True)       
        # Assing x_y
        PV_B2B=PV_B2B.merge(firms[['SellerID','x','y']], on="SellerID", how="left")
        PV_B2B.rename({'x': 'pu_x','y': 'pu_y'},axis=1, inplace=True)

        PV_B2B=PV_B2B.merge(firms[['SellerID','x','y']].set_index('SellerID'), left_on="BuyerID", right_index=True, how="left")
        PV_B2B.rename({'x': 'del_x','y': 'del_y'},axis=1, inplace=True)
        FH_B2B=FH_B2B.merge(firms[['SellerID','x','y']], on="SellerID", how="left")
        FH_B2B.rename({'x': 'pu_x','y': 'pu_y'},axis=1, inplace=True)
        FH_B2B=FH_B2B.merge(firms[['SellerID','x','y']].set_index('SellerID'), left_on="BuyerID", right_index=True, how="left")
        FH_B2B.rename({'x': 'del_x','y': 'del_y'},axis=1, inplace=True)

        PV_B2B['inbound_index']=PV_B2B['SellerCounty'].apply(lambda x: 0 if x in config.county_list else 1)
        FH_B2B['inbound_index']=FH_B2B['SellerCounty'].apply(lambda x: 0 if x in config.county_list else 1)
        truckings_org['inbound_index']=truckings_org['County'].apply(lambda x: 0 if x in config.county_list else 1)
        PV_B2B['outbound_index']=PV_B2B['BuyerCounty'].apply(lambda x: 0 if x in config.county_list else 1)
        FH_B2B['outbound_index']=FH_B2B['BuyerCounty'].apply(lambda x: 0 if x in config.county_list else 1)

        FH_B2B.to_csv(fdir_in_out+'/Sim_outputs/temp_save/FH_B2B_carrier_assigned_county%s_ship%s.csv' %(args.sel_county, args.ship_direction), index = False, header=True)
        PV_B2B = PV_B2B.sort_values(by=['SellerID', 'SCTG_Group']).reset_index(drop=True)
        FH_B2B= FH_B2B.sort_values(by=['SellerID', 'SCTG_Group']).reset_index(drop=True)
        truckings_org["BusID"]=truckings_org["BusID"].astype('int')
        FH_B2B["assigned_carrier"]=FH_B2B["assigned_carrier"].astype('int')
        # create payload and carriers
        payloads, carriers=b2b_create_output(PV_B2B,FH_B2B,truckings_org,df_dpt_dist, args.ship_type, ex_zone_list, firms, ex_zone)
        print ("**** Completed generating B2C payload/carrier file ****")
  
        new_payloads=pd.DataFrame()
        new_carriers=pd.DataFrame()
        for c_id in carriers["carrier_id"].unique():
            for v_type in output_veh_list:
                temp_pay = payloads[(payloads["carrier_id"]==c_id) & (payloads["veh_type"].str.contains(v_type))].reset_index(drop=True)
                temp_carr = carriers[carriers["carrier_id"]==c_id].reset_index(drop=True)
                num=temp_pay.shape[0]
                if num ==0:
                    temp_carr = pd.DataFrame()
                elif num <= 20 and num >0:
                    new_c_id=c_id+v_type
                    temp_pay["carrier_id"] = new_c_id
                    temp_carr["carrier_id"] = new_c_id
                else: 
                    for i in range(0,temp_pay.shape[0]):
                        new_c_id=c_id+v_type+"_{}".format(str(int(i/20)))
                        temp_pay.loc[i,"carrier_id"] = new_c_id
                    break_num=int(num/20)+1
                    temp_carr=pd.concat([temp_carr]*break_num, ignore_index=True).reset_index(drop=True)
                    for i in range(0,temp_carr.shape[0]):
                        new_c_id=c_id+v_type+"_{}".format(str(i))
                        temp_carr.loc[i,"carrier_id"] = new_c_id

                new_payloads=pd.concat([new_payloads,temp_pay], ignore_index=True).reset_index(drop=True)
                new_carriers=pd.concat([new_carriers,temp_carr], ignore_index=True).reset_index(drop=True) 

        # print ("missing x,y locations")
        with alive_bar(new_payloads.shape[0], force_tty=True) as bar:
            for i in range(0,new_payloads.shape[0]):
                if new_payloads.loc[i,"job"] =="delivery":
                    if pd.isnull(new_payloads.loc[i,"del_x"]):
                        [x,y]=random_points_in_polygon(CBGzone_df.geometry[CBGzone_df.MESOZONE==new_payloads.loc[i,"del_zone"]])
                        new_payloads.loc[i,'del_x']=x
                        new_payloads.loc[i,'del_y']=y 
                elif new_payloads.loc[i,"job"] =="pickup_delivery":
                    if pd.isnull(new_payloads.loc[i,"del_x"]):
                        [x,y]=random_points_in_polygon(CBGzone_df.geometry[CBGzone_df.MESOZONE==new_payloads.loc[i,"del_zone"]])
                        new_payloads.loc[i,'del_x']=x
                        new_payloads.loc[i,'del_y']=y
                    if pd.isnull(new_payloads.loc[i,"pu_x"]):
                        [x,y]=random_points_in_polygon(CBGzone_df.geometry[CBGzone_df.MESOZONE==new_payloads.loc[i,"pu_zone"]])
                        new_payloads.loc[i,'pu_x']=x
                        new_payloads.loc[i,'pu_y']=y      
                bar()

        file_num=10
        if not file_exists(config.fdir_main_output + str(args.target_year)+"/"):
            os.makedirs(config.fdir_main_output + str(args.target_year)+"/")
        dir_out= config.fdir_main_output + str(args.target_year)+"/" 
        new_carriers.to_csv(dir_out+config.fnm_B2B_carrier+"_county{}_ship{}_A_s{}_y{}_sr{}.csv".format(args.sel_county, args.ship_direction,args.scenario, args.target_year,sample_ratio), index = False, header=True)
        new_payloads.to_csv(dir_out+config.fnm_B2B_payload+"_county{}_ship{}_A_s{}_y{}_sr{}.csv".format(args.sel_county, args.ship_direction,args.scenario, args.target_year,sample_ratio), index = False, header=True)
        carrier_list=new_payloads["carrier_id"].unique()
        
    vehicle_types = veh_type_create()
    vehicle_types.to_csv (dir_out+config.fnm_vtype+"_s{}_y{}.csv".format(args.scenario,args.target_year), index = False, header=True)

    print ("Run time of %s: %s seconds" %(args.ship_type, time.time()-start_time))    


if __name__ == "__main__":
    main()
# %%
