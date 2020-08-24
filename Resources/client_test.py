import socket
import time

class Client:
    def __init__(self):
        self.serverIp = "10.24.35.55"
        self.port = 5555
        self.message = "keep open"

    def connect(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.serverIp, self.port))
        while True:
            try:
                self.client.send(self.message.encode())
                from_server = self.client.recv(4096)
                end = time.time()
                delay = end - float(from_server.decode())
                print("Delay is "+ str(delay))
                time.sleep(1)
            except:
                print("Connection was lost. Closing..")
                break
        self.client.close()



client = Client()
client.connect()