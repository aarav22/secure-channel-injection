from tlslite import SMTP_TLS as Client, HandshakeSettings
from database import User
import socket
import sys

import ssl

# MAILClient class represents a client program for the server application
class MAILClient(Client):
    def __init__(self, hostname, port, email, password, is_registered): 
        super().__init__(hostname,port)
        settings = HandshakeSettings()
        settings.cipherNames = ["aes128"]
        settings.cipherNames = ["aes128"]
        settings.macNames = ["sha256"]
        settings.minVersion = (3, 3)
        settings.maxVersion = (3, 3)
        settings.useEncryptThenMAC = False
        self.starttls()
        self.authenticated = False
        self.user = self.sign_user(email, password, is_registered)
        self.inbox = ''

    def sign_user(self, email, password, is_registered):
        while(not self.authenticated):
            if is_registered:
                if self.login(email,password):
                    self.authenticated = True
                    return self.get_user(email, password)
                else:
                    raise 'Invalid Credentials'
            else:
                if self.register(email, password) is True:
                    self.authenticated = True
                    return self.get_user(email, password)
                else:
                    print('Unexpected error.')
            

    def login(self, email, password):
        auth_command = 'AUTH ' + str(email) + ' ' + str(password)
        code, message = self.docmd(auth_command)
        if(str(code) == '253'):
            print(str(code) + ' ' + str(message))
            return True
        else:
            print(str(code) + ' ' + str(message))
            return False
    
    def register(self, email, password):
        reg_command = 'REG ' + str(email) + ' ' + str(password)
        code, message = self.docmd(reg_command)
        if(str(code) == '253'):
            print(message)
            return True
        else:
            print(message)
            return False

    def get_user(self, email, password):
        getuser_command = 'GETUSER ' + str(email) + ' ' + str(password)
        code, user_id = self.docmd(getuser_command)
        return User(user_id,email,password)

    # calls web server
    def update_inbox(self):
        # change web server ip address
        HOST, PORT = 'localhost', 9999
        if(self.authenticated is True):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as web_client:
                web_client = ssl.wrap_socket(web_client, 'key.key', 'cert.cert')
                #connect to web server
                web_client.connect((HOST,PORT))
                
                # send user id
                web_client.sendall(bytes(str(self.user.id) + '\n', 'utf-8'))

                # send inbox length
                length = int(str(web_client.recv(1024), 'utf-8'))

                # receive emails, save them as inbox
                self.inbox = str(web_client.recv(length), 'utf-8')
        else:
            print('not authenticated')

client = MAILClient('127.0.0.127', 6944, 'test1@project.com', '12345', True)
sender = "Private Person <from@example.com>"
receiver = "A Test User <test2@project.com>"
message = f"""\
Subject: Hi Mailtrap
To: {receiver}
From: {sender}
This is a test e-mail message."""
try:
    print("main.py; sending mail")
    client.sendmail(sender, receiver, message)
    print('main.py; sendmail done')
except Exception as e:
    print('main.py; sendmail failed', e)