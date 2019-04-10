import socket
import threading
import time
import os
import csv
from datetime import datetime
import random

host = '127.0.0.1'
port = 4500

class myThread (threading.Thread):
    def __init__(self, threadID,conSoc,dest):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.conSoc=conSoc
        self.dest=dest
        self.user=''
        self.portRange=2048
        self.password=''
        self.open=True
        self.authorized=False
        self.dataSoc=None
        self.activeIP=None
        self.activePort=None
        self.passiveIP=None
        self.passivePort=None
        self.structure='File'
        self.type='b'
        self.credentials=None
        self.currentPath=os.getcwd()
        self.transferMode='S'
    def run(self):
        self.runServer()
     

    def verifyUser(self):
        if((self.user,self.password) in self.credentials):
            self.authorized=True
        else:
            self.authorized=False
        

    def runServer(self):

        self.ReadCredentials()

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
                elif receivedData[0]=='PORT':
                    self.PORT(receivedData[1])
                elif receivedData[0]=='NOOP':
                    self.NOOP()
                elif receivedData[0]=='RETR':
                    self.RETR(receivedData[1])
                elif receivedData[0]=='TYPE':
                    self.TYPE(receivedData[1])
                elif receivedData[0]=='STOR':
                    self.STOR(receivedData[1])
                elif receivedData[0]=='SYST':
                    self.SYST()
                elif receivedData[0]=='FEAT':
                    self.FEAT()
                elif receivedData[0]=='PWD':
                    self.PWD()
                elif receivedData[0]=='LIST':
                    self.LIST(receivedData[1])
                elif receivedData[0]=='PASV':
                    self.PASV()
                elif receivedData[0]=='CWD':
                    self.CWD(receivedData[1])
                else:
                    self.UNKNOWN()

        print('Server is shutting down.')    


    def UNKNOWN(self):
        message='502 Command not implemented\r\n'
        self.conSoc.sendall(message.encode('ascii'))               

    def parseCommand(self,recCommand):
        splitStr=recCommand[:-2]
        splitStr=splitStr.split(' ',3)
        if len(splitStr) == 1:
            return [splitStr[0],'']
        return splitStr

    def ReadCredentials(self):
        with open('logins.txt') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            self.credentials=[('ADMIN','ADMIN')]
            for row in csv_reader:
                self.credentials.append((row[0],row[1]))
        print(self.credentials)

    def USER(self):
        greeting= '220 Service ready for new user\r\n'
        self.conSoc.sendall(greeting.encode('ascii'))
        rec_data=self.conSoc.recv(1024)
        response=self.parseCommand(rec_data.decode('ascii'))
        print('C %s'%response)
        self.user=response[1]

        response = '331 Need Password\r\n'
        self.conSoc.sendall(response.encode('ascii'))

        self.PASS()

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
        self.activeIP=ip
        self.activePort=port
        #do not use data port immediately
    def PASV(self):
        print('Initiating passive data port')
        self.passiveIP=host
        self.passivePort=random.randint(1024,self.portRange)
        splitIP=host.split('.')
        port1=int(self.passivePort)//256
        port2=int(self.passivePort)%256
        #ip
        sequence=splitIP[0]+','+splitIP[1]+','+splitIP[2]+','+splitIP[3]    
        #port
        sequence=sequence+','+str(port1)+','+str(port2)
        
        self.dataSoc=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.dataSoc.bind((self.passiveIP,self.passivePort))
        message='227  Entering Passive Mode '+sequence+'\r\n'

        self.conSoc.sendall(message.encode('ascii'))

    def NOOP(self):
        response = '200 NOOP Done\r\n'
        self.conSoc.sendall(response.encode('ascii'))

    def TYPE(self,newType):
        types=['A','I']
        if(newType not in types):
            response='501 Invalid Type\r\n'
            self.conSoc.sendall(response.encode('ascii'))
            return
        if(newType=='A'):
            self.type=''
        else:
            self.type='b'

        response = '200 Type Altered\r\n'
        self.conSoc.sendall(response.encode('ascii'))

    def STOR(self,filename):
        ###active
        if(self.activeIP is not None):
            try:
                newFile=open('new_onserver_'+filename,"w"+self.type)
            except:
                errorMsg='426 Connection closed; transfer aborted.\r\n'
                self.conSoc.send(errorMsg.encode('ascii'))  
                self.CloseDataSoc()
                self.activeIP=None
                self.activePort=None
                return

            transferAccept='250 Accepted\r\n'
            self.conSoc.sendall(transferAccept.encode('ascii'))

            self.dataSoc=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.dataSoc.connect((self.activeIP,self.activePort))
            
            newFile=open('new_onserver_'+filename,"w"+self.type)
            while 1:
                data=self.dataSoc.recv(1024)
                if (not data): break##meaning the connection is closed in an 'orderly' way
                if (self.type==''): data=data.decode('ascii')
                newFile.write(data)
            
            newFile.close()  
            self.CloseDataSoc()
            self.activeIP=None
            self.activePort=None
            return

        ###PASSIVE
        if (self.dataSoc is not None):
            try:
                newFile=open('new_onserver_'+filename,"w"+self.type)
            except:
                errorMsg='426 Connection closed; transfer aborted.\r\n'
                self.conSoc.send(errorMsg.encode('ascii'))  
                self.CloseDataSoc()
                self.activeIP=None
                self.activePort=None
                return           
            transferAccept='250 Accepted\r\n'
            self.conSoc.sendall(transferAccept.encode('ascii'))

            #self.dataSoc=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            #self.dataSoc.bind((self.passiveIP,self.passivePort))
            self.dataSoc.listen()
            s1,addr=self.dataSoc.accept()

            newFile=open('new_onserver_'+filename,"w"+self.type)
            while 1:
                data=s1.recv(1024)
                if (not data): break##meaning the connection is closed in an 'orderly' way
                if (self.type==''): data=data.decode('ascii')

                newFile.write(data)
            
            newFile.close() 
            self.dataSoc.close()
            self.dataSoc=None 
            self.passiveIP=None
            self.passivePort=None
            return

        noDataCon='425 Create Data connection first\r\n'
        self.conSoc.sendall(noDataCon.encode('ascii'))
        return
    
    def RETR(self,filename):
        
        filename=self.currentPath+'\\'+filename
        ###active
        if(self.activeIP is not None):
            transferAccept='250 Accepted\r\n'
            self.conSoc.sendall(transferAccept.encode('ascii'))

            self.dataSoc=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.dataSoc.connect((self.activeIP,self.activePort))
            with open(filename,"r"+self.type) as f:##read as binary                if(self.transferMode=="S")
                if(self.transferMode=='S'):
                    toSend=f.read(1024)#using send for now instead of sendall
                    while (toSend):
                        if (self.type==''): toSend=toSend.encode('ascii')
                        self.dataSoc.send(toSend)
                        toSend=f.read(1024)
                elif(self.transferMode=='B'):
                    toSend=f.read(1024)#using send for now instead of sendall
                    while (toSend):
                        if (self.type==''): toSend=toSend.encode('ascii')
                        self.dataSoc.send(toSend)
                        toSend=f.read(1024)
                elif(self.transferMode=='C'):
                    toSend=f.read(1024)#using send for now instead of sendall
                    while (toSend):
                        if (self.type==''): toSend=toSend.encode('ascii')
                        self.dataSoc.send(toSend)
                        toSend=f.read(1024)
            self.CloseDataSoc()
            self.activeIP=None
            self.activePort=None

       ###passive
        if (self.dataSoc is not None):
            transferAccept='250 Accepted\r\n'
            self.conSoc.sendall(transferAccept.encode('ascii'))

    
            self.dataSoc.listen()
            s1,addr=self.dataSoc.accept()
           
            with open(filename,"r"+self.type) as f:##read as binary
                if(self.transferMode=='S'):
                    toSend=f.read(1024)#using send for now instead of sendall
                    while (toSend):
                        if (self.type==''): toSend=toSend.encode('ascii')
                        s1.send(toSend)
                        toSend=f.read(1024)
                elif(self.transferMode=='B'):
                    toSend=f.read(1024)#using send for now instead of sendall
                    while (toSend):
                        if (self.type==''): toSend=toSend.encode('ascii')
                        s1.send(toSend)
                        toSend=f.read(1024)
                elif(self.transferMode=='C'):
                    toSend=f.read(1024)#using send for now instead of sendall
                    while (toSend):
                        if (self.type==''): toSend=toSend.encode('ascii')
                        s1.send(toSend)
                        toSend=f.read(1024)            
            self.dataSoc.close()
            self.dataSoc=None
            self.passiveIP=None
            self.passivePort=None
            return

        ##nothing
        noDataCon='425 Create Data connection first\r\n'
        self.conSoc.sendall(noDataCon.encode('ascii'))
        

    def CloseDataSoc(self):
        self.dataSoc.shutdown(socket.SHUT_RDWR)
        self.dataSoc.close()
        self.dataSoc=None
        return

    def SYST(self):
        response='200 Windows\r\n'
        self.conSoc.sendall(response.encode('ascii'))   

    def FEAT(self):
        response='211 RETR PORT\r\n'
        self.conSoc.sendall(response.encode('ascii'))     
    
    def PASS(self):
        rec_data=self.conSoc.recv(1024)
        response=self.parseCommand(rec_data.decode('ascii'))
        print('C ',response)
        if(response[0]!='PASS'):
            response='530 Not logged in\r\n'
            self.conSoc.sendall(response.encode('ascii'))
            return
        self.password=response[1]
        self.verifyUser()
        if(self.authorized):
            response='200 Success\r\n'
            self.conSoc.sendall(response.encode('ascii'))
        else:
            response='430 Invalid login\r\n'
            self.conSoc.sendall(response.encode('ascii'))
         
    def PWD(self):
        path = self.currentPath
        response='257 "'+path+'" returned path.\r\n'
        self.conSoc.sendall(response.encode('ascii'))
        return

    def LIST(self,args):
        
        if(args==''):
            files=os.listdir(self.currentPath)
            print(files)
            
            toSend=''
            for file in files:
                fullpath=self.currentPath+'\\'+ file
                fileInfo=os.stat(fullpath)
                #bin/ls format
                prefix=''
                if(os.path.isdir(fullpath)):
                    prefix='drwxr-xr-x 1'
                else:
                   prefix= '-rw-r--r-- 1'
                line = [
                prefix,
                'def',
                'def',
                str(fileInfo.st_size),
                '\t',
             #   datetime.utcfromtimestamp(fileInfo.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                '\t',
                str(file),
                '\r\n'
                ]
                
                lineStr=' '.join(line)
                print(lineStr)
                toSend+=lineStr

            ##active
            if(self.activeIP is not None):
                print('List sent')
                transferAccept='226 Accepted\r\n'
                self.conSoc.sendall(transferAccept.encode('ascii'))

                self.dataSoc=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                self.dataSoc.connect((self.activeIP,self.activePort))

                self.dataSoc.sendall(toSend.encode('ascii'))
                  
                self.CloseDataSoc()
                self.activeIP=None
                self.activePort=None
                return
            ##passive
            if (self.dataSoc is not None):
                transferAccept='250 Accepted\r\n'
                self.conSoc.sendall(transferAccept.encode('ascii'))

        
                self.dataSoc.listen()
                s1,addr=self.dataSoc.accept()
                s1.sendall(toSend.encode('ascii'))


                s1.shutdown(socket.SHUT_RDWR)
                s1.close()
                self.dataSoc.close()
                self.dataSoc=None
                self.passiveIP=None
                self.passivePort=None
                return
            
            ##nothing
            noDataCon='425 Create Data connection first\r\n'
            self.conSoc.sendall(noDataCon.encode('ascii'))


        
        return

    def CWD(self,newWd):
        if('\\' not in newWd):#if not full path sent
            newWd=self.currentPath+'\\'+newWd

        if(os.path.isdir(newWd) ):
            self.currentPath=newWd
            print('Newpath',self.currentPath)
            response='200 directory changed to+'+ newWd+'\r\n'
            self.conSoc.send(response.encode('ascii'))
            return
        else:## pwd doesnt exist
            response='550 Requested action not taken\r\n'
            self.conSoc.send(response.encode('ascii'))


        return
    def MODE(self,newMode):
        modes=['S','B','C']
        if(newMode not in modes):
            response='501 Invalid Mode\r\n'
            self.conSoc.sendall(response.encode('ascii'))
            return
        self.transferMode=newMode
        response = '200 Mode Altered\r\n'
        self.conSoc.sendall(response.encode('ascii'))
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

