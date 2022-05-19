# %%
import pandas as pd
import numpy as np
import glob
import config
import geopandas as gpd
import sys
# %%
date ={'2020-01-06':'1','2020-01-07':'2','2020-01-08':'3', '2020-01-09':'4', '2020-01-10':'5',
       '2020-01-13':'1','2020-01-14':'2','2020-01-15':'3', '2020-01-16':'4', '2020-01-17':'5',
       '2020-01-20':'1','2020-01-21':'2','2020-01-22':'3', '2020-01-23':'4', '2020-01-24':'5',
       '2020-01-27':'1','2020-01-28':'2','2020-01-29':'3', '2020-01-30':'4', '2020-01-31':'5',
       '2020-02-03':'1','2020-02-04':'2','2020-02-05':'3', '2020-02-06':'4', '2020-02-07':'5',
       '2020-02-10':'1','2020-02-11':'2','2020-02-12':'3', '2020-02-13':'4', '2020-02-14':'5',
       '2020-02-17':'1','2020-02-18':'2','2020-02-19':'3', '2020-02-20':'4', '2020-02-21':'5',
       '2020-02-24':'1','2020-02-25':'2','2020-02-26':'3', '2020-02-27':'4', '2020-02-28':'5',
       '2020-03-02':'1','2020-03-03':'2','2020-03-04':'3', '2020-03-05':'4', '2020-03-06':'5',
       '2020-03-09':'1','2020-03-10':'2','2020-03-11':'3', '2020-03-12':'4', '2020-03-13':'5',
       '2020-03-16':'1','2020-03-17':'2','2020-03-18':'3', '2020-03-19':'4', '2020-03-20':'5',
       '2020-03-23':'1','2020-03-24':'2','2020-03-25':'3', '2020-03-26':'4', '2020-03-27':'5',
       '2020-03-30':'1','2020-03-31':'2','2020-04-01':'3', '2020-04-02':'4', '2020-04-03':'5',
       '2020-04-06':'1','2020-04-07':'2','2020-04-08':'3', '2020-04-09':'4', '2020-04-10':'5',
       '2020-04-13':'1','2020-04-14':'2','2020-04-15':'3', '2020-04-16':'4', '2020-04-17':'5',
       '2020-04-20':'1','2020-04-21':'2','2020-04-22':'3', '2020-04-23':'4', '2020-04-24':'5',
       '2020-04-27':'1','2020-04-28':'2','2020-04-29':'3', '2020-04-30':'4', '2020-05-01':'5',
       '2020-05-04':'1','2020-05-05':'2','2020-05-06':'3', '2020-05-07':'4', '2020-05-08':'5',
       '2020-05-11':'1','2020-05-12':'2','2020-05-13':'3', '2020-05-14':'4', '2020-05-15':'5',
       '2020-05-18':'1','2020-05-19':'2','2020-05-20':'3', '2020-05-21':'4', '2020-05-22':'5',
       '2020-05-25':'1','2020-05-26':'2','2020-05-27':'3', '2020-05-28':'4', '2020-05-29':'5'
      }
# %%
study_region=config.study_region
fdir_geo= "../../../FRISM_input_output_{}/Sim_inputs/Geo_data/".format(study_region)
CBGzone_df = gpd.read_file(fdir_geo+config.CBG_file) # file include, GEOID(12digit), MESOZONE, area
#CBGzone_df=CBGzone_df[['GEOID','CBPZONE','MESOZONE','area']]
CBGzone_df["GEOID"]=CBGzone_df["GEOID"].astype(str)
## Add county id from GEOID
CBGzone_df["County"]=CBGzone_df["GEOID"].apply(lambda x: x[2:5] if len(x)>=12 else 0)
CBGzone_df["County"]=CBGzone_df["County"].astype(str).astype(int)
CBGzone_df["GEOID"]=CBGzone_df["GEOID"].astype(str).astype(int)
CBGzone_df=CBGzone_df[CBGzone_df["County"]!=0].reset_index()

def create_dst_veh(cbg,file_dir, v_type):
    cbg_list=list(cbg.GEOID)
    df =pd.DataFrame(columns=['Ori','Dest','Trip','start_date','start_dow','start_hour'])
    for key,value in date.items():
        for i in range(0,24):
            file_nm=file_dir+'start_date=%s/start_dow=%s/start_hour=%02d/' % (key, value,i)
            try:
                file_nm2 = glob.glob(file_nm+'*')[0]
                df_temp= pd.read_csv(file_nm2, compression='gzip', header=None, sep=',', quotechar='"', error_bad_lines=False)
                df_temp=df_temp.rename(columns={0:'Ori',1:'Dest',2:'Trip'})
                df_temp=df_temp[df_temp['Ori'].isin(cbg_list)]
                df_temp['start_date']=key
                df_temp['start_dow']=value
                df_temp['start_hour']=i
                df=df.append(df_temp)
            except:
                print ("no file")    
    temp_3=df.groupby(['start_hour'])['Trip'].sum().reset_index()
    dep_dist= pd.DataFrame()
    for cbg_id in cbg_list:
        try:
            temp = df[df.Ori == cbg_id]
            temp=temp.groupby(['start_hour'])['Trip'].sum().reset_index()
        except:
            temp = temp_3
        
        temp_2=pd.DataFrame(columns = ['cbg_id','start_hour','Trip_pdf'])
        temp_2.start_hour= np.arange(0,24)
        temp_2.cbg_id = cbg_id
        temp_2=temp_2.merge(temp, on='start_hour', how='left')
        temp_2.Trip = temp_2.Trip.fillna(0)
        temp_2.Trip_pdf = temp_2.Trip/np.sum(temp_2.Trip)
        dep_dist=pd.concat([dep_dist, temp_2],ignore_index=True) 
    save_dir="../../../FRISM_input_output_{}/Model_carrier_op/INRIX_processing/".format(study_region)     
    dep_dist.to_csv (save_dir+'depature_dist_by_cbg_{}.csv'.format(v_type), index = False, header=True)

v_type="MD"
file_dir='/projects/inrixdata/processed/nrel-csc-inrix-national-processed_20200723/od_pairs/census_block_group/hourly/vehicle_weight_class=2/'
create_dst_veh(CBGzone_df,file_dir, v_type)

v_type="HD"
file_dir='/projects/inrixdata/processed/nrel-csc-inrix-national-processed_20200723/od_pairs/census_block_group/hourly/vehicle_weight_class=3/'
create_dst_veh(CBGzone_df,file_dir, v_type) 



# # %%
# file_nm="/Users/kjeong/NREL/1_Work/1_2_SMART_2_0/Model_development/Results_from_HPC_at/start_dow=1/"
# file_nm=file_nm+"start_hour=09/"
# file_nm2 = glob.glob(file_nm+'*')[0]
