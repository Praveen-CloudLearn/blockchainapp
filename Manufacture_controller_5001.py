#Importing the libraries
from flask import Flask, jsonify,request
from uuid import uuid4
import requests

#blockchain part

import datetime
import hashlib
import json
from urllib.parse import urlparse


class Blockchain:
    
    def __init__(self):
        self.chain = []
        self.transactions=[]
        self.create_block(proof=1,previous_hash='0')
        self.nodes=set()
        
    def create_block(self,proof,previous_hash):
        block={'index':len(self.chain)+1,
               'timestamp':str(datetime.datetime.now()),
               'proof':proof,
               'previous_hash':previous_hash,
               'transactions':self.transactions}
        self.transactions=[]
        self.chain.append(block)
        return block
    
    def get_previous_block(self):
        return self.chain[-1]
    
    def proof_of_work(self,previous_proof):
        new_proof=1
        check_proof=False
        while check_proof is False:
            hash_operation=hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4]=='0000':
                check_proof = True
            else:
                new_proof=new_proof+1
        return new_proof
    
    def hash(self,block):
        encoded_block=json.dumps(block,sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()                    
    
    def is_chain_valid(self,chain):
        previous_block=chain[0]
        block_index=1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block=block
            block_index=block_index+1
        return True
    
    def add_transaction(self,sender,receiver,itemcode,lot,quantity):
        self.transactions.append({'sender':sender,
                                  'receiver':receiver,
                                  'itemcode':itemcode,
                                  'LOT':lot,
                                  'quantity':quantity})
        previous_block=self.get_previous_block()
        return previous_block['index']+1
    
    def add_node(self,address):
        parsed_url=urlparse(address)
        self.nodes.add(parsed_url.netloc)
        
    def replace_chain(self):
        network=self.nodes
        longest_chain=None
        max_length=len(self.chain)
        for node in network:
            response=requests.get(f'http://{node}/get_chain')
            if response.status_code==200:
                length=response.json()['length']
                chain=response.json()['chain']
                if length>max_length and self.is_chain_valid(chain):
                    max_length=length
                    longest_chain=chain
        if longest_chain:
            self.chain=longest_chain
            return True
        return False

    #This function is used to iterate over the blockchain to find an attribute with a particular attribute value
    def iterate_chain(self,attr_name,attr_value):
        attr_transactions=set()
        for index_block in range(len(self.chain)):
            transactions=self.chain[index_block]['transactions']
            for index_transaction in range(len(transactions)):
                if transactions[index_transaction][attr_name] == attr_value:
                    attr_transactions.add('b'+str(index_block)+'t'+str(index_transaction))
        return attr_transactions
    
#Manufacturer part
class Manufacturer:
    
    def add_transaction(self,blockchain,sender,distributor,itemcode,lot,quantity):
        index=blockchain.add_transaction(sender,distributor,itemcode,lot,quantity)
        return index
    
#    def private_public_key()

app = Flask(__name__)

#Creating a blockchain
blockchain=Blockchain()

#Creating manufacturer
manufacturer=Manufacturer()

#creating an address for the node on the port 5001
node_address=str(uuid4()).replace('-','')

#Mining a new block
@app.route('/mine_block',methods=['GET'])
def mine_block():
    previous_block=blockchain.get_previous_block()
    previous_proof=previous_block['proof']
    proof=blockchain.proof_of_work(previous_proof)
    previous_hash=blockchain.hash(previous_block)
    block=blockchain.create_block(proof,previous_hash)
    response={'message':'Congratulations, you just mined a block!',
              'index':block['index'],
              'timestamp':block['timestamp'],
              'proof':block['proof'],
              'previous_hash':block['previous_hash'],
              'transactions':block['transactions']}
    return jsonify(response), 200

@app.route('/get_chain',methods=['GET'])
def get_chain():
    response={'chain':blockchain.chain,
              'length':len(blockchain.chain)}
    return jsonify(response), 200

@app.route('/is_valid',methods=['GET'])
def is_valid():
    is_valid=blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        return jsonify({'message':'All good.. The blockchain is valid.)'}),200
    else:
        return jsonify({'message':'Houston, we have a problem. The Blockchain is not valid'}),200
           
#connecting all the nodes 
@app.route('/connect_node',methods=['POST'])
def connect_node():
    json=request.get_json()
    nodes=json.get('nodes')
    if nodes is None:
        return 'No node',400
    for node in nodes:
        blockchain.add_node(node)
    response={'message':'All the nodes are connected now. It contains the following nodes:',
              'total_nodes':list(blockchain.nodes)}
    return jsonify(response),201

@app.route('/replace_chain',methods=['GET'])
def replace_chain():
    is_chain_replaced=blockchain.replace_chain()
    if is_chain_replaced==True:
        return jsonify({'message':'The nodes had different chains so the chain was replaced by the longest one.',
                        'new_chain':blockchain.chain}),200
    else:
        return jsonify({'message':'All good. The chain is the largest one.',
                        'actual_chain':blockchain.chain}),200

@app.route('/add_transaction',methods=['GET'])        
def add_transaction():
    url='http://129.146.67.39:2401/jderest/orchestrator/Blockchain_CFC_V554211F'
    json_in={"username":"sourav",
          "password":"sourav",
          "environment":"JDV920",
          "Order Co 1":"00001",
          "Or Ty 1":"SO",
          "Business.. Unit.. 1": "30",
          "Add Num 1":"4243",
          "Order Date 1":"01/01/2021",
          "Next Stat 1":"580",
          "Last Stat 1":"560"}
    out=requests.post(url, json = json_in)
    status_code=out.status_code
    json_out=out.json()
    if(status_code!=200):
        print(status_code)
        return jsonify({'message' : json_out['message']}),200
    transactions=json_out["Blockchain_CFC_V554211F"]["rowset"]
    transaction_count=0
    for trans in transactions:
        transaction_count=transaction_count+1
        json=trans
        transaction_keys=['sender','receiver','itemcode','LOT','quantity','LOT expiration date']
        if not all (key in json for key in transaction_keys):
            return 'Some elements of the transation are missing for transaction number: '+str(transaction_count),400
        index=manufacturer.add_transaction(blockchain,json['sender'],json['receiver'],json['itemcode'],json['LOT'],json['quantity'])
    return jsonify({'message' : f'This transaction will be added to Block {index}'}),201

app.run(host='0.0.0.0',port=5001)