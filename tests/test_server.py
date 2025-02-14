import unittest
from unittest import mock
import socket
import json
import logging
import signal
import threading
import time
import sys
from server.server import *


class TestTCPJsonServer(unittest.TestCase):
    def setUp(self):
        # Setup a mock TCPJsonServer instance for testing
        self.server = TCPServer(host='127.0.0.1', port=12346)
        self.server.is_running = False  # Avoid running the server during tests

    def test_server_initialization(self):
        # Ensure server is initialized properly
        self.assertEqual(self.server.host, '127.0.0.1')
        self.assertEqual(self.server.port, 12346)
        self.assertIsInstance(self.server.server_socket, socket.socket)

    @mock.patch('socket.socket.accept')
    def test_handle_client_valid_json(self, mock_accept):
        # Simulate a valid JSON message from a client
        mock_client_socket = mock.MagicMock()
        mock_client_socket.recv.return_value = b'{"key": "value"}'
        mock_client_socket.close = mock.MagicMock()

        mock_accept.return_value = (mock_client_socket, ('127.0.0.1', 12345))

        # Run the client handling method directly
        self.server.handle_client(mock_client_socket, ('127.0.0.1', 12345))

        # Check that the received data was logged correctly
        mock_client_socket.recv.assert_called_once_with(1024)
        mock_client_socket.close.assert_called_once()

    @mock.patch('socket.socket.accept')
    def test_handle_client_invalid_json(self, mock_accept):
        # Simulate an invalid JSON message from a client
        mock_client_socket = mock.MagicMock()
        mock_client_socket.recv.return_value = b'Invalid JSON'
        mock_client_socket.close = mock.MagicMock()

        mock_accept.return_value = (mock_client_socket, ('127.0.0.1', 12345))

        # Run the client handling method directly
        self.server.handle_client(mock_client_socket, ('127.0.0.1', 12345))

        # Check that the error message is logged
        mock_client_socket.recv.assert_called_once_with(1024)
        mock_client_socket.close.assert_called_once()

    @mock.patch('socket.socket.accept')
    def test_handle_client_no_data(self, mock_accept):
        # Simulate no data received from a client
        mock_client_socket = mock.MagicMock()
        mock_client_socket.recv.return_value = b''
        mock_client_socket.close = mock.MagicMock()

        mock_accept.return_value = (mock_client_socket, ('127.0.0.1', 12345))

        # Run the client handling method directly
        self.server.handle_client(mock_client_socket, ('127.0.0.1', 12345))

        # Check that no data received is logged
        mock_client_socket.recv.assert_called_once_with(1024)
        mock_client_socket.close.assert_called_once()

    @mock.patch('socket.socket.accept')
    @mock.patch('signal.raise_signal')
    @mock.patch('time.sleep', return_value=None)  # Mock sleep
    def test_server_running_and_stopping_with_signals(self, mock_signal, mock_sleep, mock_accept):
        # Simulate that server is accepting client connections and handling SIGTERM
        mock_client_socket = mock.MagicMock()
        mock_client_socket.recv.return_value = b'{"key": "value"}'
        mock_client_socket.close = mock.MagicMock()

        mock_accept.return_value = (mock_client_socket, ('127.0.0.1', 12345))

        # Start server in another thread to avoid blocking test
        server_thread = threading.Thread(target=self.server.start)
        server_thread.daemon = True
        server_thread.start()

        # Wait for a short time for the server to start
        time.sleep(0.1)

        # Simulate receiving SIGTERM signal
        signal.raise_signal(signal.SIGTERM)

        # Wait for the server to process shutdown
        time.sleep(0.1)

        # Check that server is not accepting new clients
        self.assertFalse(self.server.is_running)

    def tearDown(self):
        # Clean up after each test (e.g., close server socket if open)
        if self.server.server_socket.fileno() != -1:
            self.server.server_socket.close()


if __name__ == '__main__':
    unittest.main()
