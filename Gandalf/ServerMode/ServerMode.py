#Imports
import socket
import os
import time
#Functions
##Run Command
def _runCommand(command):
    print (command)
    data = os.popen(command)
    return data.read()
##Server Prep Functions
def _findOpenPort():
    s = socket.socket()
    s.bind(('', 0))
    port = s.getsockname()[1]
    print (s.getsockname())
    s.close()
    return port
#Main
def run_server(output):
    try:
        s = socket.socket()
        s.bind(('', 13912))
        s.close()
        port = 13912
        output('Using default port one three nine one two')
    except:
        output('Default port unusable. Finding open port')
        port = _findOpenPort()
        output('Port selected is '+str(port))
        output('This message will repeat in five seconds')
        time.sleep(5)
        output('Port selected is '+str(port))
    s = socket.socket()
    s.bind(('', port))
    output('Server setup')
    serverRunning = True
#try:
    while serverRunning:
        # Commands:
        #"exit"=Leave session, keep server open
        #"close"=Leave session, close server
        #anything else runs a command in the shell
        try:
            s.listen()
            conn,addr = s.accept()
            output('Connection accepted from '+str(addr))
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                data = data.decode('UTF-8')
                print ('Data recieved: "'+str(data)+'"')
                if data.lower() == 'exit':
                    break
                elif data.lower() == 'close':
                    serverRunning = False
                    break
                else:
                    try:
                        out = _runCommand(data)
                        conn.sendall(bytes(out, 'UTF-8'))
                        conn.sendall(bytes('_END', 'UTF-8'))
                    except Exception as e:
                        print ('Error running command')
                        print (e)
                        conn.sendall(bytes('Error > The server encountered an error running the command', 'UTF-8'))
                        conn.sendall(bytes('_END', 'UTF-8'))
            s.close()
            output('Server closed')
        except ConnectionResetError:
            output('Connection was forcebly closed by the remote client')
            break
