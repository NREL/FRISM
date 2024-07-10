# %%
import pandas as pd
import numpy as np
import joblib
from argparse import ArgumentParser
import config_ST as config
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
import statsmodels.formula.api as smf
import seaborn as sns
import matplotlib.pyplot as plt

def input_files_processing(household_file, person_file,x_var_candidate_hh, x_var_candidate_per):
    # Household data processing
    # Read NHTS household data
    nhts_hh = pd.read_csv(household_file, header=0, sep=',')
    
    # Select data within the State (e.g., CA, TX, MI) where the study area is located   
    #nhts_hh = nhts_hh[nhts_hh['HH_CBSA'].isin(state_CBSA)]
    
    # Subset of data with potential X variables for model estimation 
    nhts_hh= nhts_hh[x_var_candidate_hh]
    
    # Filter out records that have not valid response
    ## Exlude HOUSEID (key ID) and HH_CBSA (v_type=object, not used in modeling)
    ## var_x should be "int"; Need to check if there is object type variable in a new variable set
    for var_x in x_var_candidate_hh:
        if var_x not in ['HOUSEID']: 
            nhts_hh = nhts_hh[nhts_hh[var_x]>=0]

    # Process variables using function         
    nhts_hh['income_est']=nhts_hh['HHFAMINC'].apply(income_est)
    nhts_hh['income_cls']=nhts_hh['HHFAMINC'].apply(income_group)
    #nhts_hh['WEBUSE17']=nhts_hh['WEBUSE17'].apply(web_class)
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
    #nhts_per = nhts_per[nhts_per['HH_CBSA'].isin(state_CBSA)]
    
    # Subset of data with potential X variables for model estimation 
    nhts_per= nhts_per[x_var_candidate_per]
    
    # Filter out records that have not valid response
    ## Exlude HOUSEID (key ID) and HH_CBSA (v_type=object, not used in modeling)
    ## var_x should be "int"; Need to check if there is object type variable in a new variable set
    for var_x in x_var_candidate_per:
        if var_x not in ['HOUSEID']: 
            nhts_per = nhts_per[nhts_per[var_x]>=-1]
    # Add "WEBUSE17" from household        
    nhts_per = nhts_per.merge(nhts_hh[['HOUSEID','income_est','income_cls']], on='HOUSEID', how='inner')
    # Select records with age>16 with assumption that person>16 years old can do online shopping
    nhts_per = nhts_per[nhts_per['R_AGE']>=16]           

    # Process variables using function         
    nhts_per['EDUC']=nhts_per['EDUC'].apply(edu_class)
    nhts_per['SCHTYP']=nhts_per['SCHTYP'].apply(student_class)
    #nhts_per['WRK_HOME']=nhts_per['WRK_HOME'].apply(wfh_class)
    nhts_per['WORKER']=nhts_per['WORKER'].apply(work_class)
    nhts_per['R_AGE']=nhts_per['R_AGE'].apply(age_est)
    nhts_per['WRKTRANS']=nhts_per['WRKTRANS'].apply(mode_est)
    nhts_per['onlineshop']=nhts_per['DELIVER'].apply(onlineshop_class)
    nhts_per['R_RACE']=nhts_per['R_RACE'].apply(race_class)
    nhts_per['R_SEX']=nhts_per['R_SEX'].apply(sex_class)      

    # list of variables that have class
    ## Need to update!!, if functions change used in "Process variables using function"  
    Class_vars= ['EDUC','SCHTYP', 'WORKER','R_AGE', 'WRKTRANS','R_RACE','R_SEX','income_cls'] 

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
    if DELIVER  > 0: 
        return 1
    else:
        return 0
# %%
hh_file="../../../FRISM_input_output_ST/Model_inputs/NHTS_22/hhpub.csv"
per_file="../../../FRISM_input_output_ST/Model_inputs/NHTS_22/perpub.csv"
x_var_candidate_hh=config.x_var_candidate_hh
x_var_candidate_per=config.x_var_candidate_per
df_hh_22, df_per_22 = input_files_processing(hh_file, per_file,
                                                        x_var_candidate_hh, x_var_candidate_per)

hh_file="../../../FRISM_input_output_ST/Model_inputs/NHTS/hhpub.csv"
per_file="../../../FRISM_input_output_ST/Model_inputs/NHTS/perpub.csv"
x_var_candidate_hh=config.x_var_candidate_hh
x_var_candidate_per=config.x_var_candidate_per_17
df_hh_17, df_per_17 = input_files_processing(hh_file, per_file,
                                                        x_var_candidate_hh, x_var_candidate_per)


df_per_22_hh=df_per_22.groupby(['HOUSEID'])['DELIVER'].agg(delivery_f='sum').reset_index()
df_hh_22=df_hh_22.merge(df_per_22_hh, on='HOUSEID', how='left')

df_per_17_hh=df_per_17.groupby(['HOUSEID'])['DELIVER'].agg(delivery_f='sum').reset_index()
df_hh_17=df_hh_17.merge(df_per_17_hh, on='HOUSEID', how='left')

df_per_22_hh=df_per_22.groupby(['HOUSEID']).agg(delivery_f=('DELIVER', 'sum'),
                                                food_f=('DELIV_FOOD', 'sum'),
                                                good_f=('DELIV_GOOD', 'sum'),
                                                groc_f=('DELIV_GROC', 'sum')).reset_index()

df_hh_22=df_hh_22.merge(df_per_22_hh, on='HOUSEID', how='left')

df_hh_22.to_csv("../../../FRISM_input_output_ST/Sim_outputs/Generation/NHTS_processed.csv" )






# df_hh_22=df_hh_22.dropna(subset=['delivery_f'])
# df_hh_17=df_hh_17.dropna(subset=['delivery_f'])


df_hh_22['flag'] =df_hh_22['delivery_f'].apply(lambda x: 0 if np.isnan(x) else 1)
df_hh_17['flag'] =df_hh_17['delivery_f'].apply(lambda x: 0 if np.isnan(x) else 1)

df_hh_22=df_hh_22[df_hh_22['flag'] ==1]
df_hh_17=df_hh_17[df_hh_17['flag'] ==1]

df_hh_22[df_hh_22['delivery_f']==0].shape[0]/df_hh_22.shape[0]
df_hh_17[df_hh_17['delivery_f']==0].shape[0]/df_hh_17.shape[0]

# %%
plt.figure(figsize = (8,6))
plt.hist(df_hh_22['delivery_f'], color ="blue", density=True, bins=int(df_hh_22['delivery_f'].max()), alpha = 0.3, label="2022", weights=df_hh_22['WTHHFIN'])
plt.hist(df_hh_17['delivery_f'], color ="red", density=True, bins=int(df_hh_17['delivery_f'].max()), alpha = 0.3, label="2017", weights=df_hh_17['WTHHFIN'])
plt.title("Density of Delivery Frequency")
plt.legend(loc="upper right")
plt.savefig('../../../FRISM_input_output_ST/Sim_outputs/Generation/comparison.png')

plt.figure(figsize = (8,6))
plt.hist(df_hh_22[df_hh_22['delivery_f']<=60]['delivery_f'], color ="blue", density=True, bins=int(df_hh_22[df_hh_22['delivery_f']<=60]['delivery_f'].max()), alpha = 0.3, label="2022",  weights=df_hh_22[df_hh_22['delivery_f']<=60]['WTHHFIN'])
plt.hist(df_hh_17[df_hh_17['delivery_f']<=60]['delivery_f'], color ="red", density=True, bins=int(df_hh_17[df_hh_17['delivery_f']<=60]['delivery_f'].max()), alpha = 0.3, label="2017", weights=df_hh_17[df_hh_17['delivery_f']<=60]['WTHHFIN'])
plt.title("Density of Delivery Frequency")
plt.legend(loc="upper right")
plt.savefig('../../../FRISM_input_output_ST/Sim_outputs/Generation/comparison_60.png')



plt.figure(figsize = (8,6))
plt.hist(df_hh_22[df_hh_22['delivery_f']>60]['delivery_f'], color ="blue", density=True, bins=int(df_hh_22[df_hh_22['delivery_f']>60]['delivery_f'].max()), alpha = 0.3, label="2022",  weights=df_hh_22[df_hh_22['delivery_f']>60]['WTHHFIN'])
plt.hist(df_hh_17[df_hh_17['delivery_f']>60]['delivery_f'], color ="red", density=True, bins=int(df_hh_17[df_hh_17['delivery_f']>60]['delivery_f'].max()), alpha = 0.3, label="2017", weights=df_hh_17[df_hh_17['delivery_f']>60]['WTHHFIN'])
plt.title("Density of Delivery Frequency")
plt.legend(loc="upper right")
plt.savefig('../../../FRISM_input_output_ST/Sim_outputs/Generation/comparison>60.png')

# %%

list_income=["income_cls_0","income_cls_1","income_cls_2","income_cls_3"]
dic_income={"income_cls_0": "income <$35k",
            "income_cls_1": "income $35k-$75k",
            "income_cls_2": "income $75k-125k",
            "income_cls_3": "income >$125k"}
    
for ic_nm in list_income:
    plt.figure(figsize = (8,6))
    #plt.hist(df_hh_obs[df_hh_obs[ic_nm]==1]['delivery_f'], color ="blue", density=True, bins=df_hh_obs[df_hh_obs[ic_nm]==1]['delivery_f'].max(), alpha = 0.3, label="observed")
    #plt.hist(df_hh_model[(df_hh_model[ic_nm]==1) & (df_hh_model['delivery_f']<=30)]['delivery_f'], color ="red", density=True, bins=80, alpha = 0.3, label="modeled")
    #plt.hist(df_hh_model[(df_hh_model[ic_nm]==1)]['delivery_f'], color ="red", density=True, bins=df_hh_model[(df_hh_model[ic_nm]==1)]['delivery_f'].max(), alpha = 0.3, label="modeled")
    plt.hist(df_hh_22[(df_hh_22[ic_nm]==1) & (df_hh_22['delivery_f']<=60)]['delivery_f'], color ="blue", density=True, bins=int(df_hh_22[(df_hh_22[ic_nm]==1) & (df_hh_22['delivery_f']<=60)]['delivery_f'].max()), alpha = 0.3, label="2022", weights=df_hh_22[(df_hh_22[ic_nm]==1) & (df_hh_22['delivery_f']<=60)]['WTHHFIN'])
    plt.hist(df_hh_17[(df_hh_17[ic_nm]==1)& (df_hh_17['delivery_f']<=60)]['delivery_f'], color ="red", density=True, bins=int(df_hh_17[(df_hh_17[ic_nm]==1)& (df_hh_17['delivery_f']<=60)]['delivery_f'].max()), alpha = 0.3, label="2017",weights=df_hh_17[(df_hh_17[ic_nm]==1) & (df_hh_17['delivery_f']<=60)]['WTHHFIN'])
    plt.title("Density of Delivery Frequency in {0}".format(dic_income[ic_nm]))
    plt.legend(loc="upper right")
    plt.savefig('../../../FRISM_input_output_ST/Sim_outputs/Generation/B2C_delivery_freq_{0}.png'.format(ic_nm))



# %%
def web_model(df_hh_state,state_CBSA,study_CBSA,selected_x_var_hh):
    # create training & test set : 
    ## Train data: Non-study data + 30% of study area data
    ## Test data: 70% of study area data
    ### Filter two sets from state data
    df_hh_non_study=df_hh_state[df_hh_state['HH_CBSA'].isin(list(set(state_CBSA)-set(study_CBSA)))]
    df_hh_study=df_hh_state[df_hh_state['HH_CBSA'].isin(study_CBSA)]
    val_hh=df_hh_study.groupby(['income_cls','WEBUSE17'])['income_cls'].agg(num_hh='count').reset_index()
    val_hh.to_csv('../../../FRISM_input_output_{}/Sim_outputs/Generation/{}_webuse_by_income_observed.csv'.format(config.study_region,config.study_region), index = False, header=True)
    ### Save Studay region data for validation 
    df_hh_study.to_csv('../../../FRISM_input_output_{}/Model_inputs/NHTS/{}_hh.csv'.format(config.study_region,config.study_region), index = False, header=True)
    
    X_non_study=df_hh_non_study[selected_x_var_hh]
    Y_non_study=df_hh_non_study['WEBUSE17']
    X_study=df_hh_study[selected_x_var_hh]
    Y_study=df_hh_study['WEBUSE17']
    trainX, testX, trainY, testY = train_test_split(X_study, Y_study, test_size = 0.7)
    trainX=pd.concat([trainX,X_non_study])
    trainY=pd.concat([trainY,Y_non_study])
    
    # SMOTE approach for lower sample issue for less frequent data
    oversample = SMOTE()
    trainX,trainY = oversample.fit_resample(trainX,trainY)
    
    # initial model
    model_int = LogisticRegression(solver='newton-cg', multi_class='multinomial')
    model_int.fit(trainX, trainY)
    y_pred = model_int.predict(testX)
    
    with open('B2C_gen_model_estiation_results.txt', 'a') as f:
        print ('************* Webuse Model: inital model ****************', file=f)
        print('Accuracy for initial model: {:.2f}'.format(accuracy_score(testY, y_pred)), file=f)
        print('Error rate for initial model: {:.2f}'.format(1 - accuracy_score(testY, y_pred)), file=f)
        print ('initial confusion matirix)', confusion_matrix(testY.tolist(), y_pred), file=f)


    # CalibratedclassifierCV approach to improve the model 
    testX_SM,testY_SM = oversample.fit_resample(testX,testY)
    model_cal = CalibratedClassifierCV(model_int, cv='prefit')
    model_cal.fit(testX_SM,testY_SM)

    y_pred_cal = model_cal.predict(testX)
    with open('B2C_gen_model_estiation_results.txt', 'a') as f:
        print ('************* Webuse Model: calibrated model ****************', file=f)
        print('Accuracy for calibrated model: {:.2f}'.format(accuracy_score(testY, y_pred_cal)), file=f)
        print('Error rate for calibrated model: {:.2f}'.format(1 - accuracy_score(testY, y_pred_cal)), file=f)
        print ('calibrated confusion matrix', confusion_matrix(testY, y_pred_cal), file=f)
        print('coef/intercept for initial M',model_int.coef_, model_int.intercept_, file=f)

    filename = '../Simulation/webuse_model.sav'
    joblib.dump(model_cal, filename)

def online_model(df_per_state,state_CBSA,study_CBSA,selected_x_var_per):
    # create training & test set : 
    ## Train data: Non-study data + 30% of study area data
    ## Test data: 70% of study area data
    ### Filter two sets from state data
    df_per_non_study=df_per_state[df_per_state['HH_CBSA'].isin(list(set(state_CBSA)-set(study_CBSA)))]
    df_per_study=df_per_state[df_per_state['HH_CBSA'].isin(study_CBSA)]
    val_per=df_per_study.groupby(['income_cls','onlineshop'])['income_cls'].agg(num_hh='count').reset_index()
    val_per.to_csv('../../../FRISM_input_output_{}/Sim_outputs/Generation/{}_online_by_income_observed.csv'.format(config.study_region,config.study_region), index = False, header=True)

    ### Save Studay region data for validation 
    df_per_study.to_csv('../../../FRISM_input_output_{}/Model_inputs/NHTS/{}_per.csv'.format(config.study_region,config.study_region), index = False, header=True)
    
    X_non_study=df_per_non_study[selected_x_var_per]
    Y_non_study=df_per_non_study['onlineshop']
    X_study=df_per_study[selected_x_var_per]
    Y_study=df_per_study['onlineshop']
    trainX, testX, trainY, testY = train_test_split(X_study, Y_study, test_size = 0.7)
    trainX=pd.concat([trainX,X_non_study])
    trainY=pd.concat([trainY,Y_non_study])
    
    # SMOTE approach for lower sample issue for less frequent data
    oversample = SMOTE()
    trainX,trainY = oversample.fit_resample(trainX,trainY)
    
    # initial model
    model_int = LogisticRegression(solver='newton-cg', multi_class='ovr')
    model_int.fit(trainX, trainY)
    y_pred = model_int.predict(testX)
    
    with open('B2C_gen_model_estiation_results.txt', 'a') as f:
        print ('************* Online Model: inital model ****************', file=f)
        print('Accuracy for initial model: {:.2f}'.format(accuracy_score(testY, y_pred)), file=f)
        print('Error rate for initial model: {:.2f}'.format(1 - accuracy_score(testY, y_pred)), file=f)
        print ('initial confusion matirix)', confusion_matrix(testY.tolist(), y_pred), file=f)

    filename = '../Simulation/online_shop_model.sav'
    joblib.dump(model_int, filename)

    # # CalibratedclassifierCV approach to improve the model 
    # testX_SM,testY_SM = oversample.fit_resample(testX,testY)
    # model_cal = CalibratedClassifierCV(model_int, cv='prefit')
    # model_cal.fit(testX_SM,testY_SM)

    # y_pred_cal = model_cal.predict(testX)
    # with open('B2C_gen_model_estiation_results.txt', 'a') as f:
    #     print ('************* Online Model: calibrated model ****************', file=f)
    #     print('Accuracy for calibrated model: {:.2f}'.format(accuracy_score(testY, y_pred_cal)), file=f)
    #     print('Error rate for calibrated model: {:.2f}'.format(1 - accuracy_score(testY, y_pred_cal)), file=f)
    #     print ('calibrated confusion matrix', confusion_matrix(testY, y_pred_cal), file=f)
    #     print('coef/intercept for initial M',model_int.coef_, model_int.intercept_, file=f)

    # filename = '../Simulation/online_shop_model.sav'
    # joblib.dump(model_cal, filename)

def delivery_model(df_per_state,state_CBSA,study_CBSA,selected_x_var_per):
    # create training & test set : 
    ## Train data: Non-study data + 30% of study area data
    ## Test data: 70% of study area data
    ### Filter two sets from state data
    df_per_state=df_per_state[df_per_state['onlineshop']==1]
    df_per_non_study=df_per_state[df_per_state['HH_CBSA'].isin(list(set(state_CBSA)-set(study_CBSA)))]
    df_per_study=df_per_state[df_per_state['HH_CBSA'].isin(study_CBSA)]
    
    X_non_study=df_per_non_study[selected_x_var_per]
    Y_non_study=df_per_non_study['DELIVER']
    X_study=df_per_study[selected_x_var_per]
    Y_study=df_per_study['DELIVER']
    trainX, testX, trainY, testY = train_test_split(X_study, Y_study, test_size = 0.7)
    trainX=pd.concat([trainX,X_non_study])
    trainY=pd.concat([trainY,Y_non_study])
    
    # Find alpha for the model 
    poisson_training_results = sm.GLM(trainY, trainX, family=sm.families.Poisson()).fit()
    df_train=pd.DataFrame(trainY)
    df_train['BB_LAMBDA'] = poisson_training_results.mu
    df_train['AUX_OLS_DEP'] = df_train.apply(lambda x: ((x['DELIVER'] - x['BB_LAMBDA'])**2 - x['BB_LAMBDA']) / x['BB_LAMBDA'], axis=1)
    ols_expr = """AUX_OLS_DEP ~ BB_LAMBDA - 1"""
    aux_olsr_results = smf.ols(ols_expr, df_train).fit()

    
    # model
    result=sm.GLM(trainY, trainX,family=sm.families.NegativeBinomial(alpha=aux_olsr_results.params[0])).fit()
    filename = '../Simulation/delivery_freq_model.sav'
    joblib.dump(result, filename)
    
    with open('B2C_gen_model_estiation_results.txt', 'a') as f:
        print ('************* Delivery Model ****************', file=f)
        print('Summary report:', file=f)
        print(result.summary(), file=f)

    pop_predict=result.predict(testX)
    pop_predict=pop_predict.apply(lambda x: 1 if x<=1 else round(x-0.5))
    sns.displot(testY)
    plt.savefig('Delivery plot observed_testset.png')
    sns.displot(pop_predict)
    plt.savefig('Delivery plot modeled_testset.png')

    with open('B2C_gen_model_estiation_results.txt', 'a') as f:
        print ('************* Delivery Model ****************', file=f)
        print('Model performance (Mean Squared Error): {:.2f}'.format(mean_squared_error(testY, pop_predict)) , file=f)

def main(args=None):
    # read input files
    parser = ArgumentParser()
    parser.add_argument("-hf", "--household_file", dest="hh_file",
                        help="household file in csv format", required=True, type=str)
    parser.add_argument("-pf", "--person_file", dest="per_file",
                        help="person file in csv format", required=True, type=str)
    parser.add_argument("-mt", "--models", dest="models",
                        help="models abbreviation", required=True, type=str) # W: web only,O: Online shop only ,D: Delivery only ,WOD                         
    args = parser.parse_args()
    
    # input file processing for selecting variables
    state_CBSA=config.state_CBSA
    x_var_candidate_hh=config.x_var_candidate_hh
    x_var_candidate_per=config.x_var_candidate_per
    state_CBSA=config.state_CBSA
    study_CBSA=config.study_CBSA

    df_hh_state, df_per_state = input_files_processing(args.hh_file, args.per_file,
                                                        state_CBSA,x_var_candidate_hh, x_var_candidate_per)

    if args.models == "W":
        web_model(df_hh_state,state_CBSA,study_CBSA,config.selected_x_var_web)
    elif args.models == "O":
        online_model(df_per_state,state_CBSA,study_CBSA,config.selected_x_var_online)
    elif args.models == "D":
        delivery_model(df_per_state,state_CBSA,study_CBSA,config.selected_x_var_delivery)
    elif args.models == "WOD":
        web_model(df_hh_state,state_CBSA,study_CBSA,config.selected_x_var_web)
        online_model(df_per_state,state_CBSA,study_CBSA,config.selected_x_var_online)
        delivery_model(df_per_state,state_CBSA,study_CBSA,config.selected_x_var_delivery)
    else: 
        print ("You need to input models: W: web only,O: Online shop only ,D: Delivery only ,WOD: All")                 



if __name__ == "__main__":
    main()