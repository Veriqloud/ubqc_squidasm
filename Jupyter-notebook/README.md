# Universal Blind Quantum Computing protocol simulation
Here we simulate the UBQC protocol via the simulator SquidASM.
The protocol follows the typical client server scheme. With the server being able to measure qubits while the client only implements simple quantum gates and classical computation.
The UBQC protocol provides a scenario in which the client assigns a specific quantum circuit to the server to process without revealing much information about the circuit itself.  

# Software workflow
1. The client take circuit input via one of the three means:
	- Default example circuit from `circuit_qasm.py`.
	- From a `.qasm` file in your file system, a path would be needed.
	- Customized circuit described by coding outside the `run_simulation()` function.
2. The client take one of the config files: `config_xxx.yaml` for the noise level.
3. The protocol implements its algorithm.
4. The client achieves the final computation results.
5. Matching the expected results and the real results, software runs serveral times and calculates the successful rate for this simulation.


# How to run
1. Launch the jupyter notebook `UBQC_notebook.ipynb`. A jupyter window will showup. It is an user friendly interface to launch our simulation. Usually users does not need to edit files other then `UBQC_notebook.ipynb` and `config_xxx.yaml`.
2. Configure the simulation by tuning the parameters in function `run_simulation()` in the cells. Or use the default configuration without modification.
3. Press shift + enter keys to run a cell in the jupyter notebook. If the input circuit is legit, the software will draw the input circuit and give the computational results. 

# Note
- A new configuration file with noise or loss need to be included in `ubqcSim` function in order to extract the right outcome. Otherwise the successful rate will always be 0.

# Additional tool
One of the quantum circuit import method is via a `.qasm` file. For those who are not familiar with QASM syntax but want to try the feature, we provides a script(`makeQASMfile.py`) to convert Qiskit quantum circuit object to a `.qasm` file.
Or just use the example one: `qcircuitTest.qasm`. 


# Reference
- [VeriQloud GitHub](https://github.com/Veriqloud/ubqc_squidasm)

- [VeriQloud JupyterHub](https://jupyter.veriqloud.fr)

- [Reference compiler](https://github.com/quantumprotocolzoo/protocols/tree/master/UBQC)

"We acknowledge the support of the European Union’s Horizon 2020 research and innovation program through the FET project PHOQUSING (“PHOtonic Quantum SamplING machine” – Grant Agreement No. 899544)"

# Author
Original author:
- Younes Naceur (naceur.younes@yahoo.de)

Refine and maintain:
- Chin-Te Liao (liao.chinte@veriqloud.fr)
