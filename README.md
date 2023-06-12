# Compiler for UBQC using SquidASM
A compiler to simulate Universal Blind Quantum Computation using the quantum network simulation software SquidASM. As the basic framework an outdated compiler using SimulaQron has been modified.

## 0. UBQC
Universal Blind Quantum Computation provides a method for a client without any quantum computational power to execute quantum computations on a remote server without revealing neither the input nor the output. The measurement-based scheme for quantum computation (MBQC) is chosen as the foundation. This is a different approach to quantum computation than the gate-based one, while it's possible to construct MBQC instructions from any given gate-based circuit. These instructions consist of three types of objects: Entanglement operations, measurement instructions, and byproduct operators.
The UBQC protocol relies on a mixture between classical and quantum communication: The idea is that, similarly to MBQC, quantum states are evolved through projective measurements, where the exact measurement angles are hidden from the server, providing that no information about the client's computation get's leaked. This protocol is meant to be executed using real quantum machines, while in this work the aim is to simulate the protocol using SquidASM.

The protocol can be sumarized using the following steps:

1. Alice initializes her qubits, applies random phase $\theta$\\
2. Alice further blinds her computation with an angle $r \in \{0, \pi \}$ \\
3. Alice sends the blinded qubits to Bob, together with measurement angles $\phi ' = \phi + \theta + r$\\
4. Alice sends lists of qubits to entangle  \\
5. Bob entangles the qubits, creates cluster state \\
6. Bob measures the qubits in the provided basis, sends results back to Alice \\
7. Alice unblinds the qubits by applying phase $- \theta$ \\
8. Alice applies Byproduct operators depending on Bob's measurement outcome \\

After these steps are performed, the qubits that Alice corrected should be in the quantum state that was predicted as the outcome of the simulated circuit, where the computation was run without revealing it to Bob.

## 1. File structure

1.1 measurement.py
- Contains the instructions to convert a QASM object into the correspondent MBQC instructions

1.2 flow.py
- Reorders the measurement instructions, putting them in the EMC order (Entanglement, measurement, correction)

1.3 circuits_qasm.py
- Contains 20 test circuits on which the protocol can be tested. Circuits are first defined over Qiskit and then converted to QASM objects. This yields the possibility to simulate arbitrary qiskit circuits by loading them here.

1.4 angles.py
- Contains instructions on how to compute the angle that Alice has to send to Bob, including the actual computational angle as well as Alice's blinding angle.

1.5 ubqc_client.py
- Characteristic to SquidASM. Includes all the instructions for the client's side to run the protocol.

1.6 ubqc_server.py
- Chracteristic to SquidASM. Includes the instructinos on the server's side to run the protocol.

1.7 config.yaml
- Characteristic to SquidASM. File to configure the network and the type of noise that's simulated: Possibility to modify the amount of noise that's simulated on either parties side, as well as the quantum communication channel itself. Default is a perfect generic connection.

1.8 run_ubqc.py
- Characteristic to SquidASM. File for simulation control: Yields the possibility to run the simulation N times and infer about the statistical likelyhood of success. Configure this file to change the number of runs as well as the output.

## 2. Changes from the old protocol
For debugging reasons, in this section the changes from the original protocol in SimulaQron are introduced:

2.1 Changing the input format from JSON to QASM:
- Used qiskit.qobj_todict function to extract information from QASM objects, these dictionaries can be treated equivalently to JSON files
- Only changes made in measurement.py, flow.py receives the same input as in the original compiler
- Provides naturally the option to simulate Qiskit circuits directly
- Outcome has been tested on all test circuits provided by the old compiler

2.2 Changing from SimulaQron to SquidASM
- Had to find correspondant functions in SquidASM to provide classical and quantum communication
- Classical communication: One to one correspondance between the programs
- Rotations: Slightly adjusted Syntax between SimulaQron and SquidASM
- Quantum communication: SimulaQron provides way to directly send qubits from Alice to Bob, SquidASM only offers EPR pairs 
- Implemented Quantum State Teleportation to transfer qubits from Alice to Bob

2.3 Verifying the circuit
- SquidASM's only subroutine to infer about qubit states are computational basis measurements, not revealing the full qubit state
- Subroutine in NetQASM has been implemented to convert SquidASM qubits to NetQASM, then using a NetQASM function to display the state

2.4 Implementation of X and Z gates
- X and Z gates in circuits were not simulated correctly in the old protocol
- Get converted into Byproduct operators in the flow, not containing any measurement's outcome as a condition
- Byproduct operators in the old compiler were only executed if the condition was fulfilled, not when there was no condition
- Changing this solved the problem

2.5 Generalization to N qubits
- Old compiler was only tested on 1 and 2 qubit circuits
- Running three and four qubit circuits on the new compiler yielded issues: Circuits' simulations outcome depended on the order of which commuting (!) gates were executed in the Qiskit circuit
- Issue with indices was found: Old compiler contained two arrays with indices for output qubits: qout_idx and qidx_sort. Using only the sorted version solved the problem.

2.6 Changing of the drawing engine
- Old compiler used projetq to draw the circuit that the client wants to simulate
- Heavy module, replaced it through Qiskit's drawing engine since Qiskit was used anyway for treatment of QASM input files

2.7 Statistics
- run_UBQC.py was not working properly if the protocol was run N>1 times. Issue: Qubit array on the server's side was initialized before the program was run, leading to overwriting of the N-ths simulation qubit array through the N+1-st. 
- Including the initialization of the qubit array into the beginning of the server's instructions rather then before leads to reinitialization each time the simulation is run, solving the problem

## 3. Outlook 
- Success probability depends on the number of qubits that are used for the computation: 1% failure chance for one qubit circuits, while this increases with the number of computational (!) qubits necessary for MBQC.
- Displaying the density matrices of the output states shows slight deviations from the expected DM, leading to wrong measurement results in a small fraction of the iterations
- Quantum State Teleportation implementation doesn't teleport the state 100% accurately, probably being the reason for the algorithm to fail at times. This is coherent with the fact that the more computational qubits we need, the more qubits we have to teleport and the higher the chance of failure becomes.
