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
FRISM simulates day-to-day freight activities including end-consumer shopping, distribution channel, and carrier operation with e-commerce dynamics between passenger and freight travel. It outputs an assignment of different shipments to carriers and tour plans of the carriers' vehicles to transport shipments from their origins to their destinations.

## The following are contained in this repository
- Running Household E-commerce Generation Estimation for End-Consumer Behavior:
    *   src/Simulation/HH_ecom_models.py
- Running End-Consumer Behavior Module to simulate monthly delivery frequency:
    *   src/Simulation/B2C_Generation.py
    *   src/Simulation/B2B_Generation.py
- Running Distribution Channel to simulate B2B and B2C daily shipments and shipment-carrier matching
    *   src/Simulation/Shipment2Fleet_veh_tech.py
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
cd src/Simulation
python Run_frism.py [county number] [year] [scenario name] [sampling rate] [Y or N]
```
Y for the last input parameter means there will be generation of new shipments in the 'Shipment2Fleet_veh_tech.py' script, while N means no generation of new shipment in the 'Shipment2Fleet_veh_tech.py' script.

An example of the above command that use the data in the 'Example_Data' folder is:
```linux
cd src/Simulation
python Run_frism.py 21 2030 high 10 Y
```

The output of the above simulation will be saved in a 'FRISM_input_output_AT' outside of the repository folder.
