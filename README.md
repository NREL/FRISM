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
FRISM simulates day-to-day freight activities including end-consumer shopping, distribution channel, and carrier operation with e-commerce dynamics between passenger and freight travel. It runs in four main steps:
- Running Household E-commerce Generation Estimation model for End-Consumer Behavior
- Running End-Consumer Behavior model to simulate monthly delivery frequency
- Running Distribution Channel to simulate Business to Business (B2B) and Business to Consumer (B2C) daily shipments and shipment-carrier matching
- Running Carrier Operation to simulate tour-plan for each carrier.
The final output is a set of daily tour plans for each carrier's vehicles to transport shipments from their origins to their destinations.

## The following are contained in this repository
- Running Household E-commerce Generation Estimation for End-Consumer Behavior:
    *   src/Simulation/E-Commerce_Generation/HH_ecom_models.py
    *   src/Simulation/E-Commerce_Generation/config.py
- Running End-Consumer Behavior Module to simulate monthly delivery frequency:
    *   src/Simulation/End-Consumer_Behavior/B2C_Generation.py
    *   src/Simulation/End-Consumer_Behavior/B2B_Generation.py
    *   src/Simulation/End-Consumer_Behavior/config.py
- Running Distribution Channel to simulate B2B and B2C daily shipments and shipment-carrier matching
    *   src/Simulation/B2B_B2C_Shipment/Shipment2Fleet_veh_tech.py
    *   src/Simulation/B2B_B2C_Shipment/config.py
- Running Carrier Operation to simulate tour-plan for each carrier:
    *   src/Simulation/Carrier_Tour_Plan/VRP_OR-tools_Stops_veh_tech.py
- Running the freight activity simulation:
    *   src/Simulation/Run_frism.py
- List of inputs to run simulation: [README.md](https://github.com/NREL/FRISM/tree/open-source/src#readme)

## Installation Instructions
### Setup conda environment
1. In your terminal load  environment.yml file
```linux
conda env create -f environment.yml
```
2. Activate "frism" environment
```linux
conda activate frism
```
3. To run the code, specify the input files as per this [README.md](https://github.com/NREL/FRISM/tree/open-source/src#readme) and run the following:
```linux
python src/Simulation/Run_frism.py [county number] [year] [scenario name]
```
