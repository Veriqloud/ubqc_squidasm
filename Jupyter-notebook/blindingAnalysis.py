'''
This script is used for benchmarking UBQC protocol.
By running the blinded and unblinded circuit under the same hardware configuration,
We are able to see the efficiency differnce among the two.
'''
from squidasm.run.stack.config import StackNetworkConfig
from squidasm.run.stack.run import run
from circuits_qasm import qasm_circs
#from qiskit.qasm3 import load

from qasm2squidasm import CircuitProgram
from UBQC_client import AliceProgram, LoadType
from UBQC_server import BobProgram

import matplotlib.pyplot as plt
import pandas as pd 
import numpy as np

def normalSim(path,configfile,maxQubits,num_times,exp_result):

    mypath = path
    cfg = StackNetworkConfig.from_file(configfile)

    maxQubits = maxQubits
    myCircuitProgram = CircuitProgram(maxQubits,mypath) # import from qasm code
    num_times = num_times
    resList = []

    correct_counter = 0
    for _ in range(num_times):
        run(config=cfg,
            programs={ "Bob": myCircuitProgram},
            num_times=1)
        resList.append(myCircuitProgram.res)

        if myCircuitProgram.res == exp_result:
            correct_counter += 1

    if num_times != 0:
        return resList, correct_counter/num_times
    else:
        print("num_times cannot be 0!")

def ubqcSim(path,configfile,maxQubits,num_times,exp_result):

    cfg = StackNetworkConfig.from_file(configfile)
    loadMethod = LoadType.FILE
    test_circ = 1
    maxQubits = maxQubits
    draw = False
    log = False
    output_gates = None
    input_gates = None

    args = { "circuit": test_circ,"max_qubits":maxQubits,"draw": draw, "log": log, 
        "output": output_gates, "input": input_gates,
        "loadMethod": loadMethod,"loadPath": path} # arguments needed for UBQC protocol

    alice_program = AliceProgram(args)
    bob_program = BobProgram(max_qubits=100)
    
    resListTmp = []
    resList = []
    correct_counter = 0
    for _ in range(num_times):
        resListTmp.append(run(config=cfg,
            programs={"Alice": alice_program, "Bob": bob_program},
            num_times=1))

    # extract only the result
    if(configfile!="config_noise.yaml" and configfile!="config_lossy_link.yaml"):    
        resList = resListTmp[0][0]

    if(configfile=="config_noise.yaml" or configfile=="config_lossy_link.yaml"):
        #print(f"resListTmp :{resListTmp}")

        results = [resListTmp[i][1][0][0] for i in range(num_times)]
        resList.append(results)


        for i in range(len(results)):
            if(results[i] == exp_result):
                correct_counter += 1
    

    return resList, correct_counter/num_times



if __name__ == "__main__":

    fileName = "tempCircuit.qasm"
    Mynum_times = 100
    exp_res = [1,1,1,1,0]

    normRateList = []
    ubqcRateList = []

    configFile = "config_noise.yaml"  #config_perfect.yaml,  config_default.yaml

    normalRes,correct_rate = normalSim(fileName,configFile
        ,maxQubits=20,num_times=Mynum_times,exp_result=exp_res)
    #print(f"normalRes :{normalRes}")
    #print(f"normal crrect Rate :{correct_rate}")
    normRateList.append(correct_rate)
    

    ubquRes, ubqc_correct_rate = ubqcSim(fileName,configFile
        ,maxQubits=20,num_times=Mynum_times,exp_result=exp_res)
    #print(f"ubquRes :{ubquRes}")
    #print(f"ubqc crrect Rate :{ubqc_correct_rate}")
    ubqcRateList.append(ubqc_correct_rate)

    #=========================================================================
    
    configFile = "config_lossy_link.yaml"
    normalRes,correct_rate = normalSim(fileName,configFile
        ,maxQubits=20,num_times=Mynum_times,exp_result=exp_res)
    #print(f"normalRes :{normalRes}")
    #print(f"normal crrect Rate :{correct_rate}")
    normRateList.append(correct_rate)
    

    ubquRes, ubqc_correct_rate = ubqcSim(fileName,configFile
        ,maxQubits=20,num_times=Mynum_times,exp_result=exp_res)
    #print(f"ubquRes :{ubquRes}")
    #print(f"ubqc crrect Rate :{ubqc_correct_rate}")
    ubqcRateList.append(ubqc_correct_rate)

    #print(f"normRateList:{normRateList}")
    #print(f"ubqcRateList:{ubqcRateList}")
    
    #=========================================================================
    print(f"normRateList:{normRateList}")
    print(f"ubqcRateList:{ubqcRateList}")
    #, 'Loss' 
    #'Setting': ['Noise on'], 
    df = pd.DataFrame({ 
    'Setting': ['only noise', 'only loss'], 
    'nomal circuit': normRateList, 
    'UBQC circuit': ubqcRateList 
    }) # requires the same size in list

    
    df.plot(x= 'Setting' ,y=['nomal circuit','UBQC circuit'], kind="bar")  #"Noise case", "Loss case"
    #plt.xticks(rotation=90)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.subplots_adjust(left=0.1, right=0.9, top=0.9 ) #bottom=0.8

    plt.title('UBQC algorithm benchmarking on Circuit 14 ')
    plt.yticks(np.arange(0.0, 1.0, 0.1))
    plt.ylabel('successful rate')

    plt.savefig('plotTest6.png',bbox_inches='tight')
    plt.show()





