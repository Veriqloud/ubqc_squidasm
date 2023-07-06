from UBQC_client import AliceProgram
from UBQC_server import BobProgram
from squidasm.run.stack.config import StackNetworkConfig
from squidasm.run.stack.run import run
import netsquid

cfg = StackNetworkConfig.from_file("config.yaml")

alice_program = AliceProgram()
bob_program = BobProgram()

netsquid.set_qstate_formalism(netsquid.QFormalism.KET)
meas = []
meas.append(run(config=cfg,
    programs={"Alice": alice_program, "Bob": bob_program},
    num_times=100))
    
results = meas[0][0]

counter = 0

for i in range(len(results)):
	if(results[i][0] == results[i][1]):
		counter += 1
		
print(f"Success rate: {counter} in {len(results)}")



