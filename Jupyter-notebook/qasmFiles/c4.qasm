OPENQASM 3;
include "stdgates.inc";
bit[2] c68;
qubit[2] _all_qubits;
let q68 = _all_qubits[0:1];
h q68[0];
z q68[1];
h q68[1];
cx q68[1], q68[0];
