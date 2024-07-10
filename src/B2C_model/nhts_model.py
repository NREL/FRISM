# %%
import pandas as pd
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
fdir_input= "../../../B2C_Data/NHTS_22/"
df=pd.read_csv(fdir_input+"nhts_df_model_2022.csv")
df=df.rename(columns={'EDUC_0.0':"EDUC_0" , 'EDUC_1.0':"EDUC_1",
       'EDUC_2.0':"EDUC_2", 'EDUC_3.0':"EDUC_3"})

sample_sz= df.WTPERFIN.size
sum_wgt=df.WTPERFIN.sum()    
#df["TUFINLWGT"]=df["TUFINLWGT"].apply(lambda x: x*sample_sz/sum_wgt)
df["WTPERFIN"]=df["WTPERFIN"].apply(lambda x:  (x/sum_wgt)/(1/sample_sz)) 

# online choice
# %%
df["online_choice"] = df['DELIVER'].apply(lambda x: 0 if x==0 else 1)

fit = smf.glm("online_choice ~ \
              R_AGE_0+R_AGE_1+R_AGE_2+R_AGE_3+R_AGE_4+\
              income_cls_0+income_cls_1+income_cls_2+income_cls_3+income_cls_4+income_cls_5+\
                HHSIZE+R_SEX_IMP+WORKER",
              family=sm.families.Binomial(),data=df, freq_weights=df['WTPERFIN']).fit()

fit.summary()

# %%
'''
 'DRVRCNT', 'EDUC', 'HOUSEID', 'HHFAMINC', 'HHSIZE',
       'HHVEHCNT', 'MSACAT', 'HH_HISP', 'HOMEOWN', 'HH_RACE', 'WRKCOUNT',
       'R_AGE', 'R_SEX_IMP', 'R_RACE_IMP', 'WORKER', 'DELIVER', 'DELIV_FOOD',
       'DELIV_GOOD', 'DELIV_GROC', 'WTPERFIN', 'URBRUR', 'income_est',
       'income_cls', 'EDUC_0', 'EDUC_1', 'EDUC_2', 'EDUC_3', 'R_AGE_0',
       'R_AGE_1', 'R_AGE_2', 'R_AGE_3', 'R_AGE_4', 'R_RACE_IMP_0',
       'R_RACE_IMP_1', 'R_RACE_IMP_2', 'R_RACE_IMP_3', 'income_cls_0',
       'income_cls_1', 'income_cls_2', 'income_cls_3', 'income_cls_4',
       'income_cls_5', 'online_choice']
'''
# selected_x_var_per= ['HHSIZE', 'WORKER', 'R_AGE_0', 'R_AGE_1', 'R_AGE_2', 'R_AGE_3',
#                     'R_RACE_IMP_0', 'R_RACE_IMP_1', 'R_RACE_IMP_2', 'R_RACE_IMP_3',
#                     'EDUC_0','EDUC_1', 'EDUC_2', 'EDUC_3', 
#                     'income_est','HOMEOWN',"R_SEX_IMP"]
selected_x_var_per= ['HHSIZE', 'WORKER', 'R_AGE_0', 'R_AGE_1', 'R_AGE_2', 'R_AGE_3',
                    'R_RACE_IMP_0', 'R_RACE_IMP_1', 'R_RACE_IMP_2', 'R_RACE_IMP_3',
                    'EDUC_0','EDUC_1', 'EDUC_2', 'EDUC_3', 
                    'income_cls_0', 'income_cls_1', 'income_cls_2',
       'income_cls_3', 'income_cls_4', 'income_cls_5',"R_SEX_IMP"]

df_good=df[df['DELIV_GOOD']>=0]
X=df_good[selected_x_var_per]
Y= df_good['DELIV_GOOD']

# Find alpha for the model 
poisson_training_results = sm.GLM(Y, X, family=sm.families.Poisson()).fit()
df_train=pd.DataFrame(Y)
df_train['BB_LAMBDA'] = poisson_training_results.mu
df_train['AUX_OLS_DEP'] = df_train.apply(lambda x: ((x['DELIV_GOOD'] - x['BB_LAMBDA'])**2 - x['BB_LAMBDA']) / x['BB_LAMBDA'], axis=1)
ols_expr = """AUX_OLS_DEP ~ BB_LAMBDA - 1"""
aux_olsr_results = smf.ols(ols_expr, df_train).fit()


# model
result=sm.GLM(Y, X,family=sm.families.NegativeBinomial(alpha=aux_olsr_results.params[0]),freq_weights=df_good['WTPERFIN']).fit()
#filename = '../Simulation/delivery_freq_model.sav'
#joblib.dump(result, filename)
result.summary()
# with open('B2C_gen_model_estiation_results.txt', 'a') as f:
#     print ('************* Delivery Model ****************', file=f)
#     print('Summary report:', file=f)
#     print(result.summary(), file=f)
# plt.figure(figsize = (8,6))
# plt.hist(Y, color ="blue", bins = Y.max())
# %%
selected_x_var_per= ['HHSIZE', 'WORKER', 'R_AGE_0', 'R_AGE_1', 'R_AGE_2', 'R_AGE_3',
                    'R_RACE_IMP_0', 'R_RACE_IMP_1', 'R_RACE_IMP_2', 'R_RACE_IMP_3',
                    'EDUC_0','EDUC_1', 'EDUC_2', 'EDUC_3', 
                    'income_est',"R_SEX_IMP"]
df_good=df[df['DELIV_GROC']>=0]
X=df_good[selected_x_var_per]
Y= df_good['DELIV_GROC']

# Find alpha for the model 
poisson_training_results = sm.GLM(Y, X, family=sm.families.Poisson()).fit()
df_train=pd.DataFrame(Y)
df_train['BB_LAMBDA'] = poisson_training_results.mu
df_train['AUX_OLS_DEP'] = df_train.apply(lambda x: ((x['DELIV_GROC'] - x['BB_LAMBDA'])**2 - x['BB_LAMBDA']) / x['BB_LAMBDA'], axis=1)
ols_expr = """AUX_OLS_DEP ~ BB_LAMBDA - 1"""
aux_olsr_results = smf.ols(ols_expr, df_train).fit()


# model
result=sm.GLM(Y, X,family=sm.families.NegativeBinomial(alpha=aux_olsr_results.params[0]),freq_weights=df_good['WTPERFIN']).fit()
#filename = '../Simulation/delivery_freq_model.sav'
#joblib.dump(result, filename)
result.summary()
# with open('B2C_gen_model_estiation_results.txt', 'a') as f:
#     print ('************* Delivery Model ****************', file=f)
#     print('Summary report:', file=f)
#     print(result.summary(), file=f)
plt.figure(figsize = (8,6))
plt.hist(Y, color ="blue", bins = Y.max())
# %%
# %%
selected_x_var_per= ['HHSIZE', 'WORKER', 'R_AGE_0', 'R_AGE_1', 'R_AGE_2', 'R_AGE_3',
                    'R_RACE_IMP_0', 'R_RACE_IMP_1', 'R_RACE_IMP_2', 'R_RACE_IMP_3', 
                    'income_est','HOMEOWN',"R_SEX_IMP", "URBRUR"]
df_good=df[df['DELIV_FOOD']>=0]
X=df_good[selected_x_var_per]
Y= df_good['DELIV_FOOD']

# Find alpha for the model 
poisson_training_results = sm.GLM(Y, X, family=sm.families.Poisson()).fit()
df_train=pd.DataFrame(Y)
df_train['BB_LAMBDA'] = poisson_training_results.mu
df_train['AUX_OLS_DEP'] = df_train.apply(lambda x: ((x['DELIV_FOOD'] - x['BB_LAMBDA'])**2 - x['BB_LAMBDA']) / x['BB_LAMBDA'], axis=1)
ols_expr = """AUX_OLS_DEP ~ BB_LAMBDA - 1"""
aux_olsr_results = smf.ols(ols_expr, df_train).fit()


# model
result=sm.GLM(Y, X,family=sm.families.NegativeBinomial(alpha=aux_olsr_results.params[0]),freq_weights=df_good['WTPERFIN']).fit()
#filename = '../Simulation/delivery_freq_model.sav'
#joblib.dump(result, filename)
result.summary()
# with open('B2C_gen_model_estiation_results.txt', 'a') as f:
#     print ('************* Delivery Model ****************', file=f)
#     print('Summary report:', file=f)
#     print(result.summary(), file=f)
plt.figure(figsize = (8,6))
plt.hist(Y, color ="blue", bins = Y.max())
# %%
# %% ############################### Zero-inflated
selected_x_var_per= [ 'WORKER', 'R_AGE_0', 'R_AGE_1', 'R_AGE_2', 'R_AGE_3',
                     "URBRUR","DELIV_GOOD"]
sel_x_inf= ['HHSIZE',"DELIV_GOOD",
            "R_SEX_IMP", "URBRUR"]
df_good=df[df['DELIV_GROC']>=0]
X_inflate= df_good[sel_x_inf]
X=df_good[selected_x_var_per]
Y= df_good['DELIV_GROC']

# model
result=sm.ZeroInflatedPoisson(endog=Y, exog=X, exog_infl=X_inflate, inflation='logit').fit(maxiter=100)

#filename = '../Simulation/delivery_freq_model.sav'
#joblib.dump(result, filename)
result.summary()

# %%
# %%
selected_x_var_per= [ 'WORKER', 'R_AGE_0', 'R_AGE_1', 'R_AGE_2', 'R_AGE_3',
                     "URBRUR","DELIV_GOOD"]
sel_x_inf= ['HHSIZE',"DELIV_GOOD",
            "R_SEX_IMP", "URBRUR"]
df_good=df[df['DELIV_FOOD']>=0]
X_inflate= df_good[sel_x_inf]
X=df_good[selected_x_var_per]
Y= df_good['DELIV_FOOD']

# model
result=sm.ZeroInflatedPoisson(endog=Y, exog=X, exog_infl=X_inflate, inflation='logit').fit(maxiter=100)

#filename = '../Simulation/delivery_freq_model.sav'
#joblib.dump(result, filename)
result.summary()
# %%
