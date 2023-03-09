
import pandas as pd
import importlib
import geopandas as gp

vrp = importlib.import_module("VRP_OR-tools_Stops_veh_tech")

def test_tt_cal_normal():
    """Testing normal case where the origin and destination exist in the origin-destination travel time dataframe
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
    """Testing case where the origin and destination are not in the travel time dataframe 
        but in the orgin-destination distance dataframe
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
    """
    Testing case where the origin and destination are not in the travel time dataframe 
    and are not in the orgin-destination distance dataframe
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
