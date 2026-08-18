# %%
from re import A
import pandas as pd
import numpy as np
import geopandas as gpd
import random
import os
from shapely.geometry import Point
import math 

# %%
f_dir= "../../../FRISM_input_output_BO/Sim_inputs/Geo_data/"
f_name= "Boston_freight_centroids.geojson"

g_df = gpd.read_file(f_dir+f_name) 
# %%
g_df_filtered= g_df[g_df["MESOZONE"].str.len()>10] 

county_list = g_df_filtered["CBPZONE"].unique()

'''
'25001', '25003','25005','25007','25009','25011', '25013', '25015','25017', '25019'
'25021','25023' '25025', , '25027'
'33015','33011', '33013', '33005'
'44001', '44003','44005','44007','44009'

['25001', '25003','25005','25007','25009','25011', '25013', '25015','25017', '25019',
                    '25021','25023' '25025','25027','33015','33011', '44001', '44003','44005','44007','44009']
'''
# %%
f_dir= "../../../FRISM_input_output_BO/CTPS_Data/zoning/"
f_name= "CTPS_TDM23_TAZ_2017g_v202303.shp"

g_df_zone = gpd.read_file(f_dir+f_name)
g_df_zone=g_df_zone.to_crs(g_df.crs)
# %%
g_df_zone_I = g_df_zone[g_df_zone["type"] == "I"]

g_df_zone_E= g_df_zone[g_df_zone["type"] == "E"]

# %%
single_geometry = g_df_zone_I.geometry.unary_union
single_geometry = gpd.GeoDataFrame(geometry=[single_geometry], crs=g_df_zone_I.crs)

# %%
is_inside = gpd.sjoin(g_df, g_df_zone_I, how="inner", predicate="within")

mesozone_in_region = is_inside["MESOZONE"].unique().tolist()

is_outside = g_df[~g_df["MESOZONE"].isin(mesozone_in_region)]

g_df_zone_E["centroid"] = g_df_zone_E["geometry"].centroid

g_df_zone_E=g_df_zone_E.drop(columns=['geometry'])
g_df_zone_E=g_df_zone_E.rename(columns={"centroid": "geometry"})
# %%
ENTRY_POINTS = g_df_zone_E[["taz_id", "Shape_Area"]]
ENTRY_POINTS["taz_id"]= ENTRY_POINTS["taz_id"].astype(str)
ENTRY_POINTS['lon'] = g_df_zone_E.geometry.x
ENTRY_POINTS['lat'] = g_df_zone_E.geometry.y

EXTERNAL_ZONES = pd.DataFrame([
    # name,           lat,      lon
    ("New_York",      40.7128, -74.0060),
    ("Philadelphia",  39.9526, -75.1652),
    ("Chicago",       41.8781, -87.6298),
    ("Los_Angeles",   34.0522, -118.2437),
    ("Atlanta",       33.7490, -84.3880),
    ("Albany",        42.6526, -73.7562),
    ("Hartford",      41.7658, -72.6734),
    ("Portland_ME",   43.6591, -70.2568),
    ("Manchester_NH", 42.9956, -71.4548),
    ("Montreal",      45.5017, -73.5673),
], columns=["zone_name", "lat", "lon"])

EXTERNAL_ZONES = is_outside["MESOZONE"]
EXTERNAL_ZONES['lon'] = is_outside.geometry.x
EXTERNAL_ZONES['lat'] = is_outside.geometry.y


# %%
"""
External Zone -> External Entry Point Allocation
=================================================
For an agent-based freight model with a Boston study region.

Approach
--------
Each external zone (e.g., New York, LA, Chicago) is allocated to the external
entry point (highway gateway on the study-area boundary) that minimizes the
"detour" travel distance:

    cost(zone, entry) = d(zone, entry) + d(entry, region_centroid)

This approximates the path a long-haul truck would take: travel from the
external zone to the boundary, then into the region. Using d(zone, entry)
alone can mis-assign zones to the geometrically nearest gateway even when
that gateway points the wrong way; adding the entry->centroid leg penalizes
gateways on the far side of the region.

Two allocation modes are provided:
  1. Deterministic (all-or-nothing): each zone -> single best entry point.
  2. Probabilistic (logit split): zone demand is split across entry points,
     useful when multiple parallel corridors serve the same direction
     (e.g., I-90 vs I-84 approaches from the west).

Optionally, you can replace the haversine distance with true highway network
travel times (OSRM, OpenRouteService, or your own network skim) by swapping
out the `distance_matrix` computation — the allocation logic is unchanged.

Dependencies: numpy, pandas
"""

import numpy as np
import pandas as pd

# ----------------------------------------------------------------------
# 1. Input data
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
# 2. Distance functions
# ----------------------------------------------------------------------

def haversine_miles(lat1, lon1, lat2, lon2):
    """Great-circle distance in miles. Vectorized (numpy broadcasting OK)."""
    R = 3958.8  # earth radius, miles
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(a))


def build_detour_cost_matrix(zones: pd.DataFrame,
                             entries: pd.DataFrame,
                             #centroid=REGION_CENTROID,
                             circuity=1.2) -> pd.DataFrame:
    """
    Detour cost (miles) for each (zone, entry) pair:
        cost = circuity * [ d(zone, entry) + d(entry, centroid) ]

    `circuity` roughly converts great-circle to over-the-road distance.
    Returns DataFrame indexed by zone_name, columns = entry_name.

    To use real network skims instead, replace this function with one that
    queries OSRM / your highway network and returns the same shaped frame.
    """
    z_lat = zones["lat"].values[:, None]          # (Z, 1)
    z_lon = zones["lon"].values[:, None]
    e_lat = entries["lat"].values[None, :]        # (1, E)
    e_lon = entries["lon"].values[None, :]

    d_zone_entry = haversine_miles(z_lat, z_lon, e_lat, e_lon)        # (Z, E)
    # d_entry_centroid = haversine_miles(
    #     entries["lat"].values, entries["lon"].values,
    #     centroid[0], centroid[1]
    # )[None, :]                                                         # (1, E)

    cost = circuity * (d_zone_entry) # + d_entry_centroid)
    return pd.DataFrame(cost,
                        index=zones["MESOZONE"],
                        columns=entries["taz_id"])


# ----------------------------------------------------------------------
# 3. Allocation methods
# ----------------------------------------------------------------------

def allocate_deterministic(cost: pd.DataFrame) -> pd.DataFrame:
    """All-or-nothing: each external zone -> minimum-cost entry point."""
    best_entry = cost.idxmin(axis=1)
    best_cost = cost.min(axis=1)
    return pd.DataFrame({
        "zone_name": cost.index,
        "assigned_entry": best_entry.values,
        "detour_cost_mi": best_cost.round(1).values,
    }).reset_index(drop=True)


def allocate_logit(cost: pd.DataFrame,
                   theta: float = 0.05,
                   min_share: float = 0.02) -> pd.DataFrame:
    """
    Probabilistic split: P(entry | zone) = exp(-theta * cost) / sum(...).

    theta : cost sensitivity (1/mile). Larger -> more concentrated on the
            best entry. ~0.03-0.10 is a reasonable starting range for
            long-haul truck distances; calibrate to observed gateway counts
            (e.g., MassDOT permanent count stations / WIM data) if available.
    min_share : shares below this are zeroed out and the rest renormalized,
                so trivial slivers of demand don't clutter the matrix.
    """
    util = np.exp(-theta * cost.values)
    shares = util / util.sum(axis=1, keepdims=True)
    shares[shares < min_share] = 0.0
    shares = shares / shares.sum(axis=1, keepdims=True)
    out = pd.DataFrame(shares, index=cost.index, columns=cost.columns)
    return out.round(3)

# %%
cost = build_detour_cost_matrix(EXTERNAL_ZONES, ENTRY_POINTS)

print("=== Detour cost matrix (miles) ===")
print(cost.round(0).to_string(), "\n")

det = allocate_deterministic(cost)
print("=== Deterministic allocation ===")
print(det.to_string(index=False), "\n")

logit = allocate_logit(cost, theta=0.05)
print("=== Logit entry-point shares (theta=0.05) ===")
print(logit.to_string())

det.to_csv("external_zone_allocation_deterministic.csv", index=False)
logit.to_csv("external_zone_allocation_logit_shares.csv")


# ----------------------------------------------------------------------
# 4. Run
# ----------------------------------------------------------------------

# if __name__ == "__main__":
#     cost = build_detour_cost_matrix(EXTERNAL_ZONES, ENTRY_POINTS)

#     print("=== Detour cost matrix (miles) ===")
#     print(cost.round(0).to_string(), "\n")

#     det = allocate_deterministic(cost)
#     print("=== Deterministic allocation ===")
#     print(det.to_string(index=False), "\n")

#     logit = allocate_logit(cost, theta=0.05)
#     print("=== Logit entry-point shares (theta=0.05) ===")
#     print(logit.to_string())

#     det.to_csv("external_zone_allocation_deterministic.csv", index=False)
#     logit.to_csv("external_zone_allocation_logit_shares.csv")

# %%
# %%
import pandas as pd
import openmatrix as omx
# %%
file_dict="../../../FRISM_input_output_BO/CTPS_Data/od/2019_base/"
filename = 'od_trk_md.omx'
myfile = omx.open_file(file_dict+filename)
t_name=myfile.list_matrices()

HD=myfile["htrk"]
mapping_dict = myfile.mapping('lookup')

mapping_names = myfile.list_mappings()
print('Mappings:', mapping_names)

if mapping_names:
    zone_mapping = myfile.mapping(mapping_names[0])
    print(f"First 5 items in '{mapping_names[0]}':")
    for k, v in list(zone_mapping.items())[:5]:
        print(f'  {k}: {v}')

# %%
file_dict="../../../Data/"

filename = 'skims.omx'

myfile = omx.open_file(file_dict+filename)
t_name=myfile.list_matrices()

df=pd.DataFrame(t_name)
df.to_csv(file_dict+"table_list.csv")
t_time=myfile['SOV_TIME__AM']
t_dist=myfile['DIST']

# t_time.attrs
# myfile.list_all_attributes()
'''
/data/DRV_COM_WLK_DTIM__AM._v_attrs (AttributeSet), 6 attributes:
   [CLASS := 'CARRAY',
    TITLE := '',
    VERSION := '1.1',
    measure := 'DTIM',
    mode := 'DRV_COM_WLK',
    timePeriod := 'AM']
'''

myfile.list_mappings() # ['zone_id']

zone_id = myfile.mapping('zone_id')  
# %%
# t_dist[zone_id[100]][zone_id[101]]

# t_time[zone_id[100]][zone_id[101]]

# %%
"""
Summarize external-zone origin / destination truck trips from OMX OD matrices.

Reads four time-period OMX files (am, md, nt, pm), and for each vehicle type
('htrk' = heavy-duty, 'mtrk' = medium-duty) builds a table of:

    ID, origin_sum, destination_sum

for external zones only (zone ID > EXTERNAL_ID_MIN), summed over all four
periods. Then merges the two vehicle types into a single combined table.

OMX layout assumed (verified against od_trk_am.omx):
    /data/htrk        (nzones, nzones) float32   rows = origin, cols = destination
    /data/mtrk        (nzones, nzones) float32
    /lookup/Rows      (nzones,) int32            actual zone IDs
    /lookup/Columns   (nzones,) int32            actual zone IDs (same as Rows)
    /lookup/ID        (nzones,) int32            1..nzones positional index -- NOT zone IDs
"""
# %%
from pathlib import Path

import h5py
import numpy as np
import pandas as pd

# ----------------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------------
IN_DIR = Path("../../../FRISM_input_output_BO/CTPS_Data/od/2019_base")            # folder holding the four .omx files
OUT_DIR = Path("../../../FRISM_input_output_BO/CTPS_Data/od/2019_base/output")
PERIODS = ["am", "md", "nt", "pm"]
FILE_PATTERN = "od_trk_{period}.omx"

# Matrix name in the OMX -> label used in output filenames/columns
VEHICLES = {"htrk": "htrk", "mtrk": "mtrk"}

EXTERNAL_ID_MIN = 207000      # external zones are those with ID > this

# Which cells count toward the sums:
#   False -> full row / full column (all trips to or from an external zone,
#            regardless of whether the other end is internal or external)
#   True  -> external-to-external submatrix only
EXTERNAL_TO_EXTERNAL_ONLY = False

ROW_CHUNK = 512               # rows read at a time, keeps memory modest
DROP_INTRAZONAL = False       # True -> zero the diagonal before summing


# ----------------------------------------------------------------------------
# Core
# ----------------------------------------------------------------------------
def read_zone_ids(path):
    """Return the zone ID vector from an OMX file."""
    with h5py.File(path, "r") as f:
        if "lookup" in f and "Rows" in f["lookup"]:
            return f["lookup"]["Rows"][:].astype(np.int64)
        # fall back to positional index if no lookup is present
        n = f.attrs["SHAPE"][0]
        return np.arange(1, n + 1, dtype=np.int64)


def period_sums(path, matrix_name, ext_mask):
    """
    Row sums (origins) and column sums (destinations) for one matrix in one file.

    Returns two float64 arrays of length nzones, indexed positionally.
    """
    with h5py.File(path, "r") as f:
        mat = f["data"][matrix_name]
        n = mat.shape[0]
        origin = np.zeros(n, dtype=np.float64)
        dest = np.zeros(n, dtype=np.float64)

        for start in range(0, n, ROW_CHUNK):
            stop = min(start + ROW_CHUNK, n)
            block = mat[start:stop, :].astype(np.float64)

            if DROP_INTRAZONAL:
                rows = np.arange(start, stop)
                block[rows - start, rows] = 0.0

            if EXTERNAL_TO_EXTERNAL_ONLY:
                block = block * ext_mask[np.newaxis, :]
                block = block * ext_mask[start:stop, np.newaxis]

            origin[start:stop] = block.sum(axis=1)
            dest += block.sum(axis=0)

    return origin, dest


def build_vehicle_table(files, matrix_name, zone_ids, ext_mask):
    """Sum origin/destination totals across all periods, keep external zones."""
    n = zone_ids.size
    origin_total = np.zeros(n, dtype=np.float64)
    dest_total = np.zeros(n, dtype=np.float64)

    for period, path in files.items():
        o, d = period_sums(path, matrix_name, ext_mask)
        origin_total += o
        dest_total += d
        print(f"  {matrix_name} {period}: "
              f"origins={o[ext_mask].sum():,.1f}  dests={d[ext_mask].sum():,.1f}")

    df = pd.DataFrame({
        "ID": zone_ids,
        "origin_sum": origin_total,
        "destination_sum": dest_total,
    })
    df = df.loc[ext_mask].sort_values("ID").reset_index(drop=True)
    df["total_sum"] = df["origin_sum"] + df["destination_sum"]
    return df



OUT_DIR.mkdir(parents=True, exist_ok=True)

files = {p: IN_DIR / FILE_PATTERN.format(period=p) for p in PERIODS}
missing = [str(p) for p in files.values() if not p.exists()]
if missing:
    raise FileNotFoundError("Missing OMX file(s): " + ", ".join(missing))

# Zone IDs must be consistent across periods
zone_ids = read_zone_ids(files[PERIODS[0]])
for p in PERIODS[1:]:
    if not np.array_equal(zone_ids, read_zone_ids(files[p])):
        raise ValueError(f"Zone ID vector in {files[p].name} does not match {PERIODS[0]}")

ext_mask = zone_ids > EXTERNAL_ID_MIN
print(f"{zone_ids.size} zones, {ext_mask.sum()} external (ID > {EXTERNAL_ID_MIN})")

tables = {}
for matrix_name, label in VEHICLES.items():
    print(f"Processing {label} ...")
    df = build_vehicle_table(files, matrix_name, zone_ids, ext_mask)
    df.to_csv(OUT_DIR / f"external_od_{label}.csv", index=False)
    tables[label] = df

# Combined wide table: one row per external zone, one column set per vehicle
combined = None
for label, df in tables.items():
    renamed = df.rename(columns={
        "origin_sum": f"{label}_origin_sum",
        "destination_sum": f"{label}_destination_sum",
        "total_sum": f"{label}_total_sum",
    })
    combined = renamed if combined is None else combined.merge(renamed, on="ID", how="outer")

combined = combined.fillna(0.0).sort_values("ID").reset_index(drop=True)
combined["all_origin_sum"] = combined[[f"{v}_origin_sum" for v in VEHICLES.values()]].sum(axis=1)
combined["all_destination_sum"] = combined[[f"{v}_destination_sum" for v in VEHICLES.values()]].sum(axis=1)
combined.to_csv(OUT_DIR / "external_od_combined.csv", index=False)

# Long format, if you'd rather have vehicle type as a column
long = pd.concat(
    [df.assign(vehicle_type=label) for label, df in tables.items()],
    ignore_index=True,
)[["ID", "vehicle_type", "origin_sum", "destination_sum", "total_sum"]]
long.to_csv(OUT_DIR / "external_od_combined_long.csv", index=False)

print(f"\nWrote {len(combined)} external zones to {OUT_DIR.resolve()}")
print(combined.head())
# %%
from pathlib import Path

import h5py
import numpy as np
import pandas as pd
travel_file= "../../../FRISM_input_output_BO/CTPS_Data/skim/2019_base/truck_skims_md.omx"

f = h5py.File(travel_file, 'r')

list(f.keys())
# %%
f_data=f['data']
f_data_hdt_time= f_data['htrk_time']
f_data_hdt_dist= f_data['htrk_dist']

f_lu=f['lookup'].keys()
print(f['lookup']["ID"][0], f['lookup']["Destination"][0],f['lookup']["Origin"][0])
dic_taz={}
for i in range(0,5839):
    dic_taz [f['lookup']["Origin"][i]]= f['lookup']["ID"][i] -1

# %%
list(f_data.keys())

# %%
list(f_2030_hh.keys())
# %%
f_2030_hh['block0_items']
# %%
hh=pd.read_hdf(f_2030_hh)


# %%
f_7to8=f['Skims']
list(f_7to8.keys())
tt_df = f['Skims']['heavy_truckt']
dist_df = f['Skims']['heavy_truckd']  # Slow step