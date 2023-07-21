from netqasm.sdk.external import NetQASMConnection, Socket
from netqasm.sdk.classical_communication.socket import Socket
from netqasm.sdk.connection import BaseNetQASMConnection
from netqasm.sdk.epr_socket import EPRSocket
from netqasm.sdk.qubit import Qubit
import numpy as np
from netqasm.sdk.qubit import Qubit as SdkQubit
from netsquid.qubits import qubitapi as qapi
import netsquid.qubits
import squidasm.sim.stack.globals
from squidasm.sim.stack.program import Program, ProgramContext, ProgramMeta
from UBQC_client import get_qubit

class BobProgram(Program):
    PEER_NAME = "Alice"

    @property
    def meta(self) -> ProgramMeta:
        return ProgramMeta(
            name="UBQC", 
            csockets=[self.PEER_NAME],
            epr_sockets=[self.PEER_NAME],
            max_qubits=20,
        )

    def run(self, context: ProgramContext):    
        qubits = []
        outcomes = []
        myConnection: BaseNetQASMConnection = context.connection
        myCsocket: Socket = context.csockets[self.PEER_NAME]
        myEprSocket: EPRSocket = context.epr_sockets[self.PEER_NAME]
        
        # First step: Receive nQubits classically
        nQubits = yield from myCsocket.recv()
        #print(f"Bob received info: Create {nQubits} qubits")
    
        # Now: Receive manipulated qubits using state teleportation:
        for i in range(nQubits):
            
            # Receive part of EPR pair
            eprQubit = myEprSocket.recv_keep()[0]
            yield from myConnection.flush()
            
                    # receive 2 bits message
            m0 = yield from myCsocket.recv()

            m1 = yield from myCsocket.recv()

            
            # Apply correction depending on outcome
            if int(m0) == 1:
                eprQubit.Z()
                
            if int(m1) == 1:
                eprQubit.X()

                
            # Append qubit to list
            qubits.append(eprQubit)
            
        # Now: Client sends nMeasurement
        nMeasurement = yield from myCsocket.recv()        
        E = []
        
        # Server receives lists of qubits to entangle
        E1 = yield from myCsocket.recv()        
        E2 = yield from myCsocket.recv()
        
        # Entangle qubits
        for i, j in zip(E1,E2):
            qubit_i = qubits[i-1]
            qubit_j = qubits[j-1]
            
            # Apply cz gate to induce entanglement
            qubit_i.cphase(qubit_j)
            
            # Store entangled tuples in E
            E.append([i,j])
        
        # Create list of enumerations of qubits
        qout_idx = list(range(nQubits))
        
        # Now: Iterate over list of measurements
        for i in range(nMeasurement):
            
            # Receive which qubit to measure
            qubit_n = yield from myCsocket.recv() 
            
            # Receive measurement angle
            angle = yield from myCsocket.recv()

            qout_idx.remove(qubit_n-1)
            
            # Now: Apply rotations to be able to measure in given basis, include 7 due to rotation syntax in SquidASM
            qubits[qubit_n-1].rot_Z(-int(angle)%256,7)
            qubits[qubit_n-1].rot_Y(256-64,7) # to make the measurement along in the |+> |-> basis
            m = qubits[qubit_n-1].measure()
            yield from myConnection.flush()
            
            myCsocket.send(int(m))
        
        # Now: Send back unmeasured output qubits
        for i in range(nQubits - nMeasurement):
            
            # Create EPR pair
            eprQubit = myEprSocket.create_keep()[0]
            
            # Entangle i-th output qubit with eprQubit, measure both
            qubits[qout_idx[i]].cnot(eprQubit)
            qubits[qout_idx[i]].H()
            m0 = qubits[qout_idx[i]].measure()
            m1 = eprQubit.measure()
            yield from myConnection.flush()
            
            # Send measurement result back to Alice to perform corrections
            mes=[int(m0),int(m1)]
            myCsocket.send(mes)
        
        return {}
