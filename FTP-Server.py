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
    def run(self):
        runServer(self.conSoc,self.dest)

    def USER()

def runServer(s1,addr):
    global activeCount
    with s1:
        while 1:
            rec_data=s1.recv(1024)
            if not rec_data:
                break     
            print("Received",rec_data.decode('ascii'))
            s1.sendall(rec_data)
            if rec_data.decode('ascii') == 'close':
                activeCount-=1
                print("Closing connection to....%s"%str(addr))
                break


with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as soc:
    #welcoming socket
    soc.bind((host,port))
    soc.listen(5)
 
    #open new conenction socket
    while 1:
        s1,addr = soc.accept()
        activeCount+=1
        print("New Client at: %s"%str(addr))
        threadi=myThread(0,s1,addr)
        threadi.start()
