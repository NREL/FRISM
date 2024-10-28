# %%
import pandas as pd
import numpy as np
import joblib
from argparse import ArgumentParser
import config_b2c_gen as config
import random
import geopandas as gpd
import statsmodels.api as sm
from sklearn.linear_model import LogisticRegression
import seaborn as sns
import matplotlib.pyplot as plt
# %%
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
                        "tenure": 'HOMEOWN',
                        "hh_children": "CHILD"}  , axis='columns')

    # Process variables using function         
    synth_hh['income_est']= synth_hh['income']/100000
    synth_hh['income_cls']= synth_hh['income'].apply(income_num2group)
    synth_hh['HH_RACE']=synth_hh['HH_RACE'].apply(race_class_synth)
    synth_hh['HOMEOWN']=synth_hh['HOMEOWN'].apply(home_class)
    synth_hh['CHILD']=synth_hh['CHILD'].apply(child_class)
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
    synth_per = synth_per.rename({"age": 'R_AGE',       
                        "edu":'EDUC',         
                        "race_id": 'R_RACE',         
                        "sex": 'R_SEX_IMP',       
                        "student": 'SCHTYP',
                        "work_at_home": 'WRK_HOME',
                        "worker": 'WORKER' }  , axis='columns')


    # Add household info      
    synth_per = synth_per.merge(synth_hh, on='household_id', how='inner')
    # Select records with age>16 with assumption that person>16 years old can do online shopping
    synth_per = synth_per[synth_per['R_AGE']>=16]           

    # Process variables using function         
    synth_per['EDUC']=synth_per['EDUC'].apply(edu_class_synth)
    synth_per['R_AGE_C']=synth_per['R_AGE'].apply(age_est)
    synth_per['R_RACE']=synth_per['R_RACE'].apply(race_class_synth)
    synth_per['R_SEX_IMP']=synth_per['R_SEX_IMP'].apply(sex_class)     

    # list of variables that have class
    ## Need to update!!, if functions change used in "Process variables using function"  
    Class_vars= ['EDUC','SCHTYP','WRK_HOME', 'WORKER','R_AGE_C','R_RACE', 'R_SEX_IMP'] 

    # Create class variables that has more than two classes
    cat_vars=[]
    for var_c in Class_vars:
        if synth_per[var_c].unique().size >2:
            cat_vars.append(var_c)
    for var in cat_vars:
        cat_list='var'+'_'+var
        cat_list = pd.get_dummies(synth_per[var], prefix=var)
        synth_per=synth_per.join(cat_list)
    return synth_per

# Aggregate income gorup from the number for synthfirm
def income_num2group(HHFAMINC):
    if HHFAMINC < 25000: # 25k
        return int(0)
    elif HHFAMINC >= 25000 and HHFAMINC < 50000: # 25~50k
        return int (1)
    elif HHFAMINC >= 50000 and HHFAMINC < 75000: # 50~75k 
        return int(2)
    elif HHFAMINC >= 75000 and HHFAMINC < 100000: # 75~100k  
        return int(3)
    elif HHFAMINC >= 100000 and HHFAMINC < 150000: # 100~150k  
        return int(4) 
    elif HHFAMINC >= 150000: # 150~k 
        return int(5)         

def race_class_synth(HH_RACE):
    if HH_RACE == 1: 
        return 1 # white
    elif HH_RACE == 2:
        return 2 # black
    elif HH_RACE == 6:
        return 3 # Asian
    else:
        return 0 # others
    
def home_class(HOMEOWN):
    if HOMEOWN == 1: 
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

    
def child_class(child):
    if child=="yes": 
        return 1 # adult only
    elif child=="no":
        return 0  

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
    elif EDUC in [3,4,5]:
        return 2    


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

def edu_class_synth(EDUC):
    if EDUC <16 :
        return 0
    elif EDUC ==16:
        return 1
    elif EDUC >16 and EDUC <=21:
        return 2
    else:
        return 3

def delivery_process(online_choice, delivery, income_cl):
    if online_choice ==0:
        final_delivery=0
    elif online_choice ==1:
        if income_cl==3:
            if delivery <=2.5:
                final_delivery =1
            elif delivery >2.5: #and delivery <20:
                final_delivery = round(delivery-0.5)
            #elif delivery >=20:
            #    final_delivery = random.randrange (15,60,1)
        else:     
            if delivery <=2.5:
                final_delivery =1
            elif delivery >2.5 and delivery <20:
                final_delivery = round(delivery-2)
            elif delivery >=20:
                final_delivery = random.randrange (15,60,1)
    return final_delivery

def onlineshop_calibration(income_cl, online_choice):
    if income_cl ==0:
        if online_choice ==0:
            if random.uniform(0,1) <0.65:
                return online_choice
            else:
                return 1
        else:
            return online_choice
    elif income_cl ==1:
        return online_choice                 
    # elif income_cl ==1:
    #     if online_choice ==0:
    #         if random.uniform(0,1) <0.68:
    #             return online_choice
    #         else:
    #             return 1
    #     else:
    #         return online_choice
    elif income_cl ==2:
        if online_choice ==1:
            if random.uniform(0,1) <0.8:
                return online_choice
            else:
                return 0
        else:
            return online_choice 
    elif income_cl==3:
        if online_choice ==1:
            if random.uniform(0,1) <0.7:
                return online_choice
            else:
                return 0
        else:
            return online_choice                   
# %%

    # Read and process synth household

hh_file= config.hh_file
per_file= config.per_file

synth_hh = pd.read_csv(hh_file, header=0, sep=',')
synth_per = pd.read_csv(per_file, header=0, sep=',')

df_hh = input_files_processing_hh(hh_file)
df_per= input_files_processing_per(df_hh, per_file)

study_region="ST"
fdir_in_out= "../../../FRISM_input_output_{}".format(study_region)
df_per_final = pd.read_csv(fdir_in_out+'/Sim_outputs/Generation/per_del_2018.csv', header=0, sep=',')

fdir_input= "../../../B2C_Data/NHTS_22/"
df_per_obs=pd.read_csv(fdir_input+"nhts_df_model_2022.csv")
df_per_obs["DELIV_GOOD"]= df_per_obs["DELIV_GOOD"].apply(lambda x: 0 if x<0 else x)
df_per_obs["DELIV_FOOD"]= df_per_obs["DELIV_FOOD"].apply(lambda x: 0 if x<0 else x)
df_per_obs["DELIV_GROC"]= df_per_obs["DELIV_GROC"].apply(lambda x: 0 if x<0 else x)
# %%
df_per_final= df_per_final.merge(df_per[["household_id", "income_cls"]], on="household_id", how="left")
# %%
df_per_final["DELIV_GOOD"]= df_per_final["DELIV_GOOD"].apply(lambda x: int(x))
df_per_final["DELIV_FOOD"]= df_per_final["DELIV_FOOD"].apply(lambda x: int(x))
df_per_final["DELIV_GROC"]= df_per_final["DELIV_GROC"].apply(lambda x:int(x))

df_per_final["DELIV_GOOD"]= df_per_final["DELIV_GOOD"].apply(lambda x: random.randint(1, 10) if x>6 and x <10 else x)
df_per_final["DELIV_FOOD"]= df_per_final["DELIV_FOOD"].apply(lambda x: random.randint(1, 5) if x>3 and x <5 else x)
df_per_final["DELIV_GROC"]= df_per_final["DELIV_GROC"].apply(lambda x:random.randint(1, 5) if x>3 and x <5 else x)

# %%

list_income=[0,1,2,3,4,5]
dic_income={0: "income <$25k",
            1: "income $25k-$50k",
            2: "income $50k-75k",
            3: "income $75k-100k",
            4: "income $100k-150k",
            5: "income >$150k"}
    
for ic_nm in list_income:
    plt.figure(figsize = (8,6))
    #plt.hist(df_hh_obs[df_hh_obs[ic_nm]==1]['delivery_f'], color ="blue", density=True, bins=df_hh_obs[df_hh_obs[ic_nm]==1]['delivery_f'].max(), alpha = 0.3, label="observed")
    #plt.hist(df_hh_model[(df_hh_model[ic_nm]==1) & (df_hh_model['delivery_f']<=30)]['delivery_f'], color ="red", density=True, bins=80, alpha = 0.3, label="modeled")
    #plt.hist(df_hh_model[(df_hh_model[ic_nm]==1)]['delivery_f'], color ="red", density=True, bins=df_hh_model[(df_hh_model[ic_nm]==1)]['delivery_f'].max(), alpha = 0.3, label="modeled")
    plt.hist(df_per_obs[(df_per_obs["income_cls"]==ic_nm) & (df_per_obs['DELIV_GOOD']<=60)]['DELIV_GOOD'], color ="blue", density=True, bins=60, alpha = 0.3, label="observed", weights=df_per_obs["WTPERFIN"])
    plt.hist(df_per_final[(df_per_final["income_cls"]==ic_nm)& (df_per_final['DELIV_GOOD']<=60)]['DELIV_GOOD'], color ="red", density=True, bins=60, alpha = 0.3, label="modeled")
    plt.title("Density of Delivery Frequency in {0}".format(dic_income[ic_nm]))
    plt.legend(loc="upper right")
    plt.savefig('../../../FRISM_input_output_ST/Sim_outputs/Generation/B2C_delivery_val_{0}.png'.format(ic_nm))

# %%

list_income=[0,1,2,3,4,5]
dic_income={0: "income <$25k",
            1: "income $25k-$50k",
            2: "income $50k-75k",
            3: "income $75k-100k",
            4: "income $100k-150k",
            5: "income >$150k"}
    
for ic_nm in list_income:
    plt.figure(figsize = (8,6))
    #plt.hist(df_hh_obs[df_hh_obs[ic_nm]==1]['delivery_f'], color ="blue", density=True, bins=df_hh_obs[df_hh_obs[ic_nm]==1]['delivery_f'].max(), alpha = 0.3, label="observed")
    #plt.hist(df_hh_model[(df_hh_model[ic_nm]==1) & (df_hh_model['delivery_f']<=30)]['delivery_f'], color ="red", density=True, bins=80, alpha = 0.3, label="modeled")
    #plt.hist(df_hh_model[(df_hh_model[ic_nm]==1)]['delivery_f'], color ="red", density=True, bins=df_hh_model[(df_hh_model[ic_nm]==1)]['delivery_f'].max(), alpha = 0.3, label="modeled")
    plt.hist(df_per_obs[(df_per_obs["income_cls"]==ic_nm) & (df_per_obs['DELIV_GOOD']<=60)]['DELIV_GOOD'], color ="blue", density=True, bins=60, alpha = 0.3, label="observed", weights=df_per_obs[(df_per_obs["income_cls"]==ic_nm) & (df_per_obs['DELIV_GOOD']<=60)]['WTPERFIN'])
    plt.hist(df_per_final[(df_per_final["income_cls"]==ic_nm)& (df_per_final['DELIV_GOOD']<=60)]['DELIV_GOOD'], color ="red", density=True, bins=60, alpha = 0.3, label="modeled")
    plt.title("Density of Delivery Frequency in {0}".format(dic_income[ic_nm]))
    plt.legend(loc="upper right")
    plt.savefig('../../../FRISM_input_output_ST/Sim_outputs/Generation/B2C_delivery_val_{0}.png'.format(ic_nm))


# %%
plt.figure(figsize = (8,6))
#plt.hist(df_hh_obs[df_hh_obs[ic_nm]==1]['delivery_f'], color ="blue", density=True, bins=df_hh_obs[df_hh_obs[ic_nm]==1]['delivery_f'].max(), alpha = 0.3, label="observed")
#plt.hist(df_hh_model[(df_hh_model[ic_nm]==1) & (df_hh_model['delivery_f']<=30)]['delivery_f'], color ="red", density=True, bins=80, alpha = 0.3, label="modeled")
#plt.hist(df_hh_model[(df_hh_model[ic_nm]==1)]['delivery_f'], color ="red", density=True, bins=df_hh_model[(df_hh_model[ic_nm]==1)]['delivery_f'].max(), alpha = 0.3, label="modeled")
plt.hist(df_per_obs[(df_per_obs['DELIV_GOOD']<=60)]['DELIV_GOOD'], color ="blue", density=True, bins=df_per_obs[(df_per_obs['DELIV_GOOD']<=60)]['DELIV_GOOD'].max(), alpha = 0.3, label="observed", weights=df_per_obs[(df_per_obs['DELIV_GOOD']<=60)]['WTPERFIN'])
plt.hist(df_per_final[(df_per_final['DELIV_GOOD']<=60)]['DELIV_GOOD'], color ="red", density=True, bins=df_per_final[(df_per_final['DELIV_GOOD']<=60)]['DELIV_GOOD'].max(), alpha = 0.3, label="modeled")
plt.title("Density of Delivery Frequency")
plt.legend(loc="upper right")
plt.savefig('../../../FRISM_input_output_ST/Sim_outputs/Generation/B2C_delivery_val_all.png')

# %%
plt.figure(figsize = (8,6))
#plt.hist(df_hh_obs[df_hh_obs[ic_nm]==1]['delivery_f'], color ="blue", density=True, bins=df_hh_obs[df_hh_obs[ic_nm]==1]['delivery_f'].max(), alpha = 0.3, label="observed")
#plt.hist(df_hh_model[(df_hh_model[ic_nm]==1) & (df_hh_model['delivery_f']<=30)]['delivery_f'], color ="red", density=True, bins=80, alpha = 0.3, label="modeled")
#plt.hist(df_hh_model[(df_hh_model[ic_nm]==1)]['delivery_f'], color ="red", density=True, bins=df_hh_model[(df_hh_model[ic_nm]==1)]['delivery_f'].max(), alpha = 0.3, label="modeled")
plt.hist(df_per_obs[(df_per_obs['DELIV_FOOD']<=60)]['DELIV_FOOD'], color ="blue", density=True, bins=df_per_obs[(df_per_obs['DELIV_FOOD']<=60)]['DELIV_FOOD'].max(), alpha = 0.3, label="observed", weights=df_per_obs[(df_per_obs['DELIV_FOOD']<=60)]['WTPERFIN'])
plt.hist(df_per_final[(df_per_final['DELIV_FOOD']<=60)]['DELIV_FOOD'], color ="red", density=True, bins=df_per_final[(df_per_final['DELIV_FOOD']<=60)]['DELIV_FOOD'].max(), alpha = 0.3, label="modeled")
plt.title("Density of Delivery Frequency")
plt.legend(loc="upper right")
plt.savefig('../../../FRISM_input_output_ST/Sim_outputs/Generation/B2C_food_val_all.png')
# %%
plt.figure(figsize = (8,6))
#plt.hist(df_hh_obs[df_hh_obs[ic_nm]==1]['delivery_f'], color ="blue", density=True, bins=df_hh_obs[df_hh_obs[ic_nm]==1]['delivery_f'].max(), alpha = 0.3, label="observed")
#plt.hist(df_hh_model[(df_hh_model[ic_nm]==1) & (df_hh_model['delivery_f']<=30)]['delivery_f'], color ="red", density=True, bins=80, alpha = 0.3, label="modeled")
#plt.hist(df_hh_model[(df_hh_model[ic_nm]==1)]['delivery_f'], color ="red", density=True, bins=df_hh_model[(df_hh_model[ic_nm]==1)]['delivery_f'].max(), alpha = 0.3, label="modeled")
plt.hist(df_per_obs[(df_per_obs['DELIV_GROC']<=60)]['DELIV_GROC'], color ="blue", density=True, bins=df_per_obs[(df_per_obs['DELIV_GROC']<=60)]['DELIV_GROC'].max(), alpha = 0.3, label="observed", weights=df_per_obs[(df_per_obs['DELIV_GROC']<=60)]['WTPERFIN'])
plt.hist(df_per_final[(df_per_final['DELIV_GROC']<=60)]['DELIV_GROC'], color ="red", density=True, bins=df_per_final[(df_per_final['DELIV_GROC']<=60)]['DELIV_GROC'].max(), alpha = 0.3, label="modeled")
plt.title("Density of Delivery Frequency")
plt.legend(loc="upper right")
plt.savefig('../../../FRISM_input_output_ST/Sim_outputs/Generation/B2C_grovery_val_all.png')


