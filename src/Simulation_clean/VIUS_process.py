# %%
import pandas as pd

# %% 
f_dir= "../../../VIUS_Data/2021/"
df_vius=pd.read_csv(f_dir+'vius_2021_com_crosswalk_20240624.csv', header=0, sep=',')

# %%
sel_column= [
'TABWEIGHT',
'AVGWEIGHT',
'BTYPE',
'CABDAY',
'FUELTYPE',
'GVWR_CLASS',
'KINDOFBUS',
'RGROUP',	
'RO_0_50',	
'RO_101_200',	
'RO_201_500',	
'RO_51_100',	
'RO_GT500',
'VEH_CLASS_SynthFirm'
]
df_vius= df_vius[sel_column]

# %%
df_vius_sub= df_vius.dropna(subset=['RO_0_50',
'RO_51_100',
'RO_101_200',
'RO_201_500',
'RO_GT500']).reset_index(drop=True)
'''
'Other construction',
'Utilities (includes electric power, natural gas, steam supply, water supply, and sewage removal)',
'For-hire transportation (of goods or people)', 'Manufacturing',
'01', '09', 'Other business type',
'Construction - non-residential', 'Construction - residential',
'02', '05', '07', 'Retail trade',
'Information services (includes telephone and television)', '03',
'Vehicle leasing or rental (includes short-term rentals)',
'Other services, including advertising, real estate, nonvehicle leasing or rental, educational, health care, social assistance, finance, insurance, professional, scientific, or technical services',
'Fuel wholesale or distribution', 'Wholesale trade',
'Mining (includes quarrying, well operations, and beneficiating)',
'08', 'Not reported', 'Other transportation and warehousing', '04',
'Warehousing and storage', '06'
'''
def sctg_class (KINDOFBUS):
    sctg_1= ["05","06","07", "08", 'Mining (includes quarrying, well operations, and beneficiating)']
    sctg_2= ['Fuel wholesale or distribution']
    sctg_3= ["01"]
    sctg_4= ["09", 'Manufacturing', 'Retail trade', 'Information services (includes telephone and television)',
             'Wholesale trade', 'Warehousing and storage','Other transportation and warehousing' ]
    sctg_5= ['Other construction', 'Other business type', 'Construction - non-residential', 'Construction - residential',
             ]    
    if (KINDOFBUS in sctg_1) :
        sctg =1 # bulk
    elif (KINDOFBUS in sctg_2) :
        sctg =2 # fuel_fert
    elif (KINDOFBUS in sctg_3) :
        sctg =3 # interm_food
    elif (KINDOFBUS in sctg_4):
        sctg =4 # mfr_goods
    elif (KINDOFBUS in sctg_5) :
        sctg =5 # others
    else:
        sctg =0                                     
    return sctg

# %%
df_vius_sub["sctg"]= df_vius_sub.apply(lambda x: sctg_class(x['KINDOFBUS']), axis=1)

# %%
df_vius_sub=df_vius_sub[df_vius_sub['sctg'].isin([1,2,3,4,5])]
sel_column=['RO_0_50',
'RO_51_100',
'RO_101_200',
'RO_201_500',
'RO_GT500']
df_vius_sub['RO_0_50']=df_vius_sub.apply(lambda x: int(x['RO_0_50'])*x['TABWEIGHT'],axis=1 )
df_vius_sub['RO_51_100']=df_vius_sub.apply(lambda x: int(x['RO_51_100'])*x['TABWEIGHT'],axis=1 )
df_vius_sub['RO_101_200']=df_vius_sub.apply(lambda x: int(x['RO_101_200'])*x['TABWEIGHT'],axis=1 )
df_vius_sub['RO_201_500']=df_vius_sub.apply(lambda x: int(x['RO_201_500'])*x['TABWEIGHT'],axis=1 )
df_vius_sub['RO_GT500']=df_vius_sub.apply(lambda x: int(x['RO_GT500'])*x['TABWEIGHT'],axis=1 )
df_vius_group=df_vius_sub.groupby(['sctg', 'VEH_CLASS_SynthFirm'])[sel_column].agg('sum').reset_index()
df_vius_group.to_csv(f_dir+"vehicle_proportion_by_sctg_dist_raw.csv")

# %%
veh_class= ["HDT tractor",
"HDT vocational",
# "LDT vocational",
"MDT vocational"]

df_vius_group_dist=df_vius_group[df_vius_group['VEH_CLASS_SynthFirm'].isin(veh_class)].reset_index(drop=True)
sctg=[1,2,3,4,5]

for s in sctg:
    for d in sel_column: 
        g_sum=df_vius_group_dist[df_vius_group_dist["sctg"]==s][d].sum()
        for v in veh_class:
            val=df_vius_group_dist[(df_vius_group_dist["sctg"]==s) & (df_vius_group_dist["VEH_CLASS_SynthFirm"]==v)][d].values[0]
            df_vius_group_dist.iloc[df_vius_group_dist[(df_vius_group_dist["sctg"]==s) & (df_vius_group_dist["VEH_CLASS_SynthFirm"]==v)].index,df_vius_group_dist.columns.get_loc(d)]  =val/g_sum

df_vius_group_dist.to_csv(f_dir+"vehicle_proportion_by_sctg_dist.csv")

    
# %%
