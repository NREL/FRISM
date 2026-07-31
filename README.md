# FRISM: FReight Integrated Simulation Model
## Contributors
Kyungsoo Jeong: <Kyungsoo.Jeong@nrel.gov>
<br>
Juliette Ugirumurera: <jugirumu@nrel.gov>
<br>
Alicia Birky: <Alicia.Birky@nrel.gov>
<br>

## THIS IS A SOFTWARE REPO

## Description
FRISM simulates day-to-day freight activities including end-consumer shopping, distribution channel, and carrier operation with e-commerce dynamics between passenger and freight travel. It outputs an assignment of different shipments to carriers and tour plans of the carriers' vehicles to transport shipments from their origins to their destinations. This software is associated with NREL software record SWR-24-40.

## The following are contained in this repository
- Generate folder structure, input variables and input parameters across FRISM simulation  
    *   src/PSRC_Simulation/create_input_variable.py
- Running B2B Distribution channel:
    *   src/PSRC_Simulation/sim_b2b_shipment2fleet.py
- Running B2C Distribution channel:
    *   src/PSRC_Simulation/sim_b2c_shipment2fleet.py
- Running Carrier Operation to simulate tour-plan for each carrier:
    *   src/PSRC_Simulation/sim_tour_plan_generation.py 
- Aggregating tour plans and converting to trip table:
    *   src/PSRC_Simulation/tour_postprocessing.py
- Functions used for B2B/B2C Distribution channel:
    *   src/PSRC_Simulation/frism_utility_distributionchannel.py
- Functions used for B2B/B2C Carrier Operation:
    *   src/PSRC_Simulation/frism_utility_tourplan.py
- Processing shipment and network inputs for Distribution channel:
    *   src/PSRC_Simulation/frism_pop_shipment.py
- Processing vehicle operational pattern inputs for Distribution channel:
    *   src/PSRC_Simulation/frism_vehicle_pattern.py      


## Installation Instructions
### Setup conda environment
1. In your terminal load  environment.yml file
```linux
conda env create -f environment.yml
```
2. Activate *frism* environment
```linux
conda activate frism
```
3. To run the code, first specify the input parameters for all the modules in the [Run_frism.py](https://github.com/NREL/FRISM/blob/open-source/src/Simulation/Run_frism.py) script as per this [README.md](https://github.com/NREL/FRISM/tree/open-source/src#readme). Then run the following:
```linux
cd src/Simulation
python Run_FRISM_PSRC.py
```

