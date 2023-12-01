OPENQASM 3;
include "stdgates.inc";
bit[2] c0;
qubit[2] _all_qubits;
let q0 = _all_qubits[0:1];
h q0[0];
z q0[1];
h q0[1];
cx q0[1], q0[0];
