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


fdir_geo = config.fdir_geo 
CBG_file = config.CBG_file
state_id=config.state_id
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
CBGzone_df=CBGzone_df[CBGzone_df["County"].isin(config.county_list)]
CBGzone_df.head()
df_per['GEOID'] =df_per['block_id'].apply(lambda x: np.floor(x/1000))
df_per= df_per.merge(CBGzone_df[["GEOID", "County"]], on='GEOID', how='left')
def urban(county, urban_counties):
    if county in urban_counties:
        return 1
    else: return 0    

df_per['URBRUR']=df_per["County"].apply(lambda x: urban(x,config.urban_county_list))
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
df_per_final.to_csv(config.out_file_dir+"per_del_2018.csv")
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

df_per["online_goods_act"]= df_per["DELIV_GOOD"].apply(lambda x: b2c_good_select(x,config.b2c_delivery_frequency, 100,"goods"))
df_per["online_grocery_act"]= df_per["DELIV_GROC"].apply(lambda x: b2c_good_select(x,config.b2c_delivery_frequency,100,"other"))
df_per["online_food_act"]= df_per["DELIV_FOOD"].apply(lambda x: b2c_good_select(x,config.b2c_delivery_frequency,100,"other"))
    
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
synth_per.to_csv(config.out_file_dir+"persons_w_instore_prob.csv.gz", compression="gzip", index=False)