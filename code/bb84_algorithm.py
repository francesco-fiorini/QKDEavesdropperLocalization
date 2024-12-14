#!/usr/bin/env python3

# Author: Francesco Fiorini
# francesco.fiorini@phd.unipi.it

from qiskit import QuantumCircuit
from crypto.bb84.sender import Sender
from crypto.bb84.receiver import Receiver
import binascii
import pandas as pd
import time
import sympy as sp
import numpy as np

BB84_SIMULATOR = 'BB84 SIMULATOR'
DATA = {
  'Algorithm': ['BB84'],
  'Backend': ['-'],
  'String': ['-'],
  'Interception Density': ['-'],
  'Alice Values': [],
  'Alice Axes': [],
  'Eve Values': [],
  'Eve Axes': [],
  'Bob Values': [],
  'Bob Axes': [],
  'Alice Key': [],
  'Bob Key': [],
  'Shared Key': [],
  'Alice OTP': [],
  'Bob OTP': [],
  'Result': [],
  'Encryption iteration times (ms)': [],
  'Encryption time (ms)': [],
  'Interception iteration times (ms)': [],
  'Interception time (ms)': [],
  'Decryption iteration times (ms)': [],
  'Decryption time (ms)': [],
  'Private key generation time (ms)': [],
  'Key checking time (ms)': [],
  'Shared key demonstration time (ms)': [],
  'Total time (ms)': ['-'],
  'Shared differences': ['-'],
  'Shared key length': ['-'],
  'Shared BER': ['-'],
  'Full key differences': ['-'],
  'Full key length': ['-'],
  'Full key BER': ['-'],
  'Estimated EVE position 1': ['-'],
  'Estimated EVE position 2': ['-'],
  'Dark count probability': ['-'],
  'Detector error rate': ['-'],
  'Detector efficiency': ['-'],
  'Fiber attenuation (dB/km)': ['-'],
  'Distance between Alice and Bob (km)': ['-'],
  'True Eve position from Alice (km)': ['-']
}

## An implementation of the BB84 protocol
## @see https://qiskit.org/textbook/ch-algorithms/quantum-key-distribution.html
class BB84Algorithm:
  ## Generate a key for Alice and Bob
  def __generate_key(self, backend, original_bits_size, verbose,echAB,echAE,echEB,Y0, e, eta, c, alpha):
    key_gen_time = time.time()
    # Encoder Alice
    alice = Sender('Alice', original_bits_size)
    alice.set_values()
    alice.set_axes()
    start_time = time.time()
    message, iteration_times = alice.encode_quantum_message()
    time_ms = (time.time() - start_time) * 1000
    # print('  Quantum encryption run in', str(time_ms), 'ms')
    DATA["Encryption iteration times (ms)"] = str(iteration_times)
    DATA["Encryption time (ms)"] = str(time_ms)

    # Interceptor Eve
    
    bob_axes = [] # Bob share his axes
    eve = Receiver('Eve', original_bits_size)
    eve.set_axes()
    start_time = time.time()
    message, iteration_times,checkIntercept = eve.decode_quantum_messageEve(message, self.measure_density, backend,echAE,original_bits_size)
    
    time_ms = (time.time() - start_time) * 1000
    # print('  Quantum interception run in', str(time_ms), 'ms')
    DATA["Interception iteration times (ms)"] = str(iteration_times)
    DATA["Interception time (ms)"] = str(time_ms)

    # Decoder Bob
    bob = Receiver('Bob', original_bits_size)
    bob.set_axes()
    
    start_time = time.time()
    message, iteration_times = bob.decode_quantum_messageBob(message, 1, backend,checkIntercept,echAB,echEB)
    time_ms = (time.time() - start_time) * 1000
    # print('  Quantum decryption run in', str(time_ms), 'ms')
    DATA["Decryption iteration times (ms)"] = str(iteration_times)
    DATA["Decryption time (ms)"] = str(time_ms)

    # Alice - Bob Remove Garbage
    alice_axes = alice.axes # Alice share her axes
    bob_axes = bob.axes # Bob share his axes
    countertot=0
    counterdiff=0
    for i in range(len(alice_axes)):
      if (alice.axes[i]==bob.axes[i]):
        #if(eve.values[i]!=-1):
        countertot+=1
        if(alice.values[i] != bob.values[i]):
          counterdiff+=1
    #print("Ber noise sopra: "+str(counterdiff/countertot))
    #BerNoise=counterdiff/countertot
    # Delete the difference
    alice.remove_garbage(bob_axes)
    bob.remove_garbage(alice_axes)
    

    key_gen_time_ms = (time.time() - key_gen_time) * 1000
    DATA["Private key generation time (ms)"] = str(key_gen_time_ms)

    key_check_time = time.time()
    # Bob share some values of the key to check
    SHARED_SIZE = round(0.5 * len(bob.key))
    shared_key = bob.key[:SHARED_SIZE]

    
    if verbose:
      #alice.show_values()
      #alice.show_axes()
      DATA['Alice Values'] = str(alice.show_values())
      DATA['Alice Axes'] = str(alice.show_axes())

      #eve.show_values()
      #eve.show_axes()
      DATA['Eve Values'] = str(eve.show_values())
      DATA['Eve Axes'] = str(eve.show_axes())

      #bob.show_values()
      #bob.show_axes()
      DATA['Bob Values'] = str(bob.show_values())
      DATA['Bob Axes'] = str(bob.show_axes())

      #alice.show_key()
      #bob.show_key()
      DATA['Alice Key'] = str(alice.show_key())
      DATA['Bob Key'] = str(bob.show_key())

      print('\nShared Bob Key:')
      print(shared_key)
      DATA['Shared Key'] = str(shared_key)
      
    alice_key = alice.show_key()
    compare = alice_key[:len(shared_key)]
    counter = 0
    for i in range(len(shared_key)):
      if(shared_key[i] != compare[i]):
        counter = counter + 1
    DATA["Shared differences"] = str(counter)
    DATA["Shared key length"] = str(len(shared_key))
    DATA["Shared BER"] = str(counter/len(shared_key))
    sampleQber=float(counter/len(shared_key))
    #d=float(2*(sampleQber-echAB)+2*echAB-1/2)
    d=float(2*(sampleQber)-0.5)
    pos1,pos2=self.solve_quadratic(d, Y0, e, eta, c, alpha)
    DATA["Estimated EVE position 1"]=str(pos1)
    DATA["Estimated EVE position 2"]=str(pos2)
    #psample=(sampleQber-ech)/(0.25-ech**2)
    #print('\nSample p: '+str(psample))

    alice_key = alice.show_key()
    bob_key = bob.show_key()
    counter = 0
    for i in range(len(alice_key)):
      if(alice_key[i] != bob_key[i]):
        counter = counter + 1
    DATA["Full key differences"] = str(counter)
    DATA["Full key length"] = str(len(alice_key))
    DATA["Full key BER"] = str(counter/len(alice_key))

    # Alice check the shared key
    if alice.check_key(shared_key):
      shared_size = len(shared_key)
      alice.confirm_key(shared_size)
      bob.confirm_key(shared_size)
      if verbose:
        print('\nFinal Keys')
        alice.show_key()
        bob.show_key()
        print('\nSecure Communication!')
    elif verbose:
      print('\nUnsecure Communication! Eve has been detected intercepting messages\n')
      DATA['Result'] = 'Unsecure (intercepted)'

    key_check_time_ms = (time.time() - key_check_time) * 1000
    DATA["Key checking time (ms)"] = str(key_check_time_ms)
    return alice, bob



  ## Run the implementation of BB84 protocol
  def run(self, message, backend, original_bits_size, measure_density, n_bits, verbose,echAB,echAE,echEB,Y0, e, eta, c, alpha):
    ## The original size of the message
    self.original_bits_size = original_bits_size
    ## The probability of an interception occurring
    self.measure_density = measure_density

    alice, bob = self.__generate_key(backend, original_bits_size, verbose,echAB,echAE,echEB,Y0, e, eta, c, alpha)
    #print("Ber noise sotto: "+str(BerNoise))
    shared_key_time = time.time()
    if not (alice.is_safe_key and bob.is_safe_key):
      if verbose:
        print('❌ Message not sent')
        DATA['Result'] = 'Message not sent'
        DATA['Alice OTP'] = '-'
        DATA['Bob OTP'] = '-'
        DATA["Shared key demonstration time (ms)"] = '-'
        df = pd.DataFrame(DATA)
        filename = 'data.xlsx'
        df.to_excel(filename, index=False)
      return False

    alice.generate_otp(n_bits)
    bob.generate_otp(n_bits)

    encoded_message = alice.xor_otp_message(message)
    decoded_message = bob.xor_otp_message(encoded_message)

    if verbose:
      alice.show_otp()
      bob.show_otp()
      DATA['Alice OTP'] = str(alice.show_otp())
      DATA['Bob OTP'] = str(bob.show_otp())

      print('\nInitial Message:')
      print(message)

      print('Encoded Message:')
      print(encoded_message)

      print('💡 Decoded Message:')
      print(decoded_message)

      shared_key_time_ms = (time.time() - shared_key_time) * 1000
      DATA["Shared key demonstration time (ms)"] = str(shared_key_time_ms)

      if message == decoded_message:
        print('\n✅ The initial message and the decoded message are identical')
        DATA['Result'] = 'Secure'
      else:
        print('\n❌ The initial message and the decoded message are different')
        DATA['Result'] = 'Different messages'
      df = pd.DataFrame(DATA)
      filename = 'data.xlsx'
      df.to_excel(filename, index=False)

    
  
    

  

    return True
  
  def solve_quadratic(self,d, Y0, e, eta, c, alpha):
    # Define the coefficients A, B, and C
    A = d * Y0 * eta - 0.5 * Y0 * eta
    B = d * Y0**2 + d * c * eta**2 - 0.5 * Y0**2 - 2 * e * c * eta**2  + 2 * e**2 * eta**2 * c
    C = d * Y0 * eta * c - 0.5 * Y0 * eta * c

    # Calculate the discriminant
    Delta = B**2 - 4 * A * C

    # Check the discriminant to ensure roots are real
    if Delta < 0:
        print("The equation has complex roots.")
        return 0,0

    # Calculate the roots using the quadratic formula
    sqrt_Delta = np.sqrt(Delta)
    root1 = (-B + sqrt_Delta) / (2 * A)
    root2 = (-B - sqrt_Delta) / (2 * A)

    # Calculate z from the roots
    if root1>0:
      z1 = -10 * np.log10(root1) / alpha
    else:
      z1=0
    if root2>0:
      z2 = -10 * np.log10(root2) / alpha
    else:
      z2=0

    return z1, z2
