#
#$Id: AnalogSATsolverNetlistGenerator.py,v 1.2 2024/04/30 05:20:48 ss147 Exp ss147 $
#
"""
################################################################################
Copyright (c) 2024, Shiv Nadar University, Delhi NCR, India. All Rights
Reserved. Permission to use, copy, modify and distribute this software for
educational, research, and not-for-profit purposes, without fee and without a
signed license agreement, is hereby granted, provided that this paragraph and
the following two paragraphs appear in all copies, modifications, and
distributions.
IN NO EVENT SHALL SHIV NADAR UNIVERSITY BE LIABLE TO ANY PARTY FOR DIRECT,
INDIRECT, SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST
PROFITS, ARISING OUT OF THE USE OF THIS SOFTWARE.
SHIV NADAR UNIVERSITY SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT
NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE. THE SOFTWARE PROVIDED HEREUNDER IS PROVIDED "AS IS". SHIV
NADAR UNIVERSITY HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
ENHANCEMENTS, OR MODIFICATIONS.


Revision History:
Date        By            Change Notes
----------- ------------- ------------------------------------------
 8 Apr 2024 Sejal Singh   Netlist generation code
  
26 Apr 2024 Sejal Singh   Edits made according to Spectre simulation
                          debugging and change in the method of input 
                          & m-input NAND gate function.
                                       
27 Apr 2024 Sejal Singh   Added elaborate comments for the functions used
30 Apr 2024 Venkat H      Removed Windows-specific path usage, and made it
                          OS-agnostic
 
################################################################################
"""

def main():


      
    def input_matrix(file_path):
        """
    Read a matrix from a file, excluding comment lines and empty lines.

    This function opens a file from the specified path and reads its contents to form a matrix.
    Each line in the file represents a row in the matrix, but lines that start with '#' (comments)
    or are completely empty are ignored. Each row is split into integers, forming the matrix.

    Parameters:
    file_path (str): The path to the file containing the matrix data.

    Returns:
    list[list[int]]: A 2D list of integers forming the matrix read from the file.
    """
        with open(file_path, 'r') as file:
        # Read all lines in the file
            lines = file.readlines()
        
        # Initialize the matrix
            matrix = []
        
        # Convert each line to a row in the matrix, ignoring lines that are comments or empty
            for line in lines:
                if not line.startswith('#') and line.strip() != '':
                    row = list(map(int, line.strip().split()))
                    matrix.append(row)
        
        return matrix
    
    

    def display_pos(matrix):
        """
    Display the matrix as clauses in either POS (Positive) or CNF (Conjunctive Normal Form) notation.

    This function takes a matrix where each row represents a clause, and each element in the row
    represents the state of a variable in the clause (1, -1, or 0). It then formats and prints
    each clause in a readable logical expression where 'xN' represents the N-th variable:
    - 'xN' for a positive variable (1),
    - 'xN'' (xN prime) for a negative variable (-1),
    - Skips the variable if its state is 0.

    Parameters:
    matrix (list[list[int]]): The matrix where each row represents a clause.
    """
        for row in matrix:
            clause = []
            for i, val in enumerate(row):
                if val == 1:
                    clause.append(f"x{i+1}")
                elif val == -1:
                    clause.append(f"x{i+1}'")
            print(f"({' OR '.join(clause)})")



    def find_first_non_zero(clause):
        """
    Find the index of the first non-zero variable in a clause.

    This function scans through a list representing a clause and returns the index of the first element
    that is non-zero. This is useful in algorithms that need to identify the first significant variable
    in a clause for further processing.

    Parameters:
    clause (list): The clause represented as a list of variable states.

    Returns:
    int or None: The index of the first non-zero variable, or None if all variables are zero.
    """
        for index, var in enumerate(clause):
            if var != 0:
                return index
        return None
    
    
    #function to find the index of the last non-zero variable
    """ def find_last_non_zero(clause):
        last_index = None
        for index, var in enumerate(clause):
            if var != 0:
                last_index = index
        return last_index"""



    def generate_avc_element(clause_matrix):
        """
    Generates the netlist for an Auxiliary Variable Circuit (AVC) based on the given matrix of clauses.

    This function constructs a SPICE-like netlist describing the internal connections of an AVC block.
    Each row in the input matrix represents a clause, and each element in the row indicates the state
    of a variable in the clause (non-zero means the variable is active). The function iterates over
    each clause, adds subcircuit headers, and creates connections based on the state of each variable.
    It handles the first non-zero variable in each clause specially to differentiate its connections.
    Other non-zero variables are connected in series using transistors. The function also adds components
    like operational amplifiers and capacitors specific to each clause's subcircuit.

    Parameters:
    clause_matrix (list[list[int]]): A matrix where each row represents a clause and each element
    in a row represents the state of a variable in the clause (1 for positive, -1 for negative, 0 for inactive).

    Returns:
    str: A string containing the complete netlist for the AVC based on the given clause matrix.
    """
        #Function to write netlist of internal connections of AVC block according to every clause 
        avc_netlist = ""
        net_counter=1 #to keep count of the nets in each subcircuit
        for clause_id, clause in enumerate(clause_matrix):
            # Add header for the subcircuit
            avc_netlist += f"* Clause {clause_id+1} element in AVC\n"
            avc_netlist += f".subckt avc{clause_id+1} Vam{clause_id+1} EN"
            for var_id, var_state in enumerate(clause):
                if var_state != 0:
                    avc_netlist += f" V{var_id+1}"
            avc_netlist += "\n"

            # Handle the first non-zero variable differently
            first_non_zero_index = find_first_non_zero(clause)
            for var_id, presence in enumerate(clause):
                if presence != 0:
                # Handle the first non-zero variable differently as its connections are different (its one terminal is connected to either gnd or the sw)
                    if var_id == first_non_zero_index:
                        connection = 'Vdd' if presence == 1 else '0'
                        avc_netlist += f"X{clause_id}_{var_id} net0 net1 {connection} V{var_id+1} TR2\n"
                        avc_netlist += f"X{clause_id}_{var_id+1} 0 net101 {connection} V{var_id+1} TR2\n"
                        pass
                    else: #for the other non-zero variables, connection of TR2 instances in series
                        if presence != 0:
                            connection = 'Vdd' if presence == 1 else '0'
                            # Adjust the instance numbering to avoid repetition
                            avc_netlist += f"X1{clause_id}_{net_counter} net{net_counter} net{net_counter+1} {connection} V{var_id+1} TR2\n"
                            avc_netlist += f"X2{clause_id}_{net_counter} net{net_counter+100} net{net_counter+101} {connection} V{var_id+1} TR2\n"
                            net_counter += 1  # Increment for the next net name
                        pass
                
            # Add the opamp and branch components (sw, capacitors) for the clause element
            avc_netlist += f"XOP{clause_id} net{net_counter} net{net_counter+100} Vam{clause_id+1} mod_amp\n"
            avc_netlist += f"C{clause_id}_0 net{net_counter} 0 1p\n"
            avc_netlist += f"C{clause_id}_1 net{net_counter+100} Vam{clause_id+1} 1p\n"
            avc_netlist += f"XI{clause_id}_2 net0 Vam{clause_id+1} EN sw\n"
            avc_netlist += f".ends avc{clause_id+1}\n\n"  
        return avc_netlist
    

    
    def generate_avc_top_element(clause_matrix):
        """
    Generates the top-level netlist for an Auxiliary Variable Circuit (AVC) using a matrix of clauses.

    This function constructs the top-level netlist for an AVC by defining a subcircuit that integrates
    multiple internal AVC subcircuits, each corresponding to a clause from the clause matrix. It creates
    connections between the inputs of the top-level AVC block and the inputs of each internal AVC
    subcircuit, as well as manages the output nets.

    The function iterates over the variables and clauses in the matrix to generate appropriate connections
    for each AVC subcircuit within the top-level AVC block. It includes the necessary inputs for each
    clause subcircuit based on active variables in the clause and instantiates each internal AVC subcircuit.

    After constructing the top-level AVC netlist, this function calls `generate_avc_element` to get
    the netlists for individual AVC clauses and combines them with the top-level netlist to form
    a complete AVC system netlist.

    Parameters:
    clause_matrix (list[list[int]]): A matrix where each row represents a clause, and each element
    in a row represents the state of a variable in the clause (1 for positive, -1 for negative, 0 for inactive).

    Returns:
    str: A string containing the complete netlist for the AVC, including both the top-level and
    individual clause-level netlists.
    """
        #function for creating a top module for the AVC block connecting the internal avc element pins to outside circuit 
        top_avc_netlist = "* Top Level AVC Block\n"
        top_avc_netlist += ".subckt AVC EN"
        
        # Add all Vi inputs to the top-level AVC block
        for var_id in range(len(clause_matrix[0])):
            top_avc_netlist += f" V{var_id+1}"
        for clause_id, clause in enumerate(clause_matrix):
            top_avc_netlist += f" Vam{clause_id+1}"
        top_avc_netlist += "\n"

        # Include individual AVC clause subcircuits
        for clause_id, clause in enumerate(clause_matrix):
            # Connect Vi inputs to corresponding AVC{clause_id} subcircuit inputs
            inputs = " ".join([f"V{var_id+1}" for var_id, var_state in enumerate(clause) if var_state != 0])
            # Instantiate each AVC{clause_id} with the corresponding inputs and an internal Vam net
            top_avc_netlist += f"Xavc{clause_id+1} Vam{clause_id+1} EN {inputs} avc{clause_id+1}\n"
        top_avc_netlist += f".ends AVC\n"
        
        # Combine with the individual AVC clauses netlists
        avc_netlist = generate_avc_element(clause_matrix)
        complete_netlist = avc_netlist + top_avc_netlist
        return complete_netlist
    


    def generate_sdc_element(matrix):
        """
    Generates a SPICE netlist for a Signal Dynamic Circuit (SDC) block using a matrix
    where each row represents a different clause and each column
    corresponds to a variable in the CNF.

    This function constructs a subcircuit for the SDC block, where each variable has a dedicated
    branch that handles different states according to the matrix. The netlist includes transistor
    instances (TR1 and TR2) for logic processing, resistance for convergence, and capacitors for
    stability or delay purposes. The output is modulated through inverters and Schmitt triggers
    to produce a cleaned and stabilized output signal for each variable.

    Parameters:
    matrix (list[list[int]]): A 2D list where each row represents a clause and each element
                              in a row represents the state of a variable (1 for positive, -1 for negative, 
                              and 0 for inactive).

    Returns:
    str: A string containing the complete netlist for the SDC block. This netlist can be used
         directly in SPICE simulations to model the described configurable logic behavior.
    """
        #function for generating the SDC block connections
        netlist = "*Element in SDC\n"
        netlist += f".subckt SDC"
        #header for the subcircuits
        # Assuming each row has the same number of columns
        net_counter = 1  # Unique identifier for each net in the netlist
        for var_id in range(num_variables):
            netlist += f" Q{var_id+1}"
            netlist += f" V{var_id+1}"
        for clause_id, clause in enumerate(matrix):
            netlist += f" Vam{clause_id+1}"
        netlist += "\n"
        #creating the clause-wise branches for each variable separately 
        for var_id in range(num_variables):
            netlist += f"*Variable {var_id+1} branches\n"
            previous_nets = []

            #for creating the TR1 instance for every clause where this particular variable is present
            for clause_id, clause in enumerate(matrix):
                var_presence = clause[var_id]
                if var_presence != 0:
                    state = 'Vdd' if var_presence == 1 else '0'
                    netlist += f"XTR1_{var_id+1}_{clause_id} net{net_counter} {state} Vdd Vam{clause_id+1} TR1\n"
                    current_net = f"net{net_counter}"
                    net_counter += 1

                    # Add TR2 instances for every other variable in the clause
                    for other_var_id, other_var_presence in enumerate(clause):
                        if other_var_id != var_id and other_var_presence != 0:
                            other_state = 'Vdd' if other_var_presence == 1 else '0'
                            netlist += f"XTR2_{var_id+1}_{clause_id}_{other_var_id+1} {current_net} net{net_counter} {other_state} V{other_var_id+1} TR2\n"
                            current_net = f"net{net_counter}"
                            net_counter += 1
                    previous_nets.append(current_net)

            if previous_nets:
                # Convergence point for the branches of this variable across all clauses
                convergence_net = f"net{net_counter}"
                net_counter += 1

                for end_net in previous_nets:
                    netlist += f"R{var_id+1}_{end_net} {end_net} {convergence_net} 0\n"

                # Final connections to capacitor and Schmitt trigger for this variable through the convergence point
                netlist += f"C{var_id+1} {convergence_net} 0 500f\n"
                netlist += f"XS_{var_id+1} Q{var_id+1}bar {convergence_net} INVschmitt\n"
                netlist += f"XInv_{var_id+1} Q{var_id+1} Q{var_id+1}bar INV\n"
        netlist += f".ends SDC\n"
        return netlist
    


    def generate_n_input_nand_netlist(n):
        """
    Generates a SPICE netlist for an n-input NAND gate using CMOS technology.

    The function constructs the SPICE netlist description for an n-input NAND gate,
    including both PMOS and NMOS transistor networks. The PMOS transistors are connected
    in parallel to ensure that the output is high when any input is low. The NMOS
    transistors are connected in series, ensuring that the output is low only when all
    inputs are high.

    The netlist includes a subcircuit definition with input and output terminals,
    transistor definitions for both PMOS and NMOS, and connections for the transistors.
    Each transistor is defined with specific model parameters and dimensions appropriate
    for 45 nm technology nodes.

    Parameters:
    n (int): The number of inputs to the NAND gate, specifying how many PMOS and NMOS
             transistors will be included in the netlist.

    Returns:
    str: A string containing the complete SPICE netlist for the described n-input NAND gate.
         This netlist can be used directly in SPICE simulations.
    """
        header = f"* SPICE Netlist for a {n}-input NAND gate\n"
        subckt = f".subckt NAND{n} " + " ".join([f"in{i}" for i in range(1, n+1)]) + " Out \n"

        # Generate PMOS transistors
        pmos_transistors = ""
        for i in range(1, n + 1):
            pmos_transistors += f"MP{i-1} Out in{i} Vdd Vdd g45p1svt w=120n l=45n\n"

        # Generate NMOS transistors
        nmos_transistors = ""
        for i in range(1, n + 1):
            if i == 1:
                source = "0"
            else:
                source = f"net{i-2}"

            if i == n:
                drain = "Out"
            else:
                drain = f"net{i-1}"

            nmos_transistors += f"MN{i-1} {drain} in{i} {source} 0 g45n1svt w=120n l=45n\n"

        footer = ".ends NAND" + str(n) + "\n\n"

        # Combine all parts
        netlist = header + subckt + pmos_transistors + nmos_transistors + footer
        return netlist
    

   
    def generate_dvc_element(matrix):
        """
    Generates a SPICE netlist for a Digital Verification Circuit (DVC) from a given matrix.

    This function translates a matrix, where each row represents a clause in CNF, into a DVC using
    XOR and NAND gates to simulate the clause logic. The matrix uses 1 for true, -1 for false, and 0
    for an inactive variable. Each clause is processed to create a subcircuit with XOR gates representing
    the variable states and a NAND gate combining these states. The overall output of all clauses is
    combined using another NAND gate to produce a single output indicating SATisfiability.

    Parameters:
    matrix (list[list[int]]): Matrix where each row represents a clause with integers indicating variable
                              states (1 for true, -1 for false, 0 for inactive).

    Returns:
    str: A complete netlist string for the DVC that can be used in SPICE simulations.
    """
        #function for creating DVC block connections 
        netlist = "* SPICE Netlist for Digital Verification Circuit (DVC)\n"
        #header for subcircuit
        netlist += f".subckt DVC SAT" #output pin SAT
        for var_id in range(num_variables):
            netlist += f" Q{var_id+1}" #input pins
        netlist += f"\n"
        net_counter = 1  # To create unique net names
        clause_nand_outputs = []  # To collect the outputs of each clause's NAND gate
        
        # Iterate through each clause in the CNF
        for clause_id, clause in enumerate(matrix):
            clause_variables = [idx + 1 for idx, var in enumerate(clause) if var != 0]
            current_clause_nets = []
            
            # Add XOR gates for each variable present in the clause
            for var_id in clause_variables:
                var_state = 'Vdd' if clause[var_id - 1] == 1 else '0'
                xor_output_net = f"net{net_counter}"
                netlist += f"X{clause_id}_{var_id} Q{var_id} {var_state} {xor_output_net} XOR\n"
                current_clause_nets.append(xor_output_net)
                net_counter += 1
            
            # Add an NAND gate for the clause
            nand_inputs = ' '.join(current_clause_nets)
            nand_output_net = f"net{net_counter}"
            clause_nand_outputs.append(nand_output_net)
            if len(clause_variables) == 1:
            # If only one variable in the clause, use an inverter (INV) instead of a NAND gate
                netlist += f"XINV{clause_id} {nand_inputs} {nand_output_net} INV\n"
            else:
            # For more than one variable, use a NAND gate with the appropriate number of inputs
                netlist += f"XNAND{clause_id} {nand_inputs} {nand_output_net} NAND{len(clause_variables)}\n"

            net_counter += 1   # Increment counter to get name for output

        # Assuming clause_nand_outputs contains the outputs of all clause's NAND gates
        # Add an M-input NAND gate for the final SAT output
        m_nand_inputs = ' '.join(clause_nand_outputs)
        nand_output_net = f"net{net_counter}"
        netlist += f"XNAND_final {m_nand_inputs} {nand_output_net} NAND{len(matrix)}\n"
        net_counter += 1

        # Inverter (NOT gate) to invert the NAND output to get AND indicator
        netlist += f"XINV_final SAT {nand_output_net} INV\n"
        net_counter += 1
        netlist += f".ends DVC\n"
        return netlist
    


    #Commands to run
    matrix = input_matrix('Input_File.txt')
    display_pos(matrix)

    #source file containing the definition of reusable blocks like tunable resisitors (i.e. TR1 & TR2) and the logic gates used 
    source_file_path = 'AnalogSATsolverNetlistTemplate.scs'
    #destination file in which the final netlist will be written
    destination_file_path = "netlist.sp"

    #contents of source file being copied into  destination file line by line
    with open(source_file_path, 'r') as source_file, open(destination_file_path, 'w') as destination_file:
        for line in source_file:
            destination_file.write(line)

    num_variables = len(matrix[0]) #no of variables in CNF
    num_clauses=len(matrix) #no of clauses in CNF

    netlist = f"\n"
    if num_clauses>3:
        netlist += generate_n_input_nand_netlist(num_clauses)

    #combining all the elements in a single netlist
    netlist += generate_sdc_element(matrix)+"\n"+generate_avc_top_element(matrix)+"\n"+generate_dvc_element(matrix)+"\n\n" 

    #adding the top module instantiation for SDC, AVC, DVC blocks
    netlist += f"*Top module instantiation\n"
    netlist += f"X1"

    # Add all input and output pins to the top-level SDC block
    for var_id in range(num_variables):
            netlist += f" Q{var_id+1}"
            netlist += f" V{var_id+1}"
    for clause_id, clause in enumerate(matrix):
            netlist += f" Vam{clause_id+1}"
    netlist +=" SDC\n"
    netlist += f"X2 Vdd"   

    # Add all Vi inputs to the top-level AVC block
    for var_id in range(len(matrix[0])):
        netlist += f" V{var_id+1}"

    # Add all Vam outputs to the top-level AVC block
    for clause_id, clause in enumerate(matrix):
        netlist += f" Vam{clause_id+1}"
    netlist += f" AVC\n"

    # Add all input and output pins to the top-level DVC block
    netlist += f"X3 SAT"
    for var_id in range(num_variables):
            netlist += f" Q{var_id+1}"
    netlist += f" DVC\n"

    #adding the analysis and printing of the solution 
    for var_id in range(num_variables):
        netlist += f".print tran V(Q{var_id+1})\n"
    netlist += f".print tran V(SAT)\n.end\n"
    
    #appending it all in destination file
    with open(destination_file_path, 'a') as destination_file:
        destination_file.write(netlist)


if __name__ == "__main__":
    main()
