from socket import *
import socketserver
import threading,sys,json,re
from sqlalchemy import false, true
from blockChain import Blockchain 
import time
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
def open_server():
    global IP_a
    global Port
    IP_a = input("Enter your IP: ")
    Port = int(input("Port you want to listen: "))
    server = socketserver.ThreadingTCPServer((IP_a,Port),MyServer)
    regINfo["listening_port"] = Port 
    print('waiting for connection...')
    print(regINfo)
    global others #包含自己 為鏈上所有人的port,ip
    others = []
    others.append([regINfo["account"],regINfo["password"],IP_a,Port]) #加入自己
    print(others)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.start()
    print("Starting Server ......")

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

def Send_help(latitude,longtitude,Text,contact):
    message = dict()
    message["Location"] = dict()
    message["Location"]["Latitude"] = latitude
    message["Location"]["Longitude"] = longtitude
    message["Text"] = Text
    message["Contact"] = contact
    t = time.localtime()
    result = time.strftime("%m/%d/%Y,%H:%M:%S", t)
    message["Timestamp"] = result
    block.new_message(message)
    if len(block.chain) == 0 :
        block.new_block(false)
    else: block.new_block(false,block.show_block()[-1]["hash"])
    Send_to_others()
    return

def Accept(index):
    if block.check_hash_all() != true:
        return block.check_hash_all()# return places with mistake
    if block.chain[index]["accept"] == true:
        print("The task has already been accepted by other")
        return
    block.chain[index]["accept"] = true
    block.chain[index]["accept_info"] = others[0] #自己的account password port ip
    tcpCliSock = socket(AF_INET,SOCK_STREAM)
    Send_to_others()
    return

def main():
    print("alert: press Y while server function block the register")
    global regINfo
    regINfo = register()
    global block
    block = Blockchain()
    if(regINfo == None):
        return
    print(regINfo)
    open_server()
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
            Send_help(latitude,longtitude,Text,contact)
        elif com == 'accept':
            index = input("Accept index")
            Accept(index)
        else: 
            print("wrong command")
            continue

if __name__ == '__main__':
    main()