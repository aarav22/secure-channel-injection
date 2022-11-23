import socket, os
from threading import Thread

host_IP = '127.0.0.127'
host_port = 6944

server_IP = '127.0.0.128'
server_port = 6943

class socketListener(Thread):
    def run(self):
        # Create a socket object
        p_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind to the port
        p_socket.bind((host_IP, host_port))

        while True:
            # Now wait for client connection.
            p_socket.listen()
            print(f"Listening at {host_IP} port {host_port}", end='\n\n')

            # Establish connection with client.
            self.c_socket, addr = p_socket.accept()
            print(f"Got connection from {addr}", end='\n\n')

            # Send a thank you message to the client.
            self.c_socket.send(b'Thank you for connecting to the PROXY server')

            # receive the message from the client
            msg = self.c_socket.recv(1024).decode()
            print(f'client says {msg}')

            ''' forward the connection to the real server '''

            self.c_socket.send(b'Forwarding connection to the REAL server; Send input')

            # receive the message for the real server
            c_msg = self.c_socket.recv(1024)

            # connect to the real server
            s_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s_socket.connect((server_IP, server_port))

            # receive the message from the real server
            msg = s_socket.recv(1024).decode()
            print(f'server says {msg}')

            # send the c_message to the real server
            s_socket.send(c_msg)

            # receive the s_message from the real server
            s_msg = s_socket.recv(1024)

            # send the s_message to the client
            self.c_socket.send(s_msg)

            # Close the connection
            self.c_socket.close()



pid = os.getpid()
sl = socketListener()
sl.start()
input('Socket is listening, press any key to abort...')
os.kill(pid,9)





   
  