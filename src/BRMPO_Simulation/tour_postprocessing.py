# %%
import pandas as pd
from os.path import exists as file_exists
import os
from argparse import ArgumentParser
import json
import numpy as np
import h5py
# %%
def create_global_variable(input_setting):
    """
    state_id: state code (e.g., 6: CA)
    """
    global state_id
    global state_abbr
    global county_in_region
    global dic_veh
    global fdir_in_out
    global input_variables

    #folder_path
    fdir_in_out = input_setting['input_variables']['frism_data_folder']
    # variables
    state_id = input_setting['input_variables']['state_code']
    state_abbr = input_setting['input_variables']['state_abbr']
    county_in_region= input_setting['input_variables']['county_list']
    # dictionary
    dic_veh = input_setting['dic_veh']
    input_variables=input_setting['input_variables']


def county_to_all(ship_type, county_list,target_year,scenario,fdir_in,fdir_out, sample_rate):
    tour_num=0
    N_df_payload=pd.DataFrame()
    N_df_tour=pd.DataFrame()
    N_df_carrier=pd.DataFrame()    
    for count_num in county_list:
        df_payload = pd.read_csv(fdir_in+f"{ship_type}_county{count_num}_payload_s{scenario}_y{target_year}_sr{sample_rate}.csv").reset_index()
        df_tour = pd.read_csv(fdir_in+f"{ship_type}_county{count_num}_freight_tours_s{scenario}_y{target_year}_sr{sample_rate}.csv").reset_index()
        df_carrier = pd.read_csv(fdir_in+f"{ship_type}_county{count_num}_carrier_s{scenario}_y{target_year}_sr{sample_rate}.csv").reset_index()

        df_carrier["tourId"]=df_carrier["tourId"].apply(lambda x: x+tour_num)
        df_payload["tourId"]=df_payload["tourId"].apply(lambda x: x+tour_num)
        df_tour["tour_id"]=df_tour["tour_id"].apply(lambda x: x+tour_num)
        
        tour_num=df_carrier["tourId"].iloc[-1]+1
        N_df_payload=pd.concat([N_df_payload,df_payload], ignore_index=True).reset_index(drop=True)
        N_df_tour=pd.concat([N_df_tour,df_tour], ignore_index=True).reset_index(drop=True)
        N_df_carrier=pd.concat([N_df_carrier,df_carrier], ignore_index=True).reset_index(drop=True)
    if not file_exists(fdir_out):
        os.makedirs(fdir_out)    
    N_df_payload.to_csv(fdir_out+f"{ship_type}_all_payload_s{scenario}_y{target_year}_sr{sample_rate}.csv", index = False, header=True)
    N_df_tour.to_csv(fdir_out+f"{ship_type}_all_freight_tours_s{scenario}_y{target_year}_sr{sample_rate}.csv", index = False, header=True)
    N_df_carrier.to_csv(fdir_out+f"{ship_type}_all_carrier_s{scenario}_y{target_year}_sr{sample_rate}.csv", index = False, header=True)
    print ("{},{}:{}".format(ship_type,scenario,N_df_tour.shape[0]))          

    return N_df_payload, N_df_carrier  

def create_OD_matrix_by_time_step(num_taz, df,starthr,endhr):
    # Get unique locations
    # Create a matrix filled with zeros
    matrix = np.zeros((num_taz,num_taz))
    
    for tourId in df.tourId.unique():     
        df_by_tourID = df[df["tourId"]==tourId] 
        for stop_id in range(0, df_by_tourID["sequenceRank"].max()):
            origin = df_by_tourID[df_by_tourID["sequenceRank"]==stop_id]["locationZone"].values[0]
            detination = df_by_tourID[df_by_tourID["sequenceRank"]==(stop_id+1)]["locationZone"].values[0]
            departure_time= df_by_tourID[df_by_tourID["sequenceRank"]==stop_id]["start_hour"].values[0]
            
            if endhr - starthr >0: 
                if departure_time>=starthr and departure_time<endhr:
                    origin_idx = origin -1
                    dest_idx = detination -1
                    #print (origin_idx,dest_idx)
                    matrix[origin_idx, dest_idx] = matrix[origin_idx, dest_idx]+1
            else:
                if departure_time>=starthr or departure_time<endhr:
                    origin_idx = origin -1
                    dest_idx = detination -1
                    #print (origin_idx,dest_idx)
                    matrix[origin_idx, dest_idx] = matrix[origin_idx, dest_idx]+1                

    
    return matrix

# Create an HDF5 file with the specified two-layer structure
def create_freight_h5(filename, sample_data=True):
    """
    Create HDF5 file with:
    - First layer: Time periods ['am', 'ev', 'md', 'ni', 'pm']
    - Second layer: Truck types ['mfam_deltrk_trips', 'mfam_hvytrk_trips', 'mfam_medtrk_trips']
    
    Args:
        filename: Output HDF5 filename
        sample_data: If True, populate with random sample data
    """
    
    # Define the structure
    time_periods = ['am', 'ev', 'md', 'ni', 'pm']
    truck_types = ['ligttrk_trips', 'hvytrk_trips', 'medtrk_trips']
    
    with h5py.File(filename, 'w') as f:
        # Create groups for each time period
        for period in time_periods:
            period_group = f.create_group(period)
            
            # Create datasets for each truck type under each time period
            for truck_type in truck_types:
                truck_type="mf{}_".format(period)+truck_type
                if sample_data:
                    # Create sample data - adjust dimensions as needed
                    # Example: 1000 trips with 10 attributes each
                    data = np.zeros((3750,3750))
                else:
                    # Create empty dataset that can be resized later
                    data = np.array([])
                
                period_group.create_dataset(truck_type, data=data)
                
            # Add metadata attributes
            period_group.attrs['time_period'] = period
            period_group.attrs['description'] = f'Freight trips for {period} period'
    
    print(f"HDF5 file '{filename}' created successfully!")
    return filename

def add_data_to_h5(filename, time_period, truck_type, data):
    """
    Add or update data in existing HDF5 file
    
    Args:
        filename: HDF5 filename
        time_period: One of ['am', 'ev', 'md', 'ni', 'pm']
        truck_type: One of ['mfam_deltrk_trips', 'mfam_hvytrk_trips', 'mfam_medtrk_trips']
        data: numpy array to store
    """
    
    with h5py.File(filename, 'a') as f:
        # Delete existing dataset if present
        if truck_type in f[time_period]:
            del f[time_period][truck_type]
        
        # Create new dataset with provided data
        f[time_period].create_dataset(truck_type, data=data)
        print(f"Data added to {time_period}/{truck_type}")

def main(args=None):
    parser = ArgumentParser()
    parser.add_argument("-sn", "--scenario", dest="scenario",
                    help="scenario", required=True, type=str)                
    parser.add_argument("-yt", "--analysis year", dest="target_year",
                help="20XX", required=True, type=int)                           
    parser.add_argument("-sr", "--sample ratio", dest="sample_rate",
                        help="sampeing rate for light run 0-100", default=100, type=int)
    parser.add_argument("-sa", "--study_area ", dest="study_region",
                        help="ST, SF", required=True, type=str)    
    parser.add_argument("-tm", "--trip matrix ", dest="trip_matrix_gen",
                        help="Yes, No", required=True, type=str) 
    args = parser.parse_args()
    scenario=args.scenario
    year=args.target_year
    sample_ratio=args.sample_rate
    study_region = args.study_region
    trip_gen = args.trip_matrix_gen
    with open("input_setting_{}.json".format(study_region) , 'r') as openfile:
    # Reading from json file
        input_setting = json.load(openfile)
    # Generate global variables
    create_global_variable(input_setting)
    fdir_in= fdir_in_out+input_variables["sub_folder_tour_output"]+ f"{year}/" 
    fdir_out = fdir_in_out+input_variables["sub_folder_tour_output"]+ f"{year}_all/"

    # Create one single output file from county-based results
    df_b2b_payload, df_b2b_carrier=county_to_all("B2B", input_variables["county_list"],year,scenario,fdir_in,fdir_out, sample_ratio)
    df_b2c_payload, df_b2c_carrier =county_to_all("B2C", input_variables["county_list"],year,scenario,fdir_in,fdir_out, sample_ratio)

    # To generate Trip table
    if trip_gen == "Yes":
        # B2B processing 
        df_b2b_payload['locationZone'] = df_b2b_payload['locationZone'].astype(int)
        ## Convert second-based time to hour 
        df_b2b_payload['start_hour'] = df_b2b_payload.apply(lambda x: int((x['estimatedTimeOfArrivalInSec']+x["operationDurationInSec"])/3600),axis=1)
        df_b2b_payload['start_hour'] = df_b2b_payload['start_hour'].apply(lambda x: x%24)
        ## Generate payload by vehicle type group
        df_payload_b2b_ld1 = df_b2b_payload[df_b2b_payload["tourId"].isin(df_b2b_carrier[df_b2b_carrier["vehicleTypeId"].str.contains('ld1')]["tourId"].unique())]
        df_payload_b2b_ld3 = df_b2b_payload[df_b2b_payload["tourId"].isin(df_b2b_carrier[df_b2b_carrier["vehicleTypeId"].str.contains('ld3')]["tourId"].unique())]
        df_payload_b2b_md = df_b2b_payload[df_b2b_payload["tourId"].isin(df_b2b_carrier[df_b2b_carrier["vehicleTypeId"].str.contains('md')]["tourId"].unique())]
        df_payload_b2b_hdv = df_b2b_payload[df_b2b_payload["tourId"].isin(df_b2b_carrier[df_b2b_carrier["vehicleTypeId"].str.contains('hdv')]["tourId"].unique())]
        df_payload_b2b_hdt = df_b2b_payload[df_b2b_payload["tourId"].isin(df_b2b_carrier[df_b2b_carrier["vehicleTypeId"].str.contains('hdt')]["tourId"].unique())]

        # B2C processing     
        df_b2c_payload['locationZone'] = df_b2c_payload['locationZone'].astype(int)
        ## Convert second-based time to hour 
        df_b2c_payload['start_hour'] = df_b2c_payload.apply(lambda x: int((x['estimatedTimeOfArrivalInSec']+x["operationDurationInSec"])/3600),axis=1)
        df_b2c_payload['start_hour'] = df_b2c_payload['start_hour'].apply(lambda x: x%24)
        ## Generate payload by vehicle type group
        df_payload_b2c_ld1 = df_b2c_payload[df_b2c_payload["tourId"].isin(df_b2c_carrier[df_b2c_carrier["vehicleTypeId"].str.contains('ld1')]["tourId"].unique())]
        df_payload_b2c_ld3 = df_b2c_payload[df_b2c_payload["tourId"].isin(df_b2c_carrier[df_b2c_carrier["vehicleTypeId"].str.contains('ld3')]["tourId"].unique())]
        df_payload_b2c_md = df_b2c_payload[df_b2c_payload["tourId"].isin(df_b2c_carrier[df_b2c_carrier["vehicleTypeId"].str.contains('md')]["tourId"].unique())]
        # To combine B2B and B2C, avoide duplicated tourID in B2B and B2C
        b2b_tour_id_max = df_b2b_payload["tourId"].max()
        df_payload_b2c_ld1["tourId"]=df_payload_b2c_ld1["tourId"].apply(lambda x: x+b2b_tour_id_max+1)
        df_payload_b2c_ld3["tourId"]=df_payload_b2c_ld3["tourId"].apply(lambda x: x+b2b_tour_id_max+1)
        df_payload_b2c_md["tourId"]=df_payload_b2c_md["tourId"].apply(lambda x: x+b2b_tour_id_max+1)

        # Convert agency-based vehicle types by combining B2B and B2C file by FAMOS vehicle tpye 
        LD_df = pd.concat([df_payload_b2b_ld1,df_payload_b2c_ld1], ignore_index=True).reset_index(drop=True)
        MD_df=pd.concat([df_payload_b2b_ld3,df_payload_b2c_ld3,df_payload_b2b_md,df_payload_b2c_md,df_payload_b2b_hdv], ignore_index=True).reset_index(drop=True)
        HD_df=df_payload_b2b_hdt      

        # Define time and vehicle type
        dic_time= {'am': [6,9],
                'md': [9,15],
                'pm': [15,18],
                'ev':[18,20],
                'ni': [20,6]}

        dic_veh={'ligttrk_trips': LD_df,
                'medtrk_trips': MD_df,
                'hvytrk_trips': HD_df}
        num_taz = 3750

        h5_file = create_freight_h5(fdir_out+'FRISM_trips.h5', sample_data=True)
        for time_period in dic_time.keys():
            for veh_type in dic_veh.keys():
                custom_data = create_OD_matrix_by_time_step(num_taz,dic_veh[veh_type], dic_time[time_period][0],dic_time[time_period][1])
                print (time_period, veh_type) 
                sub_file_name= 'mf{0}_{1}'.format(time_period, veh_type)
                print(np.sum(custom_data))
                add_data_to_h5(h5_file, time_period, sub_file_name, custom_data)

if __name__ == "__main__":
    main()
