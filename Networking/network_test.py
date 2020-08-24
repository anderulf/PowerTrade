import socket
import time
import random


class Network:

    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "10.24.39.91"
        self.port = 5555
        self.addr = (self.server, self.port)
        self.id = self.connect()
        self.player = random.randint(1,11)

    def getPlayer(self):
        return self.player

    def connect(self):
        try:
            self.client.connect(self.addr)
            return self.client.recv(2048).decode()
        except:
            pass

    def send(self, data):
        try:
            self.client.send(str.encode(data))
            return self.client.recv(2048).decode()
        except socket.error as e:
            print(e)


n = Network()
msg = str("From: " + str(n.getPlayer()))
while True:
    n.send(msg)
    time.sleep(3)
