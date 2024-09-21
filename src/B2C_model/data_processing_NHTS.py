# %%
import pandas as pd
import numpy as np
#%%
import joblib
from argparse import ArgumentParser
# library for models 
import statsmodels.api as sm
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
from sklearn.metrics import accuracy_score
from sklearn.model_selection import cross_val_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import mean_squared_error
from sklearn.calibration import CalibratedClassifierCV
from imblearn.over_sampling import SMOTE
import statsmodels.api as sm
import statsmodels.formula.api as smf
import seaborn as sns
import matplotlib.pyplot as plt
# %%
def input_files_processing(household_file, person_file,state_CBSA,x_var_candidate_hh, x_var_candidate_per):
    # Household data processing
    # Read NHTS household data
    nhts_hh = pd.read_csv(household_file, header=0, sep=',')
    
    # Select data within the State (e.g., CA, TX, MI) where the study area is located   
    nhts_hh = nhts_hh[nhts_hh['HH_CBSA'].isin(state_CBSA)]
    
    # Subset of data with potential X variables for model estimation 
    nhts_hh= nhts_hh[x_var_candidate_hh]
    
    # Filter out records that have not valid response
    ## Exlude HOUSEID (key ID) and HH_CBSA (v_type=object, not used in modeling)
    ## var_x should be "int"; Need to check if there is object type variable in a new variable set
    for var_x in x_var_candidate_hh:
        if var_x not in ['HOUSEID','HH_CBSA']: 
            nhts_hh = nhts_hh[nhts_hh[var_x]>=0]

    # Process variables using function         
    nhts_hh['income_est']=nhts_hh['HHFAMINC'].apply(income_est)
    nhts_hh['income_cls']=nhts_hh['HHFAMINC'].apply(income_group)
    nhts_hh['WEBUSE17']=nhts_hh['WEBUSE17'].apply(web_class)
    nhts_hh['HH_RACE']=nhts_hh['HH_RACE'].apply(race_class)
    nhts_hh['HOMEOWN']=nhts_hh['HOMEOWN'].apply(home_class)
    nhts_hh['HH_HISP']=nhts_hh['HH_HISP'].apply(hisp_class)
    nhts_hh['LIF_CYC']=nhts_hh['LIF_CYC'].apply(child_class)

    # list of variables that have class
    ## Need to update!!, if functions change used in "Process variables using function"  
    Class_vars= ['HH_RACE','HOMEOWN','HH_HISP','LIF_CYC','income_cls'] 

    # Create class variables that has more than two classes
    cat_vars=[]
    for var_c in Class_vars:
        if nhts_hh[var_c].unique().size >2:
            cat_vars.append(var_c)
    for var in cat_vars:
        cat_list='var'+'_'+var
        cat_list = pd.get_dummies(nhts_hh[var], prefix=var)
        nhts_hh=nhts_hh.join(cat_list)
    #data_vars=nhts_hh.columns.values.tolist()
    #to_keep=[i for i in data_vars if i not in cat_vars]
    #nhts_hh=nhts_hh[to_keep]
   
    # personal data processing
    # Read NHTS person data
    nhts_per = pd.read_csv(person_file, header=0, sep=',')

    # Select data within the State (e.g., CA, TX, MI) where the study area is located   
    nhts_per = nhts_per[nhts_per['HH_CBSA'].isin(state_CBSA)]
    
    # Subset of data with potential X variables for model estimation 
    nhts_per= nhts_per[x_var_candidate_per]
    
    # Filter out records that have not valid response
    ## Exlude HOUSEID (key ID) and HH_CBSA (v_type=object, not used in modeling)
    ## var_x should be "int"; Need to check if there is object type variable in a new variable set
    for var_x in x_var_candidate_per:
        if var_x not in ['HOUSEID','HH_CBSA']: 
            nhts_per = nhts_per[nhts_per[var_x]>=-1]
    # Add "WEBUSE17" from household        
    nhts_per = nhts_per.merge(nhts_hh[['HOUSEID','WEBUSE17','income_est','income_cls']], on='HOUSEID', how='inner')
    # Select records with age>16 with assumption that person>16 years old can do online shopping
    nhts_per = nhts_per[nhts_per['R_AGE_IMP']>=16]           

    # Process variables using function         
    nhts_per['EDUC']=nhts_per['EDUC'].apply(edu_class)
    nhts_per['SCHTYP']=nhts_per['SCHTYP'].apply(student_class)
    nhts_per['WRK_HOME']=nhts_per['WRK_HOME'].apply(wfh_class)
    nhts_per['WORKER']=nhts_per['WORKER'].apply(work_class)
    nhts_per['R_AGE_IMP']=nhts_per['R_AGE_IMP'].apply(age_est)
    nhts_per['WRKTRANS']=nhts_per['WRKTRANS'].apply(mode_est)
    nhts_per['onlineshop']=nhts_per['DELIVER'].apply(onlineshop_class)
    nhts_per['R_RACE']=nhts_per['R_RACE'].apply(race_class)
    nhts_per['R_SEX_IMP']=nhts_per['R_SEX_IMP'].apply(sex_class)      

    # list of variables that have class
    ## Need to update!!, if functions change used in "Process variables using function"  
    Class_vars= ['EDUC','SCHTYP','WRK_HOME', 'WORKER','R_AGE_IMP', 'WRKTRANS','R_RACE','R_SEX_IMP','WEBUSE17','income_cls'] 

    # Create class variables that has more than two classes
    cat_vars=[]
    for var_c in Class_vars:
        if nhts_per[var_c].unique().size >2:
            cat_vars.append(var_c)
    for var in cat_vars:
        cat_list='var'+'_'+var
        cat_list = pd.get_dummies(nhts_per[var], prefix=var)
        nhts_per=nhts_per.join(cat_list)
    #data_vars=nhts_per.columns.values.tolist()
    #to_keep=[i for i in data_vars if i not in cat_vars]
    #nhts_per=nhts_per[to_keep]

    return nhts_hh, nhts_per

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
# Aggregate income gorup
def income_group(HHFAMINC):
    if HHFAMINC in [1,2,3]: # 25k
        return 0
    elif HHFAMINC in [4,5]: # 25~50k
        return 1
    elif HHFAMINC in [6]: # 50~75k 
        return 2
    elif HHFAMINC in [7]: # 75~100k  
        return 3
    elif HHFAMINC in [8,9]: # 100~150k  
        return 4 
    elif HHFAMINC in [10,11]: # 150~k 
        return 5                   

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
    if EDUC in [-1, 1,2,3]:
        return 0
    elif EDUC in [4,5]:
        return 1
    elif EDUC in [6,7,8]:
        return 2    
    # elif EDUC in [5]:
    #     return 3  

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
    if R_AGE_IMP  <18 :
        return 0
    elif R_AGE_IMP  >=18 and R_AGE_IMP  <25:
        return 1
    elif R_AGE_IMP  >=25 and R_AGE_IMP  <50:
        return 2
    elif R_AGE_IMP  >=50 and R_AGE_IMP  <65:
        return 3
    elif R_AGE_IMP  >=65:
        return 4    
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
def income_est(HHFAMINC):
    if HHFAMINC == 1:
        est_income= (0+10000)
    elif HHFAMINC == 2:
        est_income= (10000+15000)/2
    elif HHFAMINC == 3:
        est_income= (15000+25000)/2
    elif HHFAMINC == 4:
        est_income= (25000+35000)/2
    elif HHFAMINC == 5:
        est_income= (35000+50000)/2
    elif HHFAMINC == 6:
        est_income= (50000+75000)/2
    elif HHFAMINC == 7:
        est_income= (75000+100000)/2
    elif HHFAMINC == 8:
        est_income= (100000+125000)/2
    elif HHFAMINC == 9:
        est_income= (125000+150000)/2
    elif HHFAMINC == 10:
        est_income= (150000+200000)/2
    elif HHFAMINC == 11:
        est_income= (200000+500000)/2
    return est_income/100000

def urban (urban):
    if urban ==1:
        return 1
    else:
        return 0
##############################
# %%    
# Household data processing
# Read NHTS household data
fdir_input= "../../../B2C_Data/NHTS_22/"
person_file=fdir_input+"perpub.csv"
nhts_per = pd.read_csv(person_file, header=0, sep=',')

x_var_candidate_per= ["DRVRCNT",
                      'EDUC',
                     'HOUSEID',
                     'HHFAMINC',
                     'HHSIZE',
                     'HHVEHCNT',
                     'MSACAT',
                     'HH_HISP', 
                     'HOMEOWN',
                     'HH_RACE',
                     'WRKCOUNT', 
                    'R_AGE',  
                    'R_SEX_IMP', 
                    'R_RACE_IMP', 
                    'WORKER',
                    "DELIVER",
                    "DELIV_FOOD",
                    "DELIV_GOOD",
                    "DELIV_GROC",
                    "WTPERFIN",
                    "URBRUR"]

# Subset of data with potential X variables for model estimation 
nhts_per= nhts_per[x_var_candidate_per]

# Filter out records that have not valid response
## Exlude HOUSEID (key ID) and HH_CBSA (v_type=object, not used in modeling)
## var_x should be "int"; Need to check if there is object type variable in a new variable set
for var_x in x_var_candidate_per:
    if var_x not in ['HOUSEID']: 
        nhts_per = nhts_per[nhts_per[var_x]>=-1]
# Add "WEBUSE17" from household        
#nhts_per = nhts_per.merge(nhts_hh[['HOUSEID','WEBUSE17','income_est','income_cls']], on='HOUSEID', how='inner')
# Select records with age>16 with assumption that person>16 years old can do online shopping
nhts_per = nhts_per[nhts_per['R_AGE']>=16]           
# %%
# Process variables using function
nhts_per['income_est']=nhts_per['HHFAMINC'].apply(income_est)
nhts_per['income_cls']=nhts_per['HHFAMINC'].apply(income_group)
nhts_per['HH_RACE']=nhts_per['HH_RACE'].apply(race_class)
nhts_per['HOMEOWN']=nhts_per['HOMEOWN'].apply(home_class)
nhts_per['HH_HISP']=nhts_per['HH_HISP'].apply(hisp_class)         
nhts_per['EDUC']=nhts_per['EDUC'].apply(edu_class)
nhts_per['WORKER']=nhts_per['WORKER'].apply(work_class)
nhts_per['R_AGE_C']=nhts_per['R_AGE'].apply(age_est)
nhts_per['R_RACE']=nhts_per['R_RACE_IMP'].apply(race_class)
nhts_per['R_SEX_IMP']=nhts_per['R_SEX_IMP'].apply(sex_class)      
nhts_per['URBRUR']=nhts_per['URBRUR'].apply(urban)
# list of variables that have class
## Need to update!!, if functions change used in "Process variables using function"  
Class_vars= ['EDUC', 'WORKER','R_RACE','R_SEX_IMP','income_cls',"R_AGE_C"] 

# Create class variables that has more than two classess
cat_vars=[]
for var_c in Class_vars:
    if nhts_per[var_c].unique().size >2:
        cat_vars.append(var_c)
for var in cat_vars:
    cat_list='var'+'_'+var
    cat_list = pd.get_dummies(nhts_per[var], prefix=var)
    nhts_per=nhts_per.join(cat_list)
#data_vars=nhts_per.columns.values.tolist()
#to_keep=[i for i in data_vars if i not in cat_vars]
#nhts_per=nhts_per[to_keep]

# %%
nhts_per.to_csv(fdir_input+"nhts_df_model_2022.csv")   
# %%
