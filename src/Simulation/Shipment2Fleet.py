## Note: To test the codes: In def main(), put for loop is restricted:
### please comment out the followings for the entire run. 
### if args.ship_type == "B2C": ... #for i in range(0,df_hh_D_GrID.shape[0]):
### elif args.ship_type == "B2B": ...#for i in range(0,FH_Seller.shape[0]): 

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

def create_global_variable():
    global md_max_load
    global hd_max_load
    md_max_load= 11000
    hd_max_load= 40000
######################### General CODES ############################
def genral_input_files_processing(firm_file, warehouse_file, dist_file,CBG_file, ship_type):
    # firm and warehouse(for-hire carrier)
    fdir_firms='../../../FRISM_input_output/Sim_inputs/Synth_firm_pop/'
    firms= pd.read_csv(fdir_firms+firm_file, header=0, sep=',')
    firms=firms.rename({'BusID':'SellerID'}, axis='columns')
    warehouses= pd.read_csv(fdir_firms+warehouse_file, header=0, sep=',')
    ## Seperate B2B and B2C trucking: Currently use NAICS code for this process; need to update later
    if ship_type == 'B2C':
        truckings=warehouses[warehouses['Industry_NAICS6_Make']=="492000"].reset_index()
        truckings['md_veh']=truckings['md_veh']+truckings['hd_veh'] # temporary solution since lack of md in delivery trucking 
        truckings['hd_veh']=0
        truckings['md_capacity']=truckings['md_veh'].apply(lambda x: x *md_max_load)
        truckings['hd_capacity']=truckings['hd_veh'].apply(lambda x: x *hd_max_load)
        truckings['time_cap'] = truckings['md_veh'].apply(lambda x: x * 60*5)       
    elif ship_type == 'B2B':
        truckings=warehouses[warehouses['Industry_NAICS6_Make']=="484000"].reset_index()
        truckings['md_capacity']=truckings['md_veh'].apply(lambda x: x *md_max_load)
        truckings['hd_capacity']=truckings['hd_veh'].apply(lambda x: x *hd_max_load)
        truckings['time_cap'] = truckings.apply(lambda x: (x['md_veh'] + x['hd_veh'])* 60*8, axis=1) 
    else:
        print ("Please define shipment type: B2B or B2C")

    # Geo data including distance, CBGzone,
    fdir_geo='../../../FRISM_input_output/Sim_inputs/Geo_data/'

    dist_df=pd.read_csv(fdir_geo+dist_file, header=0, sep=',')
    CBGzone_df = gpd.read_file(fdir_geo+CBG_file) # file include, GEOID(12digit), MESOZONE, area
    CBGzone_df=CBGzone_df[['GEOID','CBPZONE','MESOZONE','area']]
    CBGzone_df["GEOID"]=CBGzone_df["GEOID"].astype(str)
    ## Add county id from GEOID
    CBGzone_df["County"]=CBGzone_df["GEOID"].apply(lambda x: x[2:5] if len(x)>=12 else 0)
    CBGzone_df["County"]=CBGzone_df["County"].astype(str).astype(int)
    CBGzone_df["GEOID"]=CBGzone_df["GEOID"].astype(str).astype(int)

    # externalZone
    ex_zone= pd.read_csv(fdir_geo+"External_Zones_Mapping.csv")
    ex_zone_list=list(ex_zone["MESOZONE"].unique())


    # Truck activity distribution
    fdir_truck='../../../FRISM_input_output/Model_carrier_op/INRIX_processing/'
    if ship_type == 'B2C':
        df_dpt_dist=pd.read_csv(fdir_truck+'depature_dist_by_cbg_MD.csv', header=0, sep=',')
    elif ship_type == 'B2B':
        df_dpt_dist=pd.read_csv(fdir_truck+'depature_dist_by_cbg_HD.csv', header=0, sep=',')
    else:
        print ("Please define shipment type: B2B or B2C")
    df_dpt_dist=df_dpt_dist.merge(CBGzone_df[["GEOID",'MESOZONE']], left_on="cbg_id", right_on="GEOID", how='left')    

    return firms, truckings,dist_df, CBGzone_df, df_dpt_dist, ex_zone_list        

###  Calculate distance between two meso zone: currenlty Euclidian dist
#####  Update requried: Need to get network distance? -> please update "dist_df=pd.read_csv(...)""  
def dist_cal(org_meso, dest_meso, dist_df):
    dist = dist_df[(dist_df['Origin']==org_meso) & (dist_df['Destination']==dest_meso)].dist.values[0]
    if (dist == 0):
        dist =random.uniform(1,10)
    return dist

### new version
### Assign the carrier s.t.: 
### 1. distance with capacity 
### 2. select a carrier from the candidate list with distance weighted probability 
def carrier_sel(SellerZone, D_truckload, tt_time, veh_type, dist_df, truckings):
    if veh_type == "md":
        cap_index = "md_capacity"
    elif veh_type == "hd":
        cap_index ="hd_capacity"
    sel_dist_df = dist_df[(dist_df.Origin==SellerZone) & (dist_df.dist<25)]
    candidate_busid= truckings[(truckings['MESOZONE'].isin(sel_dist_df.Destination.unique())) &
                               (truckings[cap_index] >=D_truckload) &  
                               (truckings['time_cap'] >=tt_time)][['BusID','MESOZONE']] 
    
    if (candidate_busid.shape[0]  < 5):
        sel_dist_df = dist_df[(dist_df.Origin==SellerZone) & (dist_df.dist<50)]
        candidate_busid= truckings[(truckings['MESOZONE'].isin(sel_dist_df.Destination.unique())) &
                               (truckings[cap_index] >=D_truckload) &  
                               (truckings['time_cap'] >=tt_time)][['BusID','MESOZONE']] 
    if (candidate_busid.shape[0]  < 5):
        sel_dist_df = dist_df[(dist_df.Origin==SellerZone) & (dist_df.dist<100)]
        candidate_busid= truckings[(truckings['MESOZONE'].isin(sel_dist_df.Destination.unique())) & 
                               (truckings[cap_index] >=D_truckload) &  
                               (truckings['time_cap'] >=tt_time)][['BusID','MESOZONE']] 
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
        sel_busID =-1
    return sel_busID

def depot_time_depart(zone_id,df_dpt_dist,ship_type):
    if ship_type == 'B2C':     
        try:
            df_temp = df_dpt_dist[df_dpt_dist['MESOZONE']==zone_id].reset_index()
            df_temp['cdf_low']=0.0
            df_temp['cdf_up']=0.0
            for i in range(1,df_temp.shape[0]):
                df_temp.loc[i,'cdf_up']=df_temp.loc[i-1,'cdf_up']+df_temp.loc[i,'Trip_pdf']
                df_temp.loc[i,'cdf_low']=df_temp.loc[i-1,'cdf_up']
            pro_time= random.uniform(0, 0.9999999)    
            d_time=df_temp[(df_temp['cdf_low']<= pro_time) & (df_temp['cdf_up'] >  pro_time)]['start_hour'].values[0]
            d_time=random.randrange(d_time*60, (d_time+1)*60, 10)
            if d_time >16*60:
                d_time =random.randrange(14*60, 15*60, 10)
        except:
            d_time= random.randrange(7*60, 15*60, 10)
    elif ship_type == 'B2B':
        try:
            df_temp = df_dpt_dist[df_dpt_dist['MESOZONE']==zone_id].reset_index()
            df_temp['cdf_low']=0.0
            df_temp['cdf_up']=0.0
            for i in range(1,df_temp.shape[0]):
                df_temp.loc[i,'cdf_up']=df_temp.loc[i-1,'cdf_up']+df_temp.loc[i,'Trip_pdf']
                df_temp.loc[i,'cdf_low']=df_temp.loc[i-1,'cdf_up']
            pro_time= random.uniform(0, 0.9999999)    
            d_time=df_temp[(df_temp['cdf_low']<= pro_time) & (df_temp['cdf_up'] >  pro_time)]['start_hour'].values[0]
            d_time=random.randrange(d_time*60, (d_time+1)*60, 10)
        except:
            d_time= random.randrange(7*60, 14*60, 10)
        if d_time >16*60:
            d_time = d_time - random.randrange(8*60, 12*60, 10)
    else:
        print ("Please define shipment type: B2B or B2C")        
    return d_time   

def depot_time_close(d_time):
    c_time = d_time+3*60
    if c_time >=22*60: 
        c_time = 22*60
    elif c_time >= 17*60 and c_time <20*60:
        c_time= random.randrange(c_time, 24*60, 30)
    else:     
        c_time=random.randrange(17*60, 22*60, 30)
    return c_time

def veh_type_create():
    vehicle_types= pd.DataFrame(columns = ['veh_type_id',
    'veh_category',
    'veh_class',
    'body_type',
    'commodities',
    'weight', 
    'length',
    'payload_capacity_weight',
    'payload_capacity_cbf',
    'max_speed',
    'primary_fuel_type',
    'secondary_fuel_type',
    'primary_fuel_rate',
    'secondary_fuel_rate',
    'Automation level',
    'monetary cost'])

    MD= pd.DataFrame(data={'veh_type_id': [1],
    'veh_category': ['MD'],
    'veh_class':['NA'],
    'body_type':['NA'],
    'commodities':[[1,2,3,4,5]],
    'weight':[10000], 
    'length':['NA'],
    'payload_capacity_weight':[15000],
    'payload_capacity_cbf':['NA'],
    'max_speed':['NA'],
    'primary_fuel_type':['NA'],
    'secondary_fuel_type':['NA'],
    'primary_fuel_rate':['NA'],
    'secondary_fuel_rate':['NA'],
    'Automation level':['NA'],
    'monetary cost':['NA']})   

    HD= pd.DataFrame(data={'veh_type_id': [2],
    'veh_category': ['HD'],
    'veh_class':['NA'],
    'body_type':['NA'],
    'commodities':[[1,2,3,4,5]],
    'weight':[26000], 
    'length':['NA'],
    'payload_capacity_weight':[50000],
    'payload_capacity_cbf':['NA'],
    'max_speed':['NA'],
    'primary_fuel_type':['NA'],
    'secondary_fuel_type':['NA'],
    'primary_fuel_rate':['NA'],
    'secondary_fuel_rate':['NA'],
    'Automation level':['NA'],
    'monetary cost':['NA']})
                    
    vehicle_types=vehicle_types.append(MD)
    vehicle_types=vehicle_types.append(HD)

    return vehicle_types

###################################################################

########################### B2C CODES #############################
def b2c_input_files_processing(CBGzone_df, possilbe_delivey_days, sel_county):
    # read household delivery file from 
    df_hh = pd.read_csv('../../../FRISM_input_output/Sim_outputs/Generation/households_del.csv', header=0, sep=',')
    df_hh= df_hh[['household_id','delivery_f', 'block_id']]
    df_hh['GEOID'] =df_hh['block_id'].apply(lambda x: np.floor(x/1000))
    df_hh = df_hh.merge(CBGzone_df[['GEOID','MESOZONE','County']], on='GEOID', how='left')
    # select data in a county
    if sel_county != 9999:
        df_hh= df_hh[df_hh['County']==sel_county]
    df_hh = df_hh.reset_index()
    df_hh[['D_selection', 'D_packages']] = df_hh['delivery_f'].apply(lambda x: b2c_d_select(x, possilbe_delivey_days)).to_list()
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
    # Generate load in "lb"
    df_hh_D["D_truckload"]=df_hh_D["D_packages"].apply(b2c_d_truckload)
    # Save daily household having shipments and sum of load 
    df_hh_D.to_csv ('../../../FRISM_input_output/Sim_outputs/Generation/B2C_daily_%s.csv' %sel_county, index = False, header=True)
    return df_hh_D

def b2c_household_aggregation (df_hh_D, zone_df,hh_aggregation_num):
    
    df_hh_D_Group_hhcount=df_hh_D.groupby(['MESOZONE'])['household_id'].count().reset_index(name='num_hh')
    # Calculate how many shipments-households in a CBG
    df_hh_D_Group_hhcount['group_size']=df_hh_D_Group_hhcount['num_hh'].apply(lambda x: int(x/hh_aggregation_num)+1)
    # Assign the aggregate household_id 
    df_hh_D['household_gr_id']=df_hh_D['MESOZONE'].apply(lambda x: b2c_hh_group_id_gen (df_hh_D_Group_hhcount,x))
    df_hh_D_GrID= df_hh_D.groupby(['household_gr_id', 'MESOZONE'])['D_truckload'].agg(D_truckload='sum', num_hh='count').reset_index()
    ##df_hh_D_GrID['MESOZONE']=df_hh_D_GrID['household_gr_id'].apply(lambda x: int(x/100))
    df_hh_D_GrID=df_hh_D_GrID.merge(df_hh_D_Group_hhcount[['MESOZONE','group_size']], on='MESOZONE', how='left')
    # Create approximate tour travel time to serve aggregated household-shipments
    df_hh_D_GrID['tour_tt']=df_hh_D_GrID.apply(lambda x: b2c_apro_tour_time(x['MESOZONE'], x['num_hh'], x['group_size'],hh_aggregation_num,zone_df), axis=1)
    print ("A total of aggregated B2C shipments:", df_hh_D_GrID.shape[0])

    df_hh_D_GrID.to_csv ('../../../FRISM_input_output/Sim_outputs/Generation/B2C_daily_aggregation.csv', index = False, header=True)
    df_hh_D_GrID= df_hh_D_GrID.reset_index()
    return df_hh_D_GrID

# function for B2C delivery selection and number of packages for a day 
def b2c_d_select (delivery_f, fq_factor):
    # maximum delivery in the data set
    # fq_factor is the number of possible delivery days in a month: 20 days, 25 days, 30 days..
    pro=delivery_f/fq_factor
    if pro >=1:
        num_package=round(np.random.gamma(pro*0.8, 1)) # using gamma distribution assinge the number of delivery
        if num_package == 0:
            select =0
        else:
            select =1 
    else:
        r= random.uniform(0,1)
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
def b2c_hh_group_id_gen (df,MESOZONE):
    group_size = df[df['MESOZONE']==MESOZONE]['group_size'].values[0]
    group_num= MESOZONE*100+random.randint(1,group_size)
    return group_num
# B2C travel time and operation time generation, which is used for operational time  
def b2c_apro_tour_time(zone, num_visit,size, hh_aggregation_num, zone_df):
    try:
        if num_visit >1:
            area= zone_df[zone_df['MESOZONE']==zone]['area'].values[0]
            time = int(0.57*np.sqrt(area/size*num_visit*100)/15*60+0.5)
            if time > hh_aggregation_num*6: # 6 minutes thresholds
                time = int(num_visit * 6) # 6 minutes thresholds
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
    'veh_type'])

    payloads['payload_id']= np.arange(df_del.shape[0])
    payloads['carrier_id']= df_del['assigned_carrier']
    #payloads['sequence_id']=
    #payloads['tour_id']=
    payloads['commodity']=5
    payloads['weight']=df_del['D_truckload']
    payloads['job']= 'delivery'
    #payloads['pu_zone']=
    payloads['del_zone']=df_del['MESOZONE']
    #payloads['pu_stop_duration']=
    ## need to fix this distribution
    payloads['del_stop_duration'] =df_del['tour_tt']
    #payloads['del_stop_duration'] =
    #payloads['pu_tw_lower']=
    #payloads['pu_tw_upper']=
    payloads['del_tw_lower']=60*6
    payloads['del_tw_upper']=60*20
    #payloads['pu_arrival_time']=
    #payloads['del_arrival_time']=
    payloads['veh_type']=df_del['veh_type']  
    ### End Create Payload file
    
    # Create carrier files 
    carriers = pd.DataFrame(columns = ['carrier_id',
    'firm_id',
    'depot_zone',
    'contract_firms',
    'num_veh_type_1',
    'num_veh_type_2',
    'num_veh_type_3',
    'num_veh_type_4',
    'num_veh_type_5',
    'num_veh_type_6',
    'num_veh_type_7',
    'num_veh_type_8',
    'num_veh_type_9'])

    truckings=truckings.rename(columns={'BusID': 'assigned_carrier'})

    #truckings['hd_veh']=0

    carrier_input=pd.DataFrame(df_del.assigned_carrier.unique(), columns=['assigned_carrier'])

    carrier_input=carrier_input.merge(truckings[['assigned_carrier','md_veh','hd_veh','MESOZONE']], on = 'assigned_carrier', how='left')

    carriers['carrier_id']=carrier_input['assigned_carrier']
    carriers['firm_id']=carrier_input['assigned_carrier']
    carriers['depot_zone']=carrier_input['MESOZONE']
    carriers['contract_firms']='Nan'
    carriers['num_veh_type_1']=carrier_input['md_veh']
    carriers['num_veh_type_2']=carrier_input['hd_veh']
    carriers['depot_lower']= carriers['depot_zone'].apply(lambda x: depot_time_depart(x,df_dpt_dist,ship_type))
    carriers['depot_upper']= carriers['depot_lower'].apply(depot_time_close)
    carriers['depot_time_before']= [random.randrange(0,30, 5) for j in carriers.index]
    carriers['depot_time_after']= [random.randrange(0,30, 5) for j in carriers.index]
    ### End Create Carrier file
    return payloads, carriers
##################################################################

########################### B2B CODES ############################
# c1: bulk, c2:fuel_fert, c3:interm_food, c4:mfr_goods, c5:others 
def b2b_input_files_processing(firms,CBGzone_df, sel_county, ship_direction, commodity_list, weight_theshold):
    # read household delivery file from
    fdir_synth_firm='../../../FRISM_input_output/Sim_inputs/Synth_firm_results/'
    B2BF_T_D=pd.DataFrame()
    for com in commodity_list:
        B2BF_C =  b2b_d_shipment_by_commodity(fdir_synth_firm,com, weight_theshold,CBGzone_df,sel_county,ship_direction)
        B2BF_T_D=pd.concat([B2BF_T_D,B2BF_C],ignore_index=True)         
    B2BF_T_D.to_csv('../../../FRISM_input_output/Sim_outputs/Generation/B2B_daily_%s.csv' %sel_county, index = False, header=True)
    

    ## Deal with the daily shipment seperately
    ## For-hire Truck: FH_B2B
    ## Private Truck: PV_B2B
    FH_B2B= B2BF_T_D[B2BF_T_D['mode_choice']=="For-hire Truck"].reset_index(drop=True)
    PV_B2B= B2BF_T_D[B2BF_T_D['mode_choice']=="Private Truck"].reset_index(drop=True)

    firms=firms[firms["SellerID"].isin(PV_B2B["SellerID"])].reset_index(drop=True)
    firms["md_capacity"]=firms["md_veh"]*md_max_load
    firms["hd_capacity"]=firms["hd_veh"]*hd_max_load

    firms_temp=firms.copy()

    # Assign MD_truck load and HD_truck_load
    for i in range(0, PV_B2B.shape[0]):
        firm_index=firms_temp.index[firms_temp["SellerID"]==PV_B2B.loc[i,"SellerID"]].values[0]
        [md_cap, hd_cap]=firms_temp.loc[firm_index,["md_capacity","hd_capacity"]].values.tolist()
        md_load,hd_load=b2b_veh_type_truckload(PV_B2B.loc[i,"SCTG_Group"],PV_B2B.loc[i,"Distance"], PV_B2B.loc[i,"D_truckload"], md_cap, hd_cap)
        PV_B2B.loc[i,["md_truckload","hd_truckload"]]=[md_load,hd_load]
        firms_temp.loc[firm_index,["md_capacity","hd_capacity"]]=[md_cap-md_load,hd_cap-hd_load]

    for i in range(0, FH_B2B.shape[0]):
        [md_cap, hd_cap]=[100000000,100000000]
        md_load,hd_load=b2b_veh_type_truckload(FH_B2B.loc[i,"SCTG_Group"],FH_B2B.loc[i,"Distance"], FH_B2B.loc[i,"D_truckload"], md_cap, hd_cap)
        FH_B2B.loc[i,["md_truckload","hd_truckload"]]=[md_load,hd_load]

    firms_temp=firms.copy()
    ## Assign shipment can be hanlded in Private truck to For-hire truck 
    ## Rule base: for capacity
    PV_B2B =PV_B2B.sort_values(by=['SellerID', 'Distance']).reset_index(drop=True)
    sel_ID=0
    for i in range (0,PV_B2B.shape[0]):
        if (sel_ID != PV_B2B["SellerID"].iloc[i]):
            firm_index=firms_temp.index[firms_temp["SellerID"]==PV_B2B.loc[i,"SellerID"]].values[0]
            [md_cap, hd_cap]=firms_temp.loc[firm_index,["md_capacity","hd_capacity"]].values.tolist() 
            sel_ID=PV_B2B["SellerID"].iloc[i]
        if (PV_B2B["md_truckload"].iloc[i] <= md_cap) and (PV_B2B["hd_truckload"].iloc[i] <= hd_cap) :
            md_cap = md_cap - PV_B2B["md_truckload"].iloc[i]
            hd_cap = hd_cap - PV_B2B["hd_truckload"].iloc[i]
        elif (PV_B2B["md_truckload"].iloc[i] <= md_cap) and (PV_B2B["hd_truckload"].iloc[i] > hd_cap) :
            md_cap = md_cap - PV_B2B["md_truckload"].iloc[i]
            FH_B2B= pd.concat([FH_B2B,PV_B2B.iloc[[i]]], ignore_index=True).reset_index(drop=True)
            FH_B2B.loc[FH_B2B.shape[0]-1, "md_truckload"]=0
            PV_B2B.loc[i, "hd_truckload"]=0
        elif (PV_B2B["md_truckload"].iloc[i] > md_cap) and (PV_B2B["hd_truckload"].iloc[i] <= hd_cap) :
            hd_cap = hd_cap - PV_B2B["hd_truckload"].iloc[i]
            FH_B2B= pd.concat([FH_B2B,PV_B2B.iloc[[i]]], ignore_index=True).reset_index(drop=True)
            FH_B2B.loc[FH_B2B.shape[0]-1, "hd_truckload"]=0
            PV_B2B.loc[i, "md_truckload"]=0
        elif (PV_B2B["md_truckload"].iloc[i] > md_cap) and (PV_B2B["hd_truckload"].iloc[i] > hd_cap):
            FH_B2B= pd.concat([FH_B2B,PV_B2B.iloc[[i]]], ignore_index=True).reset_index(drop=True)
            PV_B2B.loc[i, "hd_truckload"]=0
            PV_B2B.loc[i, "md_truckload"]=0

    # PV MD/HD shipment level processing 
    PV_B2B_MD= PV_B2B[PV_B2B["md_truckload"]>0].reset_index(drop=True)
    PV_B2B_HD= PV_B2B[PV_B2B["hd_truckload"]>0].reset_index(drop=True)

    PV_B2B_MD["D_truckload"]=PV_B2B_MD["md_truckload"]
    PV_B2B_MD["veh_type"]='md'
    PV_B2B_HD["D_truckload"]=PV_B2B_HD["hd_truckload"]
    PV_B2B_HD["veh_type"]='hd'
    ## MD
    PV_B2B_MD_Ship=pd.DataFrame()
    for i in range(0,PV_B2B_MD.shape[0]):  
        load=PV_B2B_MD["D_truckload"].iloc[i]
        num_shipment=int(load/md_max_load)+1
        temp=pd.concat([PV_B2B_MD.iloc[[i]]]*num_shipment, ignore_index=True)
        if num_shipment ==1:
            temp["D_truckload"]= load
        else:    
            temp["D_truckload"]=md_max_load
            temp.loc[temp.shape[0]-1,"D_truckload"]=load-md_max_load*(num_shipment-1)
        PV_B2B_MD_Ship= pd.concat([PV_B2B_MD_Ship,temp], ignore_index=True).reset_index(drop=True)    
    ## HD
    PV_B2B_HD_Ship=pd.DataFrame()
    for i in range(0,PV_B2B_HD.shape[0]):  
        load=PV_B2B_HD["D_truckload"].iloc[i]
        num_shipment=int(load/hd_max_load)+1
        temp=pd.concat([PV_B2B_HD.iloc[[i]]]*num_shipment, ignore_index=True)
        if num_shipment ==1:
            temp["D_truckload"]= load
        else:    
            temp["D_truckload"]=hd_max_load
            temp.loc[temp.shape[0]-1,"D_truckload"]=load-hd_max_load*(num_shipment-1)
        PV_B2B_HD_Ship= pd.concat([PV_B2B_HD_Ship,temp], ignore_index=True).reset_index(drop=True)    

    PV_B2B = pd.concat([PV_B2B_MD_Ship, PV_B2B_HD_Ship], ignore_index=True).reset_index(drop=True)

    # FH MD/HD shipment level processing 
    FH_B2B_MD= FH_B2B[FH_B2B["md_truckload"]>0].reset_index(drop=True)
    FH_B2B_HD= FH_B2B[FH_B2B["hd_truckload"]>0].reset_index(drop=True)

    FH_B2B_MD["D_truckload"]=FH_B2B_MD["md_truckload"]
    FH_B2B_MD["veh_type"]='md'
    FH_B2B_HD["D_truckload"]=FH_B2B_HD["hd_truckload"]
    FH_B2B_HD["veh_type"]='hd'

    FH_B2B_MD_Ship=pd.DataFrame()
    for i in range(0,FH_B2B_MD.shape[0]):
        load=FH_B2B_MD["D_truckload"].iloc[i]
        num_shipment=int(load/md_max_load)+1
        temp=pd.concat([FH_B2B_MD.iloc[[i]]]*num_shipment, ignore_index=True)
        if num_shipment ==1:
            temp["D_truckload"]= load
        else:    
            temp["D_truckload"]=md_max_load
            temp.loc[temp.shape[0]-1,"D_truckload"]=load-md_max_load*(num_shipment-1)
        id_gen= np.repeat([1,2,3,4,5],int(num_shipment/5)+1)    
        temp["ship_group"]=id_gen[0:temp.shape[0]]
        FH_B2B_MD_Ship= pd.concat([FH_B2B_MD_Ship,temp], ignore_index=True).reset_index(drop=True)    

    FH_B2B_HD_Ship=pd.DataFrame()
    for i in range(0,FH_B2B_HD.shape[0]):  
        load=FH_B2B_HD["D_truckload"].iloc[i]
        num_shipment=int(load/hd_max_load)+1
        temp=pd.concat([FH_B2B_HD.iloc[[i]]]*num_shipment, ignore_index=True)
        if num_shipment ==1:
            temp["D_truckload"]= load
        else:    
            temp["D_truckload"]=hd_max_load
            temp.loc[temp.shape[0]-1,"D_truckload"]=load-hd_max_load*(num_shipment-1)
        id_gen= np.repeat([1,2,3,4,5],int(num_shipment/5)+1)    
        temp["ship_group"]=id_gen[0:temp.shape[0]]
        FH_B2B_HD_Ship= pd.concat([FH_B2B_HD_Ship,temp], ignore_index=True).reset_index(drop=True)

    FH_B2B = pd.concat([FH_B2B_MD_Ship, FH_B2B_HD_Ship], ignore_index=True).reset_index(drop=True)

    return FH_B2B, PV_B2B
# need to update this for commodity specific for daily
def b2b_d_truckload(TruckLoad, w_th):
    # w_th= weight threshold
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
def b2b_d_shipment_by_commodity(fdir,commoidty, weight_theshold, CBGzone_df,sel_county,ship_direction):
    daily_b2b_fname=fdir+'Daily_sctg%s_OD.csv' %commoidty
    if file_exists(daily_b2b_fname):
        B2BF=pd.read_csv(daily_b2b_fname, header=0, sep=',')
    else:    
        B2BF=pd.DataFrame()
        sub_fdir="sctg%s_truck/" %commoidty
        for filename in glob.glob(fdir+sub_fdir+'*.csv'):
            temp= pd.read_csv(filename, header=0, sep=',')
            # Add SellerCounty and BuyerCounty for filering 
            temp = temp.merge(CBGzone_df[['MESOZONE','County']], left_on="SellerZone", right_on='MESOZONE', how='left')
            temp=temp.rename({'County':'SellerCounty'}, axis=1)
            temp = temp.merge(CBGzone_df[['MESOZONE','County']], left_on="BuyerZone", right_on='MESOZONE', how='left')
            temp=temp.rename({'County':'BuyerCounty'}, axis=1)
            if sel_county != 9999:
                if ship_direction == "out":
                    temp= temp[temp['SellerCounty']==sel_county].reset_index(drop=True)
                elif ship_direction == "in":
                    temp= temp[temp['BuyerCounty']==sel_county].reset_index(drop=True)
                elif ship_direction == "all":
                    temp= temp[(temp['BuyerCounty']==sel_county) or (temp['SellerCounty']==sel_county)].reset_index(drop=True)
            temp['TruckLoad']=temp['TruckLoad']*2000
            temp["D_truckload"]=0
            temp["D_selection"]=0
            temp["D_truckload"]=temp['TruckLoad'].apply(lambda x: b2b_d_truckload(x, weight_theshold))
            temp["D_selection"]=temp['TruckLoad'].apply(lambda x: b2b_d_select(x, weight_theshold))
            temp=temp.query('D_selection ==1')
            B2BF=pd.concat([B2BF,temp],ignore_index=True)
        B2BF.to_csv(fdir+'Daily_sctg%s_OD.csv' %commoidty, index = False, header=True)
    return B2BF
def b2b_veh_type_truckload(SCTG_Group,Distance, D_truckload, md_capacity, hd_capacity):
    # Need to update with VIUS distribution
    if SCTG_Group==1: # bulk
        md_load= 0
        hd_load=D_truckload
    elif SCTG_Group==2: #fuel_fert
        if Distance <150:
            if D_truckload<=md_capacity:
                md_load= D_truckload
                hd_load=0
            elif D_truckload>md_capacity:
                md_load= md_capacity
                hd_load= D_truckload-md_capacity
        elif Distance >=150:
            md_load= 0
            hd_load= D_truckload
        else:           
            md_load= 0
            hd_load= D_truckload
    elif SCTG_Group==3: # interm_food
        if Distance <250:
            if D_truckload <= md_capacity:
                md_load= D_truckload
                hd_load= 0 
            else:    
                temp_md = D_truckload*0.6
                temp_hd = D_truckload*0.4
                if temp_md<=md_capacity and temp_hd <=hd_capacity:
                    md_load= temp_md
                    hd_load= temp_hd 
                elif temp_md>md_capacity and temp_hd <=hd_capacity:
                    md_load= md_capacity
                    hd_load= D_truckload - md_capacity
                elif temp_md>md_capacity and temp_hd > hd_capacity:
                    md_load= D_truckload - hd_capacity 
                    hd_load= hd_capacity                                       
                elif temp_md<=md_capacity and temp_hd > hd_capacity:
                    md_load= md_capacity
                    hd_load= D_truckload - md_capacity 
        elif Distance >=250:
            md_load= 0
            hd_load= D_truckload
        else:           
            md_load= 0
            hd_load= D_truckload   
    elif SCTG_Group==4: # mfr_goods
        if Distance <250:
            if D_truckload <= md_capacity:
                md_load= D_truckload
                hd_load= 0 
            else:             
                temp_md = D_truckload*0.4
                temp_hd = D_truckload*0.6
                if temp_md<=md_capacity and temp_hd <=hd_capacity:
                    md_load= temp_md
                    hd_load= temp_hd 
                elif temp_md>md_capacity and temp_hd <=hd_capacity:
                    md_load= md_capacity
                    hd_load= D_truckload - md_capacity
                elif temp_md>md_capacity and temp_hd > hd_capacity:
                    md_load= D_truckload - hd_capacity 
                    hd_load= hd_capacity                                       
                elif temp_md<=md_capacity and temp_hd > hd_capacity:
                    md_load= md_capacity
                    hd_load= D_truckload - md_capacity 
        elif Distance >=250:
            md_load= 0
            hd_load= D_truckload
        else:           
            md_load= 0
            hd_load= D_truckload     
    elif SCTG_Group==5: # others
        if Distance <250:
            if D_truckload <= md_capacity:
                md_load= D_truckload
                hd_load= 0 
            else:             
                temp_md = D_truckload*0.5
                temp_hd = D_truckload*0.5
                if temp_md<=md_capacity and temp_hd <=hd_capacity:
                    md_load= temp_md
                    hd_load= temp_hd 
                elif temp_md>md_capacity and temp_hd <=hd_capacity:
                    md_load= md_capacity
                    hd_load= D_truckload - md_capacity
                elif temp_md>md_capacity and temp_hd > hd_capacity:
                    md_load= D_truckload - hd_capacity 
                    hd_load= hd_capacity                                       
                elif temp_md<=md_capacity and temp_hd > hd_capacity:
                    md_load= md_capacity
                    hd_load= D_truckload - md_capacity 
        elif Distance >=250:
            md_load= 0
            hd_load= D_truckload
        else:           
            md_load= 0
            hd_load= D_truckload
    return md_load, hd_load                                
def b2b_apro_tour_time(zone, num_visit,size, zone_df):
    try:
        if num_visit >1:
            area= zone_df[zone_df['MESOZONE']==zone]['area'].values[0]
            time = int(0.57*np.sqrt(area/size*num_visit*100)/15*60+0.5)
            if time >60*3:
                time = int(num_visit * 2.5) 
        else:
            time = int(np.random.gamma(3, 1, 1)[0] +0.5) 
    except:
        time = 90 
    return time 
def b2b_create_output(B2BF_PV,B2BF_FH,truckings,df_dpt_dist, ship_type, ex_zone_list, firms):
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
    'veh_type'])

    payloads['payload_id']= np.arange(B2BF_PV.shape[0])
    payloads['carrier_id']= B2BF_PV['SellerID']
    #payloads['sequence_id']=
    #payloads['tour_id']=
    payloads['commodity']=B2BF_PV['SCTG_Group']
    payloads['weight']=B2BF_PV['D_truckload']
    payloads['job']= 'delivery'
    #payloads['pu_zone']=
    payloads['del_zone']=B2BF_PV['BuyerZone']
    #payloads['pu_stop_duration']=
    ## need to fix this distribution
    load_min =B2BF_PV.D_truckload.min()
    load_max = B2BF_PV.D_truckload.max()
    payloads['del_stop_duration']=B2BF_PV.apply(lambda x: int(np.random.gamma(2, 1, 1)[0]*((x['D_truckload'] -load_min)/(load_max-load_min))*120), axis=1)
    payloads['del_stop_duration'] =payloads['del_stop_duration'].apply(lambda x: random.randint(5,20) if x <5 else x)  
    payloads['del_stop_duration']=payloads['del_stop_duration'].apply(lambda x: 90 if x >90 else x)
    #payloads['pu_tw_lower']=
    #payloads['pu_tw_upper']=
    payloads['del_tw_lower']=60*5
    payloads['del_tw_upper']=payloads['del_zone'].apply(lambda x: 20*24*60 if x in ex_zone_list else 60*22) 
    #payloads['pu_arrival_time']=
    #payloads['del_arrival_time']=
    payloads['veh_type']=B2BF_PV['veh_type']   

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
    'veh_type'])

    payloads_FH['payload_id']= np.arange(B2BF_PV.shape[0],B2BF_PV.shape[0]+B2BF_FH.shape[0])
    payloads_FH['carrier_id']= B2BF_FH['assigned_carrier']
    #payloads['sequence_id']=
    #payloads['tour_id']=
    payloads_FH['commodity']=B2BF_FH['SCTG_Group']
    payloads_FH['weight']=B2BF_FH['D_truckload']
    payloads_FH['job']= 'pickup_delivery'
    payloads_FH['pu_zone']=B2BF_FH['SellerZone']
    payloads_FH['del_zone']=B2BF_FH['BuyerZone']
    load_min =B2BF_FH.D_truckload.min()
    load_max = B2BF_FH.D_truckload.max()
    # need to put max 
    payloads_FH['pu_stop_duration']= B2BF_FH.apply(lambda x: int(np.random.gamma(2, 1, 1)[0]*((x['D_truckload'] -load_min)/(load_max-load_min))*120), axis=1)
    payloads_FH['pu_stop_duration'] =payloads_FH['pu_stop_duration'].apply(lambda x: random.randint(5,20) if x <5 else x)   
    payloads_FH['pu_stop_duration']=payloads_FH['pu_stop_duration'].apply(lambda x: 90 if x >90 else x)
    ## need to fix this distribution
    payloads_FH['del_stop_duration']=B2BF_FH.apply(lambda x: int(np.random.gamma(2, 1, 1)[0]*((x['D_truckload'] -load_min)/(load_max-load_min))*120), axis=1)
    payloads_FH['del_stop_duration'] =payloads_FH['del_stop_duration'].apply(lambda x: random.randint(5,20) if x <5 else x)                                           
    payloads_FH['del_stop_duration']=payloads_FH['del_stop_duration'].apply(lambda x: 90 if x >90 else x)
    payloads_FH['pu_tw_lower']=60*5
    payloads_FH['pu_tw_upper']=payloads_FH['del_zone'].apply(lambda x: 20*24*60 if x in ex_zone_list else 60*22)
    payloads_FH['del_tw_lower']=60*5
    payloads_FH['del_tw_upper']=payloads_FH['del_zone'].apply(lambda x: 20*24*60 if x in ex_zone_list else 60*22)
    #payloads['pu_arrival_time']=
    #payloads['del_arrival_time']=
    payloads_FH['veh_type']=B2BF_FH['veh_type']    

    payloads=pd.concat([payloads, payloads_FH],ignore_index=True)
    ### End Create Payload file 
    ### Create Carrier file

    PV_T_D =B2BF_PV.groupby(['SellerID', 'SellerZone'])['D_truckload'].agg(D_truckload="sum").reset_index()

    firms=firms[['SellerID','MESOZONE','md_veh','hd_veh']]
    PV_T_D = PV_T_D.merge(firms, on='SellerID', how='left')

    carriers = pd.DataFrame(columns = ['carrier_id',
    'firm_id',
    'depot_zone',
    'contract_firms',
    'num_veh_type_1',
    'num_veh_type_2',
    'num_veh_type_3',
    'num_veh_type_4',
    'num_veh_type_5',
    'num_veh_type_6',
    'num_veh_type_7',
    'num_veh_type_8',
    'num_veh_type_9',
    'depot_lower',
    'depot_upper',
    'depot_time_before',
    'depot_time_after'])

    carriers['carrier_id']=PV_T_D['SellerID']
    carriers['firm_id']=PV_T_D['SellerID']
    carriers['depot_zone']=PV_T_D['SellerZone']
    carriers['contract_firms']=PV_T_D['SellerID'].apply(lambda x: [x])
    carriers['num_veh_type_1']=PV_T_D['md_veh']
    carriers['num_veh_type_2']=PV_T_D['hd_veh']
    carriers['depot_lower']= carriers['depot_zone'].apply(lambda x: depot_time_depart(x,df_dpt_dist,ship_type))
    carriers['depot_upper']= 40*24*60#carriers['depot_lower'].apply(depot_time_close)
    carriers['depot_time_before']= [random.randrange(0,30, 5) for j in carriers.index]
    carriers['depot_time_after']= [random.randrange(0,30, 5) for j in carriers.index]

    temp_FH_T_D = B2BF_FH.groupby('assigned_carrier')['SellerID'].apply(list).reset_index(name='contract_firms')
    temp_FH_T_D.rename({'assigned_carrier': 'SellerID'},axis=1, inplace=True)
    firms_sub=truckings[['BusID','MESOZONE','md_veh','hd_veh']]
    firms_sub=firms_sub.rename({'BusID':'SellerID'}, axis='columns')  
    temp_FH_T_D = temp_FH_T_D.merge(firms_sub, on='SellerID', how='left')
    temp = pd.DataFrame(columns = ['carrier_id',
    'firm_id',
    'depot_zone',
    'contract_firms',
    'num_veh_type_1',
    'num_veh_type_2',
    'num_veh_type_3',
    'num_veh_type_4',
    'num_veh_type_5',
    'num_veh_type_6',
    'num_veh_type_7',
    'num_veh_type_8',
    'num_veh_type_9',
    'depot_lower',
    'depot_upper',
    'depot_time_before',
    'depot_time_after'])
    temp['carrier_id']=temp_FH_T_D['SellerID']
    temp['firm_id']=temp_FH_T_D['SellerID']
    temp['depot_zone']=temp_FH_T_D['MESOZONE']
    temp['contract_firms']=temp_FH_T_D['contract_firms']
    temp['num_veh_type_1']=temp_FH_T_D['md_veh']
    temp['num_veh_type_2']=temp_FH_T_D['hd_veh']
    temp['depot_lower']= temp['depot_zone'].apply(lambda x: depot_time_depart(x,df_dpt_dist,ship_type))
    temp['depot_upper']= 40*24*60 #temp['depot_lower'].apply(depot_time_close)
    temp['depot_time_before']= [random.randrange(5,40, 5) for j in temp.index]
    temp['depot_time_after']= [random.randrange(5,40, 5) for j in temp.index]

    carriers=pd.concat([carriers, temp], ignore_index=True)

    return payloads, carriers
    ### End Create Carrier file    
##################################################################


def main(args=None):
    # read input files
    parser = ArgumentParser()
    parser.add_argument("-st", "--shipment type", dest="ship_type",
                        help="B2B or B2C", required=True, type=str)
    parser.add_argument("-ct", "--county", dest="sel_county",
                        help="select county; for all area run, put 9999", required=True, type=int)
    parser.add_argument("-sd", "--direction", dest="ship_direction",
                        help="select 'out', 'in', 'all' for B2B, all for B2C ", required=True, type=str)                                                                   
    args = parser.parse_args()

    start_time=time.time()
    create_global_variable()
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
    firms, truckings,dist_df, CBGzone_df, df_dpt_dist, ex_zone_list= genral_input_files_processing(config.firm_file,
                                                                                     config.warehouse_file, 
                                                                                     config.dist_file,
                                                                                     config.CBG_file, 
                                                                                     args.ship_type)

    # Read and generate daily shipment file
    if args.ship_type == "B2C":
        print ("**** Start processing daily B2C shipment")
        df_hh_D= b2c_input_files_processing(CBGzone_df, 
                                            config.b2c_delivery_frequency, args.sel_county)

        print ("**** Completed initial daily generation and Start processing aggregation")
        df_hh_D_GrID=b2c_household_aggregation (df_hh_D, CBGzone_df, 15)
        df_hh_D_GrID.loc[:,'veh_type'] ="md"
        df_hh_D_GrID.loc[:,'assigned_carrier']=-1
        df_hh_D_GrID=df_hh_D_GrID.reset_index(drop=True)
        df_hh_D_GrID.to_csv('../../../FRISM_input_output/Sim_outputs/temp_save/df_hh_D_GrID_before.csv', index = False, header=True)
        # Assigned the carrirer to shipment!: 
        ## This part is time consuming which is associated to the function "carrier_sel()"
        print ("**** Complete aggregation and Starting carrier assignement ****")
        print ("size of shipment:", df_hh_D_GrID.shape[0])
        non_sel_seller=pd.DataFrame() 
        with alive_bar(df_hh_D_GrID.shape[0], force_tty=True) as bar:
            #for i in range(0,df_hh_D_GrID.shape[0]): #***************** need to comment out and comment the line below *************************************
            for i in range(0,10):
                if df_hh_D_GrID.loc[i,'veh_type'] == "md":
                    cap_index = "md_capacity"
                elif df_hh_D_GrID.loc[i,'veh_type'] == "hd":
                    cap_index ="hd_capacity"            
                # find a carrier who can hand a shipment at row i 
                sel_busID=carrier_sel(df_hh_D_GrID.loc[i,'MESOZONE'], df_hh_D_GrID.loc[i,'D_truckload'],
                                    df_hh_D_GrID.loc[i,'tour_tt'],df_hh_D_GrID.loc[i,'veh_type'], dist_df, truckings )
                # put the carrier into df
                if sel_busID == -1:
                    non_sel_seller=pd.concat([non_sel_seller,df_hh_D_GrID.iloc[[i]]], ignore_index=True).reset_index(drop=True)
                else: 
                    df_hh_D_GrID.loc[i,'assigned_carrier']=sel_busID
                    # Calculate the reduce the capacity and time capacity that can reflect after a row assignment
                    trucking_index = truckings.index[truckings["BusID"]==sel_busID].values[0]
                    truckings.loc[trucking_index,cap_index] = truckings.loc[trucking_index,cap_index] - df_hh_D_GrID.loc[i,'D_truckload']
                    truckings.loc[trucking_index,"time_cap"] = truckings.loc[trucking_index,"time_cap"] - df_hh_D_GrID.loc[i,'tour_tt']
                bar()
                #print (i)
        print ("**** Completed carrier assignement and Generating results ****")    
        df_hh_D_GrID=df_hh_D_GrID[df_hh_D_GrID['assigned_carrier'] >=0].reset_index(drop=True)
        ## temporary saving: hh_D= with assigned_carrier
        df_hh_D_GrID.to_csv('../../../FRISM_input_output/Sim_outputs/temp_save/df_hh_D_GrID_carrier_assigned.csv', index = False, header=True)

        payloads, carriers=b2c_create_output(df_hh_D_GrID,truckings,df_dpt_dist, args.ship_type)

        payloads.to_csv (config.fdir_main_output+config.fnm_B2C_payload+"_county%s_ship%s.csv" %(args.sel_county, args.ship_direction), index = False, header=True)
        carriers.to_csv (config.fdir_main_output+config.fnm_B2C_carrier+"_county%s_ship%s.csv" %(args.sel_county, args.ship_direction), index = False, header=True)

        print ("**** Completed generating B2C payload/carrier file ****")

    elif args.ship_type == "B2B":
        # Create daily B2B for private and B2B for for-hire 
        print ("**** Start processing daily B2B shipment")
        FH_B2B, PV_B2B = b2b_input_files_processing(firms,CBGzone_df, args.sel_county, args.ship_direction, config.commodity_list, config.weight_theshold)
        PV_B2B .to_csv('../../../FRISM_input_output/Sim_outputs/temp_save/PV_B2B.csv', index = False, header=True)
        ## Get shipper's shipment the entire truckload (sum by seller ID ) for each day: 
        ## Need to find a couple of carriers (like making a contract with carriers)
        ##### Update requried: This could be updated later with contract-related modeling 
        # temporary hold 
        # print ("**** Completed daily B2B shipment and staring processing for-hire carrier aggregation ****")
        # FH_Seller= FH_B2B.groupby(['SellerID', 'SellerZone','ship_group','veh_type'])['D_truckload'].agg(D_truckload='sum', num_shipments='count').reset_index()
        # FH_Seller['tour_tt'] = FH_Seller.apply(lambda x: b2b_apro_tour_time(x['SellerZone'], x['num_shipments'], 1, CBGzone_df), axis=1)
        # FH_Seller.loc[:,'assigned_carrier']=-1
        # FH_Seller=FH_Seller.reset_index(drop=True) 
        FH_Seller=FH_B2B[['SellerID', 'SellerZone','D_truckload','veh_type']]
        FH_Seller.loc[:,'tour_tt']=30
        FH_Seller.loc[:,'assigned_carrier']=-1
        FH_Seller=FH_Seller.reset_index(drop=True)
        FH_Seller.to_csv('../../../FRISM_input_output/Sim_outputs/temp_save/FH_Seller_before.csv', index = False, header=True) 
        # Assigned the carrirer to shipment!: 
        ## This part is time consuming which is associated to the function "carrier_sel()" 
        print ("**** Completed for-hire aggregation and Starting carrier assignement for hire ****")
        print ("size of shipment:", FH_Seller.shape[0])
        non_sel_seller=pd.DataFrame() 
        with alive_bar(FH_Seller.shape[0], force_tty=True) as bar:
            #for i in range(0,FH_Seller.shape[0]): #***************** need to comment out and comment the line below *************************************
            for i in range(0,10):
                if FH_Seller.loc[i,'veh_type'] == "md":
                    cap_index = "md_capacity"
                elif FH_Seller.loc[i,'veh_type'] == "hd":
                    cap_index ="hd_capacity"
                # find a carrier who can hand a shipment at row i 
                sel_busID=carrier_sel(FH_Seller.loc[i,'SellerZone'], FH_Seller.loc[i,'D_truckload'],
                                    FH_Seller.loc[i,'tour_tt'], FH_Seller.loc[i,'veh_type'], dist_df, truckings)
                if sel_busID == -1:
                    non_sel_seller=pd.concat([non_sel_seller,FH_Seller.iloc[[i]]], ignore_index=True).reset_index(drop=True)
                else:    
                # put the carrier into df
                    FH_Seller.loc[i,'assigned_carrier']=sel_busID
                    # Calculate the reduce the capacity and time capacity that can reflect after a row assignment
                    trucking_index = truckings.index[truckings["BusID"]==sel_busID].values[0]
                    truckings.loc[trucking_index,cap_index] = truckings.loc[trucking_index,cap_index] - FH_Seller.loc[i,'D_truckload']
                    truckings.loc[trucking_index,"time_cap"] = truckings.loc[trucking_index,"time_cap"] - FH_Seller.loc[i,'tour_tt']        
                bar()
        print ("**** Completed carrier assignement ****")
        FH_Seller=FH_Seller[FH_Seller['assigned_carrier'] >=0].reset_index(drop=True)
        FH_Seller.to_csv('../../../FRISM_input_output/Sim_outputs/temp_save/FH_Seller_carrier_assigned.csv', index = False, header=True)

        FH_B2B=FH_B2B.merge(FH_Seller[['SellerID', 'assigned_carrier', 'veh_type']], on=['SellerID','veh_type'], how='inner')
        ## temporary saving: hh_D= with assigned_carrier
        FH_B2B.to_csv('../../../FRISM_input_output/Sim_outputs/temp_save/FH_B2B_carrier_assigned.csv', index = False, header=True)
        PV_B2B = PV_B2B.sort_values(by=['SellerID', 'SCTG_Group']).reset_index(drop=True)
        FH_B2B= FH_B2B.sort_values(by=['SellerID', 'SCTG_Group']).reset_index(drop=True)

        # create payload and carriers
        payloads, carriers=b2b_create_output(PV_B2B,FH_B2B,truckings,df_dpt_dist, args.ship_type, ex_zone_list, firms)

        payloads.to_csv (config.fdir_main_output+config.fnm_B2B_payload+"_county%s_ship%s.csv" %(args.sel_county, args.ship_direction), index = False, header=True)
        carriers.to_csv (config.fdir_main_output+config.fnm_B2B_carrier+"_county%s_ship%s.csv" %(args.sel_county, args.ship_direction), index = False, header=True)
        print ("**** Completed generating B2C payload/carrier file ****")

    vehicle_types = veh_type_create()
    vehicle_types.to_csv (config.fdir_main_output+config.fnm_vtype, index = False, header=True)

    print ("Run time of %s: %s seconds" %(args.ship_type, time.time()-start_time))    


if __name__ == "__main__":
    main()