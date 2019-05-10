"""File containing the handling of the connection to the opponent."""
import pickle
import socket


class Connection:
    def __init__(self, host, is_client, port=5000):
        """Initialize connection with opponent."""
        self.port = port
        self.mySocket = socket.socket()
        self.conn = None
        if is_client:
            self.mySocket.connect((host, port))
            self.conn = self.mySocket
        else:
            self.mySocket.bind((host, port))
            self.mySocket.listen(1)
            print("Your ip-address: {ip}".format(
                ip=(([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [
                    [(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in
                     [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0]))
            print("Waiting for enemy:")
            self.conn, addr = self.mySocket.accept()
            print("Connection from: {addr}".format(addr=addr))

    def send_data(self, data):
        """Send data from opponent."""
        self.conn.send(pickle.dumps(data))

    def receive_data(self):
        """Receive data from opponent."""
        return pickle.loads(self.conn.recv(1024))

    def close_connection(self):
        """Close the socket."""
        self.conn.close()
        self.mySocket.close()


if __name__ == "__main__":
    is_host_input = input("Host? [y/n] ")
    if is_host_input.upper() == "Y":
        c = Connection("0.0.0.0", False)
        print(c.receive_data())
        c.send_data([1, 2])
        c.close_connection()
    else:
        enemy_ip = input("Enemy ip: ")
        c = Connection(enemy_ip, True)
        c.send_data("hej")
        print(c.receive_data())
        c.close_connection()
