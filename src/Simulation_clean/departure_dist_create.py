# %%
import pandas as pd
import numpy as np
import glob
import seaborn as sns
import matplotlib.pyplot as pp
import pyarrow
from scipy import interpolate

# %%

state_id=[18,20,31,35,40,49,56]

date ={
       '2020-01-20':'1','2020-01-21':'2','2020-01-22':'3', '2020-01-23':'4', '2020-01-24':'5',
       '2020-02-10':'1','2020-02-11':'2','2020-02-12':'3', '2020-02-13':'4', '2020-02-14':'5',
       '2020-03-09':'1','2020-03-10':'2','2020-03-11':'3', '2020-03-12':'4', '2020-03-13':'5',
       '2020-03-16':'1','2020-03-17':'2','2020-03-18':'3', '2020-03-19':'4', '2020-03-20':'5',
       '2020-03-23':'1','2020-03-24':'2','2020-03-25':'3', '2020-03-26':'4', '2020-03-27':'5',
       '2020-03-30':'1','2020-03-31':'2','2020-04-01':'3', '2020-04-02':'4', '2020-04-03':'5',
       '2020-05-25':'1','2020-05-26':'2','2020-05-27':'3', '2020-05-28':'4', '2020-05-29':'5'
      }

file_dir='/Users/kjeong/KJ_NREL_Work/1_Work/1_3_RMobility/INRIX/HD/'
# test for a single file 
key= '2020-01-20'
value= '1'
i=0

file_nm=file_dir+'start_date=%s/start_dow=%s/start_hour=%02d/' % (key, value,i)
file_nm2 = glob.glob(file_nm+'*')[0]
df_temp= pd.read_csv(file_nm2, compression='gzip', header=None, sep=',', quotechar='"')
## 

df =pd.DataFrame(columns=['Ori','Dest','Trip','start_date','start_dow','start_hour'])
for key,value in date.items():
    for i in range(0,24):
        file_nm=file_dir+'start_date=%s/start_dow=%s/start_hour=%02d/' % (key, value,i)
        file_nm2 = glob.glob(file_nm+'*')[0]
        df_temp= pd.read_csv(file_nm2, compression='gzip', header=None, sep=',', quotechar='"', error_bad_lines=False)
        df_temp=df_temp.rename(columns={0:'Ori',1:'Dest',2:'Trip'}) # first two digits is state FIPS code 

        # need to develop code to have departure time (hourly base) distribution:
        # 1) OD pair using "OD_pair_selected.csv": State-State 
        # 2) In case of lack of data for OD, apply Origin based distribution  
         
