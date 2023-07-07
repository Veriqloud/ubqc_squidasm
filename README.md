# Compiler for UBQC using SquidASM
A compiler to simulate Universal Blind Quantum Computation [1] using the quantum network simulation software SquidASM with Qiskit/QASM circuits as an input. As the basic framework an outdated compiler using SimulaQron has been modified, which can be found in the reference section [2].

## 0. Outline
#### 1. Introduction to UBQC
#### 2. File structure
#### 3. Running the simulation
#### 4. Changes from the old compiler
#### 5. Performance
#### 6. Discussion
#### 7. Security Benchmarking
#### 8. Appendix
#### 9. References

## 1. UBQC
Universal Blind Quantum Computation provides a method for a client without any quantum computational power to execute quantum computations on a remote server without revealing neither the input nor the output. The measurement-based scheme for quantum computation (MBQC) is chosen as the foundation. This is a different approach to quantum computation than the gate-based one, while it's possible to construct MBQC instructions from any given gate-based circuit. These instructions consist of three types of objects: Entanglement operations, measurement instructions, and byproduct operators. To be able to run these instructions according to [1], one needs to reorder these instructions by making use of commutation relations. Like this, we can achieve that first all entanglement operations are perforemed, then all the measurements, and finally the byproducts. This so called $\textit{flow}$ first been first introduced by Kashefi et al. [3].

The UBQC protocol relies on a mixture between classical and quantum communication: The idea is that, similarly to MBQC, quantum states are evolved through projective measurements, where the exact measurement angles are hidden from the server, providing that no information about the client's computation get's leaked. This protocol is meant to be executed using real quantum machines, while in this work the aim is to simulate the protocol using SquidASM.

**The protocol can be sumarized using the following steps:**


**1.** For each qubit: Alice initializes it, applies random phase $\theta_i$

**2.** Alice further blinds the i-th qubit with an angle $r_i \in {0, \pi }$ 

**3.** Alice sends the blinded qubit to Bob, together with measurement angles $\phi_i ' = \phi + \theta_i + r_i$

**4.** Alice entanglement instructions to Bob  

**5.** Bob entangles the qubits, creates graph state 

**6.** Bob measures the qubits successively in the provided basis, sends results back to Alice

**7.** Alice unblinds the qubits by applying phases $- \theta_i$ 

**8.** Alice applies Byproduct operators depending on Bob's measurement outcome 

Here $\phi$ refers to the measurement angle that's acquired through the flow construction of a given gate. $\theta$ can be chosen in different scales, where in this implementation $\theta$ can take 256 values between 0 and $2\pi$. After these steps are performed, the qubits that Alice corrected should be in the quantum state that was predicted as the outcome of the simulated circuit, where the computation was run without revealing it to Bob.

## 2. File structure

#### 2.1 measurement.py
- Contains the instructions to convert a QASM object into the correspondent MBQC instructions

#### 2.2 flow.py
- Reorders the measurement instructions, putting them in the EMC order (Entanglement, measurement, correction)

#### 2.3 circuits_qasm.py
- Contains 15 test circuits on which the protocol can be tested. Circuits are first defined over Qiskit and then converted to QASM objects. This yields the possibility to simulate arbitrary qiskit circuits by loading them here.

#### 2.4 angles.py
- Contains instructions on how to compute the angle that Alice has to send to Bob, including the actual computational angle as well as Alice's blinding angle.

#### 2.5 ubqc_client.py
- Characteristic to SquidASM. Includes all the instructions for the client's side to run the protocol.

#### 2.6 ubqc_server.py
- Chracteristic to SquidASM. Includes the instructinos on the server's side to run the protocol.

#### 2.7 config_().yaml
- Characteristic to SquidASM. File to configure the network and the type of noise that's simulated: Possibility to modify the amount of noise that's simulated on either parties side, as well as the quantum communication channel itself. The default configuration (config_default.yaml), a perfect noiseless configuration (config_perfect.yaml), and a customized noise configuration (config_noise.yaml) are provided. The user can switch between those in the file run_ubqc.py.

#### 2.8 run_ubqc.py
- Characteristic to SquidASM. File for simulation control: Yields the possibility to run the simulation N times and infer about the statistical likelyhood of success. Configure this file to change the number of runs as well as the output. Configuration file is also chosen here.

#### 2.9 benchmarking.py
- Used to estimate the security of the protocol. See section 7 for further information.

## 3. Running the simulation
Functioning versions of SquidASM [4] and NetQASM [5] on the user's side are required to run the simulation. To run the simulation, head to the directory in which the files are deposited. Using the consol, python run_ubqc.py can be used to run the simulation given the current settings provided in run_ubqc.py. Possible arguments include:
- $\texttt{- l}$ for enabling and disabling the logging
- $\texttt{- c \{ CIRCUIT \} }$ for choosing a circuit from circuits_qasm.py. Note that enumeration starts from zero.
- $\texttt{- d}$ to enable or disable the drawing of the circuit
- $\texttt{- i \{ GATES \} }$ for choosing input gates that are applied onto the input qubits independently from the chosen circuit. Seperation: Comma
- $\texttt{- o \{ GATES \} }$ for choosing output gates that are applied onto the output qubits independently from the chosen circuit. Seperation: Comma
- $\texttt{- h}$ for help

## 4. Changes from the old protocol
For debugging reasons, in this section the changes from the original protocol in SimulaQron are introduced

#### 4.1 Changing the input format from JSON to QASM:
- Used qiskit.qobj_todict function to extract information from QASM objects, these dictionaries can be treated equivalently to JSON files
- Only changes made in measurement.py, flow.py receives the same input as in the original compiler
- Provides naturally the option to simulate Qiskit circuits directly
- Outcome has been tested on all test circuits provided by the old compiler

#### 4.2 Changing from SimulaQron to SquidASM
- Had to find correspondant functions in SquidASM to provide classical and quantum communication
- Classical communication: One to one correspondance between the programs
- Rotations: Slightly adjusted Syntax between SimulaQron and SquidASM
- Quantum communication: SimulaQron provides way to directly send qubits from Alice to Bob, SquidASM only offers EPR pairs 
- Implemented Quantum State Teleportation to transfer qubits from Alice to Bob

#### 4.3 Verifying the circuit
- SquidASM's only subroutine to infer about qubit states are computational basis measurements, not revealing the full qubit state
- Subroutine in NetQASM has been implemented to convert SquidASM qubits to NetQASM, then using a NetQASM function to display the state

#### 4.4 Implementation of X and Z gates
- X and Z gates in circuits were not simulated correctly using the old compiler
- These gates get converted into byproduct operators in the flow construction, not containing any measurement's outcome as a condition
- Byproduct operators in the old compiler were only executed if the condition was fulfilled, not when there was no condition
- Changing this solved the problem

#### 4.5 Generalization to N qubits
- Old compiler was only tested on 1 and 2 qubit circuits
- Running three and four qubit circuits on the new compiler yielded issues: Circuits' simulations outcome depended on the order of which commuting (!) gates were executed in the Qiskit circuit
- Issue with indices was found: Old compiler contained two arrays with indices for output qubits: qout_idx and qidx_sort. Using only the sorted version solved the problem.

#### 4.6 Changing of the drawing engine
- Old compiler used projetq to draw the circuit that the client wants to simulate
- Heavy module, replaced it through Qiskit's drawing engine since Qiskit was used anyway for treatment of QASM input files

#### 4.7 Statistics
- run_UBQC.py was not working properly if the protocol was run N>1 times. Issue: Qubit array on the server's side was initialized before the program was run, leading to overwriting of the N-ths simulation qubit array through the N+1-st. 
- Including the initialization of the qubit array into the beginning of the server's instructions rather then before leads to reinitialization each time the simulation is run, solving the problem

#### 4.8 Added noise
- Noise was added in the simulation to achieve more realistic result; the applied model contains noise for local qubit operations on either party's side, but no noise emerging from the quantum communication channel itself.

## 5. Performance

![alt text](https://github.com/veriqloud/ubqc_squidasm/blob/main/plots/internship_plot_compqubits_noise_accumulated.png?raw=true)

![alt text](https://github.com/veriqloud/ubqc_squidasm/blob/main/plots/internship_plot_nmeas_noise_accumulated.png?raw=true)

![alt text](https://github.com/veriqloud/ubqc_squidasm/blob/main/plots/internship_plot_outputqubits_noise.png?raw=true)

![alt text](https://github.com/veriqloud/ubqc_squidasm/blob/main/plots/internship_plot_entanglements_noise.png?raw=true)

## 6. Discussion
- Success probability depends on the number of qubits that are used for the computation: 1% failure chance for one qubit circuits, while this increases with the number of computational (!) qubits necessary for MBQC. Reason: Default configuration was indeed not noiseless
- Also correlation of success probability with the number of measurements needed
- Displaying the density matrices of the output states shows slight deviations from the expected DM, leading to wrong measurement results in a small fraction of the iterations
- Quantum State Teleportation implementation doesn't teleport the state 100% accurately, probably being the reason for the algorithm to fail at times. This is coherent with the fact that the more computational qubits we need, the more qubits we have to teleport and the higher the chance of failure becomes. Reason here again is SquidASM's default noise configuration file
- Besides the correlation with a high amount of measurements and a high amount of computational qubits needed, a correlation with the types of gates is apparent in the default case (circuits with more #CNOT appear to fail more often, when comparing with equivalent circuits in terms of nMeas, nQubits). Reason: Two qubit gates come with a higher depolarization chance in the default case.
- SquidASM's default file includes noise, had to be manipulated to reach $\approx$ 100\% success probability. Perfectly noiseless configuration can be found in config_perfect.yaml
- Even with the customized noise the success probability is significantly higher than the joint coin flip probability $1/2^N$ of a given circuit. Indicator that the protocol can be used to infer about the result of a UBQC computation even in the presence of noise, if the sample size is big enough.

## 7. Security Benchmarking
Besides the accuracy, the security of the protocol is another aspect that can be estimated. As a measure for security we take the probability for Bob to guess the right circuit that Alice wants to implement. For that, the following assumptions are made:

- The only gates that a circuit can consist of are the fundamental set **(X,Z,J,CZ,H)**
- Since X and Z gates appear only in the section of byproduct operators, Bob has no way to infer about their application (all estimated probabilities are up to an arbitrary number of these gates)
- The only information that Bob gets from Alice are the number of computational qubits, the number of measurements, and the number of entangled pairs
- Whenever a measurement at a given angle is performed (meaning a H or J gate), Bob cannot infer information about the measurement angle and hence has a chance of 1/256 to guess the computational angle implementing the given gate
- Different possible circuits are identified with each other if they are equivalent

To get an estimate for the probability for Bob to guess the right circuit, one has to find out how many circuits are consistent with the information given by Alice. Each fundamental gate is associated with the following instructions in the MBQC formalism:

|Gate|# of qubits added|# of measurements|# of entanglements
|---|---|---|---|
|**X**|0|0|0|
|**Z**|0|0|0|
|**H**|1|1|1|
|**J**|1|1|1|
|**CZ**|0|0|1|

Taken these into account, the problem of finding the number of consistent combinations boils down to a combinatorial problem. This again shows that Bob doesn't gather any data about X and Z gates, which is why we should rather speak of different possible circuit classes up to these gates rather than particular circuits here. Nonetheless the term is dropped to ease the description.
After all possible sets of gates are found by solving the aforementioned combinatorial problem, the number of output qubits of a given circuit is calculated via $N_{qubits} - N_{meas}$. Then all possible combinations of each set acting on each possible output qubit are getting constructed, to get a comprehensive list of circuits that are consistent with the given variables. After this is performed, all of these circuits are getting converted to Qiskit circuit, to make use of the function \textit{transpiler}, transforming circuits to their easiest equivalent. Comparing the statevectors of the given circuits with each other lets one exclude redundant circuits from the list. This finally leaves one with all distinguishable circuits that are consistent with the data Bob received from Alice, and hence with the probability of him to overcome the blindness. The code to estimate the probability and to display the given circuits for a given set of variables can be found in benchmarking.py. **Note**: In the code CX gates are used as placeholders for J gates, since they are not native in Python. This will be adjusted.

## 8. Appendix

## 8.1 Test Circuits

Drawings of the circuits that the compiler was tested upon can be found in the folder test_circuits.

### 8.2 Classification of test circuits

|Circuit| Expected Outcome|#Qubits|#Computational qubits|#Measurements|#Entanglements|
| ----- |-------|------|------|------|------|
|1      | **[0]**   | 1    | 2    | 1    |  1   |
|2      | **[0]**   | 1    | 2    | 2    |  3   |
|3      | **[0]**   | 1    | 4    | 3    |  1   |
|4      | **[0,1]**   | 2    | 4    | 2    |  2   |
|5      | **[1,1]**   | 2    | 6    | 4    |  5   |
|6      | **[1,0]**   | 2    | 10    | 8    |  11   |
|7      | **[1,1,0]**   | 3    | 6    | 3    |  3   |
|8      | **[1,1,1]**   | 3    | 6    | 5    |  6   |
|9      | **[0,1,1]**   | 3    | 10    | 7    |  9  |
|10      | **[1,1,0,0]**   | 4    | 8    | 4    |  4   |
|11      | **[1,1,1,1]**   | 4    | 10    | 6    |  7   |
|12      | **[1,1,1,1]**   | 4    | 12    | 8    |  9   |
|13      | **[1,1,0,0,0]**   | 5    | 10    | 5    |  8   |
|14      | **[1,1,1,1,0]**   | 5    | 14    | 9    |  10   |
|15      | **[0,1,1,1,1]**   | 5    | 18    | 13    |  15   |

### 8.3 Results with default noise

|Circuit/Iteration|1|2|3|4|5|6|7|8|9|10|Mean|STD|
|----|----|----|----|----|----|----|----|----|----|----|----|----|
1|100|99|100     | 98      | 98      | 99      | 97      | 99      | 99      | 97       |**98.6**| 1.0 |
2       | 98      | 97      | 97      | 96      | 97      | 98      | 100     | 99      | 100     | 98       |**98.0** | 1.3 |
3       | 94      | 94      | 97      | 98      | 94      | 93      | 91      | 96      | 95      | 96       |**94.8** | 1.9 |
4       | 97      | 95      | 96      | 97      | 98      | 95      | 94      | 92      | 92      | 92       |**94.8** | 2.1 |
5       | 92      | 88      | 93      | 88      | 91      | 93      | 92      | 95      | 92      | 93       |**91.7** | 2.1 |
6       | 85      | 80      | 77      | 82      | 82      | 85      | 81      | 89      | 82      | 81       |**82.3**|  3.1 |
7       | 88      | 95      | 94      | 94      | 95      | 89      | 90      | 95      | 90      | 98       |**92.8** | 3.1 |
8       | 88      | 96      | 92      | 89      | 94      | 92      | 94      | 93      | 91      | 89       |**91.8**| 2.4 |
9       | 85      | 85      | 87      | 84      | 90      | 80      | 82      | 94      | 85      | 89       |**86.1** | 3.9 |
10      | 89      | 86      | 90      | 89      |86      | 88      | 87      | 95      | 93      | 88       |**89.1** | 2.8 |
11      | 86      | 92      | 85      | 91      | 92      | 85      | 85      | 83      | 89      | 90       |**87.8** | 3.2 |
12      | 87      | 87      | 85      | 86      | 87      | 80      | 89      | 81      | 90      | 84       |**85.6** | 3.0 |
13      | 93      | 86      | 95      | 90      | 86      | 84      | 90      | 90      | 90      | 93       |**89.7** | 3.3 |
14      | 84      | 84      | 84      | 83      | 81      | 80      | 90      | 78      | 77      | 87       |**82.8** | 3.8 |
15      | 77      | 73      | 87      | 75      | 75      | 80      | 74      | 83      | 77      | 88       |**78.9** | 5.1|

All results here refer to the success rate out of 100 iterations for a given circuit.

### 8.4 Results with tailored noise

|Circuit/Iteration|1|2|3|4|5|6|7|8|9|10|Mean|STD|
|---|---|---|---|---|---|---|---|---|---|---|---|---|
1       | 63|72|69|74|66|72|66|75|72|77      |**70.6** | 4.2 |
2       | 50|72|63|57|55|68|56|63|57|57    |**59.8** | 6.3 |
3       | 63|72|63|69|71|70|58|73|66|80      |**68.5** | 5.9|
4       | 46|46|55|33|49|45|43|58|48|43      |**46.6** | 6.5 |
5       | 36|34|46|41|36|35|34|41|42|39       |**38.4** | 3.8 |
6       | 23|24|28|28|28|25|24|24|23|29     |**25.6** | 2.2 |
7       | 36|33|44|39|39|30|41|32|36|44     |**37.4** | 4.6 |
8       | 20|23|28|28|30|26|30|26|31|27      |**26.9** | 3.2 |
9       | 24|24|23|21|23|19|25|17|31|23      |**23.0** | 3.5 |
10      | 25|27|26|30|28|20|23|28|27|17      |**25.1** | 3.8 |
11      | 21|14|18|21|19|14|20|19|23|20      |**18.9**| 2.8 |
12      | 12|10|13|16|16|17|13|20|9|14     |**14.0** | 3.2 |
13      | 17|27|16|19|19|25|12|14|13|10    |**17.2** | 5.2 |
14      | 17|15|14|13|11|10|12|6|9|13      |**12.0** |3.0 |
15      | 7|4|6|10|7|7|5|13|13|12      |**8.4** | 3.2|

Again, the results refer to the success rate out of 100 iterations for each test circuit.

## 9. References
[1] "Universal Blind Quantum Computation", Kashefi et al. 2009

[2] Original Compiler: https://github.com/quantumprotocolzoo/protocols/tree/master/UBQC

[3] "The Measurement Calculus", Kashefi et al. 2007

[4] https://squidasm.readthedocs.io

[5] https://netqasm.readthedocs.io/en/latest/
