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
            return data
#Main
def main():
    ip = input('Enter IP >')
    port = int(input('Enter Port (Default is 13912) >'))
    s = connect(ip, port)
    print ('Pro tip: Don\'t use vim or any other text editor or anything similar. You may have to shutdown whatever is running Gandalf, and even if you don\'t, it won\'t work anyways.')
    res = modified_send(s, '_AUTH')
    if res == '_NO_PASSWORD_REQUIRED':
        print ('No password required for authentication.')
    else:
        print ('Password is required for authentication.')
        password = input('Enter password >')
        res = modified_send(s, bytes('_AUTH='+password, 'UTF-8'))
        if res == '_AUTH_SUCCESS':
            print ('Authentication successful')
        else:
            print ('Authentication failure')
            return False
    while True:
        print ('Commands:\n-"exit": Disconnect\n-"close": Disconnect and close server\n-"print": Prints all previous console messages')
        command = input('Enter OS Command Or Other Command\n>')
        if command.lower() == 'exit':
            send(s, 'exit')
            break
        elif command.lower() == 'close':
            send(s, 'close')
            break
        elif command.lower() == 'print':
            print ('---PRINT BUFFER---')
            send(s, 'print')
            while True:
                data = s.recv(1024)
                data = data.decode('UTF-8')
                if data == '_DONE_SENDING_PRINT_BUFFER':
                    break
                else:
                    print (data)
            print ('---END OF PRINT BUFFER---')
        else:
            modified_send(s, command)
    return True
main()
