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
      Date          By                     Change Notes
 ------------  ---------------------- ------------------------------------------
  8 April 2024    Sejal Singh                 Netlist generation code
################################################################################
"""
def main():
    def input_matrix():
        # Input the size of the matrix
        m = int(input("Enter the number of clauses (rows): "))
        n = int(input("Enter the number of variables (columns): "))
        
        # Initialize the matrix
        matrix = []
        print("Enter the matrix values row by row (use space to separate values in a row):")
        
        # Input each row
        for i in range(m):
            row = list(map(int, input(f"Row {i+1}: ").strip().split()))
            matrix.append(row)
        
        return matrix

    def display_pos(matrix):
        #display the input matrix in form of POS or CNF
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

        Parameters:
        clause (list): The clause represented as a list of variable states.

        Returns:
        int or None: The index of the first non-zero variable, or None if all are zero.
        """
        for index, var in enumerate(clause):
            if var != 0:
                return index
        return None
    
    def find_last_non_zero(clause):
        last_index = None
        for index, var in enumerate(clause):
            if var != 0:
                last_index = index
        return last_index

    def generate_avc_element(clause_matrix):
        #Function to write netlist of internal connections of AVC block according to every clause 
        avc_netlist = ""
        opamp_model_params = "GBP=1e+06 AOLDC=106 FP2=3e+06 RO=75 CD=1e-12 RD=2e+06 IOFF=2e-08 IB=8e-08 VOFF=0.0007 CMRRDC=90 FCM=200 PSRT=500000 NSRT=500000 VLIMP=1.2 VLIMN=-1.2 ILMAX=0.035 CSCALE=50"
        net_counter=1 #to keep count of the nets in each subcircuit
        for clause_id, clause in enumerate(clause_matrix):
            # Add header for the subcircuit
            avc_netlist += f"* Clause {clause_id+1} element in AVC\n"
            avc_netlist += f".subckt avc{clause_id+1} Vam{clause_id+1} Vdd EN"
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
                        avc_netlist += f"I{clause_id}_{var_id} net0 net1 {connection} V{var_id+1} Vdd TR2\n"
                        avc_netlist += f"I{clause_id}_{var_id+1} 0 net101 {connection} V{var_id+1} Vdd TR2\n"
                        pass
                    else: #for the other non-zero  variables, connection of TR2 instances in series
                        if var_state != 0:
                            connection = 'Vdd' if var_state == 1 else '0'
                            # Adjust the instance numbering to avoid repetition
                            avc_netlist += f"I{clause_id}_{net_counter}  net{net_counter} net{net_counter+1} {connection} V{var_id+1} Vdd TR2\n"
                            avc_netlist += f"I{clause_id}_{net_counter} net{net_counter+100} net{net_counter+101} {connection} V{var_id+1} Vdd TR2\n"
                            net_counter += 1  # Increment for the next net name
                        pass
            
                
            # Add the opamp and branch components (sw, capacitors) for the clause element
            avc_netlist += f"XOP{clause_id} net{net_counter} net{net_counter+100} Vam{clause_id+1} mod_amp {opamp_model_params}\n"
            avc_netlist += f"C{clause_id}_0 net{net_counter} 0 1p\n"
            avc_netlist += f"C{clause_id}_1 net{net_counter+100} Vam{clause_id+1} 1p\n"
            avc_netlist += f"I{clause_id}_2 net0 Vam{clause_id+1} EN Vdd sw\n"
            avc_netlist += f".ends avc{clause_id+1}\n\n"  
        return avc_netlist
    
    def generate_avc_top_element(clause_matrix):
        #function for creating a top module for the AVC block connecting the internal avc element pins to outside circuit 
        top_avc_netlist = "* Top Level AVC Block\n"
        top_avc_netlist += ".subckt AVC Vdd EN"
        
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
            top_avc_netlist += f"Xavc{clause_id+1} Vam{clause_id+1} Vdd EN {inputs} avc{clause_id+1}\n"
        top_avc_netlist += f".ends AVC\n"
        
        # Combine with the individual AVC clauses netlists
        avc_netlist = generate_avc_element(clause_matrix)
        complete_netlist = avc_netlist + top_avc_netlist
        return complete_netlist

    def generate_sdc_element(matrix):
        #function for generating the SDC block connections
        netlist = "*Element in SDC\n"
        netlist += f".subckt SDC Vdd"
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
                    netlist += f"XTR1_{var_id+1}_{clause_id} net{net_counter} {state} Vdd Vam{clause_id+1} Vdd TR1\n"
                    current_net = f"net{net_counter}"
                    net_counter += 1

                    # Add TR2 instances for every other variable in the clause
                    for other_var_id, other_var_presence in enumerate(clause):
                        if other_var_id != var_id and other_var_presence != 0:
                            other_state = 'Vdd' if other_var_presence == 1 else '0'
                            netlist += f"XTR2_{var_id+1}_{clause_id}_{other_var_id+1} {current_net} net{net_counter} {other_state} V{other_var_id+1} Vdd TR2\n"
                            current_net = f"net{net_counter}"
                            net_counter += 1

                    previous_nets.append(current_net)

            if previous_nets:
                # Convergence point for the branches of this variable across all clauses
                convergence_net = f"net{net_counter}"
                net_counter += 1

                for end_net in previous_nets:
                    netlist += f"Rconv_{var_id+1}_{end_net} {end_net} {convergence_net} 0\n"

                # Final connections to capacitor and Schmitt trigger for this variable through the convergence point
                netlist += f"C{var_id+1} {convergence_net} 0 500f\n"
                netlist += f"XS_{var_id+1} Q{var_id+1}bar {convergence_net} Vdd INVschmitt\n"
                netlist += f"XInv_{var_id+1} Q{var_id+1}bar Q{var_id+1} Vdd INV\n"
        netlist += f".ends SDC\n"
        return netlist

    def generate_n_input_nand_netlist(n, vdd='Vdd'):
        #function necessary to create an M-input (M clauses) NAND gate for DVC circuit
        """
        Generate a SPICE netlist for an n-input NAND gate using CMOS transistors.
        
        :param n: Number of inputs for the NAND gate.
        :param vdd: The power supply net name.
        :return: A string containing the SPICE netlist.
        """
        inputs = ' '.join([f'in{i}' for i in range(n)])  # Define the input pins
        output = 'out'  # Define the output pin
        subckt_name = f"NAND"  

        netlist = f".subckt {subckt_name} {inputs} {output} {vdd} GND\n"
        #define the model of PMOS and NMOS based on the technology node being used (here 45nm)
        netlist += f"M0 out {vdd} {vdd} {vdd} g45p1svt w=120n l=45n\n"

        for i in range(n):
            netlist += f"M{i+1} out in{i} GND GND g45n1svt w=120n l=45n\n"
            netlist += f"M{i+n+1} mid{i} in{i} {vdd} {vdd} g45p1svt w=120n l=45n\n"
            if i == 0:
                netlist += f"R{i} mid{i} out 1k\n"
            else:
                netlist += f"R{i} mid{i} mid{i-1} 1k\n"

        netlist += f".ends NAND\n\n"
        return netlist
    
    def generate_dvc_element(matrix):
        #function for creating DVC block connections 
        netlist = "* SPICE Netlist for Digital Verification Circuit (DVC)\n"
        #header for subcircuit
        netlist += f".subckt DVC SAT" #output pin SAT
        for var_id in range(num_variables):
            netlist += f" Q{var_id+1}" #input pins
        netlist +=f" Vdd\n"
        net_counter = 1  # To create unique net names
        clause_nand_outputs = []  # To collect the outputs of each clause's NAND gate
        
        # Iterate through each clause in the CNF
        for clause_id, clause in enumerate(matrix):
            clause_variables = [idx + 1 for idx, var in enumerate(clause) if var != 0]
            current_clause_nets = []
            
            # Add XOR gates for each variable present in the clause
            for var_id in clause_variables:
                var_state = 'Vdd' if clause[var_id - 1] == 1 else 'gnd'
                xor_output_net = f"net{net_counter}"
                netlist += f"X{clause_id}_{var_id} Q{var_id} {var_state} {xor_output_net} XOR\n"
                current_clause_nets.append(xor_output_net)
                net_counter += 1
            
            # Add an NAND gate for the clause
            nand_inputs = ' '.join(current_clause_nets)
            nand_output_net = f"net{net_counter}"
            clause_nand_outputs.append(nand_output_net)
            netlist += f"XNAND{clause_id} {nand_inputs} {nand_output_net} Vdd {len(clause_variables)}_NAND\n"
            net_counter += 1

        # Assuming clause_nand_outputs contains the outputs of all clause's NAND gates
        # Add an M-input NAND gate for the final SAT output
        m_nand_inputs = ' '.join(clause_nand_outputs)
        nand_output_net = f"net{net_counter}"
        netlist += f"XNAND_final {m_nand_inputs} {nand_output_net} Vdd NAND\n"
        net_counter += 1

        # Inverter (NOT gate) to invert the NAND output to get AND indicator
        inv_output_net = f"net{net_counter}"
        netlist += f"XINV_final {nand_output_net} {inv_output_net} INV\n"
        net_counter += 1

        # Define the SAT output pin
        netlist += f"XSAT {inv_output_net} SAT"
        netlist += "\n"
        netlist += f".ends DVC\n"
        return netlist

    #Commands to run
    matrix = input_matrix()
    display_pos(matrix)
    #source file containing the definition of reusable blocks like tunable resisitors (i.e. TR1 & TR2) and the logic gates used 
    source_file_path = 'blocks.ckt'
    #destination file in which the final netlist will be written
    destination_file_path = "generated_netlist.sp"
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
    netlist += f"X1 Vdd"
    # Add all input and output pins to the top-level SDC block
    for var_id in range(num_variables):
            netlist += f" Q{var_id+1}"
            netlist += f" V{var_id+1}"
    for clause_id, clause in enumerate(matrix):
            netlist += f" Vam{clause_id+1}"
    netlist +=" SDC\n"
    netlist += f"X2 Vdd Vdd"   
    # Add all Vi inputs to the top-level AVC block
    for var_id in range(len(matrix[0])):
        netlist += f" V{var_id+1}"
    # Add all Vam outputs to the top-level AVC block
    for clause_id, clause in enumerate(matrix):
        netlist += f" Vam{clause_id+1}"
    netlist += f" AVC\n"
    # Add all input and output pins to the top-level DVC block
    netlist += f"X3 SAT "
    for var_id in range(num_variables):
            netlist += f" Q{var_id+1}"
    netlist +=f" Vdd "
    netlist += f"DVC\n"
    #adding the analysis and printing of the solution 
    netlist += f".tran 2n \n"
    for var_id in range(num_variables):
        netlist += f".print tran V(Q{var_id+1})\n"
    netlist += f".print tran V(SAT)\n.end\n"
    print(netlist)
    #appending it all in destination file
    with open(destination_file_path, 'a') as destination_file:
        destination_file.write(netlist)
if __name__ == "__main__":
    main()
