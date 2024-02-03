import socket
import pickle


class Network:
    def __init__(self, server, port):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = server
        self.port = port
        self.addr = (self.server, self.port)
        self.p = self.connect()

    def getP(self):
        return self.p

    def connect(self):
        try:
            self.client.connect(self.addr)
            x = self.client.recv(2048).decode()
            return x
        except Exception as e:
            print(e)
            pass

    def send(self, data):
        try:

            self.client.send(str.encode(data))

            # recieved_data = []
            # while True:
            #     packet = self.client.recv(2048*2)
            #     if not packet: break
            #     recieved_data.append(packet)
            # data_arr = pickle.loads(b"".join(data))
            # print (data_arr)
            # s.close()
            #FIXME implement packets so you can send larger objects

            return pickle.loads(self.client.recv(2048*5))
        except socket.error as e:
            print(e)

    def recieve(self):
        return pickle.loads(self.client.recv(2048*5))