import socket
from tkinter import *

ServerIP='127.0.0.1'
port = 4500


class FTPClient():
    def __init__(self):
        self.conSoc=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.loggedIn=False
        self.open=True
        self.dataSoc=None
        self.passiveIP=None
        self.passivePort=None
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
        elif (command=='TYPE'):
            self.TYPE()
        elif (command=='MODE'):
            self.MODE()
        elif (command=='STRU'):
            self.STRU()
        elif (command=='RETR'):
            self.RETR()
        elif (command=='STOR'):
            self.STOR()
        elif (command=='NOOP'):
            self.NOOP()     
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
            return

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

        self.dataSoc=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.dataSoc.bind((ip,(int(portNo))))

        message='PORT '+sequence+'\r\n'
        print('C %s'%message)
        self.conSoc.sendall(message.encode('ascii'))
        serverResp=self.conSoc.recv(1024).decode('ascii')
        print('S %s'%serverResp)
        if(serverResp.startswith('5')):
            print('Error with parameters, retuning to menu..')
        return    

    def RETR(self):#stream--server will close connection, block-- eof block will be sent
        if(self.passiveIP==None and self.dataSoc==None):
            print('No data connection was set up')
            return
        
        filename=input('Input filename\n')
        message='RETR '+filename+'\r\n'
        print('C %s'%message)
        self.conSoc.sendall(message.encode('ascii'))
        serverResp=self.conSoc.recv(1024).decode('ascii')
        print('S %s'%serverResp)

        if(self.dataSoc!=None):##Assume active
            self.dataSoc.listen()
            s1,addr=self.dataSoc.accept()
            newFile=open('new_'+filename,'wb')

            while 1:
                data=s1.recv(1024)
                if (not data): break##meaning the connection is closed in an 'orderly' way
                newFile.write(data)
            
            newFile.close()        
            print('Transfer complete')
            
            serverResp=self.conSoc.recv(1024).decode('ascii')
            print('S %s'%serverResp)
            self.CloseDataSocket()
            return

        if(self.passiveIP!=None):##Assume Passive

            self.dataSoc.close()
            self.dataSoc=None
            return

    def STOR(self):
        if(self.passiveIP==None and self.dataSoc==None):
            print('No data connection was set up')
            return
        
        filename=input('Input filename\n')
        
        filenameOnServer=input('Called on server?\n')
        message='STOR '+filenameOnServer+'\r\n'
        print('C %s'%message)
        self.conSoc.sendall(message.encode('ascii'))
        serverResp=self.conSoc.recv(1024).decode('ascii')
        print('S %s'%serverResp)

        if(self.dataSoc!=None):##Assume active

            self.dataSoc.listen()
            s1,addr=self.dataSoc.accept()

            with open(filename,'rb') as f:##read as binary
                toSend=f.read(1024)#using send for now instead of sendall
                while (toSend):
                    s1.send(toSend)
                    toSend=f.read(1024)
            
            s1.shutdown(socket.SHUT_RDWR)
            s1.close()
  
            serverResp=self.conSoc.recv(1024).decode('ascii')
            print('S %s'%serverResp)
  

            self.CloseDataSocket()
            return

        if(self.passiveIP!=None):##Assume Passive
            self.dataSoc.close()
            self.dataSoc=None
            return
 
    def TYPE(self):
        type=''
        while(len(type)!=1):
            type=input('Type?\n')
        message='TYPE '+type+'\r\n'
        print('C %s'%message)
        self.conSoc.sendall(message.encode('ascii'))
        serverResp=self.conSoc.recv(1024).decode('ascii')
        print('S %s'%serverResp)
        return


    def MODE(self):
        return

    def STRU(self):
        return

    def NOOP(self):
        message='NOOP\r\n'
        print('C %s'%message)
        self.conSoc.sendall(message.encode('ascii'))
        serverResp=self.conSoc.recv(1024).decode('ascii')
        print('S %s'%serverResp)
        return
    def CloseDataSocket(self):
        #self.dataSoc.shutdown(socket.SHUT_RDWR)
        self.dataSoc.close()
        self.dataSoc=None
        return
    

thisClient=FTPClient()

       
# window = Tk()
# window.title("FTP Client") 
# window.geometry('640x480')
# btn = Button(window, text="Login",command=thisClient.login)
# btn.grid(column=1, row=0)
# window.mainloop()
    


thisClient.run()