# %%
import pandas as pd
import numpy as np
import geopandas as gpd
from argparse import ArgumentParser
import random

#%%
file_1="../../../FRISM_input_output_AT/Sim_inputs/Synth_firm_pop/xysynthetic_firms_with_fleet_2018.csv"
firms=pd.read_csv(file_1, header=0, sep=',')
file_2="../../../FRISM_input_output_AT/Sim_inputs/Synth_firm_pop/xysynthetic_carriers_2018.csv"
carriers=pd.read_csv(file_2, header=0, sep=',')
file_3="../../../FRISM_input_output_AT/Sim_inputs/Synth_firm_pop/xysynthetic_leasing_company_2018.csv"
leasings=pd.read_csv(file_3, header=0, sep=',')

# %%

def selec_ev(list_num_veh):
    new_list=[]
    j=0
    for i in range(0,len(list_num_veh)):
        j+=list_num_veh[i]/sum(list_num_veh)
        new_list.append(j)
    prob_veh = random.uniform(0,1)

    for i in range(0,len(new_list)):
        if i==0: 
            if  prob_veh <= new_list[i]:
                index=i
        else:
            if prob_veh > new_list[i-1]  and prob_veh <= new_list[i]:
                index = i 
    return index


def assign_veh_type(firms, carriers, firms_sum, carriers_sum,BusID, veh):
    try:
        [[st_firm,ev_firm ]]=firms[firms["BusID"]== BusID][['st', 'EV_powertrain (if any)']].values.tolist()
        flag="firm"
    except:
        try:      
            [[st_firm,ev_firm ]]=carriers[carriers["BusID"]== BusID][['st', 'EV_powertrain (if any)']].values.tolist()
            flag="carrier"
        except:
            st_firm=  48
            ev_firm="Battery Electric"
            flag="firm"
    if pd.isnull(ev_firm):
       ev_firm="Battery Electric" 

    if flag=="firm":
        if veh ==2:
           [[D_HD_V, D_HD_T]]=firms_sum[(firms_sum['st']==st_firm) & (firms_sum['powertrain']=="Diesel")][['HD_V', 'HD_T']].values.tolist()
           [[E_HD_V, E_HD_T]]=firms_sum[(firms_sum['st']==st_firm) & (firms_sum['powertrain']==ev_firm)][['HD_V', 'HD_T']].values.tolist()
           list_name=["D_HD_V", "D_HD_T","E_HD_V", "E_HD_T"]
           list_num_veh=[D_HD_V, D_HD_T,E_HD_V, E_HD_T]
           index=selec_ev(list_num_veh)
           if index>=2:
                veh_type_assign=  ev_firm+"_"+list_name[index]
           else:
                veh_type_assign=  list_name[index]     
        else:    
           [[D_MD]]=firms_sum[(firms_sum['st']==st_firm) & (firms_sum['powertrain']=="Diesel")][['MD']].values.tolist()
           [[E_MD]]=firms_sum[(firms_sum['st']==st_firm) & (firms_sum['powertrain']==ev_firm)][['MD']].values.tolist()
           list_name=["D_MD","E_MD"]
           list_num_veh=[D_MD,E_MD]
           index=selec_ev(list_num_veh)
           if index>=1:
                veh_type_assign=  ev_firm+"_"+list_name[index]
           else:
                veh_type_assign=  list_name[index]  

    else:
        if veh ==2:
           [[D_HD_V, D_HD_T]]=carriers_sum[(carriers_sum['st']==st_firm) & (carriers_sum['powertrain']=="Diesel")][['HD_V', 'HD_T']].values.tolist()
           [[E_HD_V, E_HD_T]]=carriers_sum[(carriers_sum['st']==st_firm) & (carriers_sum['powertrain']==ev_firm)][['HD_V', 'HD_T']].values.tolist()
           list_name=["D_HD_V", "D_HD_T","E_HD_V", "E_HD_T"]
           list_num_veh=[D_HD_V, D_HD_T,E_HD_V, E_HD_T]
           index=selec_ev(list_num_veh)
           if index>=2:
                veh_type_assign=  ev_firm+"_"+list_name[index]
           else:
                veh_type_assign=  list_name[index]     
        else:    
           [[D_MD]]=carriers_sum[(carriers_sum['st']==st_firm) & (carriers_sum['powertrain']=="Diesel")][['MD']].values.tolist()
           [[E_MD]]=carriers_sum[(carriers_sum['st']==st_firm) & (carriers_sum['powertrain']==ev_firm)][['MD']].values.tolist()
           list_name=["D_MD","E_MD"]
           list_num_veh=[D_MD,E_MD]
           index=selec_ev(list_num_veh)
           if index>=1:
                veh_type_assign=  ev_firm+"_"+list_name[index]
           else:
                veh_type_assign=  list_name[index]  
    return veh_type_assign


# %%
# carriers_bb=carriers[carriers['Industry_NAICS6_Make']==492000]
# carriers_bc=firms[firms['Industry_NAICS6_Make']==484000]
# firms=firms[firms['Industry_NAICS6_Make']!=484000]
carriers_bb=carriers[carriers['Industry_NAICS6_Make']==492000]
carriers_bc=carriers[carriers['Industry_NAICS6_Make']==484000]
firms_D= firms.groupby(['st']).agg(MD=("Diesel Class 4-6 Vocational",'sum'),
                                        HD_V=("Diesel Class 7&8 Tractor",'sum'),
                                        HD_T=("Diesel Class 7&8 Vocational",'sum') 
                                            ).reset_index()
firms_D["powertrain"]="Diesel"                                            
firms_E= firms.groupby(['st', 'EV_powertrain (if any)']).agg(MD=("Electric Class 4-6 Vocational",'sum'),
                                        HD_V=("Electric Class 7&8 Tractor",'sum'),
                                        HD_T=("Electric Class 7&8 Vocational",'sum') 
                                            ).reset_index()
firms_E=firms_E.rename({'EV_powertrain (if any)':'powertrain'}, axis='columns')
firms_sum= pd.concat([firms_D,firms_E], ignore_index=True).reset_index(drop=True)


carriers_D= carriers_bc.groupby(['st']).agg(MD=("Diesel Class 4-6 Vocational",'sum'),
                                        HD_V=("Diesel Class 7&8 Tractor",'sum'),
                                        HD_T=("Diesel Class 7&8 Vocational",'sum') 
                                            ).reset_index()
carriers_D["powertrain"]="Diesel"                                            
carriers_E= carriers_bc.groupby(['st', 'EV_powertrain (if any)']).agg(MD=("Electric Class 4-6 Vocational",'sum'),
                                        HD_V=("Electric Class 7&8 Tractor",'sum'),
                                        HD_T=("Electric Class 7&8 Vocational",'sum') 
                                            ).reset_index()
carriers_E=firms_E.rename({'EV_powertrain (if any)':'powertrain'}, axis='columns')
carriers_bc_sum= pd.concat([carriers_D,carriers_E], ignore_index=True).reset_index(drop=True)
carriers_D= carriers_bb.groupby(['st']).agg(MD=("Diesel Class 4-6 Vocational",'sum'),
                                        HD_V=("Diesel Class 7&8 Tractor",'sum'),
                                        HD_T=("Diesel Class 7&8 Vocational",'sum') 
                                            ).reset_index()
carriers_D["powertrain"]="Diesel"                                            
carriers_E= carriers_bb.groupby(['st', 'EV_powertrain (if any)']).agg(MD=("Electric Class 4-6 Vocational",'sum'),
                                        HD_V=("Electric Class 7&8 Tractor",'sum'),
                                        HD_T=("Electric Class 7&8 Vocational",'sum') 
                                            ).reset_index()
carriers_E=firms_E.rename({'EV_powertrain (if any)':'powertrain'}, axis='columns')
carriers_bb_sum= pd.concat([carriers_D,carriers_E], ignore_index=True).reset_index(drop=True)

# %%
f_dir="../../../FRISM_input_output_AT/Sim_outputs/Tour_plan_AT_2018/"
f_dir_out="../../../FRISM_input_output_AT/Sim_outputs/Tour_plan_AT_2018/"
county_list=[453, 491, 209, 55, 21, 53]
for county in county_list:
    df = pd.read_csv(f_dir+"B2B_county{}_carrier.csv".format(county))
    df['BusID'] = df['carrierId'].apply(lambda x: int(x.split("_")[1].split("d")[0]))
    # for i in range(0,df.shape[0]):
    #     df['vehicleTypeId'].iloc[i]= assign_veh_type(firms, carriers, firms_sum, carriers_bb_sum , df["BusID"].iloc[i], df["vehicleTypeId"].iloc[i])
    df['vehicleTypeId']= df.apply(lambda x: assign_veh_type(firms, carriers, firms_sum, carriers_bb_sum , x["BusID"], x["vehicleTypeId"]), axis=1)
    df=df.drop(columns=['BusID'])
    df.to_csv(f_dir_out+"B2B_county{}_carrier.csv".format(county))
for county in county_list:
    df = pd.read_csv(f_dir+"B2C_county{}_carrier.csv".format(county))
    df['BusID'] = df['carrierId'].apply(lambda x: int(x.split("_")[1].split(".")[0]))
    df['vehicleTypeId']= df.apply(lambda x: assign_veh_type(firms, carriers, firms_sum, carriers_bc_sum , x["BusID"], x["vehicleTypeId"]), axis=1)
    df=df.drop(columns=['BusID'])
    df.to_csv(f_dir_out+"B2C_county{}_carrier.csv".format(county))



############# 2040    


#%%
file_1="../../../FRISM_input_output_AT/Sim_inputs/Synth_firm_pop/xysynthetic_firms_with_fleet_2040.csv"
firms=pd.read_csv(file_1, header=0, sep=',')
file_2="../../../FRISM_input_output_AT/Sim_inputs/Synth_firm_pop/xysynthetic_carriers_2040.csv"
carriers=pd.read_csv(file_2, header=0, sep=',')
file_3="../../../FRISM_input_output_AT/Sim_inputs/Synth_firm_pop/xysynthetic_leasing_company_2040.csv"
leasings=pd.read_csv(file_3, header=0, sep=',')

# %%
# carriers_bb=carriers[carriers['Industry_NAICS6_Make']==492000]
# carriers_bc=firms[firms['Industry_NAICS6_Make']==484000]
# firms=firms[firms['Industry_NAICS6_Make']!=484000]
carriers_bb=carriers[carriers['Industry_NAICS6_Make']==492000]
carriers_bc=carriers[carriers['Industry_NAICS6_Make']==484000]
firms_D= firms.groupby(['st']).agg(MD=("Diesel Class 4-6 Vocational",'sum'),
                                        HD_V=("Diesel Class 7&8 Tractor",'sum'),
                                        HD_T=("Diesel Class 7&8 Vocational",'sum') 
                                            ).reset_index()
firms_D["powertrain"]="Diesel"                                            
firms_E= firms.groupby(['st', 'EV_powertrain (if any)']).agg(MD=("Electric Class 4-6 Vocational",'sum'),
                                        HD_V=("Electric Class 7&8 Tractor",'sum'),
                                        HD_T=("Electric Class 7&8 Vocational",'sum') 
                                            ).reset_index()
firms_E=firms_E.rename({'EV_powertrain (if any)':'powertrain'}, axis='columns')
firms_sum= pd.concat([firms_D,firms_E], ignore_index=True).reset_index(drop=True)

carriers_D= carriers_bc.groupby(['st']).agg(MD=("Diesel Class 4-6 Vocational",'sum'),
                                        HD_V=("Diesel Class 7&8 Tractor",'sum'),
                                        HD_T=("Diesel Class 7&8 Vocational",'sum') 
                                            ).reset_index()
carriers_D["powertrain"]="Diesel"                                            
carriers_E= carriers_bc.groupby(['st', 'EV_powertrain (if any)']).agg(MD=("Electric Class 4-6 Vocational",'sum'),
                                        HD_V=("Electric Class 7&8 Tractor",'sum'),
                                        HD_T=("Electric Class 7&8 Vocational",'sum') 
                                            ).reset_index()
carriers_E=firms_E.rename({'EV_powertrain (if any)':'powertrain'}, axis='columns')
carriers_bc_sum= pd.concat([carriers_D,carriers_E], ignore_index=True).reset_index(drop=True)

carriers_D= carriers_bb.groupby(['st']).agg(MD=("Diesel Class 4-6 Vocational",'sum'),
                                        HD_V=("Diesel Class 7&8 Tractor",'sum'),
                                        HD_T=("Diesel Class 7&8 Vocational",'sum') 
                                            ).reset_index()
carriers_D["powertrain"]="Diesel"                                            
carriers_E= carriers_bb.groupby(['st', 'EV_powertrain (if any)']).agg(MD=("Electric Class 4-6 Vocational",'sum'),
                                        HD_V=("Electric Class 7&8 Tractor",'sum'),
                                        HD_T=("Electric Class 7&8 Vocational",'sum') 
                                            ).reset_index()
carriers_E=firms_E.rename({'EV_powertrain (if any)':'powertrain'}, axis='columns')
carriers_bb_sum= pd.concat([carriers_D,carriers_E], ignore_index=True).reset_index(drop=True)

# %%
f_dir="../../../FRISM_input_output_AT/Sim_outputs/Tour_plan_AT_2040/"
f_dir_out="../../../FRISM_input_output_AT/Sim_outputs/Tour_plan_AT_2040/"
county_list=[453, 491, 209, 55, 21, 53]
for county in county_list:
    df = pd.read_csv(f_dir+"B2B_county{}_carrier.csv".format(county))
    df['BusID'] = df['carrierId'].apply(lambda x: int(x.split("_")[1].split("d")[0]))  
    df['vehicleTypeId']= df.apply(lambda x: assign_veh_type(firms, carriers, firms_sum, carriers_bb_sum , x["BusID"], x["vehicleTypeId"]), axis=1)
    df=df.drop(columns=['BusID'])
    df.to_csv(f_dir_out+"B2B_county{}_carrier.csv".format(county))
for county in county_list:
    df = pd.read_csv(f_dir+"B2C_county{}_carrier.csv".format(county))
    df['BusID'] = df['carrierId'].apply(lambda x: int(x.split("_")[1].split(".")[0]))
    df['vehicleTypeId']= df.apply(lambda x: assign_veh_type(firms, carriers, firms_sum, carriers_bc_sum , x["BusID"], x["vehicleTypeId"]), axis=1)
    df=df.drop(columns=['BusID'])
    df.to_csv(f_dir_out+"B2C_county{}_carrier.csv".format(county))
# %%

# %%
# %%
f_dir="../../../FRISM_input_output_AT/Sim_outputs/Tour_plan_AT_2018/"
f_dir_out="../../../FRISM_input_output_AT/Sim_outputs/Tour_plan_AT_2018/"
county_list=[453, 491, 209, 55, 21, 53]
df_b2b=pd.DataFrame()
for county in county_list:
    df = pd.read_csv(f_dir+"B2B_county{}_carrier.csv".format(county))
    df_b2b=pd.concat([df_b2b,df], ignore_index=True).reset_index(drop=True)

b2b_table_18=df_b2b.groupby(['vehicleTypeId'])['tourId'].count().reset_index(name='num_tour')  
b2b_table_18.to_csv(f_dir_out+"b2b_table_18.csv")

df_b2c=pd.DataFrame()
for county in county_list:
    df = pd.read_csv(f_dir+"B2C_county{}_carrier.csv".format(county))
    df_b2c=pd.concat([df_b2c,df], ignore_index=True).reset_index(drop=True)
b2c_table_18=df_b2c.groupby(['vehicleTypeId'])['tourId'].count().reset_index(name='num_tour')  
b2c_table_18.to_csv(f_dir_out+"b2c_table_18.csv")
# %%
f_dir="../../../FRISM_input_output_AT/Sim_outputs/Tour_plan_AT_2040/"
f_dir_out="../../../FRISM_input_output_AT/Sim_outputs/Tour_plan_AT_2040/"
county_list=[453, 491, 209, 55, 21, 53]
df_b2b=pd.DataFrame()
for county in county_list:
    df = pd.read_csv(f_dir+"B2B_county{}_carrier.csv".format(county))
    df_b2b=pd.concat([df_b2b,df], ignore_index=True).reset_index(drop=True)

b2b_table_40=df_b2b.groupby(['vehicleTypeId'])['tourId'].count().reset_index(name='num_tour')  
b2b_table_40.to_csv(f_dir_out+"b2b_table_40.csv")

df_b2c=pd.DataFrame()
for county in county_list:
    df = pd.read_csv(f_dir+"B2C_county{}_carrier.csv".format(county))
    df_b2c=pd.concat([df_b2c,df], ignore_index=True).reset_index(drop=True)
b2c_table_40=df_b2c.groupby(['vehicleTypeId'])['tourId'].count().reset_index(name='num_tour')
b2c_table_40.to_csv(f_dir_out+"b2c_table_40.csv")  
# %%
