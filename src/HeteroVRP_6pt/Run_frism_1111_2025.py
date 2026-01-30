import os
import sys
import pandas as pd
inputs = pd.read_csv("input.csv")#general input parameters such as county, year, scenario, sample rate, EV savings, EV_battery_capacity, soc_threshold
inputs_powertrain_types = pd.read_csv("input_powertrain_types.csv", index_col=0)# cost details of the different powertrain types
# print(inputs)
# print(inputs_powertrain_types)

county = inputs[inputs['key'] == 'county']['value'].iloc[0]
# print("county:", county)
year = inputs[inputs['key'] == 'year']['value'].iloc[0]
# print("year:", year)
scenario = inputs[inputs['key'] == 'scenario']['value'].iloc[0]
# print("scenario:", scenario)
sample_rate = inputs[inputs['key'] == 'sample_rate']['value'].iloc[0]
# print("sample_rate:", sample_rate)
EV_savings = inputs[inputs['key'] == 'EV_savings']['value'].iloc[0]
# print("EV_savings:", EV_savings)
EV_battery_capacity  = inputs[inputs['key'] == 'EV_battery_capacity']['value'].iloc[0]
# print("EV_battery_capacity:", EV_battery_capacity)
soc_threshold = inputs[inputs['key'] == 'soc_threshold']['value'].iloc[0]
# print("soc_threshold:", soc_threshold)  
veh_pwrtrn_types = inputs_powertrain_types.columns.tolist()
# print(veh_pwrtrn_types)  # Exclude the first column which is 'key'

fixed_cost_dict = inputs_powertrain_types.loc["fixed_cost_dict"].to_dict()
fixed_cost_dict = {k: int(float(v)) for k, v in fixed_cost_dict.items()}
cost_per_unit_time_dict  = inputs_powertrain_types.loc["cost_per_unit_time_dict"].to_dict()

# print("Vehicle types:", veh_pwrtrn_types)
# print("Fixed costs:", fixed_cost_dict)
# print("Time costs:", cost_per_unit_time_dict)

pw_str = " ".join(map(str, veh_pwrtrn_types))
fc_str = " ".join(map(str, fixed_cost_dict.values()))
cu_str = " ".join(map(str, cost_per_unit_time_dict.values()))



# B2B


cdm_B2B = (

    "python VRP_OR_tools_hetero_main_1_20_26.py "
    f"-cy {county} "
    "-t ../../Example_Data/Sim_inputs/Geo_data/Seattle_tt_df_cbg.csv.gz "
    "-d ../../Example_Data/Sim_inputs/Geo_data/Seattle_od_dist.csv.gz "
    "-ct ../../Example_Data/Sim_inputs/Geo_data/Seattle_freight_centroids.geojson "
    f"-cr ../../Example_Data/Sim_outputs/Shipment2Fleet/2018/B2B_carrier_county{county}_s{scenario}_y{year}_sr{sample_rate}_1.csv "
    f"-pl ../../Example_Data/Sim_outputs/Shipment2Fleet/2018/B2B_payload_county{county}_s{scenario}_y{year}_sr{sample_rate}.csv "
    f"-vt ../../Example_Data/Sim_outputs/Shipment2Fleet/2018/vehicle_types_s{scenario}_y{year}.csv "
    f"-sn {scenario} "
    f"-yt {year} "
    f"-es {EV_savings} "
    f"-ps ../../Example_Data/Sim_inputs/Stops_data/ "
    f"-pt {pw_str} "
    f"-fc {fc_str} "
    f"-cu {cu_str} "
    f"-ebc {EV_battery_capacity} "
    f"-soc {soc_threshold} "
)

os.system(cdm_B2B)

# B2C

# cdm_B2C = (
#     "python VRP_OR_tools_hetero_main_11_12.py "
#     f"-cy {county} "
#     "-t ../../Example_Data/Sim_inputs/Geo_data/Seattle_tt_df_cbg.csv.gz "
#     "-d ../../Example_Data/Sim_inputs/Geo_data/Seattle_od_dist.csv.gz "
#     "-ct ../../Example_Data/Sim_inputs/Geo_data/Seattle_freight_centroids.geojson "
#     f"-cr ../../Example_Data/Sim_outputs/Shipment2Fleet/2030/B2C_carrier_county{county}_shipall_s{scenario}_y{year}_sr{sample_rate}.csv "
#     f"-pl ../../Example_Data/Sim_outputs/Shipment2Fleet/2030/B2C_payload_county{county}_shipall_s{scenario}_y{year}_sr{sample_rate}.csv "
#     f"-vt ../../Example_Data/Sim_outputs/Shipment2Fleet/2030/vehicle_types_s{scenario}_y{year}.csv "    
#     f"-sn {scenario} "
#     f"-yt {year} "
#     f"-es {EV_savings} "
#     f"-ps ../../Example_Data/Sim_inputs/Stops_data/ "
#     f"-pt {pw_str} "
#     f"-fc {fc_str} "
#     f"-cu {cu_str} "
#     f"-ebc {EV_battery_capacity} "
#     f"-soc {soc_threshold} "
# )   

# os.system(cdm_B2C)



print ("Completed running modules you selected")

