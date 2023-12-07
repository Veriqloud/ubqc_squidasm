OPENQASM 3;
include "stdgates.inc";
bit[1] c0;
qubit[1] _all_qubits;
let q0 = _all_qubits[0:0];
h q0[0];
