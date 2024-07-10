# %%
import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import pytz
from datetime import datetime

# %%
utc_timezone = pytz.timezone('UTC')
pst_timezone = pytz.timezone('America/Los_Angeles') 




# Convert string to datetime object
datetime_object = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')

# %%
def read_json_file(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data

# %%
file_dict="../../../FRISM_input_output_ST/Model_carrier_op/Amazon/almrrc2021-data-training/model_build_inputs/"

filename = 'actual_sequences.json'
sequence_data = read_json_file(file_dict+filename)
'''
{
  "RouteID_<hex-hash>": {
    "actual": {
      "<stop-id>": "<uint-number>",
      "..."
    }
  },
  "..."
}
'''

filename = 'package_data.json'
package_data = read_json_file(file_dict+filename)
'''
{
  "<RouteID_<hex-hash>": {
    "<stop-id>": {
      "PackageID_<hex-hash>": {
        "scan_status": "<scan-status>",
        "time_window": {
          "start_time_utc": "<YYYY-MM-DD hh:mm:ss>",
          "end_time_utc": "<YYYY-MM-DD hh:mm:ss>"
        },
        "planned_service_time_seconds": "<uint-number>",
        "dimensions": {
          "depth_cm": "<float-number>",
          "height_cm": "<float-number>",
          "width_cm": "<float-number>"
        }
      },
      "..."
    },
    "..."
  },
  "..."
}
'''
filename = 'route_data.json'
route_data = read_json_file(file_dict+filename)

'''
{
  "RouteID_<hex-hash>": {
    "station_code": "<station-code>",
    "date_YYYY_MM_DD": "<YYYY-MM-DD>",
    "departure_time_utc": "<hh:mm:ss>",
    "executor_capacity_cm3": "<uint32-number>",
    "route_score": "<route-score>",
    "stops": {
      "<stop-id>": {
        "lat": "<float-number>",
        "lng": "<float-number>",
        "type": "<stop-type>",
        "zone_id": "<zone-id>"
      },
      "..."
    },
    "..."
  },
  "..."
}
'''

filename = 'travel_times.json'
tt_data = read_json_file(file_dict+filename)
'''
Travel times provided in the travel_times.json and new_travel_times.json files are,
for a given pair of stops, the average of historically realized travel times between 
all combinations of package delivery locations between those stops, specified in seconds.
'''

# %%
# unique route ID 
routeId_list = list(sequence_data.keys())
# a route in the data 
eampleRoute = sequence_data[routeId_list[0]]
# unique stops in a route
stop_list_inroute =list(eampleRoute['actual'].keys())
# total lenth of routes -> route length distribution; travel time
len(stop_list_inroute)


# package info
# given route and given stop
package_info= package_data[routeId_list[0]][stop_list_inroute[0]]
package_list_atstop =list(package_info.keys())
scan_status=package_info[package_list_atstop[0]]['scan_status']
service_time=package_info[package_list_atstop[0]]['planned_service_time_seconds'] # service_time disribution in second 
tw_lower=package_info[package_list_atstop[0]]['time_window']['start_time_utc']
tw_upper=package_info[package_list_atstop[0]]['time_window']['end_time_utc']
size_package = package_info[package_list_atstop[0]]['dimensions']['depth_cm'] * \
            package_info[package_list_atstop[0]]['dimensions']['height_cm'] * \
            package_info[package_list_atstop[0]]['dimensions']['width_cm'] * 10**(-6)

## any relationship between size of package and service time?

# route info
route_info=route_data[routeId_list[0]]
departure_time_utc= route_info['departure_time_utc'] # need to convert it to local time using lat, long
veh_cap =  route_info['executor_capacity_cm3']* 10**(-6)
# only need one point to conver utc time to local 
lat=route_info['stops'][stop_list_inroute[0]]['lat']
lng=route_info['stops'][stop_list_inroute[0]]['lng']





# station code 
station_code= route_info['station_code'] # this might be used to guess location DLA - LA, 
def utc_converter(time, station_id):
    LS=['DLA3', 'DSE4', 'DSE5', 'DLA9', 'DLA7',
        'DLA8', 'DLA5',  'DLA4', 'DSE2']
    AT=['DAU1']
    CH=['DCH4','DCH3', 'DCH1','DCH2', ]
    BO=['DBO2', 'DBO3','DBO1']
    time_list=time.split(":")
    if station_id in LS:
        new_time=(int(time_list[0])+16)%24
    elif station_id in AT:
        new_time=(int(time_list[0])+18)%24  
    elif station_id in CH:
        new_time=(int(time_list[0])+18)%24  
    elif station_id in BO:
        new_time=(int(time_list[0])+19)%24
    return int(new_time)+int(time_list[1])/60               
# Seattle, Los Angeles, Austin, Chicago, and Boston
# Zone
zone_id = route_info['stops'][stop_list_inroute[0]]['zone_id']
zone_L1=zone_id.split("-")[0]
zone_L2=zone_id.split("-")[1].split(".")[0]
zone_L3=zone_id.split("-")[1].split(".")[1]


## Create dataframe route_df
column_names= ['r_id', 'station_id', 'departure_time_utc', 'd_time_local', 'veh_cap', 'num_stops']
route_df= pd.DataFrame(columns=column_names)
n=0
for r_id in routeId_list:
    eampleRoute = sequence_data[r_id]
    stop_list_inroute =list(eampleRoute['actual'].keys())
    route_info=route_data[r_id]
    #departure_time_utc= route_info["date_YYYY_MM_DD"]+" "+route_info['departure_time_utc'] # need to convert it to local time using lat, long
    departure_time_utc=route_info['departure_time_utc'] # need to convert it to local time using lat, long
    veh_cap =  route_info['executor_capacity_cm3']* 10**(-6)
    station_id= route_info['station_code']
    temp_df = {'r_id':r_id, 
               'station_id': station_id, 
               'departure_time_utc': departure_time_utc,
               'd_time_local': utc_converter(departure_time_utc, station_id),
                 'veh_cap': veh_cap, 
                 'num_stops': len(stop_list_inroute)}
    route_df.loc[n]=temp_df
    n=n+1
route_df.to_csv(file_dict+"route_df.csv" )

bins=np.arange(5,11,0.25)

plt.figure(figsize = (8,6))
plt.hist(route_df['d_time_local'], color ="blue", density=True, bins=bins)
plt.title("Density of Departure time")
plt.savefig('../../../FRISM_input_output_ST/Sim_outputs/Generation/amazon_departure.png')

bins=np.arange(0,250,10)
plt.figure(figsize = (8,6))
plt.hist(route_df['num_stops'], color ="blue", density=True, bins=bins)
plt.title("Density of stops")
plt.savefig('../../../FRISM_input_output_ST/Sim_outputs/Generation/amazon_stop.png')


plt.figure(figsize = (8,6))
plt.hist(route_df['veh_cap'], color ="blue", density=True)
plt.title("Density of veh_cap")
plt.savefig('../../../FRISM_input_output_ST/Sim_outputs/Generation/amazon_v_cap.png')

plt.figure(figsize = (8,6))
plt.scatter(route_df['num_stops'],route_df['veh_cap'])
plt.title("Capacity vs Num_stops")
plt.savefig('../../../FRISM_input_output_ST/Sim_outputs/Generation/amazon_Cap_stops.png')


bins=np.arange(0,250,10)
plt.figure(figsize = (8,6))
plt.hist(route_df[route_df['veh_cap']<3.5]['num_stops'], color ="blue", density=True,  bins=bins)
plt.title("Density of veh_cap with v_cap <3.5")
plt.savefig('../../../FRISM_input_output_ST/Sim_outputs/Generation/amazon_v_cap_small.png')

bins=np.arange(0,250,10)
plt.figure(figsize = (8,6))
plt.hist(route_df[route_df['veh_cap']>4]['num_stops'], color ="blue", density=True,  bins=bins)
plt.title("Density of veh_cap with v_cap <4")
plt.savefig('../../../FRISM_input_output_ST/Sim_outputs/Generation/amazon_v_cap_md.png')



plt.figure(figsize = (8,6))
plt.scatter(route_df['num_stops'],route_df['d_time_local'])
plt.title("Depature time vs Num_stops")
plt.savefig('../../../FRISM_input_output_ST/Sim_outputs/Generation/amazon_dtime_stops.png')

SA=['DSE4', 'DSE5', 'DSE2']

route_df_SA= route_df[route_df["station_id"].isin(SA)]
plt.figure(figsize = (8,6))
plt.scatter(route_df_SA['num_stops'],route_df_SA['d_time_local'])
plt.title("Depature time vs Num_stops")
plt.savefig('../../../FRISM_input_output_ST/Sim_outputs/Generation/amazon_dtime_stops_SA.png')

## Create dataframe station_df
column_names= ['r_id', 'stop_id', 'num_package','stop_time', 'size']
station_df= pd.DataFrame(columns=column_names)
n=0
for r_id in routeId_list:
    eampleRoute = sequence_data[r_id]
    stop_list_inroute =list(eampleRoute['actual'].keys())
    for s_id in stop_list_inroute:

        package_info= package_data[r_id][s_id]
        package_list_atstop =list(package_info.keys())
        service_time=0
        size_package=0
        for p_id in package_list_atstop: 
            service_time= service_time+package_info[p_id]['planned_service_time_seconds'] # service_time disribution in second 
            size_package= size_package+ package_info[package_list_atstop[0]]['dimensions']['depth_cm'] * \
                    package_info[package_list_atstop[0]]['dimensions']['height_cm'] * \
                    package_info[package_list_atstop[0]]['dimensions']['width_cm'] * 10**(-6)
        if len(package_list_atstop) >0:    
            service_time= service_time/len(package_list_atstop)
            size_package= size_package/len(package_list_atstop)
        else:    
            service_time= "Nan"
            size_package= "Nan"
        temp_df = {'r_id':r_id, 
                'stop_id': s_id, 
                'num_package': len(package_list_atstop),
                    'stop_time': service_time, 
                    'size': size_package}
        station_df.loc[n]=temp_df
        n=n+1
#

station_df.to_csv(file_dict+"station_df.csv" )



station_df_val= station_df[station_df["stop_time"]!="Nan"]

bins=np.arange(0,500,50)
plt.figure(figsize = (8,6))
plt.hist(station_df_val[station_df_val['stop_time']<=500]['stop_time'], color ="blue", density=True, bins=bins)
plt.title("Density of Delivery Stop_time")
plt.savefig('../../../FRISM_input_output_ST/Sim_outputs/Generation/amazon_stop_time_small.png')


bins=np.arange(500,8050,50)
plt.figure(figsize = (8,6))
plt.hist(station_df_val[station_df_val['stop_time']>500]['stop_time'], color ="blue", density=True, bins=bins)
plt.title("Density of Delivery Stop_time")
plt.savefig('../../../FRISM_input_output_ST/Sim_outputs/Generation/amazon_stop_time_large.png')


bins=np.arange(0,120,5)
plt.figure(figsize = (8,6))
plt.hist(station_df_val['num_package'], color ="blue", density=True, bins=bins)
plt.title("Density of num_packages per stops")
plt.savefig('../../../FRISM_input_output_ST/Sim_outputs/Generation/amazon_num_packgaes.png')


plt.figure(figsize = (8,6))
plt.scatter(station_df_val['stop_time'],station_df_val['num_package'])
plt.title("stop_time vs num_package")
plt.savefig('../../../FRISM_input_output_ST/Sim_outputs/Generation/amazon_stime_num_p.png')



# Create datatframe for package for time
