# MINCHAT - MinServer - version alpha
# May 6 / 2023
# By: Trianan
# -----------------------------------------------------------------------------

import threading, socket, argparse, os


class Server(threading.Thread):
    def __init__(self, host, port):
        super().__init__()
        self.connections = []
        self.host = host
        self.port = port
    
    def run(self):
        skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        skt.bind((self.host, self.port))
        skt.listen(1)
        print("Listening at port", skt.getsockname())

        while True:
            client_skt, client_addr = skt.accept()
            print(f'Accepted a new connection from {client_skt.getpeername()} to {client_skt.getsockname()}')

            server_skt = ServerSocket(client_skt, client_addr, self) # To be defined.
            server_skt.start()
            self.connections.append(server_skt)
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
            message = self.sc.recv(1024).decode('ascii')
            if message:
                print(('{!r}    {}').format(message, self.sockname))
                self.server.broadcast(message, self.sockname)
            else:
                print(f'{self.sockname} has closed their connection.')
                self.sc.close()
                server.remove_connection(self)
                return
    
    def send(self, message):
        self.sc.sendall(message.encode('ascii'))


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