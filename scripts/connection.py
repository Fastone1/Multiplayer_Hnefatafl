import socket
from sys import exit

class Connection:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "127.0.0.1"
        self.port = 5555
        self.addr = (self.server, self.port)
        self.connect()

    def connect(self):
        try:
            self.client.connect(self.addr)
            return self.client.recv(2048).decode()
        except:
            print("Error connecting to the server")
            print("Closing the game...")
            print("Please try again later")
            self.client.close()
            exit()

    def send(self, data):
        try:
            length = str(len(data))
            self.client.send(str.encode(length))
            self.client.send(str.encode(data))
        except socket.error as e:
            print(e)

    def recv(self):
        try:
            length = int(self.client.recv(2048).decode())
            data = self.client.recv(length).decode()
            return data
        except socket.error as e:
            print(e)

class Server:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(("0.0.0.0", 5555))
        self.server.listen()
        print("Waiting for connection...")
        self.accept()
        
    def accept(self):
        conn, addr = self.server.accept()
        print(f"Connection from {addr}")
        conn.send(str.encode("Connected"))
        return conn
