import socket
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
import os
import csv
from ttkthemes import ThemedTk



class FTPClient():
    def __init__(self):
        self.conSoc=None
        self.loggedIn=False
        self.open=True
        self.dataSoc=None
        self.passiveIP=None
        self.passivePort=None
        self.type=''
        self.list=''
        self.mode="S"
        self.stru='F'
        self.textExtensions=None
    def Connect(self,serverip,port):
        self.conSoc=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        
        self.conSoc.connect((serverip,port))
        serverResp=''
        while(serverResp==''):
            serverResp=self.conSoc.recv(1024).decode('ascii')

        print('S %s' % serverResp)

        return

    def login(self,userName,password):
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
            return
                
        serverResp=self.conSoc.recv(1024).decode('ascii')
        print('S %s' % serverResp)

        if(serverResp.startswith('200')):
            self.loggedIn=True
            print("Login success!")
        

    def QUIT(self):  
        message='QUIT\r\n'
        print('C %s'%message)
        self.conSoc.sendall(message.encode('ascii'))
        serverResp=self.conSoc.recv(1024).decode('ascii')
        print('S %s'%serverResp)
        if(serverResp.startswith('221')):
            self.loggedIn=False
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
            splitIP=splitResp[-1]
            splitIP=splitIP.split(",")
            self.passiveIP='.'.join(splitIP[:4])
            self.passivePort=int(splitIP[4])*256+int(splitIP[5])
        elif(serverResp.startswith('5')):
            print('Error with parameters, retuning to menu..')
        return  
    def RETR(self,filename):#stream--server will close connection, block-- eof block will be sent
        if(self.passiveIP==None and self.dataSoc==None):
            print('No data connection was set up')
            return 2
        
        message='RETR '+filename+'\r\n'
        print('C %s'%message)
        self.conSoc.sendall(message.encode('ascii'))
        serverResp=self.conSoc.recv(1024).decode('ascii')
        print('S %s'%serverResp)

        if(serverResp.startswith('5') == True):
            return 1
        

        if(self.dataSoc!=None):##Assume active
            self.dataSoc.listen()
            s1,addr=self.dataSoc.accept()
            newFile=open('new_'+filename,"w"+self.type)
            if(self.mode=='S'):
                while 1:
                    data=s1.recv(1024)
                    if (not data): break##meaning the connection is closed in an 'orderly' way
                    if (self.type==''): data=data.decode('ascii')
                    newFile.write(data)
            newFile.close()        
            print('Transfer complete')
 
            self.CloseDataSocket()
            return 0

        if(self.passiveIP!=None):##Assume Passive
            self.dataSoc=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.dataSoc.connect((self.passiveIP,self.passivePort))
            newFile=open('new_'+filename,"w"+self.type)
            if(self.mode=='S'):
                while 1:
                    data=self.dataSoc.recv(1024)
                    if (not data): break##meaning the connection is closed in an 'orderly' way
                    if (self.type==''): data=data.decode('ascii')
                    newFile.write(data)
            newFile.close()        
            print('Transfer complete')
            

            self.dataSoc.close()
            self.dataSoc=None
            return 0

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


    def MODE(self,mode):
        message='MODE '+mode+'\r\n'
        print('C %s'%message)
        self.conSoc.sendall(message.encode('ascii'))
        serverResp=self.conSoc.recv(1024).decode('ascii')
        print('S %s'%serverResp)

        if(serverResp.startswith('2')):
            if(mode=='S'):self.mode='S'
            return 0 
        else:
            return 1
        return

    def STRU(self, stru):
        message='STRU '+stru+'\r\n'
        print('C %s'%message)
        self.conSoc.sendall(message.encode('ascii'))
        serverResp=self.conSoc.recv(1024).decode('ascii')
        print('S %s'%serverResp)
        if(serverResp.startswith('2')):
            if(stru=='F'):self.mode='S'
            return 0 
        else:
            return 1
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

    def PWD(self):
        message='PWD\r\n'
        print('C %s'%message)
        self.conSoc.sendall(message.encode('ascii'))
        serverResp=self.conSoc.recv(1024).decode('ascii')
        print('S %s'%serverResp)
        return serverResp[3:-2]

    def CWD(self,newDir):
        message='CWD '+newDir+'\r\n'
        print('C %s'%message)
        self.conSoc.sendall(message.encode('ascii'))
        serverResp=self.conSoc.recv(1024).decode('ascii')
        print('S %s'%serverResp)
        if(serverResp.startswith('2')):
            return 0
        else:
            return 1

    def MKD(self,newDir):
        message='MKD '+newDir+'\r\n'
        print('C %s'%message)
        self.conSoc.sendall(message.encode('ascii'))
        serverResp=self.conSoc.recv(1024).decode('ascii')
        print('S %s'%serverResp)
        if(serverResp.startswith('2')):
            return 0
        else:
            return 1

    def NOOP(self):
        message='NOOP\r\n'
        print('C %s'%message)
        self.conSoc.sendall(message.encode('ascii'))
        serverResp=self.conSoc.recv(1024).decode('ascii')
        print('S %s'%serverResp)
        return
    def CloseDataSocket(self):
        self.dataSoc.close()
        self.dataSoc=None
        return
    


class GUIClient():

    def __init__(self,client):

        ##some state vars
        self.connected=False
        self.loggedIn=False
        self.textExtensions=None
        self.FTPClient=client
        self.window = ThemedTk(theme="equilux",background='gray40')
        self.window.title("FTP Client") 
        self.window.geometry('1200x640')

        self.connectBtn=ttk.Button(self.window, text="Connect",command=self.doConnect)        
        self.loginBtn = ttk.Button(self.window, text="Login",state=DISABLED,command=self.doLogin)
        self.quitBtn = ttk.Button(self.window, text="QUIT",state=DISABLED,command=self.doQUIT)


        self.portBtn = ttk.Button(self.window, text="PORT",state=DISABLED,command=self.doPORT)
        self.pasvbBtn = ttk.Button(self.window, text="PASV",state=DISABLED,command=self.doPASV)
        

        self.typeBtn = ttk.Button(self.window, text="TYPE",state=DISABLED,command=self.doTYPE)
        self.struBtn = ttk.Button(self.window, text="STRU",state=DISABLED,command=self.doSTRU)
        self.modeBtn = ttk.Button(self.window, text="MODE",state=DISABLED,command=self.doMODE)




        self.pwdBtn = ttk.Button(self.window, text="PWD",state=DISABLED,command=self.doPWD)
        self.cwdBtn = ttk.Button(self.window, text="CWD",state=DISABLED,command=self.doCWD)
        self.mkdBtn = ttk.Button(self.window, text="MKD",state=DISABLED,command=self.doMKD)



        self.listBtn = ttk.Button(self.window, text = 'LIST',state=DISABLED, command=self.doLIST)
        self.retrBtn = ttk.Button(self.window, text = 'RETR',state=DISABLED, command=self.doRETR)
        self.storBtn = ttk.Button(self.window, text = 'STOR',state=DISABLED, command=self.doSTOR)


        self.FileList=Text(self.window,height=20,width=70,background='gray42',fg='orange')
        self.Log=Text(self.window,height=20,width=40,background='gray42',fg='orange')
        self.FileList.insert(END,'File/Dir          usr grp size \t Last modified \t filename \n')



        self.loginBtn.grid(column=1, row=1,pady=2,padx=10)
        self.connectBtn.grid(column=2, row=1,pady=2,padx=10)
        self.quitBtn.grid(column=1, row=2,pady=2,padx=10)

        self.pasvbBtn.grid(column=1, row=3,pady=2,padx=10)
        self.portBtn.grid(column=2, row=3,pady=2,padx=10)


        self.typeBtn.grid(column=1, row=4,pady=2,padx=10)
        self.modeBtn.grid(column=2, row=4,pady=2,padx=10)
        self.struBtn.grid(column=1, row=5,pady=2,padx=10)


        self.pwdBtn.grid(column=1, row=9,pady=2,padx=10)
        self.cwdBtn.grid(column=2, row=9,pady=2,padx=10)
        self.mkdBtn.grid(column=1, row=10,pady=2,padx=10)


        self.listBtn.grid(column=1, row=6,pady=2,padx=10)
        self.retrBtn.grid(column=2, row=6,pady=2,padx=10)
        self.storBtn.grid(column=1, row=7,pady=2,padx=10)


        self.FileList.grid(column=15,row=0,padx=10)
        self.Log.grid(column=7,row=0,padx=15)



        self.window.mainloop()

    def doPopUp(self,label,defaultVal=''):
        popup1=popupWindow(self.window,label,defaultVal)
        self.window.wait_window(popup1.top)
        return popup1.value

    def CheckExtension(self,file):
        name,ext=os.path.splitext(file)
        print(ext)
        if(ext not in self.textExtensions):
            self.FTPClient.TYPE("I")
        else:
            self.FTPClient.TYPE("A")
    def loadExtensions(self):
        with open('extensions.txt') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            self.textExtensions=['.txt']
            for row in csv_reader:
                for ext in row:
                    self.textExtensions.append(ext)
        print(self.textExtensions)
    def doConnect(self):
        
        serverIP=self.doPopUp('Enter IP','127.0.0.1')
        port=self.doPopUp('Enter Port','21')
        try:
            self.FTPClient.Connect(serverIP,int(port))
            self.Log.insert(END,'Connected to Server. Login..\n')
            self.connected=True
            self.connectBtn['state']='disabled'
            self.loginBtn['state']='normal'
        except:
            self.Log.insert(END,'Could not Connect... Please check firewall settings or server status\n')
        

        return

    def doLogin(self):
        self.loadExtensions()
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
                self.Log.insert(END,'Invalid login\n')

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
    
    def doMODE(self):
        mode=self.doPopUp('Mode? (S,B or C)','S')
        if(self.FTPClient.MODE(mode)==0):
            self.Log.insert(END,'Mode set to '+mode+'\n')
        else:
            self.Log.insert(END,'Could not complete\n')

    def doSTRU(self):
        ftype=self.doPopUp('Fileype?','F')
        if(self.FTPClient.STRU(ftype)==0):
            self.Log.insert(END,'Filetype set to '+ftype+'\n')
        else:
            self.Log.insert(END,'Could not complete\n')

    def doPORT(self):
        ip=self.doPopUp('Enter IP')
        port=self.doPopUp('Enter Port')
        try:
            if(self.FTPClient.PORT(ip,int(port)) ==0):
                self.Log.insert(END,'Listen socket created at '+ip+':'+port+'\n')
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
        self.CheckExtension(filename)

        try:
            if( self.FTPClient.STOR(filename)==0):
                self.Log.insert(END, 'File: '+ filename+' uploaded \n')
            else:
                self.Log.insert(END, 'Could not upload \n')
            
        except:
            self.Log.insert(END, 'Could not upload \n')

        finally:
            self.disableDataButtons()

        return

    def doRETR(self):
        filename=self.doPopUp('Filename?')
        self.CheckExtension(filename)
        try:
            res=self.FTPClient.RETR(filename)
            if(res==0):
                self.Log.insert(END,filename+' download complete\n')
            else:
                self.Log.insert(END,'Could not download...\n')
        except:
            self.Log.insert(END,'Could not download...\n')
        finally:
            self.disableDataButtons()
        return

    def doPWD(self):

        try:
            curerntPath=self.FTPClient.PWD()
            self.Log.insert(END,curerntPath+' is the current path\n')
        except:
            self.Log.insert(END,'Could not retrieve cwd...\n')
        return

    def doCWD(self):
        newDir=self.doPopUp('Directory?')

        try:
            if(self.FTPClient.CWD(newDir)==0):
                self.Log.insert(END,'Path was changes to: '+ newDir+'\n')
            else:
                self.Log.insert(END,'Could not change dir\n')

        except:
            self.Log.insert(END,'Could not change dir\n')
        return

    def doMKD(self):
        newDir=self.doPopUp('Directory?')

        try:
            if(self.FTPClient.MKD(newDir)==0):
                self.Log.insert(END,'Directory created: '+ newDir+'\n')
            else:
                self.Log.insert(END,'Could not create dir\n')

        except:
            self.Log.insert(END,'Could not create dir\n')
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
        self.pwdBtn['state']='normal'
        self.cwdBtn['state']='normal'
        self.mkdBtn['state']='normal'
        self.modeBtn['state']='normal'
        self.struBtn['state']='normal'

    
    def disableNonDataButtons(self):
        self.portBtn['state']='disabled'
        self.pasvbBtn['state']='disabled'
        self.typeBtn['state']='disabled'
        self.pwdBtn['state']='disabled'
        self.cwdBtn['state']='disabled'
        self.mkdBtn['state']='disabled'
        self.modeBtn['state']='disabled'
        self.struBtn['state']='disabled'




class popupWindow(object):
    def __init__(self,master,title,default=''):
        top=self.top=Toplevel(master,width=100,height=100)
        top.configure(background='gray42')
        top.after('1',lambda: top.focus_force())
        self.l=ttk.Label(top,text=title)
        self.l.pack()
        self.e=ttk.Entry(top)
        self.e.insert(END,default)
        self.e.pack()
        self.e.focus()
        self.b=ttk.Button(top,text='Ok',command=self.cleanup)
        top.bind('<Return>', self.returnPress)
        self.b.pack()

    def returnPress(self,e):
        self.cleanup()

    def cleanup(self):
        self.value=self.e.get()
        self.top.destroy()



guiClient=GUIClient(FTPClient())



    


