from qiskit.circuit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit.compiler.assembler import assemble
from squidasm.run.stack.config import StackNetworkConfig
from squidasm.run.stack.run import run
from qiskit.qasm3 import dump

from squidasm.sim.stack.program import Program, ProgramContext, ProgramMeta
from netqasm.sdk.qubit import Qubit

import re




def text2squidasm(myqubitList,operators):
    #print("text2squidasm")
    for q in myqubitList:
        q.H()  

    for line in operators:
        #print(f"processing...{line}")
        if line[0] == 'h':  
            #print(f"applyed h in qubit {line[1]}")                  
            myqubitList[int(line[1])].H()     
            
        elif line[0] == 'x':  
            #print(f"applyed x in qubit {line[1]}")      
            myqubitList[int(line[1])].X() 

        elif line[0] == 'y':  
            #print(f"applyed x in qubit {line[1]}")      
            myqubitList[int(line[1])].Y() 

        elif line[0] == 'z':  
            #print(f"applyed z in qubit {line[1]}")                
            myqubitList[int(line[1])].Z()

        elif line[0] == 'cx' :   # control case
            #print(f"applyed cnot in qubit {line[1],line[2]}") 
            myqubitList[int(line[1])].cnot(myqubitList[int(line[2])])

        elif line[0] == 'rx': # rotation case
            #print(f"applyed rotation x in qubit {line[2]}") 
            myqubitList[int(line[2])].rot_X(int(line[1]),7) #convert customized unit to SquidASM parameters 

        elif line[0] == 'ry': # rotation case
            #print(f"applyed rotation y in qubit {line[2]}") 
            myqubitList[int(line[2])].rot_Y(int(line[1]),7) 

        elif line[0] == 'rz': # rotation case
            #print(f"applyed rotation z in qubit {line[2]}") 
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
    num_qubits = int(re.findall('\d+', mytext[3])[0]) #fix location of num_qubits 
    #print(num_qubits)

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
        else:
            operators.append([mytext[i][0],re.findall('\d+', mytext[i])[-1]]) #fix location of operators

    #print(operators)

    return num_qubits, operators



class CircuitProgram(Program):
    PEER_NAME = "Alice"
    
    def __init__(self,maxQubits: int, num_qubits: int, operators):
        self.maxQubits = maxQubits
        self.num_qubits = num_qubits
        self.operators = operators
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

        


        # initialize qubits
        myqubitList = [] 
        for q in range(self.num_qubits):
            myqubitList.append(Qubit(myConnection))
        #print(f"length of qbuit:{len(myqubitList)}")

        self.res = text2squidasm(myqubitList,self.operators)
        
        yield from myConnection.flush()
        self.res=[int(i) for i in self.res]
        #print(f"Measurement result:{self.res}")
        

        return {}


if __name__ == "__main__":

    # Circuit 5, Expected outcome: [1,1]
    q5 = QuantumRegister(2)
    c5 = ClassicalRegister(2)
    qc5 = QuantumCircuit(q5, c5)
    qc5.h(q5[0])
    qc5.z(q5[1])
    qc5.h(q5[1])
    qc5.cx(q5[1],q5[0])

    # Circuit 14, Expected outcome: [1,1,1,1,0]
    q14 = QuantumRegister(5)
    c14 = ClassicalRegister(5)
    qc14 = QuantumCircuit(q14, c14)
    qc14.z(q14[0])
    qc14.z(q14[1])
    qc14.h(q14[0])
    qc14.h(q14[1])
    qc14.h(q14[2])
    qc14.h(q14[3])
    qc14.h(q14[4])
    qc14.rx(128,q14[2])
    qc14.cx(q14[1],q14[3])

    # Circuit 16 Expected outcome: [1,1,1,1,1,1,1,1,1,1]
    q16 = QuantumRegister(10)
    c16 = ClassicalRegister(10)
    qc16 = QuantumCircuit(q16,c16)
    qc16.h(q16[0])
    qc16.x(q16[0])
    qc16.h(q16[1])
    qc16.x(q16[1])
    qc16.h(q16[2])
    qc16.cx(q16[1],q16[2])
    qc16.h(q16[3])
    qc16.cx(q16[2],q16[3])
    qc16.h(q16[4])
    qc16.cx(q16[3],q16[4])
    qc16.h(q16[5])
    qc16.cx(q16[4],q16[5])
    qc16.h(q16[6])
    qc16.cx(q16[0],q16[6])
    qc16.h(q16[7])
    qc16.cx(q16[0],q16[7])
    qc16.h(q16[8])
    qc16.cx(q16[0],q16[8])
    qc16.h(q16[9])
    qc16.cx(q16[0],q16[9])

    # generate qasm file
    qcobj2qasm(qc14,"tempCircuit.qasm")

    # parsing qasm file
    num_qubits,operators = qasmParse("tempCircuit.qasm")

    cfg = StackNetworkConfig.from_file("config_perfect.yaml")

    maxQubits = 20
    myCircuitProgram = CircuitProgram(maxQubits,num_qubits,operators) # import from qasm code
    num_times = 1
    resList = []

    for _ in range(num_times):
        run(config=cfg,
            programs={ "Bob": myCircuitProgram},
            num_times=1)
        resList.append(myCircuitProgram.res)

    print(f"Measurement result:{resList}")