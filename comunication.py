import socket


class Connection:
    def __init__(self, host, is_client, port=5000):
        self.port = port
        self.mySocket = socket.socket()
        self.conn = None
        if is_client:
            self.mySocket.connect((host, port))
            self.conn = self.mySocket
        else:
            self.mySocket.bind((host, port))
            self.mySocket.listen(1)
            print("Waiting for enemy:")
            self.conn, addr = self.mySocket.accept()
            print("Connection from: {}".format(addr))

    def send_message(self, message):
        self.conn.send(message.encode())

    def receive_message(self):
        return self.conn.recv(1024).decode()

    def close_connection(self):
        self.conn.close()
        self.mySocket.close()


if __name__ == "__main__":
    is_host_input = input("Host? [y/n] ")
    if is_host_input.upper() == "Y":
        c = Connection("0.0.0.0", False)
        print(c.receive_message())
        c.send_message("hej")
        c.close_connection()
    else:
        enemy_ip = input("Enemy ip: ")
        c = Connection(enemy_ip, True)
        c.send_message("hej")
        print(c.receive_message())
        c.close_connection()
