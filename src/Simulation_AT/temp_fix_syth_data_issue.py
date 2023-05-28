# %%
import pandas as pd
import numpy as np

#%%
f_dir="../../../FRISM_input_output_AT/Sim_inputs/Synth_firm_pop/"

for name in ["2030_Dmd_G","2040_Dmd_G","2050_Dmd_G"]:
    firms= pd.read_csv(f_dir+name+"/synthetic_firms_with_fleet_mc_adjusted.csv", header=0, sep=',')
    firms=firms.fillna(0)
    firms["MESOZONE"]=firms["MESOZONE"].astype('int')
    carriers= pd.read_csv(f_dir+name+"/synthetic_carriers.csv", header=0, sep=',')
    carriers=carriers.fillna(0)
    carriers["MESOZONE"]=carriers["MESOZONE"].astype('int')
    leasings=pd.read_csv(f_dir+name+"/synthetic_leasing_company.csv", header=0, sep=',')
    leasings['Electric Class 7&8 Tractor']=0
    leasings=leasings.fillna(0)
    leasings["MESOZONE"]=leasings["MESOZONE"].astype('int')
    firms.to_csv(f_dir+name+"/synthetic_firms_with_fleet_mc_adjusted.csv", index = False, header=True)
    carriers.to_csv(f_dir+name+"/synthetic_carriers.csv", index = False, header=True)
    leasings.to_csv(f_dir+name+"/synthetic_leasing_company.csv", index = False, header=True)
name= "2040_Dmd_G"
firms= pd.read_csv(f_dir+name+"/synthetic_firms_with_fleet_mc_adjusted.csv", header=0, sep=',')    
# %%
