# %%
import pandas as pd
import biogeme.database as db
import biogeme.biogeme as bio
from biogeme import models
from biogeme.expressions import Beta
import numpy as np
import config_b2c as config
from statsmodels.stats.weightstats import DescrStatsW

def input_files_processing(person_file,x_var_candidate_per, at_dir, at_var_act, at_var_resp, at_var_cps ):
    nhts_per = pd.read_csv(person_file, header=0, sep=',')

    # Subset of data with potential X variables for model estimation 
    nhts_per= nhts_per[x_var_candidate_per]
    
    # Filter out records that have not valid response
    ## Exlude HOUSEID (key ID) and HH_CBSA (v_type=object, not used in modeling)
    ## var_x should be "int"; Need to check if there is object type variable in a new variable set
    for var_x in x_var_candidate_per:
        if var_x in ['DELIVER']: 
            nhts_per = nhts_per[nhts_per[var_x]>=0]         
        elif var_x not in ['HOUSEID','HH_CBSA']: 
            nhts_per = nhts_per[nhts_per[var_x]>=-1]    
    # Add "WEBUSE17" from household        
    # Select records with age>16 with assumption that person>16 years old can do online shopping
    nhts_per = nhts_per[nhts_per['R_AGE_IMP']>=16]           

    # Process variables using function         
    nhts_per['EDUC']=nhts_per['EDUC'].apply(edu_class)
    nhts_per['SCHTYP']=nhts_per['SCHTYP'].apply(student_class)
    nhts_per['WORKER']=nhts_per['WORKER'].apply(work_class)
    nhts_per['R_AGE']=nhts_per['R_AGE_IMP']
    nhts_per['R_AGE_IMP']=nhts_per['R_AGE_IMP'].apply(age_est)
    nhts_per['onlineshop']=nhts_per['DELIVER'].apply(onlineshop_class)
    nhts_per['R_RACE']=nhts_per['R_RACE'].apply(race_class)
    nhts_per['R_SEX_IMP']=nhts_per['R_SEX_IMP'].apply(sex_class)
    nhts_per['MSACAT']=nhts_per['MSACAT'].apply(msa_id)
    nhts_per['income_cls']=nhts_per['HHFAMINC'].apply(income_group)       
    nhts_per['income_val']=nhts_per['HHFAMINC'].apply(income_est)  

    # list of variables that have class
    ## Need to update!!, if functions change used in "Process variables using function"  
    Class_vars= ['EDUC','SCHTYP', 'WORKER','R_AGE_IMP','R_RACE','R_SEX_IMP','income_cls','MSACAT','CENSUS_R', "onlineshop"] 

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
    ########### ATUS data processing #########
    atus_act= pd.read_csv(at_dir+'atusact_2019.dat', sep=',', engine='python')
    atus_resp= pd.read_csv(at_dir+'atusresp_2019.dat', sep=',', engine='python')
    #atus_rost= pd.read_csv(fdir_input+'atusrost_2019.dat', sep=',', engine='python')
    atus_cps= pd.read_csv(at_dir+'atuscps_2019.dat', sep=',', engine='python')

    atus_act  = atus_act[at_var_act]
    atus_resp = atus_resp[at_var_resp]
    atus_cps  = atus_cps[at_var_cps]

    atus_resp =atus_resp.merge(atus_cps, on=["TUCASEID","TULINENO"], how="left")
    atus_resp =atus_resp[atus_resp["TULINENO"]==1]


    atus_act['offline_shop']=atus_act.apply(lambda x: offline_shop(x['TEWHERE'], x['TRCODE']), axis=1)
    atus_act['online_shop']=atus_act.apply(lambda x: online_shop(x['TEWHERE'], x['TRCODE']), axis=1)
    atus_act['offline_od']=atus_act.apply(lambda x: offline_ondemand(x['TEWHERE'], x['TRCODE']), axis=1)
    atus_act['online_od']=atus_act.apply(lambda x: online_ondemand(x['TEWHERE'], x['TRCODE']), axis=1)
    atus_df=atus_act.groupby(['TUCASEID']).agg({'offline_shop':[sum],'online_shop':[sum],'offline_od':[sum],'online_od':[sum]})
    atus_df.columns = ["_".join(x) for x in atus_df.columns.ravel()]
    atus_df.reset_index(level=(0), inplace=True)                
    atus_df['general_choice']=atus_df.apply(lambda x: shop_choice(x['offline_shop_sum'], x['online_shop_sum']), axis=1)
    atus_df['shop']=atus_df['general_choice'].apply(lambda x: 1 if x>=1 else 0 )
    atus_df['ondemand_choice']=atus_df.apply(lambda x: shop_choice(x['offline_od_sum'], x['online_od_sum']), axis=1)
    atus_df['ondemand']=atus_df['ondemand_choice'].apply(lambda x: 1 if x>=1 else 0 )
    atus_df.to_csv(at_dir+"atus_df_processed_jul.csv")
    atus_df =atus_df.merge(atus_resp, on=["TUCASEID"], how="left")

    return nhts_per

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
        est_income= (0+10000)/2
    elif HHFAMINC == 2:
        est_income= (10000+14999)/2
    elif HHFAMINC == 3:
        est_income= (15000+24999)/2
    elif HHFAMINC == 4:
        est_income= (25000+34999)/2
    elif HHFAMINC == 5:
        est_income= (35000+49999)/2
    elif HHFAMINC == 6:
        est_income= (50000+74999)/2
    elif HHFAMINC == 7:
        est_income= (75000+99999)/2
    elif HHFAMINC == 8:
        est_income= (100000+124999)/2
    elif HHFAMINC == 9:
        est_income=(125000+149999)/2
    elif HHFAMINC == 10:
        est_income= (150000+199999)/2
    elif HHFAMINC == 11:
        est_income= (200000+500000)/2
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
## Model Variable: 0: not applicalbe(-1)+others, 1: personal car, 2: public, 3: walk+bike  
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
    if DELIVER  == 0: 
        return 0
    elif DELIVER  > 0 and DELIVER <=4:
        return 1
    elif DELIVER  >4  and DELIVER <=8:
        return 2
    else: return 3        

def msa_id(MSACAT):
    if MSACAT ==4:
        return 0
    else: 
        return 1 
    
# %%
def online_preference (per_file,x_var_candidate_per): # config.per_file, config.x_var_candidate_per
    df = input_files_processing(per_file,x_var_candidate_per)
    df["Avail"] =1
    # Descriptive statistics
    # with open('Description of NHTS.txt', 'a') as f:
    #     for col in df.columns:
    #         desc_df=DescrStatsW(df[col], weights=df.WTPERFIN, ddof=1)
    #         print ('{}'.format(col), file=f)
    #         print ("{}".format(desc_df.mean), file=f)
    #         print ("{}".format(desc_df.std), file=f)
    #         print ("{}".format(df[col].min()), file=f)
    #         print ("{}".format(df[col].max()), file=f)
    # sample_sz= df.WTPERFIN.size
    # sum_wgt=df.WTPERFIN.sum()    
    # df["WTPERFIN"]=df["WTPERFIN"].apply(lambda x: x/sum_wgt*sample_sz)   
    # df.groupby(['onlineshop'])['onlineshop'].count()

    # online_only=df[df['onlineshop']>0]
    # desc_df=DescrStatsW(online_only["DELIVER"], weights=online_only.WTPERFIN, ddof=1).mean

    # %%
    ## Read the data
    #df = pd.read_csv('swissmetro.dat', sep='\t')
    database = db.Database('NHTS', df)

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
    B_income_cls_1_V0= Beta('B_income_cls_1_V0', 0, None, None, 1)
    B_income_cls_1_V1= Beta('B_income_cls_1_V1', 0, None, None, 0)
    B_income_cls_1_V2= Beta('B_income_cls_1_V2', 0, None, None, 0)
    B_income_cls_1_V3= Beta('B_income_cls_1_V3', 0, None, None, 0)
    ###
    B_income_cls_2_V0= Beta('B_income_cls_2_V0', 0, None, None, 1)
    B_income_cls_2_V1= Beta('B_income_cls_2_V1', 0, None, None, 0)
    B_income_cls_2_V2= Beta('B_income_cls_2_V2', 0, None, None, 0)
    B_income_cls_2_V3= Beta('B_income_cls_2_V3', 0, None, None, 0)
    ###
    B_income_cls_3_V0= Beta('B_income_cls_3_V0', 0, None, None, 1)
    B_income_cls_3_V1= Beta('B_income_cls_3_V1', 0, None, None, 0)
    B_income_cls_3_V2= Beta('B_income_cls_3_V2', 0, None, None, 0)
    B_income_cls_3_V3= Beta('B_income_cls_3_V3', 0, None, None, 0)
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
    av = {0: Avail, 1: Avail, 2: Avail, 3: Avail}

    # Definition of the model. This is the contribution of each
    # observation to the log likelihood function.
    logprob = models.loglogit(V, av, onlineshop)

    # Create the Biogeme object
    formulas = {'loglike': logprob, 'weight': WTPERFIN}
    biogeme = bio.BIOGEME(database, formulas)
    biogeme.modelName = 'onine_shop_logit_con'

    # Calculate the null log likelihood for reporting.
    biogeme.calculateNullLoglikelihood(av)

    # Estimate the parameters
    results = biogeme.estimate()

    # Get the results in a pandas table
    pandasResults = results.getEstimatedParameters()
    print(pandasResults)    
 
 
# %%
if __name__ == "__main__":
    main()