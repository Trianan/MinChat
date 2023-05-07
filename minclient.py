# MINCHAT - MinClient - version alpha
# May 6 / 2023
# By: Trianan
# -----------------------------------------------------------------------------

import threading, socket, argparse, os

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
            message = input(f'{self.name} > ')

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

    def run(self):
        while True:
            try:
                message = self.skt.recv(1024)
            except:
                self.skt.close()
                os._exit(1)
            
            if message:
                print(f"\r{message.decode('ascii')}\n{self.name} > ", end='')
            else:
                print('\nConnection to server lost; contact server admin.\nQuitting MinClient...')
                self.skt.close()
                os._exit(0)


class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def start(self):
        print(SPLASH_STR)
        print(f'Attempting connection to {self.host}:{self.port}...')
        self.skt.connect((self.host, self.port))
        print(f'Successfully connected!\r')
        name = input('Your name: ')
        print(f"\rWelcome to MinChat server {self.host}:{self.port} {name}!")
        print('Getting ready to send and receive messages...')

        send = Send(self.skt, name)
        receive = Receive(self.skt, name)
        receive.start()

        self.skt.sendall(f'SERVER: {name} joined the chatroom.'.encode('ascii'))
        print("\rYou are ready to chat. Quit the chatroom by typing QUIT.\n")
        send.start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Chatroom Server')
    parser.add_argument('host', help='Interface the server listens at')
    parser.add_argument('-p', metavar='PORT', type=int, default=1060,
                        help='TCP port (default 1060)')
    args = parser.parse_args()

client = Client(args.host, args.p)
client.start()
