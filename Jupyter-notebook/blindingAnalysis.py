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

    #circ = load(path)
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
    configFile = "config_noise.yaml"  #config_perfect.yaml,  config_default.yaml
    Mynum_times = 20
    exp_res = [1,1,1,1,0]

    normRateList = []
    ubqcRateList = []

    normalRes,correct_rate = normalSim(fileName,configFile
        ,maxQubits=20,num_times=Mynum_times,exp_result=exp_res)
    #print(f"normalRes :{normalRes}")
    #rint(f"normal crrect Rate :{correct_rate}")
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

    print(f"normRateList:{normRateList}")
    print(f"ubqcRateList:{ubqcRateList}")

    #=========================================================================
    '''
    #fig = plt.figure()
    fig = plt.subplots() 

    br1 = np.arange(len(normRateList))
    br2 = np.arange(len(ubqcRateList))

    x_axis = ['blinded', 'unblinded']
    successful_rate = [correct_rate,ubqc_correct_rate]

    plt.bar(x_axis, normRateList, color ='r', 
        edgecolor ='grey', width = 0.4, label='Noise case')
    plt.bar(x_axis, ubqcRateList, color ='b', 
        edgecolor ='grey',width = 0.4,  label='Loss case') 

    plt.title('Circuit 14')
    plt.ylabel('successful rate')
    plt.xlabel('circuit')
    plt.yticks(np.arange(0.0, 1.0, 0.1))
    #plt.xticks([r + 4 for r in range(len(normRateList))], ['blinded', 'unblinded'])
    plt.legend()

    plt.savefig('plotTest4.png')
    plt.show()
    '''
    #============================================
    df = pd.DataFrame({ 
    'Setting': ['Noise', 'Loss'], 
    'namal circuit': normRateList, 
    'UBQC circuit': ubqcRateList 
    }) 
    
    df.plot(x= 'Setting' ,y=['namal circuit','UBQC circuit'], kind="bar")  #"Noise case", "Loss case"

    plt.title('Circuit 14')
    plt.yticks(np.arange(0.0, 1.0, 0.1))
    plt.ylabel('successful rate')

    plt.savefig('plotTest6.png')
    plt.show()





