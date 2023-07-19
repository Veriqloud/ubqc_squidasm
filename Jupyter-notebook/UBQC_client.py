from netqasm.sdk.classical_communication.socket import Socket
from netqasm.sdk.connection import BaseNetQASMConnection
from netqasm.sdk.epr_socket import EPRSocket
from netqasm.sdk.qubit import Qubit
from qiskit import QuantumRegister,QuantumCircuit, ClassicalRegister
from qiskit.compiler.assembler import assemble
import random
import subprocess
import numpy as np
import argparse
from argparse import RawTextHelpFormatter
from netqasm.sdk.qubit import Qubit as SdkQubit
from netsquid.qubits import qubitapi as qapi
import netsquid.qubits
import squidasm.sim.stack.globals
from circuits_qasm import qasm_circs
from flow_qasm import circuit_file_to_flow, count_qubits_in_sequence
from angle import measure_angle2
from squidasm.sim.stack.program import Program, ProgramContext, ProgramMeta

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



# Define gates the client wants to apply
def apply_singleU(U,q,count):
    if U.lower()=='x':
        q.X()
    elif U.lower()=='y':
        q.Y()
    elif U.lower()=='z':
        q.Z()
    elif U.lower()=='h':
        q.H()
    elif U.lower()=='k':
        q.K()
    elif U.lower()=='t':
        q.T()
    elif U.lower()=='rot_x':
        angle = input(f"Rotation angle for qubit {}?")
        q.rot_X(int(angle),7)
    elif U.lower()=='rot_y':
        angle = input(f"Rotation angle for qubit {}?")
        q.rot_Y(int(angle),7)
    elif U.lower()=='rot_z':
        angle = input(f"Rotation angle for qubit {}?")
        q.rot_Z(int(angle),7)
    elif U.lower()=='i':
	return q
    else:
        print("Gate {} not valid!".format(U))
    return q

# Store in- and output gates in corresponding arrays

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
            max_qubits=20,
        )
    
    def __init__(self, arguments):
        self.args = arguments

    def run(self, context: ProgramContext):

        # First step: Initialize connection and sockets
        myConnection = context.connection
        myCsocket = context.csockets[self.PEER_NAME]
        myEprSocket = context.epr_sockets[self.PEER_NAME]
        measurements = []
        
        # Initialize qubit and angles list
        
        qubits = []
        angles = []
        
        # Define circuits
        circuits = qasm_circs()
        
        if not self.args["custom_circ"]:
            circ = circuits[int(self.args["circuit"]-1)]
            circ_flow = circuit_file_to_flow(circ[0])
            seq = circ_flow[0]
            result = circ[1]
            qout_idx = circ_flow[1]
            
        if self.args["custom_circ"]:
            qiskit_circ = self.args["custom_circ"]
            circ = assemble(qiskit_circ,shots=2000,memory=True)
            circ_flow = circuit_file_to_flow(circ)
            seq = circ_flow[0]
            result = 0
            qout_idx = circ_flow[1]
        

            
        if self.args["input"]:
            print("Client chose input gates: {}".format(self.args["input"]))

        if self.args["output"]:
            print("Client chose output gates: {}".format(self.args["output"]))


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
	gatecounter = 1
        
        # For all input angles: create a random angle and save it into our angles array
        for i in range(0, nInputs):
            
            # Append random initial angle onto list
            rand_angle = int(256 * random.random())
            angles.append(rand_angle)

            # Let the user know the random angles
            if(self.args["log"]):
            	print("i = {} rand_ang = {}".format(i,angles[i]))
            
            # Create qubits with these lists
            q = Qubit(myConnection)
            q.rot_Y(1,1)  # |+> state
            yield from myConnection.flush()            

            # If gates should be applied before the input
            if self.args["input"]:
                U = input_gates[i]
                q = apply_singleU(U,q,gatecounter)
		gatecounter += 1
            
            # Rotation in format (n*pi/2^d; here: n = rand_angle, d = 7)
            q.rot_Z(rand_angle,7)
            qubits.append(q)
            
            
        # Now: Do the same with auxillary qubits, without applying unitary transformations beforehand (commented out)
        
        for i in range(nInputs, nQubits):
            rand_angle = int(256 * random.random())
            angles.append(rand_angle)
            if(self.args["log"]):
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

        myCsocket.send(np.array(E1))
        myCsocket.send(np.array(E2))

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
                angle_to_send = float((measure_angle2(s, outcome, input_angle) + r * 128)) % 256 #PI = 128
                #print("s.angle = {} outcome = {} input_angle = {} meas_ang2 = {} r = {} to_send = {}".format(s.angle,outcome,input_angle,measure_angle2(s, outcome, input_angle),r,angle_to_send))

                # Now: Send information to the server telling which qubit to measure
                myCsocket.send(qubit_n)

                # Send information of the measurement angle to the server
                if(self.args["log"]):
                		print("Client Sending (classical): measurement angle {}".format(angle_to_send))
                myCsocket.send(int(angle_to_send))

                # Client receives classical result of the last measurement, either 0 or 1
                m = yield from myCsocket.recv()
		
                if(self.args["log"]):
                		print("Client Received: result {}".format(m))

                # We adjust for the randomness only we know we added
                if r == 1:
                    outcome[qubit_n - 1] = int(1 - m)

                else:
                    outcome[qubit_n - 1] = int(m)
        
        # Now: All the entanglements and measurements are performed. The server sends back the output qubits.
        if(self.args["log"]):
        		print("Client Receiving output qubits")
        		print("qout_idx = {}".format(qout_idx))
        qout = [-1]*len(qout_idx)
        qidx_sort = qout_idx[:]
        qidx_sort.sort()
        noutput = len(qout_idx)
        if(self.args["log"]):
        		print("qout_idx = {}, outcome = {}, qidx_sort = {}".format(qout_idx, [int(r) for r in outcome], qidx_sort))
        
        # Subroutine of quantum teleportation has to be implemented on the clients side to receive qubits:

        for i in range(noutput):         
            # receiving part of EPR 
            output_qubit = myEprSocket.recv_keep()[0]
            yield from myConnection.flush()

            # receive 2 bits message
            m0 = yield from myCsocket.recv()
            m1 = yield from myCsocket.recv()
            yield from myConnection.flush()

            # Apply correction depending on outcome
            if int(m0) == 1:
                output_qubit.Z()
            if int(m1) == 1:
                output_qubit.X()
                
            # Store qubits send back by server in qout
            if(self.args["log"]):
            	print("Client Received: recv qubit {} sorting to {}".format(qout_idx[i],qidx_sort.index(qout_idx[i])))
            qout[qidx_sort.index(qidx_sort[i])]=output_qubit
            
        # Here: Applying corrections on the output qubits according to the initial angles, taking care of the induced randomness

        for i in range(noutput):
            qout[qidx_sort.index(qout_idx[i])].rot_Z(-int(angles[qidx_sort[i]-1])%256,7)
            
        # Now: Apply byproduct corrections:
        if(self.args["log"]):
         	print("State before corrections:")
         	for i in range(noutput):
        	 		print(get_qubit(qout[i],"Alice").qstate.qrepr.dm)
         	for s in seq:
            		s.printinfo()
        for s in seq:
            for i in range(noutput):  
                if s.type == "Z" and s.qubit == qidx_sort[i] and (outcome[s.power_idx-1] == 1 or s.power_idx == 0): 
                    qout[i].Z()
                    if(self.args["log"]):
                    	print("Byproduct: Z : s = {} condition = {}  qout_idx = {}, qidx_sort.idx = {}".format(outcome[s.power_idx-1],s.power_idx,qout_idx[i],qidx_sort.index(qout_idx[i])))   
                if s.type == "X" and s.qubit == qidx_sort[i] and (outcome[s.power_idx-1] == 1 or s.power_idx == 0): 
                    qout[i].X()
                    if(self.args["log"]):
                    	print("Byproduct: X s = {} condition = {} qout_idx = {}, qidx_sort.idx = {}".format(outcome[s.power_idx-1],s.power_idx,qout_idx[i],qidx_sort.index(qout_idx[i])))

        if(self.args["log"]):
        		print("State after corrections:")
        		for i in range(noutput):
        			print(get_qubit(qout[i],"Alice").qstate.qrepr.dm)		


        # Initialize array with measurement results, apply measurements (again neglecting possible single qubit corrections)

        meas = []
	gatecounter = 1
        if(self.args["output"]):
            output_gates = self.args["output"]
            for i in range(noutput):
                U = output_gates[i]
                if(self.args["log"]):
                 	print("apply {} to qubit {} sorting to {}".format(U,qout_idx[i],i))
                apply_singleU(U,qout[i],gatecounter)
		gatecounter += 1
        for i in range(noutput):
            meas.append(qout[qidx_sort.index(qout_idx[i])].measure())
        yield from myConnection.flush()
        meas = [int(r) for r in meas]
        
        print("Measurement in Z-Basis: {}".format(meas))
        return [meas,result]
