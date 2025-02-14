import socket
import json
import threading


def handle_client(client_socket, client_address):
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


def start_server(host='0.0.0.0', port=12345):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Server listening on {host}:{port}")

    while True:
        client_socket, client_address = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()


if __name__ == "__main__":
    start_server()
