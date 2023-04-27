# %%
from re import A
import pandas as pd
import numpy as np
import geopandas as gpd
from argparse import ArgumentParser
import random
import config
import glob
from os.path import exists as file_exists
import os
from alive_progress import alive_bar
import time
from shapely.geometry import Point
import math 

def b2b_d_shipment_by_commodity_v2(fdir,commoidty, weight_theshold, CBGzone_df,sel_county,ship_direction, county_wo_sel, b2b_day_factor,year, scenario):
    #daily_b2b_fname=fdir+'Daily_sctg%s_OD_%s_%s.csv' % (commoidty, sel_county,ship_direction)
    # if file_exists(daily_b2b_fname):
    #     B2BF=pd.read_csv(daily_b2b_fname, header=0, sep=',')
    # else:    
    B2BF=pd.DataFrame()
    sub_fdir="{}_{}/".format(year,scenario)
    for filename in glob.glob(fdir+sub_fdir+'*.csv'):
        #print (filename)
        #filename="../../../FRISM_input_output_AT/Sim_inputs/Synth_firm_results/2050_HOP_highp2/private_truck_shipment_sctg5.csv"
        temp= pd.read_csv(filename, header=0, sep=',')
        if temp.shape[0] >0: 
            if "fleet_id" in temp.columns:
                temp["SellerID"] = temp.apply(lambda x: str(x["SellerID"]) + "_" + str(x["fleet_id"]), axis=1)
                temp = temp.drop("fleet_id", axis=1)
            else:
                temp["SellerID"] = temp.apply(lambda x: str(x["SellerID"]) + "_1", axis=1)
            temp["BuyerID"] = temp.apply(lambda x: str(x["BuyerID"]) + "_1", axis=1)        
            temp=temp.astype({'BuyerID': 'string',
            "BuyerZone":"int64",
            "BuyerNAICS":"string",
            "SellerID":"string",
            "SellerZone":"int64",
            "SellerNAICS":"string",
            "TruckLoad": "float64",
            "SCTG_Group": "int64",
            "shipment_id":"int64",
            "orig_FAFID":"int64",
            "dest_FAFID":"int64",
            "mode_choice":"string",
            "probability":"float64",
            "Distance":"float64",
            "Travel_time":"float64" 
            })
            # Add SellerCounty and BuyerCounty for filering 
            temp = temp.merge(CBGzone_df[['MESOZONE','County']], left_on="SellerZone", right_on='MESOZONE', how='left')
            temp=temp.rename({'County':'SellerCounty'}, axis=1)
            temp = temp.merge(CBGzone_df[['MESOZONE','County']], left_on="BuyerZone", right_on='MESOZONE', how='left')
            temp=temp.rename({'County':'BuyerCounty'}, axis=1)
            if sel_county != 9999:
                if ship_direction == "out":
                    temp= temp[temp['SellerCounty']==sel_county].reset_index(drop=True)
                elif ship_direction == "in":
                    temp= temp[(temp['BuyerCounty']==sel_county) & (temp['SellerCounty']!=sel_county)].reset_index(drop=True)
                elif ship_direction == "all":
                    temp= temp[(temp['BuyerCounty']==sel_county) | (temp['SellerCounty']==sel_county)].reset_index(drop=True)
                    temp= temp[~temp['SellerCounty'].isin(county_wo_sel)].reset_index(drop=True)
            temp['TruckLoad']=temp['TruckLoad']*2000
            temp["D_truckload"]=0
            temp["D_selection"]=0
            temp["D_truckload"]=temp['TruckLoad']
            #temp["D_truckload"]=temp['TruckLoad'].apply(lambda x: b2b_d_truckload(x, weight_theshold))
            temp["D_selection"]=temp['TruckLoad'].apply(lambda x: b2b_d_select_with_ship_size(x, weight_theshold, b2b_day_factor))
            #temp["D_selection"]=temp['TruckLoad'].apply(lambda x: b2b_d_select(x, weight_theshold))
            temp=temp.query('D_selection ==1')
            B2BF=pd.concat([B2BF,temp],ignore_index=True)
    #B2BF.to_csv(fdir+'Daily_sctg%s_OD_%s_%s.csv' % (commoidty, sel_county,ship_direction), index = False, header=True)
    return B2BF


def b2b_d_shipment_by_commodity(fdir,commoidty, weight_theshold, CBGzone_df,sel_county,ship_direction, county_wo_sel, b2b_day_factor):
    daily_b2b_fname=fdir+'Daily_sctg%s_OD_%s_%s.csv' % (commoidty, sel_county,ship_direction)
    # if file_exists(daily_b2b_fname):
    #     B2BF=pd.read_csv(daily_b2b_fname, header=0, sep=',')
    # else:    
    B2BF=pd.DataFrame()
    sub_fdir="sctg%s_truck/" %commoidty
    for filename in glob.glob(fdir+sub_fdir+'*.csv'):
        temp= pd.read_csv(filename, header=0, sep=',')
        temp=temp.astype({'BuyerID': 'int64',
        "BuyerZone":"int64",
        "BuyerNAICS":"string",
        "SellerID":"int64",
        "SellerZone":"int64",
        "SellerNAICS":"string",
        "TruckLoad": "float64",
        "SCTG_Group": "int64",
        "shipment_id":"int64",
        "orig_FAFID":"int64",
        "dest_FAFID":"int64",
        "mode_choice":"string",
        "probability":"float64",
        "Distance":"float64",
        "Travel_time":"float64" 
        })
        # Add SellerCounty and BuyerCounty for filering 
        temp = temp.merge(CBGzone_df[['MESOZONE','County']], left_on="SellerZone", right_on='MESOZONE', how='left')
        temp=temp.rename({'County':'SellerCounty'}, axis=1)
        temp = temp.merge(CBGzone_df[['MESOZONE','County']], left_on="BuyerZone", right_on='MESOZONE', how='left')
        temp=temp.rename({'County':'BuyerCounty'}, axis=1)
        if sel_county != 9999:
            if ship_direction == "out":
                temp= temp[temp['SellerCounty']==sel_county].reset_index(drop=True)
            elif ship_direction == "in":
                temp= temp[(temp['BuyerCounty']==sel_county) & (temp['SellerCounty']!=sel_county)].reset_index(drop=True)
            elif ship_direction == "all":
                temp= temp[(temp['BuyerCounty']==sel_county) | (temp['SellerCounty']==sel_county)].reset_index(drop=True)
                temp= temp[~temp['SellerCounty'].isin(county_wo_sel)].reset_index(drop=True)
        temp['TruckLoad']=temp['TruckLoad']*2000
        temp["D_truckload"]=0
        temp["D_selection"]=0
        temp["D_truckload"]=temp['TruckLoad']
        #temp["D_truckload"]=temp['TruckLoad'].apply(lambda x: b2b_d_truckload(x, weight_theshold))
        temp["D_selection"]=temp['TruckLoad'].apply(lambda x: b2b_d_select_with_ship_size(x, weight_theshold, b2b_day_factor))
        #temp["D_selection"]=temp['TruckLoad'].apply(lambda x: b2b_d_select(x, weight_theshold))
        temp=temp.query('D_selection ==1')
        B2BF=pd.concat([B2BF,temp],ignore_index=True)
    B2BF.to_csv(fdir+'Daily_sctg%s_OD_%s_%s.csv' % (commoidty, sel_county,ship_direction), index = False, header=True)
    return B2BF
