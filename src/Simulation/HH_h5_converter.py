# %%
from re import I
import pandas as pd
# %%
#household_file = "../../../FRISM_input_output_AT/Sim_inputs/austin_2018/households.csv.zip"
#household_file ="/Users/kjeong/NREL/1_Work/1_2_SMART_2_0/Model_development/FRISM_input_output_AT/Sim_inputs/austin_2018/households.csv.zip"
# household_file_sf="../../../FRISM_input_output_SF/Sim_inputs/plans-base-2010/households.csv"
# synth_hh_sf = pd.read_csv(household_file_sf, header=0, sep=',')

# household_file_sf="../../../FRISM_input_output_SF/Sim_inputs/sfbay_2018/households.csv.zip"
# synth_hh_sf_18 = pd.read_csv(household_file_sf, header=0, sep=',')

# person_file="../../../FRISM_input_output_SF/Sim_inputs/plans-base-2010/persons.csv"
# synth_per_sf = pd.read_csv(person_file, header=0, sep=',')

# person_file="../../../FRISM_input_output_SF/Sim_inputs/sfbay_2018/persons.csv.zip"
# synth_per_sf_18 = pd.read_csv(person_file, header=0, sep=',')

household_file="../../../FRISM_input_output_AT/Sim_inputs/austin_2018/households.csv.zip"
synth_hh_au_18 = pd.read_csv(household_file, header=0, sep=',')

person_file="../../../FRISM_input_output_AT/Sim_inputs/austin_2018/persons.csv.zip"
synth_per_au_18 = pd.read_csv(person_file, header=0, sep=',')


# %%
list(synth_hh_au_18)
list(synth_per_au_18)


# %%
import h5py
import pandas as pd
# f = h5py.File("../../../FRISM_input_output_SF/Sim_inputs/model_data_2030.h5", 'r')
# # %%
# list(f.keys())
# # %%
# f_2030=f['2030']
# # %%
# list(f_2030.keys())
# f_2030_hh= f_2030['households']
# # %%
# list(f_2030_hh.keys())
# # %%
# f_2030_hh['block0_items']
# # %%
# hh=pd.read_hdf(f_2030_hh)
# %%
s_area="SF"
year="2050"
f_dir="sfbay_{}".format(year)
hh =pd.read_hdf("../../../FRISM_input_output_{}/Sim_inputs/hh_pop/model_data_{}.h5".format(s_area,year), key="{}/households".format(year))
compression_opts = dict(method='zip',archive_name='households.csv')  
hh.to_csv('../../../FRISM_input_output_{}/Sim_inputs/hh_pop/{}/households.csv'.format(s_area,f_dir), index=True) 

per =pd.read_hdf("../../../FRISM_input_output_{}/Sim_inputs/hh_pop/model_data_{}.h5".format(s_area,year), key="{}/persons".format(year))
compression_opts = dict(method='zip',archive_name='persons.csv')  
per.to_csv('../../../FRISM_input_output_{}/Sim_inputs/hh_pop/{}/persons.csv'.format(s_area,f_dir), index=True) 
# %%
# %%
file_1="../../../FRISM_input_output_AT/Sim_inputs/Synth_firm_pop/xysynthetic_firms_with_fleet_2040.csv"
firm=pd.read_csv(file_1, header=0, sep=',')
file_2="../../../FRISM_input_output_AT/Sim_inputs/Synth_firm_pop/xysynthetic_carriers_2040.csv"
carrier=pd.read_csv(file_2, header=0, sep=',')
file_3="../../../FRISM_input_output_AT/Sim_inputs/Synth_firm_pop/xysynthetic_leasing_company_2040.csv"
leasing=pd.read_csv(file_3, header=0, sep=',')
# %%
for i in firm.columns:
    print (i)

for i in carrier.columns:
    print (i)    

for i in leasings.columns:
    print (i)     


#['Battery Electric', 'H2 Fuel Cell', 'PHEV', nan]    
# %%
firm[firm["BusID"]==2881082]
# %%
carrier["BusID"].iloc[0]
leasing["BusID"].iloc[0]
# %%

import glob
import pandas as pd
fdir="/Users/kjeong/NREL/1_Work/1_2_SMART_2_0/Model_development/FRISM_input_output_SF/Sim_inputs/Geo_data/Freight_source_destination_locations/"
for filename in glob.glob(fdir+'*.csv'):
    try: 
        temp= pd.read_csv(filename,header=None, sep=',')
        temp[2]=0
        for i in range (0,temp.shape[0]):
            list_val=temp[1].iloc[i].split(":")
            temp[1].iloc[i]= float(list_val[1].split(",")[0])
            temp[2].iloc[i]= float(list_val[2])
        temp.columns = ['adress', 'lon', "lat"]
        temp.to_csv(filename)
    except: 
        print (filename)        

    
# %%
hh =pd.read_hdf("../../../FRISM_input_output_AT/Sim_inputs/model_data_2040.h5", key="2040/households")
compression_opts = dict(method='zip',archive_name='households.csv')  
hh.to_csv('../../../FRISM_input_output_AT/Sim_inputs/austin_2040/households.csv', index=True, compression=compression_opts) 

# %%

#df_hh_model=pd.read_csv('../../../FRISM_input_output_{}/Sim_outputs/Generation/households_del.csv'.format(config.study_region))
import numpy as np
import matplotlib.pyplot as plt
df_hh_2040= pd.read_csv('../../../FRISM_input_output_AT//Sim_outputs/Generation/households_del_2040.csv')
df_hh_2018= pd.read_csv('../../../FRISM_input_output_AT//Sim_outputs/Generation/households_del.csv')

df_hh_2040['delivery_f'] =df_hh_2040['delivery_f'].apply(lambda x: 0 if np.isnan(x) else int(x))
df_hh_2018['delivery_f'] =df_hh_2018['delivery_f'].apply(lambda x: 0 if np.isnan(x) else int(x))

list_income=["income_cls_0","income_cls_1","income_cls_2","income_cls_3"]
dic_income={"income_cls_0": "income <$35k",
            "income_cls_1": "income $35k-$75k",
            "income_cls_2": "income $75k-125k",
            "income_cls_3": "income >$125k"}
    
for ic_nm in list_income:
    plt.figure(figsize = (8,6))
    #plt.hist(df_hh_obs[df_hh_obs[ic_nm]==1]['delivery_f'], color ="blue", density=True, bins=df_hh_obs[df_hh_obs[ic_nm]==1]['delivery_f'].max(), alpha = 0.3, label="observed")
    #plt.hist(df_hh_model[(df_hh_model[ic_nm]==1) & (df_hh_model['delivery_f']<=30)]['delivery_f'], color ="red", density=True, bins=80, alpha = 0.3, label="modeled")
    #plt.hist(df_hh_model[(df_hh_model[ic_nm]==1)]['delivery_f'], color ="red", density=True, bins=df_hh_model[(df_hh_model[ic_nm]==1)]['delivery_f'].max(), alpha = 0.3, label="modeled")
    plt.hist(df_hh_2018[(df_hh_2018[ic_nm]==1)]['delivery_f'], color ="blue", density=False, bins=df_hh_2018[(df_hh_2018[ic_nm]==1)]['delivery_f'].max(), alpha = 0.3, label="2018")
    plt.hist(df_hh_2040[(df_hh_2040[ic_nm]==1)]['delivery_f'], color ="red", density=False, bins=df_hh_2040[(df_hh_2040[ic_nm]==1)]['delivery_f'].max(), alpha = 0.3, label="2040")
    plt.title("Density of Delivery Frequency in {0}, {1}".format(dic_income[ic_nm], "AT"))
    plt.legend(loc="upper right")
    plt.savefig('../../../FRISM_input_output_AT/Sim_outputs/Generation/B2C_delivery_scenario_{}.png'.format(ic_nm))
# %%
for ic_nm in list_income:
    val_18=df_hh_2018[(df_hh_2018[ic_nm]==1)]['delivery_f'].sum()
    val_40=df_hh_2040[(df_hh_2040[ic_nm]==1)]['delivery_f'].sum()
    in_rate=(val_40-val_18)/val_18 *100
    print (" {0} group: {1}".format(ic_nm,in_rate))

# %%
