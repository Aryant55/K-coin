

#importing libraries
import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse


#building blockchain

class Blockchian:
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.nodes = set()
        self.createblock(proof=1, previous_hash='0')

    def createblock(self, proof, previous_hash):
        block = {'index': len(self.chain)+1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash,
                 'transactions': self.transactions}
        self.transactions = []
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]

    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            h_o = hashlib.sha256(
                str(new_proof**2-previous_proof**2).encode()).hexdigest()
            if h_o[0:4] == '0000':
                check_proof = True
            else:
                new_proof += 1

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_vaild(self, chain):
        p_block = chain[0]
        b_index = 1
        while b_index < len(chain):
            b_now = chain[b_index]
            if self.hash(p_block) != b_now['previous_hash']:
                    return False
            previous_proof = p_block['proof']
            new_proof = b_now['proof']
            h_o = hashlib.sha256(
                str(new_proof**2-previous_proof**2).encode()).hexdigest()
            if h_o[:4] != '0000':
                return False
            p_block = b_now
            b_index += 1
        return True

    def add_tran(self, sender, reciever, amount):
        self.transactions.append({'sender': sender,
                                  'reciever': reciever,
                                  'amount': amount})
        p_block = self.get_previous_block()
        return p_block['index']+1

    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_len = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['lenght']
                chain = response.json()['chain']
                if(max_len < length and self.is_chain_vaild(chain)):
                    longest_chain = chain
                    max_len = length

        if longest_chain:
            self.chain = longest_chain
            return True
        else:
            return False


#mining

#creating a web app


app = Flask(__name__)

#creating an blockchain
node_address = str(uuid4()).replace('-', '')
blockchain = Blockchian()


@app.route('/mine_block', methods=['GET'])
def mine_block():
    p_block = blockchain.get_previous_block()
    p_hash = blockchain.hash(p_block)
    proof = blockchain.proof_of_work(p_block['proof'])
    blockchain.add_tran(sender=node_address, reciever='katsura', amount=1)
    block = blockchain.createblock(proof, p_hash)
    response = {'message': 'congo bro!!!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions': block['transactions']}
    return jsonify(response), 200


@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200


@app.route('/is_valid', methods=['GET'])
def is_valid():
    ch = blockchain.chain
    response = {}
    if(blockchain.is_chain_vaild(ch) == True):
        response = {'valid': True}
    else:
        response = {'valid': False}
    return jsonify(response), 200


@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    json = request.get_json()
    t_keys = ['sender', 'reciever', 'amount']
    if not all(key in json for key in t_keys):
        return "Some keys are missing ", 400
    index = blockchain.add_tran(json['sender'], json['reciever'], json['amount'])
    response = {'message': f'This transaction will be added to block {index}'}
    return jsonify(response), 201


@app.route('/connect_node', methods=['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return "No Node",400
    for node in nodes:
        blockchain.add_node(node)
    response = {'message': 'All the nodes have been added',
                'total_node': list(blockchain.nodes)}
    return jsonify(response),201

@app.route('/replace_chain',methods = ['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = {'message': 'chain is changes',
                    'new_chain': blockchain.chain}
    else:
        response = {'message': 'chain is largest',
                    'new_chain': blockchain.chain}
    return jsonify(response),400

    
#running the app


app.run(host='0.0.0.0', port=5001)
