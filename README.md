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
- Running End-Consumer Behavior Module to simulate monthly delivery frequency
- Running Distribution Channel to simulate Business to Business (B2B) and Business to Consumer (B2C) daily shipments and shipment-carrier matching
- Running Carrier Operation to simulate tour-plan for each carrier.
The final output is a set of daily tour plans for each carrier's vehicles to transport shipments from their origins to their destinations.

## The following are contained in this repository
- TODO Kyungsoo : to add list of other code files in the rep
- Running Household E-commerce Generation Estimation for End-Consumer Behavior:
- Running End-Consumer Behavior Module to simulate monthly delivery frequency:
- Running Distribution Channel to simulate B2B and B2C daily shipments and shipment-carrier matching
- Running Carrier Operation to simulate tour-plan for each carrier:
    *   src/Simulation/VRP_OR-tools_Stops_veh_tech.py
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
3. To run the code, modify the input files as per this [README.md](https://github.com/NREL/FRISM/tree/open-source/src#readme) and run the following:
```linux
python src/Simulation/Run_frism.py
```

## Access to input data
Origin destination travel time and distance matrices, as well as freight centroid zones for the San Francisco Bay Area can be found on this [google drive link](https://drive.google.com/drive/folders/14LSjFYH3BtmqUaaAVoPk3wPhGc2f2nBz).

## Generating Freight Tours
To generate freight tours, solve the vehicle routing problem as bellow:
<br>
```
cd src/Simulation/
python VRP_OR-tools.py -t <travel time gz file> -d <distance csv file> -ct <freight centroid csv file> -cr <carrier csv file> -pl <payload csv file> -vt <vehicle type csv file>
```

This will output three files in the src/Sim_outputs/Tour_plan folder:
<br>
**_payload.csv**: csv file with payload information, when and where they were delivered.
<br>
**_carrier.csv**: csv file with tour information for each carrier and its vehicles.
<br>
**_freight_tours.csv**: csv file with freight tour information including departure location, departure time and maximum duration.

## Error Catching
If there are carriers for which tours could not be generated for some reason, they can be found in **error.csv** under src/Sim_outputs folder. This file has two columns: a **carrier** column that indicates the carrier id, and a **reason** column that indicates why a solution could not be calculated.
