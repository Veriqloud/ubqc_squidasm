# Universal Blind Quantum Computing protocol simulation
Here we simulate the UBQC protocol via the simulator SquidASM.
The protocol follows the typical client server scheme. With the server being the more competent while the client only implements simple quantum gates.
The UBQC protocol provides a scenario in which the client assigns a specific quantum circuit to the server to compute without revealing much information about the circuit itself.  

# Software workflow
1. The client take circuit input via one of the three means:
	- Default example circuit from **circuit_qasm.py**
	- From a **.qasm** file in the current folder.
	- Customized circuit described by coding outside the function.
2. The client take one of the config files: **config_xxx.yaml** for the noise level.
3. The protocol implements its algorithm.
4. The client achieves the final computation results.
5. Matching the expected results and the real results, software calculates the successful rate.


## How to run simulation

1. Launch jupyter notebook **UBQC_notebook.ipynb**.
2. Configure the simulation by tuning the parameters of function **run_simulation()** in the small cells. Or use the default configuration without modification.
3. Press shift + enter keys to run a cell in the jupyter notebook.


# Reference
[Veriqloud GitHub](https://github.com/Veriqloud/ubqc_squidasm)


# Author:
Original author:
- Younes Naceur (naceur.younes@yahoo.de)
Refine and maintain:
- Chin-Te Liao (liao.chinte@veriqloud.fr)
