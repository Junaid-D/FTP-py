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
    def __init__(self, threadID,conSoc,dest):#initialises relevenat server variables , written by both
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.conSoc=conSoc
        self.dest=dest
        self.user=''
        self.portRange=[50000,60000]
        self.password=''
        self.open=True
        self.authorized=False
        self.dataSoc=None
        self.activeIP=None
        self.activePort=None
        self.passiveIP=None
        self.passivePort=None
        self.structure='File'
        self.type=''
        self.credentials=None
        self.textExtensions=None
        self.currentPath=os.getcwd()
        self.corePath=self.currentPath
        self.transferMode='S'
    def run(self):
        self.runServer()
     

    def verifyUser(self): #user authentication #This was written by Junaid Dawood 1094837
        if((self.user,self.password) in self.credentials):#checks if the users details are present in the authentication file
            self.authorized=True
        else:
            self.authorized=False
        

    def runServer(self):#server loop
        greeting= '220 Service ready for new user\r\n'
        self.conSoc.sendall(greeting.encode('ascii'))

        self.ReadCredentials()#initialises the credentials
        self.ReadExtensions()#initialises the extension for automatic type management
        while(self.open==True):
            if(self.authorized==False):#greeting
                self.USER()#attempt to authenticate user
                
            if(self.authorized==True):
                while 1 & self.open==True:
                    rec_data=self.conSoc.recv(1024)#establishes control connection
                    decoded=rec_data.decode('ascii')
                    if not rec_data:
                        break     

                    receivedData=self.parseCommand(decoded)    #parses command to be used
                    print("Received",receivedData)
                    if receivedData[0]=='QUIT':#This was written by both students
                        self.QUIT()
                    elif receivedData[0]=='PORT':
                        self.PORT(receivedData[1])
                    elif receivedData[0]=='STRU':
                        self.STRU(receivedData[1])
                    elif receivedData[0]=='MODE':
                        self.MODE(receivedData[1])
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
                    elif receivedData[0]=='MKD':
                        self.MKD(receivedData[1])
                    else:
                        self.UNKNOWN()#if command not implemented


    def UNKNOWN(self):#alerts that command requested is not implemented #This was written by Junaid Dawood 1094837
        message='502 Command not implemented\r\n'
        self.conSoc.sendall(message.encode('ascii'))               

    def parseCommand(self,recCommand):#parses command #This was written by Junaid Dawood 1094837
        splitStr=recCommand[:-2]#removes eol characters
        splitStr=splitStr.split(' ',3)
        splitStr[0]=splitStr[0].upper()
        if len(splitStr) == 1:
            return [splitStr[0],'']
        return splitStr

    def ReadCredentials(self):#load credentials file and place result in variable #This was written by Junaid Dawood 1094837
        with open('logins.txt') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            self.credentials=[('ADMIN','ADMIN')]#adds default admin profile
            for row in csv_reader:
                self.credentials.append((row[0],row[1]))
        print(self.credentials)

    def ReadExtensions(self):#load extensions file and place result in variable, written by Xongile Nghatsane 1110680
        with open('extensions.txt') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            self.textExtensions=['.txt']#adds default text extension
            for extList in csv_reader:
                for ext in extList:
                    self.textExtensions.append(ext)

    def CheckExtension(self,file):#checks if extension is of text based document, written by Xongile Nghatsane 1110680

        if(self.type=='b'):##binary should be compatible with all
            return True

        name,ext=os.path.splitext(file)
        return (ext in self.textExtensions)

    def SendExtension(self,soc):#sends extensions to user to configure type , written by Xongile Nghatsane 1110680
        for ext in self.textExtensions:
            toSend=ext
            toSend=toSend.encode('ascii')
            soc.send(toSend)

    def USER(self):#gets username and stores in variable #This was written by Junaid Dawood 1094837
        rec_data=self.conSoc.recv(1024)
        response=self.parseCommand(rec_data.decode('ascii'))
        print('C %s'%response)
        self.user=response[1]

        response = '331 Need Password\r\n'
        self.conSoc.sendall(response.encode('ascii'))

        self.PASS()


    def PASS(self):#gets userpass for checking authentication #This was written by Junaid Dawood 1094837
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
            if(self.user!='ADMIN'):#if user is not admin, limits user to only their folder
                self.currentPath+='\\' +self.user
                self.corePath=self.currentPath
        else:
            response='430 Invalid login\r\n'
            self.conSoc.sendall(response.encode('ascii'))

    def QUIT(self):#closes connection #This was written by Junaid Dawood 1094837
        response='221 Service closing control connection\r\n'
        self.conSoc.sendall(response.encode('ascii'))
        self.open=False
        print('Server is shutting down for user %s'%self.user)    


    def PORT(self,args):#sets the server into active mode #This was written by Junaid Dawood 1094837
        splitArgs=args.split(',')
        if(len(splitArgs)!=6):#checks if input is valid
            response='501 Syntax error in parameters or arguments\r\n'
            self.conSoc.sendall(response.encode('ascii'))
        response = '200 Creating data socket\r\n'   
        self.conSoc.sendall(response.encode('ascii')) 
        ip=splitArgs[0]+'.'+splitArgs[1]+'.'+splitArgs[2]+'.'+splitArgs[3]
        port=int(splitArgs[4])*256+int(splitArgs[5])#parses IP and port to desired format
        self.activeIP=ip
        self.activePort=port
        #do not use data port immediately

    def PASV(self):#sets the server into passive mode, written by Xongile Nghatsane 1110680
        print('Initiating passive data port')
        self.passiveIP=host
        self.passivePort=random.randint(self.portRange[0],self.portRange[1])#obtains random port from a range
        splitIP=host.split('.')
        port1=int(self.passivePort)//256
        port2=int(self.passivePort)%256
        #ip
        sequence=','.join(splitIP)  #formats IP and port in set format for transmission
        #port
        sequence=sequence+','+str(port1)+','+str(port2)
        print(sequence)
        self.dataSoc=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.dataSoc.bind((self.passiveIP,self.passivePort))#binds new data socket to listen from client
        message='227 Entering Passive Mode '+ sequence+'\r\n'
            
        self.conSoc.sendall(message.encode('ascii'))#sends relevant information to client

    def NOOP(self):#no operation #This was written by Junaid Dawood 1094837
        response = '200 NOOP Done\r\n'
        self.conSoc.sendall(response.encode('ascii'))

    def TYPE(self,newType):#determines the type of encoding used, written by Xongile Nghatsane 1110680
        newType=newType.upper()
        types=['A','I']#types are ascii for text based documents and binary for everything else
        if(newType not in types):
            permitted=['A','I','E','L']#checks all types specified in standard but not implemented
            if(newType in permitted):
                response='504 Command not implemented for that parameter\r\n'
                self.conSoc.sendall(response.encode('ascii'))
                return
            else:
                response='501 Invalid type given\r\n'
                self.conSoc.sendall(response.encode('ascii'))
                return 
        if(newType=='A'):
            self.type=''
        else:
            self.type='b'

        response = '200 Type Altered\r\n'
        self.conSoc.sendall(response.encode('ascii'))#sends appropriate response

    def STOR(self,filename):#allows client to send to and store files on the server 
        if(filename==''):#ensures valid filename
            fileErr='501 No filename given\r\n'
            self.conSoc.sendall(fileErr.encode('ascii'))
            return
        if(self.CheckExtension(filename)==False):#ensures type is ascii only for established extensions
            encodingError='550 Incompatible type encoding.\r\n'
            self.conSoc.sendall(encodingError.encode('ascii'))
            return
    #error checking was written by Junaid Dawood 1094837

        ###active #This was written by Junaid Dawood 1094837
        if(self.activeIP is not None):#checks if active is set up.
            try:
                newFile=open(self.currentPath+'\\'+'new_onserver_'+filename,"w"+self.type)#checks if file can be created
            except:
                errorMsg='426 Connection closed (file error); transfer aborted.\r\n'
                self.conSoc.send(errorMsg.encode('ascii'))  
                self.CloseDataSoc()
                self.activeIP=None
                self.activePort=None
                return

            transferAccept='250 Accepted\r\n'
            self.conSoc.sendall(transferAccept.encode('ascii'))

            self.dataSoc=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.dataSoc.connect((self.activeIP,self.activePort))#connects to client socket to request data
            
            newFile=open(self.currentPath+'\\'+'new_onserver_'+filename,"w"+self.type)
            if(self.transferMode=='S'):
                while 1:
                    data=self.dataSoc.recv(1024)#receives data on data socket
                    if (not data): break##meaning the connection is closed in an 'orderly' way
                    if (self.type==''): data=data.decode('ascii')
                    newFile.write(data)
            newFile.close()  
            self.CloseDataSoc()#close data socket
            self.activeIP=None
            self.activePort=None
            return


        ###PASSIVE written by Xongile Nghatsane 1110680
        if (self.dataSoc is not None):#checks if passive is set up
            try:
                newFile=open(self.currentPath+'\\'+'new_onserver_'+filename,"w"+self.type)
            except:
                errorMsg='426 Connection closed; transfer aborted.\r\n'
                self.conSoc.send(errorMsg.encode('ascii'))  
                self.CloseDataSoc()
                self.activeIP=None
                self.activePort=None
                return           
            transferAccept='250 Accepted\r\n'
            self.conSoc.sendall(transferAccept.encode('ascii'))

        
            self.dataSoc.listen()#sets data socket to listen for connection
            s1,addr=self.dataSoc.accept()#accepts incoming data

            newFile=open(self.currentPath+'\\'+'new_onserver_'+filename,"w"+self.type)
            if(self.transferMode=='S'):
                while 1:
                    data=s1.recv(1024)#receives data on data socket
                    if (not data): break##meaning the connection is closed in an 'orderly' way
                    if (self.type==''): data=data.decode('ascii')
                    newFile.write(data)
            newFile.close() 
            self.dataSoc.close()#close data socket
            self.dataSoc=None 
            self.passiveIP=None
            self.passivePort=None
            return

        ##nothing
        noDataCon='425 Data connection was never created\r\n'#passive and active not set
        self.conSoc.sendall(noDataCon.encode('ascii'))
        #error checking was written by Junaid Dawood 1094837



    
    def RETR(self,filename):#allows user to request data from the server
        if(filename==''):#ensures valid filename
            fileErr='501 No filename given\r\n'
            self.conSoc.sendall(fileErr.encode('ascii'))
            return

        if(self.CheckExtension(filename)==False):#ensures type is ascii only for established extensions
            encodingError='550 Incompatible type encoding.\r\n'
            self.conSoc.sendall(encodingError.encode('ascii'))
            return

        filename=self.currentPath+'\\'+filename

        if(os.path.exists(filename)!=True):#checks if file exists
            fileNotFound='550 File does not exist.\r\n'
            self.conSoc.sendall(fileNotFound.encode('ascii'))
            return

        if(os.path.isfile(filename)!=True):#checks if directory or file
            fileNotFound='550 is a directory, not a file.\r\n'
            self.conSoc.sendall(fileNotFound.encode('ascii'))
            return
            ####early exits

    #error checking was written by Junaid Dawood 1094837

        ###active written by Junaid Dawood 1094837
        if(self.activeIP is not None):#sends data using active connection
            transferAccept='250 Accepted\r\n'
            self.conSoc.sendall(transferAccept.encode('ascii'))

            self.dataSoc=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.dataSoc.connect((self.activeIP,self.activePort))
            with open(filename,"r"+self.type) as f:##read as binary               
                if(self.transferMode=='S'):
                    toSend=f.read(1024)#using send for now instead of sendall
                    while (toSend):
                        if (self.type==''): toSend=toSend.encode('ascii')
                        self.dataSoc.send(toSend)
                        toSend=f.read(1024)
            self.CloseDataSoc()
            self.activeIP=None
            self.activePort=None


       ###passive written by Xongile Nghatsane 1110680
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
            self.dataSoc.close()
            self.dataSoc=None
            self.passiveIP=None
            self.passivePort=None
            return

        ##nothing
        noDataCon='425 Data connection was never created\r\n'
        self.conSoc.sendall(noDataCon.encode('ascii'))
        
    #error checking was written by Junaid Dawood 1094837

    def CloseDataSoc(self):#closes data socket written by Junaid Dawood 1094837
        self.dataSoc.shutdown(socket.SHUT_RDWR)
        self.dataSoc.close()
        self.dataSoc=None
        return

    def SYST(self):#identifies OS server is running on written by Junaid Dawood 1094837
        response='200 Windows\r\n'
        self.conSoc.sendall(response.encode('ascii'))   

    def FEAT(self):#identifies operations user can use; written by Junaid Dawood 1094837 #NB this is not used
        response='211 RETR PORT SYST PWD\r\n'
        self.conSoc.sendall(response.encode('ascii'))     
         
    def PWD(self):#prints current directory #written by Junaid Dawood 1094837
        path = self.currentPath
        response='257 '+path+'\r\n'
        self.conSoc.sendall(response.encode('ascii'))
        return

    def LIST(self,args):#lists files in current or specified directory #written by Junaid Dawood 1094837
        
        if(args==''):
            files=os.listdir(self.currentPath)
            print(files)
        else:
            if(os.path.exists(args)):
                files=os.listdir(args)
                print(files)
                if(self.corePath not in args and self.user!='ADMIN' ):
                    response='530 You do not have permission to access this.\r\n'
                    self.conSoc.sendall(response.encode('ascii'))
                    return
            else: 
                response='501 The directory does not exist \r\n'
                self.conSoc.sendall(response.encode('ascii'))
                return
        
        print('here')
            
        toSend=''
        for file in files:#parses directory information

            if(args==''):
                fullpath=self.currentPath+'\\'+ file
            else:
                fullpath=args+'\\'+file
            fileInfo=os.stat(fullpath)
            #bin/ls format
            prefix=''
            if(os.path.isdir(fullpath)):#tells whether path is directory or file
                prefix='drwxr-xr-x 1'
            else:
                prefix= '-rw-r--r-- 1'
            line = [
            prefix,
            'def',
            'def',
            str(fileInfo.st_size),
            '\t',
            datetime.utcfromtimestamp(fileInfo.st_mtime).strftime('%b \t %d \t %H:%M'),
            '\t',
            str(file),
            '\r\n'
            ]
            
            lineStr=' '.join(line)
            print(lineStr)
            toSend+=lineStr

        ##active 
        if(self.activeIP is not None):#sends data using active connection
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
        if (self.dataSoc is not None):#sends data using passive connection
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
        noDataCon='425 No data connection created\r\n'
        self.conSoc.sendall(noDataCon.encode('ascii'))


        
        return

    def CWD(self,newWd):#change working directory #written by Junaid Dawood 1094837
        if (('..' in newWd) and self.user!='ADMIN' ):#restricts non admins from browsing upwards
            response='530 You do not have permission to access this.\r\n'
            self.conSoc.sendall(response.encode('ascii'))
            return

        if('\\' not in newWd):#if not full path sent
            newWd=self.currentPath+'\\'+newWd
        
        if (self.corePath not in newWd and self.user!='ADMIN' ):#restricts non admins to their folders
            response='530 You do not have permission to access this.\r\n'
            self.conSoc.sendall(response.encode('ascii'))
            return

       

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


    def MODE(self,newMode):# defines mode of transfer. written by Xongile Nghatsane 1110680
        newMode=newMode.upper()
        modes=['S']#only stream transfer mode implemented
        if(newMode not in modes):
            permitted=['S','B','C']
            if(newMode in permitted):
                response='504 Command not implemented for that parameter\r\n'
                self.conSoc.sendall(response.encode('ascii'))
                return
            else:
                response='501 Invalid mode given\r\n'
                self.conSoc.sendall(response.encode('ascii'))
                return 
        response = '200 Mode Altered\r\n'
        self.conSoc.sendall(response.encode('ascii'))


    def STRU(self,newStru):#defines file structure, written by Xongile Nghatsane 1110680
        newStru=newStru.upper()
        strus=['F']#only file structure implemented
        if(newStru not in strus):
            permitted=['F','R','P']
            if(newStru in permitted):
                response='504 Command not implemented for that parameter\r\n'
                self.conSoc.sendall(response.encode('ascii'))
                return
            else:
                response='501 Invalid structure given\r\n'
                self.conSoc.sendall(response.encode('ascii'))
                return 
        response = '200 Structure Altered\r\n'
        self.conSoc.sendall(response.encode('ascii'))

    def MKD(self,directory):#make directory #written by Junaid Dawood 1094837
        if('\\' not in directory):#if not full path sent
            directory=self.currentPath+'\\'+directory

        if (os.path.exists(directory)):
            response='550 already exits\r\n'
            self.conSoc.sendall(response.encode('ascii'))
            return

        if (self.corePath not in directory and self.user!='ADMIN' ):
            response='530 You do not have permission to access this.\r\n'
            self.conSoc.sendall(response.encode('ascii'))
            return

        try:
            os.mkdir(directory)
            response='257 Dir '+directory+'created\r\n'
            self.conSoc.sendall(response.encode('ascii'))
        except:
            response='550 MKD failed \r\n'
            self.conSoc.sendall(response.encode('ascii'))





with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as soc:
    #welcoming socket
    soc.bind((host,port))
    soc.listen(5)#restricts number of attempts to create a connection at once
 
    #open new conenction socket
    while 1:#loop to keep server listening
        s1,addr = soc.accept()
        print("New Client at: %s"%str(addr))
        threadi=myThread(0,s1,addr)
        threadi.start()

