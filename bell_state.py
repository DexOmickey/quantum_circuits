#!/usr/bin/env python
# coding: utf-8

# In[1]:


from qiskit import *


# In[2]:


qr = QuantumRegister(2)


# In[3]:


cr = ClassicalRegister(2)


# In[4]:


circuit =  QuantumCircuit(qr,cr)


# In[5]:


circuit.h(1)


# In[6]:


circuit.cx(1,0)


# In[7]:


circuit.measure([0,1],[0,1])


# In[8]:


simulator =  Aer.get_backend('qasm_simulator')


# In[9]:


result = execute(circuit, backend=simulator, shots=1000).result()


# In[10]:


print(circuit)


# In[11]:


count = result.get_counts(circuit)


# In[13]:


print("Measurement : "+ str(count))


# In[ ]:




