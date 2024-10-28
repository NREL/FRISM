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
import random
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-fn", "--nhtsfilepath", dest="fdir_input_nhts",
                help="file path", required=True, type=str)                
parser.add_argument("-fa", "--atusfilepath", dest="fdir_input_atus",
                    help="file path", required=True, type=str)                                                                                                         
args = parser.parse_args()
# %%

df=pd.read_csv(args.fdir_input_nhts)


sample_sz= df.WTPERFIN.size
sum_wgt=df.WTPERFIN.sum()    
#df["TUFINLWGT"]=df["TUFINLWGT"].apply(lambda x: x*sample_sz/sum_wgt)
df["WTPERFIN"]=df["WTPERFIN"].apply(lambda x:  (x/sum_wgt)/(1/sample_sz)) 

# online choice
# %%
# online choice #####################################
df["online_choice_good"] = df['DELIV_GOOD'].apply(lambda x: 0 if x<=0 else 1)

model = smf.glm("online_choice_good ~ \
              R_AGE_C_1+R_AGE_C_2+R_AGE_C_3+R_AGE_C_4+\
              EDUC_1+EDUC_2+\
              income_cls_1+income_cls_2+income_cls_3+income_cls_4+income_cls_5+\
              HHSIZE+R_SEX_IMP+WORKER+HOMEOWN",
              family=sm.families.Binomial(),data=df, freq_weights=df['WTPERFIN']).fit()

model.summary()
# %%
filename = 'online_choice_good.sav'
joblib.dump(model, filename)

# %%

df["predictions"] = model.predict(df)
df["sel"] = df["predictions"].apply(lambda x: 1 if random.uniform(0, 1) < x else 0) 
df_sel = df[df["sel"]==1]

df["online_choice_food"] = df['DELIV_FOOD'].apply(lambda x: 0 if x<=0 else 1)

model = smf.glm("online_choice_food ~ \
              R_AGE_C_1+R_AGE_C_2+R_AGE_C_3+R_AGE_C_4+\
              EDUC_2+\
              income_cls_1+income_cls_2+income_cls_3+income_cls_4+income_cls_5+\
              R_SEX_IMP+WORKER+HOMEOWN+URBRUR",
              family=sm.families.Binomial(),data=df, freq_weights=df['WTPERFIN']).fit()

model.summary()
filename = 'online_choice_food.sav'
joblib.dump(model, filename)
# %%
df["predictions"] = model.predict(df)
df["sel"] = df["predictions"].apply(lambda x: 1 if random.uniform(0, 1) < x else 0) 
df_sel = df[df["sel"]==1]

# %%
df["online_choice_grc"] = df['DELIV_GROC'].apply(lambda x: 0 if x<=0 else 1)

model = smf.glm("online_choice_grc ~ \
              R_AGE_C_1+R_AGE_C_2+R_AGE_C_3+R_AGE_C_4+\
              EDUC_1+EDUC_2+\
              income_cls_1+income_cls_2+income_cls_3+income_cls_4+income_cls_5+\
              R_SEX_IMP+WORKER+HOMEOWN+URBRUR",
              family=sm.families.Binomial(),data=df, freq_weights=df['WTPERFIN']).fit()

model.summary()
filename = 'online_choice_grc.sav'
joblib.dump(model, filename)
# %%
df["predictions"] = model.predict(df)
df["sel"] = df["predictions"].apply(lambda x: 1 if random.uniform(0, 1) < x else 0) 
df_sel = df[df["sel"]==1]
# %%
selected_x_var_per= ['R_AGE','HHSIZE', 'WORKER',
                      "EDUC_1",'EDUC_2',
                      'income_cls_1', 'income_cls_2', 'income_cls_3', 'income_cls_4','income_cls_5',"URBRUR",
                     ]
df_good=df[(df['DELIV_GOOD']>=1)]
X=df_good[selected_x_var_per]
Y= df_good['DELIV_GOOD']
# df_good['DELIV_GOOD_week']=df_good['DELIV_GOOD'].apply(lambda x: x*7/30)
# Y=df_good['DELIV_GOOD_week']

# Find alpha for the model 
poisson_training_results = sm.GLM(Y, X, family=sm.families.Poisson()).fit()
df_train=pd.DataFrame(Y)
df_train['BB_LAMBDA'] = poisson_training_results.mu
df_train['AUX_OLS_DEP'] = df_train.apply(lambda x: ((x['DELIV_GOOD'] - x['BB_LAMBDA'])**2 - x['BB_LAMBDA']) / x['BB_LAMBDA'], axis=1)
ols_expr = """AUX_OLS_DEP ~ BB_LAMBDA - 1"""
aux_olsr_results = smf.ols(ols_expr, df_train).fit()
model=sm.GLM(Y, X,family=sm.families.NegativeBinomial(alpha=aux_olsr_results.params[0]),freq_weights=df_good['WTPERFIN']).fit()
model.summary()
filename = 'freq_good.sav'
joblib.dump(model, filename)
# with open('B2C_gen_model_estiation_results.txt', 'a') as f:
#     print ('************* Delivery Model ****************', file=f)
#     print('Summary report:', file=f)
#     print(result.summary(), file=f)
plt.figure(figsize = (8,6))
# plt.hist(Y, color ="blue", bins = Y.max())
df_good["DELIV_GOOD_prd"] = model.predict(X)
print(df_good["DELIV_GOOD_prd"].max(),df_good["DELIV_GOOD_prd"].min())
plt.hist(df_good["DELIV_GOOD_prd"], color ="blue", bins = int(Y.max()))

# %%
#############################
selected_x_var_per= ['R_AGE','HHSIZE','WORKER',
                      'DELIV_GOOD',"URBRUR",
                     'income_cls_1', 'income_cls_2', 'income_cls_3', 'income_cls_4','income_cls_5']

df_good=df[df['DELIV_GROC']>=1]
X=df_good[selected_x_var_per]
Y= df_good['DELIV_GROC']

# Find alpha for the model 
poisson_training_results = sm.GLM(Y, X, family=sm.families.Poisson()).fit()
df_train=pd.DataFrame(Y)
df_train['BB_LAMBDA'] = poisson_training_results.mu
df_train['AUX_OLS_DEP'] = df_train.apply(lambda x: ((x['DELIV_GROC'] - x['BB_LAMBDA'])**2 - x['BB_LAMBDA']) / x['BB_LAMBDA'], axis=1)
ols_expr = """AUX_OLS_DEP ~ BB_LAMBDA - 1"""
aux_olsr_results = smf.ols(ols_expr, df_train).fit()


model=sm.GLM(Y, X,family=sm.families.NegativeBinomial(alpha=aux_olsr_results.params[0]),freq_weights=df_good['WTPERFIN']).fit()

model.summary()
filename = 'freq_grc.sav'
joblib.dump(model, filename)
# with open('B2C_gen_model_estiation_results.txt', 'a') as f:
#     print ('************* Delivery Model ****************', file=f)
#     print('Summary report:', file=f)
#     print(result.summary(), file=f)
plt.figure(figsize = (8,6))

df_good["DELIV_GOOD_prd"] = model.predict(X)
print(df_good["DELIV_GOOD_prd"].max(),df_good["DELIV_GOOD_prd"].min())
plt.hist(df_good["DELIV_GOOD_prd"], color ="blue", bins = int(Y.max()))


# %%
################
selected_x_var_per= ['R_AGE','HHSIZE','WORKER','R_SEX_IMP',
                      'DELIV_GROC','URBRUR','income_cls_1', 'income_cls_2', 'income_cls_3', 'income_cls_4','income_cls_5',
                      "URBRUR"]
df_good=df[df['DELIV_FOOD']>=1]
X=df_good[selected_x_var_per]
Y= df_good['DELIV_FOOD']

poisson_training_results = sm.GLM(Y, X, family=sm.families.Poisson()).fit()
df_train=pd.DataFrame(Y)
df_train['BB_LAMBDA'] = poisson_training_results.mu
df_train['AUX_OLS_DEP'] = df_train.apply(lambda x: ((x['DELIV_FOOD'] - x['BB_LAMBDA'])**2 - x['BB_LAMBDA']) / x['BB_LAMBDA'], axis=1)
ols_expr = """AUX_OLS_DEP ~ BB_LAMBDA - 1"""
aux_olsr_results = smf.ols(ols_expr, df_train).fit()


model=sm.GLM(Y, X,family=sm.families.NegativeBinomial(alpha=aux_olsr_results.params[0]),freq_weights=df_good['WTPERFIN']).fit()

model.summary()
filename = 'freq_food.sav'
joblib.dump(model, filename)
# with open('B2C_gen_model_estiation_results.txt', 'a') as f:
#     print ('************* Delivery Model ****************', file=f)
#     print('Summary report:', file=f)
#     print(result.summary(), file=f)
plt.figure(figsize = (8,6))
# plt.hist(Y, color ="blue", bins = Y.max())
df_good["DELIV_GOOD_prd"] = model.predict(X)
print(df_good["DELIV_GOOD_prd"].max(),df_good["DELIV_GOOD_prd"].min())
plt.hist(df_good["DELIV_GOOD_prd"], color ="blue", bins = int(Y.max()))

####################################ATUS

df=pd.read_csv(args.fdir_input_nhts)
df['shopping']= df.apply(lambda x: 0 if x['choice_goods']+ x['choice_grocery']+ x['choice_food'] ==9 else 1, axis=1)

# %% 
######################
# Goods model 
#df_online_good= df[(df['choice_goods']!=3)].reset_index()
df_online_good= df[(df['shopping']==1)].reset_index()
sample_sz= df_online_good.TUFINLWGT.size
sum_wgt=df_online_good.TUFINLWGT.sum()    
df_online_good["TUFINLWGT"]=df_online_good["TUFINLWGT"].apply(lambda x: x*sample_sz/sum_wgt)

model = smf.glm("choice_instore_goods ~ online_goods_act+online_grocery_act+online_food_act+\
              R_RACE_0 + R_RACE_1 + R_RACE_2+ \
              income_cls_1+income_cls_2+income_cls_3+income_cls_4+income_cls_5+\
              R_AGE_C_0 +R_AGE_C_1+R_AGE_C_2+R_AGE_C_3+\
              R_SEX_IMP+HHSIZE+CHILD",
              family=sm.families.Binomial(),data=df_online_good,freq_weights=df_online_good['TUFINLWGT']).fit()

model.summary()
# %%
filename = 'instore_choice_goods.sav'
joblib.dump(model, filename)

df_online_good["predictions"] = model.predict(df_online_good)
df_online_good["sel"] = df_online_good["predictions"].apply(lambda x: 0 if x <0.5 else 1) 
df_sel = df_online_good[df_online_good["sel"]==1]
vars=['online_goods_act', 'online_grocery_act', 'online_food_act',
'R_RACE_0', 'R_RACE_1', 'R_RACE_2','R_RACE_3',
'income_cls_0', 'income_cls_1', 'income_cls_2','income_cls_3', 'income_cls_4','income_cls_5',
'R_AGE_C_0', 'R_AGE_C_1', 'R_AGE_C_2','R_AGE_C_3', 'R_AGE_C_4',
'R_SEX_IMP','HHSIZE','CHILD',"predictions"]
df_temp=df_online_good[vars]
df_temp.to_csv("../../../FRISM_input_output_SF/Sim_inputs/hh_pop/sfbay_2018/df_temp_atus.csv")

# %% 
######################
# food model 
df_online_good= df[(df['shopping']==1)].reset_index()
sample_sz= df_online_good.TUFINLWGT.size
sum_wgt=df_online_good.TUFINLWGT.sum()    
df_online_good["TUFINLWGT"]=df_online_good["TUFINLWGT"].apply(lambda x: x*sample_sz/sum_wgt)

model = smf.glm("choice_instore_food ~ online_goods_act+online_food_act+\
              \
              income_cls_1+income_cls_2+income_cls_3+income_cls_4+income_cls_5+\
              R_AGE_C_0 +R_AGE_C_1+R_AGE_C_2+R_AGE_C_3+\
              R_SEX_IMP+HHSIZE",
              family=sm.families.Binomial(),data=df_online_good,freq_weights=df_online_good['TUFINLWGT']).fit()


model.summary()
# %%
filename = 'instore_choice_food.sav'
joblib.dump(model, filename)
df_online_good["predictions"] = model.predict(df_online_good)
df_online_good["sel"] = df_online_good["predictions"].apply(lambda x: 0 if x <0.5 else 1) 
df_sel = df_online_good[df_online_good["sel"]==1]

# %% 
######################
# grocery model 
df_online_good= df[(df['shopping']==1)].reset_index()
sample_sz= df_online_good.TUFINLWGT.size
sum_wgt=df_online_good.TUFINLWGT.sum()    
df_online_good["TUFINLWGT"]=df_online_good["TUFINLWGT"].apply(lambda x: x*sample_sz/sum_wgt)

model = smf.glm("choice_instore_grocery ~ online_goods_act+online_food_act+online_grocery_act+\
              R_RACE_0 + R_RACE_1 + R_RACE_2+\
              income_cls_1+income_cls_2+income_cls_3+income_cls_4+income_cls_5+\
              R_AGE_C_0 +R_AGE_C_1+R_AGE_C_2+R_AGE_C_3+\
              R_SEX_IMP+HHSIZE",
              family=sm.families.Binomial(),data=df_online_good,freq_weights=df_online_good['TUFINLWGT']).fit()

model.summary()
# %%
filename = 'instore_choice_grc.sav'
joblib.dump(model, filename)
df_online_good["predictions"] = model.predict(df_online_good)
df_online_good["sel"] = df_online_good["predictions"].apply(lambda x: 0 if x <0.5 else 1) 
df_sel = df_online_good[df_online_good["sel"]==1]

# %%
