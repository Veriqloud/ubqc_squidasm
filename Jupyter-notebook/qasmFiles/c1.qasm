OPENQASM 3;
include "stdgates.inc";
bit[1] c17;
qubit[1] _all_qubits;
let q17 = _all_qubits[0:0];
z q17[0];
h q17[0];
rx(128.0) q17[0];
