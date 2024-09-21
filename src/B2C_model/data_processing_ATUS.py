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
# Read data 
fdir_input= "../../../B2C_Data/ATUS/2022/"
atus_act= pd.read_csv(fdir_input+'atusact_2022.dat', sep=',', engine='python')
atus_resp= pd.read_csv(fdir_input+'atusresp_2022.dat', sep=',', engine='python')
atus_cps= pd.read_csv(fdir_input+'atuscps_2022.dat', sep=',', engine='python')
# %%
# activity file
var_act= ['TUCASEID',
 'TUACTIVITY_N',
 'TEWHERE',
 'TUACTDUR',
 'TUACTDUR24',
 'TRCODE']
var_resp= ['TUCASEID', 
'TULINENO',
"TEERN",
"TEERNWKP",
"TEHRUSLT",
"TESCHENR", # Are you enrolled in HS, college, or university; 1 yes, 2 no
"TESCHFT",
"TESCHLVL",
"TRDTIND1",
"TRDTOCC1",
"TRIMIND1",
"TRMJIND1",
"TRMJOCC1",
"TRNUMHOU",
"TUFINLWGT" #    
]
# personal info: age, sex, (relationship to you), might not need to have it. 
var_rost= ['TUCASEID', 
'TULINENO',
'TEAGE',   
'TERRP',   
'TESEX'
]
var_cps= [
"GEREG", # region definition 
"GTMETSTA", # MSA
"HEFAMINC", # income
"HEHOUSUT", 
"HETENURE", # Edited: are your living quarters owned, rented for cash, or occupied without payment of cash rent?; 1 owned, 2 rented, 3, occupied without payment
"HRHTYPE", 
"HRNUMHOU", # Total number of persons in the household (household members)
"PEEDUCA", # Education
"PESCHFT",
"PESCHLVL",
"PESEX", # sex
"PRTAGE", # age
"PTDTRACE", # race
"PREXPLF", # employment
"TRATUSR",
"TUCASEID",
"TULINENO",
"PRNMCHLD"    
]

atus_act  = atus_act[var_act]
atus_resp = atus_resp[var_resp]
#atus_rost = atus_rost[var_rost]
atus_cps  = atus_cps[var_cps]

atus_resp =atus_resp.merge(atus_cps, on=["TUCASEID","TULINENO"], how="left")
#%%
atus_resp =atus_resp[atus_resp["TULINENO"]==1]

# %%
# %%
'''
# TRCODE
## online delivery
GR    070101	Grocery shopping **	
X    070102	Purchasing gas	
FD    070103	Purchasing food (not groceries) *	
GG    070104	Shopping, except groceries, food and gas **
GG    070105	Waiting associated with shopping 	
GG    070199	Shopping, n.e.c.*  **
GG    070201	Comparison shopping	*
GG    070299	Researching purchases, n.e.c.* **
    070301	Security procedures rel. to consumer purchases	
    070399	Security procedures rel. to consumer purchases, n.e.c.*
GG    079999	Consumer purchases, n.e.c.* **

## on demand
070103	Purchasing food (not groceries)
110201	Waiting associated w/eating & drinking

# TEWHERE : * place for offline
On    1 Respondent's home or yard
On    2 Respondent's workplace
On    3 Someone else's home
On-GG/off-FD    4 Restaurant or bar
On    5 Place of worship
On-GG/off-GR    6 Grocery store
Off-GG/off-GR/off-FD    7 Other store/mall
On    8 School
On    9 Outdoors away from home
On    10 Library
On    11 Other place
On    12 Car, truck, or motorcycle (driver)
On    13 Car, truck, or motorcycle (passenger)
On    14 Walking
On    15 Bus
On    16 Subway/train
On    17 Bicycle
On    18 Boat/ferry
On    19 Taxi/limousine service
On    20 Airplane
On    21 Other mode of transportation
On    30 Bank
On    31 Gym/health club
On    32 Post Office
On    89 Unspecified place
On    99 Unspecified mode of transportation
'''
def offline_good_identifier(TEWHERE, TRCODE):
    if TRCODE in [70104,70105, 70199, 70201, 70299,79999] and TEWHERE in [7] :
        return 1
    else: 
        return 0
def online_good_identifier(TEWHERE, TRCODE):
    if TRCODE in [70101,70104,70199,70299,79999] and TEWHERE not in [7] :
        return 1
    else: 
        return 0
def offline_grocery_identifier(TEWHERE, TRCODE):
    if TRCODE == 70101 and TEWHERE in [6,7] :
        return 1
    else: 
        return 0
def online_grocery_identifier(TEWHERE, TRCODE):
    if TRCODE == 70101 and TEWHERE not in [6,7] :
        return 1
    else: 
        return 0
def offline_food_identifier(TEWHERE, TRCODE):
    if TRCODE in [70101,70103, 110201] and TEWHERE in [4,7] :
        return 1
    else: 
        return 0      
def online_food_identifier(TEWHERE, TRCODE):
    if TRCODE in [70103, 110201] and TEWHERE not in [4,7] :
        return 1
    else: 
        return 0 

# %%

def income_group(HHFAMINC):
    if HHFAMINC in [1,2,3]: # less 10000
        return 0
    elif HHFAMINC in [4,5]: # 10000~15000
        return 1
    elif HHFAMINC in [6,7]: # 15k-25k
        return 2
    elif HHFAMINC in [8,9]: # 25~35k 
        return 3
    elif HHFAMINC in [10,11]: # 35~50k 
        return 4
    elif HHFAMINC in [12,13]: # 50~75k 
        return 5
    elif HHFAMINC in [14]: # 75~100k 
        return 6
    elif HHFAMINC in [15]: # 100~150k 
        return 7
    elif HHFAMINC in [16]: # 150~k 
        return 8    

def income_group_agg(HHFAMINC):
    if HHFAMINC in [1,2,3,4,5,6,7]: # less 25k
        return 0
    elif HHFAMINC in [8,9,10,11]: # 25~50k 
        return 1
    elif HHFAMINC in [12,13]: # 50~75k 
        return 2
    elif HHFAMINC in [14]: # 75~100k 
        return 3
    elif HHFAMINC in [15]: # 100~150k 
        return 4
    elif HHFAMINC in [16]: # 150~k 
        return 5   

def income_est(HHFAMINC):
    if HHFAMINC ==1:
        return (0+5000)/200000
    elif HHFAMINC ==2: # 10000~15000
        return (5000+7500)/200000
    elif HHFAMINC ==3: # 10000~15000
        return (7500+10000)/200000
    elif HHFAMINC ==4: # 10000~15000
        return (10000+12500)/200000
    elif HHFAMINC ==5: # 10000~15000
        return (12500+15000)/200000
    elif HHFAMINC ==6: # 10000~15000
        return (15000+20000)/200000
    elif HHFAMINC ==7: # 10000~15000
        return (20000+25000)/200000
    elif HHFAMINC ==8: # 10000~15000
        return (25000+30000)/200000
    elif HHFAMINC ==9: # 10000~15000
        return (30000+35000)/200000
    elif HHFAMINC ==10: # 10000~15000
        return (35000+40000)/200000
    elif HHFAMINC ==11: # 10000~15000
        return (40000+50000)/200000
    elif HHFAMINC ==12: # 10000~15000
        return (50000+ 60000)/200000
    elif HHFAMINC ==13: # 10000~15000
        return (60000+ 75000)/200000
    elif HHFAMINC ==14: # 10000~15000
        return (75000+ 100000)/200000
    elif HHFAMINC ==15: # 10000~15000
        return (100000+ 150000)/200000    
    elif HHFAMINC ==16: # 10000~15000
        return (150000+ 250000)/200000  


def home_class(HOMEOWN):
    if HOMEOWN == 1: 
        return 0
    else:
        return 1
def edu_class(EDUC):
    if EDUC in [31,32,33,34,35,36,37,38,39]: # high shcool or less
        return 0
    elif EDUC in [40,41,42]: # college and tech 
        return 1
    elif EDUC in [43,44,45,46]: # undergraduate 
        return 2    
    # elif EDUC in [44,45,46]: # graduate 
    #     return 3 
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

def sex_class(R_SEX_IMP):
    if R_SEX_IMP in [1]: 
        return 1
    else:
        return 0 
def race_class(HH_RACE):
    if HH_RACE in [1,6,7,8,9] : 
        return 1 # white
    elif HH_RACE in [2,10,11,12]:
        return 2 # black
    elif HH_RACE in [4,15]:
        return 3 # Asian
    else:
        return 0 # others
def student_class(SCHTYP):
    if SCHTYP in [1]:
        return 1
    else:
        return 0 

def msa_id(GTMETSTA):
    if GTMETSTA ==1:
        return 1
    else: 
        return 0  

def employment(PREXPLF):
    if PREXPLF ==1:
        return 1
    else: 
        return 0 
    
# %% 
atus_act['instore_goods']=atus_act.apply(lambda x: offline_good_identifier(x['TEWHERE'], x['TRCODE']), axis=1)
atus_act['online_goods']=atus_act.apply(lambda x: online_good_identifier(x['TEWHERE'], x['TRCODE']), axis=1)
atus_act['instore_grocery']=atus_act.apply(lambda x: offline_grocery_identifier(x['TEWHERE'], x['TRCODE']), axis=1)
atus_act['online_grocery']=atus_act.apply(lambda x: online_grocery_identifier(x['TEWHERE'], x['TRCODE']), axis=1)
atus_act['instore_food']=atus_act.apply(lambda x: offline_food_identifier(x['TEWHERE'], x['TRCODE']), axis=1)
atus_act['online_food']=atus_act.apply(lambda x: online_food_identifier(x['TEWHERE'], x['TRCODE']), axis=1)


atus_df=atus_act.groupby(['TUCASEID']).agg(instore_goods_act=('instore_goods','sum'), online_goods_act=('online_goods','sum'),
                                           instore_grocery_act=('instore_grocery','sum'), online_grocery_act=('online_grocery','sum'),
                                           instore_food_act=('instore_food','sum'), online_food_act=('online_food','sum'))

atus_df['instore_gen_act']=atus_df['instore_goods_act']+ atus_df['instore_grocery_act'] 
atus_df['online_gen_act']=atus_df['online_goods_act']+ atus_df['online_grocery_act'] 

atus_df['choice_instore_goods']  =atus_df["instore_goods_act"].apply(lambda x: 0 if x==0 else 1 )
atus_df['choice_online_goods']   =atus_df["online_goods_act"].apply(lambda x: 0 if x==0 else 1)
atus_df['choice_instore_grocery']=atus_df["instore_grocery_act"].apply(lambda x: 0 if x==0 else 1)
atus_df['choice_online_grocery'] =atus_df["online_grocery_act"].apply(lambda x: 0 if x==0 else 1)
atus_df['choice_instore_food']   =atus_df["instore_food_act"].apply(lambda x: 0 if x==0 else 1)
atus_df['choice_online_food']    =atus_df["online_food_act"].apply(lambda x: 0 if x==0 else 1)
atus_df['choice_instore_gen']   =atus_df["instore_gen_act"].apply(lambda x: 0 if x==0 else 1)
atus_df['choice_online_gen']    =atus_df["online_gen_act"].apply(lambda x: 0 if x==0 else 1)

atus_df =atus_df.merge(atus_resp, on=["TUCASEID"], how="left")
atus_df.to_csv(fdir_input+"atus_df_processed_2022.csv")

# %%
atus_df['income_est']     =atus_df['HEFAMINC'].apply(income_est)
atus_df['HEFAMINC']     =atus_df['HEFAMINC'].apply(income_group_agg)
atus_df['PEEDUCA']      =atus_df['PEEDUCA'].apply(edu_class)
atus_df['R_AGE']          =atus_df['PRTAGE']
atus_df['PRTAGE']       =atus_df['PRTAGE'].apply(age_est)
atus_df['PESEX']        =atus_df['PESEX'].apply(sex_class)
atus_df['PTDTRACE']     =atus_df['PTDTRACE'].apply(race_class)
atus_df['TESCHENR']     =atus_df['TESCHENR'].apply(student_class)
atus_df['GTMETSTA']     =atus_df['GTMETSTA'].apply(msa_id)
atus_df['PREXPLF']      =atus_df['PREXPLF'].apply(employment)
atus_df['CHILD']      =atus_df['PRNMCHLD'].apply(lambda x: 0 if x==0 else 1)

atus_df.rename(columns = {'HEFAMINC':'income_cls',
'PEEDUCA':'EDUC',
'PRTAGE':'R_AGE_C',
'PESEX':'R_SEX_IMP',
'PTDTRACE':'R_RACE',
'TESCHENR':'SCHTYP',
'GTMETSTA':'MSACAT',
'PREXPLF':'WORKER',
"GEREG":'CENSUS_R',
'HRNUMHOU': 'HHSIZE'}, inplace = True)

atus_df.to_csv(fdir_input+"atus_df_pre_model_2022.csv")
# %%
Class_vars= ['income_cls','EDUC', 'R_AGE_C','R_SEX_IMP','R_RACE','SCHTYP','MSACAT','WORKER','CENSUS_R']
# Create class variables that has more than two classes
cat_vars=[]
for var_c in Class_vars:
    if atus_df[var_c].unique().size >2:
        cat_vars.append(var_c)
for var in cat_vars:
    cat_list='var'+'_'+var
    cat_list = pd.get_dummies(atus_df[var], prefix=var)
    atus_df=atus_df.join(cat_list)

def shop_choice(offline_shop_sum, online_shop_sum):
    if offline_shop_sum ==0 and online_shop_sum ==0 :
        return 3    # no shop
    elif offline_shop_sum ==1 and online_shop_sum ==0 :
        return 1 # off
    elif offline_shop_sum ==0 and online_shop_sum ==1 :
        return 2 # on
    elif offline_shop_sum ==1 and online_shop_sum ==1 :
        return 0 # both

atus_df['choice_goods']=atus_df.apply(lambda x: shop_choice(x['choice_instore_goods'], x['choice_online_goods']), axis=1)
atus_df['choice_grocery']=atus_df.apply(lambda x: shop_choice(x['choice_instore_grocery'], x['choice_online_grocery']), axis=1)
atus_df['choice_food']=atus_df.apply(lambda x: shop_choice(x['choice_instore_food'], x['choice_online_food']), axis=1)
atus_df['choice_gen']=atus_df.apply(lambda x: shop_choice(x['choice_instore_gen'], x['choice_online_gen']), axis=1)

atus_df.to_csv(fdir_input+"atus_df_model_2022.csv")    
#

# %%
