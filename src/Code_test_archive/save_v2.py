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
B_AGE_IMP_0_V0= Beta('B_AGE_IMP_0_V0', 0, None, None, 1)
B_AGE_IMP_0_V1= Beta('B_AGE_IMP_0_V1', 0, None, None, 0)
B_AGE_IMP_0_V2= Beta('B_AGE_IMP_0_V2', 0, None, None, 0)
B_AGE_IMP_0_V3= Beta('B_AGE_IMP_0_V3', 0, None, None, 0)

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
B_RACE_3_V0= Beta('B_RACE_3_V0', 0, None, None, 0)
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
#Prob_no_V0= Beta('Prob_no_V0', 0, None, None, 1)
NO_V1= Beta('NO_V1', 0, None, None, 0)
NO_V2= Beta('NO_V2', 0, None, None, 0)
NO_V3= Beta('NO_V3', 0, None, None, 0)

LO_V0= Beta('LO_V0', 0, None, None, 1)
LO_V1= Beta('LO_V1', 0, None, None, 0)
LO_V2= Beta('LO_V2', 0, None, None, 0)
LO_V3= Beta('LO_V3', 0, None, None, 0)
###
MD_V0= Beta('MD_V0', 0, None, None, 1)
MD_V1= Beta('MD_V1', 0, None, None, 0)
MD_V2= Beta('MD_V2', 0, None, None, 0)
MD_V3= Beta('MD_V3', 0, None, None, 0)
##
HI_V0= Beta('HI_V0', 0, None, None, 1)
HI_V1= Beta('HI_V1', 0, None, None, 0)
HI_V2= Beta('HI_V2', 0, None, None, 0)
HI_V3= Beta('HI_V3', 0, None, None, 0)


# Definition of the utility functions
V0 =  ASC_NOS + B_SEX_V0 * R_SEX_IMP + B_HHSIZE_V0 * HHSIZE + B_WORKER_V0 *WORKER + B_EDUC_0_V0 *EDUC_0 +B_AGE_IMP_3_V0 *R_AGE_IMP_3 +\
    B_MSACAT_V0 *MSACAT + B_INC_V0 * income_val

V1 = ASC_OFF + B_SEX_V1 * R_SEX_IMP  +\
   B_MSACAT_V1 *MSACAT +\
        NO_V1*Prob_no+LO_V1*Prob_lo+MD_V1*Prob_md +HI_V1*Prob_hi 

V2 = ASC_ONS + B_SEX_V2 * R_SEX_IMP + B_HHSIZE_V2 * HHSIZE +\
     B_MSACAT_V2 *MSACAT +\
        NO_V2*Prob_no+LO_V2*Prob_lo+MD_V2*Prob_md +HI_V2*Prob_hi 

V3 = ASC_BOT + B_SEX_V3 * R_SEX_IMP + B_HHSIZE_V3 * HHSIZE +\
   B_MSACAT_V3 *MSACAT +\
        NO_V3*Prob_no+LO_V3*Prob_lo+MD_V3*Prob_md +HI_V3*Prob_hi 

# Associate utility functions with the numbering of alternatives
# Associate utility functions with the numbering of alternatives
V = {0: V0,1: V1, 2: V2, 3: V3}

# Associate the availability conditions with the alternatives
av = {0: 1, 1: 1, 2: 1, 3: 1}

# nest parameters
NEST_SHOP=Beta('NEST_SHOP',1,1.0,20,0)

NO_SHOP =1.0, [0]
SHOP=NEST_SHOP, [1,2,3]

nests = NO_SHOP, SHOP
# Definition of the model. This is the contribution of each
# observation to the log likelihood function.
logprob = models.lognested(V, av, nests, general_choice)

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
B_EDUC_0_V0= Beta('B_EDUC_0_V0', 0, None, None, 1)
B_EDUC_0_V1= Beta('B_EDUC_0_V1', 0, None, None, 0)
B_EDUC_0_V2= Beta('B_EDUC_0_V2', 0, None, None, 0)
B_EDUC_0_V3= Beta('B_EDUC_0_V3', 0, None, None, 0)
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
B_AGE_IMP_0_V0= Beta('B_AGE_IMP_0_V0', 0, None, None, 1)
B_AGE_IMP_0_V1= Beta('B_AGE_IMP_0_V1', 0, None, None, 0)
B_AGE_IMP_0_V2= Beta('B_AGE_IMP_0_V2', 0, None, None, 0)
B_AGE_IMP_0_V3= Beta('B_AGE_IMP_0_V3', 0, None, None, 0)

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
#Prob_no_V0= Beta('Prob_no_V0', 0, None, None, 1)
NO_V1= Beta('NO_V1', 0, None, None, 0)
NO_V2= Beta('NO_V2', 0, None, None, 0)
NO_V3= Beta('NO_V3', 0, None, None, 0)

LO_V0= Beta('LO_V0', 0, None, None, 1)
LO_V1= Beta('LO_V1', 0, None, None, 0)
LO_V2= Beta('LO_V2', 0, None, None, 0)
LO_V3= Beta('LO_V3', 0, None, None, 0)
###
MD_V0= Beta('MD_V0', 0, None, None, 1)
MD_V1= Beta('MD_V1', 0, None, None, 0)
MD_V2= Beta('MD_V2', 0, None, None, 0)
MD_V3= Beta('MD_V3', 0, None, None, 0)
##
HI_V0= Beta('HI_V0', 0, None, None, 1)
HI_V1= Beta('HI_V1', 0, None, None, 0)
HI_V2= Beta('HI_V2', 0, None, None, 0)
HI_V3= Beta('HI_V3', 0, None, None, 0)


# Definition of the utility functions
V0 = ASC_NOS + B_SEX_V0 * R_SEX_IMP + B_HHSIZE_V0 * HHSIZE + B_WORKER_V0 *WORKER + B_EDUC_1_V0 *EDUC_1 + B_EDUC_2_V0 *EDUC_2 + B_EDUC_3_V0 *EDUC_3 + B_AGE_IMP_1_V0 *R_AGE_IMP_1+ B_AGE_IMP_2_V0 *R_AGE_IMP_2+B_AGE_IMP_3_V0 *R_AGE_IMP_3+\
   B_RACE_1_V0 *R_RACE_1+B_RACE_2_V0 *R_RACE_2 +B_CENSUS_R_2_V0 *CENSUS_R_2 +B_CENSUS_R_3_V0 *CENSUS_R_3+B_CENSUS_R_4_V0 *CENSUS_R_4 +B_MSACAT_V0 *MSACAT + B_INC_V0 * income_val

V1 = B_SEX_V1 * R_SEX_IMP + B_HHSIZE_V1 * HHSIZE + B_WORKER_V1 *WORKER + B_EDUC_1_V1 *EDUC_1 + B_EDUC_2_V1 *EDUC_2 + B_EDUC_3_V1 *EDUC_3 + B_AGE_IMP_1_V1 *R_AGE_IMP_1+ B_AGE_IMP_2_V1 *R_AGE_IMP_2+B_AGE_IMP_3_V1 *R_AGE_IMP_3+\
   B_RACE_1_V1 *R_RACE_1+B_RACE_2_V1 *R_RACE_2+B_CENSUS_R_2_V1 *CENSUS_R_2 +B_CENSUS_R_3_V1 *CENSUS_R_3+B_CENSUS_R_4_V1 *CENSUS_R_4 +B_MSACAT_V1 *MSACAT + B_INC_V1 * income_val+\
        NO_V1*Prob_no+LO_V1*Prob_lo+MD_V1*Prob_md +HI_V1*Prob_hi 

V2 = ASC_ONS + B_SEX_V2 * R_SEX_IMP + B_HHSIZE_V2 * HHSIZE + B_WORKER_V2 *WORKER + B_EDUC_1_V2 *EDUC_1 + B_EDUC_2_V2 *EDUC_2 + B_EDUC_3_V2 *EDUC_3 + B_AGE_IMP_1_V2 *R_AGE_IMP_1+ B_AGE_IMP_2_V2 *R_AGE_IMP_2+B_AGE_IMP_3_V2 *R_AGE_IMP_3+\
   B_RACE_1_V2 *R_RACE_1+B_RACE_2_V2 *R_RACE_2 +B_CENSUS_R_2_V2 *CENSUS_R_2 +B_CENSUS_R_3_V2 *CENSUS_R_3+B_CENSUS_R_4_V2 *CENSUS_R_4 +B_MSACAT_V2 *MSACAT + B_INC_V2 * income_val+\
        NO_V2*Prob_no+LO_V2*Prob_lo+MD_V2*Prob_md +HI_V2*Prob_hi 

V3 = ASC_BOT +B_SEX_V3 * R_SEX_IMP + B_HHSIZE_V3 * HHSIZE + B_WORKER_V3 *WORKER + B_EDUC_1_V3 *EDUC_1 + B_EDUC_2_V3 *EDUC_2 + B_EDUC_3_V3 *EDUC_3 + B_AGE_IMP_1_V3 *R_AGE_IMP_1+ B_AGE_IMP_2_V3 *R_AGE_IMP_2+B_AGE_IMP_3_V3 *R_AGE_IMP_3+\
   B_RACE_1_V3 *R_RACE_1+B_RACE_2_V3 *R_RACE_2 +B_CENSUS_R_2_V3 *CENSUS_R_2 +B_CENSUS_R_3_V3 *CENSUS_R_3+B_CENSUS_R_4_V3 *CENSUS_R_4 +B_MSACAT_V3 *MSACAT+ B_INC_V3 * income_val+\
        NO_V3*Prob_no+LO_V3*Prob_lo+MD_V3*Prob_md +HI_V3*Prob_hi 

# Associate utility functions with the numbering of alternatives
# Associate utility functions with the numbering of alternatives
V = {0: V0,1: V1, 2: V2, 3: V3}

# Associate the availability conditions with the alternatives
av = {0: 1, 1: 1, 2: 1, 3: 1}

# nest parameters
NEST_SHOP=Beta('NEST_SHOP',1,1.0,20,0)

NO_SHOP =1.0, [0]
SHOP=NEST_SHOP, [1,2,3]

nests = NO_SHOP, SHOP
# Definition of the model. This is the contribution of each
# observation to the log likelihood function.
logprob = models.lognested(V, av, nests, general_choice)

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