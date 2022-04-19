import pandas as pd
county_list=[1, 13, 41, 55, 75, 81, 85, 95, 97]
f_dir="../../../FRISM_input_output_SF/Sim_outputs/Shipment2Fleet/"
for county in county_list:
    df = pd.read_csv(f_dir+"B2C_carrier_county{}_shipall.csv".format(county))
    df["num_veh_type_1"]=df["num_veh_type_1"].apply(lambda x: int((x+1)*1.5))
    df.to_csv(f_dir+f_dir+"B2C_carrier_county{}_shipall.csv".format(county), index = False, header=True)