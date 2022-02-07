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
    synth_hh['income_est']= synth_hh['income']/100000
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

def input_files_processing_per(df_hh, person_file):
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
    Class_vars= ['EDUC','SCHTYP','WRK_HOME', 'WORKER','R_AGE_IMP','R_RACE', 'R_SEX_IMP', 'WEBUSE17'] 

    # Create class variables that has more than two classes
    cat_vars=[]
    for var_c in Class_vars:
        if synth_per[var_c].unique().size >2:
            cat_vars.append(var_c)
    for var in cat_vars:
        cat_list='var'+'_'+var
        cat_list = pd.get_dummies(synth_per[var], prefix=var)
        synth_per=synth_per.join(cat_list)
    data_vars=synth_per.columns.values.tolist()
    #to_keep=[i for i in data_vars if i not in cat_vars]
    #synth_per=synth_per[to_keep]
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
    if R_AGE_IMP  <20 :
        return 0
    elif R_AGE_IMP  >=20 and R_AGE_IMP  <40:
        return 1
    elif R_AGE_IMP  >=40 and R_AGE_IMP  <60:
        return 2
    elif R_AGE_IMP  >=60:
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

def delivery_process(online_choice, delivery):
    if online_choice ==0:
        final_delivery=0
    elif online_choice ==1:
        if delivery <=1:
            final_delivery =1
        elif delivery >1 and delivery <80:
            final_delivery = round(delivery-0.5)
        elif delivery >=80:
            final_delivery = random.randrange (60,80,1)
    return final_delivery

def onlineshop_calibration(income_cl, online_choice):
    if income_cl ==0:
        if online_choice ==0:
            if random.uniform(0,1) <0.57:
                return online_choice
            else:
                return 1
        else:
            return online_choice        
    elif income_cl ==1:
        if online_choice ==0:
            if random.uniform(0,1) <0.68:
                return online_choice
            else:
                return 1
        else:
            return online_choice
    elif income_cl ==2:
        return online_choice
    elif income_cl==3:
        return online_choice                  

def main(args=None):
    # read input files
    parser = ArgumentParser()
    parser.add_argument("-hf", "--household_file", dest="hh_file",
                        help="household file in csv format", required=True, type=str)
    parser.add_argument("-pf", "--person_file", dest="per_file",
                        help="person file in csv format", required=True, type=str)                         
    args = parser.parse_args()

    # Read and process synth household
    df_hh = input_files_processing_hh(args.hh_file)

    # Run webuse_model 
    ## Define x variables which come from config.py  
    sim_X = df_hh[config.selected_x_var_web]
    loaded_model = joblib.load('webuse_model.sav')
    df_hh['WEBUSE17']=loaded_model.predict(sim_X)
    ## Process for validation and save it
    val_hh=df_hh.groupby(['income_cls','WEBUSE17'])['income_cls'].agg(num_hh='count').reset_index()
    val_hh.to_csv('../../../FRISM_input_output/Sim_outputs/Generation/%s_webuse_by_income.csv' %config.study_region, index = False, header=True)
    ## Save df_hh for further validation
    df_hh.to_csv('../../../FRISM_input_output/Sim_outputs/Generation/%s_hh_synth.csv' %config.study_region, index = False, header=True)
    print ("** Completed simulated webuse on household **")
    
    # Read and process synth household
    df_per= input_files_processing_per(df_hh, args.per_file)
    
    # Run online_shop_model 
    ## Define x variables which come from config.py  
    sim_X = df_per[config.selected_x_var_online]
    loaded_model = joblib.load('online_shop_model.sav')
    df_per['onlineshop']=loaded_model.predict(sim_X)
    df_per['onlineshop']=df_per.apply(lambda x: onlineshop_calibration(x['income_cls'], x['onlineshop']), axis=1)
    ## Process for validation and save it
    val_per=df_per.groupby(['income_cls','onlineshop'])['income_cls'].agg(num_hh='count').reset_index()
    val_per.to_csv('../../../FRISM_input_output/Sim_outputs/Generation/%s_online_by_income.csv' %config.study_region, index = False, header=True)
    print ("** Completed simulated online on individual **")

    #Run delivery frequency model
    ## Define x variables which come from config.py
    sim_X = df_per[config.selected_x_var_delivery]
    loaded_model = joblib.load('delivery_freq_model.sav')
    df_per['delivery_f']=loaded_model.predict(sim_X)
    ## post proseesing in delivery frequency
    df_per['delivery_f'] = df_per.apply(lambda x: delivery_process(x['onlineshop'], x['delivery_f']), axis=1)
    ## Process for validation and save it
    sns.displot(df_per['delivery_f'])
    plt.savefig('../../../FRISM_input_output/Sim_outputs/Generation/Delivery plot_simulated.png')
    ## Save df_per for further validation
    df_per.to_csv('../../../FRISM_input_output/Sim_outputs/Generation/%s_per_synth.csv' %config.study_region, index = False, header=True)

    # Aggregate delivery at household level
    df_per_hh=df_per.groupby(['household_id'])['delivery_f'].agg(delivery_f='sum').reset_index()
    df_hh=df_hh.merge(df_per_hh, on='household_id', how='left')
    df_hh.to_csv('../../../FRISM_input_output/Sim_outputs/Generation/households_del.csv', index = False, header=True)
    print ("** Completed simulated monthly delivery frequency on hosehold **")

if __name__ == "__main__":
    main()