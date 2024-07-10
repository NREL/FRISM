
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
fdir_input= "../../../B2C_Data/ATUS/2022/"

df=pd.read_csv(fdir_input+"atus_df_model_2022.csv")

selected_var=['choice_instore_goods', 'choice_online_goods',
       'choice_instore_grocery', 'choice_online_grocery',
       'choice_instore_food', 'choice_online_food',
                    'income_cls_0', 'income_cls_1','income_cls_2', 'income_cls_3', 'income_cls_4', 'income_cls_5', 
                    'EDUC_0', 'EDUC_1','EDUC_2', 'EDUC_3', 
                    'R_AGE_IMP_0', 'R_AGE_IMP_1', 'R_AGE_IMP_2','R_AGE_IMP_3', 'R_AGE_IMP_4', 
                    'MSACAT',
                    'HHSIZE','TUFINLWGT','CHILD',"R_SEX_IMP" ]


df = df[selected_var]
sample_sz= df.TUFINLWGT.size
sum_wgt=df.TUFINLWGT.sum()    
df["TUFINLWGT"]=df["TUFINLWGT"].apply(lambda x: x*sample_sz/sum_wgt)



# %%
# Goods model 
fit = smf.glm("choice_instore_goods ~ choice_online_goods+ choice_online_grocery+choice_online_food+\
              R_AGE_IMP_0+R_AGE_IMP_1+R_AGE_IMP_2+R_AGE_IMP_3+R_AGE_IMP_4+\
              EDUC_0+EDUC_1+EDUC_2+ EDUC_3+\
              income_cls_0+income_cls_1+income_cls_2+income_cls_3+income_cls_4+income_cls_5+\
              HHSIZE+CHILD+R_SEX_IMP",
              family=sm.families.Binomial(),data=df,freq_weights=df['TUFINLWGT']).fit()

fit.summary()

# %%
# Food model 
fit = smf.glm("choice_instore_food ~ choice_online_goods+choice_online_food+\
              R_AGE_IMP_0+R_AGE_IMP_1+R_AGE_IMP_2+R_AGE_IMP_3+R_AGE_IMP_4+\
              EDUC_0+EDUC_1+EDUC_2+ EDUC_3+\
              income_cls_0+income_cls_1+income_cls_2+income_cls_3+income_cls_4+income_cls_5+\
              HHSIZE+R_SEX_IMP",
              family=sm.families.Binomial(),data=df, freq_weights=df['TUFINLWGT']).fit()

fit.summary()

# %%
# Grc model 
fit = smf.glm("choice_instore_grocery ~ choice_online_goods +choice_online_grocery+\
              R_AGE_IMP_0+R_AGE_IMP_1+R_AGE_IMP_2+R_AGE_IMP_3+R_AGE_IMP_4+\
              EDUC_0+EDUC_1+EDUC_2+ EDUC_3+\
              income_cls_0+income_cls_1+income_cls_2+income_cls_3+income_cls_4+income_cls_5+\
              HHSIZE+R_SEX_IMP",
              family=sm.families.Binomial(),data=df, freq_weights=df['TUFINLWGT']).fit()

fit.summary()
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