OPENQASM 3;
include "stdgates.inc";
bit[3] c136;
qubit[3] _all_qubits;
let q136 = _all_qubits[0:2];
z q136[0];
z q136[1];
h q136[0];
h q136[1];
h q136[2];
cx q136[0], q136[2];
cx q136[2], q136[0];
