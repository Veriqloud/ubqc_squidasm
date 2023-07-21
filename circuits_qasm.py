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

circuits_qasm = []
def qasm_circs():

        # Circuit 1, Expected outcome: [0]
        q1 = QuantumRegister(1)
        c1 = ClassicalRegister(1)
        qc1 = QuantumCircuit(q1, c1)
        qc1.h(q1[0])
        qobj1 = assemble(qc1, shots=2000, memory=True)
        circuits_qasm.append((qobj1,[0],qc1.draw(filename="circuit.txt",output = "text")))

        # Circuit 2, Expected outcome: [0]
        q2 = QuantumRegister(1)
        c2 = ClassicalRegister(1)
        qc2 = QuantumCircuit(q2, c2)
        qc2.z(q2[0])
        qc2.h(q2[0])
        qc2.rx(128,q2[0])    
        qobj2 = assemble(qc2, shots=2000, memory=True)
        circuits_qasm.append((qobj2,[0],qc2.draw(filename="circuit.txt",output = "text")))

        # Circuit 3, Expected outcome: [0]
        q3 = QuantumRegister(1)
        c3 = ClassicalRegister(1)
        qc3 = QuantumCircuit(q3, c3)
        qc3.z(q3[0])
        qc3.h(q3[0])
        qc3.x(q3[0])
        qobj3 = assemble(qc3, shots=2000, memory=True)
        circuits_qasm.append((qobj3,[0],qc3.draw(filename="circuit.txt",output = "text")))

        # Circuit 4, Expected outcome: [0,1]
        q4 = QuantumRegister(2)
        c4 = ClassicalRegister(2)
        qc4 = QuantumCircuit(q4, c4)
        qc4.h(q4[0])
        qc4.z(q4[1])
        qc4.h(q4[1])
        qobj4 = assemble(qc4, shots=2000, memory=True)
        circuits_qasm.append((qobj4,[0,1],qc4.draw(filename="circuit.txt",output = "text")))

        # Circuit 5, Expected outcome: [1,1]
        q5 = QuantumRegister(2)
        c5 = ClassicalRegister(2)
        qc5 = QuantumCircuit(q5, c5)
        qc5.h(q5[0])
        qc5.z(q5[1])
        qc5.h(q5[1])
        qc5.cx(q5[1],q5[0])
        qobj5 = assemble(qc5, shots=2000, memory=True)
        circuits_qasm.append((qobj5,[1,1],qc5.draw(filename="circuit.txt",output = "text")))

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
        qobj6 = assemble(qc6, shots=2000, memory=True)
        circuits_qasm.append((qobj6,[1,0],qc6.draw(filename="circuit.txt",output = "text")))

        # Circuit 7, Expected outcome: [1,1,0]
        q7 = QuantumRegister(3)
        c7 = ClassicalRegister(3)
        qc7 = QuantumCircuit(q7, c7)
        qc7.z(q7[0])
        qc7.z(q7[1])
        qc7.h(q7[0])
        qc7.h(q7[1])
        qc7.h(q7[2])
        qobj7 = assemble(qc7, shots=2000, memory=True)
        circuits_qasm.append((qobj7,[1,1,0],qc7.draw(filename="circuit.txt",output = "text"))) 

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
        qobj8 = assemble(qc8, shots=2000, memory=True)
        circuits_qasm.append((qobj8,[1,1,1],qc8.draw(filename="circuit.txt",output = "text")))

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
        qobj9 = assemble(qc9, shots=2000, memory=True)
        circuits_qasm.append((qobj9,[0,1,1],qc9.draw(filename="circuit.txt",output = "text")))

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
        qobj10 = assemble(qc10, shots=2000, memory=True)
        circuits_qasm.append((qobj10,[1,1,0,0],qc10.draw(filename="circuit.txt",output = "text")))

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
        qobj11 = assemble(qc11, shots=2000, memory=True)
        circuits_qasm.append((qobj11,[1,1,1,1],qc11.draw(filename="circuit.txt",output = "text")))

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
        qobj12 = assemble(qc12, shots=2000, memory=True)
        circuits_qasm.append((qobj12,[1,1,1,1],qc12.draw(filename="circuit.txt",output = "text")))

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
        qobj13 = assemble(qc13, shots=2000, memory=True)
        circuits_qasm.append((qobj13,[1,1,0,0,0],qc13.draw(filename="circuit.txt",output = "text")))

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
        qobj14 = assemble(qc14, shots=2000, memory=True)
        circuits_qasm.append((qobj14,[1,1,1,1,0],qc14.draw(filename="circuit.txt",output = "text")))

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
        qobj15 = assemble(qc15, shots=2000, memory=True)
        circuits_qasm.append((qobj15,[0,1,1,1,1],qc15.draw(filename="circuit.txt",output = "text")))
        return circuits_qasm







