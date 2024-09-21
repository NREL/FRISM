
# %%
import pandas as pd
import numpy as np
#%%
import joblib
from argparse import ArgumentParser
# library for models 
import statsmodels.api as sms
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
fdir_input= "../../../B2C_Data/ATUS/2022/"

df=pd.read_csv(fdir_input+"atus_df_model_2022.csv")
df['shopping']= df.apply(lambda x: 0 if x['choice_goods']+ x['choice_grocery']+ x['choice_food'] ==9 else 1, axis=1)
# selected_var=['choice_instore_goods', 'choice_online_goods',
#        'choice_instore_grocery', 'choice_online_grocery',
#        'choice_instore_food', 'choice_online_food',
#                     'income_cls_0', 'income_cls_1','income_cls_2', 'income_cls_3', 'income_cls_4', 'income_cls_5', 
#                     'EDUC_0', 'EDUC_1','EDUC_2', 'EDUC_3', 
#                     'R_AGE_IMP_0', 'R_AGE_IMP_1', 'R_AGE_IMP_2','R_AGE_IMP_3', 'R_AGE_IMP_4',
#                     'R_RACE_0', 'R_RACE_1','R_RACE_2','R_RACE_3',
#                     'MSACAT',
#                     'HHSIZE','TUFINLWGT','CHILD',"R_SEX_IMP",'choice_goods','choice_grocery','choice_food','income_est',"AGE",
#                     'online_goods_act',
#                     'CENSUS_R']

# df = df[selected_var]
# sample_sz= df.TUFINLWGT.size
# sum_wgt=df.TUFINLWGT.sum()    
# df["TUFINLWGT"]=df["TUFINLWGT"].apply(lambda x: x*sample_sz/sum_wgt)

'''
'TUCASEID', 'instore_goods_act', 'online_goods_act',
       'instore_grocery_act', 'online_grocery_act', 'instore_food_act',
       'online_food_act', 'instore_gen_act', 'online_gen_act',
       'choice_instore_goods', 'choice_online_goods', 'choice_instore_grocery',
       'choice_online_grocery', 'choice_instore_food', 'choice_online_food',
       'choice_instore_gen', 'choice_online_gen', 'TULINENO', 'TEERN',
       'TEERNWKP', 'TEHRUSLT', 'SCHTYP', 'TESCHFT', 'TESCHLVL', 'TRDTIND1',
       'TRDTOCC1', 'TRIMIND1', 'TRMJIND1', 'TRMJOCC1', 'TRNUMHOU', 'TUFINLWGT',
       'CENSUS_R', 'MSACAT', 'income_cls', 'HEHOUSUT', 'HETENURE', 'HRHTYPE',
       'HHSIZE', 'EDUC', 'PESCHFT', 'PESCHLVL', 'R_SEX_IMP', 'R_AGE_IMP',
       'R_RACE', 'WORKER', 'TRATUSR', 'PRNMCHLD', 'income_est', 'AGE', 'CHILD',
       'income_cls_0', 'income_cls_1', 'income_cls_2', 'income_cls_3',
       'income_cls_4', 'income_cls_5', 'EDUC_0', 'EDUC_1', 'EDUC_2',
       'R_AGE_IMP_0', 'R_AGE_IMP_1', 'R_AGE_IMP_2', 'R_AGE_IMP_3',
       'R_AGE_IMP_4', 'R_RACE_0', 'R_RACE_1', 'R_RACE_2', 'R_RACE_3',
       'CENSUS_R_1', 'CENSUS_R_2', 'CENSUS_R_3', 'CENSUS_R_4', 'choice_goods',
       'choice_grocery', 'choice_food', 'choice_gen', 'shopping'

       
R_AGE_IMP_0 +R_AGE_IMP_1+R_AGE_IMP_2+R_AGE_IMP_3
income_cls_1+income_cls_2+income_cls_3+income_cls_4+income_cls_5
'''

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
