
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
              \
              EDUC_2+\
              R_SEX_IMP+HHSIZE+CHILD",
              family=sm.families.Binomial(),data=df_online_good,freq_weights=df_online_good['TUFINLWGT']).fit()

model.summary()

# %%
df_online_good["predictions"] = model.predict(df_online_good)
df_online_good["sel"] = df_online_good["predictions"].apply(lambda x: 0 if x <0.5 else 1) 
df_sel = df_online_good[df_online_good["sel"]==1]


# %% 
######################
# food model 
df_online_good= df[(df['choice_food']!=3)].reset_index()
df_online_good= df[(df['shopping']==1)].reset_index()
sample_sz= df_online_good.TUFINLWGT.size
sum_wgt=df_online_good.TUFINLWGT.sum()    
df_online_good["TUFINLWGT"]=df_online_good["TUFINLWGT"].apply(lambda x: x*sample_sz/sum_wgt)

model = smf.glm("choice_instore_food ~ online_food_act+\
              R_RACE_0 + R_RACE_1 + R_RACE_2+ \
              income_est+\
              HHSIZE+CHILD",
              family=sm.families.Binomial(),data=df_online_good,freq_weights=df_online_good['TUFINLWGT']).fit()

model.summary()

# %%
df_online_good["predictions"] = model.predict(df_online_good)
df_online_good["sel"] = df_online_good["predictions"].apply(lambda x: 0 if x <0.5 else 1) 
df_sel = df_online_good[df_online_good["sel"]==1]

# %% 
######################
# grocery model 
df_online_good= df[(df['choice_grocery']!=3)].reset_index()
df_online_good= df[(df['shopping']==1)].reset_index()
sample_sz= df_online_good.TUFINLWGT.size
sum_wgt=df_online_good.TUFINLWGT.sum()    
df_online_good["TUFINLWGT"]=df_online_good["TUFINLWGT"].apply(lambda x: x*sample_sz/sum_wgt)

model = smf.glm("choice_instore_grocery ~ online_goods_act+online_grocery_act+online_food_act+\
              AGE+ \
              income_est+\
              EDUC_0+EDUC_1+\
              R_SEX_IMP+CHILD",
              family=sm.families.Binomial(),data=df_online_good,freq_weights=df_online_good['TUFINLWGT']).fit()

model.summary()

# %%
df_online_good["predictions"] = model.predict(df_online_good)
df_online_good["sel"] = df_online_good["predictions"].apply(lambda x: 0 if x <0.5 else 1) 
df_sel = df_online_good[df_online_good["sel"]==1]







# %% 
######################
# Goods model 
df_online_good= df#[(df['choice_gen']!=3)].reset_index()
sample_sz= df_online_good.TUFINLWGT.size
sum_wgt=df_online_good.TUFINLWGT.sum()    
df_online_good["TUFINLWGT"]=df_online_good["TUFINLWGT"].apply(lambda x: x*sample_sz/sum_wgt)

model = smf.glm("choice_instore_gen ~ online_gen_act+\
              MSACAT+\
              income_est+ \
              AGE+\
              \
              R_SEX_IMP+CHILD ",
              family=sm.families.Binomial(),data=df_online_good,freq_weights=df_online_good['TUFINLWGT']).fit()

model.summary()

# %%
df_online_good["predictions"] = model.predict(df_online_good)
df_online_good["sel"] = df_online_good["predictions"].apply(lambda x: 0 if x <0.5 else 1) 
df_sel = df_online_good[df_online_good["sel"]==1]


# %% 
######################
# Grocery model 
df_online_good= df#[(df['choice_food']!=3)].reset_index()
sample_sz= df_online_good.TUFINLWGT.size
sum_wgt=df_online_good.TUFINLWGT.sum()    
df_online_good["TUFINLWGT"]=df_online_good["TUFINLWGT"].apply(lambda x: x*sample_sz/sum_wgt)

model = smf.glm("choice_instore_food ~online_food_act+\
              income_est+ \
              AGE+\
              CHILD+HHSIZE",
              family=sm.families.Binomial(),data=df_online_good,freq_weights=df_online_good['TUFINLWGT']).fit()

model.summary()

# %%
df_online_good["predictions"] = model.predict(df_online_good)
df_online_good["sel"] = df_online_good["predictions"].apply(lambda x: 0 if x <0.5 else 1) 
df_sel = df_online_good[df_online_good["sel"]==1]





# %% 
######################
# Goods model 
df_online_good= df[(df['choice_goods']!=3)].reset_index()
sample_sz= df_online_good.TUFINLWGT.size
sum_wgt=df_online_good.TUFINLWGT.sum()    
df_online_good["TUFINLWGT"]=df_online_good["TUFINLWGT"].apply(lambda x: x*sample_sz/sum_wgt)

model = smf.glm("choice_instore_goods ~ online_goods_act+online_grocery_act+\
              R_RACE_0 + R_RACE_1 + R_RACE_2+ \
              HHSIZE+ \
              R_AGE_IMP_1+R_AGE_IMP_2+\
              R_SEX_IMP ",
              family=sm.families.Binomial(),data=df_online_good,freq_weights=df_online_good['TUFINLWGT']).fit()

model.summary()

# %%
df_online_good["predictions"] = model.predict(df_online_good)
df_online_good["sel"] = df_online_good["predictions"].apply(lambda x: 0 if x <0.5 else 1) 
df_sel = df_online_good[df_online_good["sel"]==1]


# %% 
######################
# Grocery model 
df_online_good= df[(df['choice_food']!=3)].reset_index()
sample_sz= df_online_good.TUFINLWGT.size
sum_wgt=df_online_good.TUFINLWGT.sum()    
df_online_good["TUFINLWGT"]=df_online_good["TUFINLWGT"].apply(lambda x: x*sample_sz/sum_wgt)

model = smf.glm("choice_instore_food ~ online_goods_act+online_grocery_act+online_food_act+\
              R_AGE_IMP_1+R_AGE_IMP_2+R_AGE_IMP_0+\
              HHSIZE+CHILD",
              family=sm.families.Binomial(),data=df_online_good,freq_weights=df_online_good['TUFINLWGT']).fit()

model.summary()

# %%
df_online_good["predictions"] = model.predict(df_online_good)
df_online_good["sel"] = df_online_good["predictions"].apply(lambda x: 0 if x <0.5 else 1) 
df_sel = df_online_good[df_online_good["sel"]==1]














###########################
# %%
model = smf.mnlogit("choice_goods ~ \
              AGE+\
              EDUC_1+EDUC_2+ EDUC_3+\
              income_est+\
              HHSIZE+CHILD+R_SEX_IMP",data=df,freq_weights=df['TUFINLWGT']).fit()

model.summary()

# %%
predic_result=model.predict(df)
predic_result.to_csv(fdir_input+"results.csv")

# %%
# Goods model 
df_online_good= df[(df['choice_goods']!=3)].reset_index()
sample_sz= df_online_good.TUFINLWGT.size
sum_wgt=df_online_good.TUFINLWGT.sum()    
df_online_good["TUFINLWGT"]=df_online_good["TUFINLWGT"].apply(lambda x: x*sample_sz/sum_wgt)

model = smf.mnlogit("choice_goods ~ \
              R_AGE_IMP_1+R_AGE_IMP_2+R_AGE_IMP_3+R_AGE_IMP_4+\
              EDUC_1+EDUC_2+ EDUC_3+\
               income_cls_1+income_cls_2+income_cls_3+income_cls_4+income_cls_5+\
              HHSIZE+CHILD+R_SEX_IMP",data=df_online_good).fit()

model.summary()

# %%
# Goods model 
df_online_good= df[(df['choice_goods']!=3)].reset_index()
sample_sz= df_online_good.TUFINLWGT.size
sum_wgt=df_online_good.TUFINLWGT.sum()    
df_online_good["TUFINLWGT"]=df_online_good["TUFINLWGT"].apply(lambda x: x*sample_sz/sum_wgt)

model = smf.glm("choice_instore_goods ~ online_goods_act+\
              R_AGE_IMP_1+R_AGE_IMP_2+R_AGE_IMP_3+R_AGE_IMP_4+\
              EDUC_1+EDUC_2+ EDUC_3+\
              income_cls_1+income_cls_2+income_cls_3+income_cls_4+income_cls_5+\
              R_SEX_IMP",
              family=sm.families.Binomial(),data=df_online_good,freq_weights=df_online_good['TUFINLWGT']).fit()

model.summary()
# %%
df_online_good["predictions"] = model.predict(df_online_good)
df_online_good["sel"] = df_online_good["predictions"].apply(lambda x: 0 if x <0.5 else 1) 
df_sel = df_online_good[df_online_good["sel"]==1]


# %%
# Goods model 
df_online_good= df[df['choice_online_goods']==1]
model = smf.glm("choice_instore_goods ~ \
              AGE+\
              EDUC_1+EDUC_2+ EDUC_3+\
              income_cls_0+income_cls_1+income_cls_2+income_cls_3+income_cls_4+income_cls_5+\
              HHSIZE+CHILD+R_SEX_IMP",
              family=sm.families.Binomial(),data=df_online_good,freq_weights=df_online_good['TUFINLWGT']).fit()

model.summary()
# %%
df_online_good["predictions"] = model.predict(df_online_good)
df_online_good["sel"] = df_online_good["predictions"].apply(lambda x: 0 if x <0.5 else 1) 
df_sel = df_online_good[df_online_good["sel"]==1]


# %%
# Goods model 
df_online_good= df[df['choice_online_goods']==1]
model = smf.glm("choice_instore_goods ~ \
              R_AGE_IMP_0+R_AGE_IMP_1+R_AGE_IMP_2+R_AGE_IMP_3+R_AGE_IMP_4+\
              EDUC_0+EDUC_1+EDUC_2+ EDUC_3+\
              income_cls_0+income_cls_1+income_cls_2+income_cls_3+income_cls_4+income_cls_5+\
              HHSIZE+CHILD+R_SEX_IMP",
              family=sm.families.Binomial(),data=df_online_good,freq_weights=df_online_good['TUFINLWGT']).fit()

model.summary()
df_online_good["predictions"] = model.predict(df_online_good)
df_online_good["sel"] = df_online_good["predictions"].apply(lambda x: 0 if x <0.5 else 1) 
df_sel = df_online_good[df_online_good["sel"]==1]

# %%
# Goods model 
df_online_good= df[df['choice_online_goods']==1]
model = smf.glm("choice_instore_goods ~ \
              R_AGE_IMP_0+R_AGE_IMP_1+R_AGE_IMP_2+R_AGE_IMP_3+R_AGE_IMP_4+\
              EDUC_0+EDUC_1+EDUC_2+ EDUC_3+\
              income_cls_0+income_cls_1+income_cls_2+income_cls_3+income_cls_4+income_cls_5+\
              HHSIZE+CHILD+R_SEX_IMP",
              family=sm.families.Binomial(),data=df_online_good,freq_weights=df_online_good['TUFINLWGT']).fit()

model.summary()
df_online_good["predictions"] = model.predict(df_online_good)
df_online_good["sel"] = df_online_good["predictions"].apply(lambda x: 0 if x <0.5 else 1) 
df_sel = df_online_good[df_online_good["sel"]==1]
# %%
# Food model 
model = smf.glm("choice_instore_food ~ choice_online_goods+choice_online_food+\
              R_AGE_IMP_0+R_AGE_IMP_1+R_AGE_IMP_2+R_AGE_IMP_3+R_AGE_IMP_4+\
              EDUC_0+EDUC_1+EDUC_2+ EDUC_3+\
              income_cls_0+income_cls_1+income_cls_2+income_cls_3+income_cls_4+income_cls_5+\
              HHSIZE+R_SEX_IMP",
              family=sm.families.Binomial(),data=df, freq_weights=df['TUFINLWGT']).fit()

model.summary()
df["predictions"] = model.predict(df)
df["sel"] = df["predictions"].apply(lambda x: 0 if x <0.5 else 1) 
df_sel = df[df["sel"]==1]
# %%
# Grc model 
model = smf.glm("choice_instore_grocery ~ choice_online_goods +choice_online_grocery+\
              R_AGE_IMP_0+R_AGE_IMP_1+R_AGE_IMP_2+R_AGE_IMP_3+R_AGE_IMP_4+\
              EDUC_0+EDUC_1+EDUC_2+ EDUC_3+\
              income_cls_0+income_cls_1+income_cls_2+income_cls_3+income_cls_4+income_cls_5+\
              HHSIZE+R_SEX_IMP",
              family=sm.families.Binomial(),data=df, freq_weights=df['TUFINLWGT']).fit()

model.summary()
df["predictions"] = model.predict(df)
df["sel"] = df["predictions"].apply(lambda x: 0 if x <0.5 else 1) 
df_sel = df[df["sel"]==1]
# %%
fit = smf.glm("choice_instore_goods ~ choice_online_goods +choice_online_grocery+ choice_online_food+\
              R_AGE_IMP_0+R_AGE_IMP_1+R_AGE_IMP_2+R_AGE_IMP_3+\
              EDUC_1+EDUC_2+EDUC_3+\
              income_cls_1+income_cls_2+income_cls_3+income_cls_4+income_cls_5+\
              MSACAT + HHSIZE +CHILD+R_SEX_IMP",
              family=sm.families.Binomial(),data=df).fit()

fit.summary()

# %%
selected_x_var_per=["choice_online_goods", "choice_online_food", "choice_online_grocery",\
              "R_AGE_IMP_0","R_AGE_IMP_1","R_AGE_IMP_2","R_AGE_IMP_3",\
              "EDUC_1","EDUC_2","EDUC_3",\
              "income_cls_1","income_cls_2","income_cls_3","income_cls_4","income_cls_5",\
              "MSACAT" , "HHSIZE" ,"CHILD"]

X= df[selected_x_var_per]
Y= df['choice_instore_goods']

model = LogisticRegression(solver='newton-cg', multi_class='ovr')
model.fit(X, Y, sample_weight=df['TUFINLWGT'])
model.coef_
# %%
# Food model 
fit = smf.glm("choice_instore_food ~choice_online_goods +choice_online_grocery+ choice_online_food+\
              R_AGE_IMP_0+R_AGE_IMP_1+R_AGE_IMP_2+R_AGE_IMP_3+\
              EDUC_1+EDUC_2+EDUC_3+\
              income_cls_1+income_cls_2+income_cls_3+income_cls_4+income_cls_5+\
              MSACAT + HHSIZE +CHILD+R_SEX_IMP",
              family=sm.families.Binomial(),data=df, freq_weights=df['TUFINLWGT']).fit()

fit.summary()
# %%
selected_x_var_per=["choice_online_goods", "choice_online_food", "choice_online_grocery",\
              "R_AGE_IMP_0","R_AGE_IMP_1","R_AGE_IMP_2","R_AGE_IMP_3",\
              "EDUC_1","EDUC_2","EDUC_3",\
              "income_cls_1","income_cls_2","income_cls_3","income_cls_4","income_cls_5",\
              "MSACAT" , "HHSIZE" ,"CHILD"]

X= df[selected_x_var_per]
Y= df['choice_instore_goods']

model = LogisticRegression(solver='newton-cg', multi_class='ovr')
model.fit(X, Y, sample_weight=df['TUFINLWGT'])
model.coef_
# %%
# Grc model 
fit = smf.glm("choice_instore_grocery ~ choice_online_goods +choice_online_grocery+ choice_online_food+\
              R_AGE_IMP_0+R_AGE_IMP_1+R_AGE_IMP_2+R_AGE_IMP_3+\
              EDUC_1+EDUC_2+EDUC_3+\
              income_cls_1+income_cls_2+income_cls_3+income_cls_4+income_cls_5+\
              MSACAT + HHSIZE +CHILD+R_SEX_IMP",
              family=sm.families.Binomial(),data=df, freq_weights=df['TUFINLWGT']).fit()

fit.summary()
# %%
selected_x_var_per=["choice_online_goods", "choice_online_food", "choice_online_grocery",\
              "R_AGE_IMP_0","R_AGE_IMP_1","R_AGE_IMP_2","R_AGE_IMP_3",\
              "EDUC_1","EDUC_2","EDUC_3",\
              "income_cls_1","income_cls_2","income_cls_3","income_cls_4","income_cls_5",\
              "MSACAT" , "HHSIZE" ,"CHILD"]

X= df[selected_x_var_per]
Y= df['choice_instore_goods']

model = LogisticRegression(solver='newton-cg', multi_class='ovr')
model.fit(X, Y, sample_weight=df['TUFINLWGT'])
model.coef_
--