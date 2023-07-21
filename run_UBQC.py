from UBQC_client import AliceProgram
from UBQC_server import BobProgram
from squidasm.run.stack.config import StackNetworkConfig
from squidasm.run.stack.run import run
import netsquid
netsquid.set_qstate_formalism(netsquid.QFormalism.KET)

# Here: Choose noise configuration. Can choose between the default configuration (config_default.yaml), a perfect config (config_perfect)
# and a customized noise configuration (config_noise.yaml). Standard is perfect configuration.

cfg = StackNetworkConfig.from_file("config_perfect.yaml")

# Load client's and server's instructions

alice_program = AliceProgram()
bob_program = BobProgram()

# Initialize array with simulation results

meas = []

# Run the simulation. Number of iterations can be changed here.

meas.append(run(config=cfg,
    programs={"Alice": alice_program, "Bob": bob_program},
    num_times=100))
    
results = meas[0][0]

# Estimating the success rate by comparing the measurement results with the expected results (found for test circuits in circuits_qasm.py)

counter = 0

for i in range(len(results)):
	if(results[i][0] == results[i][1]):
		counter += 1
		
print(f"Success rate: {counter} in {len(results)}")



