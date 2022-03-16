# %%
import pandas as pd
# %%
#household_file = "../../../FRISM_input_output_AT/Sim_inputs/austin_2018/households.csv.zip"
#household_file ="/Users/kjeong/NREL/1_Work/1_2_SMART_2_0/Model_development/FRISM_input_output_AT/Sim_inputs/austin_2018/households.csv.zip"
household_file_sf="../../../FRISM_input_output_SF/Sim_inputs/plans-base-2010/households.csv"
synth_hh_sf = pd.read_csv(household_file_sf, header=0, sep=',')

household_file_sf="../../../FRISM_input_output_SF/Sim_inputs/sfbay_2018/households.csv.zip"
synth_hh_sf_18 = pd.read_csv(household_file_sf, header=0, sep=',')

person_file="../../../FRISM_input_output_SF/Sim_inputs/plans-base-2010/persons.csv"
synth_per_sf = pd.read_csv(person_file, header=0, sep=',')

person_file="../../../FRISM_input_output_SF/Sim_inputs/sfbay_2018/persons.csv.zip"
synth_per_sf_18 = pd.read_csv(person_file, header=0, sep=',')

household_file="../../../FRISM_input_output_AT/Sim_inputs/austin_2018/households.csv.zip"
synth_hh_au_18 = pd.read_csv(household_file, header=0, sep=',')

person_file="../../../FRISM_input_output_AT/Sim_inputs/austin_2018/persons.csv.zip"
synth_per_au_18 = pd.read_csv(person_file, header=0, sep=',')


# %%
