

#importing libraries
import datetime
import hashlib
import json
from flask import Flask,jsonify

#building blockchain

class Blockchian:
    def __init__(self):
        self.chain = []
        self.createblock(proof = 1, previous_hash = '0')
        
    def createblock(self,proof,previous_hash):
        block = {'index':len(self.chain)+1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash}
        self.chain.append(block)
        return block
    
    def get_previous_block(self):
        return self.chain[-1]

    def proof_of_work(self,previous_proof):
        new_proof = 1
        check_proof = False;
        while check_proof is False:
            h_o = hashlib.sha256(str(new_proof**2-previous_proof**2).encode()).hexdigest()
            if h_o[0:4]=='0000':
                check_proof = True
            else:
                new_proof+=1
        return new_proof
    
    def hash(self, block):
        encoded_block = json.dumps(block,sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_vaild(self,chain):
        p_block = chain[0]
        b_index = 1
        while b_index <len(chain):
            b_now = chain[b_index]
            if self.hash(p_block)!=b_now['previous_hash']:
                    return False
            previous_proof = p_block['proof']
            new_proof = b_now['proof']
            h_o = hashlib.sha256(str(new_proof**2-previous_proof**2).encode()).hexdigest()
            if h_o[:4]!='0000':
                return False
            p_block = b_now
            b_index+=1
        return True
            

#mining

#creating a web app

app = Flask(__name__)

#creating an blockchain

blockchain = Blockchian()

@app.route('/mine_block', methods=['GET'])
def mine_block():
    p_block = blockchain.get_previous_block()
    p_hash = blockchain.hash(p_block)
    proof= blockchain.proof_of_work(p_block['proof'])
    block = blockchain.createblock(proof,p_hash)
    response = {'message':'congo bro!!!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash']}
    return jsonify(response), 200

@app.route('/get_block', methods=['GET'])
def get_chain():
    response = {'chain': blockchain.chain ,
                'length': len(blockchain.chain)}
    return jsonify(response), 200
    
@app.route('/is_valid',methods=['GET'])
def is_valid():
    ch = blockchain.chain
    response = {}
    if(blockchain.is_chain_vaild(ch)==True):
        response = {'valid': True}
    else:
        response = {'valid':False}
    return jsonify(response),200
        

#running the app

app.run(host='0.0.0.0', port = 5000)

































