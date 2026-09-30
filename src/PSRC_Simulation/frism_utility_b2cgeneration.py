# %%
"""
Utilities for the FRISM B2C demand generation step (PSRC application).

This module holds the reusable pieces of the B2C generation process:

* recoding functions that map population codes onto the variable definitions
  used when the e-commerce models were estimated
  (see ``../Simulation/HH_ecom_model.py``);
* ``BasePopulation``, holding the zone join and dummy handling shared by every
  population format;
* ``SynthPopulation``, for the UrbanSim-style ``households.csv`` /
  ``persons.csv`` synthetic population;
* ``DaySimPopulation``, for the PSRC DaySim / SoundCast ``hh_and_persons.h5``
  population, with GEOID attached from the parcel geography file;
* ``EcomDemandModel``, which wraps the six estimated ``.sav`` models and
  applies them in the required order.

Conventions follow the other ``frism_*.py`` modules in this folder: classes
take file paths in ``__init__``, do their loading in private ``_load_*`` /
``_process_*`` methods, and expose the results as attributes.
"""
import os
import random
import sys
import types

import h5py
import joblib
import numpy as np
import pandas as pd
import geopandas as gpd


def install_pandas_compat_shim():
    """Make models pickled under pandas 1.x loadable under pandas >= 2.0.

    The .sav files in this pipeline were written when pandas still had
    ``pandas.core.indexes.numeric.Int64Index``. Pandas 2.0 removed that module
    and folded the numeric index types into plain ``pd.Index``, so unpickling
    the models on a current install fails with

        ModuleNotFoundError: No module named 'pandas.core.indexes.numeric'

    Registering a stand-in module whose Int64Index/Float64Index resolve to
    ``pd.Index`` is enough: pickle calls ``_new_Index(cls, {data, dtype, name})``,
    and ``pd.Index`` accepts exactly those arguments and infers the dtype from
    the stored data, so the reconstructed index is equivalent.

    This only affects reading the old files. Running ``resave_b2c_models.py``
    rewrites them under the current pandas and removes the need for the shim,
    which is the better long-term fix. The shim is a no-op on pandas 1.x.
    """
    name = "pandas.core.indexes.numeric"
    if name in sys.modules:
        return
    try:
        __import__(name)
        return  # pandas 1.x: the real module exists, leave it alone
    except ImportError:
        pass

    shim = types.ModuleType(name)
    for cls in ["Int64Index", "Float64Index", "UInt64Index", "NumericIndex"]:
        setattr(shim, cls, pd.Index)
    sys.modules[name] = shim


def countyid_from_cbgid(state_id, cbgid):
    """Census block group id -> three digit county id, 0 if out of state.

    Identical to ``countyid_from_cbgid`` in frism_pop_shipment.py. It is
    repeated here rather than imported so that the generation step, which runs
    first in the pipeline, does not depend on the tour-planning modules and
    their heavier requirements. Keep the two in sync.
    """
    cbgid_str = str(int(cbgid))
    if len(cbgid_str) == 12 and cbgid_str[0:2] == str(state_id).zfill(2):
        return int(cbgid_str[2:5])
    elif len(cbgid_str) == 11 and cbgid_str[0:1] == str(state_id).zfill(1):
        return int(cbgid_str[1:4])
    return 0


# ---------------------------------------------------------------------------
# Recoding functions
#
# Only the recodes actually used by the estimated models are kept here. The
# NHTS-code recodes that were used during estimation (edu_class, student_class,
# wfh_class, work_class, mode_est) live in the estimation script and are not
# needed at simulation time.
# ---------------------------------------------------------------------------
def income_num2group(income):
    """Annual household income (dollars) -> 6 income classes, as estimated."""
    if income < 25000:
        return 0
    elif income < 50000:
        return 1
    elif income < 75000:
        return 2
    elif income < 100000:
        return 3
    elif income < 150000:
        return 4
    return 5


def race_class_synth(race):
    """Synthetic-population race code -> 0: other, 1: white, 2: black, 3: Asian."""
    return {1: 1, 2: 2, 6: 3}.get(race, 0)


def race_class_daysim(prace):
    """DaySim prace -> 0: other, 1: white, 2: black, 3: Asian.

    DaySim codes (data dictionary): 1 = White alone non-Hispanic,
    2 = Black alone non-Hispanic, 3 = Asian alone non-Hispanic,
    4 = other alone, 5 = two or more races, 6 = White Hispanic,
    7 = non-White Hispanic. Codes outside that range appear in the PSRC file
    and fall through to 'other'.
    """
    return {1: 1, 2: 2, 3: 3}.get(prace, 0)


def home_class(tenure):
    """Tenure -> 1: owner, 0: otherwise.

    Works for both the synthetic-population 'tenure' field and the DaySim
    'hownrent' field, which both use 1 = own.
    """
    return 1 if tenure == 1 else 0


def child_class(child):
    """'yes'/'no' children flag -> 1/0."""
    return 1 if str(child).lower() == "yes" else 0


def edu_class_synth(educ):
    """Synthetic-population education attainment -> 0: < HS, 1: HS, 2: college, 3: graduate."""
    if educ < 16:
        return 0
    elif educ == 16:
        return 1
    elif educ <= 21:
        return 2
    return 3


def age_class(age):
    """Age -> 5 classes (R_AGE_C_0 .. R_AGE_C_4), as estimated."""
    if age < 18:
        return 0
    elif age < 25:
        return 1
    elif age < 50:
        return 2
    elif age < 65:
        return 3
    return 4


def sex_class(sex):
    """Sex -> 1: male, 0: otherwise. DaySim pgend uses the same 1 = male coding."""
    return 1 if sex == 1 else 0


def urban_class(county, urban_county_list):
    """County id -> 1 if the county is in the urban list, else 0."""
    return 1 if county in urban_county_list else 0


def worker_class_daysim(pwtyp):
    """DaySim pwtyp (0 = non-worker, 1 = full time, 2 = part time) -> 1/0."""
    return 1 if pwtyp in (1, 2) else 0


# Age-banded education distribution used when the population carries no
# educational attainment. Each entry is [min_age, max_age, [p0, p1, p2, p3]]
# over the four edu_class_synth categories: 0 = less than high school,
# 1 = high school graduate, 2 = some college / bachelor's, 3 = graduate degree.

DEFAULT_EDUCATION_DISTRIBUTION = [
    [16, 17, [1.00, 0.00, 0.00, 0.00]],
    [18, 24, [0.10, 0.30, 0.58, 0.02]],
    [25, 64, [0.08, 0.20, 0.47, 0.25]],
    [65, 999, [0.12, 0.27, 0.42, 0.19]],
]


def impute_education(age, distribution=None, rng=None):
    """Draw an education class for people whose population file has no education.
    """
    distribution = distribution or DEFAULT_EDUCATION_DISTRIBUTION
    rng = rng or np.random.default_rng()

    age = np.asarray(age)
    educ = np.full(age.shape, -1, dtype=np.int8)
    for min_age, max_age, probabilities in distribution:
        mask = (age >= min_age) & (age <= max_age)
        if mask.sum() == 0:
            continue
        probabilities = np.asarray(probabilities, dtype=float)
        probabilities = probabilities / probabilities.sum()
        educ[mask] = rng.choice(len(probabilities), size=int(mask.sum()), p=probabilities)

    unassigned = (educ == -1).sum()
    if unassigned:
        print(f"  warning: {unassigned:,} people outside every education age band; set to class 0")
        educ[educ == -1] = 0
    return educ


def add_dummies(df, class_vars, required_columns=None):
    """Create 0/1 dummy columns for every variable in ``class_vars``.

    Two differences from the original inline loop, both of which matter when
    the code is moved to a new region or population format:
    """
    for var in class_vars:
        if var not in df.columns:
            #print(f"  warning: class variable '{var}' not in the table; skipped")
            continue
        if df[var].nunique() > 2:
            df = df.join(pd.get_dummies(df[var], prefix=var, dtype=int))

    for column in required_columns or []:
        if column not in df.columns:
            print(f"  warning: '{column}' absent in this region; filled with 0")
            df[column] = 0
    return df


# ---------------------------------------------------------------------------
# Population base class
# ---------------------------------------------------------------------------
class BasePopulation:
    """Shared zone handling and dummy creation for every population format

    zone_file: str, geojson file 'XXXX_freight.geojson'
    state_id: int, state FIPS code
    county_in_region: list, three digit county ids in the study region
    urban_county_list: list, county ids treated as urban (URBRUR = 1)
    min_age: int, minimum age assumed able to shop online
    """

    # Class variables that become dummies, and the dummy columns the estimated
    # models require. Keep these in sync with HH_ecom_model.py.
    HH_CLASS_VARS = ["HH_RACE", "HOMEOWN", "income_cls"]
    PER_CLASS_VARS = ["EDUC", "SCHTYP", "WRK_HOME", "WORKER", "R_AGE_C", "R_RACE", "R_SEX_IMP"]
    REQUIRED_DUMMIES = [
        "income_cls_1", "income_cls_2", "income_cls_3", "income_cls_4", "income_cls_5",
        "R_AGE_C_1", "R_AGE_C_2", "R_AGE_C_3", "R_AGE_C_4",
        "EDUC_1", "EDUC_2",
    ]

    def __init__(self, zone_file=None, state_id=None, county_in_region=None,
                 urban_county_list=None, min_age=16):
        self.zone_file = zone_file
        self.state_id = state_id
        self.county_in_region = county_in_region or []
        self.urban_county_list = urban_county_list or []
        self.min_age = min_age

        self.household = None
        self.person = None
        self.zone = None

    def _check_files(self, files):
        for label, path in files:
            if not path or not os.path.exists(path):
                raise FileNotFoundError(f"{label} file not provided or invalid: {path}")

    def _load_zone_file(self, file_path):
        """Zone geometry reduced to the GEOID -> County lookup this step needs.

        This mirrors ``Network._load_zone_file`` in frism_pop_shipment.py, minus
        the area calculation and CRS round-trip, which the generation step does
        not use.
        """
        zone = gpd.read_file(file_path)
        zone["County"] = zone["GEOID"].apply(lambda x: countyid_from_cbgid(self.state_id, x))
        zone["GEOID"] = zone["GEOID"].astype(np.int64)
        zone = zone[zone["County"].isin(self.county_in_region)].reset_index(drop=True)
        if zone.empty:
            raise ValueError(
                f"No zones left after filtering to counties {self.county_in_region}. "
                f"Check 'state_code' and 'county_list' in the input setting."
            )
        self.zone = zone

    def _attach_geography_to_household(self):
        """Attach County to the household table and drop households outside the region..
        """
        before = len(self.household)
        self.household = self.household.merge(self.zone[["GEOID", "County"]],
                                              on="GEOID", how="inner")
        dropped = before - len(self.household)
        if dropped:
            print(f"  {dropped:,} households ({dropped / max(before, 1):.1%}) dropped: "
                  f"CBG not in the freight zone file")
        if self.household.empty:
            raise ValueError("No households left after the zone join. Check that the "
                             "population and the freight zone file cover the same region.")
        self.household["County"] = self.household["County"].astype(int)

    def _finalize_person(self):
        """Add URBRUR and report. County already arrives via the household join."""
        self.person["URBRUR"] = self.person["County"].apply(
            lambda x: urban_class(x, self.urban_county_list))
        self.person = self.person.reset_index(drop=True)
        print(f"  {len(self.person):,} persons in {self.person['County'].nunique()} counties")


# ---------------------------------------------------------------------------
# UrbanSim-style synthetic population (CSV)
# ---------------------------------------------------------------------------
class SynthPopulation(BasePopulation):
    """Synthetic household and person CSVs, recoded for the e-commerce models.

    household_file: str, synthetic population 'households.csv'
    person_file: str, synthetic population 'persons.csv'
    plus the arguments of BasePopulation.

    Attributes
    ----------
    household : pd.DataFrame, recoded household table
    person : pd.DataFrame, recoded person table joined to household and zone
    zone : gpd.GeoDataFrame, zone table with GEOID and County
    """

    HH_RENAME = {
        "persons": "HHSIZE",
        "cars": "HHVEHCNT",
        "race_of_head": "HH_RACE",
        "workers": "WRKCOUNT",
        "tenure": "HOMEOWN",
        "hh_children": "CHILD",
        "children": "CHILD",
    }
    PER_RENAME = {
        "age": "R_AGE",
        "edu": "EDUC",
        "race_id": "R_RACE",
        "sex": "R_SEX_IMP",
        "student": "SCHTYP",
        "work_at_home": "WRK_HOME",
        "worker": "WORKER",
    }

    def __init__(self, household_file=None, person_file=None, **kwargs):
        super().__init__(**kwargs)
        self.household_file = household_file
        self.person_file = person_file

        self._check_files([("Household", household_file),
                           ("Person", person_file),
                           ("Zone", self.zone_file)])

        self._load_zone_file(self.zone_file)
        self._load_household_file(household_file)
        self._attach_geography_to_household()
        self._load_person_file(person_file)
        self._finalize_person()

    def _load_household_file(self, file_path):
        """Read and recode the synthetic household table.

        Only the variables available from the synthetic population can be used,
        which is a known limitation of the estimated models.
        """
        df = pd.read_csv(file_path, header=0, sep=",")
        df = df.rename(columns={k: v for k, v in self.HH_RENAME.items() if k in df.columns})

        # Cast to int64 so the merge key dtype matches the zone table — a float
        # key here silently drops every match (or raises, depending on pandas).
        df["GEOID"] = (df["block_id"] // 1000).astype(np.int64)

        df["income_est"] = df["income"] / 100000
        df["income_cls"] = df["income"].apply(income_num2group)
        df["HH_RACE"] = df["HH_RACE"].apply(race_class_synth)
        df["HOMEOWN"] = df["HOMEOWN"].apply(home_class)
        if "CHILD" in df.columns:
            df["CHILD"] = df["CHILD"].apply(child_class)

        self.household = add_dummies(df, self.HH_CLASS_VARS)

    def _load_person_file(self, file_path):
        """Read the synthetic person table, join household attributes, recode."""
        df = pd.read_csv(file_path, header=0, sep=",")
        df = df.rename(columns={k: v for k, v in self.PER_RENAME.items() if k in df.columns})

        df = df.merge(self.household, on="household_id", how="inner")
        # Assumption: only people at or above min_age shop online.
        df = df[df["R_AGE"] >= self.min_age].reset_index(drop=True)

        df["EDUC"] = df["EDUC"].apply(edu_class_synth)
        df["R_AGE_C"] = df["R_AGE"].apply(age_class)
        df["R_RACE"] = df["R_RACE"].apply(race_class_synth)
        df["R_SEX_IMP"] = df["R_SEX_IMP"].apply(sex_class)

        self.person = add_dummies(df, self.PER_CLASS_VARS,
                                  required_columns=self.REQUIRED_DUMMIES)


# ---------------------------------------------------------------------------
# PSRC DaySim / SoundCast population (HDF5)
# ---------------------------------------------------------------------------
class DaySimPopulation(BasePopulation):
    """PSRC DaySim population ('hh_and_persons.h5') recoded for the models.

    population_file: str, HDF5 file with 'Household' and 'Person' groups
    parcel_geography_file: str, csv mapping ParcelID to census geography
    education_distribution: list, age-banded education shares (see
        impute_education); None uses DEFAULT_EDUCATION_DISTRIBUTION
    seed: int, seed for the education imputation
    plus the arguments of BasePopulation.

    The DaySim population has no vehicle count, no educational attainment and
    no household race. Vehicle count and household race are not used by any of
    the estimated models, so they are simply absent. Education is imputed —
    see impute_education for what that assumes.
    """

    HH_FIELDS = ["hhno", "hhparcel", "hhsize", "hhincome", "hownrent", "hhtaz"]
    PER_FIELDS = ["hhno", "pno", "pagey", "pgend", "prace", "pptyp", "pwtyp", "pstyp"]

    # Parcel geography columns. Census2010Block is the 15-digit block, which
    # keeps the output's block_id field consistent with the CSV synthetic
    # population; Census2010BlockGroup is the 12-digit CBG used as GEOID.
    PARCEL_FIELDS = ["ParcelID", "Census2010BlockGroup"]

    def __init__(self, population_file=None, parcel_geography_file=None,
                 education_distribution=None, seed=None, **kwargs):
        super().__init__(**kwargs)
        self.population_file = population_file
        self.parcel_geography_file = parcel_geography_file
        self.education_distribution = education_distribution
        self.rng = np.random.default_rng(seed)
        self.parcel_geography = None

        self._check_files([("Population", population_file),
                           ("Parcel geography", parcel_geography_file),
                           ("Zone", self.zone_file)])

        self._load_zone_file(self.zone_file)
        self._load_parcel_geography(parcel_geography_file)
        self._load_household_group(population_file)
        self._attach_geography_to_household()
        self._load_person_group(population_file)
        self._finalize_person()

    @staticmethod
    def _read_h5_group(file_path, group, fields):
        """Read selected datasets of an HDF5 group into a DataFrame.

        Only the needed fields are read; the PSRC file carries roughly 4.4
        million person records, so pulling every column wastes memory. Note
        that the h5 field names are not always identical to the names in the
        data dictionary (hownrent / hrestype vs hhownrent / hhrestype).
        """
        with h5py.File(file_path, "r") as store:
            if group not in store:
                raise KeyError(f"Group '{group}' not in {file_path}. "
                               f"Found: {list(store.keys())}")
            available = set(store[group].keys())
            missing = [f for f in fields if f not in available]
            if missing:
                raise KeyError(f"Fields {missing} not in group '{group}'. "
                               f"Found: {sorted(available)}")
            return pd.DataFrame({f: store[group][f][:] for f in fields})

    def _load_parcel_geography(self, file_path):
        """ParcelID -> census block and block group lookup."""
        parcel = pd.read_csv(file_path, usecols=self.PARCEL_FIELDS)
        # Written as floats in the PSRC export; the ids are exact integers.
        #parcel["block_id"] = parcel["Census2010Block"].astype(np.int64)
        parcel["GEOID"] = parcel["Census2010BlockGroup"].astype(np.int64)
        #parcel = parcel[["ParcelID", "block_id", "GEOID"]]
        parcel = parcel[["ParcelID", "GEOID"]]

        duplicates = parcel["ParcelID"].duplicated().sum()
        if duplicates:
            print(f"  warning: {duplicates:,} duplicate ParcelID rows; keeping the first")
            parcel = parcel.drop_duplicates("ParcelID")

        self.parcel_geography = parcel
        print(f"  {len(parcel):,} parcels in the geography file")

    def _load_household_group(self, file_path):
        """Read the DaySim Household group, attach GEOID by parcel, recode."""
        df = self._read_h5_group(file_path, "Household", self.HH_FIELDS)
        df = df.rename(columns={"hhno": "household_id",
                                "hhsize": "HHSIZE",
                                "hownrent": "HOMEOWN"})

        # The DaySim population locates households by parcel, not by census
        # geography, so GEOID comes from the parcel geography file.
        before = len(df)
        df = df.merge(self.parcel_geography, left_on="hhparcel",
                      right_on="ParcelID", how="inner")
        unmatched = before - len(df)
        if unmatched:
            print(f"  {unmatched:,} households ({unmatched / max(before, 1):.1%}) dropped: "
                  f"hhparcel not in the parcel geography file")

        # A negative hhincome means missing data (data dictionary), not debt.
        # Clipping sends those households to the lowest income class.
        negative = int((df["hhincome"] < 0).sum())
        if negative:
            print(f"  {negative:,} households ({negative / max(len(df), 1):.2%}) "
                  f"have negative (missing) income; clipped to 0")
        df["income"] = df["hhincome"].clip(lower=0)

        df["income_est"] = df["income"] / 100000
        df["income_cls"] = df["income"].apply(income_num2group)
        df["HOMEOWN"] = df["HOMEOWN"].apply(home_class)

        self.household = add_dummies(df, self.HH_CLASS_VARS)
        print(f"  {len(self.household):,} households with a GEOID")

    def _load_person_group(self, file_path):
        """Read the DaySim Person group, join household attributes, recode."""
        df = self._read_h5_group(file_path, "Person", self.PER_FIELDS)
        df = df.rename(columns={"hhno": "household_id",
                                "pno": "member_id",
                                "pagey": "R_AGE"})

        df = df.merge(self.household, on="household_id", how="inner")
        # Assumption: only people at or above min_age shop online.
        df = df[df["R_AGE"] >= self.min_age].reset_index(drop=True)

        df["R_AGE_C"] = df["R_AGE"].apply(age_class)
        df["R_SEX_IMP"] = df["pgend"].apply(sex_class)
        df["R_RACE"] = df["prace"].apply(race_class_daysim)
        df["WORKER"] = df["pwtyp"].apply(worker_class_daysim)
        # pstyp: 0 = non-student, 1 = full time, 2 = part time student.
        df["SCHTYP"] = (df["pstyp"] > 0).astype(int)

        # DaySim carries no educational attainment; see impute_education.
        print("  imputing education (not present in the DaySim population)")
        df["EDUC"] = impute_education(df["R_AGE"].to_numpy(),
                                      self.education_distribution,
                                      self.rng)

        self.person = add_dummies(df, self.PER_CLASS_VARS,
                                  required_columns=self.REQUIRED_DUMMIES)


# ---------------------------------------------------------------------------
# E-commerce demand models
# ---------------------------------------------------------------------------
class EcomDemandModel:
    """Applies the estimated online-choice and delivery-frequency models.

    model_dir: str, folder holding the .sav files written by HH_ecom_model.py

    The three goods types are applied in a fixed order because each frequency
    model uses the previous one's output as a predictor:
    goods -> grocery (uses DELIV_GOOD) -> food (uses DELIV_GROC).
    """
    GOODS_TYPES = [
        {
            "name": "goods",
            "demand_col": "DELIV_GOOD",
            "choice_model": "online_choice_good.sav",
            "freq_model": "freq_good.sav",
            "freq_x_var": ["R_AGE", "HHSIZE", "WORKER",
                           "EDUC_1", "EDUC_2",
                           "income_cls_1", "income_cls_2", "income_cls_3",
                           "income_cls_4", "income_cls_5", "URBRUR"],
            "high_freq_resample": None,
        },
        {
            "name": "grocery",
            "demand_col": "DELIV_GROC",
            "choice_model": "online_choice_grc.sav",
            "freq_model": "freq_grc.sav",
            "freq_x_var": ["R_AGE", "HHSIZE", "WORKER",
                           "DELIV_GOOD", "URBRUR",
                           "income_cls_1", "income_cls_2", "income_cls_3",
                           "income_cls_4", "income_cls_5"],
            "high_freq_resample": (20, 40),
        },
        {
            "name": "food",
            "demand_col": "DELIV_FOOD",
            "choice_model": "online_choice_food.sav",
            "freq_model": "freq_food.sav",
            "freq_x_var": ["R_AGE", "HHSIZE", "WORKER", "R_SEX_IMP",
                           "DELIV_GROC", "URBRUR",
                           "income_cls_1", "income_cls_2", "income_cls_3",
                           "income_cls_4", "income_cls_5",
                           "URBRUR"],  # duplicated at estimation, see note above
            "high_freq_resample": (20, 40),
        },
    ]

    def __init__(self, model_dir=None):
        self.model_dir = model_dir
        self._cache = {}
        if not model_dir or not os.path.isdir(model_dir):
            raise FileNotFoundError(f"Model folder not provided or invalid: {model_dir}")

    def _load(self, filename):
        """Load a .sav model, caching it so repeated county runs read it once."""
        if filename not in self._cache:
            path = os.path.join(self.model_dir, filename)
            if not os.path.exists(path):
                raise FileNotFoundError(
                    f"Model file not found: {path}. Run HH_ecom_model.py to create it."
                )
            # Needed for models pickled under pandas 1.x; see the function.
            install_pandas_compat_shim()
            self._cache[filename] = joblib.load(path)
        return self._cache[filename]

    @staticmethod
    def _check_design_matrix(model, columns, filename):
        """Fail loudly if the column list no longer matches the fitted model.
        """
        fitted = list(model.params.index)
        if fitted != list(columns):
            raise ValueError(
                f"Design matrix mismatch for {filename}.\n"
                f"  model was fitted on : {fitted}\n"
                f"  this code requests  : {list(columns)}\n"
                f"Update freq_x_var in EcomDemandModel.GOODS_TYPES to match the "
                f"estimation script, or re-estimate the model."
            )

    @staticmethod
    def _predict(model, df, filename):
        """Predict by building the design matrix from the fitted term names.
        """
        terms = list(model.params.index)

        # Guard the assumption above: anything that is not a plain column
        # reference would need the formula machinery to evaluate.
        expressions = [t for t in terms
                       if t != "Intercept" and not t.replace("_", "").isalnum()]
        if expressions:
            raise ValueError(
                f"{filename} contains formula terms this loader cannot rebuild: "
                f"{expressions}. Re-estimate the model or restore its design_info."
            )

        missing = [t for t in terms if t != "Intercept" and t not in df.columns]
        if missing:
            raise KeyError(
                f"{filename} needs columns absent from the population table: {missing}"
            )

        # pd.concat rather than df[terms] so that a term repeated in the fitted
        # model (freq_food carries URBRUR twice) yields a repeated column.
        columns = []
        for term in terms:
            if term == "Intercept":
                columns.append(pd.Series(1.0, index=df.index, name="Intercept"))
            else:
                columns.append(df[term].astype(float))
        exog = pd.concat(columns, axis=1)

        return model.predict(exog, transform=False)

    def _apply_one(self, df, spec):
        """Run the online-choice then frequency model for one goods type."""
        name = spec["name"]
        demand_col = spec["demand_col"]
        print(f"  {name}: online choice")

        choice_model = self._load(spec["choice_model"])
        probability = self._predict(choice_model, df, spec["choice_model"])
        shopper = pd.Series(probability, index=df.index).apply(
            lambda p: 1 if random.uniform(0, 1) < p else 0)

        shoppers = df[shopper == 1].reset_index(drop=True)
        print(f"  {name}: {len(shoppers):,} online shoppers "
              f"({len(shoppers) / max(len(df), 1):.1%})")

        if shoppers.empty:
            df[demand_col] = 0.0
            return df

        print(f"  {name}: delivery frequency")
        freq_model = self._load(spec["freq_model"])
        self._check_design_matrix(freq_model, spec["freq_x_var"], spec["freq_model"])
        shoppers[demand_col] = np.asarray(
            self._predict(freq_model, shoppers, spec["freq_model"])).round()

        # Long right tail: resample very frequent deliverers into a plausible
        # range rather than letting the negative binomial extrapolate.
        resample = spec["high_freq_resample"]
        if resample:
            low, high = resample
            shoppers[demand_col] = shoppers[demand_col].apply(
                lambda x: random.randrange(low, high) if x >= low else x)

        df = df.merge(shoppers[["household_id", "member_id", demand_col]],
                      on=["household_id", "member_id"], how="left")
        df[demand_col] = df[demand_col].fillna(0)
        return df

    def predict(self, person):
        """Return the person table with DELIV_GOOD, DELIV_GROC and DELIV_FOOD.
        """
        df = person
        for spec in self.GOODS_TYPES:
            df = self._apply_one(df, spec)
        return df


# %%
