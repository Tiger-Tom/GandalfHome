#Imports
import socket
#Functions
def connect(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))
    return s
def send(sock, data):
    sock.sendall(bytes(data, 'UTF-8'))
def modified_send(sock, data):
    sock.sendall(bytes(data, 'UTF-8'))
    while True:
        data = sock.recv(1024)
        data = data.decode('UTF-8')
        if data == '_END':
            break
        else:
            print (data)
#Main
def main():
    ip = input('Enter IP >')
    port = int(input('Enter Port (Default is 13912) >'))
    s = connect(ip, port)
    print ('Pro tip: Don\'t use vim or any other text editor or anything similar. You may have to shutdown whatever is running Gandalf, and even if you don\'t, it won\'t work anyways.')
    while True:
        print ('Commands:\n-"exit": Disconnect\n-"close": Disconnect and close server')
        command = input('Enter OS Command Or Other Command\n>')
        if command.lower() == 'exit':
            send(s, 'exit')
            break
        elif command.lower() == 'close':
            send(s, 'quit')
            break
        else:
            modified_send(s, command)
main()
