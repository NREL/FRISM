state_CBSA = ["12420","19100","26420","41700"]
study_CBSA= ["12420"] # "41700" =San Antonio-New Braunfels, TX
study_region ="AT"
x_var_candidate_hh= ['HOUSEID',
                     'HH_HISP', 
                     'HOMEOWN',
                     'HBPPOPDN',
                     'HHFAMINC',
                     'HHSIZE',
                     'HHVEHCNT',
                     'HH_RACE',
                     'WEBUSE17',
                     'LIF_CYC',
                     'WRKCOUNT',
                     'HH_CBSA']
x_var_candidate_per= ['HOUSEID', 
                    'DELIVER',
                    'EDUC',
                    'HHFAMINC', 
                    'HHSIZE', 
                    'HHVEHCNT', 
                    'HBPPOPDN', 
                    'R_AGE_IMP',  
                    'R_SEX_IMP', 
                    'R_HISP', 
                    'R_RACE', 
                    'SCHTYP',
                    'WORKER',
                    'WRKTRANS',
                    'WRK_HOME',
                    'HH_CBSA']

selected_x_var_web=[
"HHSIZE",
#"HHVEHCNT",
#"income_est",
"WRKCOUNT",
#"HH_RACE_0",
"HH_RACE_1",
"HH_RACE_2",
"HH_RACE_3",
"income_cls_0",
"income_cls_1",
"income_cls_2"#,
#"income_cls_3"
]

selected_x_var_online=[
#"HHSIZE",
"HHVEHCNT",
#"income_est",
#"HH_RACE_0",
#"HH_RACE_1",
#"HH_RACE_2",
#"HH_RACE_3",
"income_cls_0",
"income_cls_1",
"income_cls_2",
#"income_cls_3",
"R_AGE_IMP_0",
#"R_AGE_IMP_1",
#"R_AGE_IMP_2",
"R_AGE_IMP_3",
#"EDUC_0",
#"EDUC_1",
"EDUC_2",
"EDUC_3",
#"R_RACE_0",
"R_RACE_1",
#"R_RACE_2",
"R_RACE_3",
"R_SEX_IMP",
#"SCHTYP",
"WRK_HOME",
"WORKER",
#"WEBUSE17_0",
"WEBUSE17_1",
"WEBUSE17_2"
]                    

selected_x_var_delivery=[
"HHSIZE",
"HHVEHCNT",
#"income_est",
#"HH_RACE_0",
#"HH_RACE_1",
#"HH_RACE_2",
#"HH_RACE_3",
"income_cls_0",
"income_cls_1",
"income_cls_2",
#"income_cls_3",
"R_AGE_IMP_0",
"R_AGE_IMP_1",
"R_AGE_IMP_2",
#"R_AGE_IMP_3",
#"EDUC_0",
#"EDUC_1",
#"EDUC_2",
"EDUC_3",
#"R_RACE_0",
#"R_RACE_1",
#"R_RACE_2",
#"R_RACE_3",
"R_SEX_IMP",
#"SCHTYP",
#"WRK_HOME",
"WORKER",
#"WEBUSE17_0",
#"WEBUSE17_1"#,
#"WEBUSE17_2"    
]

# input for B2C
b2c_delivery_frequency=30
hh_aggregation_size=15


# input for B2B/Geo_data
firm_file= 'synthfirms_all_Sep.csv'
warehouse_file= 'warehouses_all_Sep.csv'
dist_file= 'od_distance.csv'
CBG_file= 'sfbay_freight.geojson'
##ship_direction = 'out' # ['out','in', 'all']
commodity_list= ["1", "2", "3", "4", "5"]
county_list=[1, 13, 41, 55, 75, 81, 85, 95, 97] ## this should be updated 
list_error_zone=[1047.0, 1959.0, 1979.0, 2824.0, 3801.0, 3897.0, 4303.0, 6252.0, 6810.0, 7273.0, 8857.0, 9702.0] # this should be updated
weight_theshold=40000

# output data structure
fnm_B2C_payload="B2C_payload"
fnm_B2C_carrier="B2C_carrier"
fnm_B2B_payload="B2B_payload"
fnm_B2B_carrier="B2B_carrier"
fnm_vtype="vehicle_types.csv"
fdir_main_output= "../../../FRISM_input_output_{}/Sim_outputs/Shipment2Fleet/".format(study_region)

#ship_direction = 'out' # ['out','in', 'all']
commodity_list= ["1", "2", "3", "4", "5"]
county_list=[1, 13, 41, 55, 75, 81, 85, 95, 97]
list_error_zone=[1047.0, 1959.0, 1979.0, 2824.0, 3801.0, 3897.0, 4303.0, 6252.0, 6810.0, 7273.0, 8857.0, 9702.0]
weight_theshold=40000

"""
# HH sf_2010 variables vs 2018 data

household_id      int64     household_id                 int64
serialno        float64     serialno                     int64
persons           int64     persons                      int64
cars              int64     cars                         int64
income            int64     hh_income                   object income                     float64
race_of_head      int64     hh_race_of_head             object race_of_head                 int64 
age_of_head       int64     hh_age_of_head              object  age_of_head                  int64
workers           int64     hh_workers                  object  workers                    float64
*children          int64     hh_children                 object
tenure            int64     tenure                       int64
recent_mover      int64     recent_mover                 int64
block_id          int64     block_id                     int64

# PER sf_2010 variables vs 2018 data

person_id       int64
age             int64       age                 int64   person_age         object
earning         int64       earning           float64
edu             int64       edu               float64
hours           int64       hours             float64
household_id    int64       household_id        int64
member_id       int64       member_id           int64
race_id         int64       race_id             int64   race               object
relate          int64       relate              int64
sex             int64       sex                 int64   person_sex         object
student         int64       student             int64
work_at_home    int64       work_at_home        int64
worker          int64       worker          int64       

"""
