#!/usr/bin/env python3

# Author: Francesco Fiorini


from quantum_solver.quantum_solver import QuantumSolver
from crypto.bb84.bb84_algorithm import BB84Algorithm
import time
import matplotlib.pyplot as plt
import numpy as np
from halo import Halo
from numpy.random import randint
from random import SystemRandom, randrange
import string
from alive_progress import alive_bar
import pandas as pd
import math
from math import ceil

BB84_SIMULATOR = 'BB84 SIMULATOR'
DATA = {
  'Algorithm': ['BB84'],
  'Backend': [],
  'String': [],
  'Interception Density': [],
  'Alice Values': ['-'],
  'Alice Axes': ['-'],
  'Eve Values': ['-'],
  'Eve Axes': ['-'],
  'Bob Values': ['-'],
  'Bob Axes': ['-'],
  'Alice Key': ['-'],
  'Bob Key': ['-'],
  'Shared Key': ['-'],
  'Alice OTP': ['-'],
  'Bob OTP': ['-'],
  'Result': ['-'],
  'Encryption iteration times (ms)': ['-'],
  'Encryption time (ms)': ['-'],
  'Interception iteration times (ms)': ['-'],
  'Interception time (ms)': ['-'],
  'Decryption iteration times (ms)': ['-'],
  'Decryption time (ms)': ['-'],
  'Private key generation time (ms)': ['-'],
  'Key checking time (ms)': ['-'],
  'Shared key demonstration time (ms)': ['-'],
  'Total time (ms)': [],
  'Shared differences': ['-'],
  'Shared key length': ['-'],
  'Shared BER': ['-'],
  'Full key differences': ['-'],
  'Full key length': ['-'],
  'Full key BER': ['-'],
  'Estimated EVE position 1': ['-'],
  'Estimated EVE position 2': ['-'],
  'Bob dark count probability': [],
  'Eve dark count probability': [],
  'Bob detector error rate': [],
  'Eve detector error rate': [],
  'Bob detector efficiency': [],
  'Eve detector efficiency': [],
  'Fiber attenuation (dB/km)': [],
  'Distance between Alice and Bob (km)': [],
  'True Eve position from Alice (km)': []
}

## Main class of BB84 Simulator
## @see https://qiskit.org/textbook/ch-algorithms/quantum-key-distribution.html
class BB84:
  ## Constructor
  def __init__(self, token):
    ## The implemented protocol
    self.bb84_algorithm = BB84Algorithm()
    ## The IBMQ Experience token
    self.token = token

  ## Print header, get an QExecute and run main menu
  def run(self):
    ## A QExecute instance to execute the simulation
    self.qexecute = QuantumSolver(self.token).get_qexecute()
    self.__main_menu()

  ## Loop to run the main menu
  def __main_menu(self):
    while True:
      try:
        ## If a current backend has been selected
        self.is_selected_backend = self.qexecute.current_backend != None

        self.__show_options()
        self.__select_option()
      except Exception as _:
        pass

  ## Main menu
  def __show_options(self):
    is_guest_mode = self.qexecute.is_guest_mode()
    guest_mode_string = ' (Guest Mode)' if is_guest_mode else ''
    len_guest_mode_string = len(guest_mode_string)
    print('\n' + BB84_SIMULATOR + guest_mode_string)
    print('=' * (len(BB84_SIMULATOR) + len_guest_mode_string) + '\n')
    print('[1] See available Backends')
    print('[2] Select Backend')
    if self.is_selected_backend:
      print('\tCurrent Backend: ' + str(self.qexecute.current_backend))
    if self.is_selected_backend:
      print('[3] Run Algorithm')
    if self.is_selected_backend:
      print('[4] Experimental mode')
    print('[0] Exit\n')

  ## Run BB84 simulation once
  def __run_simulation(self, message, density,echAB,echAE,echEB,Y0B,Y0E,eE,eB,etaE,etaB,c,alpha):
    DATA['String'] = message
    DATA["Interception Density"] = str(density)
    backend = self.qexecute.current_backend
    DATA['Backend'] = str(backend)
    N_BITS = 6
    # bits_size = len(message) * 5 * N_BITS
    bits_size = message
    possible_chars = string.ascii_lowercase + string.ascii_uppercase + string.digits
    message = ''.join(SystemRandom().choice(possible_chars) for _ in range(ceil(message)))
    execution_description = str(self.qexecute.current_backend)
    execution_description += ' with message "'
    execution_description += message + '" and density "' + str(density) + '"'
    halo_text = 'Running BB84 simulation in ' + execution_description
    halo = Halo(text=halo_text, spinner="dots")
    try:
      halo.start()
      start_time = time.time()
      self.bb84_algorithm.run(message, backend, bits_size, density, N_BITS, True,echAB,echAE,echEB,Y0B,Y0E,eE,eB,etaE,etaB,c,alpha)
      time_ms = (time.time() - start_time) * 1000
      halo.succeed()
      print('  BB84 simulation run in', str(time_ms), 'ms')
      DATA["Total time (ms)"] = str(time_ms)
      
      df1 = pd.read_excel('data.xlsx')
      df2 = pd.DataFrame(DATA)
      df1.replace('-', pd.NA, inplace=True)
      df2.replace('-', pd.NA, inplace=True)

      merged_df = df1.combine_first(df2)
      concat_row = merged_df.iloc[0].to_frame().T

      final_df = pd.read_excel('final_data.xlsx')
      file_concat = pd.concat([final_df, concat_row], axis=0)
      file_concat.to_excel('final_data.xlsx', index=False)

    except Exception as exception:
      halo.fail()
      print('Exception:', exception)

  ## Run an experiment of BB84 simulation
  def __experimental_mode(self, step_msg=5, len_msg_limit=75, density_step=0.05, density_min=0, density_max=1, repetition_instance=30):
    STEP_MSG = step_msg
    DENSITY_MIN = density_min
    DENSITY_MAX = density_max
    DENSITY_RANGE = int((DENSITY_MAX - DENSITY_MIN) / density_step)
    backend = self.qexecute.current_backend
    possible_chars = string.ascii_lowercase + string.ascii_uppercase + string.digits
    image = np.zeros((DENSITY_RANGE + 1, len_msg_limit // STEP_MSG))
    x = list(range(STEP_MSG, len_msg_limit + 1, STEP_MSG))
    y = list(np.arange(DENSITY_MIN, DENSITY_MAX + density_step, density_step))
    start_time = time.time()
    print('\nRunning BB84 Simulator Experiment (in ' + str(backend) + '):')

    try:
      with alive_bar(len(x) * len(y) * repetition_instance) as bar:
        for j, density in enumerate(y):
          for i, len_message in enumerate(x):
            for _ in range(repetition_instance):
              message = ''.join(SystemRandom().choice(possible_chars) for _ in range(len_message))
              bits_size = len(message) * 5
              # time_start
              flag = self.bb84_algorithm.run(message, backend, bits_size, density, 1, False)
              # time_end
              image[j][i] += 1 if flag else 0
              bar()
          
    except Exception as exception:
      print('Exception:', exception)

    time_m = (time.time() - start_time)
    print('\n[$] Experiment Finished in ' + str(time_m) + ' s!')
    print('\n💡 Output:\n\nx: ' + str(x) + '\n\ny: ' + str(y))
    print('\nImage:\n' + str(image) + '\n')
    plt.figure(num='BB84 Simulator - Experimental Mode [' + str(backend) + ']')
    plt.pcolormesh(x, y, image, cmap='inferno', shading='auto')
    plt.colorbar(label='Times the protocol is determined safe')
    plt.xlabel('Message Length (number of bits)')
    plt.ylabel('Interception Density')
    plt.show()

  ## Select the option for main menu
  def __select_option(self):
    option = int(input('[&] Select an option: '))
    if option == 0:
      print()
      exit(0)
    elif option == 1:
      self.qexecute.print_avaiable_backends()
    elif option == 2:
      self.qexecute.select_backend()
    elif option == 3 and self.is_selected_backend:
      message = int(input('[&] Key length (bits): '))
      density = float(input('[&] Interception Density (float between 0 and 1): '))
      Evepositions=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111]
      # 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111
      # 112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159
      #Evepositions=[1,2,3,4,5]
      #density_ranges = [0, 0.2, 0.4, 0.6, 0.8, 1]
      #for i in density_ranges: #se rimetto, indenta sotto fino a prima di elif
      numberofiterations=int(input('[&] Number of iterations: '))
      Y0B=float(input('[&] Bob dark count probability: '))
      DATA["Bob dark count probability"] = str(Y0B)
      Y0E=float(input('[&] Eve dark count probability: '))
      DATA["Eve dark count probability"] = str(Y0E)
      eB=float(input('[&] Bob detector error rate: '))
      DATA["Bob detector error rate"]=str(eB)
      eE=float(input('[&] Eve detector error rate: '))
      DATA["Eve detector error rate"]=str(eE)
      etaB=float(input('[&] Bob detector efficiency: '))
      DATA["Bob detector efficiency"]=str(etaB)
      etaE=float(input('[&] Eve detector efficiency: '))
      DATA["Eve detector efficiency"]=str(etaE)
      alpha=float(input('[&] Fiber attenuation (dB/km): '))
      DATA["Fiber attenuation (dB/km)"]=str(alpha)
      l=float(input('[&] Distance between Alice and Bob (km): '))
      DATA["Distance between Alice and Bob (km)"]=str(l)
      #x=float(input('[&] Eve position from Alice (km): '))
      #DATA["True Eve position from Alice (km)"]=str(x)
      for i in Evepositions:
        x=i
        DATA["True Eve position from Alice (km)"]=str(x)
        tAB=float(etaB*(10**(-alpha * l/ 10)))
        tAE=float(etaE*(10**(-alpha * x / 10)))
        tEB=float(etaB*(10**(-alpha * (l-x)/ 10)))
        echAB=float((0.5 * Y0B + eB * tAB) / (Y0B + tAB))
        echAE=float((0.5 * Y0E + eE * tAE) / (Y0E + tAE))
        echEB=float((0.5 * Y0B + eB * tEB) / (Y0B + tEB))
        c=float(10**(-alpha * l/ 10))
        for _ in range(numberofiterations):
          self.__run_simulation(message,density,echAB,echAE,echEB,Y0B,Y0E,eE,eB,etaE,etaB,c,alpha)
    elif option == 4 and self.is_selected_backend:
      step_msg = int(input('[&] Specify message steps (number of bits): '))
      len_msg_limit = int(input('[&] Specify maximum message length (number of bits): '))
      density_step = float(input('[&] Specify density step: '))
      density_min = float(input('[&] Specify density min: '))
      density_max = float(input('[&] Specify density max: '))
      repetition_instance = int(input('[&] Specify number of repetitions for each instance: '))

      if len_msg_limit <= 0:
        raise ValueError('Maximum message length must be positive (> 0)')
      elif repetition_instance <= 0:
        raise ValueError('Number of repetitions for each instance must be positive (> 0)')
      elif density_step < 0 or density_step > 1:
        raise ValueError('Density step must be between 0 and 1 (∈ [0, 1])')
      else:
        if 1.0 % density_step != 0:
          density_step = 1 / round(1 / density_step)
        self.__experimental_mode(step_msg, len_msg_limit, density_step, density_min, density_max, repetition_instance)
    else:
      print('[!] Invalid option, try again')


