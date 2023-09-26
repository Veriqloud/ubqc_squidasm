'''
This script is used to generate QASM format files only.
This should not be included in the workflow of UBQC protocol. 
'''
from qiskit.circuit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit.qasm3 import dump

# Given circuit #9 in the default circuit for example
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

iostream = open("qcircuit9.qasm", "w", encoding="utf-8")
dump(qc9,iostream)

