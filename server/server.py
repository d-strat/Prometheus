import socket
import json


def start_server(host='0.0.0.0', port=12345):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Server listening on {host}:{port}")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address[0]}:{client_address[1]}")

        try:
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                continue

            json_data = json.loads(data)
            print(f"Received JSON from {client_address[0]}: {json_data}")
        except json.JSONDecodeError:
            print("Invalid JSON received")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            client_socket.close()


if __name__ == "__main__":
    start_server()