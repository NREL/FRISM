# %%
import time
import googlemaps # pip install googlemaps
import pandas as pd # pip install pandas
# %%
def miles_to_meters(miles):
    try:
        return miles * 1_609.344
    except:
        return 0
        
API_KEY = "your key" # need to put API key 
map_client = googlemaps.Client(API_KEY)

# address = '333 Market St, San Francisco, CA'
# geocode = map_client.geocode(address=address)
# (lat, lng) = map(geocode[0]['geometry']['location'].get, ('lat', 'lng'))

cent_location=(30.262570541752208, -97.73793100519806)
#search_string = 'amazon locker'
#search_string = 'Grocery store'
search_string = 'phamacy'
distance = miles_to_meters(35)
business_list = []

response = map_client.places_nearby(
    location=cent_location,
    keyword=search_string,
    radius=distance
)   

business_list.extend(response.get('results'))
next_page_token = response.get('next_page_token')

while next_page_token:
    time.sleep(2)
    response = map_client.places_nearby(
        location=cent_location,
        keyword=search_string,
        radius=distance,
        page_token=next_page_token
    )   
    business_list.extend(response.get('results'))
    next_page_token = response.get('next_page_token')

df = pd.DataFrame(business_list)
print (search_string,df.shape[0])
# %%
df['lat']=0
df['lng']=0
for i in range(0,df.shape[0]):
    a=df["geometry"].iloc[i]
    df['lat'].iloc[i]=a['location']['lat']
    df['lng'].iloc[i]=a['location']['lng']
df= df[['name','lat','lng']]
#%%
df["GID"]=""
for i in range(0,df.shape[0]):
    df.loc[i,'GID'] = "A_LOC_{}".format(i)
df.to_csv('/Users/kjeong/NREL/1_Work/1_2_SMART_2_0/Model_development/FRISM_input_output_AT/Sim_inputs/{0}.csv'.format(search_string), index=False)
# %%
