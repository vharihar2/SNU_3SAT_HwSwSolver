# 3-SATSolver
# Netlist Generator

## Overview
This code dynamically generates and simulates a circuit netlist for efficiently solving a k-SAT problem using analog circuit simulations. It is based on a theory described in the literature[1], and we (Sejal Singh and Bhavani Namrata) developed it as part of our BTech Project in Shiv Nadar Institution of Eminence under the guidance of Dr. Venkatnarayan Hariharan.

## Features
- Input a matrix of clauses (rows) and variables (columns).
- Analysis of the matrix to display positive and negative literals in clauses.
- Generation of a netlist for the specified problem.
- Writing the generated netlist to a file for further analysis.

## Usage
1. Run the script in a Python environment.
2. When prompted, enter the number of clauses (rows) and variables (columns).
3. Input the matrix values as instructed by the script.
4. The script will process the input and generate a netlist, which will be written to the specified output file.

## Requirements
- Python 3.x

## References
[1] X. Yin, B. Sedighi, M. Varga, M. Ercsey-Ravasz, Z. Toroczkai, and X. S. Hu, “Efficient analog circuits for boolean satisfiability,” IEEE Transactions on Very Large Scale Integration (VLSI) Systems, vol. 26, no. 1, pp. 155–167, 201
