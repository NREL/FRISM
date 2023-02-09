# FRISM: FReight Integrated Simulation Model
## Contributors
Kyungsoo Jeong: <Kyungsoo.Jeong@nrel.gov>
<br>
Juliette Ugirumurera: <jugirumu@nrel.gov>
<br>

# THIS IS A SOFTWARE REPO

## Description
FRISM simulates day-to-day freight activities including end-consumer shopping, distribution channel, and carrier operation with e-commerce dynamics between passenger and freight travel. Its output are an assignment of different shipments to carriers and tour plans of the carriers' vehicles to transport shipments from their origins to their destinations.

## Access to input data
Origin destination travel time and distance matrices, as well as freight centroid zones for the San Francisco Bay Area can be found on this [google drive link](https://drive.google.com/drive/folders/14LSjFYH3BtmqUaaAVoPk3wPhGc2f2nBz).

## Setup python environment
```linux
conda env create -f environment.yml
```
Activate conda environment to run the code:
```linux
conda activate frism
```

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
