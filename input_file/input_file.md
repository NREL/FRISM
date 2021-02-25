Mock-up input files are created for carrier operation, which includes outputs from shipment assignment to carrier. 
Each carrier has a list of jobs (pickup, delivery, or pickup and delivery) that has to be completed within a day.

dictionary.csv: description of variables for each file

carrier_mock_up.csv: carrier(fleet) identifier

vehicle_type_mock_up.csv: vehicle charateristics in the freight system

freight_vehicles_mock_up.csv: population of vehicles in the freight system

payload_mock_up.csv: a list of shipments (packages) that is generated and assigned to carriers for a specific day (pre-day); key input file for tour plan

freight_tour_mock_up.csv: a list of tours that is generated and assigned to vehicles for a specific day (pre-day); output file from tour plan  

