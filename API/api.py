from flask import Flask, Response, request
from flask_cors import CORS, cross_origin
import sys
sys.path.append("..")
from socket_serve import *
from blockChain import Blockchain
app=Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/get_issue_form_backend', methods=['GET'])
@cross_origin()
def get_issue_form_backend():
    return Response('123', status=(200))

@app.route('/post_issue', methods=['POST', 'OPTIONS'])
@cross_origin()
def post_issue():
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        print("cors ok")
        return ('cors ok', 204, headers)
    elif request.method != 'POST':
        print('only post allow!')
    else:
        return Response('123', status=(200))

def main():
    print("alert: press R while server function block the register")
    global regINfo
    regINfo = register()
    if regINfo == "Account_illegal":
        return
    if regINfo == "Password_illegal":
        return
    global block
    block = Blockchain()
    regINfo["listening_port"], others = open_server()
    while true:    
        com = input("Command: ") 
        if com == 'Y':
            tar_ip = input("Input the ip you want to connect:")
            tar_port = int(input("Input the port you want to connect:"))
            sending_Client(regINfo,tar_ip,tar_port)
        elif com == 'Show others':
            print(others)
        elif com == 'Show block':
            print(block.chain)
        elif com == 'Send':
            latitude = input("Latitude:")
            longtitude = input("Longitude")
            Text = input("Text")
            contact = input("contact")
            block.new_message(Send_help(latitude,longtitude,Text,contact))
            if len(block.chain) == 0 :
                block.new_block(false)
            else: 
                block.new_block(false,block.show_block()[-1]["hash"])
            Send_to_others(others)
        elif com == 'accept':
            index = input("Accept index")
            Accept(index)
        elif com == 'R':
            continue
        else: 
            print("wrong command")
            continue

if __name__=='__main__':
    # app.run(host='127.0.0.1',port=21, debug=True, use_reloader=False)
    main()