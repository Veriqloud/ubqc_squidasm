from UBQC_client import AliceProgram
from UBQC_server import BobProgram
from squidasm.run.stack.config import StackNetworkConfig
from squidasm.run.stack.run import run
import netsquid

# Loading network configuration
cfg = StackNetworkConfig.from_file("config.yaml")

# Loading the server's and client's instructions
alice_program = AliceProgram()
bob_program = BobProgram()

# Settings for subroutine allowing us to display qubits
netsquid.set_qstate_formalism(netsquid.QFormalism.DM)

# Initialize array with results. Change here if the result of another circuit than circuit 4 (expected outcome: [1,1,0] should be confirmed. Change num_times to change number of iterations.
meas = []
meas.append(run(config=cfg,
    programs={"Alice": alice_program, "Bob": bob_program},
    num_times=50))
    
results = meas[0][0]
counter = 0
for i in range(len(results)):
	if(results[i] == [1,1,0]):
		counter += 1
		
print(f"Success probability: {counter} in {len(results)}")


