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


# Import file with circuits
#from circuits_qasm import qasm_circs
#from flow_qasm import circuit_file_to_flow, count_qubits_in_sequence

from squidasm.sim.stack.program import Program, ProgramContext, ProgramMeta

# Define qubit and outcome arrays:

def get_qubit(netqasm_qubit: SdkQubit, node_name) -> qapi.Qubit:
    """Get the the qubit(s), only possible in simulation and can be used for debugging.

    .. note:: The function gets the *current* qubit(s). So make sure the the subroutine is flushed
              before calling the method.

    Parameters
    ----------
    qubit : :class:`~netqasm.sdk.qubit.Qubit` or list
        The qubit to get the state of or list of qubits.

    Returns
    -------
    netsquid.Qubit
        The netsquid Qubit object
    """

    # Get the executor and qmemory from the backend
    network = squidasm.sim.stack.globals.GlobalSimData.get_network()
    app_id = netqasm_qubit._conn.app_id

    executor = network.stacks[node_name].qnos.app_memories[app_id]
    qmemory = network.stacks[node_name].qdevice

    # Get the physical position of the qubit
    virtual_address = netqasm_qubit.qubit_id
    phys_pos = executor.phys_id_for(virt_id=virtual_address)
    

    # Get the netsquid qubit
    ns_qubit = qmemory.mem_positions[phys_pos].get_qubit()

    return ns_qubit


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
            if np.round(m0) == 1:
                eprQubit.Z()
                
            if np.round(m1) == 1:
                eprQubit.X()

                
            # Append qubit to list
            qubits.append(eprQubit)
            
        yield from myConnection.flush()
        for i in range(nQubits):
            print(f"Qubit {i}'s state after receiving:")
            print(get_qubit(qubits[i],"Bob").qstate.qrepr.dm)

        # Now: Client sends nMeasurement
        nMeasurement = yield from myCsocket.recv()
        #print("Server received request: perform {} measurements!".format(nMeasurement))
        
        E = []
        
        # Server receives lists of qubits to entangle
        E1 = yield from myCsocket.recv()
        #print("Server received first list of qubits to entangle!")
        
        E2 = yield from myCsocket.recv()
        #print("Server received second list of qubits to entangle!")
        
        # Entangle qubits
        
        for i, j in zip(E1,E2):
            qubit_i = qubits[i-1]
            qubit_j = qubits[j-1]
            
            # Apply cz gate to induce entanglement
            qubit_i.cphase(qubit_j)
            
            # Store entangled tuples in E
            E.append([i,j])
            #print("Entangle qubit {} with qubit {}".format(i,j))
        #print("E = {}".format(E))
        
        #print("Server measuring...")
        
        # Create list of enumerations of qubits
        qout_idx = list(range(nQubits))
        
        # Now: Iterate over list of measurements
        for i in range(nMeasurement):
            
            # Receive which qubit to measure
            qubit_n = yield from myCsocket.recv() 
            
            # Receive measurement angle
            angle = yield from myCsocket.recv()

            qout_idx.remove(qubit_n-1)
            
            #print("Server measuring qubit {} using angle {}".format(qubit_n,angle))
            
            # Now: Apply rotations to be able to measure in given basis, include 7 due to rotation syntax in SquidASM
            qubits[qubit_n-1].rot_Z(-int(angle)%256,7)
            qubits[qubit_n-1].rot_Y(256-64,7) # to make the measurement along in the |+> |-> basis
            m = qubits[qubit_n-1].measure()
            yield from myConnection.flush()
            
            #print("Server sending result of measurement for qubit {}: {}".format(qubit_n,m))
            myCsocket.send(np.round(m))
        
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
            mes=[np.round(m0),np.round(m1)]
            myCsocket.send(mes)
            
        #print("All qubits sent back to the client!")
        
        return {}