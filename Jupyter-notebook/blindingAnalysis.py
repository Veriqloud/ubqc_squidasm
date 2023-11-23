'''
This script is used for comparing UBQC with corresponded original circuit.

'''
from squidasm.run.stack.config import StackNetworkConfig
from squidasm.run.stack.run import run

from qasm2squidasm import CircuitProgram
from UBQC_client import AliceProgram, LoadType
from UBQC_server import BobProgram
from circuits_qasm import qasm_circs
from qiskit.qasm3 import load


def normalSim(path,configfile,maxQubits,num_times):

    mypath = path
    cfg = StackNetworkConfig.from_file(configfile)

    maxQubits = maxQubits
    myCircuitProgram = CircuitProgram(maxQubits,mypath) # import from qasm code
    num_times = num_times
    resList = []

    for _ in range(num_times):
        run(config=cfg,
            programs={ "Bob": myCircuitProgram},
            num_times=1)
        resList.append(myCircuitProgram.res)

    return resList

def ubqcSim(path,configfile,maxQubits,num_times):

    circ = load(path)
    cfg = StackNetworkConfig.from_file(configfile)
    loadMethod = LoadType.FILE
    #"circuit": test_circ,"draw": draw, "log": log, "output": output_gates, "input": input_gates,
    test_circ = 1
    draw = False
    log = False
    output_gates = None
    input_gates = None

    args = { "circuit": test_circ,"draw": draw, "log": log, 
        "output": output_gates, "input": input_gates,
        "loadMethod": loadMethod,"loadPath": path}

    alice_program = AliceProgram(args)
    bob_program = BobProgram()
    
    resList = []
    for _ in range(num_times):
        resList.append(run(config=cfg,
            programs={"Alice": alice_program, "Bob": bob_program},
            num_times=1))

    return resList


if __name__ == "__main__":

    normalRes = normalSim("tempCircuit.qasm","config_perfect.yaml"
        ,maxQubits=20,num_times=1)
    print(f"normalRes :{normalRes}")

    ubquRes = ubqcSim("tempCircuit.qasm","config_perfect.yaml"
        ,maxQubits=20,num_times=1)
    print(f"ubquRes :{ubquRes}")


    

    






