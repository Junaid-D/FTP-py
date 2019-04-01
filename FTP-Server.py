import socket
import threading
import time
import os

host = '127.0.0.1'
port = 4500

class myThread (threading.Thread):
    def __init__(self, threadID,conSoc,dest):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.conSoc=conSoc
        self.dest=dest
        self.user=''
        self.password=''
        self.open=True
        self.authorized=False
        self.dataSoc=None
        self.activeIP=None
        self.activePort=None
        self.structure='File'
        self.type='A'
    def run(self):
        self.runServer()
     

    def verifyUser(self):
        return True    

    def runServer(self):

        if(self.authorized==False):#greeting
            self.USER()
        if(self.authorized==True):
            while 1 & self.open==True:
                rec_data=self.conSoc.recv(1024)
                decoded=rec_data.decode('ascii')
                if not rec_data:
                    break     

                receivedData=self.parseCommand(decoded)    
                print("Received",receivedData)
                if receivedData[0]=='QUIT':
                    self.QUIT()
                if receivedData[0]=='PORT':
                    self.PORT(receivedData[1])
                if receivedData[0]=='NOOP':
                    self.NOOP()
                if receivedData[0]=='RETR':
                    self.RETR(receivedData[1])
                if receivedData[0]=='TYPE':
                    self.TYPE(receivedData[1])
                if receivedData[0]=='STOR':
                    self.STOR(receivedData[1])



    print('Server is shutting down.')                

    def parseCommand(self,recCommand):
        splitStr=recCommand[:-2]
        splitStr=splitStr.split(' ',3)
        if len(splitStr) == 1:
            return [splitStr[0],'']
        return splitStr
            
    def USER(self):
        greeting= '220 Service ready for new user\r\n'
        self.conSoc.sendall(greeting.encode('ascii'))
        rec_data=self.conSoc.recv(1024)
        response=self.parseCommand(rec_data.decode('ascii'))
        print('C %s'%response)
        self.user=response[1]
        if(self.verifyUser()==True):
            self.authorized=True
            response = '200 User logged in, proceed.\r\n'
            self.conSoc.sendall(response.encode('ascii'))

    def QUIT(self):
        response='221 Service closing control connection\r\n'
        self.conSoc.sendall(response.encode('ascii'))
        self.open=False

    def PORT(self,args):
        splitArgs=args.split(',')
        if(len(splitArgs)!=6):
            response='501 Syntax error in parameters or arguments\r\n'
            self.conSoc.sendall(response.encode('ascii'))
        response = '200 Creating data socket\r\n'   
        self.conSoc.sendall(response.encode('ascii')) 
        ip=splitArgs[0]+'.'+splitArgs[1]+'.'+splitArgs[2]+'.'+splitArgs[3]
        port=int(splitArgs[4])*256+int(splitArgs[5])
        self.dataSoc=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.activeIP=ip
        self.activePort=port
        #do not use data port immediately
    
    def NOOP(self):
        response = '200 NOOP Done\r\n'
        self.conSoc.sendall(response.encode('ascii'))

    def TYPE(self,newType):
        types=['A','E','I','L']
        if(newType not in types):
            response='501 Invalid Type\r\n'
            self.conSoc.sendall(response.encode('ascii'))
            return

        self.type=newType
        response = '200 Type Altered\r\n'
        self.conSoc.sendall(response.encode('ascii'))

    def STOR(self,filename):
        ###active
        if(self.activeIP!=''):
            transferAccept='250 Accepted\r\n'
            self.conSoc.sendall(transferAccept.encode('ascii'))

            self.dataSoc=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.dataSoc.connect((self.activeIP,self.activePort))

            newFile=open('new_onserver_'+filename,'wb')
            while 1:
                data=self.dataSoc.recv(1024)
                if (not data): break##meaning the connection is closed in an 'orderly' way
                newFile.write(data)
            
            newFile.close()        

            self.CloseDataSoc()
            self.activeIP=''
            self.activePort=0
            doneTransfer='226 Done upload\r\n'
            self.conSoc.sendall(doneTransfer.encode('ascii'))

        ###PASSIVE
        if (self.dataSoc is not None):
            print('dosomething')

        return
    
    def RETR(self,filename):
        
        ###active
        if(self.activeIP!=''):
            transferAccept='250 Accepted\r\n'
            self.conSoc.sendall(transferAccept.encode('ascii'))

            self.dataSoc=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.dataSoc.connect((self.activeIP,self.activePort))
            with open(filename,'rb') as f:##read as binary
                toSend=f.read(1024)#using send for now instead of sendall
                while (toSend):
                    self.dataSoc.send(toSend)
                    toSend=f.read(1024)
            self.CloseDataSoc()
            self.activeIP=''
            self.activePort=0
            doneTransfer='226 Done download\r\n'
            self.conSoc.sendall(doneTransfer.encode('ascii'))

       ###passive
        if (self.dataSoc is not None):
            print('dosomething')
        

    def CloseDataSoc(self):
        self.dataSoc.shutdown(socket.SHUT_RDWR)
        self.dataSoc.close()
        self.dataSoc=None
        return

                

with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as soc:
    #welcoming socket
    soc.bind((host,port))
    soc.listen(5)
 
    #open new conenction socket
    while 1:
        s1,addr = soc.accept()
        print("New Client at: %s"%str(addr))
        threadi=myThread(0,s1,addr)
        threadi.start()
