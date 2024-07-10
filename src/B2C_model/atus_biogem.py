# %%
import pandas as pd
import biogeme.database as db
from biogeme.expressions import Variable
from biogeme import models
from biogeme.expressions import Beta
import biogeme.biogeme as bio
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
# %%
database = db.Database('atus', df)
# %%
CHOICE =Variable("choice_instore_goods")
ON_GOODS =Variable("choice_online_goods")
ON_FOOD =Variable("choice_online_food")
ON_GRC =Variable("choice_online_grocery")
IC_0 =Variable("income_cls_0")
IC_1 =Variable("income_cls_1")
IC_2 =Variable("income_cls_2")
IC_3 =Variable("income_cls_3")
IC_4 =Variable("income_cls_4")
IC_5 =Variable("income_cls_5")
ED_0 =Variable("EDUC_0")
ED_1 =Variable("EDUC_1")
ED_2 =Variable("EDUC_2")
ED_3 =Variable("EDUC_3")
AG_0 =Variable("R_AGE_IMP_0")
AG_1 =Variable("R_AGE_IMP_1")
AG_2 =Variable("R_AGE_IMP_2")
AG_3 =Variable("R_AGE_IMP_3")
AG_4 =Variable("R_AGE_IMP_4")
HSIZE =Variable("HHSIZE")
MSA =Variable("MSACAT")
CHILD=Variable("CHILD")
WT =Variable("TUFINLWGT")
SEX=Variable("R_SEX_IMP")

SEX_OG=database.DefineVariable('SEX_OG', SEX * (ON_GOODS == 1))
# %%
ASC         = Beta('ASC', 0, None, None, 0)
B_ON_GOODS  = Beta('B_ON_GOODS', 0, None, None, 0)
B_ON_FOOD     = Beta("B_ON_FOOD" , 0, None, None, 0)
B_ON_GRC      = Beta("B_ON_GRC"  , 0, None, None, 0)
B_IC_0        = Beta("B_IC_0"    , 0, None, None, 0)
B_IC_1        = Beta("B_IC_1"    , 0, None, None, 0)
B_IC_2        = Beta("B_IC_2"    , 0, None, None, 0)
B_IC_3        = Beta("B_IC_3"    , 0, None, None, 0)
B_IC_4        = Beta("B_IC_4"    , 0, None, None, 0)
B_IC_5        = Beta("B_IC_5"    , 0, None, None, 0)
B_ED_0        = Beta("B_ED_0"    , 0, None, None, 0)
B_ED_1        = Beta("B_ED_1"    , 0, None, None, 0)
B_ED_2        = Beta("B_ED_2"    , 0, None, None, 0)
B_ED_3        = Beta("B_ED_3"    , 0, None, None, 0)
B_AG_0        = Beta("B_AG_0"    , 0, None, None, 0)
B_AG_1        = Beta("B_AG_1"    , 0, None, None, 0)
B_AG_2        = Beta("B_AG_2"    , 0, None, None, 0)
B_AG_3        = Beta("B_AG_3"    , 0, None, None, 0)
B_AG_4        = Beta("B_AG_4"    , 0, None, None, 0)
B_HSIZE     = Beta('B_HSIZE', 0, None, None, 0)
B_MSA       = Beta('B_MSA', 0, None, None, 0)
B_CHILD      = Beta('B_CHILD', 0, None, None, 0)
B_SEX       = Beta('B_SEX', 0, None, None, 0)
B_SEX_OG    = Beta('B_SEX_OG', 0, None, None, 0)
# %%
# V0=0
# V1=ASC + B_ON_GOODS*ON_GOODS+B_ON_FOOD*ON_FOOD+B_ON_GRC*ON_GRC+\
#     B_IC_1*IC_1+B_IC_2*IC_2+B_IC_3*IC_3+B_IC_4*IC_4+B_IC_5*IC_5+\
#     B_ED_1*ED_1+B_ED_2*ED_2+B_ED_3*ED_3+\
#     B_AG_0*AG_0+B_AG_1*AG_1+B_AG_2*AG_2+B_AG_3*AG_3+\
#     B_HSIZE*HSIZE+B_MSA*MSA+B_CHILD*CHILD
V0=0
V1=ASC + B_ON_GOODS*ON_GOODS+B_SEX*SEX+ B_SEX_OG*SEX_OG
# %%
V = {0: V0, 1: V1}
av= {0:1, 1:1}
logprob = WT*models.loglogit(V, av, CHOICE)
the_biogeme = bio.BIOGEME(database, logprob)
the_biogeme.modelName = 'atuslogit'

results = the_biogeme.estimate()
print(results.short_summary())
pandas_results = results.getEstimatedParameters()
pandas_results
# %%
