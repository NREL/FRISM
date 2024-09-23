# %%
from tkinter import X
import pandas as pd
import numpy as np
import joblib
from argparse import ArgumentParser
import config_SF as config
import random

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

hh_file= "../../../FRISM_input_output_SF/Sim_inputs/hh_pop/sfbay_2018/households.csv.zip"
per_file= "../../../FRISM_input_output_SF/Sim_inputs/hh_pop/sfbay_2018/persons.csv.zip"

synth_hh = pd.read_csv(hh_file, header=0, sep=',')
synth_per = pd.read_csv(per_file, header=0, sep=',')

df_hh = input_files_processing_hh(hh_file)
df_per= input_files_processing_per(df_hh, per_file)

import geopandas as gpd
fdir_geo = "../../../FRISM_input_output_SF/Sim_inputs/Geo_data/"
CBG_file = 'BayArea_freight.geojson'
state_id="06"
CBGzone_df = gpd.read_file(fdir_geo+CBG_file) # file include, GEOID(12digit), MESOZONE, area
CBGzone_df= CBGzone_df.to_crs({'proj': 'cea'})
CBGzone_df["GEOID"]=CBGzone_df["GEOID"].astype(str)
## Add county id from GEOID
CBGzone_df["County"]=CBGzone_df["GEOID"].apply(lambda x: x[2:5] if (len(x)>=12 and x[0:2]==str(state_id))  else 0)
CBGzone_df["County"]=CBGzone_df["County"].astype(str).astype(int)
CBGzone_df["GEOID"]=CBGzone_df["GEOID"].astype(str).astype(int)
CBGzone_df=CBGzone_df[CBGzone_df["County"]!=0]
CBGzone_df= CBGzone_df.to_crs('EPSG:4269')

# %%
CBGzone_df=CBGzone_df[CBGzone_df["County"].isin([1, 13, 41, 55, 75, 81, 85, 95, 97])]
CBGzone_df.head()
df_per['GEOID'] =df_per['block_id'].apply(lambda x: np.floor(x/1000))
df_per= df_per.merge(CBGzone_df[["GEOID", "County"]], on='GEOID', how='left')
def urban(county):
    if county in [1,75,81,85]:
        return 1
    else: return 0    

df_per['URBRUR']=df_per["County"].apply(lambda x: urban(x))
# df_hh = input_files_processing_hh(args.hh_file)
# df_per= input_files_processing_per(df_hh, args.per_file)
# %%
loaded_model = joblib.load('online_choice_good.sav')
df_per['pro_online_choice_good']=loaded_model.predict(df_per)
df_per['online_choice_good']=df_per['pro_online_choice_good'].apply(lambda x: 1 if random.uniform(0, 1) < x else 0) 

loaded_model = joblib.load('online_choice_food.sav')
df_per['pro_online_choice_food']=loaded_model.predict(df_per)
df_per['online_choice_food']=df_per['pro_online_choice_food'].apply(lambda x: 1 if random.uniform(0, 1) < x else 0)     

loaded_model = joblib.load('online_choice_grc.sav')
df_per['pro_online_choice_grc']=loaded_model.predict(df_per)
df_per['online_choice_grc']=df_per['pro_online_choice_grc'].apply(lambda x: 1 if random.uniform(0, 1) < x else 0)     

sel_df_per= df_per[df_per['online_choice_good']==1].reset_index()
selected_x_var_per= ['R_AGE','HHSIZE', 'WORKER',
                    "EDUC_1",'EDUC_2',
                    'income_cls_1', 'income_cls_2', 'income_cls_3', 'income_cls_4','income_cls_5',"URBRUR",
                    ]
sel_df_per_temp=sel_df_per[selected_x_var_per]

loaded_model = joblib.load('freq_good.sav')
sel_df_per['DELIV_GOOD']=loaded_model.predict(sel_df_per_temp)
sel_df_per['DELIV_GOOD']=sel_df_per['DELIV_GOOD'].apply(lambda x: round(x))
df_per=df_per.merge(sel_df_per[['household_id','member_id', 'DELIV_GOOD']], on=['household_id','member_id'], how='left')
df_per["DELIV_GOOD"].fillna(0, inplace=True)
#df_per["DELIV_GROC"]=df_per["DELIV_GROC"].apply(lambda x: random.randrange(40,70) if x>=40 else x)
#plt.hist(df_per["DELIV_GOOD"], color ="blue", bins = int(df_per["DELIV_GOOD"].max()))
# adding update the adjustment of frequency 
######
# %%
sel_df_per= df_per[df_per['online_choice_grc']==1].reset_index()
selected_x_var_per= ['R_AGE','HHSIZE','WORKER',
                    'DELIV_GOOD',"URBRUR",
                    'income_cls_1', 'income_cls_2', 'income_cls_3', 'income_cls_4','income_cls_5']
sel_df_per_temp=sel_df_per[selected_x_var_per]

loaded_model = joblib.load('freq_grc.sav')
sel_df_per['DELIV_GROC']=loaded_model.predict(sel_df_per_temp)
sel_df_per['DELIV_GROC']=sel_df_per['DELIV_GROC'].apply(lambda x: round(x))
df_per=df_per.merge(sel_df_per[['household_id','member_id', 'DELIV_GROC']], on=['household_id','member_id'], how='left')
df_per["DELIV_GROC"].fillna(0, inplace=True)
df_per["DELIV_GROC"]=df_per["DELIV_GROC"].apply(lambda x: random.randrange(20,40) if x>=20 else x)
#plt.hist(df_per["DELIV_GROC"], color ="blue", bins = int(df_per["DELIV_GROC"].max()))

# adding update the adjustment of frequency 
# %%
sel_df_per= df_per[df_per['online_choice_food']==1].reset_index()
selected_x_var_per= ['R_AGE','HHSIZE','WORKER','R_SEX_IMP',
                    'DELIV_GROC','URBRUR','income_cls_1', 'income_cls_2', 'income_cls_3', 'income_cls_4','income_cls_5',
                    "URBRUR"]
sel_df_per_temp=sel_df_per[selected_x_var_per]
loaded_model = joblib.load('freq_food.sav')
sel_df_per['DELIV_FOOD']=loaded_model.predict(sel_df_per_temp)
sel_df_per['DELIV_FOOD']=sel_df_per['DELIV_FOOD'].apply(lambda x: round(x))
df_per=df_per.merge(sel_df_per[['household_id','member_id', 'DELIV_FOOD']], on=['household_id','member_id'], how='left')
df_per["DELIV_FOOD"].fillna(0, inplace=True)
df_per["DELIV_FOOD"]=df_per["DELIV_FOOD"].apply(lambda x: random.randrange(20,40) if x>=20 else x)
#plt.hist(df_per["DELIV_FOOD"], color ="blue", bins = int(df_per["DELIV_FOOD"].max()))

df_per_final=df_per[["household_id","member_id",'block_id','GEOID',"County", "DELIV_GOOD","DELIV_GROC","DELIV_FOOD"]]
df_per_final.to_csv("../../../FRISM_input_output_SF/Sim_outputs/Generation/per_del_2018.csv")
#####
# %%
def b2c_good_select(delivery_f,fq_factor,growth_factor,commodity_type):
    growth_factor=growth_factor+(growth_factor/100)**6
    if commodity_type == "goods":   
        day_factor = random.randrange(fq_factor,31)
    else: day_factor =50      
    pro=delivery_f/day_factor
    r= random.uniform(0,1)*(100/growth_factor)
    if r <= pro:
        select =1
        num_package=max(1,round(pro))
    else:
        select =0
        num_package=0
    return num_package


def package_aggregation(num, commodity_type):
    if commodity_type == "goods":
        if num >4:  
            agg_package = random.randrange(3,5)
            if num >= agg_package:
                return agg_package
            else: return num
        else:
            agg_package = random.randrange(1,5)
            if num >= agg_package:
                return agg_package
            else: return num
    else:            
        agg_package = random.randrange(1,4)
        if num >= agg_package:
            return agg_package
        else: return num
fq_factor=20
df_per["online_goods_act"]= df_per["DELIV_GOOD"].apply(lambda x: b2c_good_select(x,fq_factor, 100,"goods"))
df_per["online_grocery_act"]= df_per["DELIV_GROC"].apply(lambda x: b2c_good_select(x,fq_factor,100,"other"))
df_per["online_food_act"]= df_per["DELIV_FOOD"].apply(lambda x: b2c_good_select(x,fq_factor,100,"other"))
    
# Need to process df_per
# ## additing the code
#
# %%  
loaded_model = joblib.load('instore_choice_goods.sav')
df_per['pro_instore_choice_good']=loaded_model.predict(df_per)
df_per['instore_choice_good']=df_per['pro_instore_choice_good'].apply(lambda x: 1 if random.uniform(0, 1) < x else 0) 

loaded_model = joblib.load('instore_choice_food.sav')
df_per['pro_instore_choice_food']=loaded_model.predict(df_per)
df_per['instore_choice_food']=df_per['pro_instore_choice_food'].apply(lambda x: 1 if random.uniform(0, 1) < x else 0)     

loaded_model = joblib.load('instore_choice_grc.sav')
df_per['pro_instore_choice_grc']=loaded_model.predict(df_per)
df_per['instore_choice_grc']=df_per['pro_instore_choice_grc'].apply(lambda x: 1 if random.uniform(0, 1) < x else 0)  


df_per=df_per.rename({'DELIV_GOOD':'daily_delivery_frequency_goods',
                      'DELIV_GROC':'daily_delivery_frequency_grocery',
                      'DELIV_FOOD':'daily_delivery_frequency_food',
                      'pro_instore_choice_good':'probability_instore_choice_goods',
                      'pro_instore_choice_grc':'probability_instore_choice_grocery',
                      'pro_instore_choice_food':'probability_instore_choice_food'}, axis='columns')
# %%
df_per_for_merge= df_per[["household_id","member_id",'daily_delivery_frequency_goods','daily_delivery_frequency_grocery','daily_delivery_frequency_food',
                          "probability_instore_choice_goods","probability_instore_choice_grocery","probability_instore_choice_food"]]


synth_per=synth_per.merge(df_per_for_merge, on=["household_id","member_id"], how='left')
syth_per=synth_per["daily_delivery_frequency_goods"].fillna(0, inplace=True)
syth_per=synth_per["daily_delivery_frequency_grocery"].fillna(0, inplace=True)
syth_per=synth_per["daily_delivery_frequency_food"].fillna(0, inplace=True)
syth_per=synth_per["probability_instore_choice_goods"].fillna(0, inplace=True)
syth_per=synth_per["probability_instore_choice_grocery"].fillna(0, inplace=True)
syth_per=synth_per["probability_instore_choice_food"].fillna(0, inplace=True)

synth_per[(synth_per["household_id"]==472)&(synth_per["member_id"]==10)][["probability_instore_choice_goods"]]

# %%
synth_per.to_csv("../../../FRISM_input_output_SF/Sim_outputs/Generation/persons_w_instore_prob.csv.gz", compression="gzip", index=False)
# %%
####################################Code for merge #######################################################################################
# %%
sel_county =1
possilbe_delivey_days=30
growth_factor =100


#df_per_final = pd.read_csv(fdir_in_out+'/Sim_outputs/Generation/households_del_{}.csv'.format(str(year)), header=0, sep=',')
df_per_final = df_per_final.merge(CBGzone_df[['GEOID','MESOZONE']], on='GEOID', how='left')
if sel_county != 9999:
    df_per_final= df_per_final[df_per_final['County']==sel_county].reset_index(drop=True)

df_per_final[['D_selection_goods', 'D_num_goods']] = df_per_final['DELIV_GOOD'].apply(lambda x: b2c_good_select(x, possilbe_delivey_days,growth_factor)).to_list()
df_per_final[['D_selection_groc', 'D_num_groc']] = df_per_final['DELIV_GROC'].apply(lambda x: b2c_good_select(x, possilbe_delivey_days,growth_factor)).to_list()
df_per_final[['D_selection_food', 'D_num_food']] = df_per_final['DELIV_FOOD'].apply(lambda x: b2c_good_select(x, possilbe_delivey_days,growth_factor)).to_list()

df_per_goods= df_per_final[df_per_final['D_selection_goods']==1].reset_index(drop=True)
df_per_groc= df_per_final[df_per_final['D_selection_groc']==1].reset_index(drop=True)
df_per_food= df_per_final[df_per_final['D_selection_food']==1].reset_index(drop=True)

[["household_id","member_id",'block_id','GEOID',"County", "DELIV_GOOD","DELIV_GROC","DELIV_FOOD"]]
df_hh_goods = df_per_goods.groupby(["household_id",'block_id','GEOID',"County"])["D_num_goods"].agg(hh_num_goods='sum').reset_index()
df_hh_groc = df_per_groc.groupby(["household_id",'block_id','GEOID',"County"])["D_num_groc"].agg(hh_num_groc='sum').reset_index()
df_hh_food = df_per_food.groupby(["household_id",'block_id','GEOID',"County"])["D_num_food"].agg(hh_num_food='sum').reset_index()

df_hh_goods["hh_del_goods"]=df_hh_goods["hh_num_goods"].apply(lambda x: package_aggregation(x, "goods") )
df_hh_groc["hh_del_groc"]=df_hh_groc["hh_num_groc"].apply(lambda x: package_aggregation(x, "groc") )
df_hh_food["hh_del_food"]=df_hh_food["hh_num_food"].apply(lambda x: package_aggregation(x, "food") )

df_hh_goods_delivery =pd.DataFrame()
for i in range (0, df_hh_goods.shape[0]):
    num_package=df_hh_goods['hh_del_goods'].iloc[i]
    df_hh_goods_delivery=pd.concat([df_hh_goods_delivery,pd.concat([df_hh_goods.iloc[[i]]]*num_package, ignore_index=True)], ignore_index=True)

df_hh_groc_delivery =pd.DataFrame()
for i in range (0, df_hh_groc.shape[0]):
    num_package=df_hh_groc['hh_del_groc'].iloc[i]
    df_hh_groc_delivery=pd.concat([df_hh_groc_delivery,pd.concat([df_hh_groc.iloc[[i]]]*num_package, ignore_index=True)], ignore_index=True)

df_hh_food_delivery =pd.DataFrame()
for i in range (0, df_hh_food.shape[0]):
    num_package=df_hh_food['hh_del_food'].iloc[i]
    df_hh_food_delivery=pd.concat([df_hh_food_delivery,pd.concat([df_hh_food.iloc[[i]]]*num_package, ignore_index=True)], ignore_index=True)    


df_hh_goods_delivery["shipment_id"] =np.arange(df_hh_goods_delivery.shape[0])
# %%  
df_hh_goods_delivery["D_truckload"]=df_hh_goods_delivery["hh_del_goods"].apply(b2c_d_truckload)




# %%
# def b2c_good_select(delivery_f,good_type):
#     #growth_factor=growth_factor+(growth_factor/100)**6
#     if good_type=="goods":
#         if delivery_f <=10:
#             day_factor = random.randrange(10,25)
#         elif delivery_f > 10 and delivery_f <=20:
#             day_factor = random.randrange(15,30)
#         elif delivery_f > 20:
#             day_factor = random.randrange(20,30)
#     else:             
#         if delivery_f <=10:
#             day_factor = random.randrange(10,25)
#         elif delivery_f > 10 and delivery_f <=20:
#             day_factor = random.randrange(15,30)
#         elif delivery_f > 20:
#             day_factor = random.randrange(20,30)
#     pro=delivery_f/day_factor
#     r= random.uniform(0,1)#*(100/growth_factor)
#     if r <= pro:
#         num_package=max(1,round(pro))
#     else:
#         num_package=0
#     return num_package
# %%
def b2c_good_select(delivery_f,good_type):
    #growth_factor=growth_factor+(growth_factor/100)**6
    day_factor = random.randrange(20,35)  
    pro=delivery_f/day_factor
    r= random.uniform(0,1)#*(100/growth_factor)
    if r <= pro:
        num_package=max(1,round(pro))
    else:
        num_package=0
    return num_package



df_per["online_goods_act"]= df_per["DELIV_GOOD"].apply(lambda x: b2c_good_select(x,"goods"))
df_per["online_grocery_act"]= df_per["DELIV_GROC"].apply(lambda x: b2c_good_select(x,"other"))
df_per["online_food_act"]= df_per["DELIV_FOOD"].apply(lambda x: b2c_good_select(x,"other"))
    
# Need to process df_per
# ## additing the code
#  
loaded_model = joblib.load('instore_choice_goods.sav')
df_per['pro_instore_choice_good']=loaded_model.predict(df_per)
df_per['instore_choice_good']=df_per['pro_instore_choice_good'].apply(lambda x: 1 if random.uniform(0, 1) < x else 0) 

loaded_model = joblib.load('instore_choice_food.sav')
df_per['pro_instore_choice_food']=loaded_model.predict(df_per)
df_per['instore_choice_food']=df_per['pro_instore_choice_food'].apply(lambda x: 1 if random.uniform(0, 1) < x else 0)     

loaded_model = joblib.load('instore_choice_grc.sav')
df_per['pro_instore_choice_grc']=loaded_model.predict(df_per)
df_per['instore_choice_grc']=df_per['pro_instore_choice_grc'].apply(lambda x: 1 if random.uniform(0, 1) < x else 0)     

#df_per= df_per.merge(df_hh[['household_id','block_id']], on='household_id', how='left')  

df_per['GEOID'] =df_per['block_id'].apply(lambda x: np.floor(x/1000))
# %%
'''
Index(['Unnamed: 0', 'school_zone_id', 'hispanic.1', 'WORKER', 'R_RACE',
       'earning', 'p_hispanic', 'SCHTYP', 'relate', 'hispanic', 'R_SEX_IMP',
       'WRK_HOME', 'person_age', 'person_sex', 'race', 'R_AGE', 'work_zone_id',
       'MAR', 'member_id', 'hours', 'household_id', 'EDUC', 'hh_workers',
       'hh_income', 'gt2', 'CHILD', 'HHVEHCNT', 'hispanic_status_of_head',
       'recent_mover', 'hh_race_of_head', 'sf_detached', 'income', 'WRKCOUNT',
       'seniors', 'lcm_county_id', 'gt55', 'hh_age_of_head', 'serialno',
       'age_of_head', 'tenure_mover', 'hh_seniors', 'HOMEOWN', 'hispanic_head',
       'block_id', 'HH_RACE', 'hh_size', 'hh_cars', 'hh_type', 'HHSIZE',
       'income_est', 'income_cls', 'HH_RACE_0', 'HH_RACE_1', 'HH_RACE_2',
       'HH_RACE_3', 'income_cls_0', 'income_cls_1', 'income_cls_2',
       'income_cls_3', 'income_cls_4', 'income_cls_5', 'R_AGE_C', 'EDUC_0',
       'EDUC_1', 'EDUC_2', 'EDUC_3', 'R_AGE_C_0', 'R_AGE_C_1', 'R_AGE_C_2',
       'R_AGE_C_3', 'R_AGE_C_4', 'R_RACE_0', 'R_RACE_1', 'R_RACE_2',
       'R_RACE_3', 'URBRUR', 'pro_online_choice_good', 'online_choice_good',
       'pro_online_choice_food', 'online_choice_food', 'pro_online_choice_grc',
       'online_choice_grc', 'DELIV_GOOD', 'DELIV_GROC', 'DELIV_FOOD',
       'online_goods_act', 'online_grocery_act', 'online_food_act',
       'pro_instore_choice_good', 'instore_choice_good',
       'pro_instore_choice_food', 'instore_choice_food',
       'pro_instore_choice_grc', 'instore_choice_grc', 'GEOID',
       'day_online_goods', 'day_online_grocery', 'day_online_food'],
      dtype='object')

'''
df_per["day_online_goods"]=df_per['online_goods_act'].apply(lambda x: 1 if x>=1 else 0)
df_per["day_online_grocery"]=df_per['online_grocery_act'].apply(lambda x: 1 if x>=1 else 0) 
df_per["day_online_food"]=df_per['online_food_act'].apply(lambda x: 1 if x>=1 else 0)
df_temp=df_per[df_per["day_online_goods"]==1]
df_temp['instore_choice_good'].sum()
# %%
vars=['online_goods_act', 'online_grocery_act', 'online_food_act',
'R_RACE_0', 'R_RACE_1', 'R_RACE_2','R_RACE_3',
'income_cls_0', 'income_cls_1', 'income_cls_2','income_cls_3', 'income_cls_4','income_cls_5',
'R_AGE_C_0', 'R_AGE_C_1', 'R_AGE_C_2','R_AGE_C_3', 'R_AGE_C_4',
'R_SEX_IMP','HHSIZE','CHILD','pro_instore_choice_good', 'instore_choice_good',
       'pro_instore_choice_food', 'instore_choice_food',
       'pro_instore_choice_grc', 'instore_choice_grc']
df_temp=df_temp[vars]
df_temp.to_csv("../../../FRISM_input_output_SF/Sim_inputs/hh_pop/sfbay_2018/df_temp.csv")

# %%
df_temp=df_per[df_per["day_online_goods"]==1]
df_temp['instore_choice_good'].sum()
vars=['R_AGE_C_1','R_AGE_C_2','R_AGE_C_3','R_AGE_C_4',
              'EDUC_1','EDUC_2',
              'income_cls_1','income_cls_2','income_cls_3','income_cls_4','income_cls_5',
              'HHSIZE','R_SEX_IMP','WORKER','HOMEOWN',"pro_online_choice_good"]
df_temp=df_temp[vars]
df_temp.to_csv("../../../FRISM_input_output_SF/Sim_inputs/hh_pop/sfbay_2018/df_temp_v2.csv")





# %%    
import geopandas as gpd
fdir_geo = "../../../FRISM_input_output_SF/Sim_inputs/Geo_data/"
CBG_file = 'SFBay_freight.geojson'
state_id="06"
CBGzone_df = gpd.read_file(fdir_geo+CBG_file) # file include, GEOID(12digit), MESOZONE, area
CBGzone_df= CBGzone_df.to_crs({'proj': 'cea'})
CBGzone_df["GEOID"]=CBGzone_df["GEOID"].astype(str)
## Add county id from GEOID
CBGzone_df["County"]=CBGzone_df["GEOID"].apply(lambda x: x[2:5] if (len(x)>=12 and x[0:2]==str(state_id))  else 0)
CBGzone_df["County"]=CBGzone_df["County"].astype(str).astype(int)
CBGzone_df["GEOID"]=CBGzone_df["GEOID"].astype(str).astype(int)
CBGzone_df=CBGzone_df[CBGzone_df["County"]!=0]
CBGzone_df= CBGzone_df.to_crs('EPSG:4269')

# %%
CBGzone_df=CBGzone_df[CBGzone_df["County"].isin([1, 13, 41, 55, 75, 81, 85, 95, 97])]
CBGzone_df.head()


# %%
df_per_by_block=df_per.groupby(['GEOID'])['online_goods_act'].agg(num_delivery='sum').reset_index()
df_per_by_block=df_per.groupby(['GEOID']).agg(num_delivery=('online_goods_act','sum'),
                                              num_people=('GEOID','count')).reset_index()
df_per_by_block['delivery_capita']=df_per_by_block['num_delivery']/df_per_by_block['num_people']
df_per_by_block= df_per_by_block[df_per_by_block['delivery_capita']<1]
CBGzone_delivery = CBGzone_df.merge(df_per_by_block[['GEOID','delivery_capita']], on='GEOID', how='left')
CBGzone_delivery.plot(column='delivery_capita', legend=True, cmap='Reds')




df_per_by_block=df_per.groupby(['GEOID']).agg(num_delivery=('online_grocery_act','sum'),
                                              num_people=('online_grocery_act','count')).reset_index()
df_per_by_block['delivery_capita']=df_per_by_block['num_delivery']/df_per_by_block['num_people']
df_per_by_block= df_per_by_block[df_per_by_block['delivery_capita']<1]
CBGzone_delivery = CBGzone_df.merge(df_per_by_block[['GEOID','delivery_capita']], on='GEOID', how='left')
CBGzone_delivery.plot(column='delivery_capita', legend=True, cmap='Reds')




df_per_by_block=df_per.groupby(['GEOID']).agg(num_delivery=('online_food_act','sum'),
                                              num_people=('online_food_act','count')).reset_index()
df_per_by_block['delivery_capita']=df_per_by_block['num_delivery']/df_per_by_block['num_people']
df_per_by_block= df_per_by_block[df_per_by_block['delivery_capita']<1]
CBGzone_delivery = CBGzone_df.merge(df_per_by_block[['GEOID','delivery_capita']], on='GEOID', how='left')
CBGzone_delivery.plot(column='delivery_capita', legend=True, cmap='Reds')


# CBGzone_delivery = CBGzone_df.merge(df_per_by_block[['GEOID','num_delivery']], on='GEOID', how='left')
# CBGzone_delivery.plot(column='num_delivery', legend=True)
df_per_by_block=df_per.groupby(['GEOID'])['online_goods_act'].agg(num_delivery='sum').reset_index()
CBGzone_delivery = CBGzone_df.merge(df_per_by_block[['GEOID','num_delivery']], on='GEOID', how='left')
CBGzone_delivery.plot(column='num_delivery', legend=True, cmap='Reds')


df_per_by_block=df_per.groupby(['GEOID'])['online_grocery_act'].agg(num_delivery='sum').reset_index()
CBGzone_delivery = CBGzone_df.merge(df_per_by_block[['GEOID','num_delivery']], on='GEOID', how='left')
CBGzone_delivery.plot(column='num_delivery', legend=True, cmap='Reds')

df_per_by_block=df_per.groupby(['GEOID'])['online_food_act'].agg(num_delivery='sum').reset_index()
CBGzone_delivery = CBGzone_df.merge(df_per_by_block[['GEOID','num_delivery']], on='GEOID', how='left')
CBGzone_delivery.plot(column='num_delivery', legend=True, cmap='Reds')

# %%

df_per["day_online_goods"]=df_per['online_goods_act'].apply(lambda x: 1 if x>=1 else 0)
df_per["day_online_grocery"]=df_per['online_grocery_act'].apply(lambda x: 1 if x>=1 else 0) 
df_per["day_online_food"]=df_per['online_food_act'].apply(lambda x: 1 if x>=1 else 0)
df_temp=df_per[df_per["day_online_goods"]==1]
df_temp['instore_choice_good'].sum()
df_temp=df_per[df_per["day_online_grocery"]==1]
df_temp['instore_choice_grc'].sum()
df_temp=df_per[df_per["day_online_food"]==1]
df_temp['instore_choice_food'].sum()

# %%
df_temp=df_per[df_per["day_online_goods"]==1]
df_per_by_block=df_temp.groupby(['GEOID']).agg(num_instore=("instore_choice_good", "sum"),
                                              num_online=("day_online_goods", "sum")).reset_index()
df_per_by_block["ratio of both"]= df_per_by_block.apply(lambda x: x["num_instore"]/x["num_online"] if x["num_online"] >0 else 0, axis=1)
df_per_by_block= df_per_by_block[df_per_by_block['ratio of both']<1]
CBGzone_delivery = CBGzone_df.merge(df_per_by_block[['GEOID','ratio of both']], on='GEOID', how='left')
CBGzone_delivery.plot(column='ratio of both', legend=True, cmap='Reds')

df_temp=df_per[df_per["day_online_grocery"]==1]
df_per_by_block=df_temp.groupby(['GEOID']).agg(num_instore=("instore_choice_grc", "sum"),
                                              num_online=("day_online_grocery", "sum")).reset_index()
df_per_by_block["ratio of both"]= df_per_by_block.apply(lambda x: x["num_instore"]/x["num_online"] if x["num_online"] >0 else 0, axis=1)
CBGzone_delivery = CBGzone_df.merge(df_per_by_block[['GEOID','ratio of both']], on='GEOID', how='left')
CBGzone_delivery.plot(column='ratio of both', legend=True, cmap='Reds')

df_temp=df_per[df_per["day_online_food"]==1]
df_per_by_block=df_temp.groupby(['GEOID']).agg(num_instore=("instore_choice_food", "sum"),
                                              num_online=("day_online_food", "sum")).reset_index()
df_per_by_block["ratio of both"]= df_per_by_block.apply(lambda x: x["num_instore"]/x["num_online"] if x["num_online"] >0 else 0, axis=1)
CBGzone_delivery = CBGzone_df.merge(df_per_by_block[['GEOID','ratio of both']], on='GEOID', how='left')
CBGzone_delivery.plot(column='ratio of both', legend=True, cmap='Reds')

## assign to on_demand
# %%
fdir_geo = "../../../FRISM_input_output_SF/Sim_inputs/Geo_data/"
property_file = 'Property Type in SF Bay Area.geojson'
pro_df = gpd.read_file(fdir_geo+property_file) # file include, GEOID(12digit), MESOZONE, area
# pro_df= pro_df.to_crs({'proj': 'cea'})
pro_df= pro_df.to_crs(4269)

pro_df=pro_df.sjoin(CBGzone_df, how="inner",  predicate='intersects')

food_df= pro_df[pro_df["Classified 0424"]=='Food'].reset_index()
grc_df= pro_df[pro_df["Classified 0424"]=='grocery'].reset_index()

grc_df_group = grc_df.groupby(['GEOID','MESOZONE'])['MESOZONE'].agg(num_store='count').reset_index()

df_per_food=df_per[df_per["online_food_act"]>0].sample(frac=0.1).reset_index(drop=True)
df_per_grc= df_per[df_per["online_grocery_act"]>0].sample(frac=0.1).reset_index(drop=True)

travel_file = fdir_geo+"tt_df_cbg_v2.csv.gz"
tt_df = pd.read_csv(travel_file, compression='gzip', header=0, sep=',', quotechar='"')

def tt_cal(org_geoID, dest_geoID, sel_tt):
    try:
        travel_time = sel_tt['TIME_minutes'].to_numpy()[(sel_tt['origin'].to_numpy() == org_geoID)
                                              &(sel_tt['destination'].to_numpy() == dest_geoID)].item()
    except:
        10
    return travel_time




dest= df_per_grc["GEOID"].loc[0]

def assign_store(dest,df_group,loc_df):
    df_group["travel_time"]=df_group['GEOID'].apply(lambda x: tt_cal(x,dest, tt_df))
    # df_group["travel_time_bin"]=df_group["travel_time"].apply(lambda x: int(x/10+1)*10)
    # tt_inverse=1/df_group["travel_time_bin"].unique()
    # tt_inverse.sum()
    # df_group["pro"]=df_group["travel_time_bin"].apply(lambda x: (1/x)/tt_inverse.sum())
    sel_df_group= df_group[df_group["travel_time"] <=40].reset_index()
    if sel_df_group.shape[0] ==0:
        sel_df_group= df_group[df_group["travel_time"] <=60].reset_index()
    if sel_df_group.shape[0] ==0:
        sel_df_group= df_group
    sel_df_group["travel_time_bin"]=sel_df_group["travel_time"].apply(lambda x: int(x/10+1)*10)
    tt_inverse=1/sel_df_group["travel_time_bin"].unique()
    tt_inverse.sum()
    sel_df_group["pro"]=sel_df_group["travel_time_bin"].apply(lambda x: (1/x)/tt_inverse.sum())
    weighted_prob_sum= (sel_df_group["pro"]*sel_df_group["num_store"]).sum()
    sel_df_group["weighted_pro"]= sel_df_group.apply(lambda x: (x['pro']*x["num_store"])/weighted_prob_sum, axis=1)
    org= random.choices(list(sel_df_group['GEOID']), list(sel_df_group["pro"]),k=1)[0]
    selcted_loc_df = loc_df[loc_df["GEOID"]==org]
    [[y,x]]=selcted_loc_df[["latitude", "longitude"]].sample(n=1).values.tolist()
    tt=sel_df_group[sel_df_group["GEOID"]==org]["travel_time"].values[0]

    return x,y,org, tt 


payloads = pd.DataFrame(columns = ["payloadId",
                                   	"sequenceRank",
                                    "tourId", 
                                    "payloadType",	
                                    "weightInlb",	
                                    "cummulativeWeightInlb",	
                                    "requestType",	
                                    "locationZone",
                                    "estimatedTimeOfArrivalInSec",	
                                    "arrivalTimeWindowInSec_lower",	
                                    "arrivalTimeWindowInSec_upper",	
                                    "operationDurationInSec",	
                                    "locationZone_x",	
                                    "locationZone_y",	
                                    "true_locationZone",
                                    "BuyerNAICS",	
                                    "SellerNAICS",	
                                    "truck_mode"])


def time_normal(mean, std, min_time,max_time):
    time = (np.random.normal(0,std)+mean)*60
    if time < min_time*60 or time > max_time*60 :
        time= random.randrange((mean)*60,max_time*60, 10)
    return int(time)  

def order_time(goods_type):
    if goods_type == "grocery":
        d_time= random.randrange(8*60,17*60, 10)
    elif goods_type == "food":            
        if random.uniform(0, 1) <= 0.4:
            d_time =time_normal(12, 2, 10, 16)
        else:     
            d_time =time_normal(18, 2, 15, 21)

    return d_time *60
from shapely.geometry import Point
def random_points_in_polygon(polygon):
    temp = polygon.bounds
    finished= False
    while not finished:
        point = Point(random.uniform(temp.minx.values[0], temp.maxx.values[0]), random.uniform(temp.miny.values[0], temp.maxy.values[0]))
        finished = polygon.contains(point).values[0]
    return [point.x, point.y]

df_per_grc_temp =df_per_grc.iloc[0:10]
n=0
for i in range(0,df_per_grc_temp.shape[0]):
    goods_type="grocery"
    dest_geoid= df_per_grc_temp["GEOID"].loc[0]
    dest_mesoid= CBGzone_df[CBGzone_df['GEOID']==dest_geoid]['MESOZONE'].values[0]
    [dest_x,dest_y]=random_points_in_polygon(CBGzone_df.geometry[CBGzone_df.MESOZONE==dest_mesoid])
    org_x, org_y, org_geoid, tt=assign_store(dest_geoid,grc_df_group,grc_df)
    org_mesoid= CBGzone_df[CBGzone_df['GEOID']==org_geoid]['MESOZONE'].values[0]

    payloadId="grc_"+str(n)
    weightInlb= random.randrange(0,10)
    org_time= order_time(goods_type)
    org_dwell= random.randrange(5,20)*60
    dest_time= org_time +org_dwell+ int(tt*60)
    dest_dwell= random.randrange(2,10)*60

    temp_org=pd.DataFrame(data={"payloadId": [payloadId],
            "sequenceRank":[0],
            "tourId": [n], 
            "payloadType": [5],	
            "weightInlb": [weightInlb],	
            "cummulativeWeightInlb": [weightInlb] ,	
            "requestType": [3],	
            "locationZone": [org_mesoid] ,
            "estimatedTimeOfArrivalInSec": [org_time],		
            "arrivalTimeWindowInSec_lower":[7*60*60],	
            "arrivalTimeWindowInSec_upper":[22*60*60],	
            "operationDurationInSec": [org_dwell],	
            "locationZone_x": [org_x],	
            "locationZone_y": [org_y],	
            "true_locationZone": [org_mesoid],
            "BuyerNAICS": ["NA"],	
            "SellerNAICS": ["NA"],	
            "truck_mode": ["ondemand"]})
    temp_dest=pd.DataFrame(data={"payloadId": [payloadId],
            "sequenceRank":[1],
            "tourId": [n], 
            "payloadType": [5],	
            "weightInlb": [-weightInlb],	
            "cummulativeWeightInlb": [0] ,	
            "requestType": [3],	
            "locationZone": [dest_mesoid] ,
            "estimatedTimeOfArrivalInSec": [dest_time],		
            "arrivalTimeWindowInSec_lower":[7*60*60],	
            "arrivalTimeWindowInSec_upper":[22*60*60],	
            "operationDurationInSec": [dest_dwell],	
            "locationZone_x": [dest_x],	
            "locationZone_y": [dest_y],	
            "true_locationZone": [dest_mesoid],
            "BuyerNAICS": ["NA"],	
            "SellerNAICS": ["NA"],	
            "truck_mode": ["ondemand"]})
    n=n+1
    payloads=pd.concat([payloads,temp_org, temp_dest],ignore_index=True)
    payloads





# # %%
# CBGzone_df_hh = CBGzone_df.merge(hh_by_block[['GEOID','num_hh']], on='GEOID', how='left')
# CBGzone_df_hh.to_file(fdir_geo+"st_household.geojson", driver="GeoJSON") 
# CBGzone_df_hh.plot(column='num_hh', legend=True)
# for ic in [0,1,2,3]:
#     CBGzone_df_hh_temp = CBGzone_df.merge(hh_by_block_income[hh_by_block_income['ic_group']==ic][['GEOID','num_hh']], on='GEOID', how='left')
#     CBGzone_df_hh_temp.to_file(fdir_geo+"st_household_ic{}.geojson".format(ic), driver="GeoJSON")
#     CBGzone_df_hh_temp.plot(column='num_hh', legend=True)

# # %%

# df_hh = pd.read_csv('../../../FRISM_input_output_ST'+'/Sim_outputs/Generation/households_del_2018.csv', header=0, sep=',')
# df_hh= df_hh[['household_id','delivery_f', 'block_id']]
# df_hh['GEOID'] =df_hh['block_id'].apply(lambda x: np.floor(x/1000))
# df_hh_by_block=df_hh.groupby(['GEOID'])['delivery_f'].agg(sum_delivery='count').reset_index()
# CBGzone_delivery = CBGzone_df.merge(df_hh_by_block[['GEOID','sum_delivery']], on='GEOID', how='left')
# CBGzone_delivery ['avg_daily'] = CBGzone_delivery ['sum_delivery']/20
# # %%
# CBGzone_delivery.plot(column='avg_daily', legend=True)
# CBGzone_delivery.to_file(fdir_geo+"Avg_daily.geojson".format(ic), driver="GeoJSON")
# # %%
# df_daily=pd.DataFrame()
# for c in [33,35,53,61]:
#     df_temp= pd.read_csv('../../../FRISM_input_output_ST'+'/result_0423/Generation/B2C_daily_{}.csv'.format(c), header=0, sep=',')
#     df_daily=pd.concat([df_daily, df_temp], ignore_index=True).reset_index(drop=True)

# df_group= df_daily.groupby(['MESOZONE'])['household_gr_id'].agg(sum_delivery='count').reset_index()
# CBGzone_delivery = CBGzone_df.merge(df_group[['MESOZONE','sum_delivery']], on='MESOZONE', how='left')
# CBGzone_delivery.plot(column='sum_delivery', legend=True)
# CBGzone_delivery.to_file(fdir_geo+"daily_delivery.geojson".format(ic), driver="GeoJSON")
# # %%
# df_daily=pd.DataFrame()
# for c in [33,35,53,61]:
#     df_temp= pd.read_csv('../../../FRISM_input_output_ST'+'/r_tep_v3/Shipment2Fleet/B2C_payload_county{}_shipall_sBase_y2018.csv'.format(c), header=0, sep=',')
#     df_daily=pd.concat([df_daily, df_temp], ignore_index=True).reset_index(drop=True)
# df_daily.to_csv(fdir_geo+"b2c_shipment_all.csv")
# df_group= df_daily.groupby(['del_zone'])['payload_id'].agg(sum_delivery='count').reset_index()
# df_group=df_group.rename({'del_zone':'MESOZONE'}, axis='columns')
# CBGzone_delivery = CBGzone_df.merge(df_group[['MESOZONE','sum_delivery']], on='MESOZONE', how='left')
# CBGzone_delivery.plot(column='sum_delivery', legend=True)
# #CBGzone_delivery.to_file(fdir_geo+"daily_shipment.geojson".format(ic), driver="GeoJSON")




# %%
def sampling_carrier(temp, sample_ratio, bin_size):
    temp_1=temp
    total_size=temp_1.shape[0]
    if (total_size*sample_ratio)/(100) < bin_size:
        bin_size = int((total_size*sample_ratio)/(100))
    try:    
        temp_1["binned_volume"] =pd.qcut(temp_1['n_trucks'], q=bin_size, labels=False)
    except:
        temp_1["binned_volume"]=temp_1['n_trucks'].apply(lambda x:lable_creater(x))
    list_bin_labels = temp_1["binned_volume"].unique().tolist()
    list_shipper_sample=[]
    for bin_id in list_bin_labels:
        temp_2=temp_1[(temp_1['binned_volume']==bin_id)]
        list_shipper = temp_2['BusID'].unique().tolist()
        if (len(list_shipper)*sample_ratio/100 >0) & (len(list_shipper)*sample_ratio/100 <0.5):
            list_shipper= random.sample(list_shipper, int(len(list_shipper)*sample_ratio/100+0.5))
            list_shipper_sample=list_shipper_sample+list_shipper
        elif (len(list_shipper)*sample_ratio/100 >=0.5):     
            list_shipper= random.sample(list_shipper, int(len(list_shipper)*sample_ratio/100+0.5))
            list_shipper_sample=list_shipper_sample+list_shipper             
    df_sample=temp[temp["BusID"].isin(list_shipper_sample)].reset_index(drop=True)

    return df_sample 
def lable_creater(value):
    if value <2:
        return 0
    elif value>=2 and value<4:
        return 1
    elif value >=4 and value <8:
        return 2
    elif value >=8 and value <16:
        return 3    
    elif value >=16 and value <64:
        return 4 
    elif value >=64 and value <128:
        return 5
    elif value >=128 and value <256:
        return 6
    elif value >=256:
        return 7  
f_dir= "/Users/kjeong/KJ_NREL_Work/1_Work/1_2_SMART_2_0/Model_development/FRISM_input_output_SF/Sim_inputs/Synth_firm_pop/2018_Base/"
df = pd.read_csv(f_dir+"synthetic_carriers.csv")
# %%

total_size=df.shape[0]
sample_ratio=10
df["binned_volume"]=df['n_trucks'].apply(lambda x:lable_creater(x))
list_bin_labels = df["binned_volume"].unique().tolist()
list_shipper_sample=[]
for bin_id in list_bin_labels:
    temp_2=df[(df['binned_volume']==bin_id)]
    list_shipper = temp_2['BusID'].unique().tolist()
    if (len(list_shipper)*sample_ratio/100 >0) & (len(list_shipper)*sample_ratio/100 <0.5):
        list_shipper= random.sample(list_shipper, int(len(list_shipper)*sample_ratio/100+0.5))
        list_shipper_sample=list_shipper_sample+list_shipper
    elif (len(list_shipper)*sample_ratio/100 >=0.5):     
        list_shipper= random.sample(list_shipper, int(len(list_shipper)*sample_ratio/100+0.5))
        list_shipper_sample=list_shipper_sample+list_shipper             
df_sample=df[df["BusID"].isin(list_shipper_sample)].reset_index(drop=True)
# %%
plt.figure(figsize = (8,6))
#plt.hist(df_hh_obs[df_hh_obs[ic_nm]==1]['delivery_f'], color ="blue", density=True, bins=df_hh_obs[df_hh_obs[ic_nm]==1]['delivery_f'].max(), alpha = 0.3, label="observed")
#plt.hist(df_hh_model[(df_hh_model[ic_nm]==1) & (df_hh_model['delivery_f']<=30)]['delivery_f'], color ="red", density=True, bins=80, alpha = 0.3, label="modeled")
#plt.hist(df_hh_model[(df_hh_model[ic_nm]==1)]['delivery_f'], color ="red", density=True, bins=df_hh_model[(df_hh_model[ic_nm]==1)]['delivery_f'].max(), alpha = 0.3, label="modeled")
plt.hist(df[df['n_trucks']<10]['n_trucks'], color ="blue", density=True, bins=int(df[df['n_trucks']<10]['n_trucks'].max()), alpha = 0.3, label="Full population")
plt.hist(df_sample[df_sample['n_trucks']<10]['n_trucks'], color ="red", density=True, bins=int(df_sample[df_sample['n_trucks']<10]['n_trucks'].max()), alpha = 0.3, label="10 percent sample")
plt.legend(loc="upper right")
# %%
plt.figure(figsize = (8,6))
#plt.hist(df_hh_obs[df_hh_obs[ic_nm]==1]['delivery_f'], color ="blue", density=True, bins=df_hh_obs[df_hh_obs[ic_nm]==1]['delivery_f'].max(), alpha = 0.3, label="observed")
#plt.hist(df_hh_model[(df_hh_model[ic_nm]==1) & (df_hh_model['delivery_f']<=30)]['delivery_f'], color ="red", density=True, bins=80, alpha = 0.3, label="modeled")
#plt.hist(df_hh_model[(df_hh_model[ic_nm]==1)]['delivery_f'], color ="red", density=True, bins=df_hh_model[(df_hh_model[ic_nm]==1)]['delivery_f'].max(), alpha = 0.3, label="modeled")
plt.hist(df[(df['n_trucks']>=10) & (df['n_trucks']<200)]['n_trucks'], color ="blue", density=True, bins=int(df[(df['n_trucks']>=10) & (df['n_trucks']<200)]['n_trucks'].max()), alpha = 0.3, label="Full population")
plt.hist(df_sample[(df_sample['n_trucks']>=10) & (df_sample['n_trucks']<200)]['n_trucks'], color ="red", density=True, bins=int(df_sample[(df_sample['n_trucks']>=10) & (df_sample['n_trucks']<200)]['n_trucks'].max()), alpha = 0.3, label="10 percent sample")
plt.legend(loc="upper right")
# %%
plt.figure(figsize = (8,6))
#plt.hist(df_hh_obs[df_hh_obs[ic_nm]==1]['delivery_f'], color ="blue", density=True, bins=df_hh_obs[df_hh_obs[ic_nm]==1]['delivery_f'].max(), alpha = 0.3, label="observed")
#plt.hist(df_hh_model[(df_hh_model[ic_nm]==1) & (df_hh_model['delivery_f']<=30)]['delivery_f'], color ="red", density=True, bins=80, alpha = 0.3, label="modeled")
#plt.hist(df_hh_model[(df_hh_model[ic_nm]==1)]['delivery_f'], color ="red", density=True, bins=df_hh_model[(df_hh_model[ic_nm]==1)]['delivery_f'].max(), alpha = 0.3, label="modeled")
plt.hist(df[df['n_trucks']>200]['n_trucks'], color ="blue", density=True, bins=int(df[df['n_trucks']>200]['n_trucks'].max()), alpha = 0.3, label="Full population")
plt.hist(df_sample[df_sample['n_trucks']>200]['n_trucks'], color ="red", density=True, bins=int(df_sample[df_sample['n_trucks']>200]['n_trucks'].max()), alpha = 0.3, label="10 percent sample")
plt.legend(loc="upper right")
# %%
def sampling_shipper(temp, sample_ratio, bin_size):
    temp_1 = temp.groupby(['SellerID'])['SellerID'].count().reset_index(name='num_shipment')
    total_size=temp_1.shape[0]
    if (total_size*sample_ratio)/(100) < bin_size:
        bin_size = int((total_size*sample_ratio)/(100))
    try:    
        temp_1["binned_volume"] =pd.qcut(temp_1['num_shipment'], q=bin_size, labels=False)
    except:
        temp_1["binned_volume"]=temp_1['num_shipment'].apply(lambda x:lable_creater(x))

    list_bin_labels = temp_1["binned_volume"].unique().tolist()
    list_shipper_sample=[]
    for bin_id in list_bin_labels:
        temp_2=temp_1[(temp_1['binned_volume']==bin_id)]
        list_shipper = temp_2['SellerID'].unique().tolist()
        if (len(list_shipper)*sample_ratio/100 >0) & (len(list_shipper)*sample_ratio/100 <0.5):
            list_shipper= random.sample(list_shipper, int(len(list_shipper)*sample_ratio/100+0.5))
            list_shipper_sample=list_shipper_sample+list_shipper
        elif (len(list_shipper)*sample_ratio/100 >=0.5):     
            list_shipper= random.sample(list_shipper, int(len(list_shipper)*sample_ratio/100+0.5))
            list_shipper_sample=list_shipper_sample+list_shipper  
    df_sample=temp[temp['SellerID'].isin(list_shipper_sample)].reset_index(drop=True)

    return df_sample

f_dir= "/Users/kjeong/KJ_NREL_Work/1_Work/1_2_SMART_2_0/Model_development/FRISM_input_output_SF/Sim_inputs/Synth_firm_results/2018_Base/"
df = pd.read_csv(f_dir+"private_truck_shipment_sctg4.csv")
# %%
df_sample= sampling_shipper(df, sample_ratio, 10)
# %%
df_group= df.groupby(['SellerID'])['SellerID'].agg(num_ship='count').reset_index()

df_sample_group= df_sample.groupby(['SellerID'])['SellerID'].agg(num_ship='count').reset_index()

# %%
plt.figure(figsize = (8,6))
#plt.hist(df_hh_obs[df_hh_obs[ic_nm]==1]['delivery_f'], color ="blue", density=True, bins=df_hh_obs[df_hh_obs[ic_nm]==1]['delivery_f'].max(), alpha = 0.3, label="observed")
#plt.hist(df_hh_model[(df_hh_model[ic_nm]==1) & (df_hh_model['delivery_f']<=30)]['delivery_f'], color ="red", density=True, bins=80, alpha = 0.3, label="modeled")
#plt.hist(df_hh_model[(df_hh_model[ic_nm]==1)]['delivery_f'], color ="red", density=True, bins=df_hh_model[(df_hh_model[ic_nm]==1)]['delivery_f'].max(), alpha = 0.3, label="modeled")
plt.hist(df_group[df_group['num_ship']<1000]['num_ship'], color ="blue", density=True, bins=100, alpha = 0.3, label="Full population")
plt.hist(df_sample_group[df_sample_group['num_ship']<1000]['num_ship'], color ="red", density=True, bins=100, alpha = 0.3, label="10 percent sample")
plt.legend(loc="upper right")
# %%
# %%
plt.figure(figsize = (8,6))
#plt.hist(df_hh_obs[df_hh_obs[ic_nm]==1]['delivery_f'], color ="blue", density=True, bins=df_hh_obs[df_hh_obs[ic_nm]==1]['delivery_f'].max(), alpha = 0.3, label="observed")
#plt.hist(df_hh_model[(df_hh_model[ic_nm]==1) & (df_hh_model['delivery_f']<=30)]['delivery_f'], color ="red", density=True, bins=80, alpha = 0.3, label="modeled")
#plt.hist(df_hh_model[(df_hh_model[ic_nm]==1)]['delivery_f'], color ="red", density=True, bins=df_hh_model[(df_hh_model[ic_nm]==1)]['delivery_f'].max(), alpha = 0.3, label="modeled")
plt.hist(df_group[df_group['num_ship']>=1000]['num_ship'], color ="blue", density=True, bins=100, alpha = 0.3, label="Full population")
plt.hist(df_sample_group[df_sample_group['num_ship']>=1000]['num_ship'], color ="red", density=True, bins=100, alpha = 0.3, label="10 percent sample")
plt.legend(loc="upper right")
# %%
hh_file= "../../../FRISM_input_output_SF/Sim_inputs/hh_pop/sfbay_2018/households.csv.zip"
per_file= "../../../FRISM_input_output_SF/Sim_inputs/hh_pop/sfbay_2018/persons.csv.zip"

df_hh_total = pd.read_csv(hh_file, header=0, sep=',')
df_per_total = pd.read_csv(per_file, header=0, sep=',')
# %%

pay_file= "/Users/kjeong/KJ_NREL_Work/1_Work/1_2_SMART_2_0/Model_development/FRISM_input_output_SF/result_0710/Tour_plan/2018_all/B2C_all_payload_sBase_y2018.csv"
pl_df= pd.read_csv(pay_file, header=0, sep=',')
pay_file= "/Users/kjeong/KJ_NREL_Work/1_Work/1_2_SMART_2_0/Model_development/FRISM_input_output_SF/result_0710/Tour_plan/2018_all/B2C_all_freight_tours_sBase_y2018.csv"
tour_df= pd.read_csv(pay_file, header=0, sep=',')
# %%
tour_df["departureTimeInSec"]=tour_df["departureTimeInSec"]/3600
plt.hist(tour_df["departureTimeInSec"], color ="blue", bins = 20)
# %%
pl_df_temp = pl_df[pl_df['operationDurationInSec']>0]
# %%
pl_df_temp['operationDurationInSec']=pl_df_temp['operationDurationInSec']/60
plt.hist(pl_df_temp['operationDurationInSec'], color ="blue", bins = 20)
# %%
t_list=[]
for tourId in pl_df["tourId"].unique():
    temp= pl_df[pl_df["tourId"]==tourId].reset_index()
    op_time= (temp.loc[temp.shape[0]-1,"estimatedTimeOfArrivalInSec" ]-temp.loc[0,"estimatedTimeOfArrivalInSec" ])/3600 +2
    t_list.append(op_time)
plt.hist(t_list, color ="blue", bins = 20)
# %%
t_list=[]
for index in range (0,pl_df.shape[0]-1):
    op_time= (pl_df.loc[index+1,"estimatedTimeOfArrivalInSec" ]-pl_df.loc[index,"estimatedTimeOfArrivalInSec" ])/60
    if op_time >0: 
        t_list.append(op_time)
plt.hist(t_list, color ="blue", bins = 20)
# %%
