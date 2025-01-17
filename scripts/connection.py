import socket, threading

from sys import exit
from struct import pack, unpack, error
from scripts.constants import PORT, END_CONNECTION, MESSAGE_LENGTH

class Connection:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.END_CONNECTION = END_CONNECTION
        self.connected = False

    def send(self, msg:str, sock:socket.socket) -> None:
        try:
            msg_len = len(msg)
            send_len = pack('!I', msg_len)
            sock.send(send_len)
            sock.send(msg.encode())
        except socket.error as e:
            print(f'Send error: {e}')

    def recv(self, sock:socket.socket) -> str:
        try:
            msg_len = unpack('!I', sock.recv(MESSAGE_LENGTH))[0]
            return sock.recv(msg_len).decode()
        except socket.error as e:
            print(f'Recv error: {e}')
        except error as e:
            print(f'Unpacking error: {e}')
    
    def close_connection(self) -> None:
        self.socket.close()

class Client(Connection):
    def __init__(self):
        super().__init__()
        self.servers_ip = []
        self.searching = True

        self.thread_search = threading.Thread(target=self.search_server_ip)
        self.thread_search.start()

    def connect(self, server_id: int):
        try:
            self.socket.connect((self.servers_ip[server_id], PORT))
            self.connected = True
            print('Connected to server')
        except socket.error as e:
            print(f'Error: {e}')
            print('Failed to connect to server')

    def close_connection(self) -> None:
        self.searching = False
        self.thread_search.join()
        self.socket.close()

    def search_server_ip(self) -> list:
        search_ip_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        search_ip_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        search_ip_socket.settimeout(2)

        server_address = ('255.255.255.255', 9434)
        message = 'pfg_ip_broadcast_cl'

        while self.searching:
            try:
                # Send data
                print('sending: ' + message)
                sent = search_ip_socket.sendto(message.encode(), server_address)

                # Receive response
                print('waiting to receive')
                data, server = search_ip_socket.recvfrom(4096)
                if data.decode('UTF-8') == 'pfg_ip_response_serv' and server[0] not in self.servers_ip:
                    print('Received confirmation')
                    print('Server ip: ' + str(server[0]) )
                    self.servers_ip.append(server[0])
                    self.searching = False
                else:
                    print('Verification failed')
                
                print('Trying again...')
            except socket.timeout:
                print('Timeout')
                print('Servers found: ' + str(len(self.servers_ip) ) )
            except Exception as e:
                print('Error: ' + str(e) )
                print("Try again")
        search_ip_socket.close()

class Server(Connection):
    def __init__(self):
        super().__init__()
        self.socket.settimeout(1)
        self.socket.bind(('0.0.0.0', PORT))
        self.socket.listen()

        self.conn = None
        self.addr = None

        self.accepting = True
        self.thread_response = threading.Thread(target=self.respond_search_ip)
        self.thread_response.start()
        self.thread_accept = threading.Thread(target=self.accept_connection)
        self.thread_accept.start()

    def accept_connection(self) -> None:
        while self.accepting:
            try:
                self.conn, self.addr = self.socket.accept()
                self.accepting = False
                print('Connected to', self.addr)
                self.connected = True
            except socket.timeout:
                pass
            except OSError as e:
                print(f'Error: {e}')
                if self.conn is not None:
                    self.conn.close()

    def close_connection(self) -> None:
        self.accepting = False
        self.thread_response.join()
        self.thread_accept.join()
        self.socket.close()
        if self.conn is not None:
            self.conn.close()
        print('Connection closed')

    def respond_search_ip(self) -> None:
        '''
        Respond to a broadcast message from a client
        '''
        search_ip_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_address = ('', 9434)
        search_ip_socket.bind(server_address)
        search_ip_socket.settimeout(1)

        while self.conn is None and self.accepting:
            try:
                data, address = search_ip_socket.recvfrom(4096)
                data = str(data.decode('UTF-8'))
                print('Received ' + str(len(data)) + ' bytes from ' + str(address) )
                print('Data:' + data)
                
                if data == 'pfg_ip_broadcast_cl':
                    print('responding...')
                    sent = search_ip_socket.sendto('pfg_ip_response_serv'.encode(), address)
                    print('Sent confirmation back')
            except socket.timeout:
                pass
            except Exception as e:
                print('Error: ' + str(e))
                print('Try again')
        search_ip_socket.close()