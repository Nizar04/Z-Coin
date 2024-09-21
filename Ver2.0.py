import hashlib
import json
from time import time
from uuid import uuid4
from flask import Flask, jsonify, request, render_template
import sqlite3

app = Flask(__name__)

node_identifier = str(uuid4()).replace('-', '')

class Blockchain:
    def __init__(self):
        self.connection = sqlite3.connect('blockchain.db', check_same_thread=False)
        self.create_tables()
        self.chain = []
        self.current_transactions = []
        self.nodes = set()
        self.difficulty = 4  # Starting difficulty for mining
        self.max_supply = 21000000  # Maximum supply of the cryptocurrency
        self.current_supply = 0
        self.block_reward = 50  # Initial reward for mining a block
        self.halving_interval = 210000  # Blocks between reward halvings

        # Create the genesis block
        self.new_block(previous_hash='1', proof=100)

    def create_tables(self):
        with self.connection:
            self.connection.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY,
                    sender TEXT,
                    recipient TEXT,
                    amount REAL,
                    timestamp REAL
                )
            ''')
            self.connection.execute('''
                CREATE TABLE IF NOT EXISTS blocks (
                    block_index INTEGER PRIMARY KEY,
                    timestamp REAL,
                    proof INTEGER,
                    previous_hash TEXT
                )
            ''')
            self.connection.execute('''
                CREATE TABLE IF NOT EXISTS balances (
                    address TEXT PRIMARY KEY,
                    balance REAL
                )
            ''')

    def new_block(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        self.current_transactions = []
        self.chain.append(block)

        with self.connection:
            self.connection.execute('''
                INSERT INTO blocks (block_index, timestamp, proof, previous_hash)
                VALUES (?, ?, ?, ?)
            ''', (block['index'], block['timestamp'], proof, block['previous_hash']))

        return block

    def new_transaction(self, sender, recipient, amount):
        if sender != "0" and self.get_balance(sender) < amount:
            return False

        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        if sender != "0":
            self.update_balance(sender, -amount)
        self.update_balance(recipient, amount)

        with self.connection:
            self.connection.execute('''
                INSERT INTO transactions (sender, recipient, amount, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (sender, recipient, amount, time()))

        return self.last_block['index'] + 1

    def get_balance(self, address):
        cursor = self.connection.cursor()
        cursor.execute('SELECT balance FROM balances WHERE address = ?', (address,))
        result = cursor.fetchone()
        return result[0] if result else 0

    def update_balance(self, address, amount):
        current_balance = self.get_balance(address)
        new_balance = current_balance + amount
        with self.connection:
            self.connection.execute('''
                INSERT OR REPLACE INTO balances (address, balance)
                VALUES (?, ?)
            ''', (address, new_balance))

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_proof):
        proof = 0
        while not self.valid_proof(last_proof, proof):
            proof += 1
        return proof

    def valid_proof(self, last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:self.difficulty] == '0' * self.difficulty

    def adjust_difficulty(self):
        if len(self.chain) % 10 == 0:
            last_ten_blocks = self.chain[-10:]
            time_diff = last_ten_blocks[-1]['timestamp'] - last_ten_blocks[0]['timestamp']
            if time_diff < 50:
                self.difficulty += 1
            elif time_diff > 100:
                self.difficulty = max(1, self.difficulty - 1)

    def get_block_reward(self):
        halvings = len(self.chain) // self.halving_interval
        return self.block_reward / (2 ** halvings)

blockchain = Blockchain()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    reward = blockchain.get_block_reward()

    if blockchain.current_supply + reward <= blockchain.max_supply:
        blockchain.new_transaction(sender="0", recipient=node_identifier, amount=reward)
        blockchain.current_supply += reward
    else:
        return jsonify({'message': 'Maximum supply reached. No more coins can be mined.'}), 200

    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    blockchain.adjust_difficulty()

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
        'difficulty': blockchain.difficulty,
        'reward': reward,
        'current_supply': blockchain.current_supply,
    }
    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    transaction_success = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    if not transaction_success:
        return jsonify({'message': 'Insufficient balance'}), 400

    response = {'message': f'Transaction will be added to Block {blockchain.last_block["index"] + 1}'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

@app.route('/balance/<address>', methods=['GET'])
def get_balance(address):
    balance = blockchain.get_balance(address)
    return jsonify({'address': address, 'balance': balance}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

    