import os
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-rt", "--run type", dest="run_type",
            help="initial or main ", required=True, type=str)
parser.add_argument("-cy", "--county", dest="county",
            help="county number ", default=21, type=int)
parser.add_argument("-st", "--shipe type", dest="stype",
            help="B2B or B2C ", default="B2B", type=str)                        
args = parser.parse_args()

if args.run_type == "initial":
    '''
    This is to create x % (-sr x) of sample from the tour_plan and shipment results at the population level
    After running this, it will save x % of sample in "frism_light/Tour_plan/" and "frism_light/Shipment2Fleet/" under the mian result folder (-md )
    The results folder at the population level should be under the main folder (-md )
    '''
    os.system("python frism_light_initial_setting.py \
             -sr 10 \
               -md ../../../Results_veh_tech_v1/ \
                   -sn high \
                   -yt 2050")
elif args.run_type == "main":
    '''
    For this, you should run "initial" just one time. Then, you can run this iteratively
    It is desinged to run each county and shipment type seperately. That means that the parallel run can generete results quickly.  
    ship type= ["B2B, "B2C"]
    County = [453, 491, 209, 55, 21, 53] for Austin
    '''
    os.system("python frism_light_tour_update.py \
            -sr 40 \
            -md ../../../Results_veh_tech_v1/ \
            -sn high \
            -yt 2050 \
            -cy {} \
            -st {} \
            -t ../../../FRISM_input_output_AT/Sim_inputs/Geo_data/tt_df_cbg.csv.gz \
            -d ../../../FRISM_input_output_AT/Sim_inputs/Geo_data/Austin_od_dist.csv\
            -ct ../../../FRISM_input_output_AT/Sim_inputs/Geo_data/Austin_freight_centroids.geojson \
            -vt ../../../Results_veh_tech_v1/frism_light/Tour_plan/vehicle_types_slow_y2050.csv".format(args.county, args.stype))
else:
    print ("please provide a correct run type")    
   