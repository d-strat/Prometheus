import socket
import json
import threading
import signal
import sys
import logging


class TCPJsonServer:
    def __init__(self, host='0.0.0.0', port=12345):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        logging.info(f"Server listening on {self.host}:{self.port}")
        self.is_running = True  # Server state

    def handle_client(self, client_socket, client_address):
        logging.info(f"Connection from {client_address[0]}:{client_address[1]}")

        try:
            data = client_socket.recv(1024).decode('utf-8')
            if data:
                json_data = json.loads(data)
                logging.info(f"Received JSON from {client_address[0]}: {json_data}")
            else:
                logging.info("No data received")
        except json.JSONDecodeError:
            logging.info("Invalid JSON received")
        except Exception as e:
            logging.error(f"Error: {e}")
        finally:
            client_socket.close()

    def start(self):
        while self.is_running:
            try:
                client_socket, client_address = self.server_socket.accept()
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
                client_thread.start()
            except Exception as e:
                logging.error(f"Error accepting connection: {e}")

        self.shutdown()

    def shutdown(self):
        logging.info("Shutting down the server...")
        self.server_socket.close()

    def handle_signals(self):
        signal.signal(signal.SIGTERM, self.stop_server)

    def stop_server(self, signum, frame):
        logging.info("SIGTERM received. Stopping the server...")
        self.is_running = False


if __name__ == "__main__":
    server = TCPJsonServer()

    # Start the server
    server.start()
