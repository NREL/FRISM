import os

head_text = f"""
{'-'*40}
Run FRISM Module in FAMOUS, which is Freight module as part of BEAM-CORE
Deveopled by NREL
Contributors: Dr. Kyungsoo Jeong, Dr. Juliette Ugirumurera, and Dr. Alicia Birky
{'-'*40}
"""

hh_gen_est_text =f"""
{'*'*60}
Running Household E-commerce Generation Estionation model for End-Consumer Behavior Module
# Note:
# 1. Need to select models (W,O,D,WOD)Please make sure if you select models you want to run. with selction of models (W,O,D,WOD)
# 2. Please check "config.py" in the working directory. If you change selected variables used in the model, please copy and paste "config.py" to Simulation folder
# 3. This only needs to estimate, calibarte, validate models to simulate the E-commerce.
# 4. Once the models are fully estimated, you don't need to run this again for the simulation.

"""
ec_module_text = f"""
{'*'*60}
Running End-Consumer Behavior Module to simulate monthly delivery freqency
# Note:
# 1. Key inputs: Synthetic population of household and person which comes from BEAM-CORE passenger model
# 2. Key inputs: models(*.sav) estimated from "HH_ecom_models.py"
# 3. Please check "config.py" in the working directory.

"""
dc_module_text= f"""
{'*'*60}
Running Distribution Channel to simulate B2B/B2C daily shipments and shipment-carrier matching
# Note:
# 1. Key inputs: Synthetic population of household and person which comes from BEAM-CORE passenger model
# 2. Key inputs: models(*.sav) estimated from "HH_ecom_models.py"
# 3. Please check "config.py" in the working directory.

"""
co_module_text = f"""
{'*'*60}
Running Carrier Operation to simulate tour-plan for each carrier
# Note:
# 1. Key inputs: payload, carrier, and vehicle files from "Shipment2Fleet.py"
# 2. Please check all file names

"""


print (head_text)

# # 1. Model estimation for End-Consumer Behavior Module (E-commerce generation)
# print (hh_gen_est_text)
# # Please replace hf, pf if their directory changes
# os.system("python HH_ecom_models.py \
#     -hf ../../../FRISM_input_output_SF/Model_inputs/NHTS/hhpub.csv \
#         -pf ../../../FRISM_input_output_SF/Model_inputs/NHTS/perpub.csv \
#             -mt WOD")

# # 2. End-Consumer Behavior Module Run (E-commerce generation)
# print (ec_module_text)
# # Please replace W, O, D, WOD with one of thme you want to run
# os.system("python B2C_Generation.py \
#     -hf ../../../FRISM_input_output_SF/Sim_inputs/sfbay_2018/households.csv.zip \
#         -pf ../../../FRISM_input_output_SF/Sim_inputs/sfbay_2018/persons.csv.zip")

# 3. Distribution Channel Module Run
print (dc_module_text)
# B2C
# Please select a county(-ct) you want to run, make sure -sd = all for B2C
# Counties in SF bay area: [1, 13, 41, 55, 75, 81, 85, 95, 97]; if you want to run SF together, select 9999

# os.system("python Shipment2Fleet.py \
#     -st B2C \
#         -ct 1 \
#             -sd all \
#                 -rt RunSim") # if you want to run test with 100 shipment allocation to carriers, "-rt Test". Otherwise "-rt RunSim"

# # B2B
# # Please select a county(-ct) you want to run & select shipment direction(-sd) = out, in, all
# # Counties in SF bay area: [1, 13, 41, 55, 75, 81, 85, 95, 97]; if you want to run SF together, select 9999
os.system("python Shipment2Fleet.py \
    -st B2B \
        -ct 1 \
            -sd all \
                -rt RunSim") # if you want to run test with 100 shipment allocation to carriers, "-rt test". Otherwise "-rt RunSim"


# # 4. Carrier opration Module Run
# print (co_module_text)
# B2C
# os.system("python VRP_OR-tools.py \
#     -cy 13 \
#         -t ../../../FRISM_input_output_SF/Sim_inputs/Geo_data/tt_df_cbg.csv.gz \
#             -d ../../../FRISM_input_output_SF/Sim_inputs/Geo_data/od_distance.csv \
#                 -ct ../../../FRISM_input_output_SF/Sim_inputs/Geo_data/freight_centroids.geojson \
#                     -cr ../../../FRISM_input_output_SF/Sim_outputs/Shipment2Fleet/B2C_carrier_county13_shipall.csv \
#                         -pl ../../../FRISM_input_output_SF/Sim_outputs/Shipment2Fleet/B2C_payload_county13_shipall.csv \
#                             -vt ../../../FRISM_input_output_SF/Sim_outputs/Shipment2Fleet/vehicle_types.csv")
    # # B2B
# os.system("python VRP_OR-tools.py \
#     -cy 1 \
#         -t ../../../FRISM_input_output_SF/Sim_inputs/Geo_data/tt_df_cbg.csv.gz \
#             -d ../../../FRISM_input_output_SF/Sim_inputs/Geo_data/od_distance.csv \
#                 -ct ../../../FRISM_input_output_SF/Sim_inputs/Geo_data/freight_centroids.geojson \
#                     -cr ../../../FRISM_input_output_SF/Sim_outputs/Shipment2Fleet/B2B_carrier_county75_shipall_A.csv \
#                         -pl ../../../FRISM_input_output_SF/Sim_outputs/Shipment2Fleet/B2B_payload_county75_shipall_A.csv \
#                             -vt ../../../FRISM_input_output_SF/Sim_outputs/Shipment2Fleet/vehicle_types.csv")

print ("Completed running modules you selected")
