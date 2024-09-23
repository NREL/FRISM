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
f = h5py.File("../../../FRISM_input_output_ST/Sim_inputs/hh_pop/model_data_2018.h5", 'r')
# %%
list(f.keys())
# %%
f_2018=f['2018']
# %%
list(f_2018.keys())
f_2018_hh= f_2018['households']
# %%
list(f_2030_hh.keys())
# %%
f_2030_hh['block0_items']
# %%
hh=pd.read_hdf(f_2030_hh)
# %%
hh =pd.read_hdf("../../../FRISM_input_output_ST/Sim_inputs/hh_pop/model_data_2018.h5", key="2018/households")
hh=hh.reset_index()
compression_opts = dict(method='zip',archive_name='households.csv')  
hh.to_csv('../../../FRISM_input_output_ST/Sim_inputs/hh_pop/Seattle_2018/households.csv', index=True) 
# %% 
per =pd.read_hdf("../../../FRISM_input_output_ST/Sim_inputs/hh_pop/model_data_2018.h5", key="2018/persons")
per=per.reset_index()
compression_opts = dict(method='zip',archive_name='persons.csv')  
per.to_csv('../../../FRISM_input_output_ST/Sim_inputs/hh_pop/Seattle_2018/persons.csv', index=True) 

#%%
df =pd.read_hdf("../../../FRISM_input_output_ST/Sim_inputs/hh_pop/model_data_2018.h5", key="block_group_zone_geoms")
compression_opts = dict(method='zip',archive_name='block.csv')  
df.to_csv('../../../FRISM_input_output_ST/Sim_inputs/hh_pop/Seattle_2018/block.csv', index=True)

#%%
df =pd.read_hdf("../../../FRISM_input_output_ST/Sim_inputs/hh_pop/Seattle/custom_mpo_53199100_model_data.h5", key="travel_data")
compression_opts = dict(method='zip',archive_name='travel.csv')  
df.to_csv('../../../FRISM_input_output_ST/Sim_inputs/hh_pop/Seattle/travel.csv', index=True) 
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
## To test population data
import numpy as np
hh= pd.read_csv('../../../FRISM_input_output_ST/Sim_inputs/hh_pop/Seattle_2018/households.csv')

# %%
def income_num2group(HHFAMINC):
    if HHFAMINC < 35000:
        return 0
    elif HHFAMINC >= 35000 and HHFAMINC <75000:
        return 1
    elif HHFAMINC >=75000 and HHFAMINC <125000:
        return 2
    elif HHFAMINC >=125000:
        return 3   
hh['ic_group']= hh["income"].apply(lambda x: income_num2group(x))     
hh['GEOID'] =hh['block_id'].apply(lambda x: np.floor(x/1000))
# %%
hh_by_block=hh.groupby(['GEOID'])['household_id'].agg(num_hh='count').reset_index()

# %%
hh_by_block_income=hh.groupby(['GEOID', 'ic_group'])['household_id'].agg(num_hh='count').reset_index()

# %%
import geopandas as gpd
fdir_geo = "../../../FRISM_input_output_ST/Sim_inputs/Geo_data/"
CBG_file = 'Seattle_freight.geojson'
state_id=53
CBGzone_df = gpd.read_file(fdir_geo+CBG_file) # file include, GEOID(12digit), MESOZONE, area
CBGzone_df= CBGzone_df.to_crs({'proj': 'cea'})
CBGzone_df["GEOID"]=CBGzone_df["GEOID"].astype(str)
## Add county id from GEOID
CBGzone_df["County"]=CBGzone_df["GEOID"].apply(lambda x: x[2:5] if (len(x)>=12 and x[0:2]==str(state_id))  else 0)
CBGzone_df["County"]=CBGzone_df["County"].astype(str).astype(int)
CBGzone_df["GEOID"]=CBGzone_df["GEOID"].astype(str).astype(int)
CBGzone_df=CBGzone_df[CBGzone_df["County"]!=0]
CBGzone_df= CBGzone_df.to_crs('EPSG:4269')

# %%
CBGzone_df=CBGzone_df[CBGzone_df["County"].isin([61,33,53,35])]
CBGzone_df.head()
# %%
CBGzone_df_hh = CBGzone_df.merge(hh_by_block[['GEOID','num_hh']], on='GEOID', how='left')
CBGzone_df_hh.to_file(fdir_geo+"st_household.geojson", driver="GeoJSON") 
CBGzone_df_hh.plot(column='num_hh', legend=True)
for ic in [0,1,2,3]:
    CBGzone_df_hh_temp = CBGzone_df.merge(hh_by_block_income[hh_by_block_income['ic_group']==ic][['GEOID','num_hh']], on='GEOID', how='left')
    CBGzone_df_hh_temp.to_file(fdir_geo+"st_household_ic{}.geojson".format(ic), driver="GeoJSON")
    CBGzone_df_hh_temp.plot(column='num_hh', legend=True)

# %%

df_hh = pd.read_csv('../../../FRISM_input_output_ST'+'/Sim_outputs/Generation/households_del_2018.csv', header=0, sep=',')
df_hh= df_hh[['household_id','delivery_f', 'block_id']]
df_hh['GEOID'] =df_hh['block_id'].apply(lambda x: np.floor(x/1000))
df_hh_by_block=df_hh.groupby(['GEOID'])['delivery_f'].agg(sum_delivery='count').reset_index()
CBGzone_delivery = CBGzone_df.merge(df_hh_by_block[['GEOID','sum_delivery']], on='GEOID', how='left')
CBGzone_delivery ['avg_daily'] = CBGzone_delivery ['sum_delivery']/20
# %%
CBGzone_delivery.plot(column='avg_daily', legend=True)
CBGzone_delivery.to_file(fdir_geo+"Avg_daily.geojson".format(ic), driver="GeoJSON")
# %%
df_daily=pd.DataFrame()
for c in [33,35,53,61]:
    df_temp= pd.read_csv('../../../FRISM_input_output_ST'+'/result_0423/Generation/B2C_daily_{}.csv'.format(c), header=0, sep=',')
    df_daily=pd.concat([df_daily, df_temp], ignore_index=True).reset_index(drop=True)

df_group= df_daily.groupby(['MESOZONE'])['household_gr_id'].agg(sum_delivery='count').reset_index()
CBGzone_delivery = CBGzone_df.merge(df_group[['MESOZONE','sum_delivery']], on='MESOZONE', how='left')
CBGzone_delivery.plot(column='sum_delivery', legend=True)
CBGzone_delivery.to_file(fdir_geo+"daily_delivery.geojson".format(ic), driver="GeoJSON")
# %%
df_daily=pd.DataFrame()
for c in [33,35,53,61]:
    df_temp= pd.read_csv('../../../FRISM_input_output_ST'+'/r_tep_v3/Shipment2Fleet/B2C_payload_county{}_shipall_sBase_y2018.csv'.format(c), header=0, sep=',')
    df_daily=pd.concat([df_daily, df_temp], ignore_index=True).reset_index(drop=True)
df_daily.to_csv(fdir_geo+"b2c_shipment_all.csv")
df_group= df_daily.groupby(['del_zone'])['payload_id'].agg(sum_delivery='count').reset_index()
df_group=df_group.rename({'del_zone':'MESOZONE'}, axis='columns')
CBGzone_delivery = CBGzone_df.merge(df_group[['MESOZONE','sum_delivery']], on='MESOZONE', how='left')
CBGzone_delivery.plot(column='sum_delivery', legend=True)
CBGzone_delivery.to_file(fdir_geo+"daily_shipment.geojson".format(ic), driver="GeoJSON")

# %%
