import socket, os
from threading import Thread

import pickle
import secrets
import customSHA256
import random, string
from tlslite.utils import python_aes

host_IP = '127.0.0.127'
host_port = 6944

mailtrapIP = "smtp.mailtrap.io"
mailtrapPort = 2525

outlookIP = "smtp-mail.outlook.com"
outlookPort = 587

server_IP = 'localhost'
server_port = 8025

bCRLF = b"\r\n"
CRLF = "\r\n"
START_MSG = 'START: Blind Certificate Protocol'

class socketListener(Thread):

    def rcv_from_client_fwd_to_server(self):
        val = False
        self.c_socket.settimeout(1.0)   
        try:
            c_msg = self.c_socket.recv(1024)
            while c_msg:
                try:
                    decoded_c_msg = c_msg.decode()
                    if decoded_c_msg.find(START_MSG) != -1:
                        self.c_socket.send(b'OK')
                        print('START OF BLIND CERTIFICATE PROTOCOL')

                        # 32 bytes string: M_star
                        n = 32
                        m_star = ''.join(random.choices(string.ascii_letters + string.digits, k=n)).encode('ascii')

                        c_msg = self.c_socket.recv(1024) # send m stars 1 message
                        print(f'rcvd request={c_msg.decode()}')

                        # split m_star into two parts
                        m_star1 = m_star[:16]
                        m_star2 = m_star[16:]

                        m_stars_1 = [''] * 3
                        m_stars_2 = [''] * 3
                        available_indices_1 = [0, 1, 2]
                        available_indices_2 = [0, 1, 2]
                        num_m_stars = 3
                        n = 16
                        for i in range(num_m_stars - 1):
                            # generate a random 16 byte string
                            rand_1 = ''.join(random.choices(string.ascii_letters + string.digits, k=n)).encode('ascii')
                            rand_2 = ''.join(random.choices(string.ascii_letters + string.digits, k=n)).encode('ascii')
                            # choose a random index
                            rand_index_1 = random.choice(available_indices_1)
                            rand_index_2 = random.choice(available_indices_2)
                            # add the random string to the list
                            m_stars_1[rand_index_1] = rand_1
                            m_stars_2[rand_index_2] = rand_2
                            # remove the index from the available indices
                            available_indices_1.remove(rand_index_1)
                            available_indices_2.remove(rand_index_2)
                        # add the m_star1 and m_star2 to the list at the random index
                        rand_index_1 = random.choice(available_indices_1)
                        rand_index_2 = random.choice(available_indices_2)
                        m_stars_1[rand_index_1] = m_star1
                        m_stars_2[rand_index_2] = m_star2

                        # send m_stars_1
                        send_material_serialized = pickle.dumps(m_stars_1)
                        self.c_socket.send(send_material_serialized)

                        # request for m_stars_2 recvd:
                        c_msg = self.c_socket.recv(1024)
                        print(f'rcvd request={c_msg.decode()}')

                        # send m_stars_2
                        send_material_serialized = pickle.dumps(m_stars_2)
                        self.c_socket.send(send_material_serialized)


                        # recevive cipher texts
                        c_msg = self.c_socket.recv(4048)
                        deserialized_c_msg = pickle.loads(c_msg)

                        # get the cipher text
                        correct_idx = (rand_index_1 + 1) * (rand_index_2 + 1) - 1
                        print(f'm_star1={m_star1}, m_star2={m_star2}, correct_idx={correct_idx}')
                        cipher_text = deserialized_c_msg[correct_idx]

                        # send ack
                        self.c_socket.send(b'OK')

                        # intercept the mail and send it to the server
                        c_msg = self.c_socket.recv(1024)
                        print(f'rcvd mail data: {c_msg}')
                        print(' ')

                        # copy the first 5 bytes of the mail
                        tls_header = c_msg[:5] # this is the tls header
                        new_mail = tls_header + cipher_text
                        c_msg = new_mail

                        print(f'new mail data: {new_mail}')
                        raise Exception('Protocol complete')
                    else:
                        raise Exception('No full stop found')

                except Exception as e: # can't deserialize the c_message or no full stop found
                    # print(f'There was an error: {e}')
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
        if self.counter > 0:
            self.s_socket.settimeout(3.0)
        else:
            self.s_socket.settimeout(1.0)

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
            # connect to the real server
            self.s_socket = socket.create_connection((outlookIP, outlookPort))
            self.counter = 0
            while True:
                valOne = self.rcv_from_client_fwd_to_server()
                print('\n--------------Break------------------\n')
                valTwo = self.rcv_from_server_fwd_to_client()

                if not valOne and not valTwo:
                    self.counter += 1
                
                if self.counter == 2:
                    break

            self.c_socket.close()



pid = os.getpid()
sl = socketListener()
sl.start()
input('Socket is listening, press any key to abort...')
os.kill(pid,9)





   
  