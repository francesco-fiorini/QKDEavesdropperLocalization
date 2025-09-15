# QKDEavesdropperLocalization
## Qiskit Implementation of Fiber-Based BB84 Quantum Key Distribution with Intercept-Resend Attack

This project provides a **Qiskit-based simulation** of a fiber-based Quantum Key Distribution (QKD) scenario using the BB84 protocol between two parties (Alice and Bob).  
An eavesdropper (Eve) is modeled performing a full intercept-resend attack on the transmitted qubits.  

Each channel segment introduces a bit-flip error with a probability that depends on the fiber length and the properties of the employed detectors (dark count probability and detection efficiency).  

The tool also supports the simulation of an **asymmetric network scenario**, where the **receiver devices** of the eavesdropper and Bob may have **different characteristics**.  

Finally, this implementation is designed to **localize the position of the eavesdropper** along the fiber, given the sample QBER (Quantum Bit Error Rate) data, using either:  
- an **analytical/statistical method**, or  
- a **neural network–based approach**.

All simulation parameters and QBER results are stored in an external Excel file.

## Table of Contents
- [Installation and Usage](#installation-and-usage)
- [Features](#features)
- [Contributing](#contributing)
- [License](#license)


## Installation and Usage
For installation, please refer to the quantum-solver library presented by Daniel Escanez-Exposito in https://github.com/jdanielescanez/quantum-solver. The code for this implementation is intended to replace the existing BB84 folder in `quantum-solver/src/crypto`. Therefore, it is required to replace the mentioned folder with the current package `code` and rename the latter as "bb84".

## Features
- Implementation of fiber-based BB84 QKD protocol
- Channel error model depending on fiber's and receiver's parameters
- Support for asymmetric network scenarios with heterogeneous device properties
- Simulation of a full intercept-resend attack by an eavesdropper placed along the fiber
- Eavesdropper position estimation capability based on QBER sample data (analytical/statistical or neural network–based)
- Automatically simulates Eve's positions from 1 up to l-1, where l represents the fiber length (km) between Alice and Bob.

## Contributing
Contributions are welcome! Please contact francesco.fiorini@phd.unipi.it for suggested changes.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
