import socket, os
from threading import Thread
import pickle
import secrets
import customSHA256
import random, string

host_IP = '127.0.0.127'
host_port = 6944

server_IP = 'localhost'
server_port = 8025



class socketListener(Thread):

    def rcv_from_client_fwd_to_server(self):
        val = False
        self.c_socket.settimeout(4.0)   
        try:
            c_msg = self.c_socket.recv(1024)
            while c_msg:
                try:
                    # deserialize the c_message
                    # if there is a '.' in the data
                    if c_msg.find(b'.') != -1:
                        deserialized_c_msg = pickle.loads(c_msg)
                        print(f'client says Desrialized Msg is {deserialized_c_msg}')

                        m_p2 = deserialized_c_msg['m_p2']
                        m_s1 = deserialized_c_msg['m_s1']
                        h = deserialized_c_msg['h']

                        # 32 bytes string: M_star
                        n = 32
                        m_star = ''.join(random.choices(string.ascii_letters + string.digits, k=n)).encode('ascii')

                        hashObj = customSHA256.Sha256()
                        hashObj.h = h
                        print(f'len(m_p2 + m_star + m_s1): {len(m_p2 + m_star + m_s1)}')
                        hashObj.update(m_p2 + m_star + m_s1)
                        h = hashObj.h

                        print(f'The hash-s h is {h}')
                        # send the m_star:
                        print(f'The m_star is {m_star}')

                        send_material = {'h': h, 'm_star': m_star}
                        serialized_send_material = pickle.dumps(send_material)
                        self.c_socket.send(serialized_send_material)
                        
                        # receive the next message from the client
                        c_msg = self.c_socket.recv(1024)
                    else:
                        raise Exception('No full stop found')

                except Exception as e: # can't deserialize the c_message or no full stop found
                    print(f'There was an error: {e}')
                    self.s_socket.send(c_msg)
                    try:
                        print(f'client says {c_msg}')
                        print('--------------Single Break------------------')
                    except:
                        print(f'client says: some undecodable message')
                    val = True
                    c_msg = self.c_socket.recv(1024)

        except: # timeout
            c_msg = None

        self.c_socket.settimeout(None)
        return val
        
    def rcv_from_server_fwd_to_client(self):
        self.s_socket.settimeout(3.0)
        val = False
        try:
            s_msg = self.s_socket.recv(1024)
            while s_msg:
                try:
                    print(f'server says {s_msg}')
                    print('--------------Single Break------------------')
                except:
                    print(f'server says: some undecodable message')
                val = True
                self.c_socket.send(s_msg)
                s_msg = self.s_socket.recv(1024)
        except:
            s_msg = None

        self.s_socket.settimeout(None)
        return val

      

        # send the s_message to the client
        # self.c_socket.send(res)
    
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
            counter = 0
            while True:
                valOne = self.rcv_from_client_fwd_to_server()
                print('\n--------------Break------------------\n')
                valTwo = self.rcv_from_server_fwd_to_client()

                if not valOne and not valTwo:
                    counter += 1
                
                if counter == 2:
                    break

            self.c_socket.close()



pid = os.getpid()
sl = socketListener()
sl.start()
input('Socket is listening, press any key to abort...')
os.kill(pid,9)





   
  