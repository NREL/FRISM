# %%
import pandas as pd
import geopandas as gp
import csv
import numpy as np
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
from copy import copy
import os
import inspect
from xml.dom import minidom
import math
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from time import time
import numpy as np
from argparse import ArgumentParser
from shapely.geometry import Point
import random
import config
import pickle
# %%
travel_file= "../../../FRISM_input_output_SF/Sim_inputs/Geo_data/tt_df_cbg.csv.gz"
tt_df = pd.read_csv(travel_file, compression='gzip', header=0, sep=',', quotechar='"', on_bad_lines='skip')

dist_file= "../../../FRISM_input_output_SF/Sim_inputs/Geo_data/SF_travel_skim_beam.csv.zip"
dist_df = pd.read_csv(dist_file, compression='zip', header=0, sep=',', quotechar='"', on_bad_lines='skip')
dist_df=dist_df[["origin",	"destination","beam_dist_mile"]]
# %%
tt_df= tt_df.merge(dist_df, on=["origin","destination"])

# %%
factor_file= "../../../FRISM_input_output_SF/Sim_inputs/Geo_data/travel_time_scaling_factor.csv"
factor_df = pd.read_csv(factor_file)

# %%
def find_factor (distance, df):
    if distance <100:
        f_val= df[df["distance_bin_mile"]==distance]["scaling_factor"].values[0]
    else:
        f_val= df[df["distance_bin_mile"]==100]["scaling_factor"].values[0]
    return f_val       
# %%
tt_df['new_time'] = tt_df.apply(lambda x: x["TIME_minutes"]*find_factor (int(x["beam_dist_mile"]+1), factor_df), axis=1)
# %%
tt_df= tt_df[["origin","destination","new_time"]]
tt_df=tt_df.rename(columns={"new_time":"TIME_minutes"})
tt_df.to_csv("../../../FRISM_input_output_SF/Sim_inputs/Geo_data/tt_df_cbg_v2.csv.gz", compression="gzip", index=False)