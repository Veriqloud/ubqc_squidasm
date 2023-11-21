from qiskit.circuit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit.compiler.assembler import assemble
from squidasm.run.stack.config import StackNetworkConfig
from squidasm.run.stack.run import run
from qiskit.qasm3 import dump

from squidasm.sim.stack.program import Program, ProgramContext, ProgramMeta
from netqasm.sdk.qubit import Qubit

# Circuit 5, Expected outcome: [1,1]
q5 = QuantumRegister(2)
c5 = ClassicalRegister(2)
qc5 = QuantumCircuit(q5, c5)
qc5.h(q5[0])
qc5.z(q5[1])
qc5.h(q5[1])
qc5.cx(q5[1],q5[0])


def text2squidasm(num_qubits,operators,connection):
    print("text2squidasm")
    myqubitList = [] 
    for q in range(num_qubits):
        myqubitList.append(Qubit(connection))

    for line in operators:
        print(line)
        
        if line[0] == 'h':                    
            myqubitList[int(line[1])].H()     
            print(f"applyed h in qubit {line[1]}")
        elif line[0] == 'x':  
            print(f"applyed x in qubit {line[1]}")                  
            myqubitList[int(line[1])].X() 
        elif line[0] == 'z':  
            print(f"applyed z in qubit {line[1]}")                
            myqubitList[int(line[1])].Z() 
        else:
            pass
    
    # measure all qubits
    res = []
    for i in range(num_qubits):
        res.append(myqubitList[i].measure())
        
    
    #print(f"res:{res}")
    
    return res



def qasm2text(qcircuit):
    print("qasm2text")
    # make .qasm file for easier parsing
    iostream = open("qasm2squidamsTest.qasm", "w", encoding="utf-8")
    dump(qcircuit,iostream)
    iostream.close()

    # read from .qasm file and parse it
    myqasm = open("qasm2squidamsTest.qasm", "r", encoding="utf-8")  
    mytext = myqasm.readlines()
    text_size = len(mytext)
    print(mytext)

    # parse text:
    num_qubits = int(mytext[3][6]) #fix location of num_qubits 
    #print(num_qubits)

    operators = []
    for i in range(5,text_size):
        if mytext[i][0] == 'c':
            pass
        else:
            operators.append([mytext[i][0],mytext[i][5]]) #fix location of operators

    print(operators)

    return num_qubits, operators



class CircuitProgram(Program):
    PEER_NAME = "Alice"
    
    def __init__(self,maxQubits: int):
        self.maxQubits = maxQubits
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
        num_qubits,operators = qasm2text(qc5)
        self.res = text2squidasm(num_qubits,operators,myConnection)
        
        #yield from connection.flush()

        return {}


def display(qcircuit):
    print(qcircuit.draw())
    print(disassemble(qcircuit))




if __name__ == "__main__":

    cfg = StackNetworkConfig.from_file("config_perfect.yaml")

    maxQubits = 20
    myCircuitProgram = CircuitProgram(maxQubits)

    run(config=cfg,
        programs={ "Bob": myCircuitProgram},
        num_times=1)

    #print(f"Measurement result:{myCircuitProgram.res}")