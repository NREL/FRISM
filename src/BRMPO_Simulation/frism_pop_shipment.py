# %%
from re import A
import pandas as pd
import numpy as np
import geopandas as gpd
from argparse import ArgumentParser
import random
import os
from alive_progress import alive_bar
import time
from shapely.geometry import Point
from frism_utility_distributionchannel import random_points_in_polygon
import glob
# %%

def countyid_from_cbgid (cbgid):
    cbgid_str = str(int(cbgid))
    if (len(cbgid_str)==12):
        return int(cbgid_str[0:5])
    elif (len(cbgid_str)==11):
        return int(cbgid_str[1:4])
    else:
        return 0
class Network:
    """A class for the distribution channel network 
    zone_file: str, geojson file 'XXXX_freight.geojson' 
    od_distance_file: str, csv file "XXXX_od_dist.csv" 
    extnernal_zone_file: str, csv file "xyExternal_Zones_Mapping.csv" If it is None, this will be created
    state_id: int, state id 
    county_in_region: list, two digit county id in the study region 
    """
    
    def __init__(self, zone_file=None, od_distance_file=None, extnernal_zone_file=None,local_zone_file=None, local_external_zone_file=None, ondemand_location_file=None, state_id=None, county_in_region=None ):
        self.zone_file =zone_file
        self.od_distance_file=od_distance_file
        self.extnernal_zone_file=extnernal_zone_file
        self.state_id=state_id
        self.county_in_region=county_in_region
        self.ondemand_location_file=ondemand_location_file
        self.local_zone_file=local_zone_file
        self.local_external_zone_file=local_external_zone_file
        self.zone = None
        self.od_distance= None
        self.external_zone=None
        self.ex_zone_list =None
        self.ondemand_loc=None
        self.local_zone = pd.DataFrame()
        self.dic_exteranl_coordinate ={}
        if self.zone_file and os.path.exists(self.zone_file):
            self._load_zone_file(self.zone_file)
        else:
            print("Zonal data path not provided or invalid.")

        if self.od_distance_file and os.path.exists(self.od_distance_file):
            self._load_od_distance_file(self.od_distance_file)
        else:
            print("OD distance data path not provided or invalid.")

        if self.extnernal_zone_file is None:
            pass
        else :
            self._load_extnernal_zone_file(self.extnernal_zone_file) 
        
        if self.ondemand_location_file is None:
            pass
        else :
            self._load_ondemand_file(self.ondemand_location_file)
        
        if self.local_zone_file is None:
            pass
        else :
            self._local_zone_file(self.local_zone_file)
        
        if self.local_external_zone_file is None:
            pass
        else :
            self._local_external_zone_file(self.local_external_zone_file)
                                  
    def _load_zone_file(self, file_path):
        # Read file 
        self.zone = gpd.read_file(file_path) 
        self.zone= self.zone.to_crs({'proj': 'cea'})
        self.zone["area"]=self.zone['geometry'].area/(10**6)
        ## Add county id from GEOID
        self.zone["County"]=self.zone["GEOID"].apply(lambda x: countyid_from_cbgid (x))
        self.zone= self.zone.to_crs('EPSG:4269')

    def _load_od_distance_file(self, file_path):
        # Read file
        try: 
            self.od_distance=pd.read_csv(file_path, header=0, sep=',')
        except:
            self.od_distance=pd.read_csv(file_path,compression="zip", header=0, sep=',')    
        # Convert column name to the format
        self.od_distance.columns=['Origin','Destination','dist']

    def _load_extnernal_zone_file(self, file_path):
        if os.path.exists(file_path):
            self.external_zone=pd.read_csv(file_path, header=0, sep=',')
        else:
            print ("**** Generating x_y to ex_zone files")
            self.external_zone=self.zone[~self.zone["County"].isin(self.county_in_region)][['MESOZONE','geometry']].reset_index(drop=True)
            self.external_zone["BoundaryZONE"]=0
            in_zones= self.zone[self.zone["County"].isin(self.county_in_region)].reset_index(drop=True)
            for index, row in self.external_zone.iterrows():
                D = 999999
                Id = None 
                p = row['geometry'].centroid
                for i,z in enumerate(in_zones['geometry']):
                    distance = p.distance(z)
                    ID = in_zones.iloc[i]['MESOZONE']
                    if distance <= D:
                        D = distance
                        Id = ID
                self.external_zone.at[index, "BoundaryZONE"] =Id
            temp_ex_zone=self.external_zone.drop_duplicates(subset=['BoundaryZONE'])
            temp_ex_zone=temp_ex_zone.reset_index()
            temp_ex_zone['x']=0
            temp_ex_zone['y']=0
            with alive_bar(temp_ex_zone.shape[0], force_tty=True) as bar:
                for i in range(0,temp_ex_zone.shape[0]):
                    [x,y]=random_points_in_polygon(self.zone.geometry[self.zone["MESOZONE"]==temp_ex_zone.loc[i,"BoundaryZONE"]])
                    temp_ex_zone.loc[i,'x']=x
                    temp_ex_zone.loc[i,'y']=y
                    bar()  
            self.external_zone=self.external_zone.merge(temp_ex_zone[["BoundaryZONE", "x", "y"]], on="BoundaryZONE", how='left')
            self.external_zone=self.external_zone.drop('geometry', axis=1)
            self.external_zone.to_csv(file_path, index = False, header=True)
        self.ex_zone_list = list(self.external_zone["MESOZONE"].unique()) 
    
    def _load_ondemand_file(self, file_path):
        # Read file 
        self.ondemand_loc = gpd.read_file(file_path) 
        self.ondemand_loc= self.ondemand_loc.to_crs(4269)
        self.ondemand_loc=self.ondemand_loc.sjoin(self.zone[['GEOID','MESOZONE','County',"geometry"]], how="inner",  predicate='intersects')

    def _local_zone_file(self, file_path):
        # Read file 
        self.local_zone = gpd.read_file(file_path) 
        self.local_zone= self.local_zone.to_crs(4269)
        self.local_zone=self.local_zone[['taz',"geometry"]]
    def _local_external_zone_file(self, file_path):
        in_zones = gpd.read_file(file_path) 
        in_zones= in_zones.to_crs(4269) 
        self.dic_exteranl_coordinate={}
        for _, row in in_zones.iterrows():
            self.dic_exteranl_coordinate[int(row.taz)] = (row.geometry.x, row.geometry.y)

class Firms:
    """
    * A class for the firms: Shipper frims and leasing firms used in B2B shipment *
    firm_file: str, csv file 'synthetic_firms_with_fleet_mc_adjusted.csv' 
    port_file: str, csv file "port_location_in_region.csv" 
    leasing_file: str, csv file "synthetic_leasing_company.csv"
    
    """
    def __init__(self, firm_file=None, port_file=None, leasing_file=None, carrier_file=None, state_id=None):
        self.firm_file =firm_file
        self.port_file=port_file
        self.leasing_file=leasing_file
        self.carrier_file = carrier_file
        self.state_id = state_id
        self.firms = pd.DataFrame()
        self.ports=pd.DataFrame()
        self.leasings= pd.DataFrame()
        self.leasings_agg= pd.DataFrame()
        self.carriers = pd.DataFrame()

        if self.firm_file and os.path.exists(self.firm_file):
            self._load_firm_file(self.firm_file)
        else:
            print("frim data path not provided or invalid.")

        if self.port_file and os.path.exists(self.port_file):
            self._load_port_file(self.port_file)
        else:
            print("port data path not provided or invalid.")

        if self.leasing_file and os.path.exists(self.leasing_file):
            self._load_leasing_file(self.leasing_file) 
        else :
            print("leasing firm data path not provided or invalid.")
        if self.carrier_file and os.path.exists(self.carrier_file):
            self._load_carrier_file(self.carrier_file) 
        else :
            print("carrier firm data path not provided or invalid.")    
        self.firms=pd.concat([self.firms, self.ports, self.leasings, self.carriers], ignore_index=True).reset_index(drop=True)
        self.firms["County"]=self.firms["MESOZONE"].apply(lambda x: countyid_from_cbgid (x))
        # delete     
        del self.ports, self.leasings, self.carriers      
    def _load_firm_file(self, file_path):
        # Read file 
        """
            CBPZONE                             int64
            FAFZONE                             int64
            esizecat                            int64
            Industry_NAICS6_Make               object
            Commodity_SCTG                      int64
            Emp                               float64
            BusID                               int64
            MESOZONE                            int64
            lat                               float64
            lon                               float64
            ParcelID                          float64
            TAZ                               float64
            state_abbr                         object
            fleet_id                          float64
            EV_powertrain (if any)             object
            Diesel Class 1&2A Vocational      float64
            Diesel Class 2B&3 Vocational      float64
            Diesel Class 4-6 Vocational       float64
            Diesel Class 7&8 Tractor          float64
            Diesel Class 7&8 Vocational       float64
            Gasoline Class 1&2A Vocational    float64
            Gasoline Class 2B&3 Vocational    float64
            Gasoline Class 4-6 Vocational     float64
            Electric Class 7&8 Tractor        float64
            Electric Class 7&8 Vocational     float64
            Electric Class 1&2A Vocational    float64
            Electric Class 2B&3 Vocational    float64
            Electric Class 4-6 Vocational     float64
            n_trucks                          float64
        """
        self.firms=pd.read_csv(file_path, header=0, sep=',')
        self.firms =self.firms[["BusID", "MESOZONE","lat"                            
                                , "lon"                            
                                # , "ParcelID"                       
                                # , "TAZ"                            
                                , "state_abbr"                     
                                , "fleet_id"                       
                                , "EV_powertrain (if any)"        
                                , "Diesel Class 1&2A Vocational"  
                                , "Diesel Class 2B&3 Vocational"   
                                , "Diesel Class 4-6 Vocational"    
                                , "Diesel Class 7&8 Tractor"       
                                , "Diesel Class 7&8 Vocational"    
                                , "Gasoline Class 1&2A Vocational" 
                                , "Gasoline Class 2B&3 Vocational" 
                                , "Gasoline Class 4-6 Vocational"  
                                , "Electric Class 7&8 Tractor"     
                                , "Electric Class 7&8 Vocational"  
                                , "Electric Class 1&2A Vocational" 
                                , "Electric Class 2B&3 Vocational" 
                                , "Electric Class 4-6 Vocational"  
                                , 'n_trucks']]
        if "BusID" in self.firms.columns:
            self.firms=self.firms.rename({'BusID':'SellerID'}, axis='columns')
        if "lat" in self.firms.columns:
            self.firms=self.firms.rename({'lat':'y', 'lon': 'x'}, axis='columns')
        if "fleet_id" in self.firms.columns:
            self.firms["fleet_id"] = self.firms["fleet_id"].apply(lambda x: 1 if x ==0 else x)
            self.firms["SellerID"] = self.firms.apply(lambda x: str(int(x["SellerID"])) + "_" + str(int(x["fleet_id"])), axis=1)
        if "state_abbr" in self.firms.columns:
            self.firms=self.firms.rename({'state_abbr':'st'}, axis='columns')
        #self.firms["County"]=self.firms["MESOZONE"].apply(lambda x: countyid_from_cbgid (self.state_id, x))       

    def _load_port_file(self, file_path):
        # Read file
        """
        NAME                  object
        STATE                 object
        PORTID                object
        TYPE                  object
        Export Port Code       int64
        CBP Port Location     object
        is_airport             int64
        Vessel                object
        Air                   object
        Rail                  object
        Road                  object
        Fixed                 object
        FAF                    int64
        GEOID                  int64
        FAFID                  int64
        MESOZONE               int64
        CBPZONE                int64
        lat                  float64
        lon                  float64
        """
        self.ports=gpd.read_file(file_path)
        self.ports["lat"]=self.ports["lat"].astype(float)
        self.ports["lat"]=self.ports["lat"].astype(float)
        self.ports["MESOZONE"]=self.ports["GEOID"]
        self.ports=self.ports[["PORTID","TYPE","MESOZONE", "lat","lon"]]
        self.ports=self.ports.rename({"PORTID": "SellerID" ,
                                      "TYPE":"Industry_NAICS6_Make",
                                      "MESOZONE": "MESOZONE" ,
                                      "lat": "y",
                                      "lon": "x"}, axis='columns')

    def _load_leasing_file(self, file_path):
        self.leasings=pd.read_csv(file_path, header=0, sep=',')
        self.leasings =self.leasings[["BusID", "MESOZONE","lat"                            
                        , "lon"                            
                        # , "ParcelID"                       
                        # , "TAZ"                            
                        , "state_abbr"                     
                        , "fleet_id"                       
                        , "EV_powertrain (if any)"        
                        , "Diesel Class 1&2A Vocational"  
                        , "Diesel Class 2B&3 Vocational"   
                        , "Diesel Class 4-6 Vocational"    
                        , "Diesel Class 7&8 Tractor"       
                        , "Diesel Class 7&8 Vocational"    
                        , "Gasoline Class 1&2A Vocational" 
                        , "Gasoline Class 2B&3 Vocational" 
                        , "Gasoline Class 4-6 Vocational"  
                        , "Electric Class 7&8 Tractor"     
                        , "Electric Class 7&8 Vocational"  
                        , "Electric Class 1&2A Vocational" 
                        , "Electric Class 2B&3 Vocational" 
                        , "Electric Class 4-6 Vocational"  
                        , 'n_trucks']]
        if "BusID" in self.leasings.columns:
            self.leasings=self.leasings.rename({'BusID':'SellerID'}, axis='columns')
        if "lat" in self.leasings.columns:
            self.leasings=self.leasings.rename({'lat':'y', 'lon': 'x'}, axis='columns')
        if "fleet_id" in self.leasings.columns:
            self.leasings["SellerID"] = self.leasings.apply(lambda x: str(int(x["SellerID"])) + "_" + str(int(x["fleet_id"])), axis=1)
        if "state_abbr" in self.leasings.columns:
            self.leasings=self.leasings.rename({'state_abbr':'st'}, axis='columns')

        leasings_D= self.leasings.groupby(['st']).agg(ld1=("Diesel Class 1&2A Vocational",'sum'),
                                                 ld3=("Diesel Class 2B&3 Vocational",'sum'),
                                                 mdv=("Diesel Class 4-6 Vocational",'sum'),
                                                hdv=("Diesel Class 7&8 Tractor",'sum'),
                                                hdt=("Diesel Class 7&8 Vocational",'sum') 
                                                    ).reset_index()
        leasings_D["powertrain"]="Diesel"
        leasings_G= self.leasings.groupby(['st']).agg(ld1=("Gasoline Class 1&2A Vocational",'sum'),
                                                 ld3=("Gasoline Class 2B&3 Vocational",'sum'),
                                                 md=("Gasoline Class 4-6 Vocational",'sum') 
                                                    ).reset_index()
        leasings_G["powertrain"]="Gasoline"
        leasings_G["hdv"]=0
        leasings_G["hdt"]=0                                              
        leasings_E= self.leasings.groupby(['st', 'EV_powertrain (if any)']).agg(ld1=("Electric Class 1&2A Vocational",'sum'),
                                                 ld3=("Electric Class 2B&3 Vocational",'sum'),
                                                 mdv=("Electric Class 4-6 Vocational",'sum'),
                                                hdv=("Electric Class 7&8 Tractor",'sum'),
                                                hdt=("Electric Class 7&8 Vocational",'sum')
                                                    ).reset_index()
        leasings_E=leasings_E.rename({'EV_powertrain (if any)':'powertrain'}, axis='columns')
        
        self.leasings_agg= pd.concat([leasings_D,leasings_G,leasings_E], ignore_index=True).reset_index(drop=True)              
    def _load_carrier_file(self, file_path):
        self.carriers=pd.read_csv(file_path, header=0, sep=',')
        self.carriers =self.carriers[["BusID", "MESOZONE","lat"                            
                                , "lon"                            
                                # , "ParcelID"                       
                                # , "TAZ"                            
                                , "state_abbr"                     
                                , "fleet_id"                       
                                , "EV_powertrain (if any)"        
                                , "Diesel Class 1&2A Vocational"  
                                , "Diesel Class 2B&3 Vocational"   
                                , "Diesel Class 4-6 Vocational"    
                                , "Diesel Class 7&8 Tractor"       
                                , "Diesel Class 7&8 Vocational"    
                                , "Gasoline Class 1&2A Vocational" 
                                , "Gasoline Class 2B&3 Vocational" 
                                , "Gasoline Class 4-6 Vocational"  
                                , "Electric Class 7&8 Tractor"     
                                , "Electric Class 7&8 Vocational"  
                                , "Electric Class 1&2A Vocational" 
                                , "Electric Class 2B&3 Vocational" 
                                , "Electric Class 4-6 Vocational"  
                                , 'n_trucks']]
        if "BusID" in self.carriers.columns:
            self.carriers=self.carriers.rename({'BusID':'SellerID'}, axis='columns')
        if "lat" in self.carriers.columns:
            self.carriers=self.carriers.rename({'lat':'y', 'lon': 'x'}, axis='columns')
        if "fleet_id" in self.carriers.columns:
            self.carriers["fleet_id"] = self.carriers["fleet_id"].apply(lambda x: 1 if x ==0 else x)
            self.carriers["SellerID"] = self.carriers.apply(lambda x: str(int(x["SellerID"])) + "_" + str(int(x["fleet_id"])), axis=1)
        if "state_abbr" in self.carriers.columns:
            self.carriers=self.carriers.rename({'state_abbr':'st'}, axis='columns')

class Carriers:
    """
    * A class for the carier: Generate B2B and B2C seperately *
    carrier_file: str, csv file 'synthetic_carriers.csv' 
    shipment_type: str "B2B or "B2C"
    state_id: int, state id 
    county_in_region: list, two digit county id in the study region 
    dic_veh: dictionry that include vehicle type and capacity 
    """
    def __init__(self, carrier_file=None, shipment_type=None, state_id=None, county_in_region=None, dic_veh=None):
        self.carrier_file =carrier_file
        self.shipment_type=shipment_type
        self.state_id=state_id
        self.county_in_region=county_in_region
        self.dic_veh=dic_veh
        self.carrier = pd.DataFrame()

        if self.carrier_file and os.path.exists(self.carrier_file):
            self._load_carrier_file(self.carrier_file, self.shipment_type)
        else:
            print("frim data path not provided or invalid.")

    def _load_carrier_file(self, file_path, shipment_type):
        warehouses=pd.read_csv(file_path, header=0, sep=',')
        warehouses=warehouses.rename({'lat':'y', 'lon': 'x','state_abbr':'st'}, axis='columns')
        warehouses["BusID"] = warehouses.apply(lambda x: str(int(x["BusID"])) + "_" + str(int(x["fleet_id"])), axis=1)
        warehouses["County"]=warehouses["MESOZONE"].apply(lambda x: countyid_from_cbgid (x))
        if shipment_type == 'B2C':
            self.carrier=warehouses[(warehouses['Industry_NAICS6_Make']==492000) & (warehouses['County'].isin(self.county_in_region))].reset_index(drop=True)
        elif shipment_type == 'B2B':    
            self.carrier=warehouses[warehouses['Industry_NAICS6_Make']==484000].reset_index(drop=True)
        for veh_type in self.dic_veh.keys():
            selected_columns=[col for col in self.carrier.columns if self.dic_veh[veh_type]["synthfirm_name"] in col ]
            self.carrier[veh_type+"_capacity"]=self.carrier[selected_columns].sum(axis=1)
            if shipment_type == 'B2C':
                self.carrier[veh_type+"_numshipment"]=self.carrier[selected_columns].sum(axis=1) * 15
            elif shipment_type == 'B2B':
                self.carrier[veh_type+"_numshipment"]=self.carrier[selected_columns].sum(axis=1) * 8                 

class DailyShipment:
    def __init__(self, shipment_file_path=None, annual_to_day_factor=None, sample_ratio=None, sel_county= None, state_id=None, county_in_region=None, international_flag=None):
        self.shipment_file_path =shipment_file_path # fdir+sub_fdir sub_fdir="{}_{}/".format(year,scenario)
        self.annual_to_day_factor=annual_to_day_factor
        self.sample_ratio=sample_ratio
        self.sel_county=sel_county
        self.state_id=state_id
        self.county_in_region=county_in_region
        self.international_flag=international_flag # Y or N
        self.shipments_record=pd.DataFrame()
        self.sample_result ={"domestic": {"daily_tonnage": 0, "daily_shipments": 0, "sample_tonnage":0, "sample_shipments": 0},
                             "import": {"daily_tonnage": 0, "daily_shipments": 0, "sample_tonnage":0, "sample_shipments": 0},
                             "export": {"daily_tonnage": 0, "daily_shipments": 0, "sample_tonnage":0, "sample_shipments": 0}}
        if self.shipment_file_path:
            self._process_domestic_flow(self.shipment_file_path)            
        else:
            print("file path not provided or invalid.")
        if international_flag == "Y":
            self._process_international_flow(self.shipment_file_path)  
        self._process_commodity_group(self.shipment_file_path)     
    def _process_domestic_flow(self, file_path):
        B2BF=pd.DataFrame()
        ship_category="domestic"
        agent= "SellerID"
        list_file= glob.glob(file_path+'*.csv') + glob.glob(file_path+'*.csv.zip')
        for filename in list_file:
            try: 
                temp= pd.read_csv(filename)
            except:
                temp= pd.read_csv(filename, compression="zip" )    
            if temp.shape[0] >0:
                temp["SellerID"]=temp["SellerID"].astype("int") 
                if "fleet_id" in temp.columns:
                    temp["fleet_id"]=temp["fleet_id"].astype("int") 
                    temp["SellerID"] = temp.apply(lambda x: str(int(x["SellerID"])) + "_" + str(int(x["fleet_id"])), axis=1)
                    temp = temp.drop("fleet_id", axis=1)
                else:
                    temp["SellerID"] = temp.apply(lambda x: str(int(x["SellerID"])) + "_1", axis=1)
                temp["BuyerID"] = temp.apply(lambda x: str(int(x["BuyerID"])) + "_1", axis=1)        
                temp=temp.astype({'BuyerID': 'string',
                "BuyerZone":"int64",
                "BuyerNAICS":"string",
                "SellerID":"string",
                "SellerZone":"int64",
                "SellerNAICS":"string",
                "TruckLoad": "float64",
                "Commodity_SCTG": "float64",
                "SCTG_Group": "int64",
                "shipment_id":"int64",
                "orig_FAFID":"int64",
                "dest_FAFID":"int64",
                "mode_choice":"string",
                "probability":"float64",
                "Distance":"float64",
                "Travel_time":"float64" 
                })
                # Add SellerCounty and BuyerCounty for filering 
                temp["SellerCounty"]=temp["SellerZone"].apply(lambda x: countyid_from_cbgid (x))
                temp["BuyerCounty"]=temp["BuyerZone"].apply(lambda x: countyid_from_cbgid (x))
                if self.sel_county:
                    county_wo_sel= [i for i in self.county_in_region if i != self.sel_county]
                    temp= temp[(temp['BuyerCounty']==self.sel_county) | (temp['SellerCounty']==self.sel_county)].reset_index(drop=True)
                    temp= temp[~temp['SellerCounty'].isin(county_wo_sel)].reset_index(drop=True) 
                temp["D_truckload"]=0
                temp["D_selection"]=1
                temp["D_selection"]=temp["D_selection"].apply(lambda x: self._annual_to_daily_shipment_domestic(self.annual_to_day_factor) *x )
                temp=temp.query('D_selection ==1')
                temp["ship_category"]=ship_category
                # if sample_ratio <100: 
                #     temp=sampling_shipper(temp, sample_ratio, bin_size)
                # temp=temp.sample(frac=sample_ratio/100)
                B2BF=pd.concat([B2BF,temp],ignore_index=True) # Daily all population
        # sampling approach
        # calculate total tonnage ratio and shipment ratio to adjust the sample from Tour generation
        self.sample_result[ship_category]["daily_tonnage"]= B2BF['TruckLoad'].sum()
        self.sample_result[ship_category]["daily_shipments"]= B2BF.shape[0]
    
        df_group = B2BF.groupby([agent])['SellerID'].count().reset_index(name='num_shipment')
        list_agent_sample =self._sampling_shipper(df_group, self.sample_ratio, ship_category)
        self.shipments_record=B2BF[B2BF[agent].isin(list_agent_sample)].reset_index(drop=True)
        self.sample_result[ship_category]["sample_tonnage"]= self.shipments_record['TruckLoad'].sum()
        self.sample_result[ship_category]["sample_shipments"]= self.shipments_record.shape[0]  ## need to save this in the main function
        self.shipments_record['TruckLoad']=self.shipments_record['TruckLoad']*2000
        self.shipments_record['D_truckload']=self.shipments_record['TruckLoad']
        self.shipments_record["SellerID_Org"] = self.shipments_record["SellerID"]
        self.shipments_record["BuyerID_Org"] = self.shipments_record["BuyerID"]

    def _process_international_flow(self, file_path):
        file_path_port_loc =file_path+'int_port/'
        port_loc= pd.read_csv(glob.glob(file_path_port_loc+'*.csv')[0])
        dic_port={}
        n=0
        for port_id in port_loc["PORTID"].unique():
            dic_port[port_id]="P{}".format(n)
            n +=1
        #    
        file_path_port_demand =file_path+'int_flow/'
        B2BF_international =pd.DataFrame()
        for filename in glob.glob(file_path_port_demand+'*.csv'):
            temp= pd.read_csv(filename)
            if "import" in filename:
                ship_category="import"
                agent= "BuyerID"
                temp["BuyerID"]=temp["BuyerID"].apply(lambda x: str(int(x))+ "_1")
                temp=temp.rename({'PORTID':'SellerID',
                                  'PORTZONE':'SellerZone',
                                  "TYPE": "SellerNAICS", 
                                  "FAF": "orig_FAFID", 
                                  "dms_dest": "dest_FAFID"}, axis=1)
                temp["SellerID_Org"] = temp["SellerID"]
                temp["BuyerID_Org"] = temp["BuyerID"]
                temp['SellerID']=temp.apply(lambda x: dic_port[x["SellerID"]]+"_"+x["BuyerID"], axis=1)
            elif "export" in filename:
                ship_category="export"  
                agent= "SellerID"    
                temp["SellerID"]=temp["SellerID"].apply(lambda x: str(int(x))+ "_1")
                temp=temp.rename({'PORTID':'BuyerID',
                                  'PORTZONE':'BuyerZone',
                                  "TYPE": "BuyerNAICS", 
                                  "FAF": "dest_FAFID", 
                                  "dms_orig": "orig_FAFID"}, axis=1)
                temp["SellerID_Org"] = temp["SellerID"]
                temp["BuyerID_Org"] = temp["BuyerID"]
                temp['SellerID']=temp.apply(lambda x: x["SellerID"]+"_"+dic_port[x["BuyerID"]], axis=1)
            temp["SellerCounty"]=temp["SellerZone"].apply(lambda x: countyid_from_cbgid (x))
            temp["BuyerCounty"]=temp["BuyerZone"].apply(lambda x: countyid_from_cbgid (x))                 
            if self.sel_county:
                county_wo_sel= [i for i in self.county_in_region if i != self.sel_county]
                temp= temp[(temp['BuyerCounty']==self.sel_county) | (temp['SellerCounty']==self.sel_county)].reset_index(drop=True)
                temp= temp[~temp['SellerCounty'].isin(county_wo_sel)].reset_index(drop=True)    
            temp["D_truckload"]=0
            temp["D_selection"]=0
            temp["num_shipment"]=0
            temp["num_shipment"]=temp["shipments"].apply(lambda x: self._annual_to_daily_shipment_international(x,self.annual_to_day_factor))
            temp["D_selection"]=temp["num_shipment"].apply(lambda x: 1 if x>0 else 0) 
            temp=temp.query('D_selection ==1')

            self.sample_result[ship_category]["daily_tonnage"]= (temp['TruckLoad'] * temp['num_shipment']).sum()
            self.sample_result[ship_category]["daily_shipments"]= temp['num_shipment'].sum()
        
            df_group = temp.groupby([agent])['num_shipment'].sum().reset_index(name='num_shipment')
            list_agent_sample =self._sampling_shipper(df_group, self.sample_ratio, ship_category)
            temp_sample=temp[temp[agent].isin(list_agent_sample)].reset_index(drop=True)
            self.sample_result[ship_category]["sample_tonnage"]= (temp_sample['TruckLoad'] * temp_sample['num_shipment']).sum()
            self.sample_result[ship_category]["sample_shipments"]= temp_sample['num_shipment'].sum() 
            for i in range(0,temp_sample.shape[0]):
                temp_line=pd.DataFrame(data= {'BuyerID': [temp_sample.loc[i,"BuyerID"]] ,
                        "BuyerZone": [temp_sample.loc[i,"BuyerZone"]],
                        "BuyerNAICS":[temp_sample.loc[i,"BuyerNAICS"]],
                        "SellerID":[temp_sample.loc[i,"SellerID"]],
                        "SellerZone":[temp_sample.loc[i,"SellerZone"]],
                        "SellerNAICS":[temp_sample.loc[i,"SellerNAICS"]],
                        "TruckLoad":[temp_sample.loc[i,"TruckLoad"]],
                        "SCTG_Group":[temp_sample.loc[i,"SCTG_Group"]],
                        "Commodity_SCTG": [temp_sample.loc[i,"Commodity_SCTG"]],
                        "shipment_id":[temp_sample.loc[i,"bundle_id"]],
                        "orig_FAFID":[temp_sample.loc[i,"orig_FAFID"]],
                        "dest_FAFID":[temp_sample.loc[i,"dest_FAFID"]],
                        "mode_choice":[temp_sample.loc[i,"mode_choice"]],
                        "probability":[1],
                        "Distance":[temp_sample.loc[i,"Distance"]],
                        "Travel_time":[0],
                        "SellerCounty":[temp_sample.loc[i,"SellerCounty"]],
                        "BuyerCounty":[temp_sample.loc[i,"BuyerCounty"]],
                        "D_truckload":[temp_sample.loc[i,"D_truckload"]],
                        "D_selection":[temp_sample.loc[i,"D_selection"]],
                        "SellerID_Org":[temp_sample.loc[i,"SellerID_Org"]],
                        "BuyerID_Org":[temp_sample.loc[i,"BuyerID_Org"]],                        
                        "ship_category": ship_category})
                num_shipment= temp_sample.loc[i,"num_shipment"]
                temp_line =pd.concat([temp_line]*num_shipment, ignore_index=True)
                B2BF_international=pd.concat([B2BF_international,temp_line],ignore_index=True)       
        if B2BF_international.shape[0]>0:
            B2BF_international['TruckLoad']=B2BF_international['TruckLoad']*2000
            B2BF_international['D_truckload']=B2BF_international['TruckLoad']
            self.shipments_record = pd.concat([self.shipments_record,B2BF_international],ignore_index=True)

    def _process_commodity_group(self, file_path):
        file_path =file_path+'vius/'
        com_group_lu= pd.read_csv(file_path+"commodity_group_for_vius.csv", header=0, sep=',')
        self.shipments_record["SCTG_VIUS_group"]= self.shipments_record["Commodity_SCTG"].apply(lambda x: com_group_lu[com_group_lu["SCTG"]==x]["SCTG_Group"].values[0])

    def _annual_to_daily_shipment_domestic(self, day_factor):
        if random.uniform(0,1) <=(1/day_factor):
            return 1
        else: 
            return 0
    def _annual_to_daily_shipment_international(self, num_shipment,day_factor):
        n_shipment_sel=0
        for i in range(0,int(num_shipment)):
            if random.uniform(0,1) <=(1/day_factor):
                n_shipment_sel= n_shipment_sel+1
            else: n_shipment_sel= n_shipment_sel+0 
        return n_shipment_sel
    
    def _bin_by_shipment(self, shipment_size):
        if shipment_size <=1:
            return 0
        elif shipment_size>1 and shipment_size<4:
            return 1
        elif shipment_size >=4 and shipment_size <8:
            return 2
        elif shipment_size >=8 and shipment_size <16:
            return 3    
        elif shipment_size >=16 and shipment_size <64:
            return 4 
        elif shipment_size >=64 and shipment_size <128:
            return 5
        elif shipment_size >=128 and shipment_size <256:
            return 6
        elif shipment_size >=256:
            return 7  

    def _sampling_shipper(self, df_group, sample_ratio, ship_category): # agent: SellerID (domesti, export) vs BuyerID (import)
        if ship_category == "import":
            agent = "BuyerID"
        else: agent = "SellerID"

        df_group["binned_volume"]=df_group['num_shipment'].apply(lambda x: self._bin_by_shipment(x))

        list_bin_labels = df_group["binned_volume"].unique().tolist()
        list_agent_sample=[]
        for bin_id in list_bin_labels:
            temp=df_group[(df_group['binned_volume']==bin_id)]
            list_agent = temp[agent].unique().tolist()
            if (len(list_agent)*sample_ratio/100 >0) & (len(list_agent)*sample_ratio/100 <1):
                if random.uniform(0,1) <=len(list_agent)*sample_ratio/100:
                    list_agent= random.sample(list_agent, 1)
                    list_agent_sample=list_agent_sample+list_agent
            elif (len(list_agent)*sample_ratio/100 >=1):     
                list_agent= random.sample(list_agent, int(len(list_agent)*sample_ratio/100))
                list_agent_sample=list_agent_sample+list_agent  
        
        return list_agent_sample

class B2C_DailyShipment:
    def __init__(self, b2c_file_path=None, zone_df=None, hh_aggregation_num= None, delivery_factor=None, sample_ratio=None, sel_county= None, growth_factor=None):
        self.b2c_file_path =b2c_file_path # fdir+sub_fdir sub_fdir="{}_{}/".format(year,scenario)
        self.delivery_factor=delivery_factor
        self.sample_ratio=sample_ratio
        self.sel_county=sel_county
        self.growth_factor=growth_factor
        self.zone_df=zone_df
        self.hh_aggregation_num =hh_aggregation_num 


        if self.b2c_file_path:
            self._process_monthly_delivery(self.b2c_file_path)
            self._household_aggregation(self.zone_df,self.hh_aggregation_num)
            self._delivery_sampling(self.sample_ratio)            
        else:
            print("file path not provided or invalid.")
    def _b2c_good_select(self, delivery_f, fq_factor, growth_factor):
        delivery_f= delivery_f* (1+growth_factor/100)
        pro=delivery_f/fq_factor
        r= random.uniform(0,1)
        if r <= pro:
            select =1
            num_package=max(1,round(pro))
        else:
            select =0
            num_package=0
        return pd.Series([select, num_package])

    def _package_aggregation(self,num, commodity_type):
        if commodity_type == "goods":
            agg_package = random.randrange(1,5)
            if num >= agg_package:
                return agg_package
            else: return num
        elif commodity_type == "goods":
            agg_package = random.randrange(1,3)
            if num >= agg_package:
                return agg_package
            else: return num
        else:                
            agg_package = random.randrange(1,4)
            if num >= agg_package:
                return agg_package
            else: return num
    def _b2c_d_truckload(self, packages):
        if packages >=1:
            load_one= round(np.random.gamma(0.7, 15))
            if load_one ==0:
                load_one =1
        else: 
            load_one =0            
        return load_one 
    def _tour_time_approximation(self,zone, num_visit,size, hh_aggregation_num, zone_df):
        try:
            if num_visit >1:
                area= zone_df[zone_df['MESOZONE']==str(int(zone))]['area'].values[0]
                time = int(0.57*np.sqrt(area/size*num_visit*100)/10*60) + 2*num_visit
                if time > hh_aggregation_num*8: # 8 minutes thresholds
                    time = int(num_visit * 8) # 8 minutes thresholds
            else:
                time = int(np.random.gamma(3, 1, 1)[0] +0.5) 
        except:
            time = 30 
        return time 
    def _process_monthly_delivery(self, file_path):
        file_name= glob.glob(file_path+'*.csv')[0]
        df_per_final = pd.read_csv(file_name, header=0, sep=',')
        df_per_final = df_per_final.rename(columns={"GEOID": "MESOZONE"})
        df_per_final= df_per_final[df_per_final['County']==self.sel_county].reset_index(drop=True)

        df_per_final[['D_selection_goods', 'D_num_goods']] = df_per_final['DELIV_GOOD'].apply(lambda x: self._b2c_good_select(x, self.delivery_factor, self.growth_factor))
        df_per_final[['D_selection_groc', 'D_num_groc']] = df_per_final['DELIV_GROC'].apply(lambda x: self._b2c_good_select(x, self.delivery_factor, self.growth_factor))
        df_per_final[['D_selection_food', 'D_num_food']] = df_per_final['DELIV_FOOD'].apply(lambda x: self._b2c_good_select(x, self.delivery_factor, self.growth_factor))

        df_per_goods= df_per_final[df_per_final['D_selection_goods']==1].reset_index(drop=True)
        df_per_groc= df_per_final[df_per_final['D_selection_groc']==1].reset_index(drop=True)
        df_per_food= df_per_final[df_per_final['D_selection_food']==1].reset_index(drop=True)

        if df_per_goods.shape[0] >0:
            df_hh_goods = df_per_goods.groupby(["household_id",'block_id',"County",'MESOZONE'])["D_num_goods"].agg(hh_num_goods='sum').reset_index()
            df_hh_goods["hh_del_goods"]=df_hh_goods["hh_num_goods"].apply(lambda x: self._package_aggregation(x, "goods") )
            df_hh_goods_delivery =pd.DataFrame()
            for i in range (0, df_hh_goods.shape[0]):
                num_package=df_hh_goods['hh_del_goods'].iloc[i]
                df_hh_goods_delivery=pd.concat([df_hh_goods_delivery,pd.concat([df_hh_goods.iloc[[i]]]*num_package, ignore_index=True)], ignore_index=True)
            df_hh_goods_delivery["shipment_id"] =np.arange(df_hh_goods_delivery.shape[0])
        
            df_hh_goods_delivery["D_truckload"]=df_hh_goods_delivery["hh_del_goods"].apply(self._b2c_d_truckload)
        else:
            print ("no hh for goods delivery")
            df_hh_goods_delivery = pd.DataFrame(columns = ["household_id","block_id","County",'MESOZONE',
                                            "hh_num_goods","hh_del_goods","shipment_id","D_truckload"])              
        if df_per_groc.shape[0] >0:    
            df_hh_groc = df_per_groc.groupby(["household_id",'block_id',"County",'MESOZONE'])["D_num_groc"].agg(hh_num_groc='sum').reset_index()
            df_hh_groc["hh_del_groc"]=df_hh_groc["hh_num_groc"].apply(lambda x: self._package_aggregation(x, "groc") )
            df_hh_groc_delivery =pd.DataFrame()
            for i in range (0, df_hh_groc.shape[0]):
                num_package=df_hh_groc['hh_del_groc'].iloc[i]
                df_hh_groc_delivery=pd.concat([df_hh_groc_delivery,pd.concat([df_hh_groc.iloc[[i]]]*num_package, ignore_index=True)], ignore_index=True)
        else:
            print ("no hh for grocery delivery")   
            df_hh_groc_delivery = pd.DataFrame(columns = ["household_id","block_id","County",'MESOZONE',
                                            "hh_num_goods","hh_del_goods","shipment_id","D_truckload"])  
        if df_per_groc.shape[0] >0: 
            df_hh_food = df_per_food.groupby(["household_id",'block_id',"County",'MESOZONE'])["D_num_food"].agg(hh_num_food='sum').reset_index()
            df_hh_food["hh_del_food"]=df_hh_food["hh_num_food"].apply(lambda x: self._package_aggregation(x, "food") )
            df_hh_food_delivery =pd.DataFrame()
            for i in range (0, df_hh_food.shape[0]):
                num_package=df_hh_food['hh_del_food'].iloc[i]
                df_hh_food_delivery=pd.concat([df_hh_food_delivery,pd.concat([df_hh_food.iloc[[i]]]*num_package, ignore_index=True)], ignore_index=True)    
        else:
            print ("no hh for food delivery") 
            df_hh_food_delivery = pd.DataFrame(columns = ["household_id","block_id","County",'MESOZONE',
                                            "hh_num_goods","hh_del_goods","shipment_id","D_truckload"])

        self.df_hh_d_good= df_hh_goods_delivery
        self.df_hh_d_groc= df_hh_groc_delivery
        self.df_hh_d_food= df_hh_food_delivery       

    def _household_aggregation(self, zone_df,hh_aggregation_num):
        
        df_hh_D_Group_hhcount=self.df_hh_d_good.groupby(['MESOZONE'])['household_id'].count().reset_index(name='num_hh')
        # Calculate how many shipments-households in a CBG
        df_hh_D_Group_hhcount['group_size']=df_hh_D_Group_hhcount['num_hh'].apply(lambda x: int(x/hh_aggregation_num)+1)
        self.df_hh_d_good=self.df_hh_d_good.merge(df_hh_D_Group_hhcount[['MESOZONE','group_size']], on='MESOZONE', how='left')
        # Assign the aggregate household_id 
        self.df_hh_d_good['household_gr_id']=self.df_hh_d_good.apply(lambda x: str(int(x["MESOZONE"]))+"_"+str(random.randint(1,x["group_size"])), axis=1)
        # Save household_id and household_gr_id 
        self.payload_household_lookup=self.df_hh_d_good[['household_gr_id','household_id']]
        df_hh_D_GrID= self.df_hh_d_good.groupby(['household_gr_id', 'MESOZONE'])['D_truckload'].agg(D_truckload='sum', num_hh='count').reset_index()
        df_hh_D_GrID=df_hh_D_GrID.merge(df_hh_D_Group_hhcount[['MESOZONE','group_size']], on='MESOZONE', how='left')
        # Create approximate tour travel time to serve aggregated household-shipments
        df_hh_D_GrID['tour_tt']=df_hh_D_GrID.apply(lambda x: self._tour_time_approximation(x['MESOZONE'], x['num_hh'], x['group_size'],hh_aggregation_num,zone_df), axis=1)
        
        self.df_hh_d_good_aggregate= df_hh_D_GrID.reset_index()

    def _delivery_sampling (self, sample_ratio):
        self.df_hh_d_good_sample= self.df_hh_d_good_aggregate.sample(frac=sample_ratio/100).reset_index(drop=True)
        self.df_hh_d_groc_sample= self.df_hh_d_groc.sample(frac=sample_ratio/100).reset_index(drop=True) 
        self.df_hh_d_food_sample= self.df_hh_d_food.sample(frac=sample_ratio/100).reset_index(drop=True)     



# %%