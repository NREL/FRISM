# NREL-eFRISM
### Electric Truck Routing Problem with Time Windows (ETRPTW)
Electric Freight Truck Route Optimization with optimal charging station location selection in US freight networks by using Variable Neighborhood Search metaheuristics. It also enhances freight operation capability to existing FReight Integrated Simulation Model (FRISM) by adding electric truck variant and optimal charging operation.

## **Overview**
This repository addresses ETRPTW, an extension of the traditional Vehicle Routing Problem (VRP). A fleet of electric trucks must visit customer locations, meeting time windows while considering battery constraints and charging station visits. The goal is to find feasible routes that minimize total travel time, customer service time, charging station visit costs, charging times and charging costs.

Due to its NP-hard nature, the EVRPTW requires efficient heuristics for large instances. This repository uses Google OR-Tools for an initial VRP solution, a custom charging station insertion algorithm, and a Variable Neighborhood Search (VNS) metaheuristic to find near-optimal solutions.

## Solution Approach
### Problem Breakdown
**Initial VRP Solution (Google OR-Tools)**: Obtain an initial VRP solution considering customer demands and time windows, excluding charging stations and battery constraints.

**Insert Charging Station Algorithm**: Modify each route to include charging stations as needed:

**Battery Constraints**: Ensure vehicles have sufficient battery capacity between nodes, detouring to charging stations if necessary. 

**Time Window**s: Check arrival and departure times at each node to ensure they fall within time windows.  

**Objective Function**: Minimize fixed vehicle costs, total travel time, customer service time, charging time and charging costs at charging stations for a well-defined feasible solution. 

**Variable Neighborhood Search (VNS)**: Starting with the feasible solution from the charging station insertion algorithm, VNS explores neighborhoods using various operators to improve the solution iteratively.  
The operators are:  
[
        **_intra_route_2opt_swap_**,  
        **_intra_route_or_opt_**,  
        **_inter_route_swap_**,  
        **_inter_route_relocate_**,  
        **_route_merge_**
    ] 

## **Detailed Solution Steps**  

**Step 1** - Data Preparation: Load EV fleet, customer demands, time windows, and charging stations.  

**Step 2** - Initial VRP Solution (Google OR-Tools): Solve the VRP with time windows and demand constraints.  

**Step 3** - Extract Initial Routes: Retrieve and filter routes serving customers.  

**Step 4** - Charging Station Insertion: Insert charging stations to ensure feasibility based on battery and time window constraints.  

**Step 5** - Variable Neighborhood Search (VNS): Apply VNS to further optimize feasible EVRPTW solutions, balancing travel time, service times, and charging costs.  

### **Solution Components**  

**Google OR-Tools**: For initial VRP solution.  

**Charging Station Insertion & Feasibility Check Algorithm**: Ensures routes are feasible under battery and time window constraints.  

**Variable Neighborhood Search (VNS)**: Optimizes total cost using neighborhood and local search operators.  

### Getting Started  

**Prerequisites**  

**_Python 3.7+_**  
**_Required libraries:_**  

**_ortools_**: Google OR-Tools for initial VRP solution.  
**_matplotlib_**: For route visualization.  
**_numpy_**, **_pandas_**: For data handling and calculations.  


## **To Run the Model**
1. Clone the repo  
2. Have **_Required libraries:_** be installed in your environment. Simply **_pip install [library_name]_** should work in python enviroment.
3. Navigate either ETRPTW or hetero_ETRPTW folder
4. In scripts folder, **_main.py_** scripts, you need to specify the problem size i.e. num_customers as per your requirements : Remember larger problem size, larger the solution execution time would be.
5. Corresponding dataset generated and final routing results with figures can be located at **_data_** and **_results_** folder.

