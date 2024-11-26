import socket, threading

from struct import pack, unpack

PORT = 42069
END_CONNECTION = "!END!"
LENGTH = 4

class Connection:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def send(self, msg:str, conn:socket.socket|None=None):
        if not conn:
            conn = self.socket
        try:
            msg_len = len(msg)
            send_len = pack('!I', msg_len)
            conn.send(send_len)
            conn.send(msg.encode())
        except socket.error as e:
            print(f'Send error: {e}')

    def recv(self, conn:socket.socket|None=None):
        if not conn:
            conn = self.socket
        try:
            msg_len = unpack('!I', conn.recv(LENGTH))[0]
            return conn.recv(msg_len).decode()
        except socket.error as e:
            print(f'Recv error: {e}')
    
    def accept(self):
        return self.socket.accept()
    
    def close(self):
        self.socket.close()

class Client(Connection):
    def __init__(self):
        super().__init__()
        search_ip_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        search_ip_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        search_ip_socket.settimeout(2)

        server_address = ('255.255.255.255', 9434)
        message = 'pfg_ip_broadcast_cl'

        try:
            while True:
                # Send data
                print('sending: ' + message)
                sent = search_ip_socket.sendto(message.encode(), server_address)

                # Receive response
                print('waiting to receive')
                data, server = search_ip_socket.recvfrom(4096)
                if data.decode('UTF-8') == 'pfg_ip_response_serv':
                    print('Received confirmation')
                    print('Server ip: ' + str(server[0]) )
                    SERVER = server[0]
                    break
                else:
                    print('Verification failed')
                
                print('Trying again...')
            
            
        finally:	
            search_ip_socket.close()

        self.socket.connect((SERVER, PORT))

class Server(Connection):
    def __init__(self):
        super().__init__()
        self.socket.bind(('0.0.0.0', PORT))
        self.socket.listen()

        search_ip_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        server_address = ('', 9434)

        search_ip_socket.bind(server_address)

        self.responde_search_ip_thread = threading.Thread(target=self.responde_search_ip, args=(search_ip_socket,))
        self.responde_search_ip_thread.start()

    def responde_search_ip(self, sock:socket.socket):
        while True:
            data, address = sock.recvfrom(4096)
            data = str(data.decode('UTF-8'))
            print('Received ' + str(len(data)) + ' bytes from ' + str(address) )
            print('Data:' + data)
            
            if data == 'pfg_ip_broadcast_cl':
                print('responding...')
                sent = sock.sendto('pfg_ip_response_serv'.encode(), address)
                print('Sent confirmation back')

