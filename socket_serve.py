from socket import *
import socketserver
import threading,sys,json,re
from sqlalchemy import false, true
from blockChain import Blockchain 
import time
from flask import Flask, Response, request
from flask_cors import CORS, cross_origin
#定義json格式
'''
    message = {
        "category" = 1 #register and save connection
        "account" = (string)
        "password" = (string)
        "listening_port" = (int)  
    }

    message = {
        "category" = 2 #helping message
        "block" = self.block
    }

    message = {
        "category" = 3 #refresh connection list
        "others" = [[ip,port],]
    }

'''
#註冊的函式(如果不需要的話可以自動分配)
#傳回註冊的訊息(包含要傳的東西)
def register():
    myre = r"^[_a-zA-Z]\w{0,}"
    #正則驗證使用者名稱是否合乎規範
    accout = input('Please input your account: ')
    if not re.findall(myre, accout):
        print('Account illegal!')
        return None
    password1  = input('Please input your password: ')
    password2 = input('Please confirm your password: ')
    if not (password1 and password1 == password2):
        print('Password not illegal!')
        return None
    global userAccount
    userAccount = accout
    tmp = dict()
    tmp["category"]=1
    tmp["account"] = accout
    tmp["password"] = password1
    return tmp
#listen的server thread: 用於接收傳進來的資料
class MyServer(socketserver.BaseRequestHandler):
    def handle(self):
        print("\ngot connection from",self.client_address)
        while True:
            conn = self.request
            try:
                data = conn.recv(1024)
            except:
                print("connection problem or connection end")
                break
            if not data: #如果沒有收到東西
                continue
            dataobj = json.loads(data.decode('utf-8'))
            #如果連線客戶端傳送過來的資訊格式是一個列表且註冊標識為False時進行使用者註冊 list[0] account,list[1] password
            if dataobj["category"] == 1 :
                account = dataobj["account"]
                password = dataobj["password"]
                p = dataobj["listening_port"]
                if [account,password,self.client_address[0],p] in others: 
                    break
                others.append([account,password,self.client_address[0],p])
                print(others)
                message = dict()
                for i in others[1:]:
                    tcpCliSock = socket(AF_INET,SOCK_STREAM)
                    #tcpCliSock.bind(IP,Port)
                    tcpCliSock.connect((i[2],i[3]))
                    message["category"] = 3
                    message["others"] = others
                    datastr = json.dumps(message)
                    tcpCliSock.send(datastr.encode('utf-8'))
                    tcpCliSock.close()
                    print("send mutual conn List")
                Send_to_others()
                print("mutual list {}".format(others))
                break

            elif dataobj["category"] == 3:
                print("receive...mutual conn list")
                print(dataobj["others"])
                for i in dataobj["others"]:
                    find = false
                    for j in others:
                        if j[2] == i[2] and j[3] == i[3]:
                            find =true
                            break 
                    if find == false:
                        print("Adding new client")
                        others.append(i)
                        tcpCliSock = socket(AF_INET,SOCK_STREAM)
                        #tcpCliSock.bind(IP,Port)
                        tcpCliSock.connect((j[2],j[3]))
                        datastr = json.dumps(regINfo)
                        tcpCliSock.send(datastr.encode('utf-8'))
                        tcpCliSock.close()
                break
            elif dataobj["category"] == 2:
                if block.same_chain(dataobj["block"]):
                    break
                block.check_mutual_chain(dataobj["block"])
                Send_to_others()
                break
            else:
                print("cannot read message")
                print(dataobj)
                break
#將local chain傳到紀錄所有的client
def Send_to_others():
    for i in others[1:]:
        tcpCliSock = socket(AF_INET,SOCK_STREAM)
        #tcpCliSock.bind(IP,Port)
        tcpCliSock.connect((i[2],i[3]))
        send_block =  dict()
        send_block["category"] = 2
        send_block["block"] = block.chain
        datastr = json.dumps(send_block)
        tcpCliSock.send(datastr.encode('utf-8'))
        tcpCliSock.close()
        print("send message to all...")
#打開server 開始監聽
def open_server(ip , p):
    global IP_a
    global Port
    global regINfo
    regINfo = dict()
    IP_a = ip
    Port = p
    server = socketserver.ThreadingTCPServer((IP_a,Port),MyServer)
    regINfo["category"] = 1
    regINfo["listening_port"] = Port 
    regINfo["account"] = IP_a
    regINfo["password"] = Port
    print('waiting for connection...')
    global others #包含自己 為鏈上所有人的port,ip
    others = []
    others.append([regINfo["account"],regINfo["password"],IP_a,Port]) #加入自己
    print(others)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.start()
    print("Starting Server ......")
#傳入使用者註冊的資料(自己)、(目標的)IP、Port 
def sending_Client(regINfo,tar_ip,tar_port):
    print("Running register")
    tcpCliSock = socket(AF_INET,SOCK_STREAM)
    try:
        tcpCliSock.connect((tar_ip,tar_port))
    except:
        print("cannot connect to client")
        return
    if  regINfo:
        datastr = json.dumps(regINfo)
        tcpCliSock.send(datastr.encode('utf-8'))
        print("send to target")
    tcpCliSock.close()
#傳入 經緯度、附帶的訊息、聯絡方式(建立新的BLOCK)
#多傳入timestamp
def Send_help(location,Text,contact,timestemp):
    message = dict()
    message["Location"] = location
    message["Text"] = Text
    message["Contact"] = contact
    # t = time.localtime()
    # result = time.strftime("%m/%d/%Y,%H:%M:%S", t)
    message["Timestamp"] = timestemp
    message["Account"] = regINfo["account"]
    message["Password"] = regINfo["password"]
    block.new_message(message)
    if len(block.chain) == 0 :
        block.new_block(false)
    else: block.new_block(false,block.show_block()[-1]["hash"])
    Send_to_others()#傳給其他人lOCAL BLOCKCAHIN
    return
#傳入第幾個BLOCK(在BLOCK上加帶確認接受)
def Accept(index):
    index = int(index)
    if block.check_hash_all() != true:
        return block.check_hash_all()# return places with mistake
    if block.chain[index]["accept"] == "true":
        print("The task has already been accepted by other")
        return
    block.chain[index]["accept"] = "true"
    block.chain[index]["accept_info"] = others[0] #自己的account password port ip
    Send_to_others()
    return

def main():
    global quit
    quit = false
    print("alert: press R while server function block the register")
    # I= input("Enter your IP: ")
    # P= int(input("Port you want to listen: "))
    #自動偵測IP位置
    # I = "127.0.0.1"
    temps = socket(AF_INET, SOCK_DGRAM)
    temps.connect(("8.8.8.8", 80))
    I = temps.getsockname()[0]
    temps.close()

    #自動偵測空Port
    temps = socket()
    temps.bind(('', 0))
    P = temps.getsockname()[1]

    open_server(I,P)
    if(regINfo == None):
        return
    print(regINfo)
    global block
    block = Blockchain()
    while true:    
        com =input("Command: ") 
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
            t = time.time()
            Send_help({"latitude":latitude, "longtitude":longtitude},Text,contact,t)
        elif com == 'accept':
            index = input("Accept index")
            Accept(index)
        elif com == 'R':
            continue
        elif com == 'Quit':
            quit = true
            break
        else: 
            print("wrong command")
            continue
    

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
        data_dict = json.loads(request.get_data())
        #前端給的json資料放入Send_help
        Send_help(data_dict["location"], data_dict["message"], data_dict["contact"], data_dict["timestamp"])
        return Response('123', status=(200))

@app.route('/post_problem_resolve', methods=['POST', 'OPTIONS'])
@cross_origin()
def post_problem_resolve():
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
        data_dict = json.loads(request.get_data())
        return Response('123', status=(200))


if __name__ == '__main__':
    main()
    app.run(host='127.0.0.1',port=21, debug=True, use_reloader=False)