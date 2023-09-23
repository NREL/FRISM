import os
import config_SF as config
import sys

# # 2. End-Consumer Behavior Module Run (E-commerce generation)
for year in ["2050"]:
    print ("----------------SF_{}--------------".format(year))
    # Please replace W, O, D, WOD with one of thme you want to run
    os.system("python B2C_Generation.py \
        -hf ../../../FRISM_input_output_SF/Sim_inputs/hh_pop/sfbay_{0}/households.csv \
            -pf ../../../FRISM_input_output_SF/Sim_inputs/hh_pop/sfbay_{0}/persons.csv \
              -yr {0}".format(year))
    

