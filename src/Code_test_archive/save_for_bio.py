
# %%
## shopping nested 
database = db.Database('ondemand', atus_df)

# The following statement allows you to use the names of the
# variable as Python variable.
globals().update(database.variables)

# Parameters to be estimated
## shopping nested 
database = db.Database('shop', atus_df)

# The following statement allows you to use the names of the
# variable as Python variable.
globals().update(database.variables)

# Parameters to be estimated
## Intercept
ASC_NOS = Beta('ASC_NOS', 0, None, None, 1)
ASC_OFF = Beta('ASC_OFF', 0, None, None, 0)
ASC_ONS = Beta('ASC_ONS', 0, None, None, 0)
ASC_BOT = Beta('ASC_BOT', 0, None, None, 0)
## Beta
B_SEX_V0= Beta('B_SEX_V0', 0, None, None, 1)
B_SEX_V1= Beta('B_SEX_V1', 0, None, None, 0)
B_SEX_V2= Beta('B_SEX_V2', 0, None, None, 0)
B_SEX_V3= Beta('B_SEX_V3', 0, None, None, 0)

## Beta
B_INC_V0= Beta('B_INC_V0', 0, None, None, 1)
B_INC_V1= Beta('B_INC_V1', 0, None, None, 0)
B_INC_V2= Beta('B_INC_V2', 0, None, None, 0)
B_INC_V3= Beta('B_INC_V3', 0, None, None, 0)
###
B_HHSIZE_V0= Beta('B_HHSIZE_V0', 0, None, None, 1)
B_HHSIZE_V1= Beta('B_HHSIZE_V1', 0, None, None, 0)
B_HHSIZE_V2= Beta('B_HHSIZE_V2', 0, None, None, 0)
B_HHSIZE_V3= Beta('B_HHSIZE_V3', 0, None, None, 0)
###
B_WORKER_V0= Beta('B_WORKER_V0', 0, None, None, 1)
B_WORKER_V1= Beta('B_WORKER_V1', 0, None, None, 0)
B_WORKER_V2= Beta('B_WORKER_V2', 0, None, None, 0)
B_WORKER_V3= Beta('B_WORKER_V3', 0, None, None, 0)

###
B_MSACAT_V0= Beta('B_MSACAT_V0', 0, None, None, 1)
B_MSACAT_V1= Beta('B_MSACAT_V1', 0, None, None, 0)
B_MSACAT_V2= Beta('B_MSACAT_V2', 0, None, None, 0)
B_MSACAT_V3= Beta('B_MSACAT_V3', 0, None, None, 0)
###
B_EDUC_1_V0= Beta('B_EDUC_1_V0', 0, None, None, 1)
B_EDUC_1_V1= Beta('B_EDUC_1_V1', 0, None, None, 0)
B_EDUC_1_V2= Beta('B_EDUC_1_V2', 0, None, None, 0)
B_EDUC_1_V3= Beta('B_EDUC_1_V3', 0, None, None, 0)
###
B_EDUC_2_V0= Beta('B_EDUC_2_V0', 0, None, None, 1)
B_EDUC_2_V1= Beta('B_EDUC_2_V1', 0, None, None, 0)
B_EDUC_2_V2= Beta('B_EDUC_2_V2', 0, None, None, 0)
B_EDUC_2_V3= Beta('B_EDUC_2_V3', 0, None, None, 0)
###
B_EDUC_3_V0= Beta('B_EDUC_3_V0', 0, None, None, 1)
B_EDUC_3_V1= Beta('B_EDUC_3_V1', 0, None, None, 0)
B_EDUC_3_V2= Beta('B_EDUC_3_V2', 0, None, None, 0)
B_EDUC_3_V3= Beta('B_EDUC_3_V3', 0, None, None, 0)

###
B_AGE_IMP_1_V0= Beta('B_AGE_IMP_1_V0', 0, None, None, 1)
B_AGE_IMP_1_V1= Beta('B_AGE_IMP_1_V1', 0, None, None, 0)
B_AGE_IMP_1_V2= Beta('B_AGE_IMP_1_V2', 0, None, None, 0)
B_AGE_IMP_1_V3= Beta('B_AGE_IMP_1_V3', 0, None, None, 0)

###
B_AGE_IMP_2_V0= Beta('B_AGE_IMP_2_V0', 0, None, None, 1)
B_AGE_IMP_2_V1= Beta('B_AGE_IMP_2_V1', 0, None, None, 0)
B_AGE_IMP_2_V2= Beta('B_AGE_IMP_2_V2', 0, None, None, 0)
B_AGE_IMP_2_V3= Beta('B_AGE_IMP_2_V3', 0, None, None, 0)
###
B_AGE_IMP_3_V0= Beta('B_AGE_IMP_3_V0', 0, None, None, 1)
B_AGE_IMP_3_V1= Beta('B_AGE_IMP_3_V1', 0, None, None, 0)
B_AGE_IMP_3_V2= Beta('B_AGE_IMP_3_V2', 0, None, None, 0)
B_AGE_IMP_3_V3= Beta('B_AGE_IMP_3_V3', 0, None, None, 0)
###
###
B_RACE_1_V0= Beta('B_RACE_1_V0', 0, None, None, 1)
B_RACE_1_V1= Beta('B_RACE_1_V1', 0, None, None, 0)
B_RACE_1_V2= Beta('B_RACE_1_V2', 0, None, None, 0)
B_RACE_1_V3= Beta('B_RACE_1_V3', 0, None, None, 0)

###
B_RACE_2_V0= Beta('B_RACE_2_V0', 0, None, None, 1)
B_RACE_2_V1= Beta('B_RACE_2_V1', 0, None, None, 0)
B_RACE_2_V2= Beta('B_RACE_2_V2', 0, None, None, 0)
B_RACE_2_V3= Beta('B_RACE_2_V3', 0, None, None, 0)
###
B_RACE_3_V0= Beta('B_RACE_3_V0', 0, None, None, 1)
B_RACE_3_V1= Beta('B_RACE_3_V1', 0, None, None, 0)
B_RACE_3_V2= Beta('B_RACE_3_V2', 0, None, None, 0)
B_RACE_3_V3= Beta('B_RACE_3_V3', 0, None, None, 0)

###
B_CENSUS_R_2_V0= Beta('B_CENSUS_R_2_V0', 0, None, None, 1)
B_CENSUS_R_2_V1= Beta('B_CENSUS_R_2_V1', 0, None, None, 0)
B_CENSUS_R_2_V2= Beta('B_CENSUS_R_2_V2', 0, None, None, 0)
B_CENSUS_R_2_V3= Beta('B_CENSUS_R_2_V3', 0, None, None, 0)
###
B_CENSUS_R_3_V0= Beta('B_CENSUS_R_3_V0', 0, None, None, 1)
B_CENSUS_R_3_V1= Beta('B_CENSUS_R_3_V1', 0, None, None, 0)
B_CENSUS_R_3_V2= Beta('B_CENSUS_R_3_V2', 0, None, None, 0)
B_CENSUS_R_3_V3= Beta('B_CENSUS_R_3_V3', 0, None, None, 0)
##
B_CENSUS_R_4_V0= Beta('B_CENSUS_R_4_V0', 0, None, None, 1)
B_CENSUS_R_4_V1= Beta('B_CENSUS_R_4_V1', 0, None, None, 0)
B_CENSUS_R_4_V2= Beta('B_CENSUS_R_4_V2', 0, None, None, 0)
B_CENSUS_R_4_V3= Beta('B_CENSUS_R_4_V3', 0, None, None, 0)

###

Prob_no_V1= Beta('Prob_no_V1', 0, None, None, 1)
Prob_no_V2= Beta('Prob_no_V2', 0, None, None, 0)
Prob_no_V3= Beta('Prob_no_V3', 0, None, None, 0)

#Prob_lo_V0= Beta('Prob_lo_V0', 0, None, None, 1)
Prob_lo_V1= Beta('Prob_lo_V1', 0, None, None, 1)
Prob_lo_V2= Beta('Prob_lo_V2', 0, None, None, 0)
Prob_lo_V3= Beta('Prob_lo_V3', 0, None, None, 0)
###
#Prob_md_V0= Beta('Prob_md_V0', 0, None, None, 1)
# Prob_md_V1= Beta('Prob_md_V1', 0, None, None, 1)
# Prob_md_V2= Beta('Prob_md_V2', 0, None, None, 0)
# Prob_md_V3= Beta('Prob_md_V3', 0, None, None, 0)
##
#Prob_hi_V0= Beta('Prob_hi_V0', 0, None, None, 1)
Prob_hi_V1= Beta('Prob_hi_V1', 0, None, None, 1)
Prob_hi_V2= Beta('Prob_hi_V2', 0, None, None, 0)
Prob_hi_V3= Beta('Prob_hi_V3', 0, None, None, 0)


# Definition of the utility functions
V0 = ASC_NOS + B_SEX_V0 * R_SEX_IMP + B_HHSIZE_V0 * HHSIZE + B_WORKER_V0 *WORKER + B_EDUC_1_V0 *EDUC_1 + B_EDUC_2_V0 *EDUC_2 + B_EDUC_3_V0 *EDUC_3 + B_AGE_IMP_1_V0 *R_AGE_IMP_1+ B_AGE_IMP_2_V0 *R_AGE_IMP_2+B_AGE_IMP_3_V0 *R_AGE_IMP_3+\
   B_RACE_1_V0 *R_RACE_1+B_RACE_2_V0 *R_RACE_2 +B_MSACAT_V0 *MSACAT + B_INC_V0 * income_val
V1 = ASC_OFF + B_SEX_V1 * R_SEX_IMP + B_HHSIZE_V1 * HHSIZE + B_WORKER_V1 *WORKER + B_EDUC_1_V1 *EDUC_1 + B_EDUC_2_V1 *EDUC_2 + B_EDUC_3_V1 *EDUC_3 + B_AGE_IMP_1_V1 *R_AGE_IMP_1+ B_AGE_IMP_2_V1 *R_AGE_IMP_2+B_AGE_IMP_3_V1 *R_AGE_IMP_3+\
    B_RACE_1_V1 *R_RACE_1+B_RACE_2_V1 *R_RACE_2+B_CENSUS_R_2_V1 *CENSUS_R_2 +B_CENSUS_R_3_V1 *CENSUS_R_3+B_CENSUS_R_4_V1 *CENSUS_R_4 +B_MSACAT_V1 *MSACAT + B_INC_V1 * income_val +Prob_no_V1*Prob_no+Prob_lo_V1*Prob_lo+Prob_md_V1*Prob_no+Prob_md_V1*Prob_md +Prob_hi_V1*Prob_hi
V2 = ASC_ONS + B_SEX_V2 * R_SEX_IMP + B_HHSIZE_V2 * HHSIZE + B_WORKER_V2 *WORKER + B_EDUC_1_V2 *EDUC_1 + B_EDUC_2_V2 *EDUC_2 + B_EDUC_3_V2 *EDUC_3 + B_AGE_IMP_1_V2 *R_AGE_IMP_1+ B_AGE_IMP_2_V2 *R_AGE_IMP_2+B_AGE_IMP_3_V2 *R_AGE_IMP_3+\
   B_RACE_1_V2 *R_RACE_1+B_RACE_2_V2 *R_RACE_2 +B_CENSUS_R_2_V2 *CENSUS_R_2 +B_CENSUS_R_3_V2 *CENSUS_R_3+B_CENSUS_R_4_V2 *CENSUS_R_4 +B_MSACAT_V2 *MSACAT + B_INC_V2 * income_val +Prob_no_V2*Prob_no+Prob_lo_V2*Prob_lo+Prob_md_V2*Prob_no+Prob_md_V2*Prob_md +Prob_hi_V2*Prob_hi
V3 = ASC_BOT + B_SEX_V3 * R_SEX_IMP + B_HHSIZE_V3 * HHSIZE + B_WORKER_V3 *WORKER + B_EDUC_1_V3 *EDUC_1 + B_EDUC_2_V3 *EDUC_2 + B_EDUC_3_V3 *EDUC_3 + B_AGE_IMP_1_V3 *R_AGE_IMP_1+ B_AGE_IMP_2_V3 *R_AGE_IMP_2+B_AGE_IMP_3_V3 *R_AGE_IMP_3+\
   B_RACE_1_V3 *R_RACE_1+B_RACE_2_V3 *R_RACE_2 +B_CENSUS_R_2_V3 *CENSUS_R_2 +B_CENSUS_R_3_V3 *CENSUS_R_3+B_CENSUS_R_4_V3 *CENSUS_R_4 +B_MSACAT_V3 *MSACAT+ B_INC_V3 * income_val +Prob_no_V3*Prob_no+Prob_lo_V3*Prob_lo+Prob_md_V3*Prob_no+Prob_md_V3*Prob_md +Prob_hi_V3*Prob_hi
# Associate utility functions with the numbering of alternatives
# Associate utility functions with the numbering of alternatives
V = {0: V0,1: V1, 2: V2, 3: V3}

# Associate the availability conditions with the alternatives
av = {0: Avail, 1: Avail, 2: Avail, 3: Avail}

# nest parameters
NEST_OD=Beta('NEST_OD',1,1.0,10,0)

NO_OD =1.0, [0]
OD=NEST_OD, [1,2,3]

nests = NO_OD, OD
# Definition of the model. This is the contribution of each
# observation to the log likelihood function.
logprob = models.lognested(V, av, nests, ondemand_choice)

# Define level of verbosity
logger = msg.bioMessage()
# logger.setSilent()
# logger.setWarning()
logger.setGeneral()
# logger.setDetailed()

# Create the Biogeme object
formulas = {'loglike': logprob, 'weight': TUFINLWGT}
biogeme = bio.BIOGEME(database, formulas)
biogeme.modelName = "ondemand_nested"

# Calculate the null log likelihood for reporting.
biogeme.calculateNullLoglikelihood(av)

# Estimate the parameters
results = biogeme.estimate()
pandasResults = results.getEstimatedParameters()
print(pandasResults)

# Get the results in a pandas table
pandasResults = results.getEstimatedParameters()
print(pandasResults)    


# %%
# 13 
############################################# Model estimation ################################
## shopping nested 
database = db.Database('shop', atus_df)

# The following statement allows you to use the names of the
# variable as Python variable.
globals().update(database.variables)

# Parameters to be estimated
## Intercept
ASC_NOS = Beta('ASC_NOS', 0, None, None, 1)
ASC_OFF = Beta('ASC_OFF', 0, None, None, 0)
ASC_ONS = Beta('ASC_ONS', 0, None, None, 0)
ASC_BOT = Beta('ASC_BOT', 0, None, None, 0)
## Beta
B_SEX_V0= Beta('B_SEX_V0', 0, None, None, 1)
B_SEX_V1= Beta('B_SEX_V1', 0, None, None, 0)
B_SEX_V2= Beta('B_SEX_V2', 0, None, None, 0)
B_SEX_V3= Beta('B_SEX_V3', 0, None, None, 0)

## Beta
B_INC_V0= Beta('B_INC_V0', 0, None, None, 0)
B_INC_V1= Beta('B_INC_V1', 0, None, None, 0)
B_INC_V2= Beta('B_INC_V2', 0, None, None, 0)
B_INC_V3= Beta('B_INC_V3', 0, None, None, 0)
###
B_HHSIZE_V0= Beta('B_HHSIZE_V0', 0, None, None, 0)
B_HHSIZE_V1= Beta('B_HHSIZE_V1', 0, None, None, 0)
B_HHSIZE_V2= Beta('B_HHSIZE_V2', 0, None, None, 0)
B_HHSIZE_V3= Beta('B_HHSIZE_V3', 0, None, None, 0)
###
B_WORKER_V0= Beta('B_WORKER_V0', 0, None, None, 0)
B_WORKER_V1= Beta('B_WORKER_V1', 0, None, None, 0)
B_WORKER_V2= Beta('B_WORKER_V2', 0, None, None, 0)
B_WORKER_V3= Beta('B_WORKER_V3', 0, None, None, 0)

###
B_MSACAT_V0= Beta('B_MSACAT_V0', 0, None, None, 1)
B_MSACAT_V1= Beta('B_MSACAT_V1', 0, None, None, 0)
B_MSACAT_V2= Beta('B_MSACAT_V2', 0, None, None, 0)
B_MSACAT_V3= Beta('B_MSACAT_V3', 0, None, None, 0)
###
B_EDUC_0_V0= Beta('B_EDUC_0_V0', 0, None, None, 0)
B_EDUC_0_V1= Beta('B_EDUC_0_V1', 0, None, None, 0)
B_EDUC_0_V2= Beta('B_EDUC_0_V2', 0, None, None, 0)
B_EDUC_0_V3= Beta('B_EDUC_0_V3', 0, None, None, 0)
###
B_EDUC_1_V0= Beta('B_EDUC_1_V0', 0, None, None, 0)
B_EDUC_1_V1= Beta('B_EDUC_1_V1', 0, None, None, 0)
B_EDUC_1_V2= Beta('B_EDUC_1_V2', 0, None, None, 0)
B_EDUC_1_V3= Beta('B_EDUC_1_V3', 0, None, None, 0)
###
B_EDUC_2_V0= Beta('B_EDUC_2_V0', 0, None, None, 0)
B_EDUC_2_V1= Beta('B_EDUC_2_V1', 0, None, None, 0)
B_EDUC_2_V2= Beta('B_EDUC_2_V2', 0, None, None, 0)
B_EDUC_2_V3= Beta('B_EDUC_2_V3', 0, None, None, 0)
###
B_EDUC_3_V0= Beta('B_EDUC_3_V0', 0, None, None, 0)
B_EDUC_3_V1= Beta('B_EDUC_3_V1', 0, None, None, 0)
B_EDUC_3_V2= Beta('B_EDUC_3_V2', 0, None, None, 0)
B_EDUC_3_V3= Beta('B_EDUC_3_V3', 0, None, None, 0)

###
B_AGE_IMP_0_V0= Beta('B_AGE_IMP_0_V0', 0, None, None, 0)
B_AGE_IMP_0_V1= Beta('B_AGE_IMP_0_V1', 0, None, None, 0)
B_AGE_IMP_0_V2= Beta('B_AGE_IMP_0_V2', 0, None, None, 0)
B_AGE_IMP_0_V3= Beta('B_AGE_IMP_0_V3', 0, None, None, 0)

###
B_AGE_IMP_1_V0= Beta('B_AGE_IMP_1_V0', 0, None, None, 0)
B_AGE_IMP_1_V1= Beta('B_AGE_IMP_1_V1', 0, None, None, 0)
B_AGE_IMP_1_V2= Beta('B_AGE_IMP_1_V2', 0, None, None, 0)
B_AGE_IMP_1_V3= Beta('B_AGE_IMP_1_V3', 0, None, None, 0)

###
B_AGE_IMP_2_V0= Beta('B_AGE_IMP_2_V0', 0, None, None, 0)
B_AGE_IMP_2_V1= Beta('B_AGE_IMP_2_V1', 0, None, None, 0)
B_AGE_IMP_2_V2= Beta('B_AGE_IMP_2_V2', 0, None, None, 0)
B_AGE_IMP_2_V3= Beta('B_AGE_IMP_2_V3', 0, None, None, 0)
###
B_AGE_IMP_3_V0= Beta('B_AGE_IMP_3_V0', 0, None, None, 0)
B_AGE_IMP_3_V1= Beta('B_AGE_IMP_3_V1', 0, None, None, 0)
B_AGE_IMP_3_V2= Beta('B_AGE_IMP_3_V2', 0, None, None, 0)
B_AGE_IMP_3_V3= Beta('B_AGE_IMP_3_V3', 0, None, None, 0)
###
###
B_RACE_1_V0= Beta('B_RACE_1_V0', 0, None, None, 1)
B_RACE_1_V1= Beta('B_RACE_1_V1', 0, None, None, 0)
B_RACE_1_V2= Beta('B_RACE_1_V2', 0, None, None, 0)
B_RACE_1_V3= Beta('B_RACE_1_V3', 0, None, None, 0)

###
B_RACE_2_V0= Beta('B_RACE_2_V0', 0, None, None, 1)
B_RACE_2_V1= Beta('B_RACE_2_V1', 0, None, None, 0)
B_RACE_2_V2= Beta('B_RACE_2_V2', 0, None, None, 0)
B_RACE_2_V3= Beta('B_RACE_2_V3', 0, None, None, 0)
###
B_RACE_3_V0= Beta('B_RACE_3_V0', 0, None, None, 1)
B_RACE_3_V1= Beta('B_RACE_3_V1', 0, None, None, 0)
B_RACE_3_V2= Beta('B_RACE_3_V2', 0, None, None, 0)
B_RACE_3_V3= Beta('B_RACE_3_V3', 0, None, None, 0)

###
B_CENSUS_R_2_V0= Beta('B_CENSUS_R_2_V0', 0, None, None, 1)
B_CENSUS_R_2_V1= Beta('B_CENSUS_R_2_V1', 0, None, None, 0)
B_CENSUS_R_2_V2= Beta('B_CENSUS_R_2_V2', 0, None, None, 0)
B_CENSUS_R_2_V3= Beta('B_CENSUS_R_2_V3', 0, None, None, 0)
###
B_CENSUS_R_3_V0= Beta('B_CENSUS_R_3_V0', 0, None, None, 1)
B_CENSUS_R_3_V1= Beta('B_CENSUS_R_3_V1', 0, None, None, 0)
B_CENSUS_R_3_V2= Beta('B_CENSUS_R_3_V2', 0, None, None, 0)
B_CENSUS_R_3_V3= Beta('B_CENSUS_R_3_V3', 0, None, None, 0)
##
B_CENSUS_R_4_V0= Beta('B_CENSUS_R_4_V0', 0, None, None, 1)
B_CENSUS_R_4_V1= Beta('B_CENSUS_R_4_V1', 0, None, None, 0)
B_CENSUS_R_4_V2= Beta('B_CENSUS_R_4_V2', 0, None, None, 0)
B_CENSUS_R_4_V3= Beta('B_CENSUS_R_4_V3', 0, None, None, 0)

###

Prob_no_V1= Beta('Prob_no_V1', 0, None, None, 0)
Prob_no_V2= Beta('Prob_no_V2', 0, None, None, 0)
Prob_no_V3= Beta('Prob_no_V3', 0, None, None, 0)

#Prob_lo_V0= Beta('Prob_lo_V0', 0, None, None, 1)
Prob_lo_V1= Beta('Prob_lo_V1', 0, None, None, 0)
Prob_lo_V2= Beta('Prob_lo_V2', 0, None, None, 0)
Prob_lo_V3= Beta('Prob_lo_V3', 0, None, None, 0)
###
#Prob_md_V0= Beta('Prob_md_V0', 0, None, None, 1)
Prob_md_V1= Beta('Prob_md_V1', 0, None, None, 0)
Prob_md_V2= Beta('Prob_md_V2', 0, None, None, 0)
Prob_md_V3= Beta('Prob_md_V3', 0, None, None, 0)
##
#Prob_hi_V0= Beta('Prob_hi_V0', 0, None, None, 1)
Prob_hi_V1= Beta('Prob_hi_V1', 0, None, None, 0)
Prob_hi_V2= Beta('Prob_hi_V2', 0, None, None, 0)
Prob_hi_V3= Beta('Prob_hi_V3', 0, None, None, 0)


# Definition of the utility functions
V0 = ASC_NOS + B_SEX_V0 * R_SEX_IMP + B_HHSIZE_V0 * HHSIZE + B_WORKER_V0 *WORKER + B_EDUC_0_V0 *EDUC_0 +B_AGE_IMP_3_V0 *R_AGE_IMP_3 +\
    B_MSACAT_V0 *MSACAT + B_INC_V0 * income_val
V1 = ASC_OFF + B_SEX_V1 * R_SEX_IMP  +\
   B_MSACAT_V1 *MSACAT +Prob_no_V1*Prob_no+Prob_lo_V1*Prob_lo+Prob_md_V1*Prob_no+Prob_md_V1*Prob_md +Prob_hi_V1*Prob_hi
V2 = ASC_ONS + B_SEX_V2 * R_SEX_IMP + B_HHSIZE_V2 * HHSIZE +\
     B_MSACAT_V2 *MSACAT  +Prob_no_V2*Prob_no+Prob_lo_V2*Prob_lo+Prob_md_V2*Prob_no+Prob_md_V2*Prob_md +Prob_hi_V2*Prob_hi
V3 = ASC_BOT + B_SEX_V3 * R_SEX_IMP + B_HHSIZE_V3 * HHSIZE +\
   B_MSACAT_V3 *MSACAT +Prob_no_V3*Prob_no+Prob_lo_V3*Prob_lo+Prob_md_V3*Prob_no+Prob_md_V3*Prob_md +Prob_hi_V3*Prob_hi
# Associate utility functions with the numbering of alternatives
# Associate utility functions with the numbering of alternatives
V = {0: V0,1: V1, 2: V2, 3: V3}

# Associate the availability conditions with the alternatives
av = {0: Avail, 1: Avail, 2: Avail, 3: Avail}

# nest parameters
NEST_SHOP=Beta('NEST_SHOP',1,None,None,0)

NO_SHOP =1.0, [0]
SHOP=NEST_SHOP, [1,2,3]

nests = NO_SHOP, SHOP
# Definition of the model. This is the contribution of each
# observation to the log likelihood function.
logprob = models.lognested(V, av, nests, shop_choice)

# Define level of verbosity
logger = msg.bioMessage()
# logger.setSilent()
# logger.setWarning()
logger.setGeneral()
# logger.setDetailed()

# Create the Biogeme object
formulas = {'loglike': logprob, 'weight': TUFINLWGT}
biogeme = bio.BIOGEME(database, formulas)
biogeme.modelName = "shoping_nested"


# Create the Biogeme object
#logprob = models.loglogit(V, av, shop_choice)
# formulas = {'loglike': logprob, 'weight': TUFINLWGT}
# biogeme = bio.BIOGEME(database, formulas)
# biogeme.modelName = 'shopping_MNL'

# Calculate the null log likelihood for reporting.
biogeme.calculateNullLoglikelihood(av)

# Estimate the parameters
results = biogeme.estimate()
pandasResults = results.getEstimatedParameters()
print(pandasResults)



## shopping nested 
database = db.Database('shop', atus_df)

# The following statement allows you to use the names of the
# variable as Python variable.
globals().update(database.variables)

# Parameters to be estimated
## Intercept
ASC_NOS = Beta('ASC_NOS', 0, None, None, 1)
ASC_OFF = Beta('ASC_OFF', 0, None, None, 0)
ASC_ONS = Beta('ASC_ONS', 0, None, None, 0)
ASC_BOT = Beta('ASC_BOT', 0, None, None, 0)
## Beta
B_SEX_V0= Beta('B_SEX_V0', 0, None, None, 1)
B_SEX_V1= Beta('B_SEX_V1', 0, None, None, 0)
B_SEX_V2= Beta('B_SEX_V2', 0, None, None, 0)
B_SEX_V3= Beta('B_SEX_V3', 0, None, None, 0)

## Beta
B_INC_V0= Beta('B_INC_V0', 0, None, None, 1)
B_INC_V1= Beta('B_INC_V1', 0, None, None, 0)
B_INC_V2= Beta('B_INC_V2', 0, None, None, 0)
B_INC_V3= Beta('B_INC_V3', 0, None, None, 0)
###
B_HHSIZE_V0= Beta('B_HHSIZE_V0', 0, None, None, 1)
B_HHSIZE_V1= Beta('B_HHSIZE_V1', 0, None, None, 0)
B_HHSIZE_V2= Beta('B_HHSIZE_V2', 0, None, None, 0)
B_HHSIZE_V3= Beta('B_HHSIZE_V3', 0, None, None, 0)
###
B_WORKER_V0= Beta('B_WORKER_V0', 0, None, None, 1)
B_WORKER_V1= Beta('B_WORKER_V1', 0, None, None, 0)
B_WORKER_V2= Beta('B_WORKER_V2', 0, None, None, 0)
B_WORKER_V3= Beta('B_WORKER_V3', 0, None, None, 0)

###
B_MSACAT_V0= Beta('B_MSACAT_V0', 0, None, None, 1)
B_MSACAT_V1= Beta('B_MSACAT_V1', 0, None, None, 0)
B_MSACAT_V2= Beta('B_MSACAT_V2', 0, None, None, 0)
B_MSACAT_V3= Beta('B_MSACAT_V3', 0, None, None, 0)
###
B_EDUC_0_V0= Beta('B_EDUC_0_V0', 0, None, None, 0)
B_EDUC_0_V1= Beta('B_EDUC_0_V1', 0, None, None, 0)
B_EDUC_0_V2= Beta('B_EDUC_0_V2', 0, None, None, 0)
B_EDUC_0_V3= Beta('B_EDUC_0_V3', 0, None, None, 0)
###
B_EDUC_1_V0= Beta('B_EDUC_1_V0', 0, None, None, 0)
B_EDUC_1_V1= Beta('B_EDUC_1_V1', 0, None, None, 0)
B_EDUC_1_V2= Beta('B_EDUC_1_V2', 0, None, None, 0)
B_EDUC_1_V3= Beta('B_EDUC_1_V3', 0, None, None, 0)
###
B_EDUC_2_V0= Beta('B_EDUC_2_V0', 0, None, None, 0)
B_EDUC_2_V1= Beta('B_EDUC_2_V1', 0, None, None, 0)
B_EDUC_2_V2= Beta('B_EDUC_2_V2', 0, None, None, 0)
B_EDUC_2_V3= Beta('B_EDUC_2_V3', 0, None, None, 0)
###
B_EDUC_3_V0= Beta('B_EDUC_3_V0', 0, None, None, 0)
B_EDUC_3_V1= Beta('B_EDUC_3_V1', 0, None, None, 0)
B_EDUC_3_V2= Beta('B_EDUC_3_V2', 0, None, None, 0)
B_EDUC_3_V3= Beta('B_EDUC_3_V3', 0, None, None, 0)

###
B_AGE_IMP_0_V0= Beta('B_AGE_IMP_0_V0', 0, None, None, 0)
B_AGE_IMP_0_V1= Beta('B_AGE_IMP_0_V1', 0, None, None, 0)
B_AGE_IMP_0_V2= Beta('B_AGE_IMP_0_V2', 0, None, None, 0)
B_AGE_IMP_0_V3= Beta('B_AGE_IMP_0_V3', 0, None, None, 0)

###
B_AGE_IMP_1_V0= Beta('B_AGE_IMP_1_V0', 0, None, None, 0)
B_AGE_IMP_1_V1= Beta('B_AGE_IMP_1_V1', 0, None, None, 0)
B_AGE_IMP_1_V2= Beta('B_AGE_IMP_1_V2', 0, None, None, 0)
B_AGE_IMP_1_V3= Beta('B_AGE_IMP_1_V3', 0, None, None, 0)

###
B_AGE_IMP_2_V0= Beta('B_AGE_IMP_2_V0', 0, None, None, 0)
B_AGE_IMP_2_V1= Beta('B_AGE_IMP_2_V1', 0, None, None, 0)
B_AGE_IMP_2_V2= Beta('B_AGE_IMP_2_V2', 0, None, None, 0)
B_AGE_IMP_2_V3= Beta('B_AGE_IMP_2_V3', 0, None, None, 0)
###
B_AGE_IMP_3_V0= Beta('B_AGE_IMP_3_V0', 0, None, None, 0)
B_AGE_IMP_3_V1= Beta('B_AGE_IMP_3_V1', 0, None, None, 0)
B_AGE_IMP_3_V2= Beta('B_AGE_IMP_3_V2', 0, None, None, 0)
B_AGE_IMP_3_V3= Beta('B_AGE_IMP_3_V3', 0, None, None, 0)
###
###
B_RACE_1_V0= Beta('B_RACE_1_V0', 0, None, None, 1)
B_RACE_1_V1= Beta('B_RACE_1_V1', 0, None, None, 0)
B_RACE_1_V2= Beta('B_RACE_1_V2', 0, None, None, 0)
B_RACE_1_V3= Beta('B_RACE_1_V3', 0, None, None, 0)

###
B_RACE_2_V0= Beta('B_RACE_2_V0', 0, None, None, 1)
B_RACE_2_V1= Beta('B_RACE_2_V1', 0, None, None, 0)
B_RACE_2_V2= Beta('B_RACE_2_V2', 0, None, None, 0)
B_RACE_2_V3= Beta('B_RACE_2_V3', 0, None, None, 0)
###
B_RACE_3_V0= Beta('B_RACE_3_V0', 0, None, None, 1)
B_RACE_3_V1= Beta('B_RACE_3_V1', 0, None, None, 0)
B_RACE_3_V2= Beta('B_RACE_3_V2', 0, None, None, 0)
B_RACE_3_V3= Beta('B_RACE_3_V3', 0, None, None, 0)

###
B_CENSUS_R_2_V0= Beta('B_CENSUS_R_2_V0', 0, None, None, 1)
B_CENSUS_R_2_V1= Beta('B_CENSUS_R_2_V1', 0, None, None, 0)
B_CENSUS_R_2_V2= Beta('B_CENSUS_R_2_V2', 0, None, None, 0)
B_CENSUS_R_2_V3= Beta('B_CENSUS_R_2_V3', 0, None, None, 0)
###
B_CENSUS_R_3_V0= Beta('B_CENSUS_R_3_V0', 0, None, None, 1)
B_CENSUS_R_3_V1= Beta('B_CENSUS_R_3_V1', 0, None, None, 0)
B_CENSUS_R_3_V2= Beta('B_CENSUS_R_3_V2', 0, None, None, 0)
B_CENSUS_R_3_V3= Beta('B_CENSUS_R_3_V3', 0, None, None, 0)
##
B_CENSUS_R_4_V0= Beta('B_CENSUS_R_4_V0', 0, None, None, 1)
B_CENSUS_R_4_V1= Beta('B_CENSUS_R_4_V1', 0, None, None, 0)
B_CENSUS_R_4_V2= Beta('B_CENSUS_R_4_V2', 0, None, None, 0)
B_CENSUS_R_4_V3= Beta('B_CENSUS_R_4_V3', 0, None, None, 0)

###

Prob_no_V1= Beta('Prob_no_V1', 0, None, None, 0)
Prob_no_V2= Beta('Prob_no_V2', 0, None, None, 0)
Prob_no_V3= Beta('Prob_no_V3', 0, None, None, 0)

#Prob_lo_V0= Beta('Prob_lo_V0', 0, None, None, 1)
Prob_lo_V1= Beta('Prob_lo_V1', 0, None, None, 0)
Prob_lo_V2= Beta('Prob_lo_V2', 0, None, None, 0)
Prob_lo_V3= Beta('Prob_lo_V3', 0, None, None, 0)
###
#Prob_md_V0= Beta('Prob_md_V0', 0, None, None, 1)
Prob_md_V1= Beta('Prob_md_V1', 0, None, None, 0)
Prob_md_V2= Beta('Prob_md_V2', 0, None, None, 0)
Prob_md_V3= Beta('Prob_md_V3', 0, None, None, 0)
##
#Prob_hi_V0= Beta('Prob_hi_V0', 0, None, None, 1)
Prob_hi_V1= Beta('Prob_hi_V1', 0, None, None, 0)
Prob_hi_V2= Beta('Prob_hi_V2', 0, None, None, 0)
Prob_hi_V3= Beta('Prob_hi_V3', 0, None, None, 0)


# Definition of the utility functions
V0 = ASC_NOS + B_SEX_V0 * R_SEX_IMP + B_HHSIZE_V0 * HHSIZE + B_WORKER_V0 *WORKER + B_EDUC_0_V0 *EDUC_0 +B_AGE_IMP_3_V0 *R_AGE_IMP_3 +\
    B_MSACAT_V0 *MSACAT + B_INC_V0 * income_val
V1 = ASC_OFF + B_SEX_V1 * R_SEX_IMP + B_HHSIZE_V1 * HHSIZE + B_WORKER_V1 *WORKER + \
   B_MSACAT_V1 *MSACAT + B_INC_V1 * income_val +Prob_no_V1*Prob_no+Prob_lo_V1*Prob_lo+Prob_md_V1*Prob_no+Prob_md_V1*Prob_md +Prob_hi_V1*Prob_hi
V2 = ASC_ONS + B_SEX_V2 * R_SEX_IMP + B_HHSIZE_V2 * HHSIZE + B_WORKER_V2 *WORKER +\
     B_MSACAT_V2 *MSACAT + B_INC_V2 * income_val +Prob_no_V2*Prob_no+Prob_lo_V2*Prob_lo+Prob_md_V2*Prob_no+Prob_md_V2*Prob_md +Prob_hi_V2*Prob_hi
V3 = ASC_BOT + B_SEX_V3 * R_SEX_IMP + B_HHSIZE_V3 * HHSIZE + B_WORKER_V3 *WORKER +\
   B_MSACAT_V3 *MSACAT+ B_INC_V3 * income_val +Prob_no_V3*Prob_no+Prob_lo_V3*Prob_lo+Prob_md_V3*Prob_no+Prob_md_V3*Prob_md +Prob_hi_V3*Prob_hi
# Associate utility functions with the numbering of alternatives
# Associate utility functions with the numbering of alternatives
V = {0: V0,1: V1, 2: V2, 3: V3}

# Associate the availability conditions with the alternatives
av = {0: Avail, 1: Avail, 2: Avail, 3: Avail}

# nest parameters
NEST_SHOP=Beta('NEST_SHOP',1,None,None,0)

NO_SHOP =1.0, [0]
SHOP=NEST_SHOP, [1,2,3]

nests = NO_SHOP, SHOP
# Definition of the model. This is the contribution of each
# observation to the log likelihood function.
logprob = models.lognested(V, av, nests, shop_choice)

# Define level of verbosity
logger = msg.bioMessage()
# logger.setSilent()
# logger.setWarning()
logger.setGeneral()
# logger.setDetailed()

# Create the Biogeme object
formulas = {'loglike': logprob, 'weight': TUFINLWGT}
biogeme = bio.BIOGEME(database, formulas)
biogeme.modelName = "shoping_nested"


# Create the Biogeme object
#logprob = models.loglogit(V, av, shop_choice)
# formulas = {'loglike': logprob, 'weight': TUFINLWGT}
# biogeme = bio.BIOGEME(database, formulas)
# biogeme.modelName = 'shopping_MNL'

# Calculate the null log likelihood for reporting.
biogeme.calculateNullLoglikelihood(av)

# Estimate the parameters
results = biogeme.estimate()
pandasResults = results.getEstimatedParameters()
print(pandasResults)


# %%
# result 6, 7
############################################# Model estimation ################################
## shopping nested 
database = db.Database('shop', atus_df)

# The following statement allows you to use the names of the
# variable as Python variable.
globals().update(database.variables)

# Parameters to be estimated
## Intercept
ASC_NOS = Beta('ASC_NOS', 0, None, None, 1)
ASC_OFF = Beta('ASC_OFF', 0, None, None, 0)
ASC_ONS = Beta('ASC_ONS', 0, None, None, 0)
ASC_BOT = Beta('ASC_BOT', 0, None, None, 0)
## Beta
B_SEX_V0= Beta('B_SEX_V0', 0, None, None, 1)
B_SEX_V1= Beta('B_SEX_V1', 0, None, None, 0)
B_SEX_V2= Beta('B_SEX_V2', 0, None, None, 0)
B_SEX_V3= Beta('B_SEX_V3', 0, None, None, 0)

## Beta
B_INC_V0= Beta('B_INC_V0', 0, None, None, 1)
B_INC_V1= Beta('B_INC_V1', 0, None, None, 0)
B_INC_V2= Beta('B_INC_V2', 0, None, None, 0)
B_INC_V3= Beta('B_INC_V3', 0, None, None, 0)
###
B_HHSIZE_V0= Beta('B_HHSIZE_V0', 0, None, None, 1)
B_HHSIZE_V1= Beta('B_HHSIZE_V1', 0, None, None, 0)
B_HHSIZE_V2= Beta('B_HHSIZE_V2', 0, None, None, 0)
B_HHSIZE_V3= Beta('B_HHSIZE_V3', 0, None, None, 0)
###
B_WORKER_V0= Beta('B_WORKER_V0', 0, None, None, 1)
B_WORKER_V1= Beta('B_WORKER_V1', 0, None, None, 0)
B_WORKER_V2= Beta('B_WORKER_V2', 0, None, None, 0)
B_WORKER_V3= Beta('B_WORKER_V3', 0, None, None, 0)

###
B_MSACAT_V0= Beta('B_MSACAT_V0', 0, None, None, 1)
B_MSACAT_V1= Beta('B_MSACAT_V1', 0, None, None, 0)
B_MSACAT_V2= Beta('B_MSACAT_V2', 0, None, None, 0)
B_MSACAT_V3= Beta('B_MSACAT_V3', 0, None, None, 0)
###
B_EDUC_1_V0= Beta('B_EDUC_1_V0', 0, None, None, 0)
B_EDUC_1_V1= Beta('B_EDUC_1_V1', 0, None, None, 0)
B_EDUC_1_V2= Beta('B_EDUC_1_V2', 0, None, None, 0)
B_EDUC_1_V3= Beta('B_EDUC_1_V3', 0, None, None, 0)
###
B_EDUC_2_V0= Beta('B_EDUC_2_V0', 0, None, None, 0)
B_EDUC_2_V1= Beta('B_EDUC_2_V1', 0, None, None, 0)
B_EDUC_2_V2= Beta('B_EDUC_2_V2', 0, None, None, 0)
B_EDUC_2_V3= Beta('B_EDUC_2_V3', 0, None, None, 0)
###
B_EDUC_3_V0= Beta('B_EDUC_3_V0', 0, None, None, 0)
B_EDUC_3_V1= Beta('B_EDUC_3_V1', 0, None, None, 0)
B_EDUC_3_V2= Beta('B_EDUC_3_V2', 0, None, None, 0)
B_EDUC_3_V3= Beta('B_EDUC_3_V3', 0, None, None, 0)

###
B_AGE_IMP_1_V0= Beta('B_AGE_IMP_1_V0', 0, None, None, 0)
B_AGE_IMP_1_V1= Beta('B_AGE_IMP_1_V1', 0, None, None, 0)
B_AGE_IMP_1_V2= Beta('B_AGE_IMP_1_V2', 0, None, None, 0)
B_AGE_IMP_1_V3= Beta('B_AGE_IMP_1_V3', 0, None, None, 0)

###
B_AGE_IMP_2_V0= Beta('B_AGE_IMP_2_V0', 0, None, None, 0)
B_AGE_IMP_2_V1= Beta('B_AGE_IMP_2_V1', 0, None, None, 0)
B_AGE_IMP_2_V2= Beta('B_AGE_IMP_2_V2', 0, None, None, 0)
B_AGE_IMP_2_V3= Beta('B_AGE_IMP_2_V3', 0, None, None, 0)
###
B_AGE_IMP_3_V0= Beta('B_AGE_IMP_3_V0', 0, None, None, 0)
B_AGE_IMP_3_V1= Beta('B_AGE_IMP_3_V1', 0, None, None, 0)
B_AGE_IMP_3_V2= Beta('B_AGE_IMP_3_V2', 0, None, None, 0)
B_AGE_IMP_3_V3= Beta('B_AGE_IMP_3_V3', 0, None, None, 0)
###
###
B_RACE_1_V0= Beta('B_RACE_1_V0', 0, None, None, 1)
B_RACE_1_V1= Beta('B_RACE_1_V1', 0, None, None, 0)
B_RACE_1_V2= Beta('B_RACE_1_V2', 0, None, None, 0)
B_RACE_1_V3= Beta('B_RACE_1_V3', 0, None, None, 0)

###
B_RACE_2_V0= Beta('B_RACE_2_V0', 0, None, None, 1)
B_RACE_2_V1= Beta('B_RACE_2_V1', 0, None, None, 0)
B_RACE_2_V2= Beta('B_RACE_2_V2', 0, None, None, 0)
B_RACE_2_V3= Beta('B_RACE_2_V3', 0, None, None, 0)
###
B_RACE_3_V0= Beta('B_RACE_3_V0', 0, None, None, 1)
B_RACE_3_V1= Beta('B_RACE_3_V1', 0, None, None, 0)
B_RACE_3_V2= Beta('B_RACE_3_V2', 0, None, None, 0)
B_RACE_3_V3= Beta('B_RACE_3_V3', 0, None, None, 0)

###
B_CENSUS_R_2_V0= Beta('B_CENSUS_R_2_V0', 0, None, None, 1)
B_CENSUS_R_2_V1= Beta('B_CENSUS_R_2_V1', 0, None, None, 1)
B_CENSUS_R_2_V2= Beta('B_CENSUS_R_2_V2', 0, None, None, 0)
B_CENSUS_R_2_V3= Beta('B_CENSUS_R_2_V3', 0, None, None, 0)
###
B_CENSUS_R_3_V0= Beta('B_CENSUS_R_3_V0', 0, None, None, 1)
B_CENSUS_R_3_V1= Beta('B_CENSUS_R_3_V1', 0, None, None, 1)
B_CENSUS_R_3_V2= Beta('B_CENSUS_R_3_V2', 0, None, None, 0)
B_CENSUS_R_3_V3= Beta('B_CENSUS_R_3_V3', 0, None, None, 0)
##
B_CENSUS_R_4_V0= Beta('B_CENSUS_R_4_V0', 0, None, None, 1)
B_CENSUS_R_4_V1= Beta('B_CENSUS_R_4_V1', 0, None, None, 1)
B_CENSUS_R_4_V2= Beta('B_CENSUS_R_4_V2', 0, None, None, 0)
B_CENSUS_R_4_V3= Beta('B_CENSUS_R_4_V3', 0, None, None, 0)

###

Prob_no_V1= Beta('Prob_no_V1', 0, None, None, 1)
Prob_no_V2= Beta('Prob_no_V2', 0, None, None, 0)
Prob_no_V3= Beta('Prob_no_V3', 0, None, None, 0)

#Prob_lo_V0= Beta('Prob_lo_V0', 0, None, None, 1)
Prob_lo_V1= Beta('Prob_lo_V1', 0, None, None, 1)
Prob_lo_V2= Beta('Prob_lo_V2', 0, None, None, 0)
Prob_lo_V3= Beta('Prob_lo_V3', 0, None, None, 0)
###
#Prob_md_V0= Beta('Prob_md_V0', 0, None, None, 1)
Prob_md_V1= Beta('Prob_md_V1', 0, None, None, 1)
Prob_md_V2= Beta('Prob_md_V2', 0, None, None, 0)
Prob_md_V3= Beta('Prob_md_V3', 0, None, None, 0)
##
#Prob_hi_V0= Beta('Prob_hi_V0', 0, None, None, 1)
Prob_hi_V1= Beta('Prob_hi_V1', 0, None, None, 1)
Prob_hi_V2= Beta('Prob_hi_V2', 0, None, None, 0)
Prob_hi_V3= Beta('Prob_hi_V3', 0, None, None, 0)


# Definition of the utility functions
V0 = ASC_NOS + B_SEX_V0 * R_SEX_IMP + B_HHSIZE_V0 * HHSIZE + B_WORKER_V0 *WORKER + B_EDUC_1_V0 *EDUC_1 + B_EDUC_2_V0 *EDUC_2 + B_EDUC_3_V0 *EDUC_3 + B_AGE_IMP_1_V0 *R_AGE_IMP_1+ B_AGE_IMP_2_V0 *R_AGE_IMP_2+B_AGE_IMP_3_V0 *R_AGE_IMP_3+\
    B_MSACAT_V0 *MSACAT + B_INC_V0 * income_val
V1 = ASC_OFF + B_SEX_V1 * R_SEX_IMP + B_HHSIZE_V1 * HHSIZE + B_WORKER_V1 *WORKER + \
   B_CENSUS_R_2_V1 *CENSUS_R_2 +B_CENSUS_R_3_V1 *CENSUS_R_3+B_CENSUS_R_4_V1 *CENSUS_R_4 +B_MSACAT_V1 *MSACAT + B_INC_V1 * income_val +Prob_no_V1*Prob_no+Prob_lo_V1*Prob_lo+Prob_md_V1*Prob_no+Prob_md_V1*Prob_md +Prob_hi_V1*Prob_hi
V2 = ASC_ONS + B_SEX_V2 * R_SEX_IMP + B_HHSIZE_V2 * HHSIZE + B_WORKER_V2 *WORKER +\
    B_CENSUS_R_2_V2 *CENSUS_R_2 +B_CENSUS_R_3_V2 *CENSUS_R_3+B_CENSUS_R_4_V2 *CENSUS_R_4 +B_MSACAT_V2 *MSACAT + B_INC_V2 * income_val +Prob_no_V2*Prob_no+Prob_lo_V2*Prob_lo+Prob_md_V2*Prob_no+Prob_md_V2*Prob_md +Prob_hi_V2*Prob_hi
V3 = ASC_BOT + B_SEX_V3 * R_SEX_IMP + B_HHSIZE_V3 * HHSIZE + B_WORKER_V3 *WORKER +\
   B_CENSUS_R_2_V3 *CENSUS_R_2 +B_CENSUS_R_3_V3 *CENSUS_R_3+B_CENSUS_R_4_V3 *CENSUS_R_4 +B_MSACAT_V3 *MSACAT+ B_INC_V3 * income_val +Prob_no_V3*Prob_no+Prob_lo_V3*Prob_lo+Prob_md_V3*Prob_no+Prob_md_V3*Prob_md +Prob_hi_V3*Prob_hi
# Associate utility functions with the numbering of alternatives
# Associate utility functions with the numbering of alternatives
V = {0: V0,1: V1, 2: V2, 3: V3}

# Associate the availability conditions with the alternatives
av = {0: Avail, 1: Avail, 2: Avail, 3: Avail}

# nest parameters
NEST_SHOP=Beta('NEST_SHOP',1,None,None,0)

NO_SHOP =1.0, [0]
SHOP=NEST_SHOP, [1,2,3]

nests = NO_SHOP, SHOP
# Definition of the model. This is the contribution of each
# observation to the log likelihood function.
logprob = models.lognested(V, av, nests, shop_choice)

# Define level of verbosity
logger = msg.bioMessage()
# logger.setSilent()
# logger.setWarning()
logger.setGeneral()
# logger.setDetailed()

# Create the Biogeme object
formulas = {'loglike': logprob, 'weight': TUFINLWGT}
biogeme = bio.BIOGEME(database, formulas)
biogeme.modelName = "shoping_nested"


# Create the Biogeme object
#logprob = models.loglogit(V, av, shop_choice)
# formulas = {'loglike': logprob, 'weight': TUFINLWGT}
# biogeme = bio.BIOGEME(database, formulas)
# biogeme.modelName = 'shopping_MNL'

# Calculate the null log likelihood for reporting.
biogeme.calculateNullLoglikelihood(av)

# Estimate the parameters
results = biogeme.estimate()
pandasResults = results.getEstimatedParameters()
print(pandasResults)






# %%
############################################# Model estimation ################################
## shopping nested 
database = db.Database('shop', atus_df)

# The following statement allows you to use the names of the
# variable as Python variable.
globals().update(database.variables)

# Parameters to be estimated
## Intercept
ASC_NOS = Beta('ASC_NOS', 0, None, None, 1)
ASC_OFF = Beta('ASC_OFF', 0, None, None, 0)
ASC_ONS = Beta('ASC_ONS', 0, None, None, 0)
ASC_BOT = Beta('ASC_BOT', 0, None, None, 0)
## Beta
B_SEX_V0= Beta('B_SEX_V0', 0, None, None, 1)
B_SEX_V1= Beta('B_SEX_V1', 0, None, None, 0)
B_SEX_V2= Beta('B_SEX_V2', 0, None, None, 0)
B_SEX_V3= Beta('B_SEX_V3', 0, None, None, 0)

## Beta
B_INC_V0= Beta('B_INC_V0', 0, None, None, 1)
B_INC_V1= Beta('B_INC_V1', 0, None, None, 0)
B_INC_V2= Beta('B_INC_V2', 0, None, None, 0)
B_INC_V3= Beta('B_INC_V3', 0, None, None, 0)
###
B_HHSIZE_V0= Beta('B_HHSIZE_V0', 0, None, None, 1)
B_HHSIZE_V1= Beta('B_HHSIZE_V1', 0, None, None, 0)
B_HHSIZE_V2= Beta('B_HHSIZE_V2', 0, None, None, 0)
B_HHSIZE_V3= Beta('B_HHSIZE_V3', 0, None, None, 0)
###
B_WORKER_V0= Beta('B_WORKER_V0', 0, None, None, 1)
B_WORKER_V1= Beta('B_WORKER_V1', 0, None, None, 0)
B_WORKER_V2= Beta('B_WORKER_V2', 0, None, None, 0)
B_WORKER_V3= Beta('B_WORKER_V3', 0, None, None, 0)

###
B_MSACAT_V0= Beta('B_MSACAT_V0', 0, None, None, 1)
B_MSACAT_V1= Beta('B_MSACAT_V1', 0, None, None, 0)
B_MSACAT_V2= Beta('B_MSACAT_V2', 0, None, None, 0)
B_MSACAT_V3= Beta('B_MSACAT_V3', 0, None, None, 0)
###
B_EDUC_1_V0= Beta('B_EDUC_1_V0', 0, None, None, 1)
B_EDUC_1_V1= Beta('B_EDUC_1_V1', 0, None, None, 0)
B_EDUC_1_V2= Beta('B_EDUC_1_V2', 0, None, None, 0)
B_EDUC_1_V3= Beta('B_EDUC_1_V3', 0, None, None, 0)
###
B_EDUC_2_V0= Beta('B_EDUC_2_V0', 0, None, None, 1)
B_EDUC_2_V1= Beta('B_EDUC_2_V1', 0, None, None, 0)
B_EDUC_2_V2= Beta('B_EDUC_2_V2', 0, None, None, 0)
B_EDUC_2_V3= Beta('B_EDUC_2_V3', 0, None, None, 0)
###
B_EDUC_3_V0= Beta('B_EDUC_3_V0', 0, None, None, 1)
B_EDUC_3_V1= Beta('B_EDUC_3_V1', 0, None, None, 0)
B_EDUC_3_V2= Beta('B_EDUC_3_V2', 0, None, None, 0)
B_EDUC_3_V3= Beta('B_EDUC_3_V3', 0, None, None, 0)

###
B_AGE_IMP_1_V0= Beta('B_AGE_IMP_1_V0', 0, None, None, 1)
B_AGE_IMP_1_V1= Beta('B_AGE_IMP_1_V1', 0, None, None, 0)
B_AGE_IMP_1_V2= Beta('B_AGE_IMP_1_V2', 0, None, None, 0)
B_AGE_IMP_1_V3= Beta('B_AGE_IMP_1_V3', 0, None, None, 0)

###
B_AGE_IMP_2_V0= Beta('B_AGE_IMP_2_V0', 0, None, None, 1)
B_AGE_IMP_2_V1= Beta('B_AGE_IMP_2_V1', 0, None, None, 0)
B_AGE_IMP_2_V2= Beta('B_AGE_IMP_2_V2', 0, None, None, 0)
B_AGE_IMP_2_V3= Beta('B_AGE_IMP_2_V3', 0, None, None, 0)
###
B_AGE_IMP_3_V0= Beta('B_AGE_IMP_3_V0', 0, None, None, 1)
B_AGE_IMP_3_V1= Beta('B_AGE_IMP_3_V1', 0, None, None, 0)
B_AGE_IMP_3_V2= Beta('B_AGE_IMP_3_V2', 0, None, None, 0)
B_AGE_IMP_3_V3= Beta('B_AGE_IMP_3_V3', 0, None, None, 0)
###
###
B_RACE_1_V0= Beta('B_RACE_1_V0', 0, None, None, 1)
B_RACE_1_V1= Beta('B_RACE_1_V1', 0, None, None, 0)
B_RACE_1_V2= Beta('B_RACE_1_V2', 0, None, None, 0)
B_RACE_1_V3= Beta('B_RACE_1_V3', 0, None, None, 0)

###
B_RACE_2_V0= Beta('B_RACE_2_V0', 0, None, None, 1)
B_RACE_2_V1= Beta('B_RACE_2_V1', 0, None, None, 0)
B_RACE_2_V2= Beta('B_RACE_2_V2', 0, None, None, 0)
B_RACE_2_V3= Beta('B_RACE_2_V3', 0, None, None, 0)
###
B_RACE_3_V0= Beta('B_RACE_3_V0', 0, None, None, 1)
B_RACE_3_V1= Beta('B_RACE_3_V1', 0, None, None, 0)
B_RACE_3_V2= Beta('B_RACE_3_V2', 0, None, None, 0)
B_RACE_3_V3= Beta('B_RACE_3_V3', 0, None, None, 0)

###
B_CENSUS_R_2_V0= Beta('B_CENSUS_R_2_V0', 0, None, None, 1)
B_CENSUS_R_2_V1= Beta('B_CENSUS_R_2_V1', 0, None, None, 0)
B_CENSUS_R_2_V2= Beta('B_CENSUS_R_2_V2', 0, None, None, 0)
B_CENSUS_R_2_V3= Beta('B_CENSUS_R_2_V3', 0, None, None, 0)
###
B_CENSUS_R_3_V0= Beta('B_CENSUS_R_3_V0', 0, None, None, 1)
B_CENSUS_R_3_V1= Beta('B_CENSUS_R_3_V1', 0, None, None, 0)
B_CENSUS_R_3_V2= Beta('B_CENSUS_R_3_V2', 0, None, None, 0)
B_CENSUS_R_3_V3= Beta('B_CENSUS_R_3_V3', 0, None, None, 0)
##
B_CENSUS_R_4_V0= Beta('B_CENSUS_R_4_V0', 0, None, None, 1)
B_CENSUS_R_4_V1= Beta('B_CENSUS_R_4_V1', 0, None, None, 0)
B_CENSUS_R_4_V2= Beta('B_CENSUS_R_4_V2', 0, None, None, 0)
B_CENSUS_R_4_V3= Beta('B_CENSUS_R_4_V3', 0, None, None, 0)

###

Prob_no_V1= Beta('Prob_no_V1', 0, None, None, 1)
Prob_no_V2= Beta('Prob_no_V2', 0, None, None, 0)
Prob_no_V3= Beta('Prob_no_V3', 0, None, None, 0)

#Prob_lo_V0= Beta('Prob_lo_V0', 0, None, None, 1)
Prob_lo_V1= Beta('Prob_lo_V1', 0, None, None, 1)
Prob_lo_V2= Beta('Prob_lo_V2', 0, None, None, 0)
Prob_lo_V3= Beta('Prob_lo_V3', 0, None, None, 0)
###
#Prob_md_V0= Beta('Prob_md_V0', 0, None, None, 1)
Prob_md_V1= Beta('Prob_md_V1', 0, None, None, 1)
Prob_md_V2= Beta('Prob_md_V2', 0, None, None, 0)
Prob_md_V3= Beta('Prob_md_V3', 0, None, None, 0)
##
#Prob_hi_V0= Beta('Prob_hi_V0', 0, None, None, 1)
Prob_hi_V1= Beta('Prob_hi_V1', 0, None, None, 1)
Prob_hi_V2= Beta('Prob_hi_V2', 0, None, None, 0)
Prob_hi_V3= Beta('Prob_hi_V3', 0, None, None, 0)


# Definition of the utility functions
V0 = ASC_NOS + B_SEX_V0 * R_SEX_IMP + B_HHSIZE_V0 * HHSIZE + B_WORKER_V0 *WORKER + B_EDUC_1_V0 *EDUC_1 + B_EDUC_2_V0 *EDUC_2 + B_EDUC_3_V0 *EDUC_3 + B_AGE_IMP_1_V0 *R_AGE_IMP_1+ B_AGE_IMP_2_V0 *R_AGE_IMP_2+B_AGE_IMP_3_V0 *R_AGE_IMP_3+\
   B_RACE_1_V0 *R_RACE_1+B_RACE_2_V0 *R_RACE_2 +B_MSACAT_V0 *MSACAT + B_INC_V0 * income_val
V1 = ASC_OFF + B_SEX_V1 * R_SEX_IMP + B_HHSIZE_V1 * HHSIZE + B_WORKER_V1 *WORKER + \
   B_CENSUS_R_2_V1 *CENSUS_R_2 +B_CENSUS_R_3_V1 *CENSUS_R_3+B_CENSUS_R_4_V1 *CENSUS_R_4 +B_MSACAT_V1 *MSACAT + B_INC_V1 * income_val +Prob_no_V1*Prob_no+Prob_lo_V1*Prob_lo+Prob_md_V1*Prob_no+Prob_md_V1*Prob_md +Prob_hi_V1*Prob_hi
V2 = ASC_ONS + B_SEX_V2 * R_SEX_IMP + B_HHSIZE_V2 * HHSIZE + B_WORKER_V2 *WORKER +\
    B_CENSUS_R_2_V2 *CENSUS_R_2 +B_CENSUS_R_3_V2 *CENSUS_R_3+B_CENSUS_R_4_V2 *CENSUS_R_4 +B_MSACAT_V2 *MSACAT + B_INC_V2 * income_val +Prob_no_V2*Prob_no+Prob_lo_V2*Prob_lo+Prob_md_V2*Prob_no+Prob_md_V2*Prob_md +Prob_hi_V2*Prob_hi
V3 = ASC_BOT + B_SEX_V3 * R_SEX_IMP + B_HHSIZE_V3 * HHSIZE + B_WORKER_V3 *WORKER +\
   B_CENSUS_R_2_V3 *CENSUS_R_2 +B_CENSUS_R_3_V3 *CENSUS_R_3+B_CENSUS_R_4_V3 *CENSUS_R_4 +B_MSACAT_V3 *MSACAT+ B_INC_V3 * income_val +Prob_no_V3*Prob_no+Prob_lo_V3*Prob_lo+Prob_md_V3*Prob_no+Prob_md_V3*Prob_md +Prob_hi_V3*Prob_hi
# Associate utility functions with the numbering of alternatives
# Associate utility functions with the numbering of alternatives
V = {0: V0,1: V1, 2: V2, 3: V3}

# Associate the availability conditions with the alternatives
av = {0: Avail, 1: Avail, 2: Avail, 3: Avail}

# nest parameters
NEST_SHOP=Beta('NEST_SHOP',1,None,None,0)

NO_SHOP =1.0, [0]
SHOP=NEST_SHOP, [1,2,3]

nests = NO_SHOP, SHOP
# Definition of the model. This is the contribution of each
# observation to the log likelihood function.
logprob = models.lognested(V, av, nests, shop_choice)

# Define level of verbosity
logger = msg.bioMessage()
# logger.setSilent()
# logger.setWarning()
logger.setGeneral()
# logger.setDetailed()

# Create the Biogeme object
formulas = {'loglike': logprob, 'weight': TUFINLWGT}
biogeme = bio.BIOGEME(database, formulas)
biogeme.modelName = "shoping_nested"


# Create the Biogeme object
#logprob = models.loglogit(V, av, shop_choice)
# formulas = {'loglike': logprob, 'weight': TUFINLWGT}
# biogeme = bio.BIOGEME(database, formulas)
# biogeme.modelName = 'shopping_MNL'

# Calculate the null log likelihood for reporting.
biogeme.calculateNullLoglikelihood(av)

# Estimate the parameters
results = biogeme.estimate()
pandasResults = results.getEstimatedParameters()
print(pandasResults)

# %%
############################################# Model estimation ################################
## shopping nested 
database = db.Database('shop', atus_df)

# The following statement allows you to use the names of the
# variable as Python variable.
globals().update(database.variables)

# Parameters to be estimated
## Intercept
ASC_NOS = Beta('ASC_NOS', 0, None, None, 1)
ASC_OFF = Beta('ASC_OFF', 0, None, None, 0)
ASC_ONS = Beta('ASC_ONS', 0, None, None, 0)
ASC_BOT = Beta('ASC_BOT', 0, None, None, 0)
## Beta
B_SEX_V0= Beta('B_SEX_V0', 0, None, None, 1)
B_SEX_V1= Beta('B_SEX_V1', 0, None, None, 0)
B_SEX_V2= Beta('B_SEX_V2', 0, None, None, 0)
B_SEX_V3= Beta('B_SEX_V3', 0, None, None, 0)

## Beta
B_INC_V0= Beta('B_INC_V0', 0, None, None, 1)
B_INC_V1= Beta('B_INC_V1', 0, None, None, 0)
B_INC_V2= Beta('B_INC_V2', 0, None, None, 0)
B_INC_V3= Beta('B_INC_V3', 0, None, None, 0)
###
B_HHSIZE_V0= Beta('B_HHSIZE_V0', 0, None, None, 1)
B_HHSIZE_V1= Beta('B_HHSIZE_V1', 0, None, None, 0)
B_HHSIZE_V2= Beta('B_HHSIZE_V2', 0, None, None, 0)
B_HHSIZE_V3= Beta('B_HHSIZE_V3', 0, None, None, 0)
###
B_WORKER_V0= Beta('B_WORKER_V0', 0, None, None, 1)
B_WORKER_V1= Beta('B_WORKER_V1', 0, None, None, 0)
B_WORKER_V2= Beta('B_WORKER_V2', 0, None, None, 0)
B_WORKER_V3= Beta('B_WORKER_V3', 0, None, None, 0)

###
B_MSACAT_V0= Beta('B_MSACAT_V0', 0, None, None, 1)
B_MSACAT_V1= Beta('B_MSACAT_V1', 0, None, None, 0)
B_MSACAT_V2= Beta('B_MSACAT_V2', 0, None, None, 0)
B_MSACAT_V3= Beta('B_MSACAT_V3', 0, None, None, 0)
###
B_EDUC_1_V0= Beta('B_EDUC_1_V0', 0, None, None, 1)
B_EDUC_1_V1= Beta('B_EDUC_1_V1', 0, None, None, 0)
B_EDUC_1_V2= Beta('B_EDUC_1_V2', 0, None, None, 0)
B_EDUC_1_V3= Beta('B_EDUC_1_V3', 0, None, None, 0)
###
B_EDUC_2_V0= Beta('B_EDUC_2_V0', 0, None, None, 1)
B_EDUC_2_V1= Beta('B_EDUC_2_V1', 0, None, None, 0)
B_EDUC_2_V2= Beta('B_EDUC_2_V2', 0, None, None, 0)
B_EDUC_2_V3= Beta('B_EDUC_2_V3', 0, None, None, 0)
###
B_EDUC_3_V0= Beta('B_EDUC_3_V0', 0, None, None, 1)
B_EDUC_3_V1= Beta('B_EDUC_3_V1', 0, None, None, 0)
B_EDUC_3_V2= Beta('B_EDUC_3_V2', 0, None, None, 0)
B_EDUC_3_V3= Beta('B_EDUC_3_V3', 0, None, None, 0)

###
B_AGE_IMP_1_V0= Beta('B_AGE_IMP_1_V0', 0, None, None, 1)
B_AGE_IMP_1_V1= Beta('B_AGE_IMP_1_V1', 0, None, None, 0)
B_AGE_IMP_1_V2= Beta('B_AGE_IMP_1_V2', 0, None, None, 0)
B_AGE_IMP_1_V3= Beta('B_AGE_IMP_1_V3', 0, None, None, 0)

###
B_AGE_IMP_2_V0= Beta('B_AGE_IMP_2_V0', 0, None, None, 1)
B_AGE_IMP_2_V1= Beta('B_AGE_IMP_2_V1', 0, None, None, 0)
B_AGE_IMP_2_V2= Beta('B_AGE_IMP_2_V2', 0, None, None, 0)
B_AGE_IMP_2_V3= Beta('B_AGE_IMP_2_V3', 0, None, None, 0)
###
B_AGE_IMP_3_V0= Beta('B_AGE_IMP_3_V0', 0, None, None, 1)
B_AGE_IMP_3_V1= Beta('B_AGE_IMP_3_V1', 0, None, None, 0)
B_AGE_IMP_3_V2= Beta('B_AGE_IMP_3_V2', 0, None, None, 0)
B_AGE_IMP_3_V3= Beta('B_AGE_IMP_3_V3', 0, None, None, 0)
###
###
B_RACE_1_V0= Beta('B_RACE_1_V0', 0, None, None, 1)
B_RACE_1_V1= Beta('B_RACE_1_V1', 0, None, None, 0)
B_RACE_1_V2= Beta('B_RACE_1_V2', 0, None, None, 0)
B_RACE_1_V3= Beta('B_RACE_1_V3', 0, None, None, 0)

###
B_RACE_2_V0= Beta('B_RACE_2_V0', 0, None, None, 1)
B_RACE_2_V1= Beta('B_RACE_2_V1', 0, None, None, 0)
B_RACE_2_V2= Beta('B_RACE_2_V2', 0, None, None, 0)
B_RACE_2_V3= Beta('B_RACE_2_V3', 0, None, None, 0)
###
B_RACE_3_V0= Beta('B_RACE_3_V0', 0, None, None, 1)
B_RACE_3_V1= Beta('B_RACE_3_V1', 0, None, None, 0)
B_RACE_3_V2= Beta('B_RACE_3_V2', 0, None, None, 0)
B_RACE_3_V3= Beta('B_RACE_3_V3', 0, None, None, 0)

###
B_CENSUS_R_2_V0= Beta('B_CENSUS_R_2_V0', 0, None, None, 1)
B_CENSUS_R_2_V1= Beta('B_CENSUS_R_2_V1', 0, None, None, 0)
B_CENSUS_R_2_V2= Beta('B_CENSUS_R_2_V2', 0, None, None, 0)
B_CENSUS_R_2_V3= Beta('B_CENSUS_R_2_V3', 0, None, None, 0)
###
B_CENSUS_R_3_V0= Beta('B_CENSUS_R_3_V0', 0, None, None, 1)
B_CENSUS_R_3_V1= Beta('B_CENSUS_R_3_V1', 0, None, None, 0)
B_CENSUS_R_3_V2= Beta('B_CENSUS_R_3_V2', 0, None, None, 0)
B_CENSUS_R_3_V3= Beta('B_CENSUS_R_3_V3', 0, None, None, 0)
##
B_CENSUS_R_4_V0= Beta('B_CENSUS_R_4_V0', 0, None, None, 1)
B_CENSUS_R_4_V1= Beta('B_CENSUS_R_4_V1', 0, None, None, 0)
B_CENSUS_R_4_V2= Beta('B_CENSUS_R_4_V2', 0, None, None, 0)
B_CENSUS_R_4_V3= Beta('B_CENSUS_R_4_V3', 0, None, None, 0)

###

Prob_no_V1= Beta('Prob_no_V1', 0, None, None, 1)
Prob_no_V2= Beta('Prob_no_V2', 0, None, None, 0)
Prob_no_V3= Beta('Prob_no_V3', 0, None, None, 0)

#Prob_lo_V0= Beta('Prob_lo_V0', 0, None, None, 1)
Prob_lo_V1= Beta('Prob_lo_V1', 0, None, None, 1)
Prob_lo_V2= Beta('Prob_lo_V2', 0, None, None, 0)
Prob_lo_V3= Beta('Prob_lo_V3', 0, None, None, 0)
###
#Prob_md_V0= Beta('Prob_md_V0', 0, None, None, 1)
Prob_md_V1= Beta('Prob_md_V1', 0, None, None, 1)
Prob_md_V2= Beta('Prob_md_V2', 0, None, None, 0)
Prob_md_V3= Beta('Prob_md_V3', 0, None, None, 0)
##
#Prob_hi_V0= Beta('Prob_hi_V0', 0, None, None, 1)
Prob_hi_V1= Beta('Prob_hi_V1', 0, None, None, 1)
Prob_hi_V2= Beta('Prob_hi_V2', 0, None, None, 0)
Prob_hi_V3= Beta('Prob_hi_V3', 0, None, None, 0)


# Definition of the utility functions
V0 = ASC_NOS + B_SEX_V0 * R_SEX_IMP + B_HHSIZE_V0 * HHSIZE + B_WORKER_V0 *WORKER + B_EDUC_1_V0 *EDUC_1 + B_EDUC_2_V0 *EDUC_2 + B_EDUC_3_V0 *EDUC_3 + B_AGE_IMP_1_V0 *R_AGE_IMP_1+ B_AGE_IMP_2_V0 *R_AGE_IMP_2+B_AGE_IMP_3_V0 *R_AGE_IMP_3+\
   B_RACE_1_V0 *R_RACE_1+B_RACE_2_V0 *R_RACE_2 +B_MSACAT_V0 *MSACAT + B_INC_V0 * income_val
V1 = ASC_OFF + B_SEX_V1 * R_SEX_IMP + B_HHSIZE_V1 * HHSIZE + B_WORKER_V1 *WORKER + B_EDUC_1_V1 *EDUC_1 + B_EDUC_2_V1 *EDUC_2 + B_EDUC_3_V1 *EDUC_3 + B_AGE_IMP_1_V1 *R_AGE_IMP_1+ B_AGE_IMP_2_V1 *R_AGE_IMP_2+B_AGE_IMP_3_V1 *R_AGE_IMP_3+\
   B_RACE_1_V1 *R_RACE_1+B_RACE_2_V1 *R_RACE_2+B_CENSUS_R_2_V1 *CENSUS_R_2 +B_CENSUS_R_3_V1 *CENSUS_R_3+B_CENSUS_R_4_V1 *CENSUS_R_4 +B_MSACAT_V1 *MSACAT + B_INC_V1 * income_val +Prob_no_V1*Prob_no+Prob_lo_V1*Prob_lo+Prob_md_V1*Prob_no+Prob_md_V1*Prob_md +Prob_hi_V1*Prob_hi
V2 = ASC_ONS + B_SEX_V2 * R_SEX_IMP + B_HHSIZE_V2 * HHSIZE + B_WORKER_V2 *WORKER + B_EDUC_1_V2 *EDUC_1 + B_EDUC_2_V2 *EDUC_2 + B_EDUC_3_V2 *EDUC_3 + B_AGE_IMP_1_V2 *R_AGE_IMP_1+ B_AGE_IMP_2_V2 *R_AGE_IMP_2+B_AGE_IMP_3_V2 *R_AGE_IMP_3+\
   B_RACE_1_V2 *R_RACE_1+B_RACE_2_V2 *R_RACE_2 +B_CENSUS_R_2_V2 *CENSUS_R_2 +B_CENSUS_R_3_V2 *CENSUS_R_3+B_CENSUS_R_4_V2 *CENSUS_R_4 +B_MSACAT_V2 *MSACAT + B_INC_V2 * income_val +Prob_no_V2*Prob_no+Prob_lo_V2*Prob_lo+Prob_md_V2*Prob_no+Prob_md_V2*Prob_md +Prob_hi_V2*Prob_hi
V3 = ASC_BOT + B_SEX_V3 * R_SEX_IMP + B_HHSIZE_V3 * HHSIZE + B_WORKER_V3 *WORKER + B_EDUC_1_V3 *EDUC_1 + B_EDUC_2_V3 *EDUC_2 + B_EDUC_3_V3 *EDUC_3 + B_AGE_IMP_1_V3 *R_AGE_IMP_1+ B_AGE_IMP_2_V3 *R_AGE_IMP_2+B_AGE_IMP_3_V3 *R_AGE_IMP_3+\
   B_RACE_1_V3 *R_RACE_1+B_RACE_2_V3 *R_RACE_2 +B_CENSUS_R_2_V3 *CENSUS_R_2 +B_CENSUS_R_3_V3 *CENSUS_R_3+B_CENSUS_R_4_V3 *CENSUS_R_4 +B_MSACAT_V3 *MSACAT+ B_INC_V3 * income_val +Prob_no_V3*Prob_no+Prob_lo_V3*Prob_lo+Prob_md_V3*Prob_no+Prob_md_V3*Prob_md +Prob_hi_V3*Prob_hi
# Associate utility functions with the numbering of alternatives
# Associate utility functions with the numbering of alternatives
V = {0: V0,1: V1, 2: V2, 3: V3}

# Associate the availability conditions with the alternatives
av = {0: Avail, 1: Avail, 2: Avail, 3: Avail}

# nest parameters
NEST_SHOP=Beta('NEST_SHOP',1,1.0,10,0)

NO_SHOP =1.0, [0]
SHOP=NEST_SHOP, [1,2,3]

nests = NO_SHOP, SHOP
# Definition of the model. This is the contribution of each
# observation to the log likelihood function.
logprob = models.lognested(V, av, nests, shop_choice)

# Define level of verbosity
logger = msg.bioMessage()
# logger.setSilent()
# logger.setWarning()
logger.setGeneral()
# logger.setDetailed()

# Create the Biogeme object
formulas = {'loglike': logprob, 'weight': TUFINLWGT}
biogeme = bio.BIOGEME(database, formulas)
biogeme.modelName = "shoping_nested"

# Calculate the null log likelihood for reporting.
biogeme.calculateNullLoglikelihood(av)

# Estimate the parameters
results = biogeme.estimate()
pandasResults = results.getEstimatedParameters()
print(pandasResults)

# Get the results in a pandas table
pandasResults = results.getEstimatedParameters()
print(pandasResults)    
# %%
############################################# Model estimation ################################
## shopping nested 
database = db.Database('shop', atus_df)

# The following statement allows you to use the names of the
# variable as Python variable.
globals().update(database.variables)

# Parameters to be estimated
## Intercept
ASC_NOS = Beta('ASC_NOS', 0, None, None, 1)
ASC_OFF = Beta('ASC_OFF', 0, None, None, 0)
ASC_ONS = Beta('ASC_ONS', 0, None, None, 0)
ASC_BOT = Beta('ASC_BOT', 0, None, None, 0)
## Beta
B_SEX_V0= Beta('B_SEX_V0', 0, None, None, 1)
B_SEX_V1= Beta('B_SEX_V1', 0, None, None, 0)
B_SEX_V2= Beta('B_SEX_V2', 0, None, None, 0)
B_SEX_V3= Beta('B_SEX_V3', 0, None, None, 0)

## Beta
B_INC_V0= Beta('B_INC_V0', 0, None, None, 1)
B_INC_V1= Beta('B_INC_V1', 0, None, None, 0)
B_INC_V2= Beta('B_INC_V2', 0, None, None, 0)
B_INC_V3= Beta('B_INC_V3', 0, None, None, 0)
###
B_HHSIZE_V0= Beta('B_HHSIZE_V0', 0, None, None, 1)
B_HHSIZE_V1= Beta('B_HHSIZE_V1', 0, None, None, 0)
B_HHSIZE_V2= Beta('B_HHSIZE_V2', 0, None, None, 0)
B_HHSIZE_V3= Beta('B_HHSIZE_V3', 0, None, None, 0)
###
B_WORKER_V0= Beta('B_WORKER_V0', 0, None, None, 1)
B_WORKER_V1= Beta('B_WORKER_V1', 0, None, None, 0)
B_WORKER_V2= Beta('B_WORKER_V2', 0, None, None, 0)
B_WORKER_V3= Beta('B_WORKER_V3', 0, None, None, 0)

###
B_MSACAT_V0= Beta('B_MSACAT_V0', 0, None, None, 1)
B_MSACAT_V1= Beta('B_MSACAT_V1', 0, None, None, 0)
B_MSACAT_V2= Beta('B_MSACAT_V2', 0, None, None, 0)
B_MSACAT_V3= Beta('B_MSACAT_V3', 0, None, None, 0)
###
B_EDUC_1_V0= Beta('B_EDUC_1_V0', 0, None, None, 1)
B_EDUC_1_V1= Beta('B_EDUC_1_V1', 0, None, None, 0)
B_EDUC_1_V2= Beta('B_EDUC_1_V2', 0, None, None, 0)
B_EDUC_1_V3= Beta('B_EDUC_1_V3', 0, None, None, 0)
###
B_EDUC_2_V0= Beta('B_EDUC_2_V0', 0, None, None, 1)
B_EDUC_2_V1= Beta('B_EDUC_2_V1', 0, None, None, 0)
B_EDUC_2_V2= Beta('B_EDUC_2_V2', 0, None, None, 0)
B_EDUC_2_V3= Beta('B_EDUC_2_V3', 0, None, None, 0)
###
B_EDUC_3_V0= Beta('B_EDUC_3_V0', 0, None, None, 1)
B_EDUC_3_V1= Beta('B_EDUC_3_V1', 0, None, None, 0)
B_EDUC_3_V2= Beta('B_EDUC_3_V2', 0, None, None, 0)
B_EDUC_3_V3= Beta('B_EDUC_3_V3', 0, None, None, 0)

###
B_AGE_IMP_1_V0= Beta('B_AGE_IMP_1_V0', 0, None, None, 1)
B_AGE_IMP_1_V1= Beta('B_AGE_IMP_1_V1', 0, None, None, 0)
B_AGE_IMP_1_V2= Beta('B_AGE_IMP_1_V2', 0, None, None, 0)
B_AGE_IMP_1_V3= Beta('B_AGE_IMP_1_V3', 0, None, None, 0)

###
B_AGE_IMP_2_V0= Beta('B_AGE_IMP_2_V0', 0, None, None, 1)
B_AGE_IMP_2_V1= Beta('B_AGE_IMP_2_V1', 0, None, None, 0)
B_AGE_IMP_2_V2= Beta('B_AGE_IMP_2_V2', 0, None, None, 0)
B_AGE_IMP_2_V3= Beta('B_AGE_IMP_2_V3', 0, None, None, 0)
###
B_AGE_IMP_3_V0= Beta('B_AGE_IMP_3_V0', 0, None, None, 1)
B_AGE_IMP_3_V1= Beta('B_AGE_IMP_3_V1', 0, None, None, 0)
B_AGE_IMP_3_V2= Beta('B_AGE_IMP_3_V2', 0, None, None, 0)
B_AGE_IMP_3_V3= Beta('B_AGE_IMP_3_V3', 0, None, None, 0)
###
###
B_RACE_1_V0= Beta('B_RACE_1_V0', 0, None, None, 1)
B_RACE_1_V1= Beta('B_RACE_1_V1', 0, None, None, 0)
B_RACE_1_V2= Beta('B_RACE_1_V2', 0, None, None, 0)
B_RACE_1_V3= Beta('B_RACE_1_V3', 0, None, None, 0)

###
B_RACE_2_V0= Beta('B_RACE_2_V0', 0, None, None, 1)
B_RACE_2_V1= Beta('B_RACE_2_V1', 0, None, None, 0)
B_RACE_2_V2= Beta('B_RACE_2_V2', 0, None, None, 0)
B_RACE_2_V3= Beta('B_RACE_2_V3', 0, None, None, 0)
###
B_RACE_3_V0= Beta('B_RACE_3_V0', 0, None, None, 1)
B_RACE_3_V1= Beta('B_RACE_3_V1', 0, None, None, 0)
B_RACE_3_V2= Beta('B_RACE_3_V2', 0, None, None, 0)
B_RACE_3_V3= Beta('B_RACE_3_V3', 0, None, None, 0)

###
B_CENSUS_R_2_V0= Beta('B_CENSUS_R_2_V0', 0, None, None, 1)
B_CENSUS_R_2_V1= Beta('B_CENSUS_R_2_V1', 0, None, None, 0)
B_CENSUS_R_2_V2= Beta('B_CENSUS_R_2_V2', 0, None, None, 0)
B_CENSUS_R_2_V3= Beta('B_CENSUS_R_2_V3', 0, None, None, 0)
###
B_CENSUS_R_3_V0= Beta('B_CENSUS_R_3_V0', 0, None, None, 1)
B_CENSUS_R_3_V1= Beta('B_CENSUS_R_3_V1', 0, None, None, 0)
B_CENSUS_R_3_V2= Beta('B_CENSUS_R_3_V2', 0, None, None, 0)
B_CENSUS_R_3_V3= Beta('B_CENSUS_R_3_V3', 0, None, None, 0)
##
B_CENSUS_R_4_V0= Beta('B_CENSUS_R_4_V0', 0, None, None, 1)
B_CENSUS_R_4_V1= Beta('B_CENSUS_R_4_V1', 0, None, None, 0)
B_CENSUS_R_4_V2= Beta('B_CENSUS_R_4_V2', 0, None, None, 0)
B_CENSUS_R_4_V3= Beta('B_CENSUS_R_4_V3', 0, None, None, 0)

###

Prob_no_V1= Beta('Prob_lo_V1', 0, None, None, 1)
Prob_no_V2= Beta('Prob_lo_V2', 0, None, None, 0)
Prob_no_V3= Beta('Prob_lo_V3', 0, None, None, 0)

#Prob_lo_V0= Beta('Prob_lo_V0', 0, None, None, 1)
Prob_lo_V1= Beta('Prob_lo_V1', 0, None, None, 1)
Prob_lo_V2= Beta('Prob_lo_V2', 0, None, None, 0)
Prob_lo_V3= Beta('Prob_lo_V3', 0, None, None, 0)
###
#Prob_md_V0= Beta('Prob_md_V0', 0, None, None, 1)
Prob_md_V1= Beta('Prob_md_V1', 0, None, None, 1)
Prob_md_V2= Beta('Prob_md_V2', 0, None, None, 0)
Prob_md_V3= Beta('Prob_md_V3', 0, None, None, 0)
##
#Prob_hi_V0= Beta('Prob_hi_V0', 0, None, None, 1)
Prob_hi_V1= Beta('Prob_hi_V1', 0, None, None, 1)
Prob_hi_V2= Beta('Prob_hi_V2', 0, None, None, 0)
Prob_hi_V3= Beta('Prob_hi_V3', 0, None, None, 0)


# Definition of the utility functions
V0 = ASC_NOS + B_SEX_V0 * R_SEX_IMP + B_HHSIZE_V0 * HHSIZE + B_WORKER_V0 *WORKER + B_EDUC_1_V0 *EDUC_1 + B_EDUC_2_V0 *EDUC_2 + B_EDUC_3_V0 *EDUC_3 + B_AGE_IMP_1_V0 *R_AGE_IMP_1+ B_AGE_IMP_2_V0 *R_AGE_IMP_2+B_AGE_IMP_3_V0 *R_AGE_IMP_3+\
   B_RACE_1_V0 *R_RACE_1+B_RACE_2_V0 *R_RACE_2 +B_MSACAT_V0 *MSACAT + B_INC_V0 * income_val
V1 = ASC_OFF + B_SEX_V1 * R_SEX_IMP + B_HHSIZE_V1 * HHSIZE + B_WORKER_V1 *WORKER + B_EDUC_1_V1 *EDUC_1 + B_EDUC_2_V1 *EDUC_2 + B_EDUC_3_V1 *EDUC_3 + B_AGE_IMP_1_V1 *R_AGE_IMP_1+ B_AGE_IMP_2_V1 *R_AGE_IMP_2+B_AGE_IMP_3_V1 *R_AGE_IMP_3+\
   B_RACE_1_V1 *R_RACE_1+B_RACE_2_V1 *R_RACE_2+B_CENSUS_R_2_V1 *CENSUS_R_2 +B_CENSUS_R_3_V1 *CENSUS_R_3+B_CENSUS_R_4_V1 *CENSUS_R_4 +B_MSACAT_V1 *MSACAT + B_INC_V1 * income_val +Prob_no_V1*Prob_no+Prob_lo_V1*Prob_lo+Prob_md_V1*Prob_no+Prob_md_V1*Prob_md +Prob_hi_V1*Prob_hi
V2 = ASC_ONS + B_SEX_V2 * R_SEX_IMP + B_HHSIZE_V2 * HHSIZE + B_WORKER_V2 *WORKER + B_EDUC_1_V2 *EDUC_1 + B_EDUC_2_V2 *EDUC_2 + B_EDUC_3_V2 *EDUC_3 + B_AGE_IMP_1_V2 *R_AGE_IMP_1+ B_AGE_IMP_2_V2 *R_AGE_IMP_2+B_AGE_IMP_3_V2 *R_AGE_IMP_3+\
   B_RACE_1_V2 *R_RACE_1+B_RACE_2_V2 *R_RACE_2 +B_CENSUS_R_2_V2 *CENSUS_R_2 +B_CENSUS_R_3_V2 *CENSUS_R_3+B_CENSUS_R_4_V2 *CENSUS_R_4 +B_MSACAT_V2 *MSACAT + B_INC_V2 * income_val +Prob_no_V2*Prob_no+Prob_lo_V2*Prob_lo+Prob_md_V2*Prob_no+Prob_md_V2*Prob_md +Prob_hi_V2*Prob_hi
V3 = ASC_BOT + B_SEX_V3 * R_SEX_IMP + B_HHSIZE_V3 * HHSIZE + B_WORKER_V3 *WORKER + B_EDUC_1_V3 *EDUC_1 + B_EDUC_2_V3 *EDUC_2 + B_EDUC_3_V3 *EDUC_3 + B_AGE_IMP_1_V3 *R_AGE_IMP_1+ B_AGE_IMP_2_V3 *R_AGE_IMP_2+B_AGE_IMP_3_V3 *R_AGE_IMP_3+\
   B_RACE_1_V3 *R_RACE_1+B_RACE_2_V3 *R_RACE_2 +B_CENSUS_R_2_V3 *CENSUS_R_2 +B_CENSUS_R_3_V3 *CENSUS_R_3+B_CENSUS_R_4_V3 *CENSUS_R_4 +B_MSACAT_V3 *MSACAT+ B_INC_V3 * income_val +Prob_no_V3*Prob_no+Prob_lo_V3*Prob_lo+Prob_md_V3*Prob_no+Prob_md_V3*Prob_md +Prob_hi_V3*Prob_hi
# Associate utility functions with the numbering of alternatives
# Associate utility functions with the numbering of alternatives
V = {0: V0,1: V1, 2: V2, 3: V3}

# Associate the availability conditions with the alternatives
av = {0: Avail, 1: Avail, 2: Avail, 3: Avail}

# nest parameters
NEST_SHOP=Beta('NEST_SHOP',1,1.0,10,0)

NO_SHOP =1.0, [0]
SHOP=NEST_SHOP, [1,2,3]

nests = NO_SHOP, SHOP
# Definition of the model. This is the contribution of each
# observation to the log likelihood function.
logprob = models.lognested(V, av, nests, shop_choice)

# Define level of verbosity
logger = msg.bioMessage()
# logger.setSilent()
# logger.setWarning()
logger.setGeneral()
# logger.setDetailed()

# Create the Biogeme object
formulas = {'loglike': logprob, 'weight': TUFINLWGT}
biogeme = bio.BIOGEME(database, formulas)
biogeme.modelName = "shoping_nested"

# Calculate the null log likelihood for reporting.
biogeme.calculateNullLoglikelihood(av)

# Estimate the parameters
results = biogeme.estimate()
pandasResults = results.getEstimatedParameters()
print(pandasResults)

# Get the results in a pandas table
pandasResults = results.getEstimatedParameters()
print(pandasResults)    
# %%
## shopping nested 
database = db.Database('ondemand', atus_df)

# The following statement allows you to use the names of the
# variable as Python variable.
globals().update(database.variables)

# Parameters to be estimated
## shopping nested 
database = db.Database('shop', atus_df)

# The following statement allows you to use the names of the
# variable as Python variable.
globals().update(database.variables)

# Parameters to be estimated
## Intercept
ASC_NOS = Beta('ASC_NOS', 0, None, None, 1)
ASC_OFF = Beta('ASC_OFF', 0, None, None, 0)
ASC_ONS = Beta('ASC_ONS', 0, None, None, 0)
ASC_BOT = Beta('ASC_BOT', 0, None, None, 0)
## Beta
B_SEX_V0= Beta('B_SEX_V0', 0, None, None, 1)
B_SEX_V1= Beta('B_SEX_V1', 0, None, None, 0)
B_SEX_V2= Beta('B_SEX_V2', 0, None, None, 0)
B_SEX_V3= Beta('B_SEX_V3', 0, None, None, 0)

## Beta
B_INC_V0= Beta('B_INC_V0', 0, None, None, 1)
B_INC_V1= Beta('B_INC_V1', 0, None, None, 0)
B_INC_V2= Beta('B_INC_V2', 0, None, None, 0)
B_INC_V3= Beta('B_INC_V3', 0, None, None, 0)
###
B_HHSIZE_V0= Beta('B_HHSIZE_V0', 0, None, None, 1)
B_HHSIZE_V1= Beta('B_HHSIZE_V1', 0, None, None, 0)
B_HHSIZE_V2= Beta('B_HHSIZE_V2', 0, None, None, 0)
B_HHSIZE_V3= Beta('B_HHSIZE_V3', 0, None, None, 0)
###
B_WORKER_V0= Beta('B_WORKER_V0', 0, None, None, 1)
B_WORKER_V1= Beta('B_WORKER_V1', 0, None, None, 0)
B_WORKER_V2= Beta('B_WORKER_V2', 0, None, None, 0)
B_WORKER_V3= Beta('B_WORKER_V3', 0, None, None, 0)

###
B_MSACAT_V0= Beta('B_MSACAT_V0', 0, None, None, 1)
B_MSACAT_V1= Beta('B_MSACAT_V1', 0, None, None, 0)
B_MSACAT_V2= Beta('B_MSACAT_V2', 0, None, None, 0)
B_MSACAT_V3= Beta('B_MSACAT_V3', 0, None, None, 0)
###
B_EDUC_1_V0= Beta('B_EDUC_1_V0', 0, None, None, 1)
B_EDUC_1_V1= Beta('B_EDUC_1_V1', 0, None, None, 0)
B_EDUC_1_V2= Beta('B_EDUC_1_V2', 0, None, None, 0)
B_EDUC_1_V3= Beta('B_EDUC_1_V3', 0, None, None, 0)
###
B_EDUC_2_V0= Beta('B_EDUC_2_V0', 0, None, None, 1)
B_EDUC_2_V1= Beta('B_EDUC_2_V1', 0, None, None, 0)
B_EDUC_2_V2= Beta('B_EDUC_2_V2', 0, None, None, 0)
B_EDUC_2_V3= Beta('B_EDUC_2_V3', 0, None, None, 0)
###
B_EDUC_3_V0= Beta('B_EDUC_3_V0', 0, None, None, 1)
B_EDUC_3_V1= Beta('B_EDUC_3_V1', 0, None, None, 0)
B_EDUC_3_V2= Beta('B_EDUC_3_V2', 0, None, None, 0)
B_EDUC_3_V3= Beta('B_EDUC_3_V3', 0, None, None, 0)

###
B_AGE_IMP_1_V0= Beta('B_AGE_IMP_1_V0', 0, None, None, 1)
B_AGE_IMP_1_V1= Beta('B_AGE_IMP_1_V1', 0, None, None, 0)
B_AGE_IMP_1_V2= Beta('B_AGE_IMP_1_V2', 0, None, None, 0)
B_AGE_IMP_1_V3= Beta('B_AGE_IMP_1_V3', 0, None, None, 0)

###
B_AGE_IMP_2_V0= Beta('B_AGE_IMP_2_V0', 0, None, None, 1)
B_AGE_IMP_2_V1= Beta('B_AGE_IMP_2_V1', 0, None, None, 0)
B_AGE_IMP_2_V2= Beta('B_AGE_IMP_2_V2', 0, None, None, 0)
B_AGE_IMP_2_V3= Beta('B_AGE_IMP_2_V3', 0, None, None, 0)
###
B_AGE_IMP_3_V0= Beta('B_AGE_IMP_3_V0', 0, None, None, 1)
B_AGE_IMP_3_V1= Beta('B_AGE_IMP_3_V1', 0, None, None, 0)
B_AGE_IMP_3_V2= Beta('B_AGE_IMP_3_V2', 0, None, None, 0)
B_AGE_IMP_3_V3= Beta('B_AGE_IMP_3_V3', 0, None, None, 0)
###
###
B_RACE_1_V0= Beta('B_RACE_1_V0', 0, None, None, 1)
B_RACE_1_V1= Beta('B_RACE_1_V1', 0, None, None, 0)
B_RACE_1_V2= Beta('B_RACE_1_V2', 0, None, None, 0)
B_RACE_1_V3= Beta('B_RACE_1_V3', 0, None, None, 0)

###
B_RACE_2_V0= Beta('B_RACE_2_V0', 0, None, None, 1)
B_RACE_2_V1= Beta('B_RACE_2_V1', 0, None, None, 0)
B_RACE_2_V2= Beta('B_RACE_2_V2', 0, None, None, 0)
B_RACE_2_V3= Beta('B_RACE_2_V3', 0, None, None, 0)
###
B_RACE_3_V0= Beta('B_RACE_3_V0', 0, None, None, 1)
B_RACE_3_V1= Beta('B_RACE_3_V1', 0, None, None, 0)
B_RACE_3_V2= Beta('B_RACE_3_V2', 0, None, None, 0)
B_RACE_3_V3= Beta('B_RACE_3_V3', 0, None, None, 0)

###
B_CENSUS_R_2_V0= Beta('B_CENSUS_R_2_V0', 0, None, None, 1)
B_CENSUS_R_2_V1= Beta('B_CENSUS_R_2_V1', 0, None, None, 0)
B_CENSUS_R_2_V2= Beta('B_CENSUS_R_2_V2', 0, None, None, 0)
B_CENSUS_R_2_V3= Beta('B_CENSUS_R_2_V3', 0, None, None, 0)
###
B_CENSUS_R_3_V0= Beta('B_CENSUS_R_3_V0', 0, None, None, 1)
B_CENSUS_R_3_V1= Beta('B_CENSUS_R_3_V1', 0, None, None, 0)
B_CENSUS_R_3_V2= Beta('B_CENSUS_R_3_V2', 0, None, None, 0)
B_CENSUS_R_3_V3= Beta('B_CENSUS_R_3_V3', 0, None, None, 0)
##
B_CENSUS_R_4_V0= Beta('B_CENSUS_R_4_V0', 0, None, None, 1)
B_CENSUS_R_4_V1= Beta('B_CENSUS_R_4_V1', 0, None, None, 0)
B_CENSUS_R_4_V2= Beta('B_CENSUS_R_4_V2', 0, None, None, 0)
B_CENSUS_R_4_V3= Beta('B_CENSUS_R_4_V3', 0, None, None, 0)

###

Prob_no_V1= Beta('Prob_lo_V1', 0, None, None, 1)
Prob_no_V2= Beta('Prob_lo_V2', 0, None, None, 0)
Prob_no_V3= Beta('Prob_lo_V3', 0, None, None, 0)

#Prob_lo_V0= Beta('Prob_lo_V0', 0, None, None, 1)
Prob_lo_V1= Beta('Prob_lo_V1', 0, None, None, 1)
Prob_lo_V2= Beta('Prob_lo_V2', 0, None, None, 0)
Prob_lo_V3= Beta('Prob_lo_V3', 0, None, None, 0)
###
#Prob_md_V0= Beta('Prob_md_V0', 0, None, None, 1)
Prob_md_V1= Beta('Prob_md_V1', 0, None, None, 1)
Prob_md_V2= Beta('Prob_md_V2', 0, None, None, 0)
Prob_md_V3= Beta('Prob_md_V3', 0, None, None, 0)
##
#Prob_hi_V0= Beta('Prob_hi_V0', 0, None, None, 1)
Prob_hi_V1= Beta('Prob_hi_V1', 0, None, None, 1)
Prob_hi_V2= Beta('Prob_hi_V2', 0, None, None, 0)
Prob_hi_V3= Beta('Prob_hi_V3', 0, None, None, 0)


# Definition of the utility functions
V0 = ASC_NOS + B_SEX_V0 * R_SEX_IMP + B_HHSIZE_V0 * HHSIZE + B_WORKER_V0 *WORKER + B_EDUC_1_V0 *EDUC_1 + B_EDUC_2_V0 *EDUC_2 + B_EDUC_3_V0 *EDUC_3 + B_AGE_IMP_1_V0 *R_AGE_IMP_1+ B_AGE_IMP_2_V0 *R_AGE_IMP_2+B_AGE_IMP_3_V0 *R_AGE_IMP_3+\
   B_RACE_1_V0 *R_RACE_1+B_RACE_2_V0 *R_RACE_2 +B_MSACAT_V0 *MSACAT + B_INC_V0 * income_val
V1 = ASC_OFF + B_SEX_V1 * R_SEX_IMP + B_HHSIZE_V1 * HHSIZE + B_WORKER_V1 *WORKER + B_EDUC_1_V1 *EDUC_1 + B_EDUC_2_V1 *EDUC_2 + B_EDUC_3_V1 *EDUC_3 + B_AGE_IMP_1_V1 *R_AGE_IMP_1+ B_AGE_IMP_2_V1 *R_AGE_IMP_2+B_AGE_IMP_3_V1 *R_AGE_IMP_3+\
   B_RACE_1_V1 *R_RACE_1+B_RACE_2_V1 *R_RACE_2+B_CENSUS_R_2_V1 *CENSUS_R_2 +B_CENSUS_R_3_V1 *CENSUS_R_3+B_CENSUS_R_4_V1 *CENSUS_R_4 +B_MSACAT_V1 *MSACAT + B_INC_V1 * income_val +Prob_no_V1*Prob_no+Prob_lo_V1*Prob_lo+Prob_md_V1*Prob_no+Prob_md_V1*Prob_md +Prob_hi_V1*Prob_hi
V2 = ASC_ONS + B_SEX_V2 * R_SEX_IMP + B_HHSIZE_V2 * HHSIZE + B_WORKER_V2 *WORKER + B_EDUC_1_V2 *EDUC_1 + B_EDUC_2_V2 *EDUC_2 + B_EDUC_3_V2 *EDUC_3 + B_AGE_IMP_1_V2 *R_AGE_IMP_1+ B_AGE_IMP_2_V2 *R_AGE_IMP_2+B_AGE_IMP_3_V2 *R_AGE_IMP_3+\
   B_RACE_1_V2 *R_RACE_1+B_RACE_2_V2 *R_RACE_2 +B_CENSUS_R_2_V2 *CENSUS_R_2 +B_CENSUS_R_3_V2 *CENSUS_R_3+B_CENSUS_R_4_V2 *CENSUS_R_4 +B_MSACAT_V2 *MSACAT + B_INC_V2 * income_val +Prob_no_V2*Prob_no+Prob_lo_V2*Prob_lo+Prob_md_V2*Prob_no+Prob_md_V2*Prob_md +Prob_hi_V2*Prob_hi
V3 = ASC_BOT + B_SEX_V3 * R_SEX_IMP + B_HHSIZE_V3 * HHSIZE + B_WORKER_V3 *WORKER + B_EDUC_1_V3 *EDUC_1 + B_EDUC_2_V3 *EDUC_2 + B_EDUC_3_V3 *EDUC_3 + B_AGE_IMP_1_V3 *R_AGE_IMP_1+ B_AGE_IMP_2_V3 *R_AGE_IMP_2+B_AGE_IMP_3_V3 *R_AGE_IMP_3+\
   B_RACE_1_V3 *R_RACE_1+B_RACE_2_V3 *R_RACE_2 +B_CENSUS_R_2_V3 *CENSUS_R_2 +B_CENSUS_R_3_V3 *CENSUS_R_3+B_CENSUS_R_4_V3 *CENSUS_R_4 +B_MSACAT_V3 *MSACAT+ B_INC_V3 * income_val +Prob_no_V3*Prob_no+Prob_lo_V3*Prob_lo+Prob_md_V3*Prob_no+Prob_md_V3*Prob_md +Prob_hi_V3*Prob_hi
# Associate utility functions with the numbering of alternatives
# Associate utility functions with the numbering of alternatives
V = {0: V0,1: V1, 2: V2, 3: V3}

# Associate the availability conditions with the alternatives
av = {0: Avail, 1: Avail, 2: Avail, 3: Avail}

# nest parameters
NEST_OD=Beta('NEST_OD',1,1.0,10,0)

NO_OD =1.0, [0]
OD=NEST_OD, [1,2,3]

nests = NO_OD, OD
# Definition of the model. This is the contribution of each
# observation to the log likelihood function.
logprob = models.lognested(V, av, nests, ondemand_choice)

# Define level of verbosity
logger = msg.bioMessage()
# logger.setSilent()
# logger.setWarning()
logger.setGeneral()
# logger.setDetailed()

# Create the Biogeme object
formulas = {'loglike': logprob, 'weight': TUFINLWGT}
biogeme = bio.BIOGEME(database, formulas)
biogeme.modelName = "ondemand_nested"

# Calculate the null log likelihood for reporting.
biogeme.calculateNullLoglikelihood(av)

# Estimate the parameters
results = biogeme.estimate()
pandasResults = results.getEstimatedParameters()
print(pandasResults)

# Get the results in a pandas table
pandasResults = results.getEstimatedParameters()
print(pandasResults)    
# %%





# %%
## Read the data
#df = pd.read_csv('swissmetro.dat', sep='\t')
database = db.Database('NHTS', df)

# The following statement allows you to use the names of the
# variable as Python variable.
globals().update(database.variables)

# Parameters to be estimated
## Intercept
ASC_NOS = Beta('ASC_NOS', 0, None, None, 1)
ASC_LOW = Beta('ASC_LOW', 0, None, None, 0)
ASC_MID = Beta('ASC_MID', 0, None, None, 0)
ASC_HIG = Beta('ASC_HIG', 0, None, None, 0)
## Beta
B_SEX_V0= Beta('B_SEX_V0', 0, None, None, 1)
B_SEX_V1= Beta('B_SEX_V1', 0, None, None, 0)
B_SEX_V2= Beta('B_SEX_V2', 0, None, None, 0)
B_SEX_V3= Beta('B_SEX_V3', 0, None, None, 0)

## Beta
B_INC_V0= Beta('B_INC_V0', 0, None, None, 1)
B_INC_V1= Beta('B_INC_V1', 0, None, None, 0)
B_INC_V2= Beta('B_INC_V2', 0, None, None, 0)
B_INC_V3= Beta('B_INC_V3', 0, None, None, 0)
###
B_HHSIZE_V0= Beta('B_HHSIZE_V0', 0, None, None, 1)
B_HHSIZE_V1= Beta('B_HHSIZE_V1', 0, None, None, 0)
B_HHSIZE_V2= Beta('B_HHSIZE_V2', 0, None, None, 0)
B_HHSIZE_V3= Beta('B_HHSIZE_V3', 0, None, None, 0)
###
B_WORKER_V0= Beta('B_WORKER_V0', 0, None, None, 1)
B_WORKER_V1= Beta('B_WORKER_V1', 0, None, None, 0)
B_WORKER_V2= Beta('B_WORKER_V2', 0, None, None, 0)
B_WORKER_V3= Beta('B_WORKER_V3', 0, None, None, 0)

###
B_MSACAT_V0= Beta('B_MSACAT_V0', 0, None, None, 1)
B_MSACAT_V1= Beta('B_MSACAT_V1', 0, None, None, 0)
B_MSACAT_V2= Beta('B_MSACAT_V2', 0, None, None, 0)
B_MSACAT_V3= Beta('B_MSACAT_V3', 0, None, None, 0)
###
B_EDUC_1_V0= Beta('B_EDUC_1_V0', 0, None, None, 1)
B_EDUC_1_V1= Beta('B_EDUC_1_V1', 0, None, None, 0)
B_EDUC_1_V2= Beta('B_EDUC_1_V2', 0, None, None, 0)
B_EDUC_1_V3= Beta('B_EDUC_1_V3', 0, None, None, 0)
###
B_EDUC_2_V0= Beta('B_EDUC_2_V0', 0, None, None, 1)
B_EDUC_2_V1= Beta('B_EDUC_2_V1', 0, None, None, 0)
B_EDUC_2_V2= Beta('B_EDUC_2_V2', 0, None, None, 0)
B_EDUC_2_V3= Beta('B_EDUC_2_V3', 0, None, None, 0)
###
B_EDUC_3_V0= Beta('B_EDUC_3_V0', 0, None, None, 1)
B_EDUC_3_V1= Beta('B_EDUC_3_V1', 0, None, None, 0)
B_EDUC_3_V2= Beta('B_EDUC_3_V2', 0, None, None, 0)
B_EDUC_3_V3= Beta('B_EDUC_3_V3', 0, None, None, 0)

###
B_AGE_IMP_1_V0= Beta('B_AGE_IMP_1_V0', 0, None, None, 1)
B_AGE_IMP_1_V1= Beta('B_AGE_IMP_1_V1', 0, None, None, 0)
B_AGE_IMP_1_V2= Beta('B_AGE_IMP_1_V2', 0, None, None, 0)
B_AGE_IMP_1_V3= Beta('B_AGE_IMP_1_V3', 0, None, None, 0)

###
B_AGE_IMP_2_V0= Beta('B_AGE_IMP_2_V0', 0, None, None, 1)
B_AGE_IMP_2_V1= Beta('B_AGE_IMP_2_V1', 0, None, None, 0)
B_AGE_IMP_2_V2= Beta('B_AGE_IMP_2_V2', 0, None, None, 0)
B_AGE_IMP_2_V3= Beta('B_AGE_IMP_2_V3', 0, None, None, 0)
###
B_AGE_IMP_3_V0= Beta('B_AGE_IMP_3_V0', 0, None, None, 1)
B_AGE_IMP_3_V1= Beta('B_AGE_IMP_3_V1', 0, None, None, 0)
B_AGE_IMP_3_V2= Beta('B_AGE_IMP_3_V2', 0, None, None, 0)
B_AGE_IMP_3_V3= Beta('B_AGE_IMP_3_V3', 0, None, None, 0)
###
###
B_RACE_1_V0= Beta('B_RACE_1_V0', 0, None, None, 1)
B_RACE_1_V1= Beta('B_RACE_1_V1', 0, None, None, 0)
B_RACE_1_V2= Beta('B_RACE_1_V2', 0, None, None, 0)
B_RACE_1_V3= Beta('B_RACE_1_V3', 0, None, None, 0)

###
B_RACE_2_V0= Beta('B_RACE_2_V0', 0, None, None, 1)
B_RACE_2_V1= Beta('B_RACE_2_V1', 0, None, None, 0)
B_RACE_2_V2= Beta('B_RACE_2_V2', 0, None, None, 0)
B_RACE_2_V3= Beta('B_RACE_2_V3', 0, None, None, 0)
###
B_RACE_3_V0= Beta('B_RACE_3_V0', 0, None, None, 1)
B_RACE_3_V1= Beta('B_RACE_3_V1', 0, None, None, 0)
B_RACE_3_V2= Beta('B_RACE_3_V2', 0, None, None, 0)
B_RACE_3_V3= Beta('B_RACE_3_V3', 0, None, None, 0)

###
B_income_cls_1_V0= Beta('B_income_cls_1_V0', 0, None, None, 1)
B_income_cls_1_V1= Beta('B_income_cls_1_V1', 0, None, None, 0)
B_income_cls_1_V2= Beta('B_income_cls_1_V2', 0, None, None, 0)
B_income_cls_1_V3= Beta('B_income_cls_1_V3', 0, None, None, 0)
###
B_income_cls_2_V0= Beta('B_income_cls_2_V0', 0, None, None, 1)
B_income_cls_2_V1= Beta('B_income_cls_2_V1', 0, None, None, 0)
B_income_cls_2_V2= Beta('B_income_cls_2_V2', 0, None, None, 0)
B_income_cls_2_V3= Beta('B_income_cls_2_V3', 0, None, None, 0)
###
B_income_cls_3_V0= Beta('B_income_cls_3_V0', 0, None, None, 1)
B_income_cls_3_V1= Beta('B_income_cls_3_V1', 0, None, None, 0)
B_income_cls_3_V2= Beta('B_income_cls_3_V2', 0, None, None, 0)
B_income_cls_3_V3= Beta('B_income_cls_3_V3', 0, None, None, 0)
###
B_CENSUS_R_2_V0= Beta('B_CENSUS_R_2_V0', 0, None, None, 1)
B_CENSUS_R_2_V1= Beta('B_CENSUS_R_2_V1', 0, None, None, 0)
B_CENSUS_R_2_V2= Beta('B_CENSUS_R_2_V2', 0, None, None, 0)
B_CENSUS_R_2_V3= Beta('B_CENSUS_R_2_V3', 0, None, None, 0)
###
B_CENSUS_R_3_V0= Beta('B_CENSUS_R_3_V0', 0, None, None, 1)
B_CENSUS_R_3_V1= Beta('B_CENSUS_R_3_V1', 0, None, None, 0)
B_CENSUS_R_3_V2= Beta('B_CENSUS_R_3_V2', 0, None, None, 0)
B_CENSUS_R_3_V3= Beta('B_CENSUS_R_3_V3', 0, None, None, 0)
##
B_CENSUS_R_4_V0= Beta('B_CENSUS_R_4_V0', 0, None, None, 1)
B_CENSUS_R_4_V1= Beta('B_CENSUS_R_4_V1', 0, None, None, 0)
B_CENSUS_R_4_V2= Beta('B_CENSUS_R_4_V2', 0, None, None, 0)
B_CENSUS_R_4_V3= Beta('B_CENSUS_R_4_V3', 0, None, None, 0)


# Definition of the utility functions
V0 = ASC_NOS + B_SEX_V0 * R_SEX_IMP + B_HHSIZE_V0 * HHSIZE + B_WORKER_V0 *WORKER + B_EDUC_1_V0 *EDUC_1 + B_EDUC_2_V0 *EDUC_2 + B_EDUC_3_V0 *EDUC_3 + B_AGE_IMP_1_V0 *R_AGE_IMP_1+ B_AGE_IMP_2_V0 *R_AGE_IMP_2+B_AGE_IMP_3_V0 *R_AGE_IMP_3+\
   B_RACE_1_V0 *R_RACE_1+B_RACE_2_V0 *R_RACE_2+B_RACE_3_V0 *R_RACE_3 +B_CENSUS_R_2_V0 *CENSUS_R_2 +B_CENSUS_R_3_V0 *CENSUS_R_3+B_CENSUS_R_4_V0 *CENSUS_R_4 +B_MSACAT_V0 *MSACAT + B_INC_V0 * income_val
V1 = ASC_LOW + B_SEX_V1 * R_SEX_IMP + B_HHSIZE_V1 * HHSIZE + B_WORKER_V1 *WORKER + B_EDUC_1_V1 *EDUC_1 + B_EDUC_2_V1 *EDUC_2 + B_EDUC_3_V1 *EDUC_3 + B_AGE_IMP_1_V1 *R_AGE_IMP_1+ B_AGE_IMP_2_V1 *R_AGE_IMP_2+B_AGE_IMP_3_V1 *R_AGE_IMP_3+\
   B_RACE_1_V1 *R_RACE_1+B_RACE_2_V1 *R_RACE_2+B_RACE_3_V1 *R_RACE_3 +B_CENSUS_R_2_V1 *CENSUS_R_2 +B_CENSUS_R_3_V1 *CENSUS_R_3+B_CENSUS_R_4_V1 *CENSUS_R_4 +B_MSACAT_V1 *MSACAT + B_INC_V1 * income_val
V2 = ASC_MID + B_SEX_V2 * R_SEX_IMP + B_HHSIZE_V2 * HHSIZE + B_WORKER_V2 *WORKER + B_EDUC_1_V2 *EDUC_1 + B_EDUC_2_V2 *EDUC_2 + B_EDUC_3_V2 *EDUC_3 + B_AGE_IMP_1_V2 *R_AGE_IMP_1+ B_AGE_IMP_2_V2 *R_AGE_IMP_2+B_AGE_IMP_3_V2 *R_AGE_IMP_3+\
   B_RACE_1_V2 *R_RACE_1+B_RACE_2_V2 *R_RACE_2+B_RACE_3_V2 *R_RACE_3 +B_CENSUS_R_2_V2 *CENSUS_R_2 +B_CENSUS_R_3_V2 *CENSUS_R_3+B_CENSUS_R_4_V2 *CENSUS_R_4 +B_MSACAT_V2 *MSACAT + B_INC_V2 * income_val
V3 = ASC_HIG + B_SEX_V3 * R_SEX_IMP + B_HHSIZE_V3 * HHSIZE + B_WORKER_V3 *WORKER + B_EDUC_1_V3 *EDUC_1 + B_EDUC_2_V3 *EDUC_2 + B_EDUC_3_V3 *EDUC_3 + B_AGE_IMP_1_V3 *R_AGE_IMP_1+ B_AGE_IMP_2_V3 *R_AGE_IMP_2+B_AGE_IMP_3_V3 *R_AGE_IMP_3+\
   B_RACE_1_V3 *R_RACE_1+B_RACE_2_V3 *R_RACE_2+B_RACE_3_V3 *R_RACE_3 +B_CENSUS_R_2_V3 *CENSUS_R_2 +B_CENSUS_R_3_V3 *CENSUS_R_3+B_CENSUS_R_4_V3 *CENSUS_R_4 +B_MSACAT_V3 *MSACAT+ B_INC_V3 * income_val
# Associate utility functions with the numbering of alternatives
V = {0: V0,1: V1, 2: V2, 3: V3}

# Associate the availability conditions with the alternatives
av = {0: Avail, 1: Avail, 2: Avail, 3: Avail}

# Definition of the model. This is the contribution of each
# observation to the log likelihood function.
logprob = models.loglogit(V, av, onlineshop)

# Create the Biogeme object
formulas = {'loglike': logprob, 'weight': WTPERFIN}
biogeme = bio.BIOGEME(database, formulas)
biogeme.modelName = 'onine_shop_logit_con'

# Calculate the null log likelihood for reporting.
biogeme.calculateNullLoglikelihood(av)

# Estimate the parameters
results = biogeme.estimate()

# Get the results in a pandas table
pandasResults = results.getEstimatedParameters()
print(pandasResults)    
 



# %%
## Read the data
#df = pd.read_csv('swissmetro.dat', sep='\t')
database = db.Database('NHTS', df)

# The following statement allows you to use the names of the
# variable as Python variable.
globals().update(database.variables)

# Parameters to be estimated
## Intercept
ASC_NOS = Beta('ASC_NOS', 0, None, None, 1)
ASC_LOW = Beta('ASC_LOW', 0, None, None, 0)
ASC_MID = Beta('ASC_MID', 0, None, None, 0)
ASC_HIG = Beta('ASC_HIG', 0, None, None, 0)
## Beta
B_SEX_V0= Beta('B_SEX_V0', 0, None, None, 1)
B_SEX_V1= Beta('B_SEX_V1', 0, None, None, 0)
B_SEX_V2= Beta('B_SEX_V2', 0, None, None, 0)
B_SEX_V3= Beta('B_SEX_V3', 0, None, None, 0)
###
B_HHSIZE_V0= Beta('B_SEX_V0', 0, None, None, 1)
B_HHSIZE_V1= Beta('B_SEX_V1', 0, None, None, 0)
B_HHSIZE_V2= Beta('B_SEX_V2', 0, None, None, 0)
B_HHSIZE_V3= Beta('B_SEX_V3', 0, None, None, 0)
###
B_WORKER_V0= Beta('B_WORKER_V0', 0, None, None, 1)
B_WORKER_V1= Beta('B_WORKER_V1', 0, None, None, 0)
B_WORKER_V2= Beta('B_WORKER_V2', 0, None, None, 0)
B_WORKER_V3= Beta('B_WORKER_V3', 0, None, None, 0)

###
B_MSACAT_V0= Beta('B_MSACAT_V0', 0, None, None, 1)
B_MSACAT_V1= Beta('B_MSACAT_V1', 0, None, None, 0)
B_MSACAT_V2= Beta('B_MSACAT_V2', 0, None, None, 0)
B_MSACAT_V3= Beta('B_MSACAT_V3', 0, None, None, 0)
###
B_EDUC_1_V0= Beta('B_EDUC_1_V0', 0, None, None, 1)
B_EDUC_1_V1= Beta('B_EDUC_1_V1', 0, None, None, 0)
B_EDUC_1_V2= Beta('B_EDUC_1_V2', 0, None, None, 0)
B_EDUC_1_V3= Beta('B_EDUC_1_V3', 0, None, None, 0)
###
B_EDUC_2_V0= Beta('B_EDUC_2_V0', 0, None, None, 1)
B_EDUC_2_V1= Beta('B_EDUC_2_V1', 0, None, None, 0)
B_EDUC_2_V2= Beta('B_EDUC_2_V2', 0, None, None, 0)
B_EDUC_2_V3= Beta('B_EDUC_2_V3', 0, None, None, 0)
###
B_EDUC_3_V0= Beta('B_EDUC_3_V0', 0, None, None, 1)
B_EDUC_3_V1= Beta('B_EDUC_3_V1', 0, None, None, 0)
B_EDUC_3_V2= Beta('B_EDUC_3_V2', 0, None, None, 0)
B_EDUC_3_V3= Beta('B_EDUC_3_V3', 0, None, None, 0)

###
B_AGE_IMP_1_V0= Beta('B_AGE_IMP_1_V0', 0, None, None, 1)
B_AGE_IMP_1_V1= Beta('B_AGE_IMP_1_V1', 0, None, None, 0)
B_AGE_IMP_1_V2= Beta('B_AGE_IMP_1_V2', 0, None, None, 0)
B_AGE_IMP_1_V3= Beta('B_AGE_IMP_1_V3', 0, None, None, 0)

###
B_AGE_IMP_2_V0= Beta('B_AGE_IMP_2_V0', 0, None, None, 1)
B_AGE_IMP_2_V1= Beta('B_AGE_IMP_2_V1', 0, None, None, 0)
B_AGE_IMP_2_V2= Beta('B_AGE_IMP_2_V2', 0, None, None, 0)
B_AGE_IMP_2_V3= Beta('B_AGE_IMP_2_V3', 0, None, None, 0)
###
B_AGE_IMP_3_V0= Beta('B_AGE_IMP_3_V0', 0, None, None, 1)
B_AGE_IMP_3_V1= Beta('B_AGE_IMP_3_V1', 0, None, None, 0)
B_AGE_IMP_3_V2= Beta('B_AGE_IMP_3_V2', 0, None, None, 0)
B_AGE_IMP_3_V3= Beta('B_AGE_IMP_3_V3', 0, None, None, 0)
###
B_RACE_1= Beta('B_RACE_1', 0, None, None, 0)
###
B_RACE_2= Beta('B_RACE_2', 0, None, None, 0)
###
B_RACE_3= Beta('B_RACE_3', 0, None, None, 0)
###
B_income_cls_1_V0= Beta('B_income_cls_1_V0', 0, None, None, 1)
B_income_cls_1_V1= Beta('B_income_cls_1_V1', 0, None, None, 0)
B_income_cls_1_V2= Beta('B_income_cls_1_V2', 0, None, None, 0)
B_income_cls_1_V3= Beta('B_income_cls_1_V3', 0, None, None, 0)
###
B_income_cls_2_V0= Beta('B_income_cls_2_V0', 0, None, None, 1)
B_income_cls_2_V1= Beta('B_income_cls_2_V1', 0, None, None, 0)
B_income_cls_2_V2= Beta('B_income_cls_2_V2', 0, None, None, 0)
B_income_cls_2_V3= Beta('B_income_cls_2_V3', 0, None, None, 0)
###
B_income_cls_3_V0= Beta('B_income_cls_3_V0', 0, None, None, 1)
B_income_cls_3_V1= Beta('B_income_cls_3_V1', 0, None, None, 0)
B_income_cls_3_V2= Beta('B_income_cls_3_V2', 0, None, None, 0)
B_income_cls_3_V3= Beta('B_income_cls_3_V3', 0, None, None, 0)
###
B_CENSUS_R_2_V0= Beta('B_CENSUS_R_2_V0', 0, None, None, 1)
B_CENSUS_R_2_V1= Beta('B_CENSUS_R_2_V1', 0, None, None, 0)
B_CENSUS_R_2_V2= Beta('B_CENSUS_R_2_V2', 0, None, None, 0)
B_CENSUS_R_2_V3= Beta('B_CENSUS_R_2_V3', 0, None, None, 0)
###
B_CENSUS_R_3_V0= Beta('B_CENSUS_R_3_V0', 0, None, None, 1)
B_CENSUS_R_3_V1= Beta('B_CENSUS_R_3_V1', 0, None, None, 0)
B_CENSUS_R_3_V2= Beta('B_CENSUS_R_3_V2', 0, None, None, 0)
B_CENSUS_R_3_V3= Beta('B_CENSUS_R_3_V3', 0, None, None, 0)
###
B_CENSUS_R_4_V0= Beta('B_CENSUS_R_4_V0', 0, None, None, 1)
B_CENSUS_R_4_V1= Beta('B_CENSUS_R_4_V1', 0, None, None, 0)
B_CENSUS_R_4_V2= Beta('B_CENSUS_R_4_V2', 0, None, None, 0)
B_CENSUS_R_4_V3= Beta('B_CENSUS_R_4_V3', 0, None, None, 0)


# Definition of the utility functions
V0 = ASC_NOS + B_SEX_V0 * R_SEX_IMP + B_HHSIZE_V0 * HHSIZE + B_WORKER_V0 *WORKER + B_EDUC_1_V0 *EDUC_1 + B_EDUC_2_V0 *EDUC_2 + B_EDUC_3_V0 *EDUC_3 + B_AGE_IMP_1_V0 *R_AGE_IMP_1+ B_AGE_IMP_2_V0 *R_AGE_IMP_2+B_AGE_IMP_3_V0 *R_AGE_IMP_3+\
    B_income_cls_1_V0 *income_cls_1+B_income_cls_2_V0 *income_cls_2+B_income_cls_3_V0 *income_cls_3 +B_CENSUS_R_2_V0 *CENSUS_R_2 +B_CENSUS_R_3_V0 *CENSUS_R_3+B_CENSUS_R_4_V0 *CENSUS_R_4 +B_MSACAT_V0 *MSACAT
V1 = ASC_LOW + B_SEX_V1 * R_SEX_IMP + B_HHSIZE_V1 * HHSIZE + B_WORKER_V1 *WORKER + B_EDUC_1_V1 *EDUC_1 + B_EDUC_2_V1 *EDUC_2 + B_EDUC_3_V1 *EDUC_3 + B_AGE_IMP_1_V1 *R_AGE_IMP_1+ B_AGE_IMP_2_V1 *R_AGE_IMP_2+B_AGE_IMP_3_V1 *R_AGE_IMP_3+\
    B_income_cls_1_V1 *income_cls_1+B_income_cls_2_V1 *income_cls_2+B_income_cls_3_V1 *income_cls_3 +B_CENSUS_R_2_V1 *CENSUS_R_2 +B_CENSUS_R_3_V1 *CENSUS_R_3+B_CENSUS_R_4_V1 *CENSUS_R_4 +B_MSACAT_V1 *MSACAT
V2 = ASC_MID + B_SEX_V2 * R_SEX_IMP + B_HHSIZE_V2 * HHSIZE + B_WORKER_V2 *WORKER + B_EDUC_1_V2 *EDUC_1 + B_EDUC_2_V2 *EDUC_2 + B_EDUC_3_V2 *EDUC_3 + B_AGE_IMP_1_V2 *R_AGE_IMP_1+ B_AGE_IMP_2_V2 *R_AGE_IMP_2+B_AGE_IMP_3_V2 *R_AGE_IMP_3+\
    B_income_cls_1_V2 *income_cls_1+B_income_cls_2_V2 *income_cls_2+B_income_cls_3_V2 *income_cls_3 +B_CENSUS_R_2_V2 *CENSUS_R_2 +B_CENSUS_R_3_V2 *CENSUS_R_3+B_CENSUS_R_4_V2 *CENSUS_R_4 +B_MSACAT_V2 *MSACAT
V3 = ASC_HIG + B_SEX_V3 * R_SEX_IMP + B_HHSIZE_V3 * HHSIZE + B_WORKER_V3 *WORKER + B_EDUC_1_V3 *EDUC_1 + B_EDUC_2_V3 *EDUC_2 + B_EDUC_3_V3 *EDUC_3 + B_AGE_IMP_1_V3 *R_AGE_IMP_1+ B_AGE_IMP_2_V3 *R_AGE_IMP_2+B_AGE_IMP_3_V3 *R_AGE_IMP_3+\
    B_income_cls_1_V3 *income_cls_1+B_income_cls_2_V3 *income_cls_2+B_income_cls_3_V3 *income_cls_3 +B_CENSUS_R_2_V3 *CENSUS_R_2 +B_CENSUS_R_3_V3 *CENSUS_R_3+B_CENSUS_R_4_V3 *CENSUS_R_4 +B_MSACAT_V3 *MSACAT
# Associate utility functions with the numbering of alternatives
V = {0: V0,1: V1, 2: V2, 3: V3}

# Associate the availability conditions with the alternatives
av = {0: Avail, 1: Avail, 2: Avail, 3: Avail}

# Definition of the model. This is the contribution of each
# observation to the log likelihood function.
logprob = models.loglogit(V, av, onlineshop)

# Create the Biogeme object
formulas = {'loglike': logprob, 'weight': WTPERFIN}
biogeme = bio.BIOGEME(database, formulas)
biogeme.modelName = 'onine_shop_logit'

# Calculate the null log likelihood for reporting.
biogeme.calculateNullLoglikelihood(av)

# Estimate the parameters
results = biogeme.estimate()

# Get the results in a pandas table
pandasResults = results.getEstimatedParameters()
print(pandasResults)    
# %%
database = db.Database('NHTS', df)

# The following statement allows you to use the names of the
# variable as Python variable.
globals().update(database.variables)

# Parameters to be estimated
## Intercept
ASC_NOS = Beta('ASC_NOS', 0, None, None, 1)
ASC_LOW = Beta('ASC_LOW', 0, None, None, 0)
ASC_MID = Beta('ASC_MID', 0, None, None, 0)
ASC_HIG = Beta('ASC_HIG', 0, None, None, 0)
## Beta
B_SEX= Beta('B_SEX', 0, None, None, 0)
B_HHSIZE= Beta('B_HHSIZE', 0, None, None, 0)
B_WORKER= Beta('B_WORKER', 0, None, None, 0)
B_MSACAT= Beta('B_MSACAT', 0, None, None, 0)
B_EDUC_1= Beta('B_EDUC_1', 0, None, None, 0)
B_EDUC_2= Beta('B_EDUC_2', 0, None, None, 0)
B_EDUC_3= Beta('B_EDUC_3', 0, None, None, 0)
B_AGE_IMP_1= Beta('B_AGE_IMP_1', 0, None, None, 0)
B_AGE_IMP_2= Beta('B_AGE_IMP_2', 0, None, None, 0)
B_AGE_IMP_3= Beta('B_AGE_IMP_3', 0, None, None, 0)
B_RACE_1= Beta('B_RACE_1', 0, None, None, 0)
B_RACE_2= Beta('B_RACE_2', 0, None, None, 0)
B_RACE_3= Beta('B_RACE_3', 0, None, None, 0)
B_income_cls_1= Beta('B_income_cls_1', 0, None, None, 0)
B_income_cls_2= Beta('B_income_cls_2', 0, None, None, 0)
B_income_cls_3= Beta('B_income_cls_3', 0, None, None, 0)
B_CENSUS_R_2= Beta('B_CENSUS_R_2', 0, None, None, 0)
B_CENSUS_R_3= Beta('B_CENSUS_R_3', 0, None, None, 0)
B_CENSUS_R_4= Beta('B_CENSUS_R_4', 0, None, None, 0)


# Definition of the utility functions
V0 = ASC_NOS + B_SEX * R_SEX_IMP + B_HHSIZE* HHSIZE + B_WORKER*WORKER + B_EDUC_1*EDUC_1 + B_EDUC_2*EDUC_2 + B_EDUC_3*EDUC_3 + B_AGE_IMP_1*R_AGE_IMP_1+ B_AGE_IMP_2*R_AGE_IMP_2+B_AGE_IMP_3*R_AGE_IMP_3+\
    B_income_cls_1*income_cls_1+B_income_cls_2*income_cls_2+B_income_cls_3*income_cls_3 +B_CENSUS_R_2*CENSUS_R_2 +B_CENSUS_R_3*CENSUS_R_3+B_CENSUS_R_4*CENSUS_R_4 +B_MSACAT*MSACAT
V1 = ASC_LOW + B_SEX * R_SEX_IMP + B_HHSIZE* HHSIZE + B_WORKER*WORKER + B_EDUC_1*EDUC_1 + B_EDUC_2*EDUC_2 + B_EDUC_3*EDUC_3 + B_AGE_IMP_1*R_AGE_IMP_1+ B_AGE_IMP_2*R_AGE_IMP_2+B_AGE_IMP_3*R_AGE_IMP_3+\
    B_income_cls_1*income_cls_1+B_income_cls_2*income_cls_2+B_income_cls_3*income_cls_3 +B_CENSUS_R_2*CENSUS_R_2 +B_CENSUS_R_3*CENSUS_R_3+B_CENSUS_R_4*CENSUS_R_4 +B_MSACAT*MSACAT
V2 = ASC_MID + B_SEX * R_SEX_IMP + B_HHSIZE* HHSIZE + B_WORKER*WORKER + B_EDUC_1*EDUC_1 + B_EDUC_2*EDUC_2 + B_EDUC_3*EDUC_3 + B_AGE_IMP_1*R_AGE_IMP_1+ B_AGE_IMP_2*R_AGE_IMP_2+B_AGE_IMP_3*R_AGE_IMP_3+\
    B_income_cls_1*income_cls_1+B_income_cls_2*income_cls_2+B_income_cls_3*income_cls_3 +B_CENSUS_R_2*CENSUS_R_2 +B_CENSUS_R_3*CENSUS_R_3+B_CENSUS_R_4*CENSUS_R_4 +B_MSACAT*MSACAT
V3 = ASC_HIG + B_SEX * R_SEX_IMP + B_HHSIZE* HHSIZE + B_WORKER*WORKER + B_EDUC_1*EDUC_1 + B_EDUC_2*EDUC_2 + B_EDUC_3*EDUC_3 + B_AGE_IMP_1*R_AGE_IMP_1+ B_AGE_IMP_2*R_AGE_IMP_2+B_AGE_IMP_3*R_AGE_IMP_3+\
    B_income_cls_1*income_cls_1+B_income_cls_2*income_cls_2+B_income_cls_3*income_cls_3 +B_CENSUS_R_2*CENSUS_R_2 +B_CENSUS_R_3*CENSUS_R_3+B_CENSUS_R_4*CENSUS_R_4 +B_MSACAT*MSACAT
# Associate utility functions with the numbering of alternatives
V = {0: V0,1: V1, 2: V2, 3: V3}

# Associate the availability conditions with the alternatives
av = {0: Avail, 1: Avail, 2: Avail, 3: Avail}

# Definition of the model. This is the contribution of each
# observation to the log likelihood function.
logprob = models.loglogit(V, av, onlineshop)

# Create the Biogeme object
formulas = {'loglike': logprob, 'weight': weight}
biogeme = bio.BIOGEME(database, logprob)
biogeme.modelName = 'onine_shop_logit'

# Calculate the null log likelihood for reporting.
biogeme.calculateNullLoglikelihood(av)

# Estimate the parameters
results = biogeme.estimate()

# Get the results in a pandas table
pandasResults = results.getEstimatedParameters()
print(pandasResults)   

######################## ATUS##########
# %%
## shopping nested 
database = db.Database('shop', atus_df)

# The following statement allows you to use the names of the
# variable as Python variable.
globals().update(database.variables)

# Parameters to be estimated
## Intercept
ASC_NOS = Beta('ASC_NOS', 0, None, None, 1)
ASC_OFF = Beta('ASC_OFF', 0, None, None, 0)
ASC_ONS = Beta('ASC_ONS', 0, None, None, 0)
ASC_BOT = Beta('ASC_BOT', 0, None, None, 0)
## Beta
B_SEX_V0= Beta('B_SEX_V0', 0, None, None, 1)
B_SEX_V1= Beta('B_SEX_V1', 0, None, None, 0)
B_SEX_V2= Beta('B_SEX_V2', 0, None, None, 0)
B_SEX_V3= Beta('B_SEX_V3', 0, None, None, 0)
###
B_HHSIZE_V0= Beta('B_SEX_V0', 0, None, None, 1)
B_HHSIZE_V1= Beta('B_SEX_V1', 0, None, None, 0)
B_HHSIZE_V2= Beta('B_SEX_V2', 0, None, None, 0)
B_HHSIZE_V3= Beta('B_SEX_V3', 0, None, None, 0)
###
B_WORKER_V0= Beta('B_WORKER_V0', 0, None, None, 1)
B_WORKER_V1= Beta('B_WORKER_V1', 0, None, None, 0)
B_WORKER_V2= Beta('B_WORKER_V2', 0, None, None, 0)
B_WORKER_V3= Beta('B_WORKER_V3', 0, None, None, 0)

###
B_MSACAT_V0= Beta('B_MSACAT_V0', 0, None, None, 1)
B_MSACAT_V1= Beta('B_MSACAT_V1', 0, None, None, 0)
B_MSACAT_V2= Beta('B_MSACAT_V2', 0, None, None, 0)
B_MSACAT_V3= Beta('B_MSACAT_V3', 0, None, None, 0)
###
B_EDUC_1_V0= Beta('B_EDUC_1_V0', 0, None, None, 1)
B_EDUC_1_V1= Beta('B_EDUC_1_V1', 0, None, None, 0)
B_EDUC_1_V2= Beta('B_EDUC_1_V2', 0, None, None, 0)
B_EDUC_1_V3= Beta('B_EDUC_1_V3', 0, None, None, 0)
###
B_EDUC_2_V0= Beta('B_EDUC_2_V0', 0, None, None, 1)
B_EDUC_2_V1= Beta('B_EDUC_2_V1', 0, None, None, 0)
B_EDUC_2_V2= Beta('B_EDUC_2_V2', 0, None, None, 0)
B_EDUC_2_V3= Beta('B_EDUC_2_V3', 0, None, None, 0)
###
B_EDUC_3_V0= Beta('B_EDUC_3_V0', 0, None, None, 1)
B_EDUC_3_V1= Beta('B_EDUC_3_V1', 0, None, None, 0)
B_EDUC_3_V2= Beta('B_EDUC_3_V2', 0, None, None, 0)
B_EDUC_3_V3= Beta('B_EDUC_3_V3', 0, None, None, 0)

###
B_AGE_IMP_1_V0= Beta('B_AGE_IMP_1_V0', 0, None, None, 1)
B_AGE_IMP_1_V1= Beta('B_AGE_IMP_1_V1', 0, None, None, 0)
B_AGE_IMP_1_V2= Beta('B_AGE_IMP_1_V2', 0, None, None, 0)
B_AGE_IMP_1_V3= Beta('B_AGE_IMP_1_V3', 0, None, None, 0)

###
B_AGE_IMP_2_V0= Beta('B_AGE_IMP_2_V0', 0, None, None, 1)
B_AGE_IMP_2_V1= Beta('B_AGE_IMP_2_V1', 0, None, None, 0)
B_AGE_IMP_2_V2= Beta('B_AGE_IMP_2_V2', 0, None, None, 0)
B_AGE_IMP_2_V3= Beta('B_AGE_IMP_2_V3', 0, None, None, 0)
###
B_AGE_IMP_3_V0= Beta('B_AGE_IMP_3_V0', 0, None, None, 1)
B_AGE_IMP_3_V1= Beta('B_AGE_IMP_3_V1', 0, None, None, 0)
B_AGE_IMP_3_V2= Beta('B_AGE_IMP_3_V2', 0, None, None, 0)
B_AGE_IMP_3_V3= Beta('B_AGE_IMP_3_V3', 0, None, None, 0)
###
B_RACE_1= Beta('B_RACE_1', 0, None, None, 0)
###
B_RACE_2= Beta('B_RACE_2', 0, None, None, 0)
###
B_RACE_3= Beta('B_RACE_3', 0, None, None, 0)
###
B_income_cls_1_V0= Beta('B_income_cls_1_V0', 0, None, None, 1)
B_income_cls_1_V1= Beta('B_income_cls_1_V1', 0, None, None, 0)
B_income_cls_1_V2= Beta('B_income_cls_1_V2', 0, None, None, 0)
B_income_cls_1_V3= Beta('B_income_cls_1_V3', 0, None, None, 0)
###
B_income_cls_2_V0= Beta('B_income_cls_2_V0', 0, None, None, 1)
B_income_cls_2_V1= Beta('B_income_cls_2_V1', 0, None, None, 0)
B_income_cls_2_V2= Beta('B_income_cls_2_V2', 0, None, None, 0)
B_income_cls_2_V3= Beta('B_income_cls_2_V3', 0, None, None, 0)
###
B_income_cls_3_V0= Beta('B_income_cls_3_V0', 0, None, None, 1)
B_income_cls_3_V1= Beta('B_income_cls_3_V1', 0, None, None, 0)
B_income_cls_3_V2= Beta('B_income_cls_3_V2', 0, None, None, 0)
B_income_cls_3_V3= Beta('B_income_cls_3_V3', 0, None, None, 0)
###
B_CENSUS_R_2_V0= Beta('B_CENSUS_R_2_V0', 0, None, None, 1)
B_CENSUS_R_2_V1= Beta('B_CENSUS_R_2_V1', 0, None, None, 0)
B_CENSUS_R_2_V2= Beta('B_CENSUS_R_2_V2', 0, None, None, 0)
B_CENSUS_R_2_V3= Beta('B_CENSUS_R_2_V3', 0, None, None, 0)
###
B_CENSUS_R_3_V0= Beta('B_CENSUS_R_3_V0', 0, None, None, 1)
B_CENSUS_R_3_V1= Beta('B_CENSUS_R_3_V1', 0, None, None, 0)
B_CENSUS_R_3_V2= Beta('B_CENSUS_R_3_V2', 0, None, None, 0)
B_CENSUS_R_3_V3= Beta('B_CENSUS_R_3_V3', 0, None, None, 0)
###
B_CENSUS_R_4_V0= Beta('B_CENSUS_R_4_V0', 0, None, None, 1)
B_CENSUS_R_4_V1= Beta('B_CENSUS_R_4_V1', 0, None, None, 0)
B_CENSUS_R_4_V2= Beta('B_CENSUS_R_4_V2', 0, None, None, 0)
B_CENSUS_R_4_V3= Beta('B_CENSUS_R_4_V3', 0, None, None, 0)


# Definition of the utility functions
V0 = ASC_NOS + B_SEX_V0 * R_SEX_IMP + B_HHSIZE_V0 * HHSIZE + B_WORKER_V0 *WORKER + B_EDUC_1_V0 *EDUC_1 + B_EDUC_2_V0 *EDUC_2 + B_EDUC_3_V0 *EDUC_3 + B_AGE_IMP_1_V0 *R_AGE_IMP_1+ B_AGE_IMP_2_V0 *R_AGE_IMP_2+B_AGE_IMP_3_V0 *R_AGE_IMP_3+\
    B_income_cls_1_V0 *income_cls_1+B_income_cls_2_V0 *income_cls_2+B_income_cls_3_V0 *income_cls_3 +B_CENSUS_R_2_V0 *CENSUS_R_2 +B_CENSUS_R_3_V0 *CENSUS_R_3+B_CENSUS_R_4_V0 *CENSUS_R_4 +B_MSACAT_V0 *MSACAT
V1 = ASC_OFF + B_SEX_V1 * R_SEX_IMP + B_HHSIZE_V1 * HHSIZE + B_WORKER_V1 *WORKER + B_EDUC_1_V1 *EDUC_1 + B_EDUC_2_V1 *EDUC_2 + B_EDUC_3_V1 *EDUC_3 + B_AGE_IMP_1_V1 *R_AGE_IMP_1+ B_AGE_IMP_2_V1 *R_AGE_IMP_2+B_AGE_IMP_3_V1 *R_AGE_IMP_3+\
    B_income_cls_1_V1 *income_cls_1+B_income_cls_2_V1 *income_cls_2+B_income_cls_3_V1 *income_cls_3 +B_CENSUS_R_2_V1 *CENSUS_R_2 +B_CENSUS_R_3_V1 *CENSUS_R_3+B_CENSUS_R_4_V1 *CENSUS_R_4 +B_MSACAT_V1 *MSACAT
V2 = ASC_ONS + B_SEX_V2 * R_SEX_IMP + B_HHSIZE_V2 * HHSIZE + B_WORKER_V2 *WORKER + B_EDUC_1_V2 *EDUC_1 + B_EDUC_2_V2 *EDUC_2 + B_EDUC_3_V2 *EDUC_3 + B_AGE_IMP_1_V2 *R_AGE_IMP_1+ B_AGE_IMP_2_V2 *R_AGE_IMP_2+B_AGE_IMP_3_V2 *R_AGE_IMP_3+\
    B_income_cls_1_V2 *income_cls_1+B_income_cls_2_V2 *income_cls_2+B_income_cls_3_V2 *income_cls_3 +B_CENSUS_R_2_V2 *CENSUS_R_2 +B_CENSUS_R_3_V2 *CENSUS_R_3+B_CENSUS_R_4_V2 *CENSUS_R_4 +B_MSACAT_V2 *MSACAT
V3 = ASC_BOT + B_SEX_V3 * R_SEX_IMP + B_HHSIZE_V3 * HHSIZE + B_WORKER_V3 *WORKER + B_EDUC_1_V3 *EDUC_1 + B_EDUC_2_V3 *EDUC_2 + B_EDUC_3_V3 *EDUC_3 + B_AGE_IMP_1_V3 *R_AGE_IMP_1+ B_AGE_IMP_2_V3 *R_AGE_IMP_2+B_AGE_IMP_3_V3 *R_AGE_IMP_3+\
    B_income_cls_1_V3 *income_cls_1+B_income_cls_2_V3 *income_cls_2+B_income_cls_3_V3 *income_cls_3 +B_CENSUS_R_2_V3 *CENSUS_R_2 +B_CENSUS_R_3_V3 *CENSUS_R_3+B_CENSUS_R_4_V3 *CENSUS_R_4 +B_MSACAT_V3 *MSACAT
# Associate utility functions with the numbering of alternatives
V = {0: V0,1: V1, 2: V2, 3: V3}

# Associate the availability conditions with the alternatives
av = {0: Avail, 1: Avail, 2: Avail, 3: Avail}

# nest parameters
NEST_SHOP=Beta('NEST_SHOP',1,1.0,10,0)

NO_SHOP =1.0, [0]
SHOP=NEST_SHOP, [1,2,3]

nests = NO_SHOP, SHOP
# Definition of the model. This is the contribution of each
# observation to the log likelihood function.
logprob = models.lognested(V, av, nests, shop_choice)

# Define level of verbosity
logger = msg.bioMessage()
# logger.setSilent()
# logger.setWarning()
logger.setGeneral()
# logger.setDetailed()

# Create the Biogeme object
biogeme = bio.BIOGEME(database, logprob)
biogeme.modelName = "shoping_nested"

# Calculate the null log likelihood for reporting.
biogeme.calculateNullLoglikelihood(av)

# Estimate the parameters
results = biogeme.estimate()
pandasResults = results.getEstimatedParameters()
print(pandasResults)

# Get the results in a pandas table
pandasResults = results.getEstimatedParameters()
print(pandasResults)    
# %%
## shopping nested 
database = db.Database('ondemand', atus_df)

# The following statement allows you to use the names of the
# variable as Python variable.
globals().update(database.variables)

# Parameters to be estimated
## Intercept
ASC_NOS = Beta('ASC_NOS', 0, None, None, 1)
ASC_OFF = Beta('ASC_OFF', 0, None, None, 0)
ASC_ONS = Beta('ASC_ONS', 0, None, None, 0)
ASC_BOT = Beta('ASC_BOT', 0, None, None, 0)
## Beta
B_SEX_V0= Beta('B_SEX_V0', 0, None, None, 1)
B_SEX_V1= Beta('B_SEX_V1', 0, None, None, 0)
B_SEX_V2= Beta('B_SEX_V2', 0, None, None, 0)
B_SEX_V3= Beta('B_SEX_V3', 0, None, None, 0)
###
B_HHSIZE_V0= Beta('B_SEX_V0', 0, None, None, 1)
B_HHSIZE_V1= Beta('B_SEX_V1', 0, None, None, 0)
B_HHSIZE_V2= Beta('B_SEX_V2', 0, None, None, 0)
B_HHSIZE_V3= Beta('B_SEX_V3', 0, None, None, 0)
###
B_WORKER_V0= Beta('B_WORKER_V0', 0, None, None, 1)
B_WORKER_V1= Beta('B_WORKER_V1', 0, None, None, 0)
B_WORKER_V2= Beta('B_WORKER_V2', 0, None, None, 0)
B_WORKER_V3= Beta('B_WORKER_V3', 0, None, None, 0)

###
B_MSACAT_V0= Beta('B_MSACAT_V0', 0, None, None, 1)
B_MSACAT_V1= Beta('B_MSACAT_V1', 0, None, None, 0)
B_MSACAT_V2= Beta('B_MSACAT_V2', 0, None, None, 0)
B_MSACAT_V3= Beta('B_MSACAT_V3', 0, None, None, 0)
###
B_EDUC_1_V0= Beta('B_EDUC_1_V0', 0, None, None, 1)
B_EDUC_1_V1= Beta('B_EDUC_1_V1', 0, None, None, 0)
B_EDUC_1_V2= Beta('B_EDUC_1_V2', 0, None, None, 0)
B_EDUC_1_V3= Beta('B_EDUC_1_V3', 0, None, None, 0)
###
B_EDUC_2_V0= Beta('B_EDUC_2_V0', 0, None, None, 1)
B_EDUC_2_V1= Beta('B_EDUC_2_V1', 0, None, None, 0)
B_EDUC_2_V2= Beta('B_EDUC_2_V2', 0, None, None, 0)
B_EDUC_2_V3= Beta('B_EDUC_2_V3', 0, None, None, 0)
###
B_EDUC_3_V0= Beta('B_EDUC_3_V0', 0, None, None, 1)
B_EDUC_3_V1= Beta('B_EDUC_3_V1', 0, None, None, 0)
B_EDUC_3_V2= Beta('B_EDUC_3_V2', 0, None, None, 0)
B_EDUC_3_V3= Beta('B_EDUC_3_V3', 0, None, None, 0)

###
B_AGE_IMP_1_V0= Beta('B_AGE_IMP_1_V0', 0, None, None, 1)
B_AGE_IMP_1_V1= Beta('B_AGE_IMP_1_V1', 0, None, None, 0)
B_AGE_IMP_1_V2= Beta('B_AGE_IMP_1_V2', 0, None, None, 0)
B_AGE_IMP_1_V3= Beta('B_AGE_IMP_1_V3', 0, None, None, 0)

###
B_AGE_IMP_2_V0= Beta('B_AGE_IMP_2_V0', 0, None, None, 1)
B_AGE_IMP_2_V1= Beta('B_AGE_IMP_2_V1', 0, None, None, 0)
B_AGE_IMP_2_V2= Beta('B_AGE_IMP_2_V2', 0, None, None, 0)
B_AGE_IMP_2_V3= Beta('B_AGE_IMP_2_V3', 0, None, None, 0)
###
B_AGE_IMP_3_V0= Beta('B_AGE_IMP_3_V0', 0, None, None, 1)
B_AGE_IMP_3_V1= Beta('B_AGE_IMP_3_V1', 0, None, None, 0)
B_AGE_IMP_3_V2= Beta('B_AGE_IMP_3_V2', 0, None, None, 0)
B_AGE_IMP_3_V3= Beta('B_AGE_IMP_3_V3', 0, None, None, 0)
###
B_RACE_1= Beta('B_RACE_1', 0, None, None, 0)
###
B_RACE_2= Beta('B_RACE_2', 0, None, None, 0)
###
B_RACE_3= Beta('B_RACE_3', 0, None, None, 0)
###
B_income_cls_1_V0= Beta('B_income_cls_1_V0', 0, None, None, 1)
B_income_cls_1_V1= Beta('B_income_cls_1_V1', 0, None, None, 0)
B_income_cls_1_V2= Beta('B_income_cls_1_V2', 0, None, None, 0)
B_income_cls_1_V3= Beta('B_income_cls_1_V3', 0, None, None, 0)
###
B_income_cls_2_V0= Beta('B_income_cls_2_V0', 0, None, None, 1)
B_income_cls_2_V1= Beta('B_income_cls_2_V1', 0, None, None, 0)
B_income_cls_2_V2= Beta('B_income_cls_2_V2', 0, None, None, 0)
B_income_cls_2_V3= Beta('B_income_cls_2_V3', 0, None, None, 0)
###
B_income_cls_3_V0= Beta('B_income_cls_3_V0', 0, None, None, 1)
B_income_cls_3_V1= Beta('B_income_cls_3_V1', 0, None, None, 0)
B_income_cls_3_V2= Beta('B_income_cls_3_V2', 0, None, None, 0)
B_income_cls_3_V3= Beta('B_income_cls_3_V3', 0, None, None, 0)
###
B_CENSUS_R_2_V0= Beta('B_CENSUS_R_2_V0', 0, None, None, 1)
B_CENSUS_R_2_V1= Beta('B_CENSUS_R_2_V1', 0, None, None, 0)
B_CENSUS_R_2_V2= Beta('B_CENSUS_R_2_V2', 0, None, None, 0)
B_CENSUS_R_2_V3= Beta('B_CENSUS_R_2_V3', 0, None, None, 0)
###
B_CENSUS_R_3_V0= Beta('B_CENSUS_R_3_V0', 0, None, None, 1)
B_CENSUS_R_3_V1= Beta('B_CENSUS_R_3_V1', 0, None, None, 0)
B_CENSUS_R_3_V2= Beta('B_CENSUS_R_3_V2', 0, None, None, 0)
B_CENSUS_R_3_V3= Beta('B_CENSUS_R_3_V3', 0, None, None, 0)
###
B_CENSUS_R_4_V0= Beta('B_CENSUS_R_4_V0', 0, None, None, 1)
B_CENSUS_R_4_V1= Beta('B_CENSUS_R_4_V1', 0, None, None, 0)
B_CENSUS_R_4_V2= Beta('B_CENSUS_R_4_V2', 0, None, None, 0)
B_CENSUS_R_4_V3= Beta('B_CENSUS_R_4_V3', 0, None, None, 0)


# Definition of the utility functions
V0 = ASC_NOS + B_SEX_V0 * R_SEX_IMP + B_HHSIZE_V0 * HHSIZE + B_WORKER_V0 *WORKER + B_EDUC_1_V0 *EDUC_1 + B_EDUC_2_V0 *EDUC_2 + B_EDUC_3_V0 *EDUC_3 + B_AGE_IMP_1_V0 *R_AGE_IMP_1+ B_AGE_IMP_2_V0 *R_AGE_IMP_2+B_AGE_IMP_3_V0 *R_AGE_IMP_3+\
    B_income_cls_1_V0 *income_cls_1+B_income_cls_2_V0 *income_cls_2+B_income_cls_3_V0 *income_cls_3 +B_CENSUS_R_2_V0 *CENSUS_R_2 +B_CENSUS_R_3_V0 *CENSUS_R_3+B_CENSUS_R_4_V0 *CENSUS_R_4 +B_MSACAT_V0 *MSACAT
V1 = ASC_OFF + B_SEX_V1 * R_SEX_IMP + B_HHSIZE_V1 * HHSIZE + B_WORKER_V1 *WORKER + B_EDUC_1_V1 *EDUC_1 + B_EDUC_2_V1 *EDUC_2 + B_EDUC_3_V1 *EDUC_3 + B_AGE_IMP_1_V1 *R_AGE_IMP_1+ B_AGE_IMP_2_V1 *R_AGE_IMP_2+B_AGE_IMP_3_V1 *R_AGE_IMP_3+\
    B_income_cls_1_V1 *income_cls_1+B_income_cls_2_V1 *income_cls_2+B_income_cls_3_V1 *income_cls_3 +B_CENSUS_R_2_V1 *CENSUS_R_2 +B_CENSUS_R_3_V1 *CENSUS_R_3+B_CENSUS_R_4_V1 *CENSUS_R_4 +B_MSACAT_V1 *MSACAT
V2 = ASC_ONS + B_SEX_V2 * R_SEX_IMP + B_HHSIZE_V2 * HHSIZE + B_WORKER_V2 *WORKER + B_EDUC_1_V2 *EDUC_1 + B_EDUC_2_V2 *EDUC_2 + B_EDUC_3_V2 *EDUC_3 + B_AGE_IMP_1_V2 *R_AGE_IMP_1+ B_AGE_IMP_2_V2 *R_AGE_IMP_2+B_AGE_IMP_3_V2 *R_AGE_IMP_3+\
    B_income_cls_1_V2 *income_cls_1+B_income_cls_2_V2 *income_cls_2+B_income_cls_3_V2 *income_cls_3 +B_CENSUS_R_2_V2 *CENSUS_R_2 +B_CENSUS_R_3_V2 *CENSUS_R_3+B_CENSUS_R_4_V2 *CENSUS_R_4 +B_MSACAT_V2 *MSACAT
V3 = ASC_BOT + B_SEX_V3 * R_SEX_IMP + B_HHSIZE_V3 * HHSIZE + B_WORKER_V3 *WORKER + B_EDUC_1_V3 *EDUC_1 + B_EDUC_2_V3 *EDUC_2 + B_EDUC_3_V3 *EDUC_3 + B_AGE_IMP_1_V3 *R_AGE_IMP_1+ B_AGE_IMP_2_V3 *R_AGE_IMP_2+B_AGE_IMP_3_V3 *R_AGE_IMP_3+\
    B_income_cls_1_V3 *income_cls_1+B_income_cls_2_V3 *income_cls_2+B_income_cls_3_V3 *income_cls_3 +B_CENSUS_R_2_V3 *CENSUS_R_2 +B_CENSUS_R_3_V3 *CENSUS_R_3+B_CENSUS_R_4_V3 *CENSUS_R_4 +B_MSACAT_V3 *MSACAT
# Associate utility functions with the numbering of alternatives
V = {0: V0,1: V1, 2: V2, 3: V3}

# Associate the availability conditions with the alternatives
av = {0: Avail, 1: Avail, 2: Avail, 3: Avail}

# nest parameters
NEST_OD=Beta('NEST_OD',1,1.0,10,0)

NO_OD =1.0, [0]
OD=NEST_OD, [1,2,3]

nests = NO_OD, OD
# Definition of the model. This is the contribution of each
# observation to the log likelihood function.
logprob = models.lognested(V, av, nests, shop_choice)

# Define level of verbosity
logger = msg.bioMessage()
# logger.setSilent()
# logger.setWarning()
logger.setGeneral()
# logger.setDetailed()

# Create the Biogeme object
biogeme = bio.BIOGEME(database, logprob)
biogeme.modelName = "ondemand_nested"

# Calculate the null log likelihood for reporting.
biogeme.calculateNullLoglikelihood(av)

# Estimate the parameters
results = biogeme.estimate()
pandasResults = results.getEstimatedParameters()
print(pandasResults)

# Get the results in a pandas table
pandasResults = results.getEstimatedParameters()
print(pandasResults)    
# %%
