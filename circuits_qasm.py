#!/usr/bin/env python
# coding: utf-8

# In[1]:


from qiskit.circuit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit.compiler.assembler import assemble
from qiskit.assembler.disassemble import disassemble
import json
import sys

from collections import Iterable
from copy import deepcopy
from itertools import chain

# Create a circuit to assemble into a qobj
# Note: The conversion from a circuit into a QASM object is only implemented here to test that the modified function
# gives the same output as the original function.

def qasm_form(qobj):
    
    circuit = qobj.to_dict()['experiments'][0]['instructions']
    nGates = len(circuit)
    gates = []
    qubits = []
    qubits_1 = []
    qubits_2 = []
    qout_idx = []
    angles = []
    
    for g in range(0, nGates):
        qubits = qubits + circuit[g]["qubits"]
        
       # Qubits_1: Includes (for all gates) the first qubit the gate is acting upon. Results in a list e.g. [1,1,1,2] if the              circuit consits of 4 single qubit gates acting on 1,1,1,2
    
        qubits_1 = qubits_1 + [int(circuit[g]["qubits"][0]) + 1]
        
        # Qubits_2: A list of all the "second qubits" the gates is acting upon. In the case of H, H, CX: 0,0,2.
        # If the corresponding gate only acts on one qubit, add a zero to the list of "second qubits"
        
        if len(circuit[g]["qubits"]) == 1:
            qubits_2 = qubits_2 + [0]
        else:
            qubits_2 = qubits_2 + [int(circuit[g]["qubits"][1]) + 1]
            
        # Finally, "Qubits_1" and "Qubits_2", as well as "Gates" should all have nGates entries, meaning that we can execute
        # the circuit by iterating over all three lists.
        
        # Adjustment: Qiskit saves gates in lowercase letters, while the output of measurement.py needs upper case
        gates = gates + [circuit[g]["name"].upper()]
        if (gates[g] == 'RZ') | (gates[g] == 'RX'):
            
            # Adjustment: Qiskit saves circuitnames without an underscore, which we have to fix to fit the format
            
            gates[g] = gates[g][:1] + '_' + gates[g][1:]
            angles = angles + [int(circuit[g]['params'][0])]
        elif gates[g] == 'T' :
            angles = angles + [32]
            
    # Adjustment: Qubit positions are saved in Qiskit starting form zero, wereas we want them to start with one
    for i in range(len(qubits)):
        qubits[i] = int(qubits[i])
        qubits[i] += 1
        qubits[i] = str(qubits[i])
    nqbits = len(set(qubits))
    qout_idx = list(map(int, set(qubits)))
    qout_init = list(map(int, set(qubits)))
    qout_final = [-1]*len(qout_idx)

    return gates, [qubits_1, qubits_2], nqbits, angles, qout_idx, qout_init, qout_final


# In[10]:


circuits_qasm = []
def qasm_circs():

# Circuits to show two qubit circuits working perfectly

        # Circuit 1
        q1 = QuantumRegister(1)
        c1 = ClassicalRegister(1)
        qc1 = QuantumCircuit(q1, c1)
        qc1.h(q1[0])
        qobj1 = assemble(qc1, shots=2000, memory=True)
        #print("Same output for JSON and QASM, circuit1.json : " + str(load_circuit(cpaths[0]) == qasm_form(circuits_qasm[0])))
        circuits_qasm.append((qobj1,qc1.draw(filename="circuit.txt",output = "text")))

        # Circuit 2
        q2 = QuantumRegister(2)
        c2 = ClassicalRegister(2)
        qc2 = QuantumCircuit(q2, c2)
        qc2.z(q2[1])
        qc2.h(q2[0])
        qc2.h(q2[1])
        qc2.cx(q2[0],q2[1])
        qc2.cx(q2[1],q2[0])
        qc2.cx(q2[0],q2[1])
        qobj2 = assemble(qc2, shots=2000, memory=True)
        #print("Same output for JSON and QASM, circuit2.json : " + str(load_circuit(cpaths[1]) == qasm_form(qobj2)))
        circuits_qasm.append((qobj2,qc2.draw(filename="circuit.txt",output = "text")))

        # Circuit 3
        q3 = QuantumRegister(1)
        c3 = ClassicalRegister(1)
        qc3 = QuantumCircuit(q3, c3)
        qc3.z(q3[0])
        qobj3 = assemble(qc3, shots=2000, memory=True)
        #print("Same output for JSON and QASM, circuit3.json : " + str(load_circuit(cpaths[2]) == qasm_form(qobj3)))
        circuits_qasm.append((qobj3,qc3.draw(filename="circuit.txt",output = "text")))


# Circuits to see order dependency of three qubit operations

        # Circuit 4
        q4 = QuantumRegister(3)
        c4 = ClassicalRegister(3)
        qc4 = QuantumCircuit(q4, c4)
        qc4.z(q4[0])
        qc4.z(q4[1])
        qc4.h(q4[0])
        qc4.h(q4[1])
        qc4.h(q4[2])
        qobj4 = assemble(qc4, shots=2000, memory=True)
        #print("Same output for JSON and QASM, circuit4.json : " + str(load_circuit(cpaths[3]) == qasm_form(qobj4)))
        circuits_qasm.append((qobj4,qc4.draw(filename="circuit.txt",output = "text")))

        # Circuit 5
        q5 = QuantumRegister(3)
        c5 = ClassicalRegister(3)
        qc5 = QuantumCircuit(q5, c5)
        qc5.z(q5[0])
        qc5.z(q5[1])
        qc5.h(q5[2])
        qc5.h(q5[0])
        qc5.h(q5[1])
        qobj5 = assemble(qc5, shots=2000, memory=True)
        #print("Same output for JSON and QASM, circuit4.json : " + str(load_circuit(cpaths[3]) == qasm_form(qobj4)))
        circuits_qasm.append((qobj5,qc5.draw(filename="circuit.txt",output = "text")))

        # Circuit 6
        q6 = QuantumRegister(2)
        c6 = ClassicalRegister(2)
        qc6 = QuantumCircuit(q6, c6)
        qc6.cx(q6[0],q6[1])
        qc6.z(q6[0])
        qobj6 = assemble(qc6, shots=2000, memory=True)
        #print("Same output for JSON and QASM, circuit6.json : " + str(load_circuit(cpaths[5]) == qasm_form(qobj6)))
        circuits_qasm.append((qobj6,qc6.draw(filename="circuit.txt",output = "text")))

        # Circuit 7
        q7 = QuantumRegister(2)
        c7 = ClassicalRegister(2)
        qc7 = QuantumCircuit(q7, c7)
        qc7.cx(q7[0],q7[1])
        qc7.cx(q7[1],q7[0])
        qc7.cx(q7[0],q7[1])
        qc7.h(q7[0])
        qobj7 = assemble(qc7, shots=2000, memory=True)
        #print("Same output for JSON and QASM, circuit7.json : " + str(load_circuit(cpaths[6]) == qasm_form(qobj7)))
        circuits_qasm.append((qobj7,qc7.draw(filename="circuit.txt",output = "text")))

        # Circuit 8
        q8 = QuantumRegister(2)
        c8 = ClassicalRegister(2)
        qc8 = QuantumCircuit(q8, c8)
        qc8.h(q8[0])
        qc8.cx(q8[0],q8[1])
        qobj8 = assemble(qc8, shots=2000, memory=True)
        #print("Same output for JSON and QASM, circuit8.json : " + str(load_circuit(cpaths[7]) == qasm_form(qobj8)))
        circuits_qasm.append((qobj8,qc8.draw(filename="circuit.txt",output = "text")))

        # Circuit 9
        q9 = QuantumRegister(2)
        c9 = ClassicalRegister(2)
        qc9 = QuantumCircuit(q9, c9)
        qc9.z(q9[1])
        qc9.h(q9[0])
        qc9.h(q9[1])
        qc9.cx(q9[1],q9[0])
        qobj9 = assemble(qc9, shots=2000, memory=True)
        #print("Same output for JSON and QASM, circuit9.json : " + str(load_circuit(cpaths[8]) == qasm_form(qobj9)))
        circuits_qasm.append((qobj9,qc9.draw(filename="circuit.txt",output = "text")))

        # Circuit 10
        q10 = QuantumRegister(2)
        c10 = ClassicalRegister(2)
        qc10 = QuantumCircuit(q10, c10)
        qc10.cx(q10[0],q10[1])
        qobj10 = assemble(qc10, shots=2000, memory=True)
        #print("Same output for JSON and QASM, circuit10.json : " + str(load_circuit(cpaths[9]) == qasm_form(qobj10)))
        circuits_qasm.append((qobj10,qc10.draw(filename="circuit.txt",output = "text")))

        # Circuit 11
        q11 = QuantumRegister(2)
        c11 = ClassicalRegister(2)
        qc11 = QuantumCircuit(q11, c11)
        qc11.z(q11[1])
        qc11.h(q11[1])
        qc11.h(q11[0])       

        qobj11 = assemble(qc11, shots=2000, memory=True)
        #print("Same output for JSON and QASM, circuit11.json : " + str(load_circuit(cpaths[10]) == qasm_form(qobj11)))
        circuits_qasm.append((qobj11,qc11.draw(filename="circuit.txt",output = "text")))

        # Circuit 12
        q12 = QuantumRegister(2)
        c12 = ClassicalRegister(2)
        qc12 = QuantumCircuit(q12, c12)
        qc12.rx(128,q12[0])
        qobj12 = assemble(qc12, shots=2000, memory=True)
        #print("Same output for JSON and QASM, circuit12.json : " + str(load_circuit(cpaths[11]) == qasm_form(qobj12)))
        circuits_qasm.append((qobj12,qc12.draw(filename="circuit.txt",output = "text")))

        # Circuit 13
        q13 = QuantumRegister(2)
        c13 = ClassicalRegister(2)
        qc13 = QuantumCircuit(q13, c13)
        qc13.t(q13[0])
        qc13.cx(q13[0],q13[1])
        qobj13 = assemble(qc13, shots=2000, memory=True)
        #print("Same output for JSON and QASM, circuit13.json : " + str(load_circuit(cpaths[12]) == qasm_form(qobj13)))
        circuits_qasm.append((qobj13,qc13.draw(filename="circuit.txt",output = "text")))

        # Circuit 14
        q14 = QuantumRegister(1)
        c14 = ClassicalRegister(1)
        qc14 = QuantumCircuit(q14, c14)
        qc14.t(q14[0])
        qc14.rz(160,q14[0])
        qobj14 = assemble(qc14, shots=2000, memory=True)
        #print("Same output for JSON and QASM, circuit14.json : " + str(load_circuit(cpaths[13]) == qasm_form(qobj14)))
        circuits_qasm.append((qobj14,qc14.draw(filename="circuit.txt",output = "text")))

        # Circuit 15
        q15 = QuantumRegister(3)
        c15 = ClassicalRegister(3)
        qc15 = QuantumCircuit(q15, c15)
        qc15.z(q15[0])
        qc15.h(q15[2])
        qc15.h(q15[0])
        qc15.h(q15[1])                       
        qc15.cx(q15[0],q15[2])
        qobj15 = assemble(qc15, shots=2000, memory=True)
        #print("Same output for JSON and QASM, circuit15.json : " + str(load_circuit(cpaths[14]) == qasm_form(qobj15)))
        circuits_qasm.append((qobj15,qc15.draw(filename="circuit.txt",output = "text")))

        # Circuit 16
        q16 = QuantumRegister(2)
        c16 = ClassicalRegister(2)
        qc16 = QuantumCircuit(q16, c16)
        qc16.z(q16[0])
        qc16.h(q16[1])
        qc16.h(q16[0])
        qc16.cx(q16[0],q16[1])
        qc16.cx(q16[1],q16[0])
        qc16.cx(q16[0],q16[1])
        #qc16.x(q16[0])
        qobj16 = assemble(qc16, shots=2000, memory=True)
        #print("Same output for JSON and QASM, circuit16.json : " + str(load_circuit(cpaths[15]) == qasm_form(qobj16)))
        circuits_qasm.append((qobj16,qc16.draw(filename="circuit.txt",output = "text")))

        # Circuit 17
        # Check controll gate works if there's qubit in between
        q17 = QuantumRegister(3)
        c17 = ClassicalRegister(3)
        qc17 = QuantumCircuit(q17, c17)
        qc17.z(q17[0])
        qc17.z(q17[1])
        qc17.h(q17[0])
        qc17.h(q17[1])
        qc17.h(q17[2])
        #qc18.x(q17[1])
        qobj17 = assemble(qc17, shots=2000, memory=True)
        circuits_qasm.append((qobj17,qc17.draw(filename="circuit.txt",output = "text")))
        #print("Same output for JSON and QASM, circuit22.json : " + str(load_circuit(cpaths[17]) == qasm_form(qobj18)))
        
        # Circuit 18
        # Check controll gate works if there's qubit in between
        q18 = QuantumRegister(3)
        c18 = ClassicalRegister(3)
        qc18 = QuantumCircuit(q18, c18)
        qc18.z(q18[0])
        qc18.z(q18[1])
        qc18.h(q18[1])
        qc18.h(q18[0])
        qc18.h(q18[2])
        #qc18.x(q18[1])
        qobj18 = assemble(qc18, shots=2000, memory=True)
        circuits_qasm.append((qobj18,qc18.draw(filename="circuit.txt",output = "text")))
        #print("Same output for JSON and QASM, circuit22.json : " + str(load_circuit(cpaths[17]) == qasm_form(qobj18)))
         
         
# Circuits to see order dependency of four qubit circuits         
         
            
        # Circuit 19
        q19 = QuantumRegister(4)
        c19 = ClassicalRegister(4)
        qc19 = QuantumCircuit(q19, c19)
        qc19.z(q19[0])
        qc19.z(q19[1])
        qc19.h(q19[0])
        qc19.h(q19[1])
        qc19.h(q19[2])
        qc19.h(q19[3])
        qc19.cx(q19[1],q19[3])
        
        qobj19 = assemble(qc19, shots=2000, memory=True)
        circuits_qasm.append((qobj19,qc19.draw(filename="circuit.txt",output = "text")))
        #print("Same output for JSON and QASM, circuit17.json : " + str(load_circuit(cpaths[16]) == qasm_form(qobj17)))
        
        # Circuit 20
        q20 = QuantumRegister(4)
        c20 = ClassicalRegister(4)
        qc20 = QuantumCircuit(q20, c20)
        qc20.z(q20[0])
        qc20.z(q20[1])
        qc20.h(q20[3])
        qc20.h(q20[2])
        qc20.h(q20[0])
        qc20.h(q20[1])
        qc20.cx(q20[1],q20[3])
        qc20.cx(q20[3],q20[0])
        
        qobj20 = assemble(qc20, shots=2000, memory=True)
        circuits_qasm.append([qobj20,qc20.draw(filename="circuit.txt",output = "text")])
        
        # Circuit 21
        q21 = QuantumRegister(5)
        c21 = ClassicalRegister(5)
        qc21 = QuantumCircuit(q21, c21)
        qc21.z(q21[0])
        qc21.z(q21[1])
        qc21.h(q21[4])
        qc21.h(q21[3])
        qc21.h(q21[2])
        qc21.h(q21[0])
        qc21.h(q21[1])
        qc21.cx(q21[1],q21[3])
        qc21.x(q21[4])
        qc21.cx(q21[4],q21[2])
        qc21.cx(q21[0],q21[1])
        
        qobj21 = assemble(qc21, shots=2000, memory=True)
        circuits_qasm.append([qobj21,qc21.draw(filename="circuit.txt",output = "text")])
        #print("Same output for JSON and QASM, circuit17.json : " + str(load_circuit(cpaths[16]) == qasm_form(qobj17)))
        return circuits_qasm
    


# In[9]:


qasm_circs()[0]


# In[ ]:




