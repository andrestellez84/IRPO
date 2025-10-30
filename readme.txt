Instructions for Using the Code to Solve the PSO Matching Problem

This document explains how to use the provided code to solve the PSO (Professional Service Organization) matching problem using the following three methods:

MCM proposed method

Naive-Greedy algorithm

Intelligent-Greedy algorithm

Folder Structure

Each method has its own subfolder named accordingly. Inside each folder, you will find a Python file (.py) containing the implementation for that specific method.
All three files share the same structure and use identical input and output formats.

Input Data

Each method requires a matching score matrix as input.
An example matrix named "MatchingScoreV8.csv" is included in this same folder.
You must update the variable "archivoMS" in each code file to indicate the correct location and filename of the matching score matrix.

Running the Code

By executing any of the .py files, the program will:

Analyze and process the input data,

Create and solve the corresponding PSO problem, and

Generate three output files containing information about the obtained solution.

The generated files are:

OutRPO_KPI_*.csv
Contains the Key Performance Indicators (KPIs) of the solution, formatted similarly to those discussed in the "Results" section of the documentation.

OutRPO_Positions_*.csv
Lists, for each open position in each job, the corresponding assignment.
The columns are defined as follows:
pos: position to fill
job: job to which the position belongs
perStart: period when the position starts
perToFill: number of periods to be filled by a worker
ResAsig: assigned resource or worker
ResType: resource type (qualified, trained, or hired)
ResRedy: period when the assigned resource becomes ready to work
ResStart: period when the assigned resource starts working
LedTime: lead time required for training or hiring
Filled: number of filled periods
Gap: number of unassigned periods
AsigC: assignment cost
GapC: gap cost
TotC: total cost
MS: matching score of the assigned resource

OutRPO_Visual_*.csv
Provides a visual representation of the assignments across time periods:
1 indicates an assigned resource,
0 represents a gap, and
an empty cell means that no demand for that position exists in that period.

Parameters

The parameter "semilla" sets the random seed for instance generation.
All other problem-related parameters can be modified within the "crearDatosbase" function.
By default, these are set to the values described in the "Use Case" experimentation section.



For further information or assistance, please contact the authors.



