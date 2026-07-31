# %%
from re import A
import pandas as pd
import numpy as np
import geopandas as gpd
import random
import os
from shapely.geometry import Point
import math 
import sys
# %%
def externalzone_psrc(group_id):
    eval_prob=random.uniform(0,1.00001)
    if group_id ==1:
        if  eval_prob<=0.96:
            return 3733
        elif eval_prob>0.96 and eval_prob<=0.998:
            return 3734
        elif eval_prob>0.998 and eval_prob<=0.999:
            return 3735
        else:
            return random.choice([3736,3737,3750]) 
    elif group_id ==2:
        if  eval_prob<=0.97:
            return 3739
        elif eval_prob>0.97 and eval_prob<=0.987:
            return 3738
        elif eval_prob>0.987 and eval_prob<=0.999:
            return 3740
        else:
            return random.choice([3741,3742,3736,3737])
    elif group_id ==3:
        if  eval_prob<=0.965:
            return 3744
        elif eval_prob>0.965 and eval_prob<=0.984:
            return 3746
        elif eval_prob>0.984 and eval_prob<=0.998:
            return 3747
        else:
            return 3743
    elif group_id ==4:
        if  eval_prob<=0.80:
            return 3748
        elif eval_prob>0.80 and eval_prob<=0.99:
            return 3750
        else:
            return random.choice([3749,3733])  
def random_points_in_polygon(polygon):
    temp = polygon.bounds
    finished= False
    while not finished:
        point = Point(random.uniform(temp.minx.values[0], temp.maxx.values[0]), random.uniform(temp.miny.values[0], temp.maxy.values[0]))
        finished = polygon.contains(point).values[0]
    return [point.x, point.y] 

def fleet_composition(selected_firms, seller_id, input_variables, dic_veh):
    dic_fleet = {veh_type: {fuel_type: 0 for fuel_type in input_variables["fuel_type"]} for veh_type in input_variables["vehicle_type"]}
    if selected_firms.empty:
        for veh_type in dic_fleet.keys():
            dic_fleet[veh_type]["Total"]=0
        ev_powertrain = None    
    else:
        if "BusID" in selected_firms.columns:
            selected_firms = selected_firms.rename(columns={"BusID": 'SellerID'})
        for veh_type in input_variables["vehicle_type"]:
            dic_veh[veh_type]["synthfirm_name"]
            dic_fleet[veh_type]["Total"]=0
            for fuel_type in input_variables["fuel_type"]:
                try: 
                    num_veh=selected_firms[selected_firms['SellerID'] == seller_id][fuel_type + " "+ dic_veh[veh_type]["synthfirm_name"]].values[0]
                except:
                    num_veh =0    
                dic_fleet[veh_type][fuel_type]=num_veh
                dic_fleet[veh_type]["Total"]=dic_fleet[veh_type]["Total"]+dic_fleet[veh_type][fuel_type]

        ev_powertrain=selected_firms[selected_firms['SellerID'] == seller_id]["EV_powertrain (if any)"].values[0]
    return dic_fleet, ev_powertrain

def veh_type_by_payload(D_truckload,dic_veh):
    dic_possible_veh_type={}
    for veh_type in dic_veh.keys():
        if dic_veh[veh_type]["veh_capacity"] >= D_truckload:
           dic_possible_veh_type[veh_type] = D_truckload/dic_veh[veh_type]["veh_capacity"] 
    if dic_possible_veh_type=={}:
        for veh_type in dic_veh.keys():
           if D_truckload/dic_veh[veh_type]["veh_capacity"] <= 3:
                dic_possible_veh_type[veh_type] = D_truckload/dic_veh[veh_type]["veh_capacity"]
           elif "hd" in veh_type:
                dic_possible_veh_type[veh_type] = D_truckload/dic_veh[veh_type]["veh_capacity"]      
    return dic_possible_veh_type         

def veh_type_choice(SCTG_Group,Distance, D_truckload, df_vius, dic_fleet ,dic_veh, mdhdv_adjustment):
    dic_possible_veh_type = veh_type_by_payload(D_truckload,dic_veh)
    ## calculate the prior using given fleet composition and truckload
    dic_fleet_probability={}
    total_capacity= 0

    for veh_type in dic_fleet.keys():
        # Reflect avaiable vehicle type
        if veh_type in dic_possible_veh_type.keys():
            updated_total=dic_fleet[veh_type]["Total"]-dic_possible_veh_type[veh_type]
            if updated_total>=0:
                dic_fleet[veh_type]["Total"] = updated_total+0.01
            else:
                dic_fleet[veh_type]["Total"] =0   
        else: 
            dic_fleet[veh_type]["Total"] =0     
        total_capacity = total_capacity+dic_fleet[veh_type]["Total"]

    if total_capacity > 0: 
        for veh_type in dic_fleet.keys():
            dic_fleet_probability[veh_type] = dic_fleet[veh_type]["Total"]/total_capacity     
    else: 
        for veh_type in dic_fleet.keys():
            if veh_type in dic_possible_veh_type.keys(): 
                dic_fleet_probability[veh_type] = 1
            else:             
                dic_fleet_probability[veh_type] = 0
    # multiply VIUS probability    
    if Distance <=50:
        col_name="RO_0_50"
    elif Distance >50 and Distance <=100:
        col_name='RO_51_100'
    elif Distance >100 and Distance <=200: 
        col_name='RO_101_200'
    elif Distance >200 and Distance <=500:
        col_name='RO_201_500'
    else:                   
        col_name='RO_GT500'

    sum_probability = 0
    for veh_type in dic_fleet.keys():
        try:
            if SCTG_Group == 99:
                if veh_type in ["mdv"]:
                    dic_fleet_probability[veh_type]= dic_fleet_probability[veh_type]* (df_vius[(df_vius["SCTG_VIUS_Group"]==SCTG_Group) & (df_vius['VEH_CLASS_SynthFirm']==veh_type)][col_name].values[0]+mdhdv_adjustment)
                else:
                    dic_fleet_probability[veh_type]= dic_fleet_probability[veh_type]* (df_vius[(df_vius["SCTG_VIUS_Group"]==SCTG_Group) & (df_vius['VEH_CLASS_SynthFirm']==veh_type)][col_name].values[0])
            else:
                if veh_type in ["mdv","hdv"]:
                    dic_fleet_probability[veh_type]= dic_fleet_probability[veh_type]* (df_vius[(df_vius["SCTG_VIUS_Group"]==SCTG_Group) & (df_vius['VEH_CLASS_SynthFirm']==veh_type)][col_name].values[0]+mdhdv_adjustment)
                else:
                    dic_fleet_probability[veh_type]= dic_fleet_probability[veh_type]* (df_vius[(df_vius["SCTG_VIUS_Group"]==SCTG_Group) & (df_vius['VEH_CLASS_SynthFirm']==veh_type)][col_name].values[0])                            
        except:
            print (veh_type)
            print (df_vius)
            print (SCTG_Group)
            print (veh_type)
            sys.exit(1)
        sum_probability += dic_fleet_probability[veh_type]


    for veh_type in dic_fleet.keys():
        dic_fleet_probability[veh_type]= dic_fleet_probability[veh_type]/sum_probability   

    prob_veh = random.uniform(0,1)
    cum_probability =0
    selection_flag =0
    for veh_type in dic_fleet.keys():
        cum_probability += dic_fleet_probability[veh_type]
        if cum_probability >= prob_veh and selection_flag ==0:
            return_veh_type = veh_type
            selection_flag =1
    ### This is hard code to adjust higher HDT assigment    
    try:         
        return_paylaod_ratio = dic_possible_veh_type[return_veh_type]
    except:
        if SCTG_Group == 99:
            return_veh_type = "mdv"
            return_paylaod_ratio = dic_possible_veh_type[return_veh_type]
        else:
            return_veh_type = "hdv"
            return_paylaod_ratio = dic_possible_veh_type[return_veh_type]                
    return  return_veh_type, return_paylaod_ratio

def powertrain_choice(veh_type, dic_fleet, dic_energy, ev_powertrain, Distance, payload,selected_leasings):
    leasing_flag =0 
    for powertrain in dic_fleet[veh_type].keys():
        dic_fleet[veh_type][powertrain] = dic_fleet[veh_type][powertrain]-payload

    if Distance <=10:
        Distance =10
    energy_cal_by_distance = {}
    total_capacity = dic_fleet[veh_type]["Total"]
    if total_capacity >=0:
        for powertrain in dic_fleet[veh_type].keys():
            if powertrain != "Total":
                if  dic_fleet[veh_type][powertrain] >=0:     
                    if powertrain == "Electric":
                        energy_cal_by_distance[powertrain]= (Distance +int(Distance/300)*100)/dic_energy[veh_type][ev_powertrain] 
                    else:
                        energy_cal_by_distance[powertrain]= (Distance) / dic_energy[veh_type][powertrain]
                else:
                    if powertrain == "Electric":
                        energy_cal_by_distance[powertrain]= Distance*2 
                    else:
                        energy_cal_by_distance[powertrain]= Distance*2
        return_powertrain = min(energy_cal_by_distance, key=energy_cal_by_distance.get)
    else:
        leasing_flag=1
        for powertrain in dic_fleet[veh_type].keys():
            if powertrain != "Total":      
                if powertrain == "Electric":
                    if selected_leasings[selected_leasings["powertrain"] == ev_powertrain][veh_type].values[0] >0:
                        energy_cal_by_distance[powertrain]= (Distance +int(Distance/300)*100)/dic_energy[veh_type][ev_powertrain]
                    else: 
                        energy_cal_by_distance[powertrain] =  Distance*2     
                else:
                    if selected_leasings[selected_leasings["powertrain"] == powertrain][veh_type].values[0] >0:
                        energy_cal_by_distance[powertrain]= (Distance) / dic_energy[veh_type][powertrain]
                    else: 
                        energy_cal_by_distance[powertrain] =  Distance*2
        
    return_powertrain = min(energy_cal_by_distance, key=energy_cal_by_distance.get)    
    return return_powertrain, leasing_flag

def carrier_sel(SellerZone, veh_type, payload, num_shipment, dist_df, truckings, ship_type, sctg):
    def dist_cal(org_meso, dest_meso, dist_df):
        dist = dist_df[(dist_df['Origin']==org_meso) & (dist_df['Destination']==dest_meso)].dist.values[0]
        if (dist == 0):
            dist =random.uniform(1,10)
        return dist
    
    if ship_type=="B2B":
        sctg_col_name="SCTG"+str(sctg)
        veh_col_name=veh_type+"_capacity"
        numship_col_name =veh_type+"_numshipment"
        truckings =truckings[(truckings[sctg_col_name]==1) & (truckings[veh_col_name]>=payload) & (truckings[numship_col_name]>=num_shipment)]
    else:
        veh_col_name=veh_type+"_capacity"
        numship_col_name =veh_type+"_numshipment"
        truckings =truckings[(truckings[veh_col_name]>=payload) & (truckings[numship_col_name]>=num_shipment)]
 
    sel_dist_df = dist_df[(dist_df.Origin==SellerZone) & (dist_df.dist<25)]
    candidate_busid= truckings[(truckings['MESOZONE'].isin(sel_dist_df.Destination.unique()))][['BusID','MESOZONE']] 
    
    if (candidate_busid.shape[0]  < 5):
        sel_dist_df = dist_df[(dist_df.Origin==SellerZone) & (dist_df.dist<50)]
        candidate_busid= truckings[(truckings['MESOZONE'].isin(sel_dist_df.Destination.unique()))][['BusID','MESOZONE']] 
    if (candidate_busid.shape[0]  < 5):
        sel_dist_df = dist_df[(dist_df.Origin==SellerZone) & (dist_df.dist<100)]
        candidate_busid= truckings[(truckings['MESOZONE'].isin(sel_dist_df.Destination.unique()))][['BusID','MESOZONE']]
    if (candidate_busid.shape[0]  < 5):
        sel_dist_df = dist_df[(dist_df.Origin==SellerZone) & (dist_df.dist<200)]
        candidate_busid= truckings[(truckings['MESOZONE'].isin(sel_dist_df.Destination.unique()))][['BusID','MESOZONE']]
    if (candidate_busid.shape[0]  < 5):
        sel_dist_df = dist_df[(dist_df.Origin==SellerZone) & (dist_df.dist<300)]
        candidate_busid= truckings[(truckings['MESOZONE'].isin(sel_dist_df.Destination.unique()))][['BusID','MESOZONE']]                                                         
    try: 
        if candidate_busid.shape[0] >=5: 
            candidate_busid=candidate_busid.sample(5)
  
        candidate_busid["org_MESO"]=SellerZone
        candidate_busid= candidate_busid.reset_index(drop=True)

        candidate_busid['ttime']=candidate_busid.apply(lambda x: dist_cal(x['org_MESO'], x['MESOZONE'], sel_dist_df), axis=1)
        candidate_busid['inv_sqr_tt']=candidate_busid.apply(lambda x: 1/x['ttime'], axis=1)
        sum_pro=np.sum(candidate_busid['inv_sqr_tt'])
        candidate_busid['prob']=candidate_busid.apply(lambda x: x['inv_sqr_tt']/sum_pro, axis=1)
        candidate_busid['cum_prob_ub']=candidate_busid['prob'].cumsum()
        candidate_busid['cum_prob_lb']=np.nan_to_num(candidate_busid['cum_prob_ub'].shift())
        candidate_busid.loc[candidate_busid.shape[0],'cum_prob_ub'] = 1.0001
        r_num = random.uniform(0,1)
        sel_busID=candidate_busid[(candidate_busid['cum_prob_ub'] > r_num) & (candidate_busid['cum_prob_lb'] <= r_num)].BusID.values[0]
    except:
        sel_busID ="U"
    return sel_busID

def find_coordinate(firm_dic, firm_id, index):
    try: 
        return firm_dic[firm_id][index]
    except:
        return 0    

def covert_mesozone_to_local_taz(carrier_df, payload_df, gdf_TAZ):
    """ carrier depot_zone cconvertion  """
    # to spatial join the two files
    column_names = carrier_df.columns.tolist()
    gdf_car = gpd.GeoDataFrame(carrier_df, geometry=gpd.points_from_xy(carrier_df['c_x'], carrier_df['c_y']), crs="EPSG:4269")
    gdf_car["external_zone_index"]=gdf_car.apply(lambda x: "in" if x["depot_zone"]== x["true_depot_zone"] else "ex", axis=1)
    gdf_joined = gpd.sjoin(gdf_car, gdf_TAZ , how='left', predicate='within')
    #to change the mesozone ID (depot_zone column in the csv file) to the taz ID
    gdf_joined['depot_zone'] = gdf_joined.apply(lambda x: x["taz"] if x["external_zone_index"]=="in" else x["depot_zone"], axis=1)
    new_carrier_df = gdf_joined[column_names]

    """ payload pu_zone cconvertion  """
    # to spatial join the two files
    column_names = payload_df.columns.tolist() 
    gdf_payload = gpd.GeoDataFrame(payload_df, geometry=gpd.points_from_xy(payload_df['pu_x'], payload_df['pu_y']), crs="EPSG:4269")
    gdf_payload["external_zone_index"]=gdf_payload.apply(lambda x: "in" if x["pu_zone"]== x["true_pu_zone"] else "ex", axis=1)
    gdf_joined_payload_1 = gpd.sjoin(gdf_payload, gdf_TAZ , how='left', predicate='within')
    gdf_joined_payload_1['pu_zone'] = gdf_joined_payload_1.apply(lambda x: x["taz"] if x["external_zone_index"]=="in" else x["pu_zone"], axis=1)
    new_payload_df = gdf_joined_payload_1[column_names]
   
    """ payload del_zone cconvertion  """
    # to spatial join the two files 
    gdf_payload = gpd.GeoDataFrame(new_payload_df, geometry=gpd.points_from_xy(new_payload_df['del_x'], new_payload_df['del_y']), crs="EPSG:4269")
    gdf_payload["external_zone_index"]=gdf_payload.apply(lambda x: "in" if x["del_zone"]== x["true_del_zone"] else "ex", axis=1)
    gdf_joined_payload_1 = gpd.sjoin(gdf_payload, gdf_TAZ , how='left', predicate='within')
    gdf_joined_payload_1['del_zone'] = gdf_joined_payload_1.apply(lambda x: x["taz"] if x["external_zone_index"]=="in" else x["del_zone"], axis=1)
    new_payload_df = gdf_joined_payload_1[column_names]
    
    return new_carrier_df, new_payload_df

def b2b_private_distribution_channel(b2b_private, firms, selected_leasings, vius, dic_energy, input_variables, dic_veh, county_in_region,mdhdv_adjustment): # firms=firms.firms vius =vius.vius dic_energy =ehicle_energy.dic_energy
    used_firms= firms[firms["SellerID"].isin(list(b2b_private['SellerID_Org'].unique())+list(b2b_private['BuyerID_Org'].unique()))]
    firm_dic={}
    for _, row in used_firms.iterrows():
        firm_dic[row['SellerID']]=(row["x"], row['y'])
    b2b_private = b2b_private[b2b_private["SellerID_Org"].isin(list(firm_dic.keys()))] 
    b2b_private = b2b_private[b2b_private["BuyerID_Org"].isin(list(firm_dic.keys()))] 

    selected_shipper = list(b2b_private['SellerID'].unique())
    selected_firms=firms[firms["SellerID"].isin(selected_shipper)]
    final_b2b_private = pd.DataFrame()
    for seller_id in selected_shipper:
        selected_b2b_private=b2b_private[b2b_private["SellerID"]==seller_id].reset_index(drop=True)
        dic_fleet, ev_powertrain = fleet_composition(selected_firms, seller_id, input_variables, dic_veh)
        for i in range(0,selected_b2b_private.shape[0]):
            veh_type, payload = veh_type_choice(selected_b2b_private.loc[i,"SCTG_Group"], #selected_b2b_private.loc[i,"SCTG_VIUS_group"],
                                            selected_b2b_private.loc[i,"Distance"], 
                                            selected_b2b_private.loc[i,"D_truckload"], 
                                            vius, 
                                            dic_fleet, dic_veh,mdhdv_adjustment) ## need df_vius
            num_shipment=int(payload)+1
            temp=pd.concat([selected_b2b_private.loc[[i]]]*num_shipment, ignore_index=True)
            if num_shipment ==1:
                temp["D_truckload"]= selected_b2b_private.loc[i,"D_truckload"]
            else:    
                temp["D_truckload"]=dic_veh[veh_type]["veh_capacity"]
                temp["D_truckload"].iloc[-1]=selected_b2b_private.loc[i,"D_truckload"]-dic_veh[veh_type]["veh_capacity"]*(num_shipment-1)
            temp["payload"] = temp["D_truckload"].apply(lambda x : x/dic_veh[veh_type]["veh_capacity"])
            temp["veh_type_agg"] = "U"
            temp["veh_powertrain_agg"] = "U"
            temp["veh_type"] = "U"
            temp["veh_powertrain"] = "U"
            temp["assigned_carrier"] = seller_id
            for j in range(0, temp.shape[0]):
                powertrain, leasing_flag=powertrain_choice(veh_type, dic_fleet, dic_energy, ev_powertrain, temp.loc[j,"Distance"], temp.loc[j,"payload"],selected_leasings)
                if leasing_flag ==1:
                    dic_fleet[veh_type][powertrain] +=1
                    dic_fleet[veh_type]['Total'] +=1
                    selected_leasings.loc[selected_leasings["powertrain"] == powertrain, veh_type] -= 1
                    synthfirm_name = powertrain+" "+dic_veh[veh_type]["synthfirm_name"]
                    selected_firms.loc[selected_firms["SellerID"] ==seller_id, synthfirm_name] += 1
                dic_fleet[veh_type][powertrain] -= temp.loc[j,"payload"]
                dic_fleet[veh_type]['Total'] -= temp.loc[j,"payload"]
                temp.loc[j,"veh_type_agg"] = veh_type
                temp.loc[j,"veh_powertrain_agg"] = powertrain
                if powertrain == "Electric":
                    temp.loc[j,"veh_type"] = veh_type+"_"+"E_"+ev_powertrain 
                    temp.loc[j,"veh_powertrain"] = powertrain
                else:    
                    temp.loc[j,"veh_type"] = veh_type+"_"+powertrain[0]+"_"+powertrain
                    temp.loc[j,"veh_powertrain"] = powertrain
                final_b2b_private = pd.concat([final_b2b_private,temp], ignore_index=True).reset_index(drop=True)

    final_b2b_private=final_b2b_private[final_b2b_private["D_truckload"]>0].reset_index(drop=True)
    final_b2b_private["payload_id"]=final_b2b_private['shipment_id'].apply(lambda x: 'B2B_' + str(int(x)))
    final_b2b_private['pu_x']=final_b2b_private["SellerID_Org"].apply(lambda x: find_coordinate(firm_dic, x, 0) )
    final_b2b_private['pu_y']=final_b2b_private["SellerID_Org"].apply(lambda x:find_coordinate(firm_dic, x, 1))
    final_b2b_private['del_x']=final_b2b_private["BuyerID_Org"].apply(lambda x:find_coordinate(firm_dic, x, 0))
    final_b2b_private['del_y']=final_b2b_private["BuyerID_Org"].apply(lambda x:find_coordinate(firm_dic, x, 1))
    final_b2b_private = final_b2b_private[final_b2b_private['pu_x']!=0]
    final_b2b_private = final_b2b_private[final_b2b_private['del_x']!=0]    
    final_b2b_private['inbound_index']=final_b2b_private['SellerCounty'].apply(lambda x: 0 if x in county_in_region else 1)
    final_b2b_private['outbound_index']=final_b2b_private['BuyerCounty'].apply(lambda x: 0 if x in county_in_region else 1)
    # seller_inbound_dic ={}
    # for _, row in final_b2b_private.iterrows():
    #     seller_inbound_dic[row['SellerID']]=row['inbound_index']
    # selected_firms['inbound_index']=selected_firms['SellerID'].apply(lambda x:seller_inbound_dic[x])
    selected_firms['inbound_index']=selected_firms['County'].apply(lambda x: 0 if x in county_in_region else 1)
    '''
    Bundling - Need to update soon 
    '''
   
    # carr_list = list(final_b2b_private["assigned_carrier"].unique())
    # for carr_id in carr_list:
    #     selected_df=final_b2b_private[final_b2b_private["assigned_carrier"]==carr_id].reset_index(drop=True)
    #     dic_ship_pair={}
    #     for _, row in selected_df.iterrows():
    #         dic_ship_pair[(row["SellerID_Org"],row["BuyerID_Org"], row["veh_type"])]= row["veh_type_agg"]
    #     for key in dic_ship_pair.keys():
    #         dip_selected_df=selected_df[(selected_df["SellerID_Org"]==key[0] ) & (selected_df["BuyerID_Org"]==key[1] ) & (selected_df["veh_type"]==key[2])].reset_index(drop=True)
    #         dip_selected_df
    return final_b2b_private, selected_firms, selected_leasings  

def b2b_forhire_distribution_channel(carrier, firms, b2b_forhire, vius, dist_df, dic_energy, selected_leasings, input_variables, dic_veh, county_in_region,mdhdv_adjustment):
    carrier_orig=carrier.copy(deep=True)
    #selected_shipper = b2b_forhire['SellerID'].unique()
    used_firms= firms[firms["SellerID"].isin(list(b2b_forhire['SellerID_Org'].unique())+list(b2b_forhire['BuyerID_Org'].unique()))]
    firm_dic={}
    for _, row in used_firms.iterrows():
        firm_dic[row['SellerID']]=(row["x"], row['y'])
    b2b_forhire = b2b_forhire[b2b_forhire["SellerID_Org"].isin(list(firm_dic.keys()))] 
    b2b_forhire = b2b_forhire[b2b_forhire["BuyerID_Org"].isin(list(firm_dic.keys()))] 
    selected_shipper = list(b2b_forhire['SellerID'].unique())
    final_b2b_forhire = pd.DataFrame()

    for seller_id in selected_shipper:
        selected_b2b_forhire=b2b_forhire[b2b_forhire["SellerID"]==seller_id].sort_values(by='Distance').reset_index(drop=True)
        SellerZone = selected_b2b_forhire.loc[0,"SellerZone"]
        selected_firms=pd.DataFrame()
        dic_fleet, ev_powertrain = fleet_composition(selected_firms, seller_id, input_variables, dic_veh)
        temp_selected_b2b_forhire=pd.DataFrame()
        for i in range(0,selected_b2b_forhire.shape[0]):
            if selected_b2b_forhire.loc[i,"ship_category"] in ["import", "export"]:
                veh_type = "hdt"
                payload = selected_b2b_forhire.loc[i,"D_truckload"]/dic_veh[veh_type]["veh_capacity"]
            else:    
                veh_type, payload = veh_type_choice(selected_b2b_forhire.loc[i,"SCTG_Group"], #selected_b2b_forhire.loc[i,"SCTG_VIUS_group"]
                                                selected_b2b_forhire.loc[i,"Distance"], 
                                                selected_b2b_forhire.loc[i,"D_truckload"], 
                                                vius, 
                                                dic_fleet, dic_veh, mdhdv_adjustment) ## need df_vius
            num_shipment=int(payload)+1
            temp=pd.concat([selected_b2b_forhire.loc[[i]]]*num_shipment, ignore_index=True)
            if num_shipment ==1:
                temp["D_truckload"]= selected_b2b_forhire.loc[i,"D_truckload"]
            else:    
                temp["D_truckload"]=dic_veh[veh_type]["veh_capacity"]
                temp["D_truckload"].iloc[-1]=selected_b2b_forhire.loc[i,"D_truckload"]-dic_veh[veh_type]["veh_capacity"]*(num_shipment-1)
            temp["payload"] = temp["D_truckload"].apply(lambda x : x/dic_veh[veh_type]["veh_capacity"])
            temp["veh_type_agg"] = veh_type
            temp["veh_powertrain_agg"] = "U"
            temp["veh_type"] = "U"
            temp["veh_powertrain"] = "U"
            temp["assigned_carrier"] = "U"
            temp_selected_b2b_forhire = pd.concat([temp_selected_b2b_forhire,temp], ignore_index=True).reset_index(drop=True)
        grouped_temp=temp_selected_b2b_forhire.groupby(["veh_type_agg", "SCTG_Group"])["payload"].agg(payload_sum ="sum", num_shipment ="count").reset_index()
        grouped_temp["assigned_carrier"]= grouped_temp.apply(lambda x:carrier_sel(SellerZone, x["veh_type_agg"], x["payload_sum"], x["num_shipment"], dist_df, carrier, "B2B", x["SCTG_Group"]), axis=1)
        temp_selected_b2b_forhire["assigned_carrier"]=temp_selected_b2b_forhire.apply(lambda x:grouped_temp[(grouped_temp["veh_type_agg"]==x["veh_type_agg"]) & (grouped_temp["SCTG_Group"]==x["SCTG_Group"])]["assigned_carrier"].values[0], axis=1)
        for i in range(0,grouped_temp.shape[0]):
            carrier_id = grouped_temp.loc[i,"assigned_carrier"]
            veh_type= grouped_temp.loc[i,"veh_type_agg"]
            veh_col_name=veh_type+"_capacity"
            numship_col_name =veh_type+"_numshipment"
            if carrier_id != "U":
                carrier.loc[carrier["BusID"]==carrier_id, veh_col_name] -= grouped_temp.loc[i,"payload_sum"]
                carrier.loc[carrier["BusID"]==carrier_id, numship_col_name] -= grouped_temp.loc[i,"num_shipment"]

        for i in range(0,temp_selected_b2b_forhire.shape[0]):
            carrier_id= temp_selected_b2b_forhire.loc[i,"assigned_carrier"]
            if carrier_id == "U":
                carrier_id = carrier_sel(SellerZone, temp_selected_b2b_forhire.loc[i,"veh_type_agg"], temp_selected_b2b_forhire.loc[i,"payload"], 1, dist_df, carrier, "B2B", temp_selected_b2b_forhire.loc[i,"SCTG_Group"])
                temp_selected_b2b_forhire.loc[i,"assigned_carrier"] = carrier_id
                veh_type= temp_selected_b2b_forhire.loc[i,"veh_type_agg"]
                veh_col_name=veh_type+"_capacity"
                numship_col_name =veh_type+"_numshipment"
                if carrier_id != "U":
                    carrier.loc[carrier["BusID"]==carrier_id, veh_col_name] -= temp_selected_b2b_forhire.loc[i,"payload"]
                    carrier.loc[carrier["BusID"]==carrier_id, numship_col_name] -= 1
        temp_selected_b2b_forhire = temp_selected_b2b_forhire[temp_selected_b2b_forhire["assigned_carrier"] != "U"].reset_index(drop=True)
        
           
        for i in range(0,temp_selected_b2b_forhire.shape[0]):    
            carrier_id= temp_selected_b2b_forhire.loc[i,"assigned_carrier"]
            veh_type = temp_selected_b2b_forhire.loc[i,"veh_type_agg"]
            dic_fleet, ev_powertrain = fleet_composition(carrier, carrier_id, input_variables, dic_veh)
            powertrain, leasing_flag=powertrain_choice(veh_type, dic_fleet, dic_energy, ev_powertrain, temp_selected_b2b_forhire.loc[i,"Distance"], temp_selected_b2b_forhire.loc[i,"payload"],selected_leasings)
            synthfirm_name = powertrain+" "+dic_veh[veh_type]["synthfirm_name"]
            if leasing_flag ==1:
                selected_leasings.loc[selected_leasings["powertrain"] == powertrain, veh_type] -= 1
                carrier.loc[carrier["BusID"] ==carrier_id, synthfirm_name] += 1 
                carrier_orig.loc[carrier["BusID"] ==carrier_id, synthfirm_name] += 1
            carrier.loc[carrier["BusID"] ==carrier_id, synthfirm_name] -= temp_selected_b2b_forhire.loc[i,"payload"]
            temp_selected_b2b_forhire.loc[i,"veh_powertrain_agg"] = powertrain     
            if powertrain == "Electric":
                temp_selected_b2b_forhire.loc[i,"veh_type"] = veh_type+"_"+"E_"+ev_powertrain 
                temp_selected_b2b_forhire.loc[i,"veh_powertrain"] = powertrain
            else:    
                temp_selected_b2b_forhire.loc[i,"veh_type"] = veh_type+"_"+powertrain[0]+"_"+powertrain
                temp_selected_b2b_forhire.loc[i,"veh_powertrain"] = powertrain        

        final_b2b_forhire= pd.concat([final_b2b_forhire,temp_selected_b2b_forhire], ignore_index=True).reset_index(drop=True)

    final_b2b_forhire=final_b2b_forhire[final_b2b_forhire["D_truckload"]>0].reset_index(drop=True)
    final_b2b_forhire=final_b2b_forhire.dropna(subset=["assigned_carrier"]).reset_index(drop=True)
    final_b2b_forhire["payload_id"]=final_b2b_forhire['shipment_id'].apply(lambda x: 'B2B_' + str(int(x)))
    final_b2b_forhire['pu_x']=final_b2b_forhire["SellerID_Org"].apply(lambda x:find_coordinate(firm_dic, x, 0))
    final_b2b_forhire['pu_y']=final_b2b_forhire["SellerID_Org"].apply(lambda x:find_coordinate(firm_dic, x, 1))
    final_b2b_forhire['del_x']=final_b2b_forhire["BuyerID_Org"].apply(lambda x:find_coordinate(firm_dic, x, 0))
    final_b2b_forhire['del_y']=final_b2b_forhire["BuyerID_Org"].apply(lambda x:find_coordinate(firm_dic, x, 1))
    final_b2b_forhire = final_b2b_forhire[final_b2b_forhire['pu_x']!=0]
    final_b2b_forhire = final_b2b_forhire[final_b2b_forhire['del_x']!=0]  
    final_b2b_forhire['inbound_index']=final_b2b_forhire['SellerCounty'].apply(lambda x: 0 if x in county_in_region else 1)
    final_b2b_forhire['outbound_index']=final_b2b_forhire['BuyerCounty'].apply(lambda x: 0 if x in county_in_region else 1)
    selected_carrier = carrier_orig[carrier_orig["BusID"].isin(list(final_b2b_forhire["assigned_carrier"].unique()))]
    selected_carrier['inbound_index']=selected_carrier['County'].apply(lambda x: 0 if x in county_in_region else 1)

    return final_b2b_forhire, selected_carrier, selected_leasings  

def b2c_forhire_distribution_channel (carrier, b2c_shipment, CBGzone_df, vius, dist_df, dic_energy, selected_leasings, input_variables, dic_veh, mdhdv_adjustment):
    carrier_orig=carrier.copy(deep=True)

    for i, _ in b2c_shipment.iterrows():
        selected_firms=pd.DataFrame()
        dic_fleet, ev_powertrain = fleet_composition(selected_firms, None, input_variables, dic_veh)       
        veh_type, payload = veh_type_choice(99,
                                0, 
                                b2c_shipment.loc[i,"D_truckload"], 
                                vius, 
                                dic_fleet, dic_veh, mdhdv_adjustment)
        b2c_shipment.loc[i,"veh_type_agg"] = veh_type
        b2c_shipment.loc[i,"assigned_carrier"]="no"
        carrier_id=carrier_sel(int(b2c_shipment.loc[i,"MESOZONE"]), b2c_shipment.loc[i,"veh_type_agg"], payload, 1, dist_df, carrier, "B2C", 99)
        b2c_shipment.loc[i,"assigned_carrier"] = carrier_id
        veh_col_name=veh_type+"_capacity"
        numship_col_name =veh_type+"_numshipment"
        if carrier_id != "U":
            carrier.loc[carrier["BusID"]==carrier_id, veh_col_name] -= payload
            carrier.loc[carrier["BusID"]==carrier_id, numship_col_name] -= 1
            
        dic_fleet, ev_powertrain = fleet_composition(carrier, carrier_id, input_variables, dic_veh)
        powertrain, leasing_flag=powertrain_choice(veh_type, dic_fleet, dic_energy, ev_powertrain, 50,payload ,selected_leasings)
        synthfirm_name = powertrain+" "+dic_veh[veh_type]["synthfirm_name"]
        if leasing_flag ==1:
            selected_leasings.loc[selected_leasings["powertrain"] == powertrain, veh_type] -= 1
            carrier.loc[carrier["BusID"] ==carrier_id, synthfirm_name] += 1 
            carrier_orig.loc[carrier["BusID"] ==carrier_id, synthfirm_name] += 1
        carrier.loc[carrier["BusID"] ==carrier_id, synthfirm_name] -= payload
        b2c_shipment.loc[i,"veh_powertrain_agg"] = powertrain     
        if powertrain == "Electric":
            b2c_shipment.loc[i,"veh_type"] = veh_type+"_"+"E_"+ev_powertrain 
            b2c_shipment.loc[i,"veh_powertrain"] = powertrain
        else:    
            b2c_shipment.loc[i,"veh_type"] = veh_type+"_"+powertrain[0]+"_"+powertrain
            b2c_shipment.loc[i,"veh_powertrain"] = powertrain
        [x,y]=random_points_in_polygon(CBGzone_df["geometry"][CBGzone_df["MESOZONE"]==str(int(b2c_shipment.loc[i,"MESOZONE"]))])
        b2c_shipment.loc[i,'del_x']=x
        b2c_shipment.loc[i,'del_y']=y      

    final_b2c_forhire = b2c_shipment[b2c_shipment["assigned_carrier"] != "U"].reset_index(drop=True)
    final_b2c_forhire=final_b2c_forhire[final_b2c_forhire["D_truckload"]>0].reset_index(drop=True)
    final_b2c_forhire=final_b2c_forhire.dropna(subset=["assigned_carrier"]).reset_index(drop=True)
    final_b2c_forhire["payload_id"]=final_b2c_forhire['household_gr_id'].apply(lambda x: 'B2C_' + str(int(x)))
    final_b2c_forhire.loc[:,'inbound_index']=0
    final_b2c_forhire.loc[:,'outbound_index']=0
    selected_carrier = carrier_orig[carrier_orig["BusID"].isin(list(final_b2c_forhire["assigned_carrier"].unique()))]
    selected_carrier.loc[:,'inbound_index']=0 #B2C is internal
    
    return final_b2c_forhire, selected_carrier, selected_leasings          


def ex_seller_zone_to_boundary(sellerzone,df_ex,dic_ex):
    if dic_ex=={}:
        [[new_zone,new_x, new_y]]= df_ex[df_ex['MESOZONE']==sellerzone][['BoundaryZONE','x',"y"]].values.tolist()
        return new_zone,new_x, new_y
    else:
        new_zone=externalzone_psrc(df_ex[df_ex["MESOZONE"]==sellerzone]["Boundary_group"].values[0])
        new_x=dic_ex[new_zone][0]
        new_y=dic_ex[new_zone][1]
    return new_zone,new_x, new_y    
def depot_time_depart_v2(df_dpt_dist,ship_type, veh_type):
    if ship_type == 'B2C': 
        df_dpt_dist=df_dpt_dist[df_dpt_dist["veh_type"]==veh_type]
        pro_time= random.uniform(0, 1)    
        sel_time=df_dpt_dist[(df_dpt_dist['cdf_low']<= pro_time) & (df_dpt_dist['cdf_up'] >  pro_time)]['start_hour'].values[0]    
        if random.uniform(0, 1) <= 0.85:
            d_time=random.randrange(sel_time*60, (sel_time+1)*60, 10) 
        else:     
            d_time=random.randrange(sel_time*60, (sel_time+1)*60, 10)+ random.randrange(5*60, 6*60, 10)
        if d_time < 13*60: 
            d_time_upper = d_time +5*60
        else:
            d_time_upper = 22*60       
    elif ship_type == 'B2B':
        df_dpt_dist=df_dpt_dist[df_dpt_dist["veh_type"]==veh_type]
        pro_time= random.uniform(0, 1)    
        sel_time=df_dpt_dist[(df_dpt_dist['cdf_low']<= pro_time) & (df_dpt_dist['cdf_up'] >  pro_time)]['start_hour'].values[0]  
        if sel_time>=10 and sel_time <16: 
            d_time =random.randrange(sel_time*60, (sel_time+1)*60, 10)- random.randrange(2*60, 6*60, 10)
        elif sel_time>=16 and sel_time <20:
            d_time =random.randrange(sel_time*60, (sel_time+1)*60, 10)- random.randrange(4*60, 10*60, 10)
        elif sel_time>=20:
            d_time =random.randrange(sel_time*60, (sel_time+1)*60, 10)- random.randrange(6*60, 18*60, 10)         
        else:     
            d_time =random.randrange(sel_time*60, (sel_time+1)*60, 10)
        if d_time < 18*60: 
            d_time_upper = (24+4)*60
        else:
            d_time_upper = d_time+ 5*60   
    else:
        print ("Please define shipment type: B2B or B2C")            
    return d_time, d_time_upper
def stop_duration (load, load_min, load_max):
    temp =int(np.random.gamma(2, 1, 1)[0]*((load -load_min)/(load_max-load_min))*60)
    if temp < 5:
        return random.randint(5,20)
    elif temp >70:
        return random.randint(60,90)
    else:
        return temp
def b2b_create_output(final_b2b_private,final_b2b_forhire, selected_firms, selected_carrier, ship_type,ex_zone,df_dpt_dist, input_variables, dic_veh,dic_ex, gdf_TAZ):
    final_b2b_private = final_b2b_private[final_b2b_private["veh_type_agg"]!="U"]
    final_b2b_forhire = final_b2b_forhire[final_b2b_forhire["veh_type_agg"]!="U"]
    final_b2b_private["veh_type_output"] = final_b2b_private["veh_type"].apply(lambda x: x[:5])
    final_b2b_forhire["veh_type_output"] = final_b2b_forhire["veh_type"].apply(lambda x: x[:5])
    final_b2b_private_ship= final_b2b_private.groupby(["assigned_carrier","veh_type_output"])["assigned_carrier"].count().reset_index(name='num_shipment')
    final_b2b_forhire_ship= final_b2b_forhire.groupby(["assigned_carrier","veh_type_output"])["assigned_carrier"].count().reset_index(name='num_shipment')
    output_veh_dic={}
    for veh_type in input_variables['vehicle_type']:
        for fuel_type in input_variables['fuel_type']: 
            syn_column= fuel_type +" "+dic_veh[veh_type]["synthfirm_name"]
            frism_column = veh_type+"_"+fuel_type[0]
            if syn_column in selected_firms.columns:
                output_veh_dic[frism_column]=syn_column

    # Create carrier by aggregate vehicle type
    dic_carrier_id={}
    for _, row in final_b2b_private.iterrows():
        new_carrier_id = row["assigned_carrier"]+"_"+row["veh_type_agg"]
        dic_carrier_id[new_carrier_id]={"org_id":row["assigned_carrier"], "veh_type": row["veh_type_agg"]}

    dic_firm ={}
    for _,row in selected_firms.iterrows():
        dic_basic = {"MESOZONE": row["MESOZONE"],
                    "x": row ["x"],
                    "y": row ["y"],
                    "ev_type":row ["EV_powertrain (if any)"],
                    "inbound_index": row["inbound_index"]}
        # dic_fleet={}
        # for veh_type in output_veh_dic.keys():
        #     dic_fleet[veh_type]= row[output_veh_dic[veh_type]]
        # dic_fleet={}
        for veh_type in output_veh_dic.keys():
            dic_basic[veh_type]= row[output_veh_dic[veh_type]]
        dic_firm[row["SellerID"]] = dic_basic

    carriers = []
    for carrier_id in dic_carrier_id.keys():
        if dic_firm[dic_carrier_id[carrier_id]["org_id"]]['inbound_index'] ==1:
            # print (dic_firm[dic_carrier_id[carrier_id]["org_id"]]["MESOZONE"])
            zone, x, y =ex_seller_zone_to_boundary(dic_firm[dic_carrier_id[carrier_id]["org_id"]]["MESOZONE"],ex_zone,dic_ex)
        else:
            zone=dic_firm[dic_carrier_id[carrier_id]["org_id"]]["MESOZONE"]
            x= dic_firm[dic_carrier_id[carrier_id]["org_id"]]["x"]
            y= dic_firm[dic_carrier_id[carrier_id]["org_id"]]["y"]
        departure_lower, departure_upper= depot_time_depart_v2(df_dpt_dist,ship_type,dic_carrier_id[carrier_id]["veh_type"])
                
        row = {'carrier_id': carrier_id ,
                'firm_id': dic_carrier_id[carrier_id]["org_id"] ,
                'depot_zone': zone,
                'contract_firms': dic_carrier_id[carrier_id]["org_id"],
                'depot_lower': departure_lower,
                'depot_upper': departure_upper,
                'depot_time_before': random.randrange(5,30, 5),
                'depot_time_after': random.randrange(5,30, 5),
                'c_x': x,
                'c_y': y,
                'true_depot_zone': dic_firm[dic_carrier_id[carrier_id]["org_id"]]["MESOZONE"],
                "ev_type": dic_firm[dic_carrier_id[carrier_id]["org_id"]]["ev_type"]}

        for veh_type in output_veh_dic.keys():
            try:
                num_shipment=final_b2b_private_ship[(final_b2b_private_ship["assigned_carrier"] == dic_carrier_id[carrier_id]["org_id"]) &(final_b2b_private_ship["veh_type_output"] == veh_type)]["num_shipment"].values[0]
            except:
                num_shipment =0 
            num_veh= dic_firm[dic_carrier_id[carrier_id]["org_id"]][veh_type]
            if num_veh ==0 and num_shipment ==0 :        
                row[veh_type]= num_veh
            else:
                if np.ceil(num_shipment*0.7) < num_veh:
                   row[veh_type]= num_veh
                else:
                   row[veh_type]= np.ceil(num_shipment*0.7)      

        carriers.append(row)

    dic_carrier_id={}
    for _, row in final_b2b_forhire.iterrows():
        new_carrier_id = row["assigned_carrier"]+"_"+row["veh_type_agg"]
        dic_carrier_id[new_carrier_id]={"org_id":row["assigned_carrier"], "veh_type": row["veh_type_agg"]}

    dic_firm ={}
    for _,row in selected_carrier.iterrows():
        dic_basic = {"MESOZONE": row["MESOZONE"],
                    "x": row ["x"],
                    "y": row ["y"],
                    "ev_type":row ["EV_powertrain (if any)"],
                    "inbound_index": row["inbound_index"]}
 
        for veh_type in output_veh_dic.keys():
            dic_basic[veh_type]= row[output_veh_dic[veh_type]]
        dic_firm[row["BusID"]] = dic_basic
    for carrier_id in dic_carrier_id.keys():
        if dic_firm[dic_carrier_id[carrier_id]["org_id"]]['inbound_index'] ==1:
            # print (dic_firm[dic_carrier_id[carrier_id]["org_id"]]["MESOZONE"])
            zone, x, y =ex_seller_zone_to_boundary(dic_firm[dic_carrier_id[carrier_id]["org_id"]]["MESOZONE"],ex_zone,dic_ex)
        else:
            zone=dic_firm[dic_carrier_id[carrier_id]["org_id"]]["MESOZONE"]
            x= dic_firm[dic_carrier_id[carrier_id]["org_id"]]["x"]
            y= dic_firm[dic_carrier_id[carrier_id]["org_id"]]["y"]
        departure_lower, departure_upper= depot_time_depart_v2(df_dpt_dist,ship_type,dic_carrier_id[carrier_id]["veh_type"])
                
        row = {'carrier_id': carrier_id ,
                'firm_id': dic_carrier_id[carrier_id]["org_id"] ,
                'depot_zone': zone,
                'contract_firms': dic_carrier_id[carrier_id]["org_id"],
                'depot_lower': departure_lower,
                'depot_upper': departure_upper,
                'depot_time_before': random.randrange(5,30, 5),
                'depot_time_after': random.randrange(5,30, 5),
                'c_x': x,
                'c_y': y,
                'true_depot_zone': dic_firm[dic_carrier_id[carrier_id]["org_id"]]["MESOZONE"],
                "ev_type": dic_firm[dic_carrier_id[carrier_id]["org_id"]]["ev_type"]}

        for veh_type in output_veh_dic.keys():
            try:
                num_shipment=final_b2b_forhire_ship[(final_b2b_forhire_ship["assigned_carrier"] == dic_carrier_id[carrier_id]["org_id"]) &(final_b2b_forhire_ship["veh_type_output"] == veh_type)]["num_shipment"].values[0]
            except:
                num_shipment =0 
            num_veh= dic_firm[dic_carrier_id[carrier_id]["org_id"]][veh_type]
            if num_veh ==0 and num_shipment ==0 :        
                row[veh_type]= num_veh
            else:
                if np.ceil(num_shipment*0.8) < num_veh:
                   row[veh_type]= num_shipment
                else:
                   row[veh_type]= np.ceil(num_shipment*0.8)      
        carriers.append(row)
    carriers = pd.DataFrame(carriers)

    payloads = []
    load_min =final_b2b_private["D_truckload"].min()
    load_max = final_b2b_private["D_truckload"].max()

    for _, row in final_b2b_private.iterrows():
        if row['outbound_index'] ==1:
            # print (row["BuyerZone"])
            del_zone, del_x, del_y =ex_seller_zone_to_boundary(row["BuyerZone"],ex_zone,dic_ex)
            del_tw_upper = (24+8)*60
            ship_index = "external" 
        else:
            del_zone= row["BuyerZone"]
            del_x= row["del_x"]
            del_y= row["del_y"]
            del_tw_upper = (24+2)*60 
            ship_index = "internal"

        if row['inbound_index'] ==1:
            # print (row["SellerZone"])
            pu_zone, pu_x, pu_y =ex_seller_zone_to_boundary(row["SellerZone"],ex_zone, dic_ex)

        else:
            pu_zone= row["SellerZone"]
            pu_x= row["pu_x"]
            pu_y= row["pu_y"]
               
        carrier_id = row["assigned_carrier"]+"_"+row["veh_type_agg"]
        depot_lower = carriers[carriers["carrier_id"]==carrier_id]["depot_lower"].values[0]
        del_tw_lower = depot_lower


        row = {'payload_id': row["payload_id"], 
        'carrier_id':carrier_id ,
        'sequence_id': np.nan,
        'tour_id':np.nan,
        'commodity': row['SCTG_Group'],
        'weight': row["D_truckload"],
        'job':'delivery',
        'pu_zone': pu_zone ,
        'del_zone': del_zone,
        'pu_stop_duration': np.nan,
        'del_stop_duration': stop_duration(row["D_truckload"],load_min, load_max),
        'pu_tw_lower': np.nan ,
        'pu_tw_upper': np.nan ,
        'del_tw_lower': del_tw_lower,
        'del_tw_upper': del_tw_upper,
        'pu_arrival_time': np.nan ,
        'del_arrival_time': np.nan ,
        'veh_type': row["veh_type"],
        'del_x': del_x,
        'del_y': del_y,
        'pu_x': pu_x,
        'pu_y': pu_y,
        'ship_index': ship_index,
        'true_pu_zone': row["SellerZone"], 
        'true_del_zone': row["BuyerZone"] , 
        'truck_mode': row["mode_choice"], 
        'BuyerNAICS': row["BuyerNAICS"],
        'SellerNAICS': row["SellerNAICS"],
        'outbound_index':row['outbound_index'],
        'inbound_index':row['inbound_index'] 
        }
        payloads.append(row)

    load_min =final_b2b_forhire["D_truckload"].min()
    load_max = final_b2b_forhire["D_truckload"].max()
    for _, row in final_b2b_forhire.iterrows():
        if row['outbound_index'] ==1:
            # print (row["BuyerZone"])
            del_zone, del_x, del_y =ex_seller_zone_to_boundary(row["BuyerZone"],ex_zone,dic_ex)
            del_tw_upper = (24+8)*60
            ship_index = "external" 
        else:
            del_zone= row["BuyerZone"]
            del_x= row["del_x"]
            del_y= row["del_y"]
            del_tw_upper = (24+2)*60 
            ship_index = "internal" 
        if row['inbound_index'] ==1:
            # print (row["SellerZone"])
            pu_zone, pu_x, pu_y =ex_seller_zone_to_boundary(row["SellerZone"],ex_zone,dic_ex)
            pu_tw_upper = (24+4)*60
        else:
            pu_zone= row["SellerZone"]
            pu_x= row["pu_x"]
            pu_y= row["pu_y"]
            pu_tw_upper = (24+2)*60 
    
        carrier_id = row["assigned_carrier"]+"_"+row["veh_type_agg"]
        depot_lower = carriers[carriers["carrier_id"]==carrier_id]["depot_lower"].values[0]
        pu_stop = stop_duration(row["D_truckload"],load_min, load_max)
        del_stop=stop_duration(row["D_truckload"],load_min, load_max)

        pu_tw_lower= depot_lower
        del_tw_lower = pu_tw_lower + pu_stop
        

        row = {'payload_id': row["payload_id"], 
        'carrier_id':carrier_id ,
        'sequence_id': np.nan,
        'tour_id':np.nan,
        'commodity': row['SCTG_Group'],
        'weight': row["D_truckload"],
        'job':'pickup_delivery',
        'pu_zone': pu_zone ,
        'del_zone': del_zone,
        'pu_stop_duration': pu_stop,
        'del_stop_duration': del_stop,
        'pu_tw_lower':pu_tw_lower ,
        'pu_tw_upper': pu_tw_upper ,
        'del_tw_lower': del_tw_lower,
        'del_tw_upper': del_tw_upper,
        'pu_arrival_time': np.nan ,
        'del_arrival_time': np.nan ,
        'veh_type': row["veh_type"],
        'del_x': del_x,
        'del_y': del_y,
        'pu_x': pu_x,
        'pu_y': pu_y,
        'ship_index': ship_index,
        'true_pu_zone': row["SellerZone"], 
        'true_del_zone': row["BuyerZone"] , 
        'truck_mode': row["mode_choice"], 
        'BuyerNAICS': row["BuyerNAICS"],
        'SellerNAICS': row["SellerNAICS"],
        'outbound_index':row['outbound_index'],
        'inbound_index':row['inbound_index']  
        }
        payloads.append(row)
    payloads = pd.DataFrame(payloads)
    if gdf_TAZ.shape[0]==0:
        pass
    else:
        carriers, payloads = covert_mesozone_to_local_taz(carriers, payloads, gdf_TAZ)
    return carriers, payloads 

def b2c_create_output(final_b2c_forhire,selected_carrier,df_dpt_dist,input_variables, ship_type, dic_veh,gdf_TAZ):
    final_b2c_forhire = final_b2c_forhire[final_b2c_forhire["veh_type_agg"]!="U"]
    final_b2c_forhire["veh_type_output"] = final_b2c_forhire["veh_type"].apply(lambda x: x[:5])
    final_b2c_forhire_ship= final_b2c_forhire.groupby(["assigned_carrier","veh_type_output"])["assigned_carrier"].count().reset_index(name='num_shipment')
    output_veh_dic={}
    for veh_type in input_variables['vehicle_type']:
        for fuel_type in input_variables['fuel_type']: 
            syn_column= fuel_type +" "+dic_veh[veh_type]["synthfirm_name"]
            frism_column = veh_type+"_"+fuel_type[0]
            if syn_column in selected_carrier.columns:
                output_veh_dic[frism_column]=syn_column

    carriers = []
    dic_carrier_id={}
    for _, row in final_b2c_forhire.iterrows():
        new_carrier_id = row["assigned_carrier"]+"_"+row["veh_type_agg"]
        dic_carrier_id[new_carrier_id]={"org_id":row["assigned_carrier"], "veh_type": row["veh_type_agg"]}

    dic_firm ={}
    for _,row in selected_carrier.iterrows():
        dic_basic = {"MESOZONE": row["MESOZONE"],
                    "x": row ["x"],
                    "y": row ["y"],
                    "ev_type":row ["EV_powertrain (if any)"],
                    "inbound_index": row["inbound_index"]}
 
        for veh_type in output_veh_dic.keys():
            dic_basic[veh_type]= row[output_veh_dic[veh_type]]
        dic_firm[row["BusID"]] = dic_basic

    for carrier_id in dic_carrier_id.keys():

        zone=dic_firm[dic_carrier_id[carrier_id]["org_id"]]["MESOZONE"]
        x= dic_firm[dic_carrier_id[carrier_id]["org_id"]]["x"]
        y= dic_firm[dic_carrier_id[carrier_id]["org_id"]]["y"]
        departure_lower, departure_upper= depot_time_depart_v2(df_dpt_dist,ship_type,dic_carrier_id[carrier_id]["veh_type"])
                
        row = {'carrier_id': carrier_id ,
                'firm_id': dic_carrier_id[carrier_id]["org_id"] ,
                'depot_zone': zone,
                'contract_firms': dic_carrier_id[carrier_id]["org_id"],
                'depot_lower': departure_lower,
                'depot_upper': departure_upper,
                'depot_time_before': random.randrange(5,30, 5),
                'depot_time_after': random.randrange(5,30, 5),
                'c_x': x,
                'c_y': y,
                'true_depot_zone': dic_firm[dic_carrier_id[carrier_id]["org_id"]]["MESOZONE"],
                "ev_type": dic_firm[dic_carrier_id[carrier_id]["org_id"]]["ev_type"]}

        for veh_type in output_veh_dic.keys():
            try:
                num_shipment=final_b2c_forhire_ship[(final_b2c_forhire_ship["assigned_carrier"] == dic_carrier_id[carrier_id]["org_id"]) &(final_b2c_forhire_ship["veh_type_output"] == veh_type)]["num_shipment"].values[0]
            except:
                num_shipment =0 
            num_veh= dic_firm[dic_carrier_id[carrier_id]["org_id"]][veh_type]
            if num_veh ==0 and num_shipment ==0 :        
                row[veh_type]= num_veh
            else:
                if np.ceil(num_shipment*0.8) < num_veh:
                   row[veh_type]= num_shipment
                else:
                   row[veh_type]= np.ceil(num_shipment*0.8)      
        carriers.append(row)
    carriers = pd.DataFrame(carriers)

    payloads = []
    for _, row in final_b2c_forhire.iterrows():
        carrier_id = row["assigned_carrier"]+"_"+row["veh_type_agg"]
        del_zone= int(row["MESOZONE"])
        del_x= row["del_x"]
        del_y= row["del_y"]
        del_tw_upper = (21)*60 
        ship_index = "internal" 

        pu_zone= carriers[carriers["carrier_id"]==carrier_id]["depot_zone"].values[0]
        pu_x= carriers[carriers["carrier_id"]==carrier_id]["c_x"].values[0]
        pu_y= carriers[carriers["carrier_id"]==carrier_id]["c_y"].values[0]
        pu_tw_upper = (21)*60 

        
        depot_lower = carriers[carriers["carrier_id"]==carrier_id]["depot_lower"].values[0]
        pu_stop = 0
        del_stop=row["tour_tt"]

        pu_tw_lower= depot_lower
        del_tw_lower = pu_tw_lower + pu_stop
        

        row = {'payload_id': row["payload_id"], 
        'carrier_id':carrier_id ,
        'sequence_id': np.nan,
        'tour_id':np.nan,
        'commodity': 5,
        'weight': row["D_truckload"],
        'job':'delivery',
        'pu_zone': pu_zone ,
        'del_zone': del_zone,
        'pu_stop_duration': pu_stop,
        'del_stop_duration': del_stop,
        'pu_tw_lower':pu_tw_lower ,
        'pu_tw_upper': pu_tw_upper ,
        'del_tw_lower': del_tw_lower,
        'del_tw_upper': del_tw_upper,
        'pu_arrival_time': np.nan ,
        'del_arrival_time': np.nan ,
        'veh_type': row["veh_type"],
        'del_x': del_x,
        'del_y': del_y,
        'pu_x': pu_x,
        'pu_y': pu_y,
        'ship_index': ship_index,
        'true_pu_zone': pu_zone, 
        'true_del_zone': del_zone, 
        'truck_mode': "For-hire Truck", 
        'BuyerNAICS': "492000",
        'SellerNAICS': "492000",
        'outbound_index':row['outbound_index'],
        'inbound_index':row['inbound_index']  
        }
        payloads.append(row)
    payloads = pd.DataFrame(payloads)
    if gdf_TAZ.shape[0]==0:
        pass
    else:
        carriers, payloads = covert_mesozone_to_local_taz(carriers, payloads, gdf_TAZ)    
    return carriers, payloads 

def b2c_ondemand_distribution_channel(df_input_org, ondemand_loc, dist_df, CBGzone_df, sel_county, good_type):
    def store_over_county(county, select_county):
        if county == select_county:
            return 1
        else: return 0.4

    def assign_store(df_group):
        sel_df_group= df_group[df_group["travel_time"] <=30].reset_index()
        if sel_df_group.shape[0] ==0:
            sel_df_group= df_group[df_group["travel_time"] <=40].reset_index()
        if sel_df_group.shape[0] ==0:
            sel_df_group= df_group[df_group["travel_time"] <=60].reset_index()
        if sel_df_group.shape[0] ==0:
            sel_df_group= df_group[df_group["travel_time"] <=90].reset_index()    
        if sel_df_group.shape[0] >0:    
            sel_df_group["travel_time_bin"]=sel_df_group["travel_time"].apply(lambda x: int(x/10+1)*10)
            tt_inverse=1/sel_df_group["travel_time_bin"].unique()
            tt_inverse.sum()
            sel_df_group["pro"]=sel_df_group["travel_time_bin"].apply(lambda x: (1/x)/tt_inverse.sum())
            weighted_prob_sum= (sel_df_group["pro"]*sel_df_group["num_store"]).sum()
            sel_df_group["weighted_pro"]= sel_df_group.apply(lambda x: (x['pro']*x["num_store"])/weighted_prob_sum, axis=1)
            org= random.choices(list(sel_df_group['MESOZONE']), list(sel_df_group["pro"]),k=1)[0]
        else:
            org=0
        return org
    def time_normal(mean, std, min_time,max_time):
        time = (np.random.normal(0,std)+mean)*60
        if time < min_time*60 or time > max_time*60 :
            time= random.randrange((mean)*60,max_time*60, 10)
        return int(time)   
    def order_time(goods_type):
        if goods_type == "grocery":
            d_time= random.randrange(8*60,19*60, 10)
        elif goods_type == "food":            
            if random.uniform(0, 1) <= 0.4:
                d_time =time_normal(12, 2, 10, 16)
            else:     
                d_time =time_normal(18, 2, 15, 21)

        return d_time *60
    def tt_cal(org_meso, dest_meso, dist_df):
        dist = dist_df[(dist_df['Origin']==org_meso) & (dist_df['Destination']==dest_meso)].dist.values[0]
        if (dist == 0):
            dist =random.uniform(1,10)
        return 60*dist/30 # minutes

    ondemand_loc['MESOZONE'] = ondemand_loc['MESOZONE'].astype('int64')
    CBGzone_df['MESOZONE'] = CBGzone_df['MESOZONE'].astype('int64')
    ondemand_loc['Classified 0424'] = ondemand_loc['Classified 0424'].str.lower()
    loc_df= ondemand_loc[ondemand_loc["Classified 0424"]==good_type].reset_index()
    loc_group=  loc_df.groupby(['MESOZONE','County'])['MESOZONE'].agg(num_store='count').reset_index()
    loc_group["store_over_county"]=loc_group['County'].apply(lambda x: store_over_county(x,sel_county))

    df_input=df_input_org.groupby(['MESOZONE'])["household_id"].agg(n_households='count').reset_index()

    payloads = pd.DataFrame(columns = ["payloadId",
                            "sequenceRank",
                            "tourId", 
                            "payloadType",	
                            "weightInlb",	
                            "cummulativeWeightInlb",	
                            "requestType",	
                            "locationZone",
                            "estimatedTimeOfArrivalInSec",	
                            "arrivalTimeWindowInSec_lower",	
                            "arrivalTimeWindowInSec_upper",	
                            "operationDurationInSec",	
                            "locationZone_x",	
                            "locationZone_y",	
                            "true_locationZone",
                            "BuyerNAICS",	
                            "SellerNAICS",	
                            "truck_mode"])
    n=0
    if df_input.shape[0]>0:
        for i in range(0,df_input.shape[0]):
            dest_mesoid= df_input["MESOZONE"].loc[i]
            if loc_group.shape[0] >50:
                sub_loc_group=loc_group.sample(n=50, weights='store_over_county').reset_index(drop=True)
            else:
                sub_loc_group=loc_group    
            sub_loc_group["travel_time"]=sub_loc_group['MESOZONE'].apply(lambda x: tt_cal(x,dest_mesoid, dist_df))
            for n_hh in range(0, df_input["n_households"].loc[i]):

                [dest_x,dest_y]=random_points_in_polygon(CBGzone_df.geometry[CBGzone_df.MESOZONE==dest_mesoid])
                org_geoid=assign_store(sub_loc_group)
                if org_geoid !=0:
                    selcted_loc_df = loc_df[loc_df["MESOZONE"]==org_geoid]
                    [[org_y,org_x]]=selcted_loc_df[["latitude", "longitude"]].sample(n=1).values.tolist()
                    tt=sub_loc_group[sub_loc_group["MESOZONE"]==org_geoid]["travel_time"].values[0]
                    org_mesoid= CBGzone_df[CBGzone_df['MESOZONE']==org_geoid]['MESOZONE'].values[0]

                    payloadId=good_type+"_"+str(n)
                    weightInlb= random.randrange(0,10)
                    org_time= order_time(good_type)
                    org_dwell= random.randrange(5,20)*60
                    dest_time= org_time +org_dwell+ int(tt*60)
                    dest_dwell= random.randrange(2,10)*60

                    temp_org=pd.DataFrame(data={"payloadId": [payloadId],
                            "sequenceRank":[0],
                            "tourId": [n], 
                            "payloadType": [5],	
                            "weightInlb": [weightInlb],	
                            "cummulativeWeightInlb": [weightInlb] ,	
                            "requestType": [3],	
                            "locationZone": [org_mesoid] ,
                            "estimatedTimeOfArrivalInSec": [org_time],		
                            "arrivalTimeWindowInSec_lower":[7*60*60],	
                            "arrivalTimeWindowInSec_upper":[22*60*60],	
                            "operationDurationInSec": [org_dwell],	
                            "locationZone_x": [org_x],	
                            "locationZone_y": [org_y],	
                            "true_locationZone": [org_mesoid],
                            "BuyerNAICS": ["NA"],	
                            "SellerNAICS": ["NA"],	
                            "truck_mode": ["ondemand"]})
                    temp_dest=pd.DataFrame(data={"payloadId": [payloadId],
                            "sequenceRank":[1],
                            "tourId": [n], 
                            "payloadType": [5],	
                            "weightInlb": [-weightInlb],	
                            "cummulativeWeightInlb": [0] ,	
                            "requestType": [3],	
                            "locationZone": [dest_mesoid] ,
                            "estimatedTimeOfArrivalInSec": [dest_time],		
                            "arrivalTimeWindowInSec_lower":[7*60*60],	
                            "arrivalTimeWindowInSec_upper":[22*60*60],	
                            "operationDurationInSec": [dest_dwell],	
                            "locationZone_x": [dest_x],	
                            "locationZone_y": [dest_y],	
                            "true_locationZone": [dest_mesoid],
                            "BuyerNAICS": ["NA"],	
                            "SellerNAICS": ["NA"],	
                            "truck_mode": ["ondemand"]})
                    n=n+1
                    payloads=pd.concat([payloads,temp_org, temp_dest],ignore_index=True)

    return payloads
def veh_type_create(dic_energy, dic_veh):
    vehicle_types= pd.DataFrame()

    for veh_class in dic_energy.keys():
        for veh_fuel in dic_energy[veh_class]:
            if veh_fuel == "Diesel":
                mid_fuel="D"
            elif veh_fuel == "Gasoline":
                mid_fuel="G"
            else:
                mid_fuel="E"

            temp= pd.DataFrame(data={'veh_type_id': [veh_class+"_"+mid_fuel+"_"+veh_fuel],
                                'veh_category': [veh_fuel+" "+dic_veh[veh_class]["synthfirm_name"]],
                                'veh_class':[dic_veh[veh_class]["synthfirm_name"]],
                                'body_type':['NA'],
                                'commodities':[[1,2,3,4,5]],
                                'weight':[dic_veh[veh_class]["veh_weight"]], 
                                'length':['NA'],
                                'payload_capacity_weight':[dic_veh[veh_class]["veh_capacity"]],
                                'payload_capacity_cbf':['NA'],
                                'max_speed(mph)':[dic_veh[veh_class]["speed"]],
                                'primary_fuel_type':veh_fuel,
                                'secondary_fuel_type':['NA'],
                                'primary_fuel_rate':[dic_energy[veh_class][veh_fuel]],
                                'secondary_fuel_rate':['NA'],
                                'Automation level':['NA'],
                                'monetary cost':['NA']})
            vehicle_types=pd.concat([vehicle_types,temp], ignore_index=True).reset_index(drop=True)                       

    return vehicle_types

