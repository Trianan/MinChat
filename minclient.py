# MINCHAT - MinClient - version alpha
# May 6 / 2023
# By: Trianan
# -----------------------------------------------------------------------------

import threading, socket, argparse, os, sys
import tkinter as tk

SPLASH_STR = '''


 /@@      /@@ /@@            /@@@@@@  /@@                   /@@    
| @@@    /@@@|__/           /@@__  @@| @@                  | @@    
| @@@@  /@@@@ /@@ /@@@@@@@ | @@  \__/| @@@@@@@   /@@@@@@  /@@@@@@  
| @@ @@/@@ @@| @@| @@__  @@| @@      | @@__  @@ |____  @@|_  @@_/  
| @@  @@@| @@| @@| @@  \ @@| @@      | @@  \ @@  /@@@@@@@  | @@    
| @@\  @ | @@| @@| @@  | @@| @@    @@| @@  | @@ /@@__  @@  | @@ /@@
| @@ \/  | @@| @@| @@  | @@|  @@@@@@/| @@  | @@|  @@@@@@@  |  @@@@/
|__/     |__/|__/|__/  |__/ \______/ |__/  |__/ \_______/   \___/  
                                                             
MinClient - Version Alpha - TriaNaN Inc.
--------------------------------------------------------------------------------
'''


class Send(threading.Thread):
    def __init__(self, skt, name):
        super().__init__()
        self.skt = skt
        self.name = name

    def run(self):
        while True:
            print('{}: '.format(self.name), end='')
            sys.stdout.flush()
            message = sys.stdin.readline()[:-1]

            if message == 'QUIT':
                self.skt.sendall(f'SERVER: {self.name} left the chatroom.'.encode('ascii'))
                break
            else:
                self.skt.sendall(f'{self.name}: {message}'.encode('ascii'))

        print('\nQuitting MinClient...')
        self.skt.close()
        os._exit(0)


class Receive(threading.Thread):
    def __init__(self, skt, name):
        super().__init__()
        self.skt = skt
        self.name = name
        self.messages = None

    def run(self):
        while True:
            try:
                message = self.skt.recv(1024).decode('ascii')
            except:
                #self.skt.close()
                os._exit(1)
            
            if message:
                if self.messages:
                    self.messages.insert(tk.END, message)
                print(f"\r{message}\n{self.name} > ", end='')
            else:
                print('\nConnection to server lost; contact server admin.\nQuitting MinClient...')
                self.skt.close()
                os._exit(0)


class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.name = None
        self.messages = None
    
    def start(self):
        print(SPLASH_STR)
        print(f'Attempting connection to {self.host}:{self.port}...')
        self.skt.connect((self.host, self.port))
        print(f'Successfully connected!\r')
        self.name = input('Your name: ')
        print(f"\rWelcome to MinChat server {self.host}:{self.port} {self.name}!")
        print('Getting ready to send and receive messages...')

        send = Send(self.skt, self.name)
        receive = Receive(self.skt, self.name)
        receive.start()

        self.skt.sendall(f'SERVER: {self.name} joined the chatroom.'.encode('ascii'))
        print("\rYou are ready to chat. Quit the chatroom by typing QUIT.\n")
        send.start()

        return receive
    
    def send(self, text_input):
        msg = text_input.get()
        text_input.delete(0, tk.END)
        self.messages.insert(tk.END, f'{self.name}: {msg}')

        if msg == 'QUIT':
            self.skt.sendall(f'SERVER: {self.name} left the chatroom.'.encode('ascii'))
            print('\nQuitting MinClient...')
            self.skt.close()
            os._exit(0)
        else:
            self.skt.sendall(f'{self.name}: {msg}'.encode('ascii'))


def main(host, port):
    client = Client(host, port)
    receive = client.start()
    window = tk.Tk()
    window.title('MinChat - minclient version alpha')

    frm_messages = tk.Frame(master=window)
    scrollbar = tk.Scrollbar(master=frm_messages)
    messages = tk.Listbox(
        master=frm_messages,
        yscrollcommand=scrollbar.set
    )
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y, expand=False)
    messages.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    client.messages = messages
    receive.messages = messages

    frm_messages.grid(row=0, column=0, columnspan=2, sticky='nsew')
    frm_entry = tk.Frame(master=window)
    text_input = tk.Entry(master=frm_entry)
    text_input.pack(fill=tk.BOTH, expand=True)
    text_input.bind("<Return>", lambda x: client.send(text_input))
    text_input.insert(0, "Your message here.")

    btn_send = tk.Button(
        master=window,
        text='Send',
        command=lambda: client.send(text_input)
    )

    frm_entry.grid(row=1, column=0, padx=10, sticky="ew")
    btn_send.grid(row=1, column=1, pady=10, sticky="ew")

    window.rowconfigure(0, minsize=500, weight=1)
    window.rowconfigure(1, minsize=50, weight=0)
    window.columnconfigure(0, minsize=500, weight=1)
    window.columnconfigure(1, minsize=200, weight=0)

    window.mainloop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Chatroom Server')
    parser.add_argument('host', help='Interface the server listens at')
    parser.add_argument('-p', metavar='PORT', type=int, default=1060,
                        help='TCP port (default 1060)')
    args = parser.parse_args()

    main(args.host, args.p)
