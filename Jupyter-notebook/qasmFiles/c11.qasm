OPENQASM 3;
include "stdgates.inc";
bit[4] c187;
qubit[4] _all_qubits;
let q187 = _all_qubits[0:3];
z q187[0];
z q187[1];
h q187[0];
h q187[1];
h q187[2];
h q187[3];
h q187[2];
z q187[2];
h q187[2];
cx q187[2], q187[3];