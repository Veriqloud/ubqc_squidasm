# Code to estimate the probability of Bob to guess the circuit Alice wants to implement

import scipy.special
import numpy as np
from collections.abc import Iterable
from itertools import chain
import itertools
import pandas as pd
from qiskit.circuit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit.compiler.assembler import assemble
from qiskit.assembler.disassemble import disassemble
from qiskit import transpile
from qiskit.quantum_info import Statevector
from itertools import combinations_with_replacement
from itertools import combinations
from measurement_qasm import load_circuit_qasm
from flow_qasm import circuit_file_to_flow, count_qubits_in_sequence

# Define the three fundamental gates that are used in the measurement formalism. All circuits will be expressed in terms of these.

gate_types = {
    'H': {'n_ent': 1, 'n_meas': 1, 'n_qubit': 1},
    'CZ': {'n_ent': 1, 'n_meas': 0, 'n_qubit': 0},
    'J': {'n_ent': 1, 'n_meas': 1, 'n_qubit': 1},
}

# First step: Find all possible combinations of H, CZ, and J gates that are consistent with the given variables of n_qubits, n_measurements, n_entanglements

def find_consistent_combinations(num_qubits, num_meas, num_ent):
    consistent_combinations = []
    n_output = num_qubits - num_meas
    comp_qubits = num_qubits - n_output
    
    for r in range(1, num_qubits):
        for combination in combinations_with_replacement(gate_types.items(), r):
            total_ent = 0
            total_meas = 0
            total_qubit = 0
            
            for _, parameters in combination:
                total_ent += parameters['n_ent']
                total_meas += parameters['n_meas']
                total_qubit += parameters['n_qubit']
            
            if (
                total_ent == num_ent and
                total_meas == num_meas and
                total_qubit == comp_qubits
            ):
                consistent_combinations.append([gate_type for gate_type, _ in combination])  
                
    nCombinations = 0
    for combination in consistent_combinations:
        degenerate_combinations = 1
        for gate in combination:
            if(gate == 'H' or gate == 'J'):
                degenerate_combinations = degenerate_combinations*max(1,scipy.special.binom(n_output,1))
            if(gate == 'CZ'):
                degenerate_combinations = degenerate_combinations*2*max(1,scipy.special.binom(n_output,2))
        nCombinations += degenerate_combinations
    
    return consistent_combinations, nCombinations, n_output

# Next subroutine: Gives all possible gate/qubit combinations for a given gate type and a given number of qubits

def get_degenerate_gate(gate, nqubits):
    degenerate_gates = []
    for i in range(nqubits):
        if(gate == 'H' or gate == 'J'):
            degenerate_gates.append([gate,[i+1,0]])
        if(gate == 'CZ'):
            for j in range(nqubits):
                if(j != i):
                    degenerate_gates.append([gate,[i+1,j+1]])
    return degenerate_gates   

# Gives all possible gate/qubit combinations for all gates in a given circuit

def all_deg_gates(combination,nqubits):
    allgates = []
    for i, gate in enumerate(combination):
        deg_gates = get_degenerate_gate(gate,nqubits)
        allgates.append(deg_gates)
    return allgates

# Returns all possibilities to build a circuit with the given gate types

def get_all_combinations_with_degs(combination,nqubits):
    combinations_with_degs = []
    for i in range(len(combination)):
        combinations_with_degs.append(all_deg_gates(combination,nqubits))
    return combinations_with_degs

# Define a function to get all unique permutations of the given circuit configurations

def generate_unique_combinations(list_of_lists):
    return list(itertools.product(*list_of_lists))

# Pick out all the unique combinations from the list of all combinations

def get_all_combinations(combination,nqubits):
    combinations_with_degs = get_all_combinations_with_degs(combination,nqubits)
    return generate_unique_combinations(combinations_with_degs[0])

# Subroutine to get all combinations directly from the initial variables

def all_combinations_from_vars(num_qubits,num_meas,num_ent):
    combinations, chance, nqubits = find_consistent_combinations(num_qubits,num_meas,num_ent)
    allCombs = []
    for i, combination in enumerate(combinations):
        allCombs_i = get_all_combinations(combination,nqubits)
        for j in range(len(allCombs_i)):
            allCombs.append(list(itertools.permutations(allCombs_i[j])))
    return allCombs, chance

# Subroutine to find the number of qubits in a given circuit

def count_output_qubits(gates):
    max_qubit = 1
    for i,gate in enumerate(gates):
        if(gate[1][0]) > max_qubit:
            max_qubit = gate[1][0]
        if(gate[1][1]) > max_qubit:
            max_qubit = gate[1][1]
    return max_qubit

# Subroutine to convert gate instructions into a qiskit circuit

def qiskit_circ_from_gates(gates):
    nQubits = count_output_qubits(gates)
    q = QuantumRegister(nQubits)
    c = ClassicalRegister(nQubits)
    qc = QuantumCircuit(q,c)
    for i, gate in enumerate(gates):
        if(gate[0] == 'H'):
            qc.h(q[gate[1][0]-1])
        elif(gate[0] == 'J'):
            qc.rx(128,q[gate[1][0]-1])
        elif(gate[0] == 'CZ'):
            qc.cz(q[gate[1][0]-1],q[gate[1][1]-1])
    return qc

# Subroutine to convert a list of circuit instructions into a list of qiskit circuits. Doesn't include circuits if their state vector is the same.

def qiskit_circs_from_list(combinations):
    circuits = []
    for i, comb in enumerate(combinations):
        for k in range(len(comb)):
            qiskit_circ = transpile(qiskit_circ_from_gates(comb[k]),optimization_level=3)
            if(len(circuits) == 0):
                circuits.append(qiskit_circ)
            in_list = False
            for j in range(len(circuits)):
                if(Statevector.from_instruction(qiskit_circ).equiv(Statevector.from_instruction(circuits[j]))):
                    in_list = True
            if(in_list == False):
                circuits.append(qiskit_circ)
    return circuits

# Subroutine to reconvert a qiskit circuit into a list

def qiskit_circ_to_list(circ):
    gates, [qubits_1, qubits_2], nqbits, angles, qout_idx, qout_init, qout_final = load_circuit_qasm(assemble(circ, shots=2000, memory=True))
    return [[gates[i], [qubits_1[i],qubits_2[i]]] for i in range(len(gates))]

# Here: Go through all possible combinations for a given set of variables, build all possible circuits, simplify them and return list of qiskit circuits

def get_all_circuits(combinations):
    all_circuits = []
    qiskit_circuits = qiskit_circs_from_list(combinations)
    for i in range(len(qiskit_circuits)):
        circ_list = qiskit_circ_to_list(qiskit_circuits[i])
        if(circ_list != []):
            all_circuits.append(circ_list)
    return all_circuits

# Count all possible circuits, including ambivalency regarding rotation angles (1 out of 256), to estimate probabilityto guess right circuit

def get_probability(n_qubit,n_meas,n_ent):
    possibilities = 0
    all_circs = get_all_circuits(all_combinations_from_vars(n_qubit,n_meas,n_ent)[0])
    for i, circuit in enumerate(all_circs):
        meas_count = 0
        for j, gate in enumerate(circuit):
            if(gate[0] == 'R_X' or 'H'):
                meas_count += 1
        possibilities_circ = 256**meas_count
        possibilities += possibilities_circ
    return 1/possibilities



def get_variables(circuit):
    qobj = assemble(circuit, shots=2000, memory=True)
    circ_flow = circuit_file_to_flow(qobj)
    seq = circ_flow[0]
    nQubits = count_qubits_in_sequence(seq)
    nEntanglement = 0
    nMeasurement = 0
    for s in seq:
        if s.type == "E":
            nEntanglement +=1
        if s.type == "M":
            nMeasurement += 1
    return nQubits, nMeasurement, nEntanglement

# Example usage: Either provide the given variables n_compqubits, n_measurement, n_entanglement,
# or provide a qiskit circuit and extract the corresponding information:

# Load test circuit

q = QuantumRegister(1)
c = ClassicalRegister(1)
qc = QuantumCircuit(q,c)
qc.h(q[0])
qc.h(q[0])

# Extract variables from test circuit

n_compqubits, n_measurement, n_entanglement = get_variables(qc)

# Estimate security from these variables

print(f"Variables for the given circuit: n_comp = {n_compqubits}, n_meas = {n_measurement}, n_ent = {n_entanglement}")

print(f"Gate combinations: \n {find_consistent_combinations(n_compqubits,n_measurement,n_entanglement)[0]} \n")

print(f"All possible circuits (redundant): \n {all_combinations_from_vars(n_compqubits,n_measurement,n_entanglement)[0]} \n")

print(f"All possible circuits (unique): \n {get_all_circuits(all_combinations_from_vars(n_compqubits,n_measurement,n_entanglement)[0])} \n")

print(f"Total probability to guess right circuit (up to X and Z gates): \n {get_probability(n_compqubits,n_measurement,n_entanglement)} \n")

# Still to do: Two qubit circuits where only one qubit is manipulated could get excluded, replace RX gates with J gates
