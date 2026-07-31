import pandas as pd
import numpy as np
import geopandas as gpd
from argparse import ArgumentParser
import random
import os
import time
from shapely.geometry import Point


# %%

class Departure_distribution:
    """
    * A class for truck departure distribution by vehicle type: Generate B2B and B2C seperately *
    file_path: str, fdir_in_out+'/Sim_inputs/Veh_operations/'
    shipment_type: str "B2B or "B2C"
    dic_veh: dictionry that include vehicle type and capacity 
    """    
    def __init__(self, file_path=None, shipment_type=None, dic_veh=None):
        self.file_path =file_path
        self.shipment_type=shipment_type
        self.dic_veh=dic_veh
        self.departure_distribution = pd.DataFrame()

        self._load_departure_time_file(self.file_path, self.shipment_type)

    def _load_departure_time_file(self, file_path, shipment_type):
        # fdir_truck=fdir_in_out+'/Model_carrier_op/INRIX_processing/'
        if shipment_type == 'B2C':
            temp_df=pd.read_csv(file_path+'delivery_fleet_departure.csv', header=0, sep=',')
            temp_df["start_hour"]=temp_df["d_time_local"].apply(lambda x: int(x))
            temp_df=temp_df.groupby(['start_hour'])["station_id"].count().reset_index(name='obs_trips')
            
            df_dpt_dist=pd.DataFrame({"start_hour": list(range(0, 24))})
            df_dpt_dist=df_dpt_dist.merge(temp_df[["start_hour", "obs_trips"]], on="start_hour", how="left")
            df_dpt_dist.fillna({"obs_trips":0}, inplace = True)
            # df_dpt_dist["veh_type"]='MD'
            df_dpt_dist['pro_trips']= df_dpt_dist['obs_trips']/df_dpt_dist['obs_trips'].sum()
            df_dpt_dist['cdf_low']=0.0
            df_dpt_dist['cdf_up']=df_dpt_dist['pro_trips']
            for i in range(1,df_dpt_dist.shape[0]):
                df_dpt_dist.loc[i,'cdf_up']=df_dpt_dist.loc[i-1,'cdf_up']+df_dpt_dist.loc[i,'pro_trips']
                df_dpt_dist.loc[i,'cdf_low']=df_dpt_dist.loc[i-1,'cdf_up'] 
            for veh in self.dic_veh.keys():
                df_dpt_dist["veh_type"]=veh
                self.departure_distribution=pd.concat([self.departure_distribution,df_dpt_dist], ignore_index=True)


        elif shipment_type == 'B2B':
            for veh in self.dic_veh.keys():
                if veh in ["ld1", "ld3", "mdv"]:
                    g="MD"
                else:
                    g="HD"    
                temp_df=pd.read_csv(file_path+'depature_dist_by_cbg_{}.csv'.format(g), header=0, sep=',')
                temp_df=temp_df.groupby(['start_hour'])['Trip'].sum().reset_index(name='obs_trips')

                df_dpt_dist=pd.DataFrame({"start_hour": list(range(0, 24))})
                df_dpt_dist=df_dpt_dist.merge(temp_df[["start_hour", "obs_trips"]], on="start_hour", how="left")
                df_dpt_dist.fillna({"obs_trips":0}, inplace = True)
                df_dpt_dist["veh_type"]=veh
                df_dpt_dist['pro_trips']= df_dpt_dist['obs_trips']/df_dpt_dist['obs_trips'].sum()
                df_dpt_dist['cdf_low']=0.0
                df_dpt_dist['cdf_up']=df_dpt_dist['pro_trips']
                for i in range(1,df_dpt_dist.shape[0]):
                    df_dpt_dist.loc[i,'cdf_up']=df_dpt_dist.loc[i-1,'cdf_up']+df_dpt_dist.loc[i,'pro_trips']
                    df_dpt_dist.loc[i,'cdf_low']=df_dpt_dist.loc[i-1,'cdf_up']

                self.departure_distribution=pd.concat([self.departure_distribution,df_dpt_dist], ignore_index=True)     

class Vehicle_energy:
    """
    * A class for truck departure distribution by vehicle type: Generate B2B and B2C seperately *
    stock_file: str, stock_file = fdir_in_out+'/Sim_inputs/Synth_firm_pop/'TDA_Base.csv'
    target_year: int, scenario year
    dic_crosswalk_TDA_class: dictionry (key: TDA file Class; value: synthfirm Class)
    dic_crosswalk_TDA_Powertrain: dictionry  (key: TDA file Powertrain; value: synthfirm Powertain)
    """  
    def __init__(self, stock_file=None, target_year=None, dic_crosswalk_TDA_class = None, dic_crosswalk_TDA_Powertrain=None, dic_veh = None):
        self.stock_file =stock_file
        self.target_year=target_year
        self.dic_crosswalk_TDA_class=dic_crosswalk_TDA_class
        self.dic_crosswalk_TDA_Powertrain=dic_crosswalk_TDA_Powertrain
        self.dic_veh=dic_veh
        self.dic_energy = {}

        self._create_energy_dictionary(self.stock_file, self.target_year)

    def _create_energy_dictionary (self, file_path, target_year):
        vehcile_stock=pd.read_csv(file_path, header=0, sep=',')
        vehcile_stock = vehcile_stock[(vehcile_stock["Class"].isin(self.dic_crosswalk_TDA_class.keys())) & (vehcile_stock["Powertrain"].isin(self.dic_crosswalk_TDA_Powertrain.keys()))]
        vehcile_stock["Class"]=vehcile_stock["Class"].apply(lambda x: self.dic_crosswalk_TDA_class[x])
        vehcile_stock["Powertrain"]=vehcile_stock["Powertrain"].apply(lambda x: self.dic_crosswalk_TDA_Powertrain[x] if self.dic_crosswalk_TDA_Powertrain[x] else x)
        self.dic_energy={veh_class: {self.dic_crosswalk_TDA_Powertrain[veh_fuel]: 1 for veh_fuel in self.dic_crosswalk_TDA_Powertrain.keys()}  for veh_class in self.dic_veh.keys()}
        for veh_class in self.dic_energy.keys():
            veh_class_synthfirm= self.dic_veh[veh_class]['synthfirm_name']
            for veh_powertrain in self.dic_energy[veh_class].keys():
                temp= vehcile_stock[(vehcile_stock["Year"] == target_year) &
                    (vehcile_stock["Powertrain"]==veh_powertrain) &
                    (vehcile_stock["Class"]==veh_class_synthfirm) & 
                    (vehcile_stock["mpgge"] >=4) & 
                    (vehcile_stock["MY"] > (target_year-30))]
                try: 
                    temp['w_mpgge']= temp.apply(lambda x: x["mpgge"]*x["Stock"], axis=1)
                    mpg= temp["w_mpgge"].sum()/temp["Stock"].sum()
                except:
                    mpg=0.1
                if pd.isna(mpg):
                    mpg =0.1      
                # Replace the mpge using AFLEET input (https://afleet.esia.anl.gov/afleet/total-cost-ownership-calculator) to prevent errors in TDA
                if veh_class_synthfirm == 'Class 1&2A Vocational':
                    if  veh_powertrain == 'Battery Electric':
                        mpg= max(mpg,(73.5 + 44.6)/2)
                    elif  veh_powertrain == 'H2 Fuel Cell':
                        mpg= max(mpg,(41.4 + 24.8)/2)                            
                    elif  veh_powertrain == 'PHEV':
                        mpg= max(mpg,(35.2 + 17.9)/2)
                elif veh_class_synthfirm == 'Class 2B&3 Vocational':
                    if  veh_powertrain == 'Battery Electric':
                        mpg= max(mpg, 44.6)
                    elif  veh_powertrain == 'H2 Fuel Cell':
                        mpg= max(mpg, 24.8)                          
                    elif  veh_powertrain == 'PHEV':
                        mpg= max(mpg, 17.9)  
                elif veh_class_synthfirm == 'Class 4-6 Vocational':
                    if  veh_powertrain == 'Battery Electric':
                        mpg= max(mpg, 26.1)
                    elif  veh_powertrain == 'H2 Fuel Cell':
                        mpg= max(mpg, 16.3)                          
                    elif  veh_powertrain == 'PHEV':
                        mpg= max(mpg, 9.9) 
                elif veh_class_synthfirm == 'Class 7&8 Tractor':
                    if  veh_powertrain == 'Battery Electric':
                        mpg= max(mpg, 12.7) 
                    elif  veh_powertrain == 'H2 Fuel Cell':
                        mpg= max(mpg, 7.9)                           
                    elif  veh_powertrain == 'PHEV':
                        mpg= max(mpg, 7.3)
                elif veh_class_synthfirm == 'Class 7&8 Vocational':
                    if  veh_powertrain == 'Battery Electric':
                        mpg= max(mpg, 23.1) 
                    elif  veh_powertrain == 'H2 Fuel Cell':
                        mpg= max(mpg, 14.5)                           
                    elif  veh_powertrain == 'PHEV':
                        mpg= max(mpg, 8.8)  

                if pd.isna(mpg):
                    self.dic_energy[veh_class][veh_powertrain]= 0.1
                else: 
                    self.dic_energy[veh_class][veh_powertrain]= mpg
        self.dic_energy["hdt"]['Gasoline']= self.dic_energy["hdt"]['Diesel'] *0.82             

    """
    expected outcome
        {'Class 1&2A Vocational': {'Diesel': 12.546266518568675,
        'Gasoline': 9.622058941864163,
        'Battery Electric': 0.1,
        'H2 Fuel Cell': 0.1,
        'PHEV': 0.1},
        'Class 2&B3 Vocational': {'Diesel': 12.445564921797056,
        'Gasoline': 8.853391687482597,
        'Battery Electric': 23.091,
        'H2 Fuel Cell': 0.1,
        'PHEV': 0.1},
        'Class 4-6 Vocational': {'Diesel': 7.8547431270155395,
        'Gasoline': 6.6089506704047,
        'Battery Electric': 16.431362385445546,
        'H2 Fuel Cell': 0.1,
        'PHEV': 0.1},
        'Class 7&8 Tractor': {'Diesel': 5.455022304475813,
        'Gasoline': 5.280320490479675,
        'Battery Electric': 5.563471212,
        'H2 Fuel Cell': 0.1,
        'PHEV': 0.1},
        'Class 7&8 Vocational': {'Diesel': 5.373479341019703,
        'Gasoline': 5.309067343133419,
        'Battery Electric': 8.771,
        'H2 Fuel Cell': 0.1,
        'PHEV': 0.1}}
    """                             

class Vius_truck_distribution:
    def __init__(self, vius_file=None):
        self.vius_file =vius_file
        self.vius= pd.read_csv(vius_file, header=0, sep=',')
        #Create probability for b2c shipment
        GROUP_COL = "SCTG_VIUS_Group"
        CLASS_COL = "VEH_CLASS_SynthFirm"
        SHARE_COLS = ["RO_0_50", "RO_51_100", "RO_101_200", "RO_201_500", "RO_GT500"]
        
        SOURCE_GROUP = 5                  # group the new one is derived from
        NEW_GROUP = 99                    # label for the derived group
        SOURCE_CLASSES = ["hdt", "hdv"]   # classes to be absorbed
        TARGET_CLASS = "mdv"              # class that absorbs them

        new = self.vius.loc[self.vius[GROUP_COL] == SOURCE_GROUP].copy()
        new[GROUP_COL] = NEW_GROUP
        
        src_mask = new[CLASS_COL].isin(SOURCE_CLASSES)
        tgt_mask = new[CLASS_COL] == TARGET_CLASS
        
        absorbed = new.loc[src_mask, SHARE_COLS].sum()          # hdt + hdv, per column
        new.loc[tgt_mask, SHARE_COLS] += absorbed.values        # fold into mdv
        new.loc[src_mask, SHARE_COLS] = 0.0                     # zero out hdt / hdv
        
        # --------------------------------------------- 3. append, keeping originals
        self.vius = pd.concat([self.vius, new], ignore_index=True)
        self.vius.index.name = None
 



