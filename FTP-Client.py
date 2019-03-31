import socket

ServerIP='127.0.0.1'
port = 4500


class FTPClient():
    def __init__(self):
        self.conSoc=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.loggedIn=False
    def run(self):
        self.conSoc.connect((ServerIP,port))
        serverResp=''
        while(serverResp==''):
            serverResp=self.conSoc.recv(1024).decode('ascii')

        print('S %s' % serverResp)
        if(serverResp.startswith('220')):
            self.login()
        if(self.loggedIn==True):
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
            print("Login success!")

    def parseCommand(self,command):
        


thisClient=FTPClient()
thisClient.run()