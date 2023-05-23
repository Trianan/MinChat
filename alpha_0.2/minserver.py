# MinChat - minserver - Alpha 0.2

# MODULES: ---------------------------------------------------------------------

import threading
import os, argparse
import socket as skt
from datetime import datetime


# GLOBAL CONSTANTS -------------------------------------------------------------

ENCODING = 'ascii'
DEFAULT_PORT = 1060
SESSION_START = datetime.today().isoformat().replace('T', '_').replace(':', '-')
ADMIN_LOG = f"./session_{SESSION_START}_admin.txt"
PUBLIC_LOG = f"./session_{SESSION_START}_client.txt"
HIST = '!HIST!'
HIST_RET = '!HIST_RETURN!'

def get_public_log():
    '''Returns the public chat log as a list of messages.'''
    with open(PUBLIC_LOG, 'r') as p_log:
        pl = p_log.readlines()[2:] # Slice gets rid of header in file.
        return pl

SPLASH = '''
+==+---------------------------------------------------------------------------+==+



::::    ::::  ::::::::::: ::::    :::  ::::::::  :::    :::     :::     ::::::::::: 
+:+:+: :+:+:+     :+:     :+:+:   :+: :+:    :+: :+:    :+:   :+: :+:       :+:     
+:+ +:+:+ +:+     +:+     :+:+:+  +:+ +:+        +:+    +:+  +:+   +:+      +:+     
+#+  +:+  +#+     +#+     +#+ +:+ +#+ +#+        +#++:++#++ +#++:++#++:     +#+     
+#+       +#+     +#+     +#+  +#+#+# +#+        +#+    +#+ +#+     +#+     +#+     
#+#       #+#     #+#     #+#   #+#+# #+#    #+# #+#    #+# #+#     #+#     #+#     
###       ### ########### ###    ####  ########  ###    ### ###     ###     ###     



                        minserver - Version Alpha 0.2
+==+---------------------------------------------------------------------------+==+
'''
HRULE = '-----------------------------------------------------------------------------------\n'


# SERVER -----------------------------------------------------------------------

class Server(threading.Thread):
    
    def __init__(self, host, port):
        super().__init__()
        self.host = host # Local computer's external IP address.
        self.port = port # Unused and unreserved port on local computer.
        self.connections = [] # Active connections with clients.
    
    def run(self):
        '''
            Starts this thread to listen for incoming connections.
            When a new connection to a client is established,
            this spawns a new thread which manages the connection
            to the client alongside this thread.
        '''
        print(SPLASH)
        print('\nStarting minserver .. .  .   .    .     .      .       .        . \n')

        # Initialize log files:
        with open(PUBLIC_LOG, 'w') as log:
            log.write(
                f'MinChat Public Log - Session Start: {SESSION_START} - ' +
                f'Server {self.host}:{self.port}\n' +
                HRULE
            )
        with open(ADMIN_LOG, 'w') as log:
            log.write(
                f'MinChat Administrator Log - Session Start: {SESSION_START} - ' +
                f'Server {self.host}:{self.port}\n' +
                HRULE
            )

        # Socket object created with defined address family and socket type:
        socket = skt.socket(skt.AF_INET, skt.SOCK_STREAM)

        # This allows server to reuse same port quickly
        # after a connection is closed on that port:
        socket.setsockopt(skt.SOL_SOCKET, skt.SO_REUSEADDR, 1)

        # Bind socket to socket address on local machine:
        socket.bind((self.host, self.port))

        # The socket is then used as a listening-socket for 
        # establishing incoming connections in the following loop:
        socket.listen(1)
        status_msg = f'SERVER STARTED SUCCESSFULLY.\nLISTENING AT: {socket.getsockname()}'
        print(status_msg)
        self.log_message(status_msg, False)

        while True:
            # Accept a new connection; blocks thread until one is received:
            client_sock, client_addr = socket.accept()

            status_msg = (
                f'NEW CONNECTION: Client {client_sock.getpeername()} -> Local {client_sock.getsockname()}'
            )
            print(status_msg)
            self.log_message(status_msg, False)

            # Create and start new thread to manage client connection; add to active connections:
            connection_sock = ConnectionSocket(client_sock, client_addr, self)
            connection_sock.start()
            self.connections.append(connection_sock)
            status_msg = (
                f'CONNECTION READY: Ready to receive data from {client_sock.getpeername()}'
            )
            print(status_msg)
            self.log_message(status_msg, False)

    def post_msg(self, msg, source):
        '''Send message from client to all other connected clients.'''
        for connection in self.connections:
            if connection.client_addr != source:
                connection.send(msg)
        self.log_message(msg)

    def msg_client(self, msg, client_addr):
        '''Sends a message from the server to an individual client'''
        for connection in self.connections:
            if connection.client_addr == client_addr:
                connection.send(msg)
                self.log_message(msg, False)
                return
        print('Could not message the given client.')

    def send_history(self, client_addr):
        with open(PUBLIC_LOG, 'r') as public_logs:
            print('CURRENT HISTORY: ')
            logs = f'{HIST_RET} |' + '|'.join(public_logs.readlines()[2:])
            self.msg_client(logs, client_addr)
            print('\tEND HISTORY')

        status_msg = f'SEND HISTORY: Sent public logs to client {client_addr}.'
        print(status_msg)
        self.log_message(status_msg, False)

    def remove_connection(self, connection):
        '''Remove client socket from connections.'''
        self.connections.remove(connection)

    def log_message(self, msg, public=True):
        '''
        Appends a message to both the public and admin log files by default,
        with the option of appending only to the admin log.
        '''
        if public:
            with open(PUBLIC_LOG, 'a') as p_log:
                p_log.write(msg + '\n')
        with open(ADMIN_LOG, 'a') as a_log:
            a_log.write(msg + '\n')
    

# CONNECTION SOCKET ------------------------------------------------------------

class ConnectionSocket(threading.Thread):

    def __init__(self, client_sock, client_addr, server):
        super().__init__()
        self.client_sock = client_sock # Connected socket between client and server.
        self.client_addr = client_addr # Client address.
        self.server = server # Reference to hosting server.

    def run(self):
        '''
        Starts this thread to listen for data sent by this connections client.
        '''
        while True:
            # Blocks thread until data is received from client:
            msg = self.client_sock.recv(1024).decode(ENCODING)
            if msg:
                status_msg = (
                    'MESSAGE RECEIVED: {} says...\n\t{!r}'.format(self.client_addr, msg)
                )
                print(status_msg)
                self.server.log_message(status_msg, False)

                # Check for special commands:
                if msg == HIST:
                    self.server.send_history(self.client_addr)

                # Forward msg to other clients:
                else:
                    self.server.post_msg(msg, self.client_addr)
            else:
                # Client closed connection (recv returned ''); cleanup connection:
                status_msg = (
                    f'CONNECTION CLOSED: {self.client_addr} has closed their connection.'
                )
                print(status_msg)
                self.server.log_message(status_msg, False)
                self.client_sock.close()
                self.server.remove_connection(self)
                return # Exit thread.
            
    def send(self, msg):
        '''
        Sends data to the connected client.
        '''
        self.client_sock.sendall(msg.encode(ENCODING)) # Sends all data in buffer.


# COMMAND ----------------------------------------------------------------------

def command(server):
    '''
    Sends commands to the server from the keyboard.
    '''
    while True:
        cmd = input('')

        if cmd == 'q': # quit

            # Close all connections:
            print(
                'COMMAND: quit (q)\n\t' + 
                f"Closing {len(server.connections)} active" + 
                f" connection{'s' if len(server.connections) != 1 else ''}..."
            )
            for connection in server.connections:
                connection.client_sock.close()

            # Shut down server:
            print('SHUTDOWN: Shutting down server...')
            os._exit(0)

        elif cmd == 'c': # clients
            # Show the addresses of all connected clients:
            print(
                'COMMAND: clients (c)\n\t' + 
                f"Displaying {len(server.connections)} active" + 
                f" connection{'s' if len(server.connections) != 1 else ''}..."
            )
            for connection in server.connections:
                print(f"\t{connection.client_addr}")

        elif cmd == 'm': # message client
            print('COMMAND: message client (m)\n\tEnter client IP > ', end='')
            client_ip = input()
            client_port = int(input('Enter client port > '))
            print(f'Enter your message to client {(client_ip, client_port)}\n\t > ', end='')
            msg = 'SERVER: ' + input()
            server.msg_client(msg, (client_ip, client_port))

            


 # MAIN ------------------------------------------------------------------------

if __name__ == '__main__':
    # Create terminal interface and argument parser:
    parser = argparse.ArgumentParser(description='Chatroom Server')
    parser.add_argument('host', help='Interface the server listens at')
    parser.add_argument('-p', metavar='PORT', type=int, default=DEFAULT_PORT,
                        help=f'TCP port (default {DEFAULT_PORT})')
    args = parser.parse_args()

    # Instantiate with external ip and port, and run server:
    server = Server(args.host, args.p) 
    server.start()

    # Create thread for command loop, and start it:
    command = threading.Thread(target=command, args=(server,))
    command.start()