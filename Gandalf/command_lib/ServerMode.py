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
##Start Socket
def _startSocket(output):
    try:
        s = socket.socket()
        s.bind(('', 13912))
        s.close()
        port = 13912
        output('Using default port 13912')
    except:
        output('Default port unusable. Finding open port')
        port = _findOpenPort()
        output('Port selected is '+str(port))
        output('This message will repeat in five seconds')
        time.sleep(5)
        output('Port selected is '+str(port))
    s = socket.socket()
    s.bind(('', port))
    return s
#Main
def run_server(output, passkey, printBuffer):
    try:
        s = _startSocket(output)
        output('Server setup')
        serverRunning = True
    except Exception as e:
        print (e)
        output('Fatal error: Unable to run server')
        return
    while serverRunning:
        # Commands:
        #"exit"=Leave session, keep server open
        #"close"=Leave session, close server
        #anything else runs a command in the shell
        try:
            try:
                s.listen()
            except OSError:
                print ('Socket is closed. Restarting...')
                s = _startSocket(output)
                s.listen()
            conn,addr = s.accept()
            output('Connection accepted from '+str(addr))
            if passkey == '':
                auth = True
                conn.sendall(bytes('_NO_PASSWORD_REQUIRED', 'UTF-8'))
            else:
                auth = False
            while True:
                if auth:
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
                    elif data.lower() == 'print':
                        for i in printBuffer:
                            conn.sendall(bytes(i, 'UTF-8'))
                            print ('Send '+i)
                        while printBuffer != []:
                            del printBuffer[0]
                        print ('Flushed printBuffer')
                        conn.sendall(bytes('_DONE_SENDING_PRINT_BUFFER', 'UTF-8'))
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
                else:
                    print ('Waiting for authentication')
                    conn.sendall(bytes('_AUTH', 'UTF-8'))
                    data = conn.recv(1024)
                    if not data:
                        output('Authentication failed')
                        conn.sendall(bytes('_AUTH_FAILURE', 'UTF-8'))
                        break
                    data = data.decode('UTF-8')
                    if data.startswith('_AUTH='):
                        inPass = data[6:]
                    else:
                        inPass = None
                    if inPass == passkey:
                        print ('Authentication successful')
                        conn.sendall(bytes('_AUTH_SUCCESS', 'UTF-8'))
                    else:
                        print ('Authentication failure')
                        conn.sendall(bytes('_AUTH_FAIL', 'UTF-8'))
                        break
            s.close()
            output('Server closed')
        except ConnectionResetError:
            output('Connection was forcebly closed by the remote client')
            break
        except Exception as e:
            print (e)
            output('A fatal exception has occured. Server closed')
            return
