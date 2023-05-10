# MinChat - minserver - Alpha 0.2

# MODULES ----------------------------------------------------------------------

import threading
import os, sys, argparse
import socket as skt
import tkinter as tkr

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



                        minclient - Version Alpha 0.2
+==+---------------------------------------------------------------------------+==+
'''
EXIT_MSG = 'Quitting MinChat client .. .  .   .    .     .      .       .'
PROMPT = lambda n: print(f"{n} -> ", end='') # 'Username: message goes here'


# SEND -------------------------------------------------------------------------

class Send(threading.Thread):
    '''Sends input from the client user to the server.'''

    def __init__(self, socket, name):
        super().__init__()
        self.socket = socket # Connection with server
        self.name = name # Username


    def run(self):
        while True:
            # Get text input from user:
            PROMPT(self.name)
            sys.stdout.flush() # Flush all data from stdout buffer.
            msg = sys.stdin.readline()[:-1] # Read line (not including last character)

            if msg == 'QUIT':
                self.socket.sendall(f'SERVER: {self.name} has left the chatroom.'.encode(ENCODING))
                break
            else:
                # Send message to server for posting:
                self.socket.sendall(f'{self.name}: {msg}'.encode(ENCODING))
        
        print(EXIT_MSG)
        self.socket.close() # Close connection with server and exit program.
        os._exit(0)


# RECEIVE ----------------------------------------------------------------------

class Receive(threading.Thread):
    '''Receives input from server to display to client user.'''

    def __init__(self, socket, name):
        super().__init__()
        self.socket = socket  # Connection to server.
        self.name = name  # Username
        self.msg_box = None # GUI element used to display messages.


    def run(self):
        while True:
            # Blocks until data received from server.
            # Returns '' if connection closed.
            msg = self.socket.recv(1024).decode(ENCODING)

            if msg:
                if self.msg_box:
                    # GUI ready:
                    print(f'\r{msg}')
                    self.msg_box.insert(tkr.END, msg) # Append message to GUI container.
                    PROMPT(self.name)
                else:
                    # GUI not ready yet:
                    print(f'\r{msg}')
                    PROMPT(self.name)
            else:
                print('Connection lost with server:\n\tContact server admin.')
                print(EXIT_MSG)
                self.socket.close() # Close socket and terminate program.
                os._exit(0)


# CLIENT -----------------------------------------------------------------------

class Client:
    '''Manages connection with server; instantiates Send and Receive threads.'''

    def __init__(self, host, port):
        self.host = host # Address of server hosting a chatroom.
        self.port = port # Port server is using for chatroom.
        self.socket = skt.socket(skt.AF_INET, skt.SOCK_STREAM) # Connection to server.
        self.name = None # Username
        self.msg_box = None # GUI element used to display messages.


    def start(self):
        '''
        Connects to chatroom server and initialize sending and receiving threads.
        Returns reference to receiving thread.
        '''

        print(SPLASH)
        # Create initial connection with server:
        print(f'Attempting to connect to {self.host}:{self.port} .. .  .   .    .     .')
        try:
            self.socket.connect((self.host, self.port))
        except:
            print(f'Could not connect to server:\n\tContact server admin.')
            self.socket.close() # If failure, close socket and terminate program.
            print(EXIT_MSG)
            os._exit(1)
        print(f'Connection with {self.host}:{self.port} established.')

        # Enter username for session:
        self.name = input('\n\nWho are you?\n---> ')
        print(
            f'\n\nWelcome {self.name}, to MinChat (server {self.host}:{self.port})!' +
            'Initializing chat .. .  .   .    .     .       .'
        )

        # Create and start threads for sending and receiving messages from server:
        outbox = Send(self.socket, self.name)
        inbox = Receive(self.socket, self.name)
        outbox.start()
        inbox.start()

        # Notify chatroom that new client has joined:
        self.socket.sendall(f'SERVER: {self.name} has entered the chatroom.'.encode(ENCODING))
        print("MinChat client initialized.\n\tDon't be shy.")
        PROMPT(self.name)
        
        # For GUI integration:
        return outbox
    

    def send(self, input_box):
        '''Sends data from GUI text input box to the server.'''

        # Get text from input, clear input element, and append input to messages element.
        msg = input_box.get() 
        input_box.delete(0, tkr.END)
        self.msg_box.insert(tkr.END, f'{self.name}: {msg}')

        # Special commands:
        if msg == 'QUIT':
            self.socket.sendall(f'SERVER: {self.name} has left the chatroom.'.encode(ENCODING))
            print(EXIT_MSG)
            self.socket.close() # Close connection and terminate program.
            os._exit(0)
        # More can be implemented through special server behaviour upon reception
        # of certain keywords. Perhaps special rendering could be provided
        # for votes or surveys initiated within the chatroom. -Trianan
        else:
            # Send message to server for posting:
            self.socket.sendall(f'{self.name}: {msg.encode(ENCODING)}')

    

# MAIN -------------------------------------------------------------------------

if __name__ == '__main__':

    # Define parameters passed through command line:
    arg_parser = argparse.ArgumentParser(description='MinChat Client')
    arg_parser.add_argument(
        'host',
        help='External IP interface of the server.')
    arg_parser.add_argument(
        '-p',
        metavar='PORT',
        type=int,
        default=DEFAULT_PORT,
        help=f'TCP port of server. (default {DEFAULT_PORT})'
    )
    # Get arguments from command line:
    args = arg_parser.parse_args()

    # Create client with cmd arguments, and start it:
    client = Client(args.host, args.p)
    client.start()