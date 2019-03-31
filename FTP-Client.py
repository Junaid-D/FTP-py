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
        


thisClient=FTPClient()
thisClient.run()