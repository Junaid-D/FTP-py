import socket
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
import os
import csv
from ttkthemes import ThemedTk



class FTPClient():#defines class used for backend implementation of ftp commands
    def __init__(self):#initialises variables for client
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
        self.serverIP=None
    def Connect(self,serverip,port):#attempts to connect to servewr on specified ip and port #This was written by Junaid Dawood 1094837
        self.conSoc=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        
        self.conSoc.connect((serverip,port))
        serverResp=''
        while(serverResp==''):#waits for server response
            serverResp=self.conSoc.recv(1024).decode('ascii')

        self.serverIP=serverip
        print('S %s' % serverResp)

        return

    def login(self,userName,password):#attempts to log in #This was written by Junaid Dawood 1094837
        loginMessage='USER '+userName+'\r\n'#sends username
        print('C %s' % loginMessage)
        self.conSoc.sendall(loginMessage.encode('ascii'))
        serverResp=self.conSoc.recv(1024).decode('ascii')
        print('S %s' % serverResp)

        if(serverResp.startswith('331')):#sends password after username is confirmed received
            loginMessage='PASS '+password+'\r\n'
            print('C %s' % loginMessage)
            self.conSoc.sendall(loginMessage.encode('ascii'))
        else:
            return
                
        serverResp=self.conSoc.recv(1024).decode('ascii')
        print('S %s' % serverResp)

        if(serverResp.startswith('2')):#waits for login confirmation from server
            self.loggedIn=True
            print("Login success!")
        

    def QUIT(self):  #closes the connection #This was written by Junaid Dawood 1094837
        message='QUIT\r\n'
        print('C %s'%message)
        self.conSoc.sendall(message.encode('ascii'))
        serverResp=self.conSoc.recv(1024).decode('ascii')
        print('S %s'%serverResp)
        if(serverResp.startswith('221')):#clears variables after server confirms connection closed
            self.loggedIn=False
            self.open=False
            print('Connection closed by server.')
            self.conSoc.shutdown(socket.SHUT_WR) 
            self.conSoc.close()
            return

    def PORT(self,ip,portNo):#sets the client in passive mode #This was written by Junaid Dawood 1094837
        print('Requesting data port')

        splitIP=ip.split('.')
        port1=int(portNo)//256
        port2=int(portNo)%256
        #ip
        sequence=splitIP[0]+','+splitIP[1]+','+splitIP[2]+','+splitIP[3]    
        #port
        sequence=sequence+','+str(port1)+','+str(port2)#formats the client ip details as needed

        self.dataSoc=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.dataSoc.bind((ip,(int(portNo))))#binds socket to listen for data from server

        message='PORT '+sequence+'\r\n'
        print('C %s'%message)
        self.conSoc.sendall(message.encode('ascii'))
        serverResp=self.conSoc.recv(1024).decode('ascii')
        print('S %s'%serverResp)
        if(serverResp.startswith('5')):
            print('Error with parameters, retuning to menu..')
            return 1
        return 0


    def PASV(self):#sets the client in active mode #This was written by Xongile Nghatsane 1110680
        message='PASV\r\n'
        print('C %s'%message)
        self.conSoc.sendall(message.encode('ascii'))
        serverResp=self.conSoc.recv(1024).decode('ascii')#requests ip information from server for data connection
        print('S %s'%serverResp)
        if(serverResp.startswith('2')):
            splitResp=serverResp[:-2]
            print(splitResp)
            splitResp=splitResp.split()
            splitIP=splitResp[-1]
            splitIP=splitIP.strip('().')
            splitIP=splitIP.split(",")
            self.passiveIP='.'.join(splitIP[:4])
            self.passivePort=int(splitIP[4])*256+int(splitIP[5])#formats the received ip data and sets the appropriate variables
        elif(serverResp.startswith('5')):
            print('Error with parameters, retuning to menu..')
        return  


    def RETR(self,filename):#stream--server will close connection, block-- eof block will be sent
        #attempt to get file from server
        message='RETR '+filename+'\r\n'
        print('C %s'%message)
        self.conSoc.sendall(message.encode('ascii'))
        serverResp=self.conSoc.recv(1024).decode('ascii')
        print('S %s'%serverResp)

        if(serverResp.startswith('2') == False):#Error handling written by Junaid Dawood 1094837
            return 1
        

        if(self.dataSoc!=None):##Assume server is in active mode #This was written by Junaid Dawood 1094837
            self.dataSoc.listen()
            s1,addr=self.dataSoc.accept()#listen for connection on socket
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


        
        if(self.passiveIP!=None):##Assume server is in Passive mode #This was written by Xongile Nghatsane 1110680
            self.dataSoc=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.dataSoc.connect((self.passiveIP,self.passivePort))#request data on socket
            newFile=open('new_'+filename,"w"+self.type)
            if(self.mode=='S'):
                while 1:
                    data=self.dataSoc.recv(1024)
                    if (not data): break##meaning the connection is closed in an 'orderly' way
                    if (self.type==''): data=data.decode('ascii')
                    newFile.write(data)
            newFile.close()        
            print('Transfer complete')
            
            self.passiveIP=None
            self.passivePort=None
            self.dataSoc.close()
            self.dataSoc=None
            return 0

    def STOR(self,filename):#send file to and store on server
    
        
        head, filenameOnServer = os.path.split(filename)#split filename to remove details of current computer

        message='STOR '+filenameOnServer+'\r\n'
        print('C %s'%message)
        self.conSoc.sendall(message.encode('ascii'))
        serverResp=self.conSoc.recv(1024).decode('ascii')
        print('S %s'%serverResp)

        if(serverResp.startswith('2') == False):#checks if transfer accept #Error handling written by Junaid Dawood 1094837
            return 1


        if(self.dataSoc!=None):##Assume server is active #This was written by Junaid Dawood 1094837

            self.dataSoc.listen()
            s1,addr=self.dataSoc.accept()#wait for server to initiate transfer

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


        if(self.passiveIP!=None):##Assume server is Passive #This was written by Xongile Nghatsane 1110680
            self.dataSoc=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.dataSoc.connect((self.passiveIP,self.passivePort))#initiate data transfer with server
            with open(filename,"r"+self.type) as f:##read as binary
                toSend=f.read(1024)#using send for now instead of sendall
                while (toSend):
                    if (self.type==''): toSend=toSend.encode('ascii')
                    self.dataSoc.send(toSend)
                    toSend=f.read(1024)

            self.passiveIP=None
            self.passivePort=None
            self.dataSoc.close()
            self.dataSoc=None
            return 0

        print('No data connection was set up')
        return 1
        
 
    def TYPE(self,type):#sets whether files are read in ascii or binary #This was written by Xongile Nghatsane 1110680

        message='TYPE '+type+'\r\n'
        print('C %s'%message)
        self.conSoc.sendall(message.encode('ascii'))
        serverResp=self.conSoc.recv(1024).decode('ascii')
        print('S %s'%serverResp)

        if(serverResp.startswith('2')):
            if(type=='I'):self.type='b'
            else: self.type=''#defaults to binary if not explicitly ascii
            return 0 
        else:
            return 1


    def MODE(self,mode):#sets mode of transfer #This was written by Xongile Nghatsane 1110680
        message='MODE '+mode+'\r\n'
        print('C %s'%message)
        self.conSoc.sendall(message.encode('ascii'))
        serverResp=self.conSoc.recv(1024).decode('ascii')
        print('S %s'%serverResp)

        if(serverResp.startswith('2')):
            if(mode=='S'):self.mode='S'#sets to stream transfer mode
            return 0 
        else:
            return 1
        return

    def STRU(self, stru):#sets file structure to be used #This was written by Xongile Nghatsane 1110680
        message='STRU '+stru+'\r\n'
        print('C %s'%message)
        self.conSoc.sendall(message.encode('ascii'))
        serverResp=self.conSoc.recv(1024).decode('ascii')
        print('S %s'%serverResp)
        if(serverResp.startswith('2')):
            if(stru=='F'):self.stru='F'#sets to default file structure
            return 0 
        else:
            return 1
        return

    def LIST(self,args):#attempts to obtain list of accesible files on server #This was written by Junaid Dawood 1094837
        print(args)
        message = 'LIST '+args+'\r\n'
        print('C %s'%message)
        self.conSoc.sendall(message.encode('ascii'))

        serverResp=self.conSoc.recv(1024).decode('ascii')
        print('S %s'%serverResp)

        if(serverResp.startswith('2') == False):
            return 1


        list=''

        if(self.dataSoc!=None):##Assume server is active

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
            return 0


        if(self.passiveIP!=None):##Assume server is passive Passive
            self.dataSoc=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.dataSoc.connect((self.passiveIP,self.passivePort))
            
            while 1:
                data=self.dataSoc.recv(1024)
                if not data:
                    break
                list+=data.decode()
            
            self.passiveIP=None
            self.passivePort=None

            self.dataSoc.close()
            self.dataSoc=None
            print (list)

            self.list=list

            return 0
       

    def PWD(self):#attempts to have server print current directory #This was written by Junaid Dawood 1094837
        message='PWD\r\n'
        print('C %s'%message)
        self.conSoc.sendall(message.encode('ascii'))
        serverResp=self.conSoc.recv(1024).decode('ascii')
        print('S %s'%serverResp)
        return serverResp[3:-2]

    def CWD(self,newDir):#attempts to change directory on server #This was written by Junaid Dawood 1094837
        message='CWD '+newDir+'\r\n'
        print('C %s'%message)
        self.conSoc.sendall(message.encode('ascii'))
        serverResp=self.conSoc.recv(1024).decode('ascii')
        print('S %s'%serverResp)
        if(serverResp.startswith('2')):
            return 0
        else:
            return 1

    def MKD(self,newDir):#attempts to make directory on server #This was written by Junaid Dawood 1094837
        message='MKD '+newDir+'\r\n'
        print('C %s'%message)
        self.conSoc.sendall(message.encode('ascii'))
        serverResp=self.conSoc.recv(1024).decode('ascii')
        print('S %s'%serverResp)
        if(serverResp.startswith('2')):
            return 0
        else:
            return 1

    def NOOP(self):#no operation. Keep connection alive #This was written by Junaid Dawood 1094837
        message='NOOP\r\n'
        print('C %s'%message)
        self.conSoc.sendall(message.encode('ascii'))
        serverResp=self.conSoc.recv(1024).decode('ascii')
        print('S %s'%serverResp)
        return
    def CloseDataSocket(self):#close data socket
        self.dataSoc.close()
        self.dataSoc=None
        return
    


class GUIClient():#defines class for GUI to utilise FTPClient class functionality #GUI was written by Junaid Dawood 1094837, except for automated type checks

    def __init__(self,client):#initialises variables and buttons to default state

        ##some state vars
        self.connected=False
        self.loggedIn=False
        self.textExtensions=None
        self.FTPClient=client
        self.window = ThemedTk(theme="equilux",background='gray40')
        self.window.title("FTP Client") 
        self.window.geometry('1200x640')

        #button initialisation with all disabled except for connect
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

        #initialises the visuals for text
        self.FileList=Text(self.window,height=20,width=70,background='gray42',fg='orange')
        self.Log=Text(self.window,height=20,width=40,background='gray42',fg='orange')
        self.FileList.insert(END,'File/Dir          usr grp size \t Last modified \t filename \n')


        #places buttons on grid
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

    def doPopUp(self,label,defaultVal=''):#create pop up for text for command
        popup1=popupWindow(self.window,label,defaultVal)
        self.window.wait_window(popup1.top)
        return popup1.value

    def CheckExtension(self,file):#checks extensions for type #Automated type checking written by Xongile Nghatsane 1110680
        name,ext=os.path.splitext(file)
        print(ext)
        if(ext not in self.textExtensions):#binary
            self.FTPClient.TYPE("I")
        else:#ascii
            self.FTPClient.TYPE("A")
    def loadExtensions(self):#load extensions
        with open('extensions.txt') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            self.textExtensions=['.txt']
            for row in csv_reader:
                for ext in row:
                    self.textExtensions.append(ext)
        print(self.textExtensions)
    def doConnect(self):#attempt to connect to server
        
        serverIP=self.doPopUp('Enter IP','127.0.0.1')
        port=self.doPopUp('Enter Port','21')#default values
        try:
            self.FTPClient.Connect(serverIP,int(port))
            self.Log.insert(END,'Connected to Server. Login..\n')
            self.connected=True
            self.connectBtn['state']='disabled'#disable connect button
            self.loginBtn['state']='normal'#enable login butotn
        except:
            self.Log.insert(END,'Could not Connect... Please check firewall settings or server status\n')
        

        return

    def doLogin(self):#attempts login
        self.loadExtensions()
        #acquire login details from user
        username=self.doPopUp('Enter username','ADMIN')

        password=self.doPopUp('Enter password','ADMIN')

        try:
            self.FTPClient.login(username,password)
            if(self.FTPClient.loggedIn):#check if logged in
                self.Log.delete('1.0', END)
                self.Log.insert(END,'Logged in !\n')
                self.loggedIn=True
                self.loginBtn['state']='disabled'#disable login
                self.quitBtn['state']='normal'#enable quit button
                self.enableNonDataButtons()#enable buttons for interacting with server
            else:
                self.disableNonDataButtons()
                self.Log.insert(END,'Invalid login\n')

                return
        except:
            self.disableNonDataButtons()
            self.Log.insert(END,'Could not log in...\n')
        

        return

    def doQUIT(self):#initiate quitting conection
        self.FTPClient.QUIT()
        self.disableDataButtons()#disable buttons
        self.disableNonDataButtons()
        self.loginBtn['state']='disabled'
        self.connectBtn['state']='normal'#reset to only connect button available
        self.quitBtn['state']='disabled'

        self.Log.delete('1.0', END)

        self.FileList.delete('1.0', END)

        self.FileList.insert(END,'File/Dir          usr grp size \t Last modified \t filename \n')

        self.Log.insert(END,'Connection terminated.\n')

        return

    def doTYPE(self):#call type of FTPCLient class
        type=self.doPopUp('Type? (I or A)','I')
        if( self.FTPClient.TYPE(type)==0):
            self.Log.insert(END,'Type set to '+type+'\n')
        else:
            self.Log.insert(END,'Could not complete\n')
    
    def doMODE(self):#call mode of ftpclient class
        mode=self.doPopUp('Mode? (S,B or C)','S')
        if(self.FTPClient.MODE(mode)==0):
            self.Log.insert(END,'Mode set to '+mode+'\n')
        else:
            self.Log.insert(END,'Could not complete\n')

    def doSTRU(self):#call stru of ftpclient class
        ftype=self.doPopUp('Fileype?','F')
        if(self.FTPClient.STRU(ftype)==0):
            self.Log.insert(END,'Filetype set to '+ftype+'\n')
        else:
            self.Log.insert(END,'Could not complete\n')

    def doPORT(self):#set client to passive and server to active
        ip=self.doPopUp('Enter IP')
        port=self.doPopUp('Enter Port')
        try:
            if(self.FTPClient.PORT(ip,int(port)) ==0):
                self.Log.insert(END,'Listen socket created at '+ip+':'+port+'\n')
                self.enableDataButtons()
            else:
                self.Log.insert(END,'Failed, invalid input...\n')
        except:
            self.Log.insert(END,'Failed, invalid input...\n')
            self.disableDataButtons()



        return
    
    def doPASV(self):#set client to active and server to passive
        self.FTPClient.PASV()
        self.enableDataButtons()
        self.Log.insert(END,'Created Passive Data soc \n')
        self.Log.insert(END,'Passive at: '+self.FTPClient.passiveIP +':'+str(self.FTPClient.passivePort) +'\n')
        return

    def doLIST(self):#execute list command from ftpclient class
        dir=self.doPopUp('Enter dir (leave blank for current dir)','')
        try:
            if(self.FTPClient.LIST(dir)==0):
              self.FileList.insert(END,self.FTPClient.list)
              self.Log.insert(END,'list obtained \n')
            else:
                self.Log.insert(END,'directory does not exist \n')

        except:
            self.Log.insert(END,'Could not obtain list \n')

        finally:
            self.disableDataButtons()#reset data buttons



        return

    def doSTOR(self):#attempt to store file on server 
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
            self.disableDataButtons()#reset data buttons


        return

    def doRETR(self):#attempt to retrieve file from server
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

    def doPWD(self):#get working directory from server

        try:
            curerntPath=self.FTPClient.PWD()
            self.Log.insert(END,curerntPath+' is the current path\n')
        except:
            self.Log.insert(END,'Could not retrieve cwd...\n')
        return

    def doCWD(self):#attempt to chagne wroking directory on server
        newDir=self.doPopUp('Directory?')

        try:
            if(self.FTPClient.CWD(newDir)==0):
                self.Log.insert(END,'Path was changes to: '+ newDir+'\n')
            else:
                self.Log.insert(END,'Could not change dir\n')

        except:
            self.Log.insert(END,'Could not change dir\n')
        return

    def doMKD(self):#attempt to make directory on server
        newDir=self.doPopUp('Directory?')

        try:
            if(self.FTPClient.MKD(newDir)==0):
                self.Log.insert(END,'Directory created: '+ newDir+'\n')
            else:
                self.Log.insert(END,'Could not create dir\n')

        except:
            self.Log.insert(END,'Could not create dir\n')
        return
    


    def enableDataButtons(self):#enable buttons related to using data connection
        self.listBtn['state']='normal'
        self.retrBtn['state']='normal'
        self.storBtn['state']='normal'


    def disableDataButtons(self):#disable buttons related to using data connection
        self.listBtn['state']='disabled'
        self.retrBtn['state']='disabled'
        self.storBtn['state']='disabled'


    
    def enableNonDataButtons(self):#enable buttons related to using control connection
        self.portBtn['state']='normal'
        self.pasvbBtn['state']='normal'
        self.typeBtn['state']='normal'
        self.pwdBtn['state']='normal'
        self.cwdBtn['state']='normal'
        self.mkdBtn['state']='normal'
        self.modeBtn['state']='normal'
        self.struBtn['state']='normal'

    
    def disableNonDataButtons(self):#disable buttons related to using control connection
        self.portBtn['state']='disabled'
        self.pasvbBtn['state']='disabled'
        self.typeBtn['state']='disabled'
        self.pwdBtn['state']='disabled'
        self.cwdBtn['state']='disabled'
        self.mkdBtn['state']='disabled'
        self.modeBtn['state']='disabled'
        self.struBtn['state']='disabled'




class popupWindow(object):
    def __init__(self,master,title,default=''):#initialise gui window
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



    


