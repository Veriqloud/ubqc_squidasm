from qiskit.circuit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit.compiler.assembler import assemble
from qiskit.assembler.disassemble import disassemble
from qiskit.qasm3 import dump
import json
import sys

from collections.abc import Iterable
from copy import deepcopy
from itertools import chain


# return a list of qCircuit [0,15]
def qasm_circs():

    circuits_qasm = []
    # Circuit 1, Expected outcome: [0]
    q1 = QuantumRegister(1)
    c1 = ClassicalRegister(1)
    qc1 = QuantumCircuit(q1, c1)
    qc1.h(q1[0])
    circuits_qasm.append(qc1)


    # Circuit 2, Expected outcome: [0]
    q2 = QuantumRegister(1)
    c2 = ClassicalRegister(1)
    qc2 = QuantumCircuit(q2, c2)
    qc2.z(q2[0])
    qc2.h(q2[0])
    qc2.rx(128,q2[0])    
    circuits_qasm.append(qc2)

    # Circuit 3, Expected outcome: [0]
    q3 = QuantumRegister(1)
    c3 = ClassicalRegister(1)
    qc3 = QuantumCircuit(q3, c3)
    qc3.z(q3[0])
    qc3.h(q3[0])
    qc3.x(q3[0])
    circuits_qasm.append(qc3)

    # Circuit 4, Expected outcome: [0,1]
    q4 = QuantumRegister(2)
    c4 = ClassicalRegister(2)
    qc4 = QuantumCircuit(q4, c4)
    qc4.h(q4[0])
    qc4.z(q4[1])
    qc4.h(q4[1])
    circuits_qasm.append(qc4)

    # Circuit 5, Expected outcome: [1,1]
    q5 = QuantumRegister(2)
    c5 = ClassicalRegister(2)
    qc5 = QuantumCircuit(q5, c5)
    qc5.h(q5[0])
    qc5.z(q5[1])
    qc5.h(q5[1])
    qc5.cx(q5[1],q5[0])
    circuits_qasm.append(qc5)

    # Circuit 6, Expected outcome: [1,0]
    q6 = QuantumRegister(2)
    c6 = ClassicalRegister(2)
    qc6 = QuantumCircuit(q6, c6)
    qc6.h(q6[0])
    qc6.z(q6[1])
    qc6.h(q6[1])
    qc6.cx(q6[0],q6[1]) # Swap operation
    qc6.cx(q6[1],q6[0])
    qc6.cx(q6[0],q6[1])
    circuits_qasm.append(qc6)

    # Circuit 7, Expected outcome: [1,1,0]
    q7 = QuantumRegister(3)
    c7 = ClassicalRegister(3)
    qc7 = QuantumCircuit(q7, c7)
    qc7.z(q7[0])
    qc7.z(q7[1])
    qc7.h(q7[0])
    qc7.h(q7[1])
    qc7.h(q7[2])
    circuits_qasm.append(qc7)

    # Circuit 8, Expected outcome: [1,1,1]
    q8 = QuantumRegister(3)
    c8 = ClassicalRegister(3)
    qc8 = QuantumCircuit(q8, c8)
    qc8.z(q8[0])
    qc8.z(q8[1])
    qc8.h(q8[0])
    qc8.h(q8[1])
    qc8.h(q8[2])
    qc8.cx(q8[0],q8[2])
    circuits_qasm.append(qc8)

    # Circuit 9, Expected outcome: [0,1,1]
    q9 = QuantumRegister(3)
    c9 = ClassicalRegister(3)
    qc9 = QuantumCircuit(q9, c9)
    qc9.z(q9[0])
    qc9.z(q9[1])
    qc9.h(q9[0])
    qc9.h(q9[1])
    qc9.h(q9[2])
    qc9.cx(q9[0],q9[2])
    qc9.cx(q9[2],q9[0])
    circuits_qasm.append(qc9)


    # Circuit 10, Expected outcome: [1,1,0,0]
    q10 = QuantumRegister(4)
    c10 = ClassicalRegister(4)
    qc10 = QuantumCircuit(q10, c10)
    qc10.z(q10[0])
    qc10.z(q10[1])
    qc10.h(q10[0])
    qc10.h(q10[1])
    qc10.h(q10[2])
    qc10.h(q10[3])
    circuits_qasm.append(qc10)

    # Circuit 11, Expected outcome: [1,1,1,1]
    q11 = QuantumRegister(4)
    c11 = ClassicalRegister(4)
    qc11 = QuantumCircuit(q11, c11)
    qc11.z(q11[0])
    qc11.z(q11[1])
    qc11.h(q11[0])
    qc11.h(q11[1])
    qc11.h(q11[2])
    qc11.h(q11[3])
    qc11.x(q11[2]) 
    qc11.cx(q11[2],q11[3])
    circuits_qasm.append(qc11)

    # Circuit 12, Expected outcome: [1,1,1,1]
    q12 = QuantumRegister(4)
    c12 = ClassicalRegister(4)
    qc12 = QuantumCircuit(q12, c12)
    qc12.z(q12[0])
    qc12.z(q12[1])
    qc12.h(q12[0])
    qc12.h(q12[1])
    qc12.h(q12[2])
    qc12.h(q12[3])
    qc12.h(q12[2])
    qc12.z(q12[2]) 
    qc12.h(q12[2]) 
    qc12.cx(q12[2],q12[3])
    circuits_qasm.append(qc12)

    # Circuit 13, Expected outcome: [1,1,0,0,0]
    q13 = QuantumRegister(5)
    c13 = ClassicalRegister(5)
    qc13 = QuantumCircuit(q13, c13)
    qc13.z(q13[0])
    qc13.z(q13[1])
    qc13.h(q13[0])
    qc13.h(q13[1])
    qc13.h(q13[2])
    qc13.h(q13[3])
    qc13.h(q13[4])
    circuits_qasm.append(qc13)

    # Circuit 14, Expected outcome: [1,1,1,1,0]
    q14 = QuantumRegister(5)
    c14 = ClassicalRegister(5)
    qc14 = QuantumCircuit(q14, c14)
    qc14.z(q14[0])
    qc14.z(q14[1])
    qc14.h(q14[0])
    qc14.h(q14[1])
    qc14.h(q14[2])
    qc14.h(q14[3])
    qc14.h(q14[4])
    qc14.rx(128,q14[2])
    qc14.cx(q14[1],q14[3])
    circuits_qasm.append(qc14)

    # Circuit 15, Expected outcome: [0,1,1,1,1]
    q15 = QuantumRegister(5)
    c15 = ClassicalRegister(5)
    qc15 = QuantumCircuit(q15, c15)
    qc15.z(q15[0])
    qc15.z(q15[1])
    qc15.h(q15[0])
    qc15.h(q15[1])
    qc15.h(q15[2])
    qc15.h(q15[3])
    qc15.h(q15[4])
    qc15.rx(128,q15[2])
    qc15.cx(q15[1],q15[3])
    qc15.h(q15[4])
    qc15.z(q15[4])
    qc15.h(q15[4])
    qc15.cx(q15[4],q15[0])
    circuits_qasm.append(qc15)    

    # Circuit 16 Expected outcome: [1,1,1,1,1,1,1,1,1,1]
    q16 = QuantumRegister(10)
    c16 = ClassicalRegister(10)
    qc16 = QuantumCircuit(q16,c16)
    qc16.h(q16[0])
    qc16.x(q16[0])
    qc16.h(q16[1])
    qc16.x(q16[1])
    qc16.h(q16[2])
    qc16.cx(q16[1],q16[2])
    qc16.h(q16[3])
    qc16.cx(q16[2],q16[3])
    qc16.h(q16[4])
    qc16.cx(q16[3],q16[4])
    qc16.h(q16[5])
    qc16.cx(q16[4],q16[5])
    qc16.h(q16[6])
    qc16.cx(q16[0],q16[6])
    qc16.h(q16[7])
    qc16.cx(q16[0],q16[7])
    qc16.h(q16[8])
    qc16.cx(q16[0],q16[8])
    qc16.h(q16[9])
    qc16.cx(q16[0],q16[9])
    circuits_qasm.append(qc16)


    return circuits_qasm