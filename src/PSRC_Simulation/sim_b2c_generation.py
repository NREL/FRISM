
# %%
"""
Reads the population, applies the estimated e-commerce models, and writes a
person-level monthly delivery frequency table.

Two population formats are supported, selected with -pt:
  daysim   PSRC DaySim / SoundCast 'hh_and_persons.h5'. GEOID is attached to
           each household by joining hhparcel to ParcelID in the parcel
           geography file.
  synthpop UrbanSim-style 'households.csv' / 'persons.csv'. GEOID is derived
           from the census block id.

Usage:
    python sim_b2c_generation.py -sn Base -yt 2018 -sa ST -pt daysim
"""
import os
import json
import random
import warnings
from argparse import ArgumentParser

import numpy as np

from frism_utility_b2cgeneration import (SynthPopulation, DaySimPopulation,
                                         EcomDemandModel)

warnings.filterwarnings("ignore")


# create global variables
def create_global_variable(input_setting):
    global state_id            # state_code e.g. WA: 53 CA: 6
    global state_abbr          # state abbr e.g. WA
    global county_in_region    # list of county id
    global urban_county_list   # list of county id treated as urban
    global fdir_in_out         # upper folder
    global input_variables     # various input files and folders identified in create_input_variable.py

    # folder_path
    fdir_in_out = input_setting['input_variables']['frism_data_folder']
    # variables
    state_id = input_setting['input_variables']['state_code']
    state_abbr = input_setting['input_variables']['state_abbr']
    county_in_region = input_setting['input_variables']['county_list']
    urban_county_list = input_setting['input_variables'].get('urban_county_list', county_in_region)
    input_variables = input_setting['input_variables']


# generate file path information
def b2c_generation_file_path(input_variables, year, population_type):
    """Locate the population, zone file and estimated model folder."""
    pop_path = (input_variables["frism_data_folder"]
                + input_variables["sub_folder_synth_pop"]
                + str(year) + "/")

    if population_type == "daysim":
        population_file = pop_path + input_variables["daysim_population_file"]
        parcel_geography_file = pop_path + input_variables["parcel_geography_file"]
        population_paths = {"population_file": population_file,
                            "parcel_geography_file": parcel_geography_file}
    else:
        population_paths = {"household_file": pop_path + "households.csv",
                            "person_file": pop_path + "persons.csv"}

    zone_file = (input_variables["frism_data_folder"]
                 + input_variables["sub_folder_network"]
                 + input_variables["zone_file"])

    model_dir = (input_variables["frism_data_folder"]
                 + input_variables["sub_folder_b2c_model"])

    return population_paths, zone_file, model_dir


def main(args=None):
    # read input files
    parser = ArgumentParser()
    parser.add_argument("-sn", "--scenario", dest="scenario",
                        help="scenario", required=True, type=str)
    parser.add_argument("-yt", "--analysis year", dest="target_year",
                        help="20XX", required=True, type=int)
    parser.add_argument("-sa", "--Study_area ", dest="study_region",
                        help="ST, SF", required=True, type=str)
    parser.add_argument("-pt", "--population type", dest="population_type",
                        help="daysim (h5) or synthpop (csv)", default="daysim",
                        choices=["daysim", "synthpop"], type=str)
    parser.add_argument("-sd", "--random seed", dest="seed",
                        help="seed for reproducible runs", default=None, type=int)
    args = parser.parse_args()
    scenario = args.scenario
    year = args.target_year
    study_region = args.study_region
    population_type = args.population_type

    # The choice and frequency models are both sampled from, as is the
    # education imputation, so a run is not reproducible without a seed.
    if args.seed is not None:
        random.seed(args.seed)
        np.random.seed(args.seed)

    # Read input_setting. Before this need to run create_input_variable.py that will create input_setting_{region}.json file
    with open("input_setting_{}.json".format(study_region), 'r') as openfile:
        # Reading from json file
        input_setting = json.load(openfile)
    # create dictionary by name in input_setting
    input_variables = input_setting['input_variables']

    # Generate global variables
    create_global_variable(input_setting)

    # Create the file path for input data processing
    population_paths, zone_file, model_dir = b2c_generation_file_path(
        input_variables, year, population_type)

    common = dict(zone_file=zone_file,
                  state_id=state_id,
                  county_in_region=county_in_region,
                  urban_county_list=urban_county_list,
                  min_age=16)

    print(f"Creating population ({population_type})")
    if population_type == "daysim":
        population = DaySimPopulation(
            education_distribution=input_variables.get("b2c_education_distribution"),
            seed=args.seed,
            **population_paths, **common)
    else:
        population = SynthPopulation(**population_paths, **common)

    print("Applying e-commerce demand models")
    models = EcomDemandModel(model_dir=model_dir)
    df_per = models.predict(population.person)

    print("Write the result in the folder")
    out_dir = (input_variables["frism_data_folder"]
               + input_variables["sub_folder_b2c_demand"]
               + f"{year}_{scenario}/")
    os.makedirs(out_dir, exist_ok=True)

    df_per["block_id"]= df_per["GEOID"]
    df_per_final = df_per[["household_id", "member_id", "block_id", "GEOID", "County",
                           "DELIV_GOOD", "DELIV_GROC", "DELIV_FOOD"]]
    df_per_final.to_csv(out_dir + f"per_del_{year}.csv", index=False)

    print(f"Completed: {len(df_per_final):,} persons written to {out_dir}per_del_{year}.csv")
    # for column in ["DELIV_GOOD", "DELIV_GROC", "DELIV_FOOD"]:
    #     share = (df_per_final[column] > 0).mean()
    #     print(f"  {column}: {share:.1%} of persons, mean {df_per_final[column].mean():.2f} deliveries/month")


if __name__ == "__main__":
    main()
