import socket
from tkinter import *
from tkinter import filedialog
import os



class FTPClient():
    def __init__(self):
        self.conSoc=None
        self.loggedIn=False
        self.open=True
        self.dataSoc=None
        self.passiveIP=None
        self.passivePort=None
        self.type='b'
        self.list=''

    def Connect(self,serverip,port):
        self.conSoc=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        
        self.conSoc.connect((serverip,port))
        serverResp=''
        while(serverResp==''):
            serverResp=self.conSoc.recv(1024).decode('ascii')

        print('S %s' % serverResp)

        return

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
            self.PORT('','')
        elif (command=="PASV"):
            self.PASV()
        elif (command=='TYPE'):
            self.TYPE('')
        elif (command=='MODE'):
            self.MODE()
        elif (command=='STRU'):
            self.STRU()
        elif (command=='RETR'):
            self.RETR('')
        elif (command=='STOR'):
            self.STOR('')
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
            self.conSoc.shutdown(socket.SHUT_WR) 
            self.conSoc.close()
            return

    def PORT(self,ip,portNo):
        print('Requesting data port')

        splitIP=ip.split('.')
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
            return 1
        return 0
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
    def RETR(self,filename):#stream--server will close connection, block-- eof block will be sent
        if(self.passiveIP==None and self.dataSoc==None):
            print('No data connection was set up')
            return
        
        message='RETR '+filename+'\r\n'
        print('C %s'%message)
        self.conSoc.sendall(message.encode('ascii'))
        serverResp=self.conSoc.recv(1024).decode('ascii')
        print('S %s'%serverResp)

        if(self.dataSoc!=None):##Assume active
            self.dataSoc.listen()
            s1,addr=self.dataSoc.accept()
            newFile=open('new_'+filename,"w"+self.type)

            while 1:
                data=s1.recv(1024)
                if (not data): break##meaning the connection is closed in an 'orderly' way
                if (self.type==''): data=data.decode('ascii')
                newFile.write(data)
            
            newFile.close()        
            print('Transfer complete')
 
            self.CloseDataSocket()
            return

        if(self.passiveIP!=None):##Assume Passive
            self.dataSoc=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.dataSoc.connect((self.passiveIP,self.passivePort))
            newFile=open('new_'+filename,"w"+self.type)

            while 1:
                data=self.dataSoc.recv(1024)
                if (not data): break##meaning the connection is closed in an 'orderly' way
                if (self.type==''): data=data.decode('ascii')
                newFile.write(data)
            
            newFile.close()        
            print('Transfer complete')
            

            self.dataSoc.close()
            self.dataSoc=None
            return

    def STOR(self,filename):
        if(self.passiveIP==None and self.dataSoc==None):
            print('No data connection was set up')
            return 1
        
        head, filenameOnServer = os.path.split(filename)

        message='STOR '+filenameOnServer+'\r\n'
        print('C %s'%message)
        self.conSoc.sendall(message.encode('ascii'))
        serverResp=self.conSoc.recv(1024).decode('ascii')
        print('S %s'%serverResp)

        if(self.dataSoc!=None):##Assume active

            self.dataSoc.listen()
            s1,addr=self.dataSoc.accept()

            with open(filename,"r"+self.type) as f:##read as binary
                toSend=f.read(1024)#using send for now instead of sendall
                while (toSend):
                    if (self.type==''): toSend=toSend.encode('ascii')
    
                    s1.send(toSend)
                    toSend=f.read(1024)
            
            s1.shutdown(socket.SHUT_RDWR)
            s1.close()


            self.CloseDataSocket()
            return 0

        if(self.passiveIP!=None):##Assume Passive
            self.dataSoc=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.dataSoc.connect((self.passiveIP,self.passivePort))
            with open(filename,"r"+self.type) as f:##read as binary
                toSend=f.read(1024)#using send for now instead of sendall
                while (toSend):
                    if (self.type==''): toSend=toSend.encode('ascii')
                    self.dataSoc.send(toSend)
                    toSend=f.read(1024)
            self.dataSoc.close()
            self.dataSoc=None
            return 0

        
 
    def TYPE(self,type):

        message='TYPE '+type+'\r\n'
        print('C %s'%message)
        self.conSoc.sendall(message.encode('ascii'))
        serverResp=self.conSoc.recv(1024).decode('ascii')
        print('S %s'%serverResp)
        if(serverResp.startswith('2')):
            if(type=='I'):self.type='b'
            else: self.type=''
            return 0 
        else:
            return 1


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

        self.connectBtn=Button(self.window, text="Connect",command=self.doConnect)        
        self.loginBtn = Button(self.window, text="Login",state=DISABLED,command=self.doLogin)
        self.quitBtn = Button(self.window, text="QUIT",state=DISABLED,command=self.doQUIT)


        self.portBtn = Button(self.window, text="PORT",state=DISABLED,command=self.doPORT)
        self.pasvbBtn = Button(self.window, text="PASV",state=DISABLED,command=self.doPASV)
        

        self.typeBtn = Button(self.window, text="TYPE",state=DISABLED,command=self.doTYPE)



        self.listBtn=Button(self.window, text = 'LIST',state=DISABLED, command=self.doLIST)
        self.retrBtn=Button(self.window, text = 'RETR',state=DISABLED, command=self.doRETR)
        self.storBtn=Button(self.window, text = 'STOR',state=DISABLED, command=self.doSTOR)


        self.FileList=Text(self.window,height=20,width=50)
        self.Log=Text(self.window,height=20,width=50)


        self.loginBtn.grid(column=1, row=0)
        self.connectBtn.grid(column=1, row=8)
        self.quitBtn.grid(column=2, row=10)

        self.pasvbBtn.grid(column=1, row=2)
        self.portBtn.grid(column=1, row=4)

        self.typeBtn.grid(column=1, row=6)

        self.listBtn.grid(column=1, row =10)
        self.retrBtn.grid(column=2,row=2)
        self.storBtn.grid(column=2,row=4)


        self.FileList.grid(column=8,row=3)
        self.Log.grid(column=5,row=3)


        self.window.mainloop()

    def doPopUp(self,label,defaultVal=''):
        popup1=popupWindow(self.window,label,defaultVal)
        self.window.wait_window(popup1.top)
        return popup1.value


    def doConnect(self):
        
        serverIP=self.doPopUp('Enter IP','127.0.0.1')
        port=self.doPopUp('Enter Port','4500')
        try:
            self.FTPClient.Connect(serverIP,int(port))
            self.Log.insert(END,'Connected to Server. Login..\n')
            self.connected=True
            self.connectBtn['state']='disabled'
            self.loginBtn['state']='normal'
        except:
            self.Log.insert(END,'Could not Connect\n')
        

        return

    def doLogin(self):
        username=self.doPopUp('Enter username','ADMIN')

        password=self.doPopUp('Enter password','ADMIN')

        try:
            self.FTPClient.login(username,password)
            if(self.FTPClient.loggedIn):
                self.Log.insert(END,'Logged in !\n')
                self.loggedIn=True
                self.loginBtn['state']='disabled'
                self.quitBtn['state']='normal'
                self.enableNonDataButtons()
            else:
                self.disableNonDataButtons()
                return
        except:
            self.disableNonDataButtons()
            self.Log.insert(END,'Could not log in...\n')
        

        return

    def doQUIT(self):
        self.FTPClient.QUIT()
        self.disableDataButtons()
        self.disableNonDataButtons()
        self.loginBtn['state']='disabled'
        self.connectBtn['state']='normal'
        self.quitBtn['state']='disabled'
        self.Log.insert(END,'Connection terminated.\n')

        return

    def doTYPE(self):
        type=self.doPopUp('Type? (I or A)','I')
        if( self.FTPClient.TYPE(type)==0):
            self.Log.insert(END,'Type set to '+type+'\n')
        else:
            self.Log.insert(END,'Could not complete\n')
    

    def doPORT(self):
        ip=self.doPopUp('Enter IP')
        port=self.doPopUp('Enter Port')
        try:
            if(self.FTPClient.PORT(ip,int(port)) ==0):
                self.Log.insert(END,'Listen socket created at'+ip+':'+port+'\n')
                self.enableDataButtons()
            else:
                self.Log.insert(END,'Failed, invalid input...\n')
                self.disableDataButtons()
        except:
            self.Log.insert(END,'Failed, invalid input...\n')
            self.disableDataButtons()


        return
    
    def doPASV(self):
        self.FTPClient.PASV()
        self.enableDataButtons()
        self.Log.insert(END,'Created Passive Data soc \n')
        self.Log.insert(END,'Passive at: '+self.FTPClient.passiveIP +':'+str(self.FTPClient.passivePort) +'\n')
        return

    def doLIST(self):
        self.FTPClient.LIST()
        try:
            self.FileList.insert(END,self.FTPClient.list)
            self.Log.insert(END,'list obtained \n')

        except:
            self.Log.insert(END,'Could not obtain list \n')

        finally:
            self.disableDataButtons()

        return

    def doSTOR(self):
        filename =  filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = [("all files","*.*")])
        print(filename)
        try:
            if( self.FTPClient.STOR(filename)==0):
                self.Log.insert(END, 'File: '+ filename+'uploaded \n')
            else:
                self.Log.insert(END, 'Could not upload \n')
            
        except:
            self.Log.insert(END, 'Could not upload \n')

        finally:
            self.disableDataButtons()

        return

    def doRETR(self):
        filename=self.doPopUp('Filename?')
        try:
            self.FTPClient.RETR(filename)
            self.Log.insert(END,filename+'downloaded\n')
        except:
            self.Log.insert(END,'Could not download...\n')
        finally:
            self.disableDataButtons()
        return

    def enableDataButtons(self):
        self.listBtn['state']='normal'
        self.retrBtn['state']='normal'
        self.storBtn['state']='normal'


    def disableDataButtons(self):
        self.listBtn['state']='disabled'
        self.retrBtn['state']='disabled'
        self.storBtn['state']='disabled'


    
    def enableNonDataButtons(self):
        self.portBtn['state']='normal'
        self.pasvbBtn['state']='normal'
        self.typeBtn['state']='normal'

    
    def disableNonDataButtons(self):
        self.portBtn['state']='disabled'
        self.pasvbBtn['state']='disabled'
        self.typeBtn['state']='disabled'


class popupWindow(object):
    def __init__(self,master,title,default=''):
        top=self.top=Toplevel(master,width=100,height=100)
        top.after('1',lambda: top.focus_force())
        self.l=Label(top,text=title)
        self.l.pack()
        self.e=Entry(top)
        self.e.insert(END,default)
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



    


