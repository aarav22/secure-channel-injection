import socket, os
from threading import Thread

host_IP = '127.0.0.127'
host_port = 6944

server_IP = 'localhost'
server_port = 8025



class socketListener(Thread):

    def rcv_from_client_fwd_to_server(self):
        c_msg = self.c_socket.recv(1024)
        
        try:
            print(f'client says {c_msg.decode()}')
        except:
            print(f'client says: some undecodable message')
        
        # send the STARTTLS message to the real server
        self.s_socket.send(c_msg)

    def rcv_from_server_fwd_to_client(self):
        s_msg = self.s_socket.recv(1024)
        try:
            print(f'server says {s_msg.decode()}')
        except:
            print(f'server says: some undecodable message')

        # send the s_message to the client
        self.c_socket.send(s_msg)
    
    def run(self):
        # Create a socket object
        self.p_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind to the port
        self.p_socket.bind((host_IP, host_port))

        while True:
            # Now wait for client connection.
            self.p_socket.listen()
            print(f"Listening at {host_IP} port {host_port}", end='\n\n')

            # Establish connection with client.
            self.c_socket, addr = self.p_socket.accept()
            print(f"Got connection from {addr}", end='\n\n')

            ''' forward the connection to the real server '''
            # TODO: The connection is still being made from proxy to server, not from client to server
            # connect to the real server
            self.s_socket = socket.create_connection((server_IP, server_port))

            # receive the first message from the real server
            self.rcv_from_server_fwd_to_client()

            # receive the STARTTLS message from the client
            self.rcv_from_client_fwd_to_server()
           

            # receive the response from the real server
            self.rcv_from_server_fwd_to_client()

            # receive the OK message from the client
            self.rcv_from_client_fwd_to_server()

            # receive the s_message from the real server
            self.rcv_from_server_fwd_to_client()

            # receive the s_message from the real server
            self.rcv_from_server_fwd_to_client()

            # receive the c_message from the client
            self.rcv_from_client_fwd_to_server()

            # Close the connection
            self.c_socket.close()



pid = os.getpid()
sl = socketListener()
sl.start()
input('Socket is listening, press any key to abort...')
os.kill(pid,9)





   
  