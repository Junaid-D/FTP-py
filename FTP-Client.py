import socket

ServerIP='127.0.0.1'
port = 4500


class FTPClient():
    def __init__(self):
        self.conSoc=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.loggedIn=False
        self.open=True

    def run(self):
        self.conSoc.connect((ServerIP,port))
        serverResp=''
        while(serverResp==''):
            serverResp=self.conSoc.recv(1024).decode('ascii')

        print('S %s' % serverResp)
        if(serverResp.startswith('220')):
            self.login()
        if(self.loggedIn==True):
            while 1 & self.open==True:
                command=input('Input next command..')
                self.parseCommand(command)


                



    def login(self):
        #serverResp=self.conSoc.recv(1024).decode('ascii')
       # print('S %s' % serverResp)
        userName=input("type username..")
        loginMessage='USER '+userName+'\r\n'
        print('C %s' % loginMessage)
        self.conSoc.sendall(loginMessage.encode('ascii'))
        serverResp=self.conSoc.recv(1024).decode('ascii')
        print('S %s' % serverResp)
        if(serverResp.startswith('200')):
            self.loggedIn=True
            print("Login success!")

    def parseCommand(self,command):
        if (command=='QUIT'):
            self.QUIT() 
        elif (command=='PORT'):
                self.PORT()
        else:
            print('Invalid Command')

    def QUIT(self):  
        message='QUIT\r\n'
        print('C %s'%message)
        self.conSoc.sendall(message.encode('ascii'))
        serverResp=self.conSoc.recv(1024).decode('ascii')
        print('S %s'%serverResp)
        if(serverResp.startswith('221')):
            self.open=False
            print('Connection closed by server.')
            self.conSoc.close()

    def PORT(self):
        print('Requesting data port')
        ip=''
        while ip.count('.')!=3:
            ip=input('IP use . as separator?\n')
        splitIP=ip.split('.')
        portNo=input('Port no: ?\n')
        port1=int(portNo)//256
        port2=int(portNo)%256
        #ip
        sequence=splitIP[0]+','+splitIP[1]+','+splitIP[2]+','+splitIP[3]    
        #port
        sequence=sequence+','+str(port1)+','+str(port2)
        message='PORT '+sequence+'\r\n'
        print('C %s'%message)
        self.conSoc.sendall(message.encode('ascii'))
        


thisClient=FTPClient()
thisClient.run()