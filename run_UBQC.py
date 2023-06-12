from UBQC_client import AliceProgram
from UBQC_server import BobProgram
from squidasm.run.stack.config import StackNetworkConfig
from squidasm.run.stack.run import run
import netsquid



cfg = StackNetworkConfig.from_file("config.yaml")


alice_program = AliceProgram()
bob_program = BobProgram()

netsquid.set_qstate_formalism(netsquid.QFormalism.DM)
meas = []
meas.append(run(config=cfg,
    programs={"Alice": alice_program, "Bob": bob_program},
    num_times=1))
    
results = meas[0][0]
counter = 0
for i in range(len(results)):
	if(results[i] == [1,1,0]):
		counter += 1
		
print(f"Success probability: {counter} in {len(results)}")


