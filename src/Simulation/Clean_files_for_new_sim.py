import os
import config

Study_region="AT"
# local
# dir="/Users/kjeong/NREL/1_Work/1_2_SMART_2_0/Model_development/FRISM_input_output_{}".format(Study_region)
# HPC
dir="/projects/frism/FRISM_input_output_{}".format(Study_region)
# delete Daily B2B selected
os.system("find {}/Sim_inputs/Synth_firm_results/ -type f -name '*csv*' -delete".format(dir))

# # delete output Step 2 (Generation)
# ## B2B
# os.system("find {}/Sim_outputs/Generation/ -type f -name '*B2B*' -delete".format(dir))
# ## B2C
# os.system("find {}/Sim_outputs/Generation/ -type f -name '*B2C*' -delete".format(dir))

# delete output Step 3 (shipment)
## B2B
os.system("find {}/Sim_outputs/Shipment2Fleet/ -type f -name '*B2B*' -delete".format(dir))
## B2C
os.system("find {}/Sim_outputs/Shipment2Fleet/ -type f -name '*B2C*' -delete".format(dir))

# # delete output Step 4 (Tour_plan)
# ## B2B
# os.system("find {}/Sim_outputs/Tour_plan/ -type f -name '*B2B*' -delete".format(dir))
# ## B2C
# os.system("find {}/Sim_outputs/Tour_plan/ -type f -name '*B2C*' -delete".format(dir))

# # delete temp_save
# ## B2B
# os.system("find {}/Sim_inputs/temp_save/ -type f -name '*csv*' -delete".format(dir))
