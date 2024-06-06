import pandas as pd
import importlib
import pytest
import geopandas as gp
import time
import sys
import pickle
from unittest import TestCase
from shapely.geometry import Point

sys.path.append('../src/Simulation')

vrp = importlib.import_module("VRP_OR-tools_Stops_veh_tech")

def test_tt_cal_normal():
    """ Testing normal case where the origin and destination exist in the origin-destination travel time dataframe
    """
    sel_tt = pd.DataFrame()
    sel_tt['origin'] = [1000, 1000,1001,1001]
    sel_tt['destination'] = [1000,1001,1000,1001]
    sel_tt['TIME_minutes'] = [0,5,10,0]

    sel_dist = pd.DataFrame()
    sel_dist['Origin'] = [10, 10,12,12]
    sel_dist['Destination'] = [10,12,10,12]
    sel_dist['dist'] = [0,500,1000,0]

    assert vrp.tt_cal(10, 10, 1000, 1001, sel_tt, sel_dist) == 5, "incorrect travel time"


def test_tt_cal_dist():
    """ Testing case where the origin and destination are not in the travel time dataframe but in the orgin-destination distance dataframe
    """
    sel_tt = pd.DataFrame()
    sel_tt['origin'] = [1000, 1000,1001,1001]
    sel_tt['destination'] = [1000,1001,1000,1001]
    sel_tt['TIME_minutes'] = [0,5,10,0]

    sel_dist = pd.DataFrame()
    sel_dist['Origin'] = [10, 10,12,12]
    sel_dist['Destination'] = [10,12,10,12]
    sel_dist['dist'] = [0,500,1000,0]

    assert vrp.tt_cal(10, 12, 1005, 1012, sel_tt, sel_dist) == 750, "incorrect travel time"


def test_tt_cal_exception():
    """Testing case where the origin and destination are not in the travel time dataframe and are not in the orgin-destination distance dataframe
    """
    sel_tt = pd.DataFrame()
    sel_tt['origin'] = [1000, 1000,1001,1001]
    sel_tt['destination'] = [1000,1001,1000,1001]
    sel_tt['TIME_minutes'] = [0,5,10,0]

    sel_dist = pd.DataFrame()
    sel_dist['Origin'] = [10, 10,12,12]
    sel_dist['Destination'] = [10,12,10,12]
    sel_dist['dist'] = [0,500,1000,0]

    assert vrp.tt_cal(13, 15, 1005, 1012, sel_tt, sel_dist) == 180, "incorrect travel time"


def test_get_geoId_normal():
    """ Testing getting geo id (census block Id) from geo Id files, case where the geo id exist in the file
    """
    pd_df = pd.DataFrame()
    pd_df['GEOID'] = [456, 457]
    pd_df['CBPZONE'] = [1234, 1235]
    pd_df['MESOZONE'] = [101,1001]
    pd_df['geometry'] = [Point(-101.91, 33.55), Point(-98.53, 29.53)]

    gp_df = gp.GeoDataFrame(pd_df, geometry='geometry')

    assert vrp.get_geoId(101,gp_df) == 456, "incorrect geo Id"


def test_get_geoId_exception():
    """ Testing getting geo id (census block Id) from geo Id files, case where the geo id does not exist in the file
        This case returns -1
    """
    pd_df = pd.DataFrame()
    pd_df['GEOID'] = [456, 457]
    pd_df['CBPZONE'] = [1234, 1235]
    pd_df['MESOZONE'] = [101,1001]
    pd_df['geometry'] = [Point(-101.91, 33.55), Point(-98.53, 29.53)]

    gp_df = gp.GeoDataFrame(pd_df, geometry='geometry')

    assert vrp.get_geoId(2003,gp_df) == -1, "incorrect geo Id"


def test_create_data_model_delivery_external_normal():
    """Testing creating the problem data dictionary for a delivery problem with external destinations
        This is is similar to testing the pickup problem with external origins
    """
    df_prob = pd.read_csv('test_data/df_prob_delivery.csv')
    c_prob = pd.read_csv('test_data/c_prob_delivery.csv')
    v_df = pd.read_csv('test_data/v_df_delivery.csv')
    vc_prob = pd.read_csv('test_data/vc_prob_delivery.csv')
    CBGzone_df = pd.read_csv('test_data/CBGzone_df.csv')
    tt_df = pd.read_csv('test_data/sel_tt_delivery.csv')
    dist_df = pd.read_csv('test_data/sel_dist_delivery.csv')
    prob_type = 'delivery'
    carr_id = 'B2C_2879885.0'
    depot_loc = c_prob.loc[c_prob['carrier_id'] == carr_id]['depot_zone'].values[0]
    veh = 'md_D_Diesel'
    comm = 5
    index = 'external'
    path_stops = ''  # We do not info on stop distribution for external tours

    data = {}
    with open('test_data/b2c_delivery_external.pickle', 'rb') as handle:
        data = pickle.load(handle)

    ret_data = vrp.create_data_model(df_prob, depot_loc, prob_type, v_df, vc_prob, c_prob, carr_id,
                                                CBGzone_df, tt_df, dist_df, veh, comm, index, path_stops)

    TestCase().assertDictEqual(ret_data, data, "incorrect data dictionary created")


def test_create_data_model_pickup_delivery_external_normal():
    """Testing creating the problem data dictionary for a pickup-delivery problem with external locations
    """
    df_prob = pd.read_csv('test_data/df_prob_pickup_delivery.csv')
    c_prob = pd.read_csv('test_data/c_prob_pickup_delivery.csv')
    v_df = pd.read_csv('test_data/v_df_pickup_delivery.csv')
    vc_prob = pd.read_csv('test_data/vc_prob_pickup_delivery.csv')
    CBGzone_df = pd.read_csv('test_data/CBGzone_df.csv')
    tt_df = pd.read_csv('test_data/sel_tt_pickup_delivery.csv')
    dist_df = pd.read_csv('test_data/sel_dist_pickup_delivery.csv')
    prob_type = 'pickup_delivery'
    carr_id = 'B2B_2627740_0hdt_D'
    depot_loc = c_prob.loc[c_prob['carrier_id'] == carr_id]['depot_zone'].values[0]
    veh = 'hdt_D_Diesel'
    comm = 2
    index = 'external'
    path_stops = ''  # We do not info on stop distribution for external tours

    data = {}
    with open('test_data/b2b_pickup_delivery_external.pickle', 'rb') as handle:
        data = pickle.load(handle)

    ret_data = vrp.create_data_model(df_prob, depot_loc, prob_type, v_df, vc_prob, c_prob, carr_id,
                                                CBGzone_df, tt_df, dist_df, veh, comm, index, path_stops)

    TestCase().assertDictEqual(ret_data, data, "incorrect data dictionary created")



def test_create_data_model_delivery_internal_normal():
    """Testing creating the problem data dictionary for a delivery problem with internal destinations
        This is is similar to testing the pickup problem with internal origins
    """
    df_prob = pd.read_csv('test_data/df_prob_delivery.csv')
    c_prob = pd.read_csv('test_data/c_prob_delivery.csv')
    v_df = pd.read_csv('test_data/v_df_delivery.csv')
    vc_prob = pd.read_csv('test_data/vc_prob_delivery.csv')
    CBGzone_df = pd.read_csv('test_data/CBGzone_df.csv')
    tt_df = pd.read_csv('test_data/sel_tt_delivery.csv')
    dist_df = pd.read_csv('test_data/sel_dist_delivery.csv')
    prob_type = 'delivery'
    carr_id = 'B2C_2879885.0'
    depot_loc = c_prob.loc[c_prob['carrier_id'] == carr_id]['depot_zone'].values[0]
    veh = 'md_D_Diesel'
    comm = 5
    index = 'internal'
    path_stops = '../../FRISM_input_output_AT/Survey_Data/'  # We do not info on stop distribution for external tours

    data = {}
    with open('test_data/b2c_delivery_internal.pickle', 'rb') as handle:
        data = pickle.load(handle)

    ret_data = vrp.create_data_model(df_prob, depot_loc, prob_type, v_df, vc_prob, c_prob, carr_id,
                                                CBGzone_df, tt_df, dist_df, veh, comm, index, path_stops)

    TestCase().assertDictEqual(ret_data, data, "incorrect data dictionary created")



def test_create_data_model_pickup_delivery_internal_normal():
    """Testing creating the problem data dictionary for a pickup-delivery problem with internal destinations
    """
    df_prob = pd.read_csv('test_data/df_prob_pickup_delivery.csv')
    c_prob = pd.read_csv('test_data/c_prob_pickup_delivery.csv')
    v_df = pd.read_csv('test_data/v_df_pickup_delivery.csv')
    vc_prob = pd.read_csv('test_data/vc_prob_pickup_delivery.csv')
    CBGzone_df = pd.read_csv('test_data/CBGzone_df.csv')
    tt_df = pd.read_csv('test_data/sel_tt_pickup_delivery.csv')
    dist_df = pd.read_csv('test_data/sel_dist_pickup_delivery.csv')
    prob_type = 'pickup_delivery'
    carr_id = 'B2B_2627740_0hdt_D'
    depot_loc = c_prob.loc[c_prob['carrier_id'] == carr_id]['depot_zone'].values[0]
    veh = 'hdt_D_Diesel'
    comm = 5
    index = 'internal'
    path_stops = '../../FRISM_input_output_AT/Survey_Data/'  # We do not info on stop distribution for external tours

    data = {}
    with open('test_data/b2b_pickup_delivery_internal.pickle', 'rb') as handle:
        data = pickle.load(handle)

    ret_data = vrp.create_data_model(df_prob, depot_loc, prob_type, v_df, vc_prob, c_prob, carr_id,
                                                CBGzone_df, tt_df, dist_df, veh, comm, index, path_stops)

    TestCase().assertDictEqual(ret_data, data, "incorrect data dictionary created")



def test_input_files_processing_delivery_normal():
    """ Testing the input_files_processing function for normal, no exception functionality
    """
    travel_file = 'test_data/sel_tt_delivery.csv.gz'
    dist_file = 'test_data/sel_dist_delivery.csv'
    CBGzone_file = 'test_data/CBGzone_df.geojson'
    carrier_file = 'test_data/c_prob_delivery.csv'
    payload_file = 'test_data/df_prob_delivery.csv'
    vehicleType_file = 'test_data/v_df_delivery.csv'

    p_df = pd.read_csv(payload_file)
    c_df = pd.read_csv(carrier_file)
    v_df = pd.read_csv(vehicleType_file)
    vc_df = pd.read_csv('test_data/vc_df_processing_delivery.csv')
    CBGzone_df = gp.read_file(CBGzone_file)
    tt_df = pd.read_csv(travel_file, compression='gzip', header=0, sep=',', quotechar='"', error_bad_lines=False)
    dist_df = pd.read_csv(dist_file)

    ret_tt_df, ret_dist_df, ret_CBGzone_df, ret_c_df, ret_p_df, ret_v_df, ret_vc_df = vrp.input_files_processing(travel_file, dist_file,
                                                                                                                 CBGzone_file, carrier_file, payload_file, vehicleType_file)

    assert ret_tt_df.equals(tt_df), "incorrect travel time dataframe"
    assert ret_dist_df.equals(dist_df), "incorrect distance dataframe"
    assert ret_CBGzone_df.equals(CBGzone_df), "incorrect census block id file"
    assert ret_c_df.equals(c_df), "incorrect carrier dataframe"
    assert ret_p_df.equals(p_df), "incorrect payload dataframe"
    assert ret_v_df.equals(v_df), "incorrect vehicle dataframe"
    assert ret_vc_df.equals(vc_df), "incorrect vehicle details dataframe"


def test_input_files_processing_exception():
    """ Testing the input_files_processing function for exception cases, where one of the input files can't be read.
    """
    travel_file = 'test_data/sel_tt_delivery.csv'
    dist_file = 'test_data/sel_dist_delivery.csv'
    CBGzone_file = 'test_data/CBGzone_df.geojson'
    carrier_file = 'test_data/c_prob_delivery.csv'
    payload_file = 'test_data/df_prob_delivery.csv'
    vehicleType_file = 'test_data/v_df_delivery.csv'

    # Checking if we capture exception from travel_file
    assert vrp.input_files_processing(travel_file, dist_file, CBGzone_file,
                                       carrier_file, payload_file, vehicleType_file) == None, 'Missed exception on reading travel time input file format'
    #Checking if we capture exception from dist_file
    travel_file = 'test_data/sel_tt_delivery.csv.gz'
    dist_file = 'test_data/sel_dist_delivery.txt'
    assert vrp.input_files_processing(travel_file, dist_file, CBGzone_file,
                                       carrier_file, payload_file, vehicleType_file) == None, 'Missed exception on reading distance input file format'
    #Checking if we capture exception from geoid file
    dist_file = 'test_data/sel_dist_delivery.csv'
    CBGzone_file = 'test_data/CBGzone_df.csv'
    assert vrp.input_files_processing(travel_file, dist_file, CBGzone_file,
                                       carrier_file, payload_file, vehicleType_file) == None, 'Missed exception on reading geo id input file format'
    # Checking if we capture exception from carrier file
    CBGzone_file = 'test_data/CBGzone_df.geojson'
    carrier_file = 'src/test_data/c_prob_delivery.csv'
    assert vrp.input_files_processing(travel_file, dist_file, CBGzone_file,
                                       carrier_file, payload_file, vehicleType_file) == None, 'Missed exception on reading carrier input file format'

    # Checking if we capture exception from payload file
    carrier_file = 'test_data/c_prob_delivery.csv'
    payload_file = 'test_data/df_prob_delivery.txt'
    assert vrp.input_files_processing(travel_file, dist_file, CBGzone_file,
                                       carrier_file, payload_file, vehicleType_file) == None, 'Missed exception on reading payload input file format'

    # Checking if we capture exception from payload file
    payload_file = 'test_data/df_prob_delivery.csv'
    vehicleType_file = 'test_data/v_df_delivery.txt'
    assert vrp.input_files_processing(travel_file, dist_file, CBGzone_file,
                                       carrier_file, payload_file, vehicleType_file) == None, 'Missed exception on reading vehicle input file format'


def test_form_solve_vpr_delivery_internal_normal():
    """Testing creating the problem data dictionary and solving a delivery problem with internal destinations
        This is is similar to testing the pickup problem with internal origins
    """

    tour_df = pd.DataFrame(columns = ['tour_id', 'departureTimeInSec', 'departureLocation_zone', 'maxTourDurationInSec',
                                        'departureLocation_x','departureLocation_y'])
    # Format for carrier data frame: carrierId,tourId, vehicleId,vehicleTypeId,depot_zone
    carrier_df = pd.DataFrame(columns = ['carrierId','tourId', 'vehicleId', 'vehicleTypeId','depot_zone', 'depot_zone_x', 'depot_zone_y'])
    # format for payload format
    # payloadId, sequenceRank, tourId, payloadType, weightInlb, requestType,locationZone,
    # estimatedTimeOfArrivalInSec, arrivalTimeWindowInSec_lower, arrivalTimeWindowInSec_upper,operationDurationInSec
    payload_df = pd.DataFrame(columns = ['payloadId','sequenceRank','tourId','payloadType','weightInlb','cummulativeWeightInlb',
                                        'requestType','locationZone','estimatedTimeOfArrivalInSec','arrivalTimeWindowInSec_lower',
                                        'arrivalTimeWindowInSec_upper','operationDurationInSec', 'locationZone_x', 'locationZone_y'])

    df_prob = pd.read_csv('test_data/df_prob_delivery.csv')
    c_prob = pd.read_csv('test_data/c_prob_delivery.csv')
    v_df = pd.read_csv('test_data/v_df_delivery.csv')
    vc_prob = pd.read_csv('test_data/vc_prob_delivery.csv')
    CBGzone_df = pd.read_csv('test_data/CBGzone_df.csv')
    tt_df = pd.read_csv('test_data/sel_tt_delivery.csv')
    dist_df = pd.read_csv('test_data/sel_dist_delivery.csv')
    prob_type = 'delivery'
    carr_id = 'B2C_2879885.0'
    depot_loc = c_prob.loc[c_prob['carrier_id'] == carr_id]['depot_zone'].values[0]
    veh = 'md_D_Diesel'
    ship_type = 'B2C'
    max_time = 900
    comm = 5
    count_num = 21
    s_used_veh = [11]
    index = 'internal'
    path_stops = '../../FRISM_input_output_AT/Survey_Data/'  # We do not info on stop distribution for external tours
    tour_id = payload_i = depot_i = 0

    data = vrp.create_data_model(df_prob, depot_loc, prob_type, v_df, vc_prob, c_prob, carr_id,
                                                CBGzone_df, tt_df, dist_df, veh, comm, index, path_stops)

    used_veh = vrp.form_solve(data, tour_df, carr_id, carrier_df, payload_df, prob_type, count_num,
                          ship_type, c_prob, df_prob, max_time, index, comm, tour_id, payload_i, depot_i)


    # Reading in saved solution dataframes for tour, paylaod and carrier
    sv_tour_df = pd.read_csv('test_data/tour_df_delivery_internal.csv')
    sv_payload_df = pd.read_csv('test_data/payload_df_delivery_internal.csv')
    sv_carrier_df = pd.read_csv('test_data/carrier_df_delivery_internal.csv')

    # Make sure all columns have same data types
    for c in list(tour_df.columns):
        tour_df[c] = tour_df[c].astype(sv_tour_df[c].dtypes)

    for c in list(payload_df.columns):
        payload_df[c] = payload_df[c].astype(sv_payload_df[c].dtypes)

    for c in list(carrier_df.columns):
        carrier_df[c] = carrier_df[c].astype(sv_carrier_df[c].dtypes)

    assert s_used_veh == used_veh, "incorrect list of used vehicles"
    assert sv_tour_df.equals(tour_df), "incorrect solution in tour df"
    # Neglectt last comments to bypass high resolutions issues with x and y coordinates
    assert sv_payload_df.iloc[:, :-2].equals(payload_df.iloc[:, :-2]), "incorrect solution in payload df"
    assert sv_carrier_df.equals(carrier_df), "incorrect solution in carrier df"


def test_form_solve_vpr_delivery_external_normal():
    """Testing creating the problem data dictionary and solving a delivery problem with internal destinations
        This is is similar to testing the pickup problem with internal origins
    """

    tour_df = pd.DataFrame(columns = ['tour_id', 'departureTimeInSec', 'departureLocation_zone', 'maxTourDurationInSec',
                                        'departureLocation_x','departureLocation_y'])
    # Format for carrier data frame: carrierId,tourId, vehicleId,vehicleTypeId,depot_zone
    carrier_df = pd.DataFrame(columns = ['carrierId','tourId', 'vehicleId', 'vehicleTypeId','depot_zone', 'depot_zone_x', 'depot_zone_y'])
    # format for payload format
    # payloadId, sequenceRank, tourId, payloadType, weightInlb, requestType,locationZone,
    # estimatedTimeOfArrivalInSec, arrivalTimeWindowInSec_lower, arrivalTimeWindowInSec_upper,operationDurationInSec
    payload_df = pd.DataFrame(columns = ['payloadId','sequenceRank','tourId','payloadType','weightInlb','cummulativeWeightInlb',
                                        'requestType','locationZone','estimatedTimeOfArrivalInSec','arrivalTimeWindowInSec_lower',
                                        'arrivalTimeWindowInSec_upper','operationDurationInSec', 'locationZone_x', 'locationZone_y'])

    df_prob = pd.read_csv('test_data/df_prob_delivery.csv')
    c_prob = pd.read_csv('test_data/c_prob_delivery.csv')
    v_df = pd.read_csv('test_data/v_df_delivery.csv')
    vc_prob = pd.read_csv('test_data/vc_prob_delivery.csv')
    CBGzone_df = pd.read_csv('test_data/CBGzone_df.csv')
    tt_df = pd.read_csv('test_data/sel_tt_delivery.csv')
    dist_df = pd.read_csv('test_data/sel_dist_delivery.csv')
    prob_type = 'delivery'
    carr_id = 'B2C_2879885.0'
    depot_loc = c_prob.loc[c_prob['carrier_id'] == carr_id]['depot_zone'].values[0]
    veh = 'md_D_Diesel'
    ship_type = 'B2C'
    max_time = 900
    comm = 5
    count_num = 21
    r_used_veh = [11]
    index = 'external'
    path_stops = '../../FRISM_input_output_AT/Survey_Data/'  # We do not info on stop distribution for external tours
    tour_id = payload_i = depot_i = 0

    data = vrp.create_data_model(df_prob, depot_loc, prob_type, v_df, vc_prob, c_prob, carr_id,
                                                CBGzone_df, tt_df, dist_df, veh, comm, index, path_stops)

    used_veh = vrp.form_solve(data, tour_df, carr_id, carrier_df, payload_df, prob_type, count_num,
                          ship_type, c_prob, df_prob, max_time, index, comm, tour_id, payload_i, depot_i)

    # Reading in saved solution dataframes for tour, paylaod and carrier
    sv_tour_df = pd.read_csv('test_data/tour_df_delivery_external.csv')
    sv_payload_df = pd.read_csv('test_data/payload_df_delivery_external.csv')
    sv_carrier_df = pd.read_csv('test_data/carrier_df_delivery_external.csv')

    # Make sure all columns have same data types
    for c in list(tour_df.columns):
        tour_df[c] = tour_df[c].astype(sv_tour_df[c].dtypes)

    for c in list(payload_df.columns):
        payload_df[c] = payload_df[c].astype(sv_payload_df[c].dtypes)

    for c in list(carrier_df.columns):
        carrier_df[c] = carrier_df[c].astype(sv_carrier_df[c].dtypes)

    assert r_used_veh == used_veh, "incorrect list of used vehicles"
    assert sv_tour_df.equals(tour_df), "incorrect solution in tour df"
    # Neglectt last comments to bypass high resolutions issues with x and y coordinates
    assert sv_payload_df.iloc[:, :-2].equals(payload_df.iloc[:, :-2]), "incorrect solution in payload df"
    assert sv_carrier_df.equals(carrier_df), "incorrect solution in carrier df"


def test_form_solve_vpr_pickup_delivery_external_normal():
    """Testing creating the problem data dictionary and solving a pickup-delivery problem with external locations
    """
    tour_df = pd.DataFrame(columns = ['tour_id', 'departureTimeInSec', 'departureLocation_zone', 'maxTourDurationInSec',
                                        'departureLocation_x','departureLocation_y'])
    # Format for carrier data frame: carrierId,tourId, vehicleId,vehicleTypeId,depot_zone
    carrier_df = pd.DataFrame(columns = ['carrierId','tourId', 'vehicleId', 'vehicleTypeId','depot_zone', 'depot_zone_x', 'depot_zone_y'])
    # format for payload format
    # payloadId, sequenceRank, tourId, payloadType, weightInlb, requestType,locationZone,
    # estimatedTimeOfArrivalInSec, arrivalTimeWindowInSec_lower, arrivalTimeWindowInSec_upper,operationDurationInSec
    payload_df = pd.DataFrame(columns = ['payloadId','sequenceRank','tourId','payloadType','weightInlb','cummulativeWeightInlb',
                                        'requestType','locationZone','estimatedTimeOfArrivalInSec','arrivalTimeWindowInSec_lower',
                                        'arrivalTimeWindowInSec_upper','operationDurationInSec', 'locationZone_x', 'locationZone_y'])

    df_prob = pd.read_csv('test_data/df_prob_pickup_delivery.csv')
    c_prob = pd.read_csv('test_data/c_prob_pickup_delivery.csv')
    v_df = pd.read_csv('test_data/v_df_pickup_delivery.csv')
    vc_prob = pd.read_csv('test_data/vc_prob_pickup_delivery.csv')
    CBGzone_df = pd.read_csv('test_data/CBGzone_df.csv')
    tt_df = pd.read_csv('test_data/sel_tt_pickup_delivery.csv')
    dist_df = pd.read_csv('test_data/sel_dist_pickup_delivery.csv')
    prob_type = 'pickup_delivery'
    carr_id = 'B2B_2627740_0hdt_D'
    depot_loc = c_prob.loc[c_prob['carrier_id'] == carr_id]['depot_zone'].values[0]
    veh = 'hdt_D_Diesel'
    ship_type = 'B2B'
    max_time = 900
    comm = 2
    count_num = 21
    index = 'external'
    path_stops = ''  # We do not info on stop distribution for external tours
    r_used_veh = [6]
    tour_id = payload_i = depot_i = 0

    data = vrp.create_data_model(df_prob, depot_loc, prob_type, v_df, vc_prob, c_prob, carr_id,
                                                CBGzone_df, tt_df, dist_df, veh, comm, index, path_stops)

    used_veh = vrp.form_solve(data, tour_df, carr_id, carrier_df, payload_df, prob_type, count_num,
                          ship_type, c_prob, df_prob, max_time, index, comm, tour_id, payload_i, depot_i)

    # Reading in saved solution dataframes for tour, paylaod and carrier
    sv_tour_df = pd.read_csv('test_data/tour_df_pickup_delivery_external.csv')
    sv_payload_df = pd.read_csv('test_data/payload_df_pickup_delivery_external.csv')
    sv_carrier_df = pd.read_csv('test_data/carrier_df_pickup_delivery_external.csv')

    # Make sure all columns have same data types
    for c in list(tour_df.columns):
        tour_df[c] = tour_df[c].astype(sv_tour_df[c].dtypes)

    for c in list(payload_df.columns):
        payload_df[c] = payload_df[c].astype(sv_payload_df[c].dtypes)

    for c in list(carrier_df.columns):
        carrier_df[c] = carrier_df[c].astype(sv_carrier_df[c].dtypes)

    assert r_used_veh == used_veh, "incorrect list of used vehicles"
    assert sv_tour_df.equals(tour_df), "incorrect solution in tour df"
    # Neglectt last comments to bypass high resolutions issues with x and y coordinates
    assert sv_payload_df.iloc[:, :-2].equals(payload_df.iloc[:, :-2]), "incorrect solution in payload df"
    assert sv_carrier_df.equals(carrier_df), "incorrect solution in carrier df"


def test_form_solve_vrp_pickup_delivery_internal_normal():
    """Testing creating the problem data dictionary for a pickup-delivery problem with internal destinations
    """
    tour_df = pd.DataFrame(columns = ['tour_id', 'departureTimeInSec', 'departureLocation_zone', 'maxTourDurationInSec',
                                        'departureLocation_x','departureLocation_y'])
    # Format for carrier data frame: carrierId,tourId, vehicleId,vehicleTypeId,depot_zone
    carrier_df = pd.DataFrame(columns = ['carrierId','tourId', 'vehicleId', 'vehicleTypeId','depot_zone', 'depot_zone_x', 'depot_zone_y'])
    # format for payload format
    # payloadId, sequenceRank, tourId, payloadType, weightInlb, requestType,locationZone,
    # estimatedTimeOfArrivalInSec, arrivalTimeWindowInSec_lower, arrivalTimeWindowInSec_upper,operationDurationInSec
    payload_df = pd.DataFrame(columns = ['payloadId','sequenceRank','tourId','payloadType','weightInlb','cummulativeWeightInlb',
                                        'requestType','locationZone','estimatedTimeOfArrivalInSec','arrivalTimeWindowInSec_lower',
                                        'arrivalTimeWindowInSec_upper','operationDurationInSec', 'locationZone_x', 'locationZone_y'])

    df_prob = pd.read_csv('test_data/df_prob_pickup_delivery.csv')
    c_prob = pd.read_csv('test_data/c_prob_pickup_delivery.csv')
    v_df = pd.read_csv('test_data/v_df_pickup_delivery.csv')
    vc_prob = pd.read_csv('test_data/vc_prob_pickup_delivery.csv')
    CBGzone_df = pd.read_csv('test_data/CBGzone_df.csv')
    tt_df = pd.read_csv('test_data/sel_tt_pickup_delivery.csv')
    dist_df = pd.read_csv('test_data/sel_dist_pickup_delivery.csv')
    prob_type = 'pickup_delivery'
    carr_id = 'B2B_2627740_0hdt_D'
    depot_loc = c_prob.loc[c_prob['carrier_id'] == carr_id]['depot_zone'].values[0]
    veh = 'hdt_D_Diesel'
    comm = 5
    index = 'internal'
    path_stops = '../../FRISM_input_output_AT/Survey_Data/'  # We do not info on stop distribution for external tours
    ship_type = 'B2B'
    count_num = 21
    r_used_veh = [6, 7]
    max_time = 900
    tour_id = payload_i = depot_i = 0

    data = vrp.create_data_model(df_prob, depot_loc, prob_type, v_df, vc_prob, c_prob, carr_id,
                                                CBGzone_df, tt_df, dist_df, veh, comm, index, path_stops)

    used_veh = vrp.form_solve(data, tour_df, carr_id, carrier_df, payload_df, prob_type, count_num,
                          ship_type, c_prob, df_prob, max_time, index, comm, tour_id, payload_i, depot_i)

    # Reading in saved solution dataframes for tour, paylaod and carrier
    sv_tour_df = pd.read_csv('test_data/tour_df_pickup_delivery_internal.csv')
    sv_payload_df = pd.read_csv('test_data/payload_df_pickup_delivery_internal.csv')
    sv_carrier_df = pd.read_csv('test_data/carrier_df_pickup_delivery_internal.csv')

    # Make sure all columns have same data types
    for c in list(tour_df.columns):
        tour_df[c] = tour_df[c].astype(sv_tour_df[c].dtypes)

    for c in list(payload_df.columns):
        payload_df[c] = payload_df[c].astype(sv_payload_df[c].dtypes)

    for c in list(carrier_df.columns):
        carrier_df[c] = carrier_df[c].astype(sv_carrier_df[c].dtypes)

    assert r_used_veh == used_veh, "incorrect list of used vehicles"
    assert sv_tour_df.equals(tour_df), "incorrect solution in tour df"
    assert sv_payload_df.iloc[:, :-2].equals(payload_df.iloc[:, :-2]), "incorrect solution in payload df"
    assert sv_carrier_df.equals(carrier_df), "incorrect solution in carrier df"


def test_form_solve_vpr_delivery_external_exception():
    """Testing creating the problem data dictionary and solving a delivery problem with internal destinations
        This is is similar to testing the pickup problem with internal origins
    """

    tour_df = pd.DataFrame(columns = ['tour_id', 'departureTimeInSec', 'departureLocation_zone', 'maxTourDurationInSec',
                                        'departureLocation_x','departureLocation_y'])
    # Format for carrier data frame: carrierId,tourId, vehicleId,vehicleTypeId,depot_zone
    carrier_df = pd.DataFrame(columns = ['carrierId','tourId', 'vehicleId', 'vehicleTypeId','depot_zone', 'depot_zone_x', 'depot_zone_y'])
    # format for payload format
    # payloadId, sequenceRank, tourId, payloadType, weightInlb, requestType,locationZone,
    # estimatedTimeOfArrivalInSec, arrivalTimeWindowInSec_lower, arrivalTimeWindowInSec_upper,operationDurationInSec
    payload_df = pd.DataFrame(columns = ['payloadId','sequenceRank','tourId','payloadType','weightInlb','cummulativeWeightInlb',
                                        'requestType','locationZone','estimatedTimeOfArrivalInSec','arrivalTimeWindowInSec_lower',
                                        'arrivalTimeWindowInSec_upper','operationDurationInSec', 'locationZone_x', 'locationZone_y'])

    df_prob = pd.read_csv('test_data/df_prob_delivery_time_window_exception.csv')
    c_prob = pd.read_csv('test_data/c_prob_delivery.csv')
    v_df = pd.read_csv('test_data/v_df_delivery.csv')
    vc_prob = pd.read_csv('test_data/vc_prob_delivery.csv')
    CBGzone_df = pd.read_csv('test_data/CBGzone_df.csv')
    tt_df = pd.read_csv('test_data/sel_tt_delivery.csv')
    dist_df = pd.read_csv('test_data/sel_dist_delivery.csv')
    prob_type = 'delivery'
    carr_id = 'B2C_2879885.0'
    depot_loc = c_prob.loc[c_prob['carrier_id'] == carr_id]['depot_zone'].values[0]
    veh = 'md_D_Diesel'
    ship_type = 'B2C'
    max_time = 900
    comm = 5
    count_num = 21
    r_used_veh = [11]
    index = 'internal'
    path_stops = '../../FRISM_input_output_AT/Survey_Data/'  # We do not info on stop distribution for external tours
    tour_id = payload_i = depot_i = 0

    # time window lowebound = time window upper bound, no way to meet time window constraints
    data = vrp.create_data_model(df_prob, depot_loc, prob_type, v_df, vc_prob, c_prob, carr_id,
                                                CBGzone_df, tt_df, dist_df, veh, comm, index, path_stops)

    used_veh = vrp.form_solve(data, tour_df, carr_id, carrier_df, payload_df, prob_type, count_num,
                              ship_type, c_prob, df_prob, max_time, index, comm, tour_id, payload_i, depot_i)

    assert [] == used_veh, "incorrect list of used vehicles"
    assert pd.DataFrame(columns = ['tour_id', 'departureTimeInSec', 'departureLocation_zone', 'maxTourDurationInSec',
                                        'departureLocation_x','departureLocation_y']).equals(tour_df), "incorrect solution in tour df"
    assert pd.DataFrame(columns = ['payloadId','sequenceRank','tourId','payloadType','weightInlb','cummulativeWeightInlb',
                                        'requestType','locationZone','estimatedTimeOfArrivalInSec','arrivalTimeWindowInSec_lower',
                                        'arrivalTimeWindowInSec_upper','operationDurationInSec', 'locationZone_x', 'locationZone_y']).equals(payload_df), "incorrect solution in payload df"
    assert pd.DataFrame(columns = ['carrierId','tourId', 'vehicleId', 'vehicleTypeId','depot_zone', 'depot_zone_x', 'depot_zone_y']).equals(carrier_df), "incorrect solution in carrier df"

    # Payloads are too large to be carried by vehicles
    df_prob = pd.read_csv('test_data/df_prob_delivery_exception.csv')
    data = vrp.create_data_model(df_prob, depot_loc, prob_type, v_df, vc_prob, c_prob, carr_id,
                                                CBGzone_df, tt_df, dist_df, veh, comm, index, path_stops)

    used_veh = vrp.form_solve(data, tour_df, carr_id, carrier_df, payload_df, prob_type, count_num,
                              ship_type, c_prob, df_prob, max_time, index, comm, tour_id, payload_i, depot_i)
    assert [] == used_veh, "incorrect list of used vehicles"
    assert pd.DataFrame(columns = ['tour_id', 'departureTimeInSec', 'departureLocation_zone', 'maxTourDurationInSec',
                                        'departureLocation_x','departureLocation_y']).equals(tour_df), "incorrect solution in tour df"
    assert pd.DataFrame(columns = ['payloadId','sequenceRank','tourId','payloadType','weightInlb','cummulativeWeightInlb',
                                        'requestType','locationZone','estimatedTimeOfArrivalInSec','arrivalTimeWindowInSec_lower',
                                        'arrivalTimeWindowInSec_upper','operationDurationInSec', 'locationZone_x', 'locationZone_y']).equals(payload_df), "incorrect solution in payload df"
    assert pd.DataFrame(columns = ['carrierId','tourId', 'vehicleId', 'vehicleTypeId','depot_zone', 'depot_zone_x', 'depot_zone_y']).equals(carrier_df), "incorrect solution in carrier df"


def test_input_processing_create_data_solve_vrp_delivery_normal():
    """ Testing the input_files_processing, creating data dictionary, and solving a normal,
        no exception vehicle routing problem
    """
    tour_df = pd.DataFrame(columns = ['tour_id', 'departureTimeInSec', 'departureLocation_zone', 'maxTourDurationInSec',
                                        'departureLocation_x','departureLocation_y'])
    # Format for carrier data frame: carrierId,tourId, vehicleId,vehicleTypeId,depot_zone
    carrier_df = pd.DataFrame(columns = ['carrierId','tourId', 'vehicleId', 'vehicleTypeId','depot_zone', 'depot_zone_x', 'depot_zone_y'])
    # format for payload format
    # payloadId, sequenceRank, tourId, payloadType, weightInlb, requestType,locationZone,
    # estimatedTimeOfArrivalInSec, arrivalTimeWindowInSec_lower, arrivalTimeWindowInSec_upper,operationDurationInSec
    payload_df = pd.DataFrame(columns = ['payloadId','sequenceRank','tourId','payloadType','weightInlb','cummulativeWeightInlb',
                                        'requestType','locationZone','estimatedTimeOfArrivalInSec','arrivalTimeWindowInSec_lower',
                                        'arrivalTimeWindowInSec_upper','operationDurationInSec', 'locationZone_x', 'locationZone_y'])

    travel_file = 'test_data/sel_tt_delivery.csv.gz'
    dist_file = 'test_data/sel_dist_delivery.csv'
    CBGzone_file = 'test_data/CBGzone_df.geojson'
    carrier_file = 'test_data/c_prob_delivery.csv'
    payload_file = 'test_data/df_prob_delivery.csv'
    vehicleType_file = 'test_data/v_df_delivery.csv'

    tt_df, dist_df, CBGzone_df, c_prob, df_prob, v_df, vc_prob = vrp.input_files_processing(travel_file, dist_file,
                                                                                                                 CBGzone_file, carrier_file, payload_file, vehicleType_file)

    prob_type = 'delivery'
    carr_id = 'B2C_2879885.0'
    depot_loc = c_prob.loc[c_prob['carrier_id'] == carr_id]['depot_zone'].values[0]
    veh = 'md_D_Diesel'
    ship_type = 'B2C'
    max_time = 900
    comm = 5
    count_num = 21
    s_used_veh = [11]
    index = 'internal'
    path_stops = '../../FRISM_input_output_AT/Survey_Data/'  # We do not info on stop distribution for external tours
    tour_id = payload_i = depot_i = 0

    data = vrp.create_data_model(df_prob, depot_loc, prob_type, v_df, vc_prob, c_prob, carr_id,
                                                CBGzone_df, tt_df, dist_df, veh, comm, index, path_stops)

    used_veh = vrp.form_solve(data, tour_df, carr_id, carrier_df, payload_df, prob_type, count_num,
                          ship_type, c_prob, df_prob, max_time, index, comm, tour_id, payload_i, depot_i)


    # Reading in saved solution dataframes for tour, paylaod and carrier
    sv_tour_df = pd.read_csv('test_data/tour_df_delivery_internal.csv')
    sv_payload_df = pd.read_csv('test_data/payload_df_delivery_internal.csv')
    sv_carrier_df = pd.read_csv('test_data/carrier_df_delivery_internal.csv')

    # Make sure all columns have same data types
    for c in list(tour_df.columns):
        tour_df[c] = tour_df[c].astype(sv_tour_df[c].dtypes)

    for c in list(payload_df.columns):
        payload_df[c] = payload_df[c].astype(sv_payload_df[c].dtypes)

    for c in list(carrier_df.columns):
        carrier_df[c] = carrier_df[c].astype(sv_carrier_df[c].dtypes)

    assert s_used_veh == used_veh, "incorrect list of used vehicles"
    assert sv_tour_df.equals(tour_df), "incorrect solution in tour df"
    assert sv_payload_df.iloc[:, :-2].equals(payload_df.iloc[:, :-2]), "incorrect solution in payload df"
    assert sv_carrier_df.equals(carrier_df), "incorrect solution in carrier df"
