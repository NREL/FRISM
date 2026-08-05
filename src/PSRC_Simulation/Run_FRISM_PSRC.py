import os
import sys
scenario="Base" # scenario name: Base
year=2018
sample_rate=10 # [sample_rate =X] means X percent of shipments for daily shipment. 100 means all shipments from daily shipments generated. For test, use 10%, but 100% for full trip table
study_region= "ST"
vehicle_choice_calibration=0.1 # more weight on medium duty and heavy duty vocational truck
""" Step 1: Input setting
- Generate folder structure, variables, etc. which are defined in create_input_variable.py
- Users need to change the setting if needed 
- Outputs: input_setting_{study_region}.json 
"""
os.system("python create_input_variable.py")

""" Step 2: B2B shipment to fleet
- 1. Process SynthFirm Annual Demand and covert them to daily shipments
- 2. Shipments to Carrier with vehicle assignment 
- User can split this run by county for parallel run  
- Outputs: payload and carrier files in "Shipment2Fleet" folder 
"""
ship_type="B2B"
for c_num in [33,35,53,61]:
    print (f"B2B shipment to fleet for county{c_num}")
    os.system(f"python sim_b2b_shipment2fleet.py \
              -sn {scenario} \
                -yt {year} \
                    -st {ship_type} \
                        -ct {c_num} \
                            -sr {sample_rate} \
                                -sa {study_region} \
                                    -va {vehicle_choice_calibration}")

""" Step 3: B2C shipment to fleet
- 1. Process personal monthly B2C demand and covert them to daily shipments
- 2. Shipments to Carrier with vehicle assignment 
- User can split this run by county for parallel run  
- Outputs: payload and carrier files in "Shipment2Fleet" folder 
"""
ship_type="B2C"
for c_num in [33,35,53,61]:
    print (f"B2C shipment to fleet for county{c_num}")
    os.system(f"python sim_b2b_shipment2fleet.py \
              -sn {scenario} \
                -yt {year} \
                    -st {ship_type} \
                        -ct {c_num} \
                            -sr {sample_rate} \
                                -sa {study_region} \
                                    -va {vehicle_choice_calibration}")

""" Step 4: B2B and B2C tour generation
- 1. Process payload and carrier file 
- 2. Generate tour plan  
- User can split this run by county for parallel run  
- Outputs: payload, carrier, tour files in "Tour_plan" folder 
"""
for ship_type in ["B2B","B2C" ]:
    for c_num in [33,35,53,61]:
        print (f"{ship_type} tour generation for {c_num}")
        os.system(f"python sim_tour_plan_generation.py \
                -sn {scenario} \
                    -yt {year} \
                        -st {ship_type} \
                            -ct {c_num} \
                                -sr {sample_rate} \
                                    -sa {study_region}")
 
""" Step 5: Aggregate tour plans and covert to trip table
- 1. Combine all tour plan files into single files by shipment type
- 2. Covert tour plan to trip matrix met PSRC format
- Outputs: payload, carrier, tour files in "Tour_plan/2018_all" folder 
"""

os.system(f"python tour_postprocessing.py \
        -sn {scenario} \
            -yt {year} \
                -sr {sample_rate} \
                    -sa {study_region} \
                        -tm Yes")

print ("Completed running modules you selected")

