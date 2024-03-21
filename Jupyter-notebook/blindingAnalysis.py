'''
This script is used for benchmarking UBQC protocol.
By running the blinded and unblinded circuit under the same hardware configuration,
We are able to see the efficiency differnce among the two.
'''
from squidasm.run.stack.config import StackNetworkConfig
from squidasm.run.stack.run import run

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

    #print(f"resListTmp: {resListTmp}")
    # extract only the result
    if(configfile!="config_noise_low.yaml" and configfile!="config_lossy_link.yaml" and configfile!="config_noise_high.yaml" ):    
        resList = resListTmp[0][0]
        #print(f"~~resList:{resList}")

    if(configfile=="config_noise_low.yaml" or configfile=="config_lossy_link.yaml" or configfile=="config_noise_high.yaml" ):
        #print(f"resListTmp :{resListTmp}")
        results = [resListTmp[i][1][0][0] for i in range(num_times)]
        resList.append(results)

        

        for i in range(len(results)):
            if(results[i] == exp_result):
                correct_counter += 1

    #print(f"~resList:{resList}")

    return resList, correct_counter/num_times



if __name__ == "__main__":

    fileName = "testCircuit5.qasm"
    Mynum_times = 200
    exp_res = [1,1] #[1,1,1,1,0]

    normRateList = []
    ubqcRateList = []
    '''
    configFile = "config_perfect.yaml"  #config_perfect.yaml,  config_default.yaml

    normalRes,correct_rate = normalSim(fileName,configFile
        ,maxQubits=20,num_times=Mynum_times,exp_result=exp_res)
    #print(f"normalRes :{normalRes}")
    #print(f"normal crrect Rate :{correct_rate}")
    normRateList.append(correct_rate)
    

    ubquRes, ubqc_correct_rate = ubqcSim(fileName,configFile
        ,maxQubits=20,num_times=Mynum_times,exp_result=exp_res)
    print(f"ubquRes :{ubquRes}")
    print(f"ubqc crrect Rate :{ubqc_correct_rate}")
    ubqcRateList.append(ubqc_correct_rate)
    '''
    #=============================================================================
    configFile = "config_noise_low.yaml"  #config_perfect.yaml,  config_default.yaml

    normalRes1,correct_rate1 = normalSim(fileName,configFile
        ,maxQubits=20,num_times=Mynum_times,exp_result=exp_res)
    #print(f"normalRes1 :{normalRes1}")
    #print(f"normal crrect Rate1 :{correct_rate1}")
    normRateList.append(correct_rate1)
    

    ubquRes1, ubqc_correct_rate1 = ubqcSim(fileName,configFile
        ,maxQubits=20,num_times=Mynum_times,exp_result=exp_res)
    #print(f"ubquRes1 :{ubquRes1}")
    #print(f"ubqc crrect Rate1 :{ubqc_correct_rate1}")
    ubqcRateList.append(ubqc_correct_rate1)

    #=========================================================================
    
    configFile = "config_noise_high.yaml"
    normalRes2,correct_rate2 = normalSim(fileName,configFile
        ,maxQubits=20,num_times=Mynum_times,exp_result=exp_res)
    '''
    print(f"normalRes2 :{normalRes2}")
    print(f"normal crrect Rate2 :{correct_rate2}")
    '''
    normRateList.append(correct_rate2)
    

    ubquRes2, ubqc_correct_rate2 = ubqcSim(fileName,configFile
        ,maxQubits=20,num_times=Mynum_times,exp_result=exp_res)
    '''
    print(f"ubquRes2 :{ubquRes2}")
    print(f"ubqc crrect Rate2 :{ubqc_correct_rate2}")
    '''
    ubqcRateList.append(ubqc_correct_rate2)

    
    #=========================================================================
    print(f"normRateList:{normRateList}")
    print(f"ubqcRateList:{ubqcRateList}")
    #'perfect',
    df = pd.DataFrame({ 
    'Hardware configuration': ['low noise', 'high noise'], 
    'nomal circuit': normRateList, 
    'UBQC circuit': ubqcRateList 
    }) # requires the same size in list


    df.plot(x= 'Hardware configuration' ,y=['nomal circuit','UBQC circuit'], kind="bar")  #"Noise case", "Loss case"

    plt.xticks(rotation='horizontal')
    plt.tight_layout()
    plt.subplots_adjust(left=0.1, right=0.9, top=0.9 ) #bottom=0.8

    plt.title('UBQC algorithm benchmarking on Circuit 5 ')
    plt.yticks(np.arange(0.0, 1.0, 0.1))
    plt.ylabel('successful rate')

    plt.savefig('plotTest16.png',bbox_inches='tight')
    plt.show()





