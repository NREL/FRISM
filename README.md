# FRISM
### Contributors
Kyungsoo Jeong: <Kyungsoo.Jeong@nrel.gov>
<br>
Juliette Ugirumurera: <jugirumu@nrel.gov>
<br>

## Generating freight routes
Run Generalized_VRP.ipynb for generating freight routes

## Running the Vehicle Routing Problem
To generate freight tours, solve the vehicle routing problem as bellow:
<br>
```
python VRP-OR-tools.py -t <travel time gz file> -d <distance csv file> -ct <freight centroid csv file> -cr <carrier csv file> -pl <payload csv file> -vt <vehicle type csv file> -vc < vehicle by carrier csv file>
```

This will output three files:
payload.csv: csv file with payload information, when and where they were delivered
<br>
carrier.csv: csv file with tour information for each carrier and its vehicles
<br>
freight_tours.csv: csv file with freight tour information including departure location, departure time and maximum duration.
