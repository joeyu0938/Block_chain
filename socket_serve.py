from email.headerregistry import Address
from multiprocessing import Lock
from socket import *
import socketserver
import string
from telnetlib import IP
import threading,sys,json,re
from sqlalchemy import false, true
from blockChain import Blockchain
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
        "Location": {
            "Latitude": 24.941764,
            "Longitude": 121.367751,
            "Other": ""
        },
        "Text": "Need some water",
        "Timestamp": 1650635046,
        "Contact": "+886987654321"
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
                for i in dataobj["others"]:
                    find = false
                    for j in others[1:]:
                        if j[2] == i[2] and j[3] == i[3]:
                            find =true
                            break
                    if find == false and (i[2]!= IP_a and i[3]!= Port):
                        print("Adding new client")
                        tcpCliSock = socket(AF_INET,SOCK_STREAM)
                        #tcpCliSock.bind(IP,Port)
                        tcpCliSock.connect((j[2],j[3]))
                        datastr = json.dumps(regINfo)
                        tcpCliSock.send(datastr.encode('utf-8'))
                        tcpCliSock.close()
                break
            elif dataobj["category"] == 2:
                #create new message block 
                break
            else:
                print("cannot read message")
                print(dataobj)
                break


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

def main():
    print("alert: press Y while server function block the register")
    global regINfo
    regINfo = register()
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
        elif com == 'Show other':
            print(others)
        

if __name__ == '__main__':
    main()


                    
                