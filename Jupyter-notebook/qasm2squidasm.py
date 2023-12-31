'''
The purpose of this script is to have a SquidASM quantum program object that execute 
quantum circuit converted from QASM. 
The main function runs an example and generates a .qasm file.
'''

from qiskit.circuit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit.compiler.assembler import assemble
from squidasm.run.stack.config import StackNetworkConfig
from squidasm.run.stack.run import run
from qiskit.qasm3 import dump

from squidasm.sim.stack.program import Program, ProgramContext, ProgramMeta
from netqasm.sdk.qubit import Qubit

#from circuits_qasm import qasm_circs

import re

from qasmFiles.qCircuit import qasm_circs



def text2squidasm(myqubitList,operators):

    for q in myqubitList:
        q.H()  # fix the initial difference of ubits

    for line in operators:
        #print(f"processing...{line}")
        if line[0] == 'h':                   
            myqubitList[int(line[1])].H()     
            
        elif line[0] == 'x':        
            myqubitList[int(line[1])].X() 

        elif line[0] == 'y':      
            myqubitList[int(line[1])].Y() 

        elif line[0] == 'z':                  
            myqubitList[int(line[1])].Z()

        elif line[0] == 'cx' :   # control case
            #print(f"applyed cnot in qubit {line[1],line[2]}") 
            myqubitList[int(line[1])].cnot(myqubitList[int(line[2])])

        elif line[0] == 'rx': # rotation case
            #print(f"applyed rotation x in qubit {line[2]}") 
            myqubitList[int(line[2])].rot_X(int(line[1]),7) #convert customized unit to SquidASM parameters 

        elif line[0] == 'ry':  
            myqubitList[int(line[2])].rot_Y(int(line[1]),7) 

        elif line[0] == 'rz': 
            myqubitList[int(line[2])].rot_Z(int(line[1]),7) 

        else:
            pass

    # measure all qubits
    res = []
    for q in myqubitList:
        res.append(q.measure())
    
    return res

def qcobj2qasm(qcobj,path):
    # make .qasm file for easier parsing
    iostream = open(path, "w", encoding="utf-8")
    dump(qcobj,iostream)
    iostream.close()

def qasmParse(path):
    
    # read from .qasm file and parse it
    myqasm = open(path, "r", encoding="utf-8")  
    mytext = myqasm.readlines()
    text_size = len(mytext)
    #print(f"mytext: {mytext}")

    # parse text:
    num_qubits = int(re.findall('\d+', mytext[3])[0]) #find integers then take the first one  

    operators = []
    for i in range(5,text_size):
        if mytext[i][0] == 'c':    # control case
            operators.append([mytext[i][:2]
                ,re.findall('\d+', mytext[i])[-3]
                ,re.findall('\d+', mytext[i])[-1]])
        if mytext[i][0] == 'r':    # rotation case
            operators.append([mytext[i][:2]
                ,float(re.findall("\d+\.\d+", mytext[i])[0])
                ,re.findall('\d+', mytext[i])[-1]])
        else: # H,X,Y,Z cases
            operators.append([mytext[i][0],re.findall('\d+', mytext[i])[-1]]) 
            # record the operation and find the qubit index

    #print(operators)

    return num_qubits, operators



class CircuitProgram(Program):
    PEER_NAME = "Alice"
    
    def __init__(self,maxQubits: int, path:str):
        self.maxQubits = maxQubits
        self.path = path
        self.res = []

    @property
    def meta(self) -> ProgramMeta:
        return ProgramMeta(
            name="tempCirsuit",
            csockets=[self.PEER_NAME],
            epr_sockets=[self.PEER_NAME],
            max_qubits=self.maxQubits,
        )

    def run(self, context: ProgramContext):

        myConnection = context.connection

        
        num_qubits, self.operators = qasmParse(self.path)

        # initialize qubits
        myqubitList = [] 
        for q in range(num_qubits):
            myqubitList.append(Qubit(myConnection))


        self.res = text2squidasm(myqubitList,self.operators)

        
        
        # send results to the processor
        yield from myConnection.flush()
        self.res=[int(i) for i in self.res]
        

        return {}


if __name__ == "__main__":


    # generate qasm file
    for i in range(16):
        mypath = "qasmFiles/c"+str(i)+".qasm"
        qcobj2qasm(qasm_circs()[i],mypath) #list [0,15]


    # run sim
    '''
    # parsing qasm file
    num_qubits,operators = qasmParse(mypath)

    
    cfg = StackNetworkConfig.from_file("config_perfect.yaml")

    maxQubits = 50
    myCircuitProgram = CircuitProgram(maxQubits,mypath) # import from qasm code
    num_times = 1
    resList = []

    for _ in range(num_times):
        # We execute the circuit only at Bob's side since he is usually the server side. 
        run(config=cfg,
            programs={ "Bob": myCircuitProgram},
            num_times=1)
        resList.append(myCircuitProgram.res)
    
    print(f"Measurement result:{resList}")
    '''