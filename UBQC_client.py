from netqasm.sdk.classical_communication.socket import Socket
from netqasm.sdk.connection import BaseNetQASMConnection
from netqasm.sdk.epr_socket import EPRSocket
from netqasm.sdk.qubit import Qubit
from qiskit import QuantumRegister,QuantumCircuit, ClassicalRegister
from qiskit.compiler.assembler import assemble
import random
#import subprocess
import numpy as np
import argparse
from argparse import RawTextHelpFormatter
from netqasm.sdk.qubit import Qubit as SdkQubit
from netsquid.qubits import qubitapi as qapi
#import netsquid.qubits
import squidasm.sim.stack.globals
from circuits_qasm import qasm_circs
from flow_qasm import circuit_file_to_flow, count_qubits_in_sequence
from angle import measure_angle
from squidasm.sim.stack.program import Program, ProgramContext, ProgramMeta
from qiskit.qasm3 import load
from enum import Enum

class LoadType(Enum):
    DEFAULT = 0
    FILE = 1
    #CUSTOM = 2

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

# Load parser to get arguments from the client
parser=argparse.ArgumentParser(
    description='Choose a circuit',
    formatter_class=RawTextHelpFormatter)

# If the client wants to draw the circuit
parser.add_argument('-d','--draw', action="store_true", help='draw the circuit')

# Include logging
parser.add_argument('-l','--log', action="store_true", help='enable or disable the logging')

# Choose circuit
parser.add_argument('-c','--circuit', type=int, help='choose a particular circuit in circuits')

# Choose gates to be applied before protocol
parser.add_argument('-i','--input', type=str, help='choose gates to apply on input states, default |+>. can be Pauli, rot_Pauli(angle),H,K,T.', default="")

# Choose gates to be applied after protocol
parser.add_argument('-o','--output', type=str, help='choose gates to apply before measurement, default is Z. can be Pauli, rot_Pauli(angle),H,K,T.', default="")

# Choose the means of source
parser.add_argument('-s','--source', type=int
                    ,help='choose a way to input quantum cirsuit: 0: Use default circuits. 1:Use customized circuit. 2: Import from a .qasm file.', default = 0)

# Put .qasm file path to load from if choosing import from source from a file in -s
parser.add_argument('-p','--path', type=str, help='.qasm file path to load from if choosing import from source from a file in -s', default="")


# Save arguments in args
args=parser.parse_args()

# Define circuits
circuits = qasm_circs()

# Which circuit?


# If no circuit is chosen, take a simple Hadamard gate (Circuit 1)
if not args.circuit:
    circ = circuits[0]
    result = circ[1]
    circ_flow = circuit_file_to_flow(circ[0])
    seq = circ_flow[0]
    qout_idx = circ_flow[1]
    args.circuit = 0

# Otherwise, take the circuit the client chose
else:
    circ = circuits[int(args.circuit)]
    circ_flow = circuit_file_to_flow(circ[0])
    seq = circ_flow[0]
    result = circ[1]
    qout_idx = circ_flow[1]
    #print("Client chose circuit {}!".format(int(args.circuit)+1))

if(args.log and result):
    print(f"expected result :{result}")

if args.source :
    print("Loading circuit from path:{}".format)
else :
    print(f"Client chose default circuit {args.circuit}") #.format(int(args.circuit)+1)


# If the client wants to draw the circuit
if(args.draw):
    print(circ[2])

# Define gates the client wants to apply
def apply_singleU(U,q,angle=None):
    if U.lower()=='x':
        q.X()
    elif U.lower()=='y':
        q.Y()
    elif U.lower()=='z':
        q.Z()
    elif U.lower()=='h':
        q.H()
    elif U[:5].lower()=='rot_x':
        q.rot_X(int(angle),7)
    elif U[:5].lower()=='rot_y':
        q.rot_Y(int(angle),7)
    elif U[:5].lower()=='rot_z':
        q.rot_Z(int(angle),7)
    elif U.lower()=='i':
        return q
    else:
        print("Gate {} not valid!".format(U))
    return q

# Store in- and output gates in corresponding arrays

if args.input:
    input_gates = args.input.split(',')
    print(f"Client chose input gates {input_gates}!")

if args.output:
    output_gates = args.output.split(',')
    print(f"Client chose output gates {output_gates}!")

# Count how many qubits are needed
#if not args.source:
nQubits = count_qubits_in_sequence(seq)

nMeasurement = 0
E1 = []
E2 = []

# Construct lists for entanglement
for s in seq:
    if s.type == "E":
        E1.append(s.qubits[0])
        E2.append(s.qubits[1])
    if s.type == "M":
        nMeasurement += 1
nInputs = nQubits - nMeasurement

# Initialize list to store measurement results, needed for corrections
outcome = nQubits * [-1]

class AliceProgram(Program):
    PEER_NAME = "Bob"
    
    '''
    def __init__(self, targetQubit: int):
        self.targetQubit = targetQubit
    '''

    @property
    def meta(self) -> ProgramMeta:
        return ProgramMeta(
            name="UBQC",
            csockets=[self.PEER_NAME],
            epr_sockets=[self.PEER_NAME],
            max_qubits=self.max_qubits,
        )
    
    def __init__(self, max_qubits):
        self.max_qubits = max_qubits

    def run(self, context: ProgramContext):

        # First step: Initialize connection and sockets
        myConnection = context.connection
        myCsocket = context.csockets[self.PEER_NAME]
        myEprSocket = context.epr_sockets[self.PEER_NAME]
        
        # Initialize qubit and angles list
        
        qubits = []
        angles = []
        
        # Define circuits
        circuits = qasm_circs()
        if(args.log):
            print(f"source index:{args.source}") 

        if  LoadType(args.source) == LoadType.FILE:  #load from file
            if(args.log):
                print("client load from a file")
            if not args.path :
                print("Error! Please specify a file path with command -p ")
                return 
            else:
                circ_obj = load(args.path)
                circ = assemble(circ_obj,shots=2000,memory=True)
                circ_flow = circuit_file_to_flow(circ)
                seq = circ_flow[0]
                result = 0
                qout_idx = circ_flow[1]
            

        else : #args.source == LoadType.DEFAULT #load default circit
            
            if not args.circuit:
                args.circuit = 1
            if(args.log):
                print(f"use default circuit:{int(args.circuit)-1}")

            circ = circuits[int(args.circuit)-1]
            
            circ_flow = circuit_file_to_flow(circ[0])
            seq = circ_flow[0]
            result = circ[1]
            qout_idx = circ_flow[1]

        # Count how many qubits are needed
        nQubits = count_qubits_in_sequence(seq)

        nMeasurement = 0
        E1 = []
        E2 = []

        # Construct lists for entanglement
        for s in seq:
            if s.type == "E":
                E1.append(s.qubits[0])
                E2.append(s.qubits[1])
            if s.type == "M":
                nMeasurement += 1
        nInputs = nQubits - nMeasurement

        # Initialize list to store measurement results, needed for corrections
        outcome = nQubits * [-1]
        
        # For all input angles: create a random angle and save it into our angles array
        for i in range(0, nInputs):
            
            # Append random initial angle onto list
            rand_angle = int(256 * random.random())
            angles.append(rand_angle)

            # Let the user know the random angles
            if(args.log):
            	print("i = {} rand_ang = {}".format(i,angles[i]))

            # Create qubits with these lists
            q = Qubit(myConnection)
            q.rot_Y(1,1)  # |+> state
            yield from myConnection.flush()            

            # If gates should be applied before the input
            if args.input:
                U = input_gates[i]
                angle = 0
                if(U[:3] == 'rot'):
                    angle = U[6:-1]
                q = apply_singleU(U,q,angle)

            
            # Rotation in format (n*pi/2^d; here: n = rand_angle, d = 7)
            q.rot_Z(rand_angle,7)
            qubits.append(q)
            
            
        # Now: Do the same with auxillary qubits, without applying unitary transformations beforehand (commented out)
        
        for i in range(nInputs, nQubits):
            rand_angle = int(256 * random.random())
            angles.append(rand_angle)
            if(args.log):
                print("i = {} rand_ang = {}".format(i,angles[i]))
            q = Qubit(myConnection)
            q.rot_Y(1,1)  # |+> state
            q.rot_Z(rand_angle,7)
            qubits.append(q)

        yield from myConnection.flush()
            
        # Now: List of qubits is initialized. Next step: Sending them to the server
        myCsocket.send(nQubits)
        
        # Send the qubits by making use of the quantum teleportation protocol
        
        for i in range(0,nQubits):
            # For each qubit: Initialize an EPR qubit to send the information to server
            eprqubit = myEprSocket.create_keep()[0]
            
            # Here: Not sure if to apply H or not! -> Check!
            qubits[i].cnot(eprqubit)
            qubits[i].H()
            
            # Send measurement result to server for corrections
            m0 = qubits[i].measure()
            m1 = eprqubit.measure()
            yield from myConnection.flush()
            
            mes=[int(m0),int(m1)]
            myCsocket.send(mes)
            
        # Now: Client sends the number of measurements that are to perform. This information comes from the flow file
        myCsocket.send(nMeasurement)
        
        # Then: Send lists E1 and E2 of which qubits to entangle

        myCsocket.send([np.array(E1),np.array(E2)])

        qout_idx2 = list(range(nQubits))
        
        # Now: Iterate over the sequence to perform the measurements
        for s in seq:

            # If the server is meant to do a measurement:

            if s.type == "M":

                # Which qubit are we measuring?
                qubit_n = s.qubit
                qout_idx2.remove(qubit_n-1)

                # What is the angle we wish to measure (according to circuit implementation)
                computation_angle = s.angle

                # What is the angle we randomized our qubit with?
                input_angle = angles[qubit_n-1]

                # What is our random variable r?
                r = np.round(random.random())

                # Calculate the angle to send with randomisation applied
                angle_to_send = float((measure_angle(s, outcome, input_angle) + r * 128)) % 256 #PI = 128
                #print("s.angle = {} outcome = {} input_angle = {} meas_ang2 = {} r = {} to_send = {}".format(s.angle,outcome,input_angle,measure_angle2(s, outcome, input_angle),r,angle_to_send))

                # Now: Send information to the server telling which qubit to measure
                myCsocket.send(qubit_n)

                # Send information of the measurement angle to the server
                if(args.log):
                		print("Client Sending (classical): measurement angle {}".format(angle_to_send))
                myCsocket.send(int(angle_to_send))

                # Client receives classical result of the last measurement, either 0 or 1
                m = yield from myCsocket.recv()

                # We adjust for the randomness only we know we added
                if r == 1:
                    outcome[qubit_n - 1] = int(1 - m)

                else:
                    outcome[qubit_n - 1] = int(m)
        
        # Now: All the entanglements and measurements are performed. The server sends back the output qubits.
        qout = [-1]*len(qout_idx)
        qidx_sort = qout_idx[:]
        qidx_sort.sort()
        noutput = len(qout_idx)
        
        # Subroutine of quantum teleportation has to be implemented on the clients side to receive qubits:

        for i in range(noutput):         
            # receiving part of EPR 
            output_qubit = myEprSocket.recv_keep()[0]
            yield from myConnection.flush()

            # receive 2 bits message
            loc_mes = yield from myCsocket.recv()
            yield from myConnection.flush()

            # Apply correction depending on outcome
            if int(loc_mes[0]) == 1:
                output_qubit.Z()
            if int(loc_mes[1]) == 1:
                output_qubit.X()
                
            # Store qubits send back by server in qout
            qout[qidx_sort.index(qidx_sort[i])]=output_qubit
            
        # Here: Applying corrections on the output qubits according to the initial angles, taking care of the induced randomness

        for i in range(noutput):
            qout[qidx_sort.index(qout_idx[i])].rot_Z(-int(angles[qidx_sort[i]-1])%256,7)

        for s in seq:
            for i in range(noutput):  
                if s.type == "Z" and s.qubit == qidx_sort[i] and (outcome[s.power_idx-1] == 1 or s.power_idx == 0): 
                    qout[i].Z()
                    if(args.log):
                    	print("Byproduct: Z : s = {} condition = {}  qout_idx = {}, qidx_sort.idx = {}".format(outcome[s.power_idx-1],s.power_idx,qout_idx[i],qidx_sort.index(qout_idx[i])))   
                if s.type == "X" and s.qubit == qidx_sort[i] and (outcome[s.power_idx-1] == 1 or s.power_idx == 0): 
                    qout[i].X()
                    if(args.log):
                    	print("Byproduct: X s = {} condition = {} qout_idx = {}, qidx_sort.idx = {}".format(outcome[s.power_idx-1],s.power_idx,qout_idx[i],qidx_sort.index(qout_idx[i])))	


        # Initialize array with measurement results, apply measurements (again neglecting possible single qubit corrections)

        meas = []
        if(args.output):
            for i in range(noutput):
                U = output_gates[i]
                if(U[:3] == 'rot'):
                    angle = U[6:-1]
                if(args.log):
                     print("apply {} to qubit {} sorting to {}".format(U,qout_idx[i],i))
                apply_singleU(U,qout[i],angle)
        for i in range(noutput):
            meas.append(qout[qidx_sort.index(qout_idx[i])].measure())
        yield from myConnection.flush()
        meas = [int(r) for r in meas]
        if(args.log):
            print("Measurement in Z-Basis: {}".format(meas))
        return [meas,result]
