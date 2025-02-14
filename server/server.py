import socket
import json
import threading


class TCPJsonServer:
    def __init__(self, host='0.0.0.0', port=12345):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server listening on {self.host}:{self.port}")

    def handle_client(self, client_socket, client_address):
        print(f"Connection from {client_address[0]}:{client_address[1]}")

        try:
            data = client_socket.recv(1024).decode('utf-8')
            if data:
                json_data = json.loads(data)
                print(f"Received JSON from {client_address[0]}: {json_data}")
            else:
                print("No data received")
        except json.JSONDecodeError:
            print("Invalid JSON received")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            client_socket.close()

    def start(self):
        while True:
            client_socket, client_address = self.server_socket.accept()
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
            client_thread.start()


if __name__ == "__main__":
    server = TCPJsonServer()
    server.start()