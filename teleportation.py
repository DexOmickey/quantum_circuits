#!/usr/bin/env python

# circuit 2


from qiskit import *
qr=QuantumRegister(3)
cr=ClassicalRegister(3)
circuit=QuantumCircuit(qr,cr)
circuit.h(1)
circuit.cx(1,2)
circuit.cx(0,1)
circuit.h(0)
circuit.measure([0,1],[0,1])
simulator = Aer.get_backend('qasm_simulator')
result = execute(circuit, backend=simulator, shots=100).result()
counts = result.get_counts(circuit)
circuit.draw(output='mpl')
print("Measurement is:", counts)




