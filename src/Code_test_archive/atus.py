## Note: To test the codes: In def main(), put for loop is restricted:
### please comment out the followings for the entire run. 
### if args.ship_type == "B2C": ... #for i in range(0,df_hh_D_GrID.shape[0]):
### elif args.ship_type == "B2B": ...#for i in range(0,FH_Seller.shape[0]): 
# %%
import pandas as pd
import numpy as np
import geopandas as gpd
from argparse import ArgumentParser
import random
import config
import glob
from os.path import exists as file_exists
from alive_progress import alive_bar
import time
from shapely.geometry import Point

# library for models 
import joblib
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
import statsmodels.formula.api as smf
import seaborn as sns
import matplotlib.pyplot as plt
# %%
fdir_input= "../../../FRISM_input_output_SF/Model_inputs/ATUS/2019/"
atus_act= pd.read_csv(fdir_input+'atusact_2019.dat', sep=',', engine='python')
atus_resp= pd.read_csv(fdir_input+'atusresp_2019.dat', sep=',', engine='python')
#atus_rost= pd.read_csv(fdir_input+'atusrost_2019.dat', sep=',', engine='python')
atus_cps= pd.read_csv(fdir_input+'atuscps_2019.dat', sep=',', engine='python')
# %%
'''
a=pd.DataFrame(columns = ['var_name'])
a['var_name']=atus_resp.columns
a.to_csv(fdir_input+"resp_var.csv")
b=pd.DataFrame(columns = ['var_name'])
b['var_name']=atus_cps.columns
b.to_csv(fdir_input+"cps_var.csv")
'''
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
"TESCHENR", #
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
"HEFAMINC", #
"HEHOUSUT", 
"HETENURE", #
"HRHTYPE", 
"HRNUMHOU", #
"PEEDUCA", #
"PESCHFT",
"PESCHLVL",
"PESEX", #
"PRTAGE", #
"PTDTRACE", #
"TRATUSR",
"TUCASEID",
"TULINENO"    
]

atus_act  = atus_act[var_act]
atus_resp = atus_resp[var_resp]
#atus_rost = atus_rost[var_rost]
atus_cps  = atus_cps[var_cps]

atus_resp =atus_resp.merge(atus_cps, on=["TUCASEID","TULINENO"], how="left")
atus_resp =atus_resp[atus_resp["TULINENO"]==1]



# %%
'''
# TRCODE
## online delivery
*070101	Grocery shopping **	
070102	Purchasing gas	
070103	Purchasing food (not groceries)	
*070104	Shopping, except groceries, food and gas **
070105	Waiting associated with shopping 	
*070199	Shopping, n.e.c.*  **
070201	Comparison shopping	
*070299	Researching purchases, n.e.c.* **
070301	Security procedures rel. to consumer purchases	
070399	Security procedures rel. to consumer purchases, n.e.c.*
*079999	Consumer purchases, n.e.c.* **

## on demand
070103	Purchasing food (not groceries)
110201	Waiting associated w/eating & drinking

# TEWHERE : * place for offline
1 Respondent's home or yard
2 Respondent's workplace
3 Someone else's home
*4 Restaurant or bar
5 Place of worship
*6 Grocery store
*7 Other store/mall
8 School
9 Outdoors away from home
10 Library
11 Other place
12 Car, truck, or motorcycle (driver)
13 Car, truck, or motorcycle (passenger)
14 Walking
15 Bus
16 Subway/train
17 Bicycle
18 Boat/ferry
19 Taxi/limousine service
20 Airplane
21 Other mode of transportation
30 Bank
31 Gym/health club
32 Post Office
89 Unspecified place
99 Unspecified mode of transportation
'''
def offline_identifier(TEWHERE, TRCODE):
    if TRCODE in [70101,70104,70199,70299,79999] and TEWHERE in [4,6,7] :
        return 1
    else: 
        return 0
def online_identifier(TEWHERE, TRCODE):
    if TRCODE in [70101,70104,70199,70299,79999] and TEWHERE not in [4,6,7] :
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
def ondemand_identifier(TEWHERE, TRCODE):
    if TRCODE in [70101,70103, 110201] and TEWHERE not in [4,6,7] :
        return 1
    else: 
        return 0

def shop_choice(offline_shop_sum, online_shop_sum):
    if offline_shop_sum ==0 and online_shop_sum ==0 :
        return 0
    elif offline_shop_sum > 0 and online_shop_sum ==0 :
        return 1
    elif offline_shop_sum ==0 and online_shop_sum > 0 :
        return 2
    elif offline_shop_sum >0 and online_shop_sum >0 :
        return 3

atus_act['offline_shop']=atus_act.apply(lambda x: offline_identifier(x['TEWHERE'], x['TRCODE']), axis=1)
atus_act['online_shop']=atus_act.apply(lambda x: online_identifier(x['TEWHERE'], x['TRCODE']), axis=1)
atus_act['offline_gro_shop']=atus_act.apply(lambda x: offline_grocery_identifier(x['TEWHERE'], x['TRCODE']), axis=1)
atus_act['online_gro_shop']=atus_act.apply(lambda x: online_grocery_identifier(x['TEWHERE'], x['TRCODE']), axis=1)
atus_act['ondemand']=atus_act.apply(lambda x: ondemand_identifier(x['TEWHERE'], x['TRCODE']), axis=1)
atus_df=atus_act.groupby(['TUCASEID']).agg({'offline_shop':[sum],'online_shop':[sum],'offline_gro_shop':[sum],'online_gro_shop':[sum], 'ondemand':[sum]})
atus_df.columns = ["_".join(x) for x in atus_df.columns.ravel()]
atus_df.reset_index(level=(0), inplace=True)                
atus_df['shop_choice']=atus_df.apply(lambda x: shop_choice(x['offline_shop_sum'], x['online_shop_sum']), axis=1)
atus_df.to_csv(fdir_input+"atus_df_processed_jul.csv")
atus_df =atus_df.merge(atus_resp, on=["TUCASEID"], how="left")

def income_group(HHFAMINC):
    if HHFAMINC in [1,2,3,4,5,6,7,8,9]: # 35000
        return 0
    elif HHFAMINC in [10,11,12,13]: # 35000~75000
        return 1
    elif HHFAMINC in [14,15]: # 75000~125000
        return 2
    elif HHFAMINC in [16]: # 125000~
        return 3  
def home_class(HOMEOWN):
    if HOMEOWN == 1: 
        return 1
    else:
        return 0
def edu_class(EDUC):
    if EDUC in [31,32,33,34,35,36,37,38]:
        return 0
    elif EDUC in [39]:
        return 1
    elif EDUC in [40,41,42,43]:
        return 2    
    elif EDUC in [44,45,46]:
        return 3 
def age_est(R_AGE_IMP):
    if R_AGE_IMP  <20 :
        return 0
    elif R_AGE_IMP  >=20 and R_AGE_IMP  <40:
        return 1
    elif R_AGE_IMP  >=40 and R_AGE_IMP  <60:
        return 2
    elif R_AGE_IMP  >=60:
        return 3

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
# %%
atus_df['HEFAMINC']   =atus_df['HEFAMINC'].apply(income_group)
atus_df['HETENURE']   =atus_df['HETENURE'].apply(home_class)
atus_df['PEEDUCA']     =atus_df['PEEDUCA'].apply(edu_class)
atus_df['PRTAGE']      =atus_df['PRTAGE'].apply(age_est)
atus_df['PESEX']      =atus_df['PESEX'].apply(sex_class)
atus_df['PTDTRACE']      =atus_df['PTDTRACE'].apply(race_class)
atus_df['TESCHENR']      =atus_df['TESCHENR'].apply(student_class)


# list of variables that have class
    ## Need to update!!, if functions change used in "Process variables using function"  
Class_vars= ['HEFAMINC',
'HETENURE',
'PEEDUCA',
'PRTAGE',
'PESEX', 
'PTDTRACE',
'TESCHENR'
] 

# Create class variables that has more than two classes
cat_vars=[]
for var_c in Class_vars:
    if atus_df[var_c].unique().size >2:
        cat_vars.append(var_c)
for var in cat_vars:
    cat_list='var'+'_'+var
    cat_list = pd.get_dummies(atus_df[var], prefix=var)
    atus_df=atus_df.join(cat_list)


# %%    
selected_x= [ 'ondemand_sum',
       'shop_choice',  'TESCHENR','TUFINLWGT', 'HETENURE',
    'HRNUMHOU', 'PESEX', 'HEFAMINC_0', 'HEFAMINC_1',
       'HEFAMINC_2', 'HEFAMINC_3', 'PEEDUCA_0', 'PEEDUCA_1', 'PEEDUCA_2',
       'PEEDUCA_3', 'PRTAGE_0', 'PRTAGE_1', 'PRTAGE_2', 'PRTAGE_3',
       'PTDTRACE_0', 'PTDTRACE_1', 'PTDTRACE_2', 'PTDTRACE_3']

X_study=atus_df[selected_x]
Y_study=atus_df['shop_choice']
#trainX, testX, trainY, testY = train_test_split(X_study, Y_study, test_size = 0.7)

# SMOTE approach for lower sample issue for less frequent data
#oversample = SMOTE()
#trainX,trainY = oversample.fit_resample(X_study,Y_study)
trainX=X_study
trainY=Y_study

# initial model
model_int = LogisticRegression(solver='newton-cg', multi_class='multinomial')
model_int.fit(trainX, trainY)
y_pred = model_int.predict(trainX)

with open('atus_model.txt', 'a') as f:
    print ('************* Webuse Model: inital model ****************', file=f)
    print('Accuracy for initial model: {:.2f}'.format(accuracy_score(trainY, y_pred)), file=f)
    print('Error rate for initial model: {:.2f}'.format(1 - accuracy_score(trainY, y_pred)), file=f)
    print ('initial confusion matirix)', confusion_matrix(trainY.tolist(), y_pred), file=f)

# %%
filename = '../Simulation/atus_model.sav'
joblib.dump(model_int, filename)


# %%
fdir_in_out= "../../../FRISM_input_output_SF"
fdir_firms=fdir_in_out+'/Sim_inputs/Synth_firm_pop/'
firm_file='synthfirms_all_Sep.csv'
# firm and warehouse(for-hire carrier)
firm_file_xy=fdir_firms+"xy"+firm_file
if file_exists(firm_file_xy):
    firms=pd.read_csv(firm_file_xy, header=0, sep=',')
    if "BusID" in firms.columns:
        firms=firms.rename({'BusID':'SellerID'}, axis='columns')
    if "lat" in firms.columns:
        firms=firms.rename({'lat':'y', 'lon': 'x'}, axis='columns')
# %%
firms_group= firms.groupby(['Industry_NAICS6_Make'])['Industry_NAICS6_Make'].agg(num_firms='count').reset_index()
firms_group.to_csv(fdir_firms+"naics_in_firmfile.csv")
# %%
import overpy
api = overpy.Overpass()
# small_test = (37.779125,-122.295224,37.889793,-122.151232)
# full region = (37.221225, -123.115864, 38.469739, -121.496602)
# eating: ammenity= restaurant;bar;fast_food
# Grocery: shop=supermarket; wholesale
eating_result = api.query("node[amenity=restaurant](37.221225, -123.115864, 38.469739, -121.496602);out;")
#grocery_result = api.query("node[shop=supermarket](37.221225, -123.115864, 38.469739, -121.496602);out;")
# %%
#len(eating_result.nodes)

tag1 = pd.Series()
tag2 = pd.Series()
tag3 = pd.Series()
tag4 = pd.Series()
tag5 = pd.Series()

for i in range(len(eating_result.nodes)):
    tag1.at[i] = eating_result.nodes[i].id
    tag2.at[i] = eating_result.nodes[i].tags.get('amenity')
    tag3.at[i] = eating_result.nodes[i].tags.get('name')
    tag4.at[i] = eating_result.nodes[i].lat
    tag5.at[i] = eating_result.nodes[i].lon
    
df_eating_result = pd.concat([tag1, tag2,tag3, tag4,tag5], axis=1)
df_eating_result.columns = ['id', 'type', 'name', 'lat', 'lon']
# %%
api = overpy.Overpass()
grocery_result = api.query("node[shop=supermarket](37.221225, -123.115864, 38.469739, -121.496602);out;")
tag1 = pd.Series()
tag2 = pd.Series()
tag3 = pd.Series()
tag4 = pd.Series()
tag5 = pd.Series()

for i in range(len(grocery_result.nodes)):
    tag1.at[i] = grocery_result.nodes[i].id
    tag2.at[i] = grocery_result.nodes[i].tags.get('shop')
    tag3.at[i] = grocery_result.nodes[i].tags.get('name')
    tag4.at[i] = grocery_result.nodes[i].lat
    tag5.at[i] = grocery_result.nodes[i].lon
    
df_grocery_result = pd.concat([tag1, tag2,tag3, tag4,tag5], axis=1)
df_grocery_result.columns = ['id', 'type', 'name', 'lat', 'lon']
# %%
