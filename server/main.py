import socket
import os
from threading import Thread

# run the server

host_IP = '127.0.0.128'
host_port = 6943


class socketListener(Thread):
    def run(self):
        # Create a socket object
        s_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind to the port
        s_socket.bind((host_IP, host_port))

        while True:
            # Now wait for client connection.
            s_socket.listen()
            print(f"Real Server Listening at {host_IP} port {host_port}", end='\n\n')

            # Establish connection with client.
            c_socket, addr = s_socket.accept()
            print(f"Got connection from {addr}", end='\n\n')

            # Send a thank you message to the client.
            c_socket.send(b'Thank you for connecting to the REAL server')

            # receive the message from the client
            msg = c_socket.recv(1024).decode()
            print(f'client says {msg}')

            # send the message to the client
            c_socket.send(b'OK. Received your secret message')

            
            # Close the connection
            c_socket.close()



pid = os.getpid()
sl = socketListener()
sl.start()
input('Socket is listening, press any key to abort...')
os.kill(pid,9)