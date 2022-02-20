# %%
import pandas as pd
import numpy as np
#import geopandas as gpd
#import networkx as nx
import matplotlib.pyplot as plt
from argparse import ArgumentParser
#import osmnx as ox
#import plotly.graph_objects as go

parser = ArgumentParser()
parser.add_argument("-st", "--shipment type", dest="ship_type",
                    help="B2B or B2C", required=True, type=str)
args = parser.parse_args()

# %%
county_list=[1, 13, 41, 55, 75, 81, 85, 95, 97]
sf_map = plt.imread('../../../FRISM_input_output/Sim_inputs/Geo_data/SF_map.png')
BBox= (-123.655,-121.524,36.869,38.852)

# %%
ship_type=args.ship_type
#ship_type="B2B"
for count_num in county_list:

    payload_df=pd.read_csv("../../../FRISM_input_output/Sim_outputs/Tour_plan/{0}_county{1}_payload_xy.csv" .format(ship_type, count_num))
    #'locationZone_x':long, 'locationZone_y':lat
    fig, ax = plt.subplots(figsize = (9.68,11.45))
    ax.scatter(payload_df.locationZone_x, payload_df.locationZone_y, zorder=1, alpha= 0.2, c='b', s=10)
    ax.set_title('Plotting payload points for county{0}'.format(count_num))
    ax.set_xlim(BBox[0],BBox[1])
    ax.set_ylim(BBox[2],BBox[3])
    ax.imshow(sf_map, zorder=0, extent = BBox, aspect= 'equal')
    fig.savefig('../../../FRISM_input_output/Sim_outputs/{0}payload_plot_county{1}.png'.format(ship_type, count_num))
