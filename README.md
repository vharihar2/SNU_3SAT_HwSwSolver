# 3-SATSolver
# Netlist Generator
## Overview

This Python script generates a SPICE netlist based on the input matrix for CNF. It can be used for solving any 3-SAT problem containing at most 3 literals per clause. It is based on expanding the existing AC-SAT analog hardware solution. The script allows for the input, analysis, and netlist generation of a given set of clauses and variables, contributing significantly to the field of computational electronics.

## License

Copyright © 2024 Shiv Nadar University, Delhi NCR, India. All rights reserved.

This software is provided "as is", without warranty of any kind, express or implied. It can be used, copied, modified, and distributed for educational, research, and not-for-profit purposes without fee, provided the included copyright and permission notice are retained. Shiv Nadar University is not liable for any damages arising from the use of this software.

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

## Revision History

- **April 8, 2024:** Initial release by Sejal Singh.

## Support

This software is provided without maintenance, support, updates, enhancements, or modifications. For educational and research inquiries, please contact Shiv Nadar University.
