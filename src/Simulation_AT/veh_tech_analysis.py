# %%
from matplotlib.image import AxesImage
import pandas as pd
import numpy as np
#import geopandas as gpd
#import networkx as nx
import matplotlib.pyplot as plt
from argparse import ArgumentParser
import seaborn as sns
import geopandas as gpd
#import osmnx as ox
#import plotly.graph_objects as go

# %%
f_dir="../../../Results_veh_tech_v1/"
#f_dir="/Users/kjeong/NREL/1_Work/1_2_SMART_2_0/Model_development/FRISM_input_output_AT/Sim_outputs/"


year_list=[2030,2040,2050]
s_list=["low", "central", "high"]
county_list=[453, 491, 209, 55, 21, 53]
stype_list=["B2B","B2C"]
df_ship=pd.DataFrame(county_list, columns =["county"])
df_tour=pd.DataFrame(county_list, columns =["county"])

dic_veh={'md': "Class 4-6 Vocational",
'hdt':"Class 7&8 Tractor",
'hdv':"Class 7&8 Vocational"
}
dic_fuel={"Diesel": "Diesel", "Battery Electric": "Electricity", "H2 Fuel Cell": "Hydrogen" , "PHEV": "Diesel"}
input_veh_list= ['Diesel Class 4-6 Vocational','Electric Class 4-6 Vocational',
                    'Diesel Class 7&8 Tractor','Electric Class 7&8 Tractor',
                    'Diesel Class 7&8 Vocational','Electric Class 7&8 Vocational',
                    'EV_powertrain (if any)' ]
output_veh_list=["md_D","md_E", "hdt_D", "hdt_E", "hdv_D", "hdv_E"]
y_s_list=[]
for y in year_list:
    for s in s_list:
        y_s_list.append(str(y)+s)
df_veh_agg=pd.DataFrame(y_s_list, columns =["scenario"])
df_veh_disagg=pd.DataFrame(y_s_list, columns =["scenario"])        
veh_disagg_list=[]

for veh_class in output_veh_list:
    for veh_fuel in dic_fuel.keys():
        df_veh_disagg[veh_class+"_"+veh_fuel]=0
        veh_disagg_list.append(veh_class+"_"+veh_fuel)

for veh_class in output_veh_list:
    df_veh_agg[veh_class]=0


for t in  stype_list:
    for y in year_list:
        for s in s_list:
            df_ship[t+str(y)+s]=0
            df_tour[t+str(y)+s]=0

for t in  stype_list:
    for y in year_list:
        for s in s_list:
            for c in county_list:
                try: 
                    i= df_ship.index[df_ship["county"]==c].values[0]
                    if t == "B2C":
                        ship=  pd.read_csv(f_dir+"Shipment2Fleet/{0}/{1}_payload_county{2}_shipall_s{3}_y{4}.csv". format(y,t,c,s,y))
                    else:
                        ship=  pd.read_csv(f_dir+"Shipment2Fleet/{0}/{1}_payload_county{2}_shipall_A_s{3}_y{4}.csv". format(y,t,c,s,y))

                    tour=  pd.read_csv(f_dir+"Tour_plan/{0}/{1}_county{2}_freight_tours_s{3}_y{4}.csv".format(y,t,c,s,y))
                    df_ship[t+str(y)+s].iloc[i]=ship.shape[0]
                    df_tour[t+str(y)+s].iloc[i]=tour.shape[0]
                except:
                    print ("No data for type: {0}; County: {1}; Scenario: {2}; Year: {3}".format(t,c,s,y))

for y in year_list:
    for s in s_list:
        i= df_veh_disagg.index[df_veh_disagg["scenario"]==str(y)+s].values[0]
        for c in county_list:
            for t in  stype_list:
                tour=  pd.read_csv(f_dir+"Tour_plan/{0}/{1}_county{2}_carrier_s{3}_y{4}.csv".format(y,t,c,s,y))
                for veh in veh_disagg_list:
                    try:
                        df_veh_disagg[veh].iloc[i] += len(tour[tour["vehicleTypeId"]==veh])
                    except:
                        pass    

                for veh_class in output_veh_list:
                    try:
                        df_veh_agg[veh_class].iloc[i] += len(tour[tour["vehicleTypeId"].str.contains(veh_class)])  
                    except:
                        pass

df_ship.loc['Total']= df_ship.sum(numeric_only=True, axis=0)
df_tour.loc['Total']= df_tour.sum(numeric_only=True, axis=0)

df_ship.to_csv(f_dir+"ship_summary.csv")
df_tour.to_csv(f_dir+"tour_summary.csv")
df_veh_disagg.to_csv(f_dir+"veh_type_disagg.csv")
df_veh_agg.to_csv(f_dir+"veh_type_agg.csv")

for t in  stype_list:
    for y in year_list:
        for s in s_list:
            for c in county_list:
                try:
                    tour=  pd.read_csv(f_dir+"Tour_plan/{0}/{1}_county{2}_freight_tours_s{3}_y{4}.csv".format(y,t,c,s,y))
                except:
                    print ("No data for type: {0}; County: {1}; Scenario: {2}; Year: {3}".format(t,c,s,y))                    
# %%
import shutil
import os

file_list=["carrier", "freight_tours", "payload"]

for y in year_list:
    for s in s_list:
        if not os.path.exists(f_dir+"Tour_plan/"+"{0}_{1}/".format(str(y),s)):
            os.makedirs(f_dir+"Tour_plan/"+"{0}_{1}/".format(str(y),s))
        origin=f_dir+"Shipment2Fleet/"+"{0}/vehicle_types_s{1}_y{0}.csv".format(y,s)
        target=f_dir+"Tour_plan/"+"{0}_{1}/vehicle_types_s{1}_y{0}.csv".format(y,s)    
        shutil.copy(origin, target)    
        for t in  stype_list:
            for c in county_list:
                for f in file_list:    
                    origin=f_dir+"Tour_plan/"+"{0}/{1}_county{2}_{3}_s{4}_y{5}.csv".format(y,t,c,f,s,y)
                    target=f_dir+"Tour_plan/"+"{0}_{4}/{1}_county{2}_{3}_s{4}_y{5}.csv".format(y,t,c,f,s,y)    
                    shutil.copy(origin, target)

# %%
f_dir="../../../Results_veh_tech_v1/"
#f_dir="/Users/kjeong/NREL/1_Work/1_2_SMART_2_0/Model_development/FRISM_input_output_AT/Sim_outputs/"


year_list=[2030,2040,2050]
s_list=["low", "central", "high"]
county_list=[453, 491, 209, 55, 21, 53]
stype_list=["B2B","B2C"]
dic_veh={'md': "Class 4-6 Vocational",
'hdt':"Class 7&8 Tractor",
'hdv':"Class 7&8 Vocational"
}
dic_fuel={"Diesel": "Diesel", "Battery Electric": "Electricity", "H2 Fuel Cell": "Hydrogen" , "PHEV": "Diesel"}
input_veh_list= ['Diesel Class 4-6 Vocational','Electric Class 4-6 Vocational',
                    'Diesel Class 7&8 Tractor','Electric Class 7&8 Tractor',
                    'Diesel Class 7&8 Vocational','Electric Class 7&8 Vocational',
                    'EV_powertrain (if any)' ]
output_veh_list=["md_D","md_E", "hdt_D", "hdt_E", "hdv_D", "hdv_E"]
df=pd.DataFrame(columns=["year", "scenario", "shipment", "vehicle type","powertrain","num_ship","num_tour"])
for t in  stype_list:
    for y in year_list:
        for s in s_list:
            ship_t=pd.DataFrame()
            tour_t=pd.DataFrame()
            for c in county_list:
                if t == "B2C":
                    ship=  pd.read_csv(f_dir+"Shipment2Fleet/{0}/{1}_payload_county{2}_shipall_s{3}_y{4}.csv". format(y,t,c,s,y))
                else:
                    ship=  pd.read_csv(f_dir+"Shipment2Fleet/{0}/{1}_payload_county{2}_shipall_A_s{3}_y{4}.csv". format(y,t,c,s,y))
                ship_t = pd.concat([ship_t,ship], ignore_index=True)
                tour=  pd.read_csv(f_dir+"Tour_plan/{0}/{1}_county{2}_carrier_s{3}_y{4}.csv".format(y,t,c,s,y))
                tour_t = pd.concat([tour_t,tour], ignore_index=True)
            for veh in dic_veh.keys():
                for fuel in dic_fuel.keys():
                    if fuel == "Diesel": 
                        veh_type=veh+"_D_"+fuel
                    else:
                        veh_type=veh+"_E_"+fuel    
                    try:
                        n_ship = len(ship_t[ship_t["veh_type"]==veh_type])
                    except:
                        n_ship =0 
                    try:
                        n_tour = len(tour_t[tour_t["vehicleTypeId"]==veh_type])
                    except:
                        n_tour = 0  
                    df=df.append({"year": y, "scenario":s, "shipment":t, "vehicle type": veh,"powertrain": fuel,"num_ship":n_ship,"num_tour": n_tour
                    }, ignore_index=True)

# %%
# Tour by fuel
for s in s_list:
    D_list=[]
    Ev_lsit=[]
    H2_list=[]
    Ph_list=[]
    for y in year_list:
        D_list.append(df[(df["scenario"]==s) & (df["year"]==y) & (df["powertrain"]=="Diesel") ]['num_tour'].sum()/
        df[(df["scenario"]==s) & (df["year"]==y)]['num_tour'].sum())
        Ev_lsit.append(df[(df["scenario"]==s) & (df["year"]==y) & (df["powertrain"]=="Battery Electric") ]['num_tour'].sum()/
        df[(df["scenario"]==s) & (df["year"]==y)]['num_tour'].sum())
        H2_list.append(df[(df["scenario"]==s) & (df["year"]==y) & (df["powertrain"]=="H2 Fuel Cell") ]['num_tour'].sum()/
        df[(df["scenario"]==s) & (df["year"]==y)]['num_tour'].sum())
        Ph_list.append(df[(df["scenario"]==s) & (df["year"]==y) & (df["powertrain"]=="PHEV") ]['num_tour'].sum()/
        df[(df["scenario"]==s) & (df["year"]==y)]['num_tour'].sum())    


    colors = sns.color_palette("pastel")
    labels=["Diesel","Battery Electric","H2 Fuel Cell","PHEV"]
    plt.figure(figsize = (8,6))
    plt.stackplot(year_list, D_list, Ev_lsit, H2_list, Ph_list,labels=labels, colors=colors )

    plt.legend(loc = "upper center", bbox_to_anchor=(1.1, 0.8), ncol=1)
    title='Tour plan fraction by powertrain type (tech level: {})'.format(s)
    plt.title(title)
    plt.ylabel('Fraction')
    plt.xticks(year_list, rotation=40)
    plt.savefig(f_dir+ '{}.png'.format(title))

# %%
s_list={"low" : "r", "central": "b", "high": "g"}
for veh in dic_veh.keys():
    plt.figure(figsize = (8,6))
    for s in s_list.keys():
        ND_list=[]
       
        for y in year_list:
            ND_list.append(1-df[(df["vehicle type"]==veh)& (df["scenario"]==s) & (df["year"]==y) & (df["powertrain"]=="Diesel") ]['num_tour'].sum()/
            df[(df["vehicle type"]==veh)& (df["scenario"]==s) & (df["year"]==y)]['num_tour'].sum())

        plt.plot(year_list,ND_list ,label=s, color=s_list[s])

    plt.legend(loc = "upper center", bbox_to_anchor=(1.1, 0.8), ncol=1)
    title='Tour plan fraction of alternative fuel {} by techology scenario'.format(dic_veh[veh])
    plt.title(title)
    plt.ylabel('Fraction')
    plt.ylim(0,1)
    plt.xticks(year_list, rotation=40)
    plt.savefig(f_dir+ '{}.png'.format(title))
# %%
for veh in dic_veh.keys():
    x=["Base", "Low tech", "Central tech", "High tech"]

    D_list=[]
    Ev_lsit=[]
    H2_list=[]
    Ph_list=[]
    y=2030
    s="low"
    D_list.append(df[(df["vehicle type"]==veh)& (df["scenario"]==s) & (df["year"]==y) & (df["powertrain"]=="Diesel") ]['num_tour'].sum()/
    df[(df["vehicle type"]==veh)&(df["scenario"]==s) & (df["year"]==y)]['num_tour'].sum())
    Ev_lsit.append(df[(df["vehicle type"]==veh)&(df["scenario"]==s) & (df["year"]==y) & (df["powertrain"]=="Battery Electric") ]['num_tour'].sum()/
    df[(df["vehicle type"]==veh)&(df["scenario"]==s) & (df["year"]==y)]['num_tour'].sum())
    H2_list.append(df[(df["scenario"]==s) & (df["year"]==y) & (df["powertrain"]=="H2 Fuel Cell") ]['num_tour'].sum()/
    df[(df["vehicle type"]==veh)&(df["scenario"]==s) & (df["year"]==y)]['num_tour'].sum())
    Ph_list.append(df[(df["vehicle type"]==veh)&(df["scenario"]==s) & (df["year"]==y) & (df["powertrain"]=="PHEV") ]['num_tour'].sum()/
    df[(df["vehicle type"]==veh)&(df["scenario"]==s) & (df["year"]==y)]['num_tour'].sum())   
    for s in s_list:
        y=2050
        D_list.append(df[(df["vehicle type"]==veh)&(df["scenario"]==s) & (df["year"]==y) & (df["powertrain"]=="Diesel") ]['num_tour'].sum()/
        df[(df["vehicle type"]==veh)&(df["scenario"]==s) & (df["year"]==y)]['num_tour'].sum())
        Ev_lsit.append(df[(df["vehicle type"]==veh)&(df["scenario"]==s) & (df["year"]==y) & (df["powertrain"]=="Battery Electric") ]['num_tour'].sum()/
        df[(df["vehicle type"]==veh)&(df["scenario"]==s) & (df["year"]==y)]['num_tour'].sum())
        H2_list.append(df[(df["vehicle type"]==veh)&(df["scenario"]==s) & (df["year"]==y) & (df["powertrain"]=="H2 Fuel Cell") ]['num_tour'].sum()/
        df[(df["vehicle type"]==veh)&(df["scenario"]==s) & (df["year"]==y)]['num_tour'].sum())
        Ph_list.append(df[(df["vehicle type"]==veh)&(df["scenario"]==s) & (df["year"]==y) & (df["powertrain"]=="PHEV") ]['num_tour'].sum()/
        df[(df["vehicle type"]==veh)&(df["scenario"]==s) & (df["year"]==y)]['num_tour'].sum())    

    D_list=np.array(D_list)
    Ev_lsit=np.array(Ev_lsit)
    H2_list=np.array(H2_list)
    Ph_list=np.array(Ph_list)    
    plt.figure(figsize = (8,6))
    plt.bar(x, D_list, color='r')
    plt.bar(x, Ev_lsit, bottom=D_list, color='b')
    plt.bar(x, H2_list, bottom=D_list+Ev_lsit, color='y')
    plt.bar(x, Ph_list, bottom=D_list+Ev_lsit+H2_list, color='g')
    plt.xlabel("Tech Scenarios")
    plt.ylabel('Fraction')
    plt.legend(["Diesel","Battery Electric","H2 Fuel Cell","PHEV"], loc = "upper center", bbox_to_anchor=(1.15, 0.8), ncol=1)
    title="Tour plan fraction of {} by powertrain type".format(dic_veh[veh])
    plt.title(title)
    plt.savefig(f_dir+ '{}.png'.format(title))
# %%
