import hashlib
from itertools import chain
import json
from re import L
from tabnanny import check
from time import time
from typing_extensions import Self
from socket_serve import *
from sqlalchemy import false

class Blockchain(object):
    def _init_(self):
        self.current_message = [] #json message
        self.chain = []
        self.new_block(previous_hash = 1 , proof = 100)

    def new_message(self,m):
        self.current_message = m
        
    def new_block(self, proof, previous_hash=None):
 
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'message': self.current_message,
            'proof': proof, #proof id
            'hash': None,
            'previous_hash': previous_hash,
            'accept':false,
            'accept_info': None
        }
        self.current_transactions = []
        self.chain.append(block)
        return block

    def show_block(self):
        return self.chain
    
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    def proof_accept(self,account,password,b,p):
        if [account,password,b,p] in others:
            print('{} accept mission'.format(account))
            return true
        else:
            print('{} is not identified'.format(account))
            return false
    
    def find_hash(self,hash_value):
        v=-1
        for i in self.chain:
            v += 1
            if hash_value == i["hash"]:
                return v
        return v
    
    def check_hash_all(self):
        v = 0
        for i in self.chain[1:]:
            v+=1
            if i['previous_hash'] != hash(i-1):
                return v
        return true
    def check_hash(self,ch,place_hold):
        #還沒考慮溢為問題
        if self.hash(ch[place_hold-1]) != ch[place_hold]["previous_hash"] or self.hash(ch[place_hold]) != ch[place_hold]["hash"]:
            return false
        else:
            return true
    #return false if seriously problem
    def check_mutual_chain(self,others_chain):
        print("Checking mutual chain")
        v=-1
        if len(self.chain) > len(others_chain):
            others_chain.extend(self.chain[len(others_chain)])
        elif len(self.chain) < len(others_chain):
            self.chain.extend(others_chain[len(self.chain)])
        for i,j in self.chain,others_chain:
            v+=1
            if i["hash"]!= j["hash"]:
                print("collapse...solving")
                if self.check_hash(self.chain,v) == false and self.check_hash(others_chain,v) != false:
                    self.chain[v] = others_chain[v]
                    continue
                elif self.check_hash(self.chain,v) != false and self.check_hash(others_chain,v) == false:
                    others_chain[v] = self.chain[v]
                    continue
                elif self.check_hash(self.chain,v) == true and self.check_hash(others_chain,v) == true:
                    self.chain.insert(v+1,j)
                    self.chain[v+1]["previous_hash"] = self.chain[v]["hash"]
                    if v+2 < len(self.chain):
                        self.chain[v+2]["previous_hash"] = self.chain[v+1]["hash"]
                    others_chain.insert(v,i)
                    if v-1>=0:
                        others_chain[v]["previous_hash"] = self.chain[v-1]["hash"]
                    others_chain[v+1]["previous_hash"] = self.chain[v]["hash"]
                    continue
                print("collapse seriously......")
                return false
        print("finish_merging")
        return true

                

            
        
    
    
    
