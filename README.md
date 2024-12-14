# QKDEavesdropperLocalization
# Qiskit Implementation of Eavesdropper Localization method for fiber BB84 Quantum Key Distribution protocol

This code provides a Qiskit implementation of a statistical method for localizing eavesdroppers along an optical fiber within the framework of the BB84 Quantum Key Distribution protocol. The software simulates the protocol's operations and by leveraging the analytical Quantum Bit Error Rate (QBER) model, it identifies the two candidate positions of an eavesdropper conducting a full intercept-resend attack on the fiber.

## Table of Contents
- [Installation and Usage](#installation-and-usage)
- [Features](#features)
- [Contributing](#contributing)
- [License](#license)


## Installation and Usage
For installation, please refer to the quantum-solver library presented by Daniel Escanez-Exposito in https://github.com/jdanielescanez/quantum-solver. The code for this implementation is intended to replace the existing BB84 folder in `quantum-solver/src/crypto`. Therefore, it is required to replace the mentioned folder with the current package bb84Localization and rename the latter as "bb84".

## Features
- Implementation of fiber-based BB84 QKD protocol
- Channel error model depending on fiber's and receiver's parameters.
- Simulation of a full intercept-resend attack by an eavesdropper placed along the fiber
- Eeavesdropper position estimation based on QBER statistics

## Contributing
Contributions are welcome! Please contact francesco.fiorini@phd.unipi.it for suggested changes.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
