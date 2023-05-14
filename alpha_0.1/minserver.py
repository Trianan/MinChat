# MINCHAT - MinServer - version alpha_0.1
# May 6 / 2023
# By: Trianan
# -----------------------------------------------------------------------------

import threading, socket, argparse, os
from datetime import datetime

H_RULE = '-----------------------------------------------------------------------------------\n'
SPLASH_STR = '''


::::    ::::  ::::::::::: ::::    :::  ::::::::  :::    :::     :::     ::::::::::: 
+:+:+: :+:+:+     :+:     :+:+:   :+: :+:    :+: :+:    :+:   :+: :+:       :+:     
+:+ +:+:+ +:+     +:+     :+:+:+  +:+ +:+        +:+    +:+  +:+   +:+      +:+     
+#+  +:+  +#+     +#+     +#+ +:+ +#+ +#+        +#++:++#++ +#++:++#++:     +#+     
+#+       +#+     +#+     +#+  +#+#+# +#+        +#+    +#+ +#+     +#+     +#+     
#+#       #+#     #+#     #+#   #+#+# #+#    #+# #+#    #+# #+#     #+#     #+#     
###       ### ########### ###    ####  ########  ###    ### ###     ###     ###     
                                                             
MinServer - Version Alpha 0.1 - TriaNaN Inc.
--------------------------------------------------------------------------------
'''
SESSION_START = datetime.today().isoformat()
HISTORY = f"./.sessions/session_{SESSION_START}.txt"
def get_current_history():
    # Send session history to client upon connection:
    current_history = []
    with open(HISTORY, 'r') as session_history:
        current_history = session_history.readlines()[2:]
        current_history = [ line.split('    ')[1].replace('\n', '') for line in current_history]
        current_history.insert(0, "_HIST_")
    print(f'DEBUG: Current history:\n\n{current_history}\n\n')
    return current_history


class Server(threading.Thread):
    def __init__(self, host, port):
        super().__init__()
        self.connections = []
        self.host = host
        self.port = port
    
    def run(self):
        print(SPLASH_STR)

        with open(HISTORY, 'w') as session_history:
            session_history.write(
                f'MINCHAT SERVER LOGS - SESSION {SESSION_START} - IP: {self.host} PORT: {self.port}\n' +
                H_RULE
            )

        skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        skt.bind((self.host, self.port))
        skt.listen(1)
        print("Listening at port", skt.getsockname())

        while True:
            client_skt, client_addr = skt.accept()
            print(f'Accepted a new connection from {client_skt.getpeername()} to {client_skt.getsockname()}')

            server_skt = ServerSocket(client_skt, client_addr, self)
            server_skt.start()
            self.connections.append(server_skt)

            print(f'Sending current history to {client_skt.getpeername()}...')
            hist = get_current_history()
            for line in hist:
                server_skt.send(line + '|')

            print(f'Ready to receive messages from {client_skt.getpeername()}')
    
    def broadcast(self, message, source):
        for connection in self.connections:
            if connection.sockname != source:
                connection.send(message)

    def remove_connection(self, server_skt):
        self.connections.remove(server_skt)


class ServerSocket(threading.Thread):
    def __init__(self, sc, sockname, server):
        super().__init__()
        self.sc = sc
        self.sockname = sockname
        self.server = server

    def run(self):
        while True:
            try:
                message = self.sc.recv(1024).decode('ascii')
            except:
                print("A client exited with not-fatal errors.")
            if message:
                print(('{!r}    {}').format(message, self.sockname))
                self.server.broadcast(message, self.sockname)
                with open(HISTORY, 'a') as session_history:
                    session_history.write(f'({datetime.today().isoformat()})    {message}\n')
            else:
                print(f'{self.sockname} has closed their connection.')
                self.sc.close()
                server.remove_connection(self)
                return
    
    def send(self, message):
        try:
            self.sc.sendall(message.encode('ascii'))
        except:
            print(f'Could not send message:\n\t{message}\n\n')


def exit(server):
    while True:
        action = input('')
        if action == 'q':
            print('Closing all connections...')
            for connection in server.connections:
                connection.sc.close()
            print('Shutting down server...')
            os._exit(0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MinServer')
    parser.add_argument('host', help='Interface the server listens at')
    parser.add_argument('-p', metavar='PORT', type=int, default=1060,
                        help='TCP port (default 1060)')
    args = parser.parse_args()

    # Create and start server thread
    server = Server(args.host, args.p)
    server.start()

    exit = threading.Thread(target = exit, args = (server,))
    exit.start()
