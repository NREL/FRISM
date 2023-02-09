# %%
from tkinter import X
import pandas as pd
import numpy as np
import joblib
from argparse import ArgumentParser
import config
import random

import statsmodels.api as sm
from sklearn.linear_model import LogisticRegression
import seaborn as sns
import matplotlib.pyplot as plt

import biogeme.database as db
import biogeme.biogeme as bio
from biogeme import models
import biogeme.messaging as msg
from biogeme.expressions import Beta, DefineVariable
import biogeme.results as res
from statsmodels.stats.weightstats import DescrStatsW

def input_files_processing_hh(household_file):
    # Household data processing
    # Read Synthetic household file
    ## variables
    ### household_id      int64
    ### serialno        float64
    ### persons           int64
    ### cars              int64
    ### income            int64
    ### race_of_head      int64
    ### age_of_head       int64
    ### workers           int64
    ### children          int64
    ### tenure            int64
    ### recent_mover      int64
    ### block_id          int64
    synth_hh = pd.read_csv(household_file, header=0, sep=',')
    # Covert variable names to ones used in the model
    # Those are only variables that we can get from Synth pop (need to check any update?)
    ## Thus, for the simulation, we need to use the following variable for model estimation, which is a limitation.   
    synth_hh = synth_hh.rename({"persons": 'HHSIZE',       
                        "cars":'HHVEHCNT',                  
                        "race_of_head": 'HH_RACE',       
                        "workers": 'WRKCOUNT',
                        "tenure": 'HOMEOWN'}  , axis='columns')

    # Process variables using function         
    synth_hh['income_val']= synth_hh['income']/100000
    synth_hh['income_cls']= synth_hh['income'].apply(income_num2group)
    synth_hh['HH_RACE']=synth_hh['HH_RACE'].apply(race_class_synth)
    synth_hh['HOMEOWN']=synth_hh['HOMEOWN'].apply(home_class)

    # list of variables that have class
    ## Need to update!!, if functions change used in "Process variables using function"  
    Class_vars= ['HH_RACE','HOMEOWN','income_cls'] 

    # Create class variables that has more than two classes
    cat_vars=[]
    for var_c in Class_vars:
        if synth_hh[var_c].unique().size >2:
            cat_vars.append(var_c)
    for var in cat_vars:
        cat_list='var'+'_'+var
        cat_list = pd.get_dummies(synth_hh[var], prefix=var)
        synth_hh=synth_hh.join(cat_list)
    data_vars=synth_hh.columns.values.tolist()
    #to_keep=[i for i in data_vars if i not in cat_vars]
    #synth_hh=synth_hh[to_keep]

    return synth_hh

def input_files_processing_per(df_hh, person_file, msacat, census_r):
    # porcessed df with web estimation
    synth_hh = df_hh
    # personal data processing
    # Read NHTS person data
    ## variables
    ### person_id       int64
    ### age             int64
    ### earning         int64
    ### edu             int64
    ### hours           int64
    ### household_id    int64
    ### member_id       int64
    ### race_id         int64
    ### relate          int64
    ### sex             int64
    ### student         int64
    ### work_at_home    int64
    ### worker          int64
    synth_per = pd.read_csv(person_file, header=0, sep=',')

    # Covert variable names to ones used in the model
    # Those are only variables that we can get from Synth pop (need to check any update?)
    ## Thus, for the simulation, we need to use the following variable for model estimation, which is a limitation.   
    synth_per = synth_per.rename({"age": 'R_AGE_IMP',       
                        "edu":'EDUC',         
                        "race_id": 'R_RACE',         
                        "sex": 'R_SEX_IMP',       
                        "student": 'SCHTYP',
                        "work_at_home": 'WRK_HOME',
                        "worker": 'WORKER' }  , axis='columns')


    # Add household info      
    synth_per = synth_per.merge(synth_hh, on='household_id', how='inner')
    # Select records with age>16 with assumption that person>16 years old can do online shopping
    synth_per = synth_per[synth_per['R_AGE_IMP']>=16]           

    # Process variables using function         
    synth_per['EDUC']=synth_per['EDUC'].apply(edu_class_synth)
    synth_per['R_AGE_IMP']=synth_per['R_AGE_IMP'].apply(age_est)
    synth_per['R_RACE']=synth_per['R_RACE'].apply(race_class_synth)
    synth_per['R_SEX_IMP']=synth_per['R_SEX_IMP'].apply(sex_class)     

    # list of variables that have class
    ## Need to update!!, if functions change used in "Process variables using function"  
    Class_vars= ['EDUC','SCHTYP','WRK_HOME', 'WORKER','R_AGE_IMP','R_RACE', 'R_SEX_IMP'] 

    # Create class variables that has more than two classes
    cat_vars=[]
    for var_c in Class_vars:
        if synth_per[var_c].unique().size >2:
            cat_vars.append(var_c)
    for var in cat_vars:
        cat_list='var'+'_'+var
        cat_list = pd.get_dummies(synth_per[var], prefix=var)
        synth_per=synth_per.join(cat_list)
    #data_vars=synth_per.columns.values.tolist()
    #to_keep=[i for i in data_vars if i not in cat_vars]
    #synth_per=synth_per[to_keep]
    synth_per["MSACAT"]=msacat

    synth_per["CENSUS_R_1"]=0
    synth_per["CENSUS_R_2"]=0
    synth_per["CENSUS_R_3"]=0
    synth_per["CENSUS_R_4"]=0

    if census_r==1:
        synth_per["CENSUS_R_1"]=1
    elif census_r==2:
        synth_per["CENSUS_R_2"]=1
    elif census_r==3:   
        synth_per["CENSUS_R_3"]=1
    elif census_r==4:       
        synth_per["CENSUS_R_4"]=1
    synth_per = synth_per [["SCHTYP",
                "EDUC",
                "R_SEX_IMP",
                "work_zone_id",
                "school_zone_id",
                "member_id",
                "R_AGE_IMP",
                "WORKER",
                "R_RACE",
                "household_id",
                "WRK_HOME",
                "income",
                "lcm_county_id",
                "age_of_head",
                "block_id",
                "HHVEHCNT",
                "WRKCOUNT",
                "HH_RACE",
                "HOMEOWN",
                "HHSIZE",
                "income_val",
                "income_cls",
                "HH_RACE_0",
                "HH_RACE_1",
                "HH_RACE_2",
                "HH_RACE_3",
                "income_cls_0",
                "income_cls_1",
                "income_cls_2",
                "income_cls_3",
                "EDUC_0",
                "EDUC_1",
                "EDUC_2",
                "EDUC_3",
                "R_AGE_IMP_0",
                "R_AGE_IMP_1",
                "R_AGE_IMP_2",
                "R_AGE_IMP_3",
                "R_RACE_0",
                "R_RACE_1",
                "R_RACE_2",
                "R_RACE_3",
                "MSACAT",
                "CENSUS_R_1",
                "CENSUS_R_2",
                "CENSUS_R_3",
                "CENSUS_R_4"]]

    return synth_per


# Covert income group to estimated value: Synth household/population have values not group
## NHTS code:
### 01=Less than $10,000
### 02=$10,000 to $14,999
### 03=$15,000 to $24,999
### 04=$25,000 to $34,999
### 05=$35,000 to $49,999
### 06=$50,000 to $74,999
### 07=$75,000 to $99,999
### 08=$100,000 to $124,999
### 09=$125,000 to $149,999
### 10=$150,000 to $199,999
### 11=$200,000 or more
def income_est(HHFAMINC):
    if HHFAMINC == 1:
        est_income= np.random.randint(0,10000)
    elif HHFAMINC == 2:
        est_income= np.random.randint(10000,14999)
    elif HHFAMINC == 3:
        est_income= np.random.randint(15000,24999)
    elif HHFAMINC == 4:
        est_income= np.random.randint(25000,34999)
    elif HHFAMINC == 5:
        est_income= np.random.randint(35000,49999)
    elif HHFAMINC == 6:
        est_income= np.random.randint(50000,74999)
    elif HHFAMINC == 7:
        est_income= np.random.randint(75000,99999)
    elif HHFAMINC == 8:
        est_income= np.random.randint(100000,124999)
    elif HHFAMINC == 9:
        est_income= np.random.randint(125000,149999)
    elif HHFAMINC == 10:
        est_income= np.random.randint(150000,199999)
    elif HHFAMINC == 11:
        est_income= np.random.randint(200000,500000)
    return est_income/100000
# Aggregate income gorup
def income_group(HHFAMINC):
    if HHFAMINC in [1,2,3,4]: # 35000
        return 0
    elif HHFAMINC in [4,5,6]: # 35000~75000
        return 1
    elif HHFAMINC in [7,8]: # 75000~125000
        return 2
    elif HHFAMINC in [9,10,11]: # 125000~
        return 3    
# Aggregate income gorup from the number for synthfirm
def income_num2group(HHFAMINC):
    if HHFAMINC < 35000:
        return 0
    elif HHFAMINC >= 35000 and HHFAMINC <75000:
        return 1
    elif HHFAMINC >=75000 and HHFAMINC <125000:
        return 2
    elif HHFAMINC >=125000:
        return 3         

# Convert web use class to three classes
## NHTS code:
### 01=Daily
### 02=A few times a week
### 03=A few times a month
### 04=A few times a year
### 05=Never
## Model Variable: 0:never use, 1: frequent use, 2: often use 
def web_class(WEBUSE17):
    if WEBUSE17 in [1]: 
        return 1 # frequenct use (more than a few time a week)
    elif WEBUSE17 in [2,3,4]:
        return 2 # often use (more than a few times a year)
    else:
        return 0 # (never)

# Convert race class to four classes
## NHTS code:
### 01=White
### 02=Black or African American
### 03=Asian
### 04=American Indian or Alaska Native
### 05=Native Hawaiian or other Pacific Islander
### 06=Multiple responses selected
### 97=Some other race
## Model Variable: 1:white, 2:black, 3: asian; 0:others
def race_class(HH_RACE):
    if HH_RACE == 1: 
        return 1 # white
    elif HH_RACE == 2:
        return 2 # black
    elif HH_RACE == 3:
        return 3 # Asian
    else:
        return 0 # others

def race_class_synth(HH_RACE):
    if HH_RACE == 1: 
        return 1 # white
    elif HH_RACE == 2:
        return 2 # black
    elif HH_RACE == 6:
        return 3 # Asian
    else:
        return 0 # others


# Convert house ownership type to two classes
## NHTS code:
### 01=Own
### 02=Rent
### 97=Some other arrangement
## Model Variable: 0: others, 1: own
def home_class(HOMEOWN):
    if HOMEOWN == 1: 
        return 1
    else:
        return 0


# Convert "Hispanic status of household respondent" to two classes
## NHTS code:
### 01=Yes
### 02=No
## Model Variable: 0: non_his, 1: hispenic
def hisp_class(HH_HISP):
    if HH_HISP == 1: 
        return 1
    else:
        return 0 

# Convert "Life Cycle classification" to two classes 
## NHTS code:
### 01=one adult, no children
### 02=2+ adults, no children
### 03=one adult, youngest child 0-5
### 04=2+ adults, youngest child 0-5
### 05=one adult, youngest child 6-15
### 06=2+ adults, youngest child 6-15
### 07=one adult, youngest child 16-21
### 08=2+ adults, youngest child 16-21
### 09=one adult, retired, no children
### 10=2+ adults, retired, no children
## Model Variable: 0: adult only, 1: retired without kids, 2:single parent with kid, 3: parent with kid 
def child_class(LIF_CYC):
    if LIF_CYC in [1,2]: 
        return 0 # adult only
    elif LIF_CYC in [9,10]:
        return 1 # retired 
    elif LIF_CYC in [3,5,7]:
        return 2 # single parent
    elif LIF_CYC in [4,6,8]:
        return 3 # two parent

# Convert education to four classes (person)
## NHTS code:
### -1=Appropriate skip
### 01=Less than a high school graduate
### 02=High school graduate or GED
### 03=Some college or associates degree
### 04=Bachelor's degree
### 05=Graduate degree or professional degree
## Model Variable: 0: not applicable +low hc, 1:hc, 2:BA+college, 3: MS+
def edu_class(EDUC):
    if EDUC in [-1, 1]:
        return 0
    elif EDUC in [2]:
        return 1
    elif EDUC in [3,4]:
        return 2    
    elif EDUC in [5]:
        return 3   

# Convert student status to two classes (person)
## NHTS code
### -1=Appropriate skip
### 01=Public or private school
### 02=Home schooled
### 03=Not in school
## Model Variable: 1: student, 2: no 
def student_class(SCHTYP):
    if SCHTYP in [1, 2]:
        return 1
    else:
        return 0 
# Convert worker' work from home to two classes (person)
## NHTS code
### -1=Appropriate skip
### 01=Yes
### 02=No
## Model Variable 1: work from home, 0: no work from home
def wfh_class(WRK_HOME):
    if WRK_HOME in [1]: 
        return 1
    else:
        return 0  
# Convert worker' work to two classes (person)
## NHTS code
### -1=Appropriate skip
### 01=Yes
### 02=No
## Model Variable: 1: work, 0: no work
def work_class(WORKER):
    if WORKER in [1]: 
        return 1
    else:
        return 0
# Convert age to four classes (person)
## NHTS code
## Model Variable
def age_est(R_AGE_IMP):
    if R_AGE_IMP  <=25 :
        return 0
    elif R_AGE_IMP  >25 and R_AGE_IMP  <=40:
        return 1
    elif R_AGE_IMP  >40 and R_AGE_IMP  <=60:
        return 2
    elif R_AGE_IMP  >60:
        return 3
# Convert sex to two classes (person)
## NHTS code
### 01=Male
### 02=Female
## Model Variable: 1: male, 0: female
def sex_class(R_SEX_IMP):
    if R_SEX_IMP in [1]: 
        return 1
    else:
        return 0        

# Convert work mode to four classes (person)
## NHTS code
## Model Variable: 0: not applicalbe, 1: personal car, 2: public, 3: walk+bike, 4: others  
def mode_est(WRKTRANS):
    if WRKTRANS  in [3,4,5,6,18]:
        return 1
    elif WRKTRANS  in [10,11,12,13,14,15,16,17]:
        return 2
    elif  WRKTRANS  in [1,2]:
        return 3
    else :
        return 0

# Convert delivery to two classes (person)
## NHTS code
## Model Variable
def onlineshop_class(DELIVER):
    if DELIVER  > 0: 
        return 1
    else:
        return 0

def edu_class_synth(EDUC):
    if EDUC <16 :
        return 0
    elif EDUC ==16:
        return 1
    elif EDUC >16 and EDUC <=21:
        return 2
    else:
        return 3

# def delivery_process(online_choice, delivery, income_cl):
#     if online_choice ==0:
#         final_delivery=0
#     elif online_choice ==1:
#         if delivery <=1:
#             final_delivery =1
#         elif delivery >1 and delivery <80:
#             final_delivery = round(delivery-0.5)
#         elif delivery >=80:
#             final_delivery = random.randrange (60,80,1)
#     return final_delivery

# def onlineshop_calibration(income_cl, online_choice):
#     if income_cl ==0:
#         if online_choice ==0:
#             if random.uniform(0,1) <0.57:
#                 return online_choice
#             else:
#                 return 1
#         else:
#             return online_choice        
#     elif income_cl ==1:
#         if online_choice ==0:
#             if random.uniform(0,1) <0.68:
#                 return online_choice
#             else:
#                 return 1
#         else:
#             return online_choice
#     elif income_cl ==2:
#         return online_choice
#     elif income_cl==3:
#         return online_choice                  

def delivery_process(online_choice, delivery, income_cl):
    if online_choice ==0:
        final_delivery=0
    elif online_choice ==1:
        if income_cl==2 :
            if delivery <=2.5:
                final_delivery =1
            elif delivery >2.5: #and delivery <20:
                final_delivery = round(delivery-2)
            #elif delivery >=20:
            #    final_delivery = random.randrange (15,60,1)
        elif income_cl==3 :
            if delivery <=2.5:
                final_delivery =1
            elif delivery >2.5: #and delivery <20:
                if random.uniform(0,1) <0.85:
                    final_delivery = round(delivery-0.8)
                else:
                    final_delivery = random.randrange (5,40,5)         
            #elif delivery >=20:
            #    final_delivery = random.randrange (15,60,1)
        elif income_cl==1 :
            if delivery <=1.5:
                final_delivery =1
            elif delivery >1.5: #and delivery <20:
                final_delivery = round(delivery-1.5)
            #elif delivery >=20:
            #    final_delivery = random.randrange (15,60,1)             
        elif income_cl==0 :     
            if delivery <=1.5:
                final_delivery =1
            elif delivery >1.5 and delivery <20:
                final_delivery = round(delivery-2)
            elif delivery >=20:
                final_delivery = random.randrange (15,60,1)
    return final_delivery

def onlineshop_calibration(income_cl, online_choice):
    if income_cl ==0:
        if online_choice ==0:
            if random.uniform(0,1) <0.56:
                return online_choice
            else:
                return 1
        else:
            return online_choice
    # elif income_cl ==1:
    #     return online_choice                 
    elif income_cl ==1:
        if online_choice ==0:
            if random.uniform(0,1) <0.85:
                return online_choice
            else:
                return 1
        else:
            return online_choice
    elif income_cl ==2:
        if online_choice ==1:
            if random.uniform(0,1) <0.85:
                return online_choice
            else:
                return 0
        else:
            return online_choice 
    elif income_cl==3:
        if online_choice ==1:
            if random.uniform(0,1) <0.68:
                return online_choice
            else:
                return 0
        else:
            return online_choice                   


# %%
def main(args=None):
    # read input files
    parser = ArgumentParser()
    parser.add_argument("-hf", "--household_file", dest="hh_file",
                        help="household file in csv format", required=True, type=str)
    parser.add_argument("-pf", "--person_file", dest="per_file",
                        help="person file in csv format", required=True, type=str)                         
    args = parser.parse_args()
    # %%
    # need to comment after testing
    temp_hh_file="../../../FRISM_input_output_AT/Sim_inputs/austin_2018/households.csv.zip"
    temp_per_file="../../../FRISM_input_output_AT/Sim_inputs/austin_2018/persons.csv.zip"
    
    # Read and process synth household
    #df_hh = input_files_processing_hh(args.hh_file)
    df_hh = input_files_processing_hh(temp_hh_file)
    # Read and process synth household
    #df_per= input_files_processing_per(df_hh, args.per_file)
    df_per= input_files_processing_per(df_hh, temp_per_file, config.msacat, config.census_r)
    # %%
############################################# Model Simulation  ################################
    database = db.Database('shop', df_per)

    # The following statement allows you to use the names of the
    # variable as Python variable.
    globals().update(database.variables)

    # Parameters to be estimated
    ## Intercept
    ASC_NOS = Beta('ASC_NOS', 0, None, None, 1)
    ASC_LOW = Beta('ASC_LOW', 0, None, None, 0)
    ASC_MID = Beta('ASC_MID', 0, None, None, 0)
    ASC_HIG = Beta('ASC_HIG', 0, None, None, 0)
    ## Beta
    B_SEX_V0= Beta('B_SEX_V0', 0, None, None, 1)
    B_SEX_V1= Beta('B_SEX_V1', 0, None, None, 0)
    B_SEX_V2= Beta('B_SEX_V2', 0, None, None, 0)
    B_SEX_V3= Beta('B_SEX_V3', 0, None, None, 0)

    ## Beta
    B_INC_V0= Beta('B_INC_V0', 0, None, None, 1)
    B_INC_V1= Beta('B_INC_V1', 0, None, None, 0)
    B_INC_V2= Beta('B_INC_V2', 0, None, None, 0)
    B_INC_V3= Beta('B_INC_V3', 0, None, None, 0)
    ###
    B_HHSIZE_V0= Beta('B_HHSIZE_V0', 0, None, None, 1)
    B_HHSIZE_V1= Beta('B_HHSIZE_V1', 0, None, None, 0)
    B_HHSIZE_V2= Beta('B_HHSIZE_V2', 0, None, None, 0)
    B_HHSIZE_V3= Beta('B_HHSIZE_V3', 0, None, None, 0)
    ###
    B_WORKER_V0= Beta('B_WORKER_V0', 0, None, None, 1)
    B_WORKER_V1= Beta('B_WORKER_V1', 0, None, None, 0)
    B_WORKER_V2= Beta('B_WORKER_V2', 0, None, None, 0)
    B_WORKER_V3= Beta('B_WORKER_V3', 0, None, None, 0)

    ###
    B_MSACAT_V0= Beta('B_MSACAT_V0', 0, None, None, 1)
    B_MSACAT_V1= Beta('B_MSACAT_V1', 0, None, None, 0)
    B_MSACAT_V2= Beta('B_MSACAT_V2', 0, None, None, 0)
    B_MSACAT_V3= Beta('B_MSACAT_V3', 0, None, None, 0)
    ###
    B_EDUC_1_V0= Beta('B_EDUC_1_V0', 0, None, None, 1)
    B_EDUC_1_V1= Beta('B_EDUC_1_V1', 0, None, None, 0)
    B_EDUC_1_V2= Beta('B_EDUC_1_V2', 0, None, None, 0)
    B_EDUC_1_V3= Beta('B_EDUC_1_V3', 0, None, None, 0)
    ###
    B_EDUC_2_V0= Beta('B_EDUC_2_V0', 0, None, None, 1)
    B_EDUC_2_V1= Beta('B_EDUC_2_V1', 0, None, None, 0)
    B_EDUC_2_V2= Beta('B_EDUC_2_V2', 0, None, None, 0)
    B_EDUC_2_V3= Beta('B_EDUC_2_V3', 0, None, None, 0)
    ###
    B_EDUC_3_V0= Beta('B_EDUC_3_V0', 0, None, None, 1)
    B_EDUC_3_V1= Beta('B_EDUC_3_V1', 0, None, None, 0)
    B_EDUC_3_V2= Beta('B_EDUC_3_V2', 0, None, None, 0)
    B_EDUC_3_V3= Beta('B_EDUC_3_V3', 0, None, None, 0)

    ###
    B_AGE_IMP_1_V0= Beta('B_AGE_IMP_1_V0', 0, None, None, 1)
    B_AGE_IMP_1_V1= Beta('B_AGE_IMP_1_V1', 0, None, None, 0)
    B_AGE_IMP_1_V2= Beta('B_AGE_IMP_1_V2', 0, None, None, 0)
    B_AGE_IMP_1_V3= Beta('B_AGE_IMP_1_V3', 0, None, None, 0)

    ###
    B_AGE_IMP_2_V0= Beta('B_AGE_IMP_2_V0', 0, None, None, 1)
    B_AGE_IMP_2_V1= Beta('B_AGE_IMP_2_V1', 0, None, None, 0)
    B_AGE_IMP_2_V2= Beta('B_AGE_IMP_2_V2', 0, None, None, 0)
    B_AGE_IMP_2_V3= Beta('B_AGE_IMP_2_V3', 0, None, None, 0)
    ###
    B_AGE_IMP_3_V0= Beta('B_AGE_IMP_3_V0', 0, None, None, 1)
    B_AGE_IMP_3_V1= Beta('B_AGE_IMP_3_V1', 0, None, None, 0)
    B_AGE_IMP_3_V2= Beta('B_AGE_IMP_3_V2', 0, None, None, 0)
    B_AGE_IMP_3_V3= Beta('B_AGE_IMP_3_V3', 0, None, None, 0)
    ###
    ###
    B_RACE_1_V0= Beta('B_RACE_1_V0', 0, None, None, 1)
    B_RACE_1_V1= Beta('B_RACE_1_V1', 0, None, None, 0)
    B_RACE_1_V2= Beta('B_RACE_1_V2', 0, None, None, 0)
    B_RACE_1_V3= Beta('B_RACE_1_V3', 0, None, None, 0)

    ###
    B_RACE_2_V0= Beta('B_RACE_2_V0', 0, None, None, 1)
    B_RACE_2_V1= Beta('B_RACE_2_V1', 0, None, None, 0)
    B_RACE_2_V2= Beta('B_RACE_2_V2', 0, None, None, 0)
    B_RACE_2_V3= Beta('B_RACE_2_V3', 0, None, None, 0)
    ###
    B_RACE_3_V0= Beta('B_RACE_3_V0', 0, None, None, 1)
    B_RACE_3_V1= Beta('B_RACE_3_V1', 0, None, None, 0)
    B_RACE_3_V2= Beta('B_RACE_3_V2', 0, None, None, 0)
    B_RACE_3_V3= Beta('B_RACE_3_V3', 0, None, None, 0)

    ###
    B_CENSUS_R_2_V0= Beta('B_CENSUS_R_2_V0', 0, None, None, 1)
    B_CENSUS_R_2_V1= Beta('B_CENSUS_R_2_V1', 0, None, None, 0)
    B_CENSUS_R_2_V2= Beta('B_CENSUS_R_2_V2', 0, None, None, 0)
    B_CENSUS_R_2_V3= Beta('B_CENSUS_R_2_V3', 0, None, None, 0)
    ###
    B_CENSUS_R_3_V0= Beta('B_CENSUS_R_3_V0', 0, None, None, 1)
    B_CENSUS_R_3_V1= Beta('B_CENSUS_R_3_V1', 0, None, None, 0)
    B_CENSUS_R_3_V2= Beta('B_CENSUS_R_3_V2', 0, None, None, 0)
    B_CENSUS_R_3_V3= Beta('B_CENSUS_R_3_V3', 0, None, None, 0)
    ##
    B_CENSUS_R_4_V0= Beta('B_CENSUS_R_4_V0', 0, None, None, 1)
    B_CENSUS_R_4_V1= Beta('B_CENSUS_R_4_V1', 0, None, None, 0)
    B_CENSUS_R_4_V2= Beta('B_CENSUS_R_4_V2', 0, None, None, 0)
    B_CENSUS_R_4_V3= Beta('B_CENSUS_R_4_V3', 0, None, None, 0)


    # Definition of the utility functions
    V0 = ASC_NOS + B_SEX_V0 * R_SEX_IMP + B_HHSIZE_V0 * HHSIZE + B_WORKER_V0 *WORKER + B_EDUC_1_V0 *EDUC_1 + B_EDUC_2_V0 *EDUC_2 + B_EDUC_3_V0 *EDUC_3 + B_AGE_IMP_1_V0 *R_AGE_IMP_1+ B_AGE_IMP_2_V0 *R_AGE_IMP_2+B_AGE_IMP_3_V0 *R_AGE_IMP_3+\
    B_RACE_1_V0 *R_RACE_1+B_RACE_2_V0 *R_RACE_2 +B_CENSUS_R_2_V0 *CENSUS_R_2 +B_CENSUS_R_3_V0 *CENSUS_R_3+B_CENSUS_R_4_V0 *CENSUS_R_4 +B_MSACAT_V0 *MSACAT + B_INC_V0 * income_val
    V1 = ASC_LOW + B_SEX_V1 * R_SEX_IMP + B_HHSIZE_V1 * HHSIZE + B_WORKER_V1 *WORKER + B_EDUC_1_V1 *EDUC_1 + B_EDUC_2_V1 *EDUC_2 + B_EDUC_3_V1 *EDUC_3 + B_AGE_IMP_1_V1 *R_AGE_IMP_1+ B_AGE_IMP_2_V1 *R_AGE_IMP_2+B_AGE_IMP_3_V1 *R_AGE_IMP_3+\
    B_RACE_1_V1 *R_RACE_1+B_RACE_2_V1 *R_RACE_2+B_CENSUS_R_2_V1 *CENSUS_R_2 +B_CENSUS_R_3_V1 *CENSUS_R_3+B_CENSUS_R_4_V1 *CENSUS_R_4 +B_MSACAT_V1 *MSACAT + B_INC_V1 * income_val
    V2 = ASC_MID + B_SEX_V2 * R_SEX_IMP + B_HHSIZE_V2 * HHSIZE + B_WORKER_V2 *WORKER + B_EDUC_1_V2 *EDUC_1 + B_EDUC_2_V2 *EDUC_2 + B_EDUC_3_V2 *EDUC_3 + B_AGE_IMP_1_V2 *R_AGE_IMP_1+ B_AGE_IMP_2_V2 *R_AGE_IMP_2+B_AGE_IMP_3_V2 *R_AGE_IMP_3+\
    B_RACE_1_V2 *R_RACE_1+B_RACE_2_V2 *R_RACE_2 +B_CENSUS_R_2_V2 *CENSUS_R_2 +B_CENSUS_R_3_V2 *CENSUS_R_3+B_CENSUS_R_4_V2 *CENSUS_R_4 +B_MSACAT_V2 *MSACAT + B_INC_V2 * income_val
    V3 = ASC_HIG + B_SEX_V3 * R_SEX_IMP + B_HHSIZE_V3 * HHSIZE + B_WORKER_V3 *WORKER + B_EDUC_1_V3 *EDUC_1 + B_EDUC_2_V3 *EDUC_2 + B_EDUC_3_V3 *EDUC_3 + B_AGE_IMP_1_V3 *R_AGE_IMP_1+ B_AGE_IMP_2_V3 *R_AGE_IMP_2+B_AGE_IMP_3_V3 *R_AGE_IMP_3+\
    B_RACE_1_V3 *R_RACE_1+B_RACE_2_V3 *R_RACE_2 +B_CENSUS_R_2_V3 *CENSUS_R_2 +B_CENSUS_R_3_V3 *CENSUS_R_3+B_CENSUS_R_4_V3 *CENSUS_R_4 +B_MSACAT_V3 *MSACAT+ B_INC_V3 * income_val
    # Associate utility functions with the numbering of alternatives
    # Associate utility functions with the numbering of alternatives
    V = {0: V0,1: V1, 2: V2, 3: V3}

    # Associate the availability conditions with the alternatives
    av = {0: 1, 1: 1, 2: 1, 3: 1}
    # The choice model is a logit, with availability conditions
    prob0 = models.logit(V, av, 0)
    prob1 = models.logit(V, av, 1)
    prob2 = models.logit(V, av, 2)
    prob3 = models.logit(V, av, 3)

    simulate = {
        'Prob_no': prob0,
        'Prob_lo': prob1,
        'Prob_md': prob2,
        'Prob_hi': prob3,
    }

    online_results = res.bioResults(pickleFile = 'onine_shop_logit_con.pickle')

    biogeme = bio.BIOGEME(database, simulate)
    biogeme.modelName = 'onlineshop_simul'

    online_sim_results = biogeme.simulate(online_results.getBetaValues())
    print(online_sim_results.describe())

    df_per['Prob_no']=online_sim_results['Prob_no']*10
    df_per['Prob_lo']=online_sim_results['Prob_lo']*10
    df_per['Prob_md']=online_sim_results['Prob_md']*10
    df_per['Prob_hi']=online_sim_results['Prob_hi']*10

    ############################################# general Model simulation ################################
    # %%
    ## shopping nested 
    database = db.Database('shop', df_per)

    # The following statement allows you to use the names of the
    # variable as Python variable.
    globals().update(database.variables)

    # Parameters to be estimated
    ## Intercept
    ASC_NOS = Beta('ASC_NOS', 0, None, None, 1)
    ASC_OFF = Beta('ASC_OFF', 0, None, None, 0)
    ASC_ONS = Beta('ASC_ONS', 0, None, None, 0)
    ASC_BOT = Beta('ASC_BOT', 0, None, None, 0)
    ## Beta
    B_SEX_V0= Beta('B_SEX_V0', 0, None, None, 1)
    B_SEX_V1= Beta('B_SEX_V1', 0, None, None, 0)
    B_SEX_V2= Beta('B_SEX_V2', 0, None, None, 0)
    B_SEX_V3= Beta('B_SEX_V3', 0, None, None, 0)

    ## Beta
    B_INC_V0= Beta('B_INC_V0', 0, None, None, 1)
    B_INC_V1= Beta('B_INC_V1', 0, None, None, 0)
    B_INC_V2= Beta('B_INC_V2', 0, None, None, 0)
    B_INC_V3= Beta('B_INC_V3', 0, None, None, 0)
    ###
    B_HHSIZE_V0= Beta('B_HHSIZE_V0', 0, None, None, 1)
    B_HHSIZE_V1= Beta('B_HHSIZE_V1', 0, None, None, 0)
    B_HHSIZE_V2= Beta('B_HHSIZE_V2', 0, None, None, 0)
    B_HHSIZE_V3= Beta('B_HHSIZE_V3', 0, None, None, 0)
    ###
    B_WORKER_V0= Beta('B_WORKER_V0', 0, None, None, 1)
    B_WORKER_V1= Beta('B_WORKER_V1', 0, None, None, 0)
    B_WORKER_V2= Beta('B_WORKER_V2', 0, None, None, 0)
    B_WORKER_V3= Beta('B_WORKER_V3', 0, None, None, 0)

    ###
    B_MSACAT_V0= Beta('B_MSACAT_V0', 0, None, None, 1)
    B_MSACAT_V1= Beta('B_MSACAT_V1', 0, None, None, 0)
    B_MSACAT_V2= Beta('B_MSACAT_V2', 0, None, None, 0)
    B_MSACAT_V3= Beta('B_MSACAT_V3', 0, None, None, 0)
    ###
    B_EDUC_0_V0= Beta('B_EDUC_0_V0', 0, None, None, 1)
    B_EDUC_0_V1= Beta('B_EDUC_0_V1', 0, None, None, 0)
    B_EDUC_0_V2= Beta('B_EDUC_0_V2', 0, None, None, 0)
    B_EDUC_0_V3= Beta('B_EDUC_0_V3', 0, None, None, 0)
    ###
    B_EDUC_1_V0= Beta('B_EDUC_1_V0', 0, None, None, 1)
    B_EDUC_1_V1= Beta('B_EDUC_1_V1', 0, None, None, 0)
    B_EDUC_1_V2= Beta('B_EDUC_1_V2', 0, None, None, 0)
    B_EDUC_1_V3= Beta('B_EDUC_1_V3', 0, None, None, 0)
    ###
    B_EDUC_2_V0= Beta('B_EDUC_2_V0', 0, None, None, 1)
    B_EDUC_2_V1= Beta('B_EDUC_2_V1', 0, None, None, 0)
    B_EDUC_2_V2= Beta('B_EDUC_2_V2', 0, None, None, 0)
    B_EDUC_2_V3= Beta('B_EDUC_2_V3', 0, None, None, 0)
    ###
    B_EDUC_3_V0= Beta('B_EDUC_3_V0', 0, None, None, 1)
    B_EDUC_3_V1= Beta('B_EDUC_3_V1', 0, None, None, 0)
    B_EDUC_3_V2= Beta('B_EDUC_3_V2', 0, None, None, 0)
    B_EDUC_3_V3= Beta('B_EDUC_3_V3', 0, None, None, 0)

    ###
    B_AGE_IMP_0_V0= Beta('B_AGE_IMP_0_V0', 0, None, None, 1)
    B_AGE_IMP_0_V1= Beta('B_AGE_IMP_0_V1', 0, None, None, 0)
    B_AGE_IMP_0_V2= Beta('B_AGE_IMP_0_V2', 0, None, None, 0)
    B_AGE_IMP_0_V3= Beta('B_AGE_IMP_0_V3', 0, None, None, 0)

    ###
    B_AGE_IMP_1_V0= Beta('B_AGE_IMP_1_V0', 0, None, None, 1)
    B_AGE_IMP_1_V1= Beta('B_AGE_IMP_1_V1', 0, None, None, 0)
    B_AGE_IMP_1_V2= Beta('B_AGE_IMP_1_V2', 0, None, None, 0)
    B_AGE_IMP_1_V3= Beta('B_AGE_IMP_1_V3', 0, None, None, 0)

    ###
    B_AGE_IMP_2_V0= Beta('B_AGE_IMP_2_V0', 0, None, None, 1)
    B_AGE_IMP_2_V1= Beta('B_AGE_IMP_2_V1', 0, None, None, 0)
    B_AGE_IMP_2_V2= Beta('B_AGE_IMP_2_V2', 0, None, None, 0)
    B_AGE_IMP_2_V3= Beta('B_AGE_IMP_2_V3', 0, None, None, 0)
    ###
    B_AGE_IMP_3_V0= Beta('B_AGE_IMP_3_V0', 0, None, None, 1)
    B_AGE_IMP_3_V1= Beta('B_AGE_IMP_3_V1', 0, None, None, 0)
    B_AGE_IMP_3_V2= Beta('B_AGE_IMP_3_V2', 0, None, None, 0)
    B_AGE_IMP_3_V3= Beta('B_AGE_IMP_3_V3', 0, None, None, 0)
    ###
    ###
    B_RACE_1_V0= Beta('B_RACE_1_V0', 0, None, None, 1)
    B_RACE_1_V1= Beta('B_RACE_1_V1', 0, None, None, 0)
    B_RACE_1_V2= Beta('B_RACE_1_V2', 0, None, None, 0)
    B_RACE_1_V3= Beta('B_RACE_1_V3', 0, None, None, 0)

    ###
    B_RACE_2_V0= Beta('B_RACE_2_V0', 0, None, None, 1)
    B_RACE_2_V1= Beta('B_RACE_2_V1', 0, None, None, 0)
    B_RACE_2_V2= Beta('B_RACE_2_V2', 0, None, None, 0)
    B_RACE_2_V3= Beta('B_RACE_2_V3', 0, None, None, 0)
    ###
    B_RACE_3_V0= Beta('B_RACE_3_V0', 0, None, None, 1)
    B_RACE_3_V1= Beta('B_RACE_3_V1', 0, None, None, 0)
    B_RACE_3_V2= Beta('B_RACE_3_V2', 0, None, None, 0)
    B_RACE_3_V3= Beta('B_RACE_3_V3', 0, None, None, 0)

    ###
    B_CENSUS_R_2_V0= Beta('B_CENSUS_R_2_V0', 0, None, None, 1)
    B_CENSUS_R_2_V1= Beta('B_CENSUS_R_2_V1', 0, None, None, 0)
    B_CENSUS_R_2_V2= Beta('B_CENSUS_R_2_V2', 0, None, None, 0)
    B_CENSUS_R_2_V3= Beta('B_CENSUS_R_2_V3', 0, None, None, 0)
    ###
    B_CENSUS_R_3_V0= Beta('B_CENSUS_R_3_V0', 0, None, None, 1)
    B_CENSUS_R_3_V1= Beta('B_CENSUS_R_3_V1', 0, None, None, 0)
    B_CENSUS_R_3_V2= Beta('B_CENSUS_R_3_V2', 0, None, None, 0)
    B_CENSUS_R_3_V3= Beta('B_CENSUS_R_3_V3', 0, None, None, 0)
    ##
    B_CENSUS_R_4_V0= Beta('B_CENSUS_R_4_V0', 0, None, None, 1)
    B_CENSUS_R_4_V1= Beta('B_CENSUS_R_4_V1', 0, None, None, 0)
    B_CENSUS_R_4_V2= Beta('B_CENSUS_R_4_V2', 0, None, None, 0)
    B_CENSUS_R_4_V3= Beta('B_CENSUS_R_4_V3', 0, None, None, 0)

    ###
    #Prob_no_V0= Beta('Prob_no_V0', 0, None, None, 1)
    NO_V1= Beta('NO_V1', 0, None, None, 0)
    NO_V2= Beta('NO_V2', 0, None, None, 0)
    NO_V3= Beta('NO_V3', 0, None, None, 0)

    LO_V0= Beta('LO_V0', 0, None, None, 1)
    LO_V1= Beta('LO_V1', 0, None, None, 0)
    LO_V2= Beta('LO_V2', 0, None, None, 0)
    LO_V3= Beta('LO_V3', 0, None, None, 0)
    ###
    MD_V0= Beta('MD_V0', 0, None, None, 1)
    MD_V1= Beta('MD_V1', 0, None, None, 0)
    MD_V2= Beta('MD_V2', 0, None, None, 0)
    MD_V3= Beta('MD_V3', 0, None, None, 0)
    ##
    HI_V0= Beta('HI_V0', 0, None, None, 1)
    HI_V1= Beta('HI_V1', 0, None, None, 0)
    HI_V2= Beta('HI_V2', 0, None, None, 0)
    HI_V3= Beta('HI_V3', 0, None, None, 0)


    # Definition of the utility functions
    V0 = ASC_NOS + B_SEX_V0 * R_SEX_IMP + B_HHSIZE_V0 * HHSIZE + B_WORKER_V0 *WORKER + B_EDUC_0_V0 *EDUC_0 +B_AGE_IMP_3_V0 *R_AGE_IMP_3+\
    B_CENSUS_R_2_V0 *CENSUS_R_2 +B_CENSUS_R_3_V0 *CENSUS_R_3+B_CENSUS_R_4_V0 *CENSUS_R_4 +B_MSACAT_V0 *MSACAT + B_INC_V0 * income_val

    V1 = ASC_OFF+ B_SEX_V1 * R_SEX_IMP + B_HHSIZE_V1 * HHSIZE + B_WORKER_V1 *WORKER + B_EDUC_0_V1 *EDUC_0 +B_AGE_IMP_3_V1 *R_AGE_IMP_3+\
    B_CENSUS_R_2_V1 *CENSUS_R_2 +B_CENSUS_R_3_V1 *CENSUS_R_3+B_CENSUS_R_4_V1 *CENSUS_R_4 +B_MSACAT_V1 *MSACAT + B_INC_V1 * income_val+\
            NO_V1*Prob_no+LO_V1*Prob_lo+MD_V1*Prob_md  

    V2 = ASC_ONS + B_SEX_V2 * R_SEX_IMP + B_HHSIZE_V2 * HHSIZE + B_WORKER_V2 *WORKER + B_EDUC_0_V2 *EDUC_0 +B_AGE_IMP_3_V2 *R_AGE_IMP_3+\
    B_CENSUS_R_2_V2 *CENSUS_R_2 +B_CENSUS_R_3_V2 *CENSUS_R_3+B_CENSUS_R_4_V2 *CENSUS_R_4 +B_MSACAT_V2 *MSACAT + B_INC_V2 * income_val+\
            NO_V2*Prob_no+LO_V2*Prob_lo+MD_V2*Prob_md 

    V3 = ASC_BOT +B_SEX_V3 * R_SEX_IMP + B_HHSIZE_V3 * HHSIZE + B_WORKER_V3 *WORKER + B_EDUC_0_V3 *EDUC_0 +B_AGE_IMP_3_V3 *R_AGE_IMP_3+\
    B_CENSUS_R_2_V3 *CENSUS_R_2 +B_CENSUS_R_3_V3 *CENSUS_R_3+B_CENSUS_R_4_V3 *CENSUS_R_4 +B_MSACAT_V3 *MSACAT+ B_INC_V3 * income_val+\
            NO_V3*Prob_no+LO_V3*Prob_lo+MD_V3*Prob_md 

    # Associate utility functions with the numbering of alternatives
    # Associate utility functions with the numbering of alternatives
    V = {0: V0,1: V1, 2: V2, 3: V3}

    # Associate the availability conditions with the alternatives
    av = {0: 1, 1: 1, 2: 1, 3: 1}

    # nest parameters
    NEST_SHOP=Beta('NEST_SHOP',1,1.0,20,0)

    NO_SHOP =1.0, [0]
    SHOP=NEST_SHOP, [1,2,3]

    nests = NO_SHOP, SHOP
    # Definition of the model. This is the contribution of each
    # observation to the log likelihood function.
    prob0 = models.lognested(V, av, nests, 0)
    prob1 = models.lognested(V, av, nests, 1)
    prob2 = models.lognested(V, av, nests, 2)
    prob3 = models.lognested(V, av, nests, 3)

    simulate = {
        'Prob_no': prob0,
        'Prob_off': prob1,
        'Prob_on': prob2,
        'Prob_both': prob3,
    }

    genral_results = res.bioResults(pickleFile = 'shoping_nested.pickle')

    biogeme = bio.BIOGEME(database, simulate)
    biogeme.modelName = 'onlineshop_simul'

    general_sim_results = biogeme.simulate(genral_results.getBetaValues())
    print(online_sim_results.describe())

    df_per['Prob_no_g']  =general_sim_results['Prob_no']
    df_per['Prob_off_g'] =general_sim_results['Prob_off']
    df_per['Prob_on_g']  =general_sim_results['Prob_on']
    df_per['Prob_both_g']=general_sim_results['Prob_both']



    # %%
    ############################################# Ondemand Model estimation ################################
    # %%
    ################### final model -on demand ##########
    database = db.Database('shop', df_per)

    # The following statement allows you to use the names of the
    # variable as Python variable.
    globals().update(database.variables)

    # Parameters to be estimated
    ## Intercept
    ASC_NOS = Beta('ASC_NOS', 0, None, None, 1)
    ASC_OFF = Beta('ASC_OFF', 0, None, None, 0)
    ASC_ONS = Beta('ASC_ONS', 0, None, None, 0)
    ASC_BOT = Beta('ASC_BOT', 0, None, None, 0)
    ## Beta
    B_SEX_V0= Beta('B_SEX_V0', 0, None, None, 1)
    B_SEX_V1= Beta('B_SEX_V1', 0, None, None, 0)
    B_SEX_V2= Beta('B_SEX_V2', 0, None, None, 0)
    B_SEX_V3= Beta('B_SEX_V3', 0, None, None, 0)

    ## Beta
    B_INC_V0= Beta('B_INC_V0', 0, None, None, 1)
    B_INC_V1= Beta('B_INC_V1', 0, None, None, 0)
    B_INC_V2= Beta('B_INC_V2', 0, None, None, 0)
    B_INC_V3= Beta('B_INC_V3', 0, None, None, 0)
    ###
    B_HHSIZE_V0= Beta('B_HHSIZE_V0', 0, None, None, 1)
    B_HHSIZE_V1= Beta('B_HHSIZE_V1', 0, None, None, 0)
    B_HHSIZE_V2= Beta('B_HHSIZE_V2', 0, None, None, 0)
    B_HHSIZE_V3= Beta('B_HHSIZE_V3', 0, None, None, 0)
    ###
    B_WORKER_V0= Beta('B_WORKER_V0', 0, None, None, 1)
    B_WORKER_V1= Beta('B_WORKER_V1', 0, None, None, 0)
    B_WORKER_V2= Beta('B_WORKER_V2', 0, None, None, 0)
    B_WORKER_V3= Beta('B_WORKER_V3', 0, None, None, 0)

    ###
    B_MSACAT_V0= Beta('B_MSACAT_V0', 0, None, None, 1)
    B_MSACAT_V1= Beta('B_MSACAT_V1', 0, None, None, 0)
    B_MSACAT_V2= Beta('B_MSACAT_V2', 0, None, None, 0)
    B_MSACAT_V3= Beta('B_MSACAT_V3', 0, None, None, 0)
    ###
    B_EDUC_0_V0= Beta('B_EDUC_0_V0', 0, None, None, 1)
    B_EDUC_0_V1= Beta('B_EDUC_0_V1', 0, None, None, 0)
    B_EDUC_0_V2= Beta('B_EDUC_0_V2', 0, None, None, 0)
    B_EDUC_0_V3= Beta('B_EDUC_0_V3', 0, None, None, 0)
    ###
    B_EDUC_1_V0= Beta('B_EDUC_1_V0', 0, None, None, 1)
    B_EDUC_1_V1= Beta('B_EDUC_1_V1', 0, None, None, 0)
    B_EDUC_1_V2= Beta('B_EDUC_1_V2', 0, None, None, 0)
    B_EDUC_1_V3= Beta('B_EDUC_1_V3', 0, None, None, 0)
    ###
    B_EDUC_2_V0= Beta('B_EDUC_2_V0', 0, None, None, 1)
    B_EDUC_2_V1= Beta('B_EDUC_2_V1', 0, None, None, 0)
    B_EDUC_2_V2= Beta('B_EDUC_2_V2', 0, None, None, 0)
    B_EDUC_2_V3= Beta('B_EDUC_2_V3', 0, None, None, 0)
    ###
    B_EDUC_3_V0= Beta('B_EDUC_3_V0', 0, None, None, 1)
    B_EDUC_3_V1= Beta('B_EDUC_3_V1', 0, None, None, 0)
    B_EDUC_3_V2= Beta('B_EDUC_3_V2', 0, None, None, 0)
    B_EDUC_3_V3= Beta('B_EDUC_3_V3', 0, None, None, 0)

    ###
    B_AGE_IMP_0_V0= Beta('B_AGE_IMP_0_V0', 0, None, None, 1)
    B_AGE_IMP_0_V1= Beta('B_AGE_IMP_0_V1', 0, None, None, 0)
    B_AGE_IMP_0_V2= Beta('B_AGE_IMP_0_V2', 0, None, None, 0)
    B_AGE_IMP_0_V3= Beta('B_AGE_IMP_0_V3', 0, None, None, 0)

    ###
    B_AGE_IMP_1_V0= Beta('B_AGE_IMP_1_V0', 0, None, None, 1)
    B_AGE_IMP_1_V1= Beta('B_AGE_IMP_1_V1', 0, None, None, 0)
    B_AGE_IMP_1_V2= Beta('B_AGE_IMP_1_V2', 0, None, None, 0)
    B_AGE_IMP_1_V3= Beta('B_AGE_IMP_1_V3', 0, None, None, 0)

    ###
    B_AGE_IMP_2_V0= Beta('B_AGE_IMP_2_V0', 0, None, None, 1)
    B_AGE_IMP_2_V1= Beta('B_AGE_IMP_2_V1', 0, None, None, 0)
    B_AGE_IMP_2_V2= Beta('B_AGE_IMP_2_V2', 0, None, None, 0)
    B_AGE_IMP_2_V3= Beta('B_AGE_IMP_2_V3', 0, None, None, 0)
    ###
    B_AGE_IMP_3_V0= Beta('B_AGE_IMP_3_V0', 0, None, None, 1)
    B_AGE_IMP_3_V1= Beta('B_AGE_IMP_3_V1', 0, None, None, 0)
    B_AGE_IMP_3_V2= Beta('B_AGE_IMP_3_V2', 0, None, None, 0)
    B_AGE_IMP_3_V3= Beta('B_AGE_IMP_3_V3', 0, None, None, 0)
    ###
    ###
    B_RACE_1_V0= Beta('B_RACE_1_V0', 0, None, None, 1)
    B_RACE_1_V1= Beta('B_RACE_1_V1', 0, None, None, 0)
    B_RACE_1_V2= Beta('B_RACE_1_V2', 0, None, None, 0)
    B_RACE_1_V3= Beta('B_RACE_1_V3', 0, None, None, 0)

    ###
    B_RACE_2_V0= Beta('B_RACE_2_V0', 0, None, None, 1)
    B_RACE_2_V1= Beta('B_RACE_2_V1', 0, None, None, 0)
    B_RACE_2_V2= Beta('B_RACE_2_V2', 0, None, None, 0)
    B_RACE_2_V3= Beta('B_RACE_2_V3', 0, None, None, 0)
    ###
    B_RACE_3_V0= Beta('B_RACE_3_V0', 0, None, None, 1)
    B_RACE_3_V1= Beta('B_RACE_3_V1', 0, None, None, 0)
    B_RACE_3_V2= Beta('B_RACE_3_V2', 0, None, None, 0)
    B_RACE_3_V3= Beta('B_RACE_3_V3', 0, None, None, 0)

    ###
    B_CENSUS_R_2_V0= Beta('B_CENSUS_R_2_V0', 0, None, None, 1)
    B_CENSUS_R_2_V1= Beta('B_CENSUS_R_2_V1', 0, None, None, 0)
    B_CENSUS_R_2_V2= Beta('B_CENSUS_R_2_V2', 0, None, None, 0)
    B_CENSUS_R_2_V3= Beta('B_CENSUS_R_2_V3', 0, None, None, 0)
    ###
    B_CENSUS_R_3_V0= Beta('B_CENSUS_R_3_V0', 0, None, None, 1)
    B_CENSUS_R_3_V1= Beta('B_CENSUS_R_3_V1', 0, None, None, 0)
    B_CENSUS_R_3_V2= Beta('B_CENSUS_R_3_V2', 0, None, None, 0)
    B_CENSUS_R_3_V3= Beta('B_CENSUS_R_3_V3', 0, None, None, 0)
    ##
    B_CENSUS_R_4_V0= Beta('B_CENSUS_R_4_V0', 0, None, None, 1)
    B_CENSUS_R_4_V1= Beta('B_CENSUS_R_4_V1', 0, None, None, 0)
    B_CENSUS_R_4_V2= Beta('B_CENSUS_R_4_V2', 0, None, None, 0)
    B_CENSUS_R_4_V3= Beta('B_CENSUS_R_4_V3', 0, None, None, 0)

    ###
    #Prob_no_V0= Beta('Prob_no_V0', 0, None, None, 1)
    NO_V1= Beta('NO_V1', 0, None, None, 0)
    NO_V2= Beta('NO_V2', 0, None, None, 0)
    NO_V3= Beta('NO_V3', 0, None, None, 0)

    LO_V0= Beta('LO_V0', 0, None, None, 1)
    LO_V1= Beta('LO_V1', 0, None, None, 0)
    LO_V2= Beta('LO_V2', 0, None, None, 0)
    LO_V3= Beta('LO_V3', 0, None, None, 0)
    ###
    MD_V0= Beta('MD_V0', 0, None, None, 1)
    MD_V1= Beta('MD_V1', 0, None, None, 0)
    MD_V2= Beta('MD_V2', 0, None, None, 0)
    MD_V3= Beta('MD_V3', 0, None, None, 0)
    ##
    HI_V0= Beta('HI_V0', 0, None, None, 1)
    HI_V1= Beta('HI_V1', 0, None, None, 0)
    HI_V2= Beta('HI_V2', 0, None, None, 0)
    HI_V3= Beta('HI_V3', 0, None, None, 0)


    # Definition of the utility functions
    V0 = ASC_NOS + B_SEX_V0 * R_SEX_IMP + B_WORKER_V0 *WORKER + B_EDUC_0_V0 *EDUC_0  +B_AGE_IMP_3_V0 *R_AGE_IMP_3+\
    B_RACE_1_V0 *R_RACE_1+B_RACE_2_V0 *R_RACE_2  +B_MSACAT_V0 *MSACAT + B_INC_V0 * income_val

    V1 = ASC_OFF+ B_SEX_V1 * R_SEX_IMP  + B_WORKER_V1 *WORKER + B_EDUC_0_V1 *EDUC_0 +B_AGE_IMP_3_V1 *R_AGE_IMP_3+\
    B_RACE_1_V1 *R_RACE_1+B_RACE_2_V1 *R_RACE_2+B_MSACAT_V1 *MSACAT + B_INC_V1 * income_val+\
            NO_V1*Prob_no

    V2 = ASC_ONS + B_SEX_V2 * R_SEX_IMP + B_WORKER_V2 *WORKER + B_EDUC_0_V2 *EDUC_0 +B_AGE_IMP_3_V2 *R_AGE_IMP_3+\
    B_RACE_1_V2 *R_RACE_1+B_RACE_2_V2 *R_RACE_2  +B_MSACAT_V2 *MSACAT + B_INC_V2 * income_val+\
            NO_V2*Prob_no

    V3 = ASC_BOT +B_SEX_V3 * R_SEX_IMP  + B_WORKER_V3 *WORKER + B_EDUC_0_V3 *EDUC_0 +B_AGE_IMP_3_V3 *R_AGE_IMP_3+\
    B_RACE_1_V3 *R_RACE_1+B_RACE_2_V3 *R_RACE_2  +B_MSACAT_V3 *MSACAT+ B_INC_V3 * income_val+\
            NO_V3*Prob_no

    # Associate utility functions with the numbering of alternatives
    # Associate utility functions with the numbering of alternatives
    V = {0: V0,1: V1, 2: V2, 3: V3}

    # Associate the availability conditions with the alternatives
    av = {0: 1, 1: 1, 2: 1, 3: 1}

    # nest parameters
    NEST_SHOP=Beta('NEST_SHOP',1,1.0,20,0)

    NO_SHOP =1.0, [0]
    SHOP=NEST_SHOP, [1,2,3]

    nests = NO_SHOP, SHOP
    # Definition of the model. This is the contribution of each
    # observation to the log likelihood function.
    # observation to the log likelihood function.
    prob0 = models.lognested(V, av, nests, 0)
    prob1 = models.lognested(V, av, nests, 1)
    prob2 = models.lognested(V, av, nests, 2)
    prob3 = models.lognested(V, av, nests, 3)

    simulate = {
        'Prob_no': prob0,
        'Prob_off': prob1,
        'Prob_on': prob2,
        'Prob_both': prob3,
    }

    genral_results = res.bioResults(pickleFile = 'ondemand_choice.pickle')

    biogeme = bio.BIOGEME(database, simulate)
    biogeme.modelName = 'onlineshop_simul'

    general_sim_results = biogeme.simulate(genral_results.getBetaValues())
    print(online_sim_results.describe())

    df_per['Prob_no_on']  =general_sim_results['Prob_no']
    df_per['Prob_off_on'] =general_sim_results['Prob_off']
    df_per['Prob_on_on']  =general_sim_results['Prob_on']
    df_per['Prob_both_on']=general_sim_results['Prob_both']
    
    def choice(no,off,on,both):
        r_num = random.uniform(0,1)
        if r_num >=0 and r_num < no:
            return [1,0,0] #"No"
        elif r_num >=no and r_num < no +off:
            return [0,1,0] #"Off"
        elif r_num >=no +off and r_num < no+off+on:
            return [0,0,1] #"On"
        elif r_num >= no+off+on and r_num <=  no+off+on+both:
            return [0,1,1] #"Both"    
  

    df_per[['general_no','general_off','general_on']]=df_per.apply(lambda x: choice(x['Prob_no_g'], x['Prob_off_g'], x['Prob_on_g'], x['Prob_both_g']), axis=1).to_list()
    df_per[['ondmd_no','ondmd_off','ondmd_on']]=df_per.apply(lambda x: choice(x['Prob_no_on'], x['Prob_off_on'], x['Prob_on_on'], x['Prob_both_on']), axis=1).to_list()
    df_per=df_per[['household_id','member_id','block_id', 'general_no','general_off','general_on','ondmd_no','ondmd_off','ondmd_on']]
    df_per.to_csv('../../../FRISM_input_output_{}/Sim_outputs/Generation/{}_per_synth.csv'.format(config.study_region,config.study_region), index = False, header=True)

    df_per_hh=df_per.groupby(['household_id']).agg(general_no= ("general_no",'sum'),
                                                    general_off= ("general_off",'sum'),
                                                    general_on= ("general_on",'sum'),
                                                    ondmd_no= ("ondmd_no",'sum'),
                                                    ondmd_off= ("ondmd_off",'sum'),
                                                    ondmd_on= ("ondmd_on",'sum')).reset_index()
    df_per_hh["delivery_d"]= df_per_hh["general_on"]
    df_per_hh["ondmd_delivery_d"]= df_per_hh["ondmd_on"]
    df_hh= df_hh[['household_id','block_id',"hh_income","income_cls_0","income_cls_1","income_cls_2","income_cls_3"]]
    df_hh_model=df_hh.merge(df_per_hh, on='household_id', how='left')
    df_hh_model.to_csv('../../../FRISM_input_output_{}/Sim_outputs/Generation/households_del_dalily.csv'.format(config.study_region), index = False, header=True)

    ## need to updat later
    #Run delivery frequency model
    ## Define x variables which come from config.py
    # sim_X = df_per[config.selected_x_var_delivery]
    # loaded_model = joblib.load('delivery_freq_model.sav')
    # df_per['delivery_f']=loaded_model.predict(sim_X)
    # ## post proseesing in delivery frequency
    # df_per['delivery_f'] = df_per.apply(lambda x: delivery_process(x['onlineshop'], x['delivery_f'], x['income_cls']), axis=1) #**********************
    # ## Process for validation and save it
    # sns.displot(df_per['delivery_f'])
    # plt.savefig('../../../FRISM_input_output_{}/Sim_outputs/Generation/Delivery plot_simulated.png'.format(config.study_region))
    # ## Save df_per for further validation
    # df_per.to_csv('../../../FRISM_input_output_{}/Sim_outputs/Generation/{}_per_synth.csv'.format(config.study_region,config.study_region), index = False, header=True)

    ## Need to update later 
    # print ("** Plot observed and simulatated by income group")
    # df_hh_obs=pd.read_csv('../../../FRISM_input_output_{}/Model_inputs/NHTS/{}_hh.csv'.format(config.study_region,config.study_region))
    # df_per_obs=pd.read_csv('../../../FRISM_input_output_{}/Model_inputs/NHTS/{}_per.csv'.format(config.study_region,config.study_region))
    # df_per_obs_hh=df_per_obs.groupby(['HOUSEID'])['DELIVER'].agg(delivery_f='sum').reset_index()
    # df_hh_obs=df_hh_obs.merge(df_per_obs_hh, on='HOUSEID', how='left')

    # #df_hh_model=pd.read_csv('../../../FRISM_input_output_{}/Sim_outputs/Generation/households_del.csv'.format(config.study_region))


    # df_hh_obs['delivery_f'] =df_hh_obs['delivery_f'].apply(lambda x: 0 if np.isnan(x) else int(x))
    # df_hh_model['delivery_f'] =df_hh_model['delivery_f'].apply(lambda x: 0 if np.isnan(x) else int(x))


    # list_income=["income_cls_0","income_cls_1","income_cls_2","income_cls_3"]
    # dic_income={"income_cls_0": "income <$35k",
    #             "income_cls_1": "income $35k-$75k",
    #             "income_cls_2": "income $75k-125k",
    #             "income_cls_3": "income >$125k"}
        
    # for ic_nm in list_income:
    #     plt.figure(figsize = (8,6))
    #     #plt.hist(df_hh_obs[df_hh_obs[ic_nm]==1]['delivery_f'], color ="blue", density=True, bins=df_hh_obs[df_hh_obs[ic_nm]==1]['delivery_f'].max(), alpha = 0.3, label="observed")
    #     #plt.hist(df_hh_model[(df_hh_model[ic_nm]==1) & (df_hh_model['delivery_f']<=30)]['delivery_f'], color ="red", density=True, bins=80, alpha = 0.3, label="modeled")
    #     #plt.hist(df_hh_model[(df_hh_model[ic_nm]==1)]['delivery_f'], color ="red", density=True, bins=df_hh_model[(df_hh_model[ic_nm]==1)]['delivery_f'].max(), alpha = 0.3, label="modeled")
    #     plt.hist(df_hh_obs[(df_hh_obs[ic_nm]==1) & (df_hh_obs['delivery_f']<=60)]['delivery_f'], color ="blue", density=True, bins=df_hh_obs[(df_hh_obs[ic_nm]==1) & (df_hh_obs['delivery_f']<=60)]['delivery_f'].max(), alpha = 0.3, label="observed")
    #     plt.hist(df_hh_model[(df_hh_model[ic_nm]==1)& (df_hh_model['delivery_f']<=60)]['delivery_f'], color ="red", density=True, bins=df_hh_model[(df_hh_model[ic_nm]==1)& (df_hh_model['delivery_f']<=60)]['delivery_f'].max(), alpha = 0.3, label="modeled")
    #     plt.title("Density of Delivery Frequency in {0}, {1}".format(dic_income[ic_nm], config.study_region))
    #     plt.legend(loc="upper right")
    #     plt.savefig('../../../FRISM_input_output_{0}/Sim_outputs/Generation/B2C_delivery_val_{1}.png'.format(config.study_region, ic_nm))

if __name__ == "__main__":
    main()

##
#     