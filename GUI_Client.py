import socket
from tkinter import *




class FTPClient():
    def __init__(self):
        self.conSoc=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.loggedIn=False
        self.open=True
        self.dataSoc=None
        self.passiveIP=None
        self.passivePort=None
        self.type='b'
        self.list=''

    def login(self,userName,password):

       while 1:
            loginMessage='USER '+userName+'\r\n'
            print('C %s' % loginMessage)
            self.conSoc.sendall(loginMessage.encode('ascii'))
            serverResp=self.conSoc.recv(1024).decode('ascii')
            print('S %s' % serverResp)

            if(serverResp.startswith('331')):
                loginMessage='PASS '+password+'\r\n'
                print('C %s' % loginMessage)
                self.conSoc.sendall(loginMessage.encode('ascii'))
            else:
                continue
                
            serverResp=self.conSoc.recv(1024).decode('ascii')
            print('S %s' % serverResp)

            if(serverResp.startswith('200')):
                self.loggedIn=True
                print("Login success!")
                break

    def parseCommand(self,command):
        if (command=='QUIT'):
            self.QUIT() 
        elif (command=='PORT'):
            self.PORT()
        elif (command=="PASV"):
            self.PASV()
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
    def PASV(self):
        message='PASV\r\n'
        print('C %s'%message)
        self.conSoc.sendall(message.encode('ascii'))
        serverResp=self.conSoc.recv(1024).decode('ascii')
        print('S %s'%serverResp)
        if(serverResp.startswith('2')):
            splitResp=serverResp[:-2]
            print(splitResp)
            splitResp=splitResp.split()
            splitIP=splitResp[4]
            splitIP=splitIP.split(",")
            self.passiveIP='.'.join(splitIP[:4])
            self.passivePort=int(splitIP[4])*256+int(splitIP[5])
        elif(serverResp.startswith('5')):
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
            newFile=open('new_'+filename,'w'+self.type)

            while 1:
                data=s1.recv(1024)
                if (not data): break##meaning the connection is closed in an 'orderly' way
                newFile.write(data)
            
            newFile.close()        
            print('Transfer complete')
 
            self.CloseDataSocket()
            return

        if(self.passiveIP!=None):##Assume Passive
            self.dataSoc=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.dataSoc.connect((self.passiveIP,self.passivePort))
            newFile=open('new_'+filename,'w'+self.type)

            while 1:
                data=self.dataSoc.recv(1024)
                if (not data): break##meaning the connection is closed in an 'orderly' way
                newFile.write(data)
            
            newFile.close()        
            print('Transfer complete')
            

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

            with open(filename,'r'+self.type) as f:##read as binary
                toSend=f.read(1024)#using send for now instead of sendall
                while (toSend):
                    if (self.type==''): toSend=toSend.encode('ascii')
    
                    s1.send(toSend)
                    toSend=f.read(1024)
            
            s1.shutdown(socket.SHUT_RDWR)
            s1.close()


            self.CloseDataSocket()
            return

        if(self.passiveIP!=None):##Assume Passive
            self.dataSoc=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.dataSoc.connect((self.passiveIP,self.passivePort))
            with open(filename,'r'+self.type) as f:##read as binary
                toSend=f.read(1024)#using send for now instead of sendall
                while (toSend):
                    if (self.type==''): toSend=toSend.encode('ascii')
                    self.dataSoc.send(toSend)
                    toSend=f.read(1024)
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

    def Connect(self,serverip,port):
        self.conSoc.connect((serverip,port))
        serverResp=''
        while(serverResp==''):
            serverResp=self.conSoc.recv(1024).decode('ascii')

        print('S %s' % serverResp)

        return

    def MODE(self):
        return

    def STRU(self):
        return

    def LIST(self):
        message = 'LIST \r\n'
        print('C %s'%message)
        self.conSoc.sendall(message.encode('ascii'))

        serverResp=self.conSoc.recv(1024).decode('ascii')
        print('S %s'%serverResp)
        if(serverResp.startswith('2')):
            list=''

            if(self.dataSoc!=None):##Assume active

                self.dataSoc.listen()
                s1,addr=self.dataSoc.accept()

                while 1:
                    data=s1.recv(1024)
                    if not data:
                        break
                    list+=data.decode()

                s1.shutdown(socket.SHUT_RDWR)
                s1.close()

                print (list)
                self.CloseDataSocket()
                self.list=list

            if(self.passiveIP!=None):##Assume Passive
                self.dataSoc=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                self.dataSoc.connect((self.passiveIP,self.passivePort))
                
                while 1:
                    data=self.dataSoc.recv(1024)
                    if not data:
                        break
                    list+=data.decode()

                self.dataSoc.close()
                self.dataSoc=None
                print (list)

                self.list=list
        else:

            print("No data soc")
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
    


class GUIClient():

    def __init__(self,client):

        ##some state vars
        self.connected=False
        self.loggedIn=False

        self.FTPClient=client
        self.window = Tk()
        self.window.title("FTP Client") 
        self.window.geometry('1280x1024')

        self.loginBtn = Button(self.window, text="Login",command=self.doLogin)
        self.pasvbBtn = Button(self.window, text="PASV",command=self.doPASV)

        self.portBtn = Button(self.window, text="PORT",command=self.doPORT)
        self.typeBtn = Button(self.window, text="TYPE",command=self.doTYPE)

        self.connectBtn=Button(self.window, text="Connect",command=self.doConnect)
        self.listBtn=Button(self.window, text = 'LIST', command=self.doList)

        self.FileList=Text(self.window,height=20,width=50)
        self.Log=Text(self.window,height=20,width=50)


        self.loginBtn.grid(column=1, row=0)
        self.pasvbBtn.grid(column=1, row=2)
        self.portBtn.grid(column=1, row=4)
        self.typeBtn.grid(column=1, row=6)
        self.listBtn.grid(column=1, row =10)
        self.connectBtn.grid(column=1, row=8)
        self.Log.grid(column=5,row=3)
        self.FileList.grid(column=7,row=3)

        self.window.mainloop()

    def doPopUp(self,label):
        popup1=popupWindow(self.window,label)
        self.window.wait_window(popup1.top)
        return popup1.value


    def doConnect(self):
        
        serverIP=self.doPopUp('Enter IP')
        port=self.doPopUp('Enter Port')
        try:
            self.FTPClient.Connect(serverIP,int(port))
            self.Log.insert(END,'Connected to Server. Login..\n')
            self.connected=True
        except:
            self.Log.insert(END,'Could not Connect\n')
        

        return

    def doLogin(self):
        username=self.doPopUp('Enter username')

        password=self.doPopUp('Enter password')

        try:
            self.FTPClient.login(username,password)
            if(self.FTPClient.loggedIn):
                self.Log.insert(END,'Logged in !\n')
                self.loggedIn=True
            else:
                return
        except:
            self.Log.insert(END,'Could not log in...\n')
        

        return


    def doTYPE(self):
        return
    

    def doPORT(self):
        return
    
    def doPASV(self):
        self.FTPClient.PASV()
        self.Log.insert(END,'Created Passive Data soc\n')
        self.Log.insert(END,'Passive at: '+self.FTPClient.passiveIP +':'+str(self.FTPClient.passivePort))
        return

    def doList(self):
        self.FTPClient.LIST()
        self.FileList.insert(END,self.FTPClient.list)
        return

    

        

class popupWindow(object):
    def __init__(self,master,title):
        top=self.top=Toplevel(master,width=100,height=100)
        top.after('1',lambda: top.focus_force())
        self.l=Label(top,text=title)
        self.l.pack()
        self.e=Entry(top)
        self.e.pack()
        self.e.focus()
        self.b=Button(top,text='Ok',command=self.cleanup)
        top.bind('<Return>', self.returnPress)
        self.b.pack()

    def returnPress(self,e):
        self.cleanup()

    def cleanup(self):
        self.value=self.e.get()
        self.top.destroy()



guiClient=GUIClient(FTPClient())



    


