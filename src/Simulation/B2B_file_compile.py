import pandas as pd
# %%
county_list=[1, 13, 41, 55, 75, 81, 85, 95, 97]
#ounty_list=[1]
f_dir="../../../FRISM_input_output_SF/Sim_outputs/Tour_plan/"
def change_payloadid(payloadId,tourId,c_nm):
    if "dB2B" in payloadId:
        if payloadId.endswith("_"):
            payloadId =str(c_nm)+ "_dB2B"+str(tourId)+"_"
        else:    
            payloadId =str(c_nm)+ "_dB2B"+str(tourId)
    return payloadId

for county in county_list:
    tour_num=0
    N_df_payload=pd.DataFrame()
    N_df_tour=pd.DataFrame()
    N_df_carrier=pd.DataFrame()
    for file_nm in range(0,10):
    #for file_nm in range(0,3):    
        df_payload = pd.read_csv(f_dir+"B2B_county{}_payload{}.csv".format(str(county), str(file_nm))).reset_index()
        df_tour = pd.read_csv(f_dir+"B2B_county{}_freight_tours{}.csv".format(str(county), str(file_nm))).reset_index()
        df_carrier = pd.read_csv(f_dir+"B2B_county{}_carrier{}.csv".format(str(county), str(file_nm))).reset_index()

        df_carrier["tourId"]=df_carrier["tourId"].apply(lambda x: x+tour_num)
        df_payload["tourId"]=df_payload["tourId"].apply(lambda x: x+tour_num)
        df_tour["tour_id"]=df_tour["tour_id"].apply(lambda x: x+tour_num)
        df_payload["payloadId"]=df_payload.apply(lambda x:change_payloadid(x["payloadId"],x["tourId"],county),axis=1)

        tour_num=df_carrier["tourId"].iloc[-1]+1
        N_df_payload=pd.concat([N_df_payload,df_payload], ignore_index=True).reset_index(drop=True)
        N_df_tour=pd.concat([N_df_tour,df_tour], ignore_index=True).reset_index(drop=True)
        N_df_carrier=pd.concat([N_df_carrier,df_carrier], ignore_index=True).reset_index(drop=True)

    N_df_payload.to_csv(f_dir+"B2B_county{}_payload.csv".format(str(county)), index = False, header=True)
    N_df_tour.to_csv(f_dir+"B2B_county{}_freight_tours.csv".format(str(county)), index = False, header=True)
    N_df_carrier.to_csv(f_dir+"B2B_county{}_carrier.csv".format(str(county)), index = False, header=True)        


# %%
