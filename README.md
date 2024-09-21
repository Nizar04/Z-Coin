# Z-Coin


## Description
This project is a simulated cryptocurrency blockchain application that demonstrates fundamental blockchain principles and functionality. Developed using Python with Flask, the application enables users to interact with a decentralized ledger, allowing them to mine new blocks, create transactions, and explore the blockchain.

## Key Features

- **Blockchain Structure:**
  - Implements a blockchain data structure with a linked list of blocks, each containing a list of transactions, proof of work, a timestamp, and a reference to the previous block.

- **Mining Functionality:**
  - Simulates mining by solving a proof-of-work problem to add new blocks to the chain. Future enhancements will include real mining capabilities that utilize computational resources from users' devices, making the mining process more challenging as the number of miners increases.

- **Transaction Management:**
  - Users can create and manage transactions, with the application ensuring sufficient balance before processing. Future updates will introduce user accounts with unique IDs and wallet functionalities for more robust transaction management.

- **Web Interface:**
  - Provides a user-friendly web interface for interaction using Flask and HTML templates. Users will be able to mine directly from the webpage, leveraging their computer's processing power.

- **Data Storage:**
  - Utilizes SQLite to store transactions and blockchain data, ensuring that the state of the blockchain is preserved between sessions.

## Technologies Used
- Python
- Flask
- SQLite
- HTML/CSS

## Purpose
This project serves as an educational tool to demonstrate blockchain mechanics and transaction processing. It highlights foundational concepts of decentralized networks, consensus algorithms, and the economic principles behind cryptocurrency.

## Future Enhancements
- Integrating user accounts with wallets.
- Implementing real mining mechanics that utilize user computational resources.
- Dynamically adjusting mining difficulty based on the number of active miners.
  
These enhancements aim to provide a more realistic and engaging user experience.
