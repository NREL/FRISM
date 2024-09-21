
# %%
import pandas as pd
import numpy as np
from statsmodels.stats.weightstats import DescrStatsW

fdir_input= fdir_input= "../../../B2C_Data/ATUS/2022/"
atus_df= pd.read_csv(fdir_input+"atus_df_model_2022.csv")
fdir_input= "../../../B2C_Data/NHTS_22/"
nhts_per= pd.read_csv(fdir_input+"nhts_df_model_2022.csv")   

with open('Description of ATUS.txt', 'a') as f:
    for col in atus_df.columns:
        desc_df=DescrStatsW(atus_df[col], weights=atus_df.TUFINLWGT, ddof=1)
        print ('{}'.format(col), file=f)
        print ("{}".format(desc_df.mean), file=f)
        print ("{}".format(desc_df.std), file=f)
        print ("{}".format(atus_df[col].min()), file=f)
        print ("{}".format(atus_df[col].max()), file=f)
nhts_per.DELIV_FOOD=nhts_per.DELIV_FOOD.apply(lambda x:  0 if x<=0 else x)
nhts_per.DELIV_GOOD=nhts_per.DELIV_GOOD.apply(lambda x:  0 if x<=0 else x)
nhts_per.DELIV_GROC=nhts_per.DELIV_GROC.apply(lambda x:  0 if x<=0 else x)
nhts_per["adopt_food"]=nhts_per.DELIV_FOOD.apply(lambda x:  0 if x<=0 else 1)
nhts_per["adopt_good"]=nhts_per.DELIV_GOOD.apply(lambda x:  0 if x<=0 else 1)
nhts_per["adopt_grc"]=nhts_per.DELIV_GROC.apply(lambda x:  0 if x<=0 else 1)
with open('Description of NHTS.txt', 'a') as f:
    for col in nhts_per.columns:
        desc_df=DescrStatsW(nhts_per[col], weights=nhts_per.WTPERFIN, ddof=1)
        print ('{}'.format(col), file=f)
        print ("{}".format(desc_df.mean), file=f)
        print ("{}".format(desc_df.std), file=f)
        print ("{}".format(nhts_per[col].min()), file=f)
        print ("{}".format(nhts_per[col].max()), file=f)

# %%
