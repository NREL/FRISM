# %%
from matplotlib.image import AxesImage
import pandas as pd
import numpy as np
#import geopandas as gpd
#import networkx as nx
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline

# %%
# Define the directory 
f_dir_val= "../../../FRISM_input_output_SF/Validation/"
# %%
# Read TOD from INRIX  
MD_dpt=pd.read_csv(f_dir_val+"md_tod_inrix_observed.csv")
HD_dpt=pd.read_csv(f_dir_val+"hd_tod_inrix_observed.csv" )
# Read TOD from Simulation
MD_dpt_B2BC=pd.read_csv(f_dir_val+"md_tod_frism_simulated.csv")
HD_dpt_B2B=pd.read_csv(f_dir_val+"hd_tod_frism_simulated.csv")

# %%
# To convert 24 hour aggregation to spline for smooth plots
md_sim_trip = MD_dpt_B2BC['Trip_rate'].to_numpy()
md_sim_hour = MD_dpt_B2BC['start_hour'].to_numpy()
hd_sim_trip = HD_dpt_B2B['Trip_rate'].to_numpy()
hd_sim_hour = HD_dpt_B2B['start_hour'].to_numpy()

md_inrix_trip = MD_dpt['Trip_rate'].to_numpy()
md_inrix_hour = MD_dpt['start_hour'].to_numpy()
hd_inrix_trip = HD_dpt['Trip_rate'].to_numpy()
hd_inrix_hour = HD_dpt['start_hour'].to_numpy()

md_sim_Spline = make_interp_spline(md_sim_hour, md_sim_trip)
hd_sim_Spline = make_interp_spline(hd_sim_hour, hd_sim_trip)
md_inrix_Spline = make_interp_spline(md_inrix_hour, md_inrix_trip)
hd_inrix_Spline = make_interp_spline(md_inrix_hour, md_inrix_trip)


md_sim_hour = np.linspace(md_sim_hour.min(), md_sim_hour.max(), 24*10)
md_sim_trip = md_sim_Spline(md_sim_hour)
hd_sim_hour = np.linspace(hd_sim_hour.min(), hd_sim_hour.max(), 24*10)
hd_sim_trip = hd_sim_Spline(hd_sim_hour)

 
md_inrix_hour = np.linspace(md_inrix_hour.min(), hd_inrix_hour.max(), 24*10)
md_inrix_trip = md_inrix_Spline(md_inrix_hour)
hd_inrix_hour = np.linspace(hd_inrix_hour.min(), hd_inrix_hour.max(), 24*10)
hd_inrix_trip = hd_inrix_Spline(hd_inrix_hour)

# Plot for MD
plt.figure(figsize = (8,6))
plt.plot(md_inrix_hour,md_inrix_trip,color ="blue", label="Observed (INRIX)", alpha = 0.3,)
plt.plot(md_sim_hour,md_sim_trip , color ="red", label="Simulated (FRISM)", alpha = 0.3,)
plt.title("Distrubtion of MD stop activities  by time of day")
plt.legend(loc="upper right")
plt.savefig(f_dir_val+'Val_truck_dist_MD.png')
# Plot for HD
plt.figure(figsize = (8,6))
plt.plot(hd_inrix_hour,hd_inrix_trip,color ="blue", label="Observed (INRIX)", alpha = 0.3,)
plt.plot(hd_sim_hour,hd_sim_trip , color ="red", label="Simulated (FRISM)", alpha = 0.3,)
plt.title("Distrubtion of HD stop activities by time of day")
plt.legend(loc="upper right")
plt.savefig(f_dir_val+'Val_truck_dist_HD.png')
# %%

