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
HIST = '!HIST!'
HIST_RET = '!HIST_RETURN!'



# SEND -------------------------------------------------------------------------

class Send(threading.Thread):
    '''Sends input from the client terminal to the server.'''

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
                print(EXIT_MSG)
                self.socket.close() # Close connection with server and exit program.
                os._exit(0)
            else:
                # Send message to server for posting:
                self.socket.sendall(f'{self.name}: {msg}'.encode(ENCODING))


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
                    if msg.split('|')[0].strip() == HIST_RET:
                        for line in msg.split('|')[1:]:
                            print(f'\r{line}')
                            self.msg_box.insert(tkr.END, line) # Append message to GUI container.
                    else:
                        print(f'\r{msg}')
                        self.msg_box.insert(tkr.END, msg) # Append message to GUI container.
                    PROMPT(self.name)
                else:
                    # GUI not ready yet:
                    if msg.split('|')[0].strip() == HIST_RET:
                        for line in msg.split('|')[1:]:
                            print(f'\r{line}')
                    else:
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
            '\n\nInitializing chat .. .  .   .    .     .       .'
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
        return inbox
    

    def send(self, input_box): 
        '''Sends data from GUI text input box to the server.'''

        # Get text from input, clear input element, and append input to messages element.
        msg = input_box.get() 
        input_box.delete(0, tkr.END)

        # Special commands:
        if msg == 'QUIT':
            self.socket.sendall(f'SERVER: {self.name} has left the chatroom.'.encode(ENCODING))
            print(EXIT_MSG)
            self.socket.close() # Close connection and terminate program.
            os._exit(0)
        # More can be implemented through special server behaviour upon reception
        # of certain keywords. Perhaps special rendering could be provided
        # for votes or surveys initiated within the chatroom. -Trianan
        elif msg == HIST:
            self.socket.sendall(msg.encode(ENCODING))
        else:
            # Send message to server for posting:
            self.socket.sendall(f'{self.name}: {msg}'.encode(ENCODING))
            self.msg_box.insert(tkr.END, f'{self.name}: {msg}')
            print(f'{self.name}: {msg}')

    

# MAIN -------------------------------------------------------------------------

def main(host, port):
    '''Initializes and runs GUI. Takes server IP and port as arguments.'''
    # Initialize client and reference to receiving thread:
    client = Client(host, port)
    inbox = client.start()

    # Create GUI window:
    window = tkr.Tk()
    window.title('.     .    .   .  . .. MinChat Client .. .  .   .    .     .')

    # Initialize frame with scrollbar for viewing chatroom messages:
    msg_frame = tkr.Frame(master=window)
    scrollbar = tkr.Scrollbar(master=msg_frame)
    msg_box = tkr.Listbox(
        master=msg_frame,
        yscrollcommand=scrollbar.set,
        fg='spring green',
        bg='black'
    )
    scrollbar.pack(side=tkr.RIGHT, fill=tkr.Y, expand=False)
    msg_box.pack(side=tkr.LEFT, fill=tkr.BOTH, expand=True)

    # Assign GUI message frame to client's GUI outbox and inbox reference:
    client.msg_box = msg_box
    inbox.msg_box = msg_box

    # Define messages spatial area, and a text input box:
    msg_frame.grid(row=0, column=0, columnspan=2, sticky='nsew')
    entry_frame = tkr.Frame(master=window)
    input_box = tkr.Entry(master=entry_frame)
    input_box.pack(fill=tkr.BOTH, expand=True)

    # Bind ENTER key to sending text in input box to server:
    input_box.bind("<Return>", lambda e: client.send(input_box))
    # Define 'send' button for same purpose:
    send_btn = tkr.Button(
        master=window,
        text='Post',
        command=lambda: client.send(input_box)
    )

    # Define spatial areas for input box and send button:
    entry_frame.grid(row=1, column=0, padx=10, sticky='ew')
    send_btn.grid(row=1, column=1, padx=10, sticky='ew')

    # Define where the elements will be positioned within the window:
    window.rowconfigure(0, minsize=500, weight=1)
    window.rowconfigure(1, minsize=50, weight=0)
    window.columnconfigure(0, minsize=500, weight=1)
    window.columnconfigure(1, minsize=200, weight=0)

    window.configure(background='black')

    input_box.insert(0, HIST)
    client.send(input_box) # Client requests history once GUI initialized.
    window.mainloop() # This blocks from here.


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

    # Start the client and GUI:
    main(args.host, args.p)