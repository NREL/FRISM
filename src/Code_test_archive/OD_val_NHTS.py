# %%
import pandas as pd
import numpy as np

t_od=pd.read_csv("../../../NG_NHTS_validation/National Truck Final OD Data_2020.csv")

# %%
S_Austin=[
"15180_TX",
"18580_TX",
"29700_TX",
"32580_TX",
"41700_TX",
"47020_TX",
"RTX10_TX",
"RTX7_TX"
]
N_Austin=[
"19100_TX",
"28660_TX",
"43300_TX",
"47380_TX",
"RTX9_TX",
"30980_TX",
"46340_TX"]
N_S_Austin=[
"OH",
"NY",
"NJ",
"PA",
"IA",
"MI",
"AL",
"WI",
"NC",
"GA",
"SC",
"MD",
"ME",
"MA",
"WV",
"VA",
"IL",
"IN",
"NH",
"KY",
"CT",
"VT",
"MO",
"TN",
"DE",
"MN",
"ND",
"AR",
"OK",
"MS",
"KS",
"NE",
"LA",
"RI",
"SD",
"DC"]

W_Austin=[
"33260_TX",
"36220_TX",
"41660_TX",
"RTX4_TX"]

E_Austin=[
"26420_TX",
"13140_TX",
"47020_TX",
"RTX10_TX"   
]
Austin=["12420_TX"]
# %% lower 
S_Austin=[
"29700_TX",
"41700_TX"
]
N_Austin=[
"19100_TX", 
"28660_TX", 
"43300_TX", 
"47380_TX"]
N_S_Austin=[
"OH",
"NY",
"NJ",
"PA",
"IA",
"MI",
"AL",
"WI",
"NC",
"GA",
"SC",
"MD",
"ME",
"MA",
"WV",
"VA",
"IL",
"IN",
"NH",
"KY",
"CT",
"VT",
"MO",
"TN",
"DE",
"MN",
"ND",
"AR",
"OK",
"MS",
"KS",
"NE",
"LA",
"RI",
"SD",
"DC"]

W_Austin=[
"33260_TX",
"36220_TX",
"41660_TX",
"RTX4_TX"]

E_Austin=[
"26420_TX",
"13140_TX",
"47020_TX",
"RTX10_TX"   
]
Austin=["12420_TX"]



#%%
T_wi= t_od[t_od["origin_zone_id"].isin(Austin) & t_od["destination_zone_id"].isin(Austin)]["annual_total_trips"].sum()

# %%
T_o=t_od[t_od["origin_zone_id"].isin(Austin)]["annual_total_trips"].sum()
T_i=t_od[t_od["destination_zone_id"].isin(Austin)]["annual_total_trips"].sum()
# %%
T_th_1=t_od[t_od["origin_zone_id"].isin(S_Austin) & t_od["destination_zone_id"].isin(N_Austin)]["annual_total_trips"].sum()
T_th_2=t_od[t_od["origin_zone_id"].isin(N_Austin) & t_od["destination_zone_id"].isin(S_Austin)]["annual_total_trips"].sum()
T_th_3=t_od[t_od["origin_zone_id"].isin(S_Austin) & t_od["destination_state"].isin(N_S_Austin)]["annual_total_trips"].sum()
T_th_4=t_od[t_od["origin_state"].isin(N_S_Austin) & t_od["destination_zone_id"].isin(S_Austin)]["annual_total_trips"].sum()
T_th_5=t_od[t_od["origin_zone_id"].isin(W_Austin) & t_od["destination_zone_id"].isin(E_Austin)]["annual_total_trips"].sum()
T_th_6=t_od[t_od["origin_zone_id"].isin(E_Austin) & t_od["destination_zone_id"].isin(W_Austin)]["annual_total_trips"].sum()
# %%
print(T_wi)
print(T_o-T_wi)
print(T_i-T_wi)
print(T_th_1+T_th_2+T_th_3+T_th_4+T_th_5+T_th_6)

# %%
