import hashlib
import json
from time import time
from numpy import object0

from sqlalchemy import false, true

class Blockchain(object):
    def __init__(self):
        self.current_message = [] #json message
        self.chain = []
    def hash(self,block):
        print("hashing")
        encoded_block = json.dumps(block["message"], sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    def new_message(self,m):
        self.current_message = m
        
    def new_block(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': None,
            'message': self.current_message,
            'proof': None, #proof id
            'hash': None,
            'previous_hash': previous_hash,
            'accept': "false",
            'accept_info': None
        }
        print(block)
        self.chain.append(block)
        self.chain[-1]["hash"] = self.hash(block)
        return block

    def show_block(self):
        return self.chain

    def proof_accept(self,account,password,b,p,others):
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
            if i['previous_hash'] != self.hash(self.chain[v-1]):
                return v
        return true
    def check_hash(self,ch,place_hold):
        #還沒考慮溢為問題
        if self.hash(ch[place_hold-1]) != ch[place_hold]["previous_hash"] or self.hash(ch[place_hold]) != ch[place_hold]["hash"]:
            return false
        else:
            return true
    #return false if seriously problem
    def same_chain(self,others_chain):
        if self.chain == others_chain:
            return true
        else: return
    def check_mutual_chain(self,others_chain):
        print("Checking mutual chain")
        v=-1
        #長度變一樣
        if len(self.chain) > len(others_chain):
            others_chain.extend(self.chain[len(others_chain):])
        elif len(self.chain) < len(others_chain):
            self.chain.extend(others_chain[len(self.chain):])
        #
        print("collapse...solving")
        print(f'self chain{self.chain}')
        print(f'others chain{others_chain}')
        for i,j in zip(self.chain,others_chain):
            v+=1
            if i["hash"]!= j["hash"]:
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
        self.chain = others_chain
        print("finish_merging")
        return true

                

            
        
    
    
    
