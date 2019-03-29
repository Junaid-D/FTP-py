import socket

ServerIP='127.0.0.1'
port = 4500
serv_resp=''

with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as soc:
    soc.connect((ServerIP,port))
    while serv_resp != 'close':
        toSend=input("Input Data to send \n")
        soc.sendall(toSend.encode('ascii'))
        serv_resp=soc.recv(1024).decode('ascii')

