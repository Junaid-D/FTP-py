import socket
import threading
import time
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
    print('Server is shutting down.')                

    def parseCommand(self,recCommand):
        splitStr=recCommand[:-2]
        splitStr=splitStr.split(' ',3)
        if len(splitStr) == 1:
            return [splitStr[0],'']
        return splitStr
            
    def USER(self):
        greeting= '220 Service ready for new user \r\n'
        self.conSoc.sendall(greeting.encode('ascii'))
        rec_data=self.conSoc.recv(1024)
        response=self.parseCommand(rec_data.decode('ascii'))
        print('C %s'%response)
        self.user=response[1]
        if(self.verifyUser()==True):
            self.authorized=True
            response = '200 User logged in, proceed.'
            self.conSoc.sendall(response.encode('ascii'))

    def QUIT(self):
        response='221 Service closing control connection \r\n'
        self.conSoc.sendall(response.encode('ascii'))
        self.open=False

    def PORT(self,args):
        print(args)
        


                

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
