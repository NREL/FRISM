import pandas as pd
import random
import numpy as np
# county_list=[1, 13, 41, 55, 75, 81, 85, 95, 97]
# f_dir="../../../FRISM_input_output_SF/Sim_outputs/Shipment2Fleet/"
# for county in county_list:
#     df = pd.read_csv(f_dir+"B2C_carrier_county{}_shipall.csv".format(county))
#     df["num_veh_type_1"]=df["num_veh_type_1"].apply(lambda x: int((x+1)*1.5))
#     df.to_csv(f_dir+f_dir+"B2C_carrier_county{}_shipall.csv".format(county), index = False, header=True)
def time_normal(mean, std, min_time,max_time):
    time = np.random.normal(mean,std)
    if time < min_time:
        time=min_time
    elif time > max_time:
        time =max_time
    return int(time)*60 

def pu_tu(pu_tw_upper, job):
    if job == "pickup_delivery":
        if pu_tw_upper <= 15*60:
            return 24*60
        else:
            return 24*60    
    else:
        return pu_tw_upper
def del_tu(del_tw_upper):
    
    if del_tw_upper >= 24*60:
        return (24+4)*60
    else:
        return 24*60    
            
# county_list=[1, 13, 41, 55, 75, 81, 85, 95, 97]
# #county_list=[1]
# f_dir="../../../FRISM_input_output_SF/Sim_outputs/Shipment2Fleet/"
# for county in county_list:
#     for file_nm in range(0, 10):
#         df = pd.read_csv(f_dir+"B2B_payload_county{}_shipall_{}.csv".format(county, file_nm))
#         df["pu_tw_upper"] = df.apply(lambda x:pu_tu(x["pu_tw_upper"], x["job"]), axis=1)
#         df["del_tw_upper"] = df.apply(lambda x:del_tu(x["del_tw_upper"]), axis=1)
#         df.to_csv(f_dir+f_dir+"B2B_payload_county{}_shipall_{}.csv".format(county, file_nm), index = False, header=True)  

county_list=[1, 13, 41, 55, 75, 81, 85, 95, 97]
#county_list=[1]
f_dir="../../../FRISM_input_output_SF/Sim_outputs/Shipment2Fleet/"
for county in county_list:
    df = pd.read_csv(f_dir+"B2B_carrier_county{}_shipall_A.csv".format(county))
    df["depot_upper"] = df["depot_upper"].apply(lambda x: 48*60 if x>25*60 else random.randint(21,24+4)*60)
    df.to_csv(f_dir+f_dir+"B2B_carrier_county{}_shipall_A.csv".format(county), index = False, header=True)  