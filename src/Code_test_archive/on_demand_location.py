# %%
# %%
fdir_in_out= "../../../FRISM_input_output_SF"
fdir_firms=fdir_in_out+'/Sim_inputs/Synth_firm_pop/'
firm_file='synthfirms_all_Sep.csv'
# firm and warehouse(for-hire carrier)
firm_file_xy=fdir_firms+"xy"+firm_file
if file_exists(firm_file_xy):
    firms=pd.read_csv(firm_file_xy, header=0, sep=',')
    if "BusID" in firms.columns:
        firms=firms.rename({'BusID':'SellerID'}, axis='columns')
    if "lat" in firms.columns:
        firms=firms.rename({'lat':'y', 'lon': 'x'}, axis='columns')
# %%
firms_group= firms.groupby(['Industry_NAICS6_Make'])['Industry_NAICS6_Make'].agg(num_firms='count').reset_index()
firms_group.to_csv(fdir_firms+"naics_in_firmfile.csv")
# %%
import overpy
api = overpy.Overpass()
# small_test = (37.779125,-122.295224,37.889793,-122.151232)
# full region = (37.221225, -123.115864, 38.469739, -121.496602)
# eating: ammenity= restaurant;bar;fast_food
# Grocery: shop=supermarket; wholesale
eating_result = api.query("node[amenity=restaurant](37.221225, -123.115864, 38.469739, -121.496602);out;")
#grocery_result = api.query("node[shop=supermarket](37.221225, -123.115864, 38.469739, -121.496602);out;")
# %%
#len(eating_result.nodes)

tag1 = pd.Series()
tag2 = pd.Series()
tag3 = pd.Series()
tag4 = pd.Series()
tag5 = pd.Series()

for i in range(len(eating_result.nodes)):
    tag1.at[i] = eating_result.nodes[i].id
    tag2.at[i] = eating_result.nodes[i].tags.get('amenity')
    tag3.at[i] = eating_result.nodes[i].tags.get('name')
    tag4.at[i] = eating_result.nodes[i].lat
    tag5.at[i] = eating_result.nodes[i].lon
    
df_eating_result = pd.concat([tag1, tag2,tag3, tag4,tag5], axis=1)
df_eating_result.columns = ['id', 'type', 'name', 'lat', 'lon']
# %%
api = overpy.Overpass()
grocery_result = api.query("node[shop=supermarket](37.221225, -123.115864, 38.469739, -121.496602);out;")
tag1 = pd.Series()
tag2 = pd.Series()
tag3 = pd.Series()
tag4 = pd.Series()
tag5 = pd.Series()

for i in range(len(grocery_result.nodes)):
    tag1.at[i] = grocery_result.nodes[i].id
    tag2.at[i] = grocery_result.nodes[i].tags.get('shop')
    tag3.at[i] = grocery_result.nodes[i].tags.get('name')
    tag4.at[i] = grocery_result.nodes[i].lat
    tag5.at[i] = grocery_result.nodes[i].lon
    
df_grocery_result = pd.concat([tag1, tag2,tag3, tag4,tag5], axis=1)
df_grocery_result.columns = ['id', 'type', 'name', 'lat', 'lon']
# %%
