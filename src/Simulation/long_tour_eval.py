# %%
import pandas as pd
import numpy as np

county_list=[1, 13, 41, 55, 75, 81, 85, 95, 97]
target_year="2018"
scenario="Base"
f_dir= "../../..//Results_from_HPC_sfn_v1/"
f_dir_t="../../..//Results_from_HPC_sfn_v1/Tour_plan/{}_all/".format(target_year)

# ship_type = "B2B"
# B2B_S_carrier=pd.DataFrame()
# B2B_S_payload=pd.DataFrame()
# for c in county_list: 
#     S_carrier=  pd.read_csv(f_dir+"Shipment2Fleet/2018/{}_carrier_county{}_shipall_A_s{}_y{}_sr10.csv".format(ship_type, c, scenario,target_year))
#     S_payload=  pd.read_csv(f_dir+"Shipment2Fleet/2018/{}_payload_county{}_shipall_A_s{}_y{}_sr10.csv".format(ship_type, c, scenario,target_year))
#     B2B_S_carrier=pd.concat([B2B_S_carrier,S_carrier], ignore_index=True).reset_index(drop=True)
#     B2B_S_payload=pd.concat([B2B_S_payload,S_payload], ignore_index=True).reset_index(drop=True)
# ship_type = "B2C"
# B2C_S_carrier=pd.DataFrame()
# B2C_S_payload=pd.DataFrame()
# for c in county_list: 
#     S_carrier=  pd.read_csv(f_dir+"Shipment2Fleet/2018/{}_carrier_county{}_shipall_s{}_y{}_sr10.csv".format(ship_type, c, scenario,target_year))
#     S_payload=  pd.read_csv(f_dir+"Shipment2Fleet/2018/{}_payload_county{}_shipall_s{}_y{}_sr10.csv".format(ship_type, c, scenario,target_year))
#     B2C_S_carrier=pd.concat([B2C_S_carrier,S_carrier], ignore_index=True).reset_index(drop=True)
#     B2C_S_payload=pd.concat([B2C_S_payload,S_payload], ignore_index=True).reset_index(drop=True)

# %%
# read long_tour_file from Haitam
long_tour_file= pd.read_csv(f_dir+"baseline-tours-350miles_sfbay.csv")
long_tour_file["FRISM_time"]=0
long_tour_file["B-F_time"]=0
B2B_L_carrier=pd.DataFrame()
B2B_L_payload=pd.DataFrame()
B2C_L_carrier=pd.DataFrame()
B2C_L_payload=pd.DataFrame()

for i in range(0,long_tour_file.shape[0]):
    # find carrier ID and Vehicle ID to indentify tour ID 
    tourTime_BEAM= long_tour_file.loc[i,'tourTime']
    id_parsing= long_tour_file.loc[i,'vehicle'].split("-")
    ship_type= id_parsing[1].upper()
    vehicleId = int(id_parsing[len(id_parsing)-1])
    carrierId= ship_type
    for j in range(3,len(id_parsing)-1 ):
        if id_parsing[j] == 'd':
            add_str= "D"
        else: add_str=  id_parsing[j]   
        carrierId= carrierId+"_"+add_str
 

    df_payload = pd.read_csv(f_dir_t+"{0}_all_payload_s{1}_y{2}.csv".format(ship_type,scenario,target_year))
    df_tour = pd.read_csv(f_dir_t+"{0}_all_freight_tours_s{1}_y{2}.csv".format(ship_type,scenario,target_year))
    df_carrier = pd.read_csv(f_dir_t+"{0}_all_carrier_s{1}_y{2}.csv".format(ship_type,scenario,target_year))

    tourId= df_carrier[(df_carrier["carrierId"]==carrierId) & (df_carrier["vehicleId"]==vehicleId)]["tourId"].values[0]

    sel_tour =df_payload[df_payload["tourId"]==tourId ].reset_index(drop=True)
    # county info
    c=sel_tour.loc[0,"payloadId"].split("_")[0]
    # cal FRISM travel time and comparing it with BEAM
    tourTime_FRISM= sel_tour.loc[sel_tour.index[-1],'estimatedTimeOfArrivalInSec']- sel_tour.loc[0,'estimatedTimeOfArrivalInSec']
    long_tour_file.loc[i,"FRISM_time"]=tourTime_FRISM
    long_tour_file.loc[i,"B-F_time"]=tourTime_BEAM-tourTime_FRISM
 
    if ship_type =="B2B":
        S_carrier=  pd.read_csv(f_dir+"Shipment2Fleet/2018/{}_carrier_county{}_shipall_A_s{}_y{}_sr10.csv".format(ship_type, c, scenario,target_year))
        S_payload=  pd.read_csv(f_dir+"Shipment2Fleet/2018/{}_payload_county{}_shipall_A_s{}_y{}_sr10.csv".format(ship_type, c, scenario,target_year))
        sel_carr=  S_carrier[S_carrier["carrier_id"]==carrierId].reset_index(drop=True)
        sel_payload =  S_payload[S_payload["carrier_id"]==carrierId].reset_index(drop=True)
        B2B_L_carrier=pd.concat([B2B_L_carrier,sel_carr], ignore_index=True).reset_index(drop=True)
        B2B_L_payload=pd.concat([B2B_L_payload,sel_payload], ignore_index=True).reset_index(drop=True)
    elif ship_type =="B2C":
        S_carrier=  pd.read_csv(f_dir+"Shipment2Fleet/2018/{}_carrier_county{}_shipall_s{}_y{}_sr10.csv".format(ship_type, c, scenario,target_year))
        S_payload=  pd.read_csv(f_dir+"Shipment2Fleet/2018/{}_payload_county{}_shipall_s{}_y{}_sr10.csv".format(ship_type, c, scenario,target_year))
        sel_carr=  S_carrier[S_carrier["carrier_id"]==carrierId].reset_index(drop=True)
        sel_payload =  S_payload[S_payload["carrier_id"]==carrierId].reset_index(drop=True)
        B2C_L_carrier=pd.concat([B2C_L_carrier,sel_carr], ignore_index=True).reset_index(drop=True)
        B2C_L_payload=pd.concat([B2C_L_payload,sel_payload], ignore_index=True).reset_index(drop=True)

long_tour_file.to_csv(f_dir+"long_tour_comp_sfbay.csv", index = False, header=True)
B2B_L_carrier.to_csv(f_dir+"B2B_carrier_county0_shipall_A_s2018.csv", index = False, header=True)
B2B_L_payload.to_csv(f_dir+"B2B_payload_county0_shipall_A_s2018.csv", index = False, header=True)
B2C_L_carrier.to_csv(f_dir+"B2C_carrier_county0_shipall_A_s2018.csv", index = False, header=True)
B2C_L_payload.to_csv(f_dir+"B2C_payload_county0_shipall_A_s2018.csv", index = False, header=True)
# %%
travel_file= "../../../FRISM_input_output_SF/Sim_inputs/Geo_data/tt_df_cbg.csv.gz"
tt_df = pd.read_csv(travel_file, compression='gzip', header=0, sep=',', quotechar='"')