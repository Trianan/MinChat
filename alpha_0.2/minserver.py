# MinChat - minserver - Alpha 0.2

# MODULES: ---------------------------------------------------------------------

import threading, argparse, os
import socket as skt


# GLOBAL CONSTANTS -------------------------------------------------------------

ENCODING = 'ascii'
DEFAULT_PORT = 1060

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
        print(f'LISTENING AT: {socket.getsockname()}')

        while True:
            # Accept a new connection; blocks thread until one is received:
            client_sock, client_addr = socket.accept()
            print(f'NEW CONNECTION: Client {client_sock.getpeername()} -> Local {client_sock.getsockname()}')

            # Create and start new thread to manage client connection; add to active connections:
            connection_sock = ConnectionSocket(client_sock, client_addr, self)
            connection_sock.start()
            self.connections.append(connection_sock)
            print(f'CONNECTION READY: Ready to receive data from {client_sock.getpeername()}')
    
    def post_message(self, message, source):
        '''Send message from client to all other connected clients.'''
        for connection in self.connections:
            if connection.client_addr != source:
                connection.send(message)


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
            message = self.client_sock.recv(1024).decode(ENCODING)
            if message:
                print('MESSAGE RECEIVED: {} says...\n\t{!r}'.format(self.client_addr, message))
                # Forward message to other clients:
                self.server.broadcast(message, self.client_addr)
            else:
                # Client closed connection (recv returned ''); cleanup connection:
                print(f'CONNECTION CLOSED: {self.client_addr} has closed their connection.')
                self.client_sock.close()
                self.server.remove_connection(self)
                return # Exit thread.
            
    def send(self, message):
        '''
        Sends data to the connected client.
        '''
        self.client_sock.sendall(message.encode(ENCODING)) # Sends all data in buffer.


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


 # -----------------------------------------------------------------------------

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
