# %%
import pandas as pd
import numpy as np
import glob
import config
import geopandas as gpd
import sys
# %%
date ={'20200106':'1','20200107':'2','20200108':'3', '20200109':'4', '20200110':'5',
       '20200113':'1','20200114':'2','20200115':'3', '20200116':'4', '20200117':'5',
       '20200120':'1','20200121':'2','20200122':'3', '20200123':'4', '20200124':'5',
       '20200127':'1','20200128':'2','20200129':'3', '20200130':'4', '20200131':'5',
       '20200203':'1','20200204':'2','20200205':'3', '20200206':'4', '20200207':'5',
       '20200210':'1','20200211':'2','20200212':'3', '20200213':'4', '20200214':'5',
       '20200217':'1','20200218':'2','20200219':'3', '20200220':'4', '20200221':'5',
       '20200224':'1','20200225':'2','20200226':'3', '20200227':'4', '20200228':'5',
       '20200302':'1','20200303':'2','20200304':'3', '20200305':'4', '20200306':'5',
       '20200309':'1','20200310':'2','20200311':'3', '20200312':'4', '20200313':'5',
       '20200316':'1','20200317':'2','20200318':'3', '20200319':'4', '20200320':'5',
       '20200323':'1','20200324':'2','20200325':'3', '20200326':'4', '20200327':'5',
       '20200330':'1','20200331':'2','20200401':'3', '20200402':'4', '20200403':'5',
       '20200406':'1','20200407':'2','20200408':'3', '20200409':'4', '20200410':'5',
       '20200413':'1','20200414':'2','20200415':'3', '20200416':'4', '20200417':'5',
       '20200420':'1','20200421':'2','20200422':'3', '20200423':'4', '20200424':'5',
       '20200427':'1','20200428':'2','20200429':'3', '20200430':'4', '20200501':'5',
       '20200504':'1','20200505':'2','20200506':'3', '20200507':'4', '20200508':'5',
       '20200511':'1','20200512':'2','20200513':'3', '20200514':'4', '20200515':'5',
       '20200518':'1','20200519':'2','20200520':'3', '20200521':'4', '20200522':'5',
       '20200525':'1','20200526':'2','20200527':'3', '20200528':'4', '20200529':'5'
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
# %%
def create_dst_veh(cbg,file_dir, v_type, v_file):
    cbg_list=list(cbg.GEOID)
    df =pd.DataFrame(columns=['Ori','Dest','Trip','start_date','start_dow','start_hour'])
    for key,value in date.items():
        for i in range(0,24):
            file_nm2=file_dir+'inrix.od.%s.%02d0000.census.hourly.%s.csv.gz'% (key,i, v_file)
            try:
                #file_nm2 = glob.glob(file_nm+'*')[0]
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

# %%
v_type="MD"
file_dir='/Users/kjeong/KJ_NREL_Work/1_Work/1_2_SMART_2_0/Model_development/INRIX_data/Veh_2/Unziped/'
create_dst_veh(CBGzone_df,file_dir, v_type, "vehicle2")

v_type="HD"
file_dir='/Users/kjeong/KJ_NREL_Work/1_Work/1_2_SMART_2_0/Model_development/INRIX_data/Veh_3/Unziped/'
create_dst_veh(CBGzone_df,file_dir, v_type, "vehicle3") 



# # %%
# file_nm="/Users/kjeong/NREL/1_Work/1_2_SMART_2_0/Model_development/Results_from_HPC_at/start_dow=1/"
# file_nm=file_nm+"start_hour=09/"
# file_nm2 = glob.glob(file_nm+'*')[0]
# %%
file_nm2= "/Users/kjeong/KJ_NREL_Work/1_Work/1_2_SMART_2_0/Model_development/INRIX_data/Veh_2/inrix.od.20200101.census.hourly.vehicle2/inrix.od.20200101.150000.census.hourly.vehicle2.csv.gz"
df_temp= pd.read_csv(file_nm2, compression='gzip', header=None, sep=',', quotechar='"', error_bad_lines=False)
# %%
import zipfile

for key,value in date.items():
    path_to_zip_file= "/Users/kjeong/KJ_NREL_Work/1_Work/1_2_SMART_2_0/Model_development/INRIX_data/Veh_2/inrix.od.{}.census.hourly.vehicle2.zip".format(key)
    directory_to_extract_to = "/Users/kjeong/KJ_NREL_Work/1_Work/1_2_SMART_2_0/Model_development/INRIX_data/Veh_2/Unziped"
    with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
        zip_ref.extractall(directory_to_extract_to)
    path_to_zip_file= "/Users/kjeong/KJ_NREL_Work/1_Work/1_2_SMART_2_0/Model_development/INRIX_data/Veh_3/inrix.od.{}.census.hourly.vehicle3.zip".format(key)
    directory_to_extract_to = "/Users/kjeong/KJ_NREL_Work/1_Work/1_2_SMART_2_0/Model_development/INRIX_data/Veh_3/Unziped"
    with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
        zip_ref.extractall(directory_to_extract_to)

