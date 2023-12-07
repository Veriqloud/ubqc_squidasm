OPENQASM 3;
include "stdgates.inc";
bit[2] c51;
qubit[2] _all_qubits;
let q51 = _all_qubits[0:1];
h q51[0];
z q51[1];
h q51[1];
