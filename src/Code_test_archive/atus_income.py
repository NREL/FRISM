## Note: To test the codes: In def main(), put for loop is restricted:
### please comment out the followings for the entire run. 
### if args.ship_type == "B2C": ... #for i in range(0,df_hh_D_GrID.shape[0]):
### elif args.ship_type == "B2B": ...#for i in range(0,FH_Seller.shape[0]): 
# %%
# %%
import pandas as pd
import biogeme.database as db
import biogeme.biogeme as bio
from biogeme import models
import biogeme.messaging as msg
from biogeme.expressions import Beta, DefineVariable
import biogeme.results as res
import numpy as np
import config_b2c as config
from statsmodels.stats.weightstats import DescrStatsW


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
# def offline_identifier(TEWHERE, TRCODE):
#     if TRCODE in [70101,70104,70199,70299,79999] and TEWHERE in [4,6,7] :
#         return 1
#     else: 
#         return 0
# def online_identifier(TEWHERE, TRCODE):
#     if TRCODE in [70101,70104,70199,70299,79999] and TEWHERE not in [4,6,7] :
#         return 1
#     else: 
#         return 0
# def offline_grocery_identifier(TEWHERE, TRCODE):
#     if TRCODE == 70101 and TEWHERE in [6,7] :
#         return 1
#     else: 
#         return 0
# def online_grocery_identifier(TEWHERE, TRCODE):
#     if TRCODE == 70101 and TEWHERE not in [6,7] :
#         return 1
#     else: 
#         return 0
# def ondemand_identifier(TEWHERE, TRCODE):
#     if TRCODE in [70101,70103, 110201] and TEWHERE not in [4,6,7] :
#         return 1
#     else: 
#         return 0

def offline_shop(TEWHERE, TRCODE):
    if TRCODE in [70104,70199,70299,79999] and TEWHERE in [4,6,7] :
        return 1
    else: 
        return 0
def online_shop(TEWHERE, TRCODE):
    if TRCODE in [70104,70199,70299,79999] and TEWHERE not in [4,6,7] :
        return 1
    else: 
        return 0
def offline_ondemand(TEWHERE, TRCODE):
    if TRCODE in [70101,70103, 110201] and TEWHERE in [4,6,7] :
        return 1
    else: 
        return 0
def online_ondemand(TEWHERE, TRCODE):
    if TRCODE in [70101,70103, 110201] and TEWHERE not in [4,6,7]  :
        return 1
    else: 
        return 0

def shop_choice(offline_shop_sum, online_shop_sum):
    if offline_shop_sum ==0 and online_shop_sum ==0 :
        return 0    # no shop
    elif offline_shop_sum > 0 and online_shop_sum ==0 :
        return 1 # off
    elif offline_shop_sum ==0 and online_shop_sum > 0 :
        return 2 # on
    elif offline_shop_sum >0 and online_shop_sum >0 :
        return 3 # both
# def ondemand_choice(offline_od_sum, online_od_sum):
#     if offline_od_sum ==0 and online_od_sum ==0 :
#         return 0 # no gro   
#     elif offline_od_sum > 0 and online_od_sum ==0 :
#         return 1 # off gro
#     elif offline_od_sum ==0 and online_od_sum > 0 :
#         return 2 # on gro
#     elif offline_od_sum >0 and online_od_sum >0 :
#         return 3 # both       

atus_act['offline_shop']    =atus_act.apply(lambda x: offline_shop(x['TEWHERE'], x['TRCODE']), axis=1)
atus_act['online_shop']     =atus_act.apply(lambda x: online_shop(x['TEWHERE'], x['TRCODE']), axis=1)
atus_act['offline_od']      =atus_act.apply(lambda x: offline_ondemand(x['TEWHERE'], x['TRCODE']), axis=1)
atus_act['online_od']       =atus_act.apply(lambda x: online_ondemand(x['TEWHERE'], x['TRCODE']), axis=1)
atus_df=atus_act.groupby(['TUCASEID']).agg({'offline_shop':[sum],'online_shop':[sum],'offline_od':[sum],'online_od':[sum]})
atus_df.columns = ["_".join(x) for x in atus_df.columns.ravel()]
atus_df.reset_index(level=(0), inplace=True)                
atus_df['general_choice']=atus_df.apply(lambda x: shop_choice(x['offline_shop_sum'], x['online_shop_sum']), axis=1)
atus_df['shop']=atus_df['general_choice'].apply(lambda x: 1 if x>=1 else 0 )
atus_df['ondemand_choice']=atus_df.apply(lambda x: shop_choice(x['offline_od_sum'], x['online_od_sum']), axis=1)
atus_df['ondemand']=atus_df['ondemand_choice'].apply(lambda x: 1 if x>=1 else 0 )
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
    if R_AGE_IMP  <=25 :
        return 0
    elif R_AGE_IMP  >25 and R_AGE_IMP  <=40:
        return 1
    elif R_AGE_IMP  >40 and R_AGE_IMP  <=60:
        return 2
    elif R_AGE_IMP  >60:
        return 3

def sex_class(R_SEX_IMP):
    if R_SEX_IMP in [1]: 
        return 1
    else:
        return 0 
def race_class(HH_RACE):
    if HH_RACE in [1] : 
        return 1 # white
    elif HH_RACE in [2]:
        return 2 # black
    elif HH_RACE in [4]:
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
def income_est(HHFAMINC):
    if HHFAMINC in [1,2,3]:
        est_income= (0+10000)/2
    elif HHFAMINC in [4,5]:
        est_income= (10000+14999)/2
    elif HHFAMINC in [6,7]:
        est_income= (15000+24999)/2
    elif HHFAMINC in [8,9]:
        est_income= (25000+34999)/2
    elif HHFAMINC in [10,11]:
        est_income= (35000+49999)/2
    elif HHFAMINC in [12,13]:
        est_income= (50000+74999)/2
    elif HHFAMINC in [14]:
        est_income= (75000+99999)/2
    elif HHFAMINC in [15]:
        est_income= (100000+149999)/2
    elif HHFAMINC in [16]:
        est_income=(150000+500000)/2
    return est_income/100000
# %%
atus_df['income_val']   =atus_df['HEFAMINC'].apply(income_est)
atus_df['HEFAMINC']     =atus_df['HEFAMINC'].apply(income_group)
atus_df['PEEDUCA']      =atus_df['PEEDUCA'].apply(edu_class)
atus_df['AGE']          =atus_df['PRTAGE']
atus_df['PRTAGE']       =atus_df['PRTAGE'].apply(age_est)
atus_df['PESEX']        =atus_df['PESEX'].apply(sex_class)
atus_df['PTDTRACE']     =atus_df['PTDTRACE'].apply(race_class)
atus_df['TESCHENR']     =atus_df['TESCHENR'].apply(student_class)
atus_df['GTMETSTA']     =atus_df['GTMETSTA'].apply(msa_id)
atus_df['PREXPLF']      =atus_df['PREXPLF'].apply(employment)
atus_df.rename(columns = {'HEFAMINC':'income_cls',
'PEEDUCA':'EDUC',
'PRTAGE':'R_AGE_IMP',
'PESEX':'R_SEX_IMP',
'PTDTRACE':'R_RACE',
'TESCHENR':'SCHTYP',
'GTMETSTA':'MSACAT',
'PREXPLF':'WORKER',
"GEREG":'CENSUS_R',
'HRNUMHOU': 'HHSIZE'}, inplace = True)

# list of variables that have class
    ## Need to update!!, if functions change used in "Process variables using function"  
Class_vars= ['EDUC','SCHTYP', 'WORKER','R_AGE_IMP','R_RACE','R_SEX_IMP','income_cls','MSACAT','CENSUS_R','general_choice', 'ondemand_choice']

# Create class variables that has more than two classes
cat_vars=[]
for var_c in Class_vars:
    if atus_df[var_c].unique().size >2:
        cat_vars.append(var_c)
for var in cat_vars:
    cat_list='var'+'_'+var
    cat_list = pd.get_dummies(atus_df[var], prefix=var)
    atus_df=atus_df.join(cat_list)

atus_df["Avail"] =1
for col in atus_df.columns:
    print (col)


with open('Description of ATUS.txt', 'a') as f:
    for col in atus_df.columns:
        desc_df=DescrStatsW(atus_df[col], weights=atus_df.TUFINLWGT, ddof=1)
        print ('{}'.format(col), file=f)
        print ("{}".format(desc_df.mean), file=f)
        print ("{}".format(desc_df.std), file=f)
        print ("{}".format(atus_df[col].min()), file=f)
        print ("{}".format(atus_df[col].max()), file=f)
sample_sz= atus_df.TUFINLWGT.size
sum_wgt=atus_df.TUFINLWGT.sum()    
atus_df["TUFINLWGT"]=atus_df["TUFINLWGT"].apply(lambda x: x/sum_wgt*sample_sz)      
#atus_df.groupby(['onlineshop'])['onlineshop'].count()  
# %%
############################################# Model Simulation  ################################
database = db.Database('shop', atus_df)

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

nhts_results = res.bioResults(pickleFile = 'onine_shop_logit_con.pickle')

biogeme = bio.BIOGEME(database, simulate)
biogeme.modelName = 'onlineshop_simul'

nhts_sim_results = biogeme.simulate(nhts_results.getBetaValues())
print(nhts_sim_results.describe())

atus_df['Prob_no']=nhts_sim_results['Prob_no']*10
atus_df['Prob_lo']=nhts_sim_results['Prob_lo']*10
atus_df['Prob_md']=nhts_sim_results['Prob_md']*10
atus_df['Prob_hi']=nhts_sim_results['Prob_hi']*10
# atus_df['online_pf'] = nhts_sim_results.idxmax(axis=1)

# def online_ct(online_pf):
#     if online_pf == "Prob_no":
#         return 0
#     elif online_pf == "Prob_lo":
#         return 1
#     elif online_pf == "Prob_md":
#         return 2
#     elif online_pf == "Prob_hi":
#         return 3      
# atus_df['online_pf'] = atus_df['online_pf'].apply(lambda x: online_ct(x))

# Class_vars= ['online_pf']

# # Create class variables that has more than two classes
# cat_vars=[]
# for var_c in Class_vars:
#     if atus_df[var_c].unique().size >2:
#         cat_vars.append(var_c)
# for var in cat_vars:
#     cat_list='var'+'_'+var
#     cat_list = pd.get_dummies(atus_df[var], prefix=var)
#     atus_df=atus_df.join(cat_list)                          


############################################# general Model estimation ################################
# %%
## shopping nested 
database = db.Database('shop', atus_df)

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
logprob = models.lognested(V, av, nests, general_choice)

# Define level of verbosity
logger = msg.bioMessage()
# logger.setSilent()
# logger.setWarning()
logger.setGeneral()
# logger.setDetailed()

# Create the Biogeme object
formulas = {'loglike': logprob, 'weight': TUFINLWGT}
biogeme = bio.BIOGEME(database, formulas)
biogeme.modelName = "general_nest"


# Create the Biogeme object
#logprob = models.loglogit(V, av, shop_choice)
# formulas = {'loglike': logprob, 'weight': TUFINLWGT}
# biogeme = bio.BIOGEME(database, formulas)
# biogeme.modelName = 'shopping_MNL'

# Calculate the null log likelihood for reporting.
biogeme.calculateNullLoglikelihood(av)

# Estimate the parameters
results = biogeme.estimate()
pandasResults = results.getEstimatedParameters()
print(pandasResults)
# %%
############################################# Ondemand Model estimation ################################
# %%
################### final model -on demand ##########
database = db.Database('shop', atus_df)

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
logprob = models.lognested(V, av, nests, ondemand_choice)

# Define level of verbosity
logger = msg.bioMessage()
# logger.setSilent()
# logger.setWarning()
logger.setGeneral()
# logger.setDetailed()

# Create the Biogeme object
formulas = {'loglike': logprob, 'weight': TUFINLWGT}
biogeme = bio.BIOGEME(database, formulas)
biogeme.modelName = "ondemand_nest"
################### final model ##########

# Create the Biogeme object
#logprob = models.loglogit(V, av, shop_choice)
# formulas = {'loglike': logprob, 'weight': TUFINLWGT}
# biogeme = bio.BIOGEME(database, formulas)
# biogeme.modelName = 'shopping_MNL'

# Calculate the null log likelihood for reporting.
biogeme.calculateNullLoglikelihood(av)

# Estimate the parameters
results = biogeme.estimate()
pandasResults = results.getEstimatedParameters()
print(pandasResults)
# %%
