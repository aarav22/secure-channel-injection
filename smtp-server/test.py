from tlslite.api import *

email = 'e3658980310f3a'
password = 'cc5c386f9fcb0a'

server_add = 'localhost'
port = 8025

s = SMTP_TLS(server_add, port)
settings = HandshakeSettings()
settings.cipherNames = ["aes128"]
settings.cipherNames = ["aes128"]
settings.macNames = ["sha256"]
settings.minVersion = (3, 3)
settings.maxVersion = (3, 3)
settings.useEncryptThenMAC = False
try:
    s.ehlo()
    print('main.py; ehlo done')
except Exception as e:
    print('main.py; ehlo failed', e)

try:
    s.starttls(settings=settings)
    print('main.py; starttls done')
except Exception as e:
    print('main.py; starttls failed', e)

try:
    def login(email, password):
        auth_command = 'AUTH ' + str(email) + ' ' + str(password)
        code, message = s.docmd(auth_command)
        if(str(code) == '253'):
            print(str(code) + ' ' + str(message))
            return True
        else:
            print(str(code) + ' ' + str(message))
            return False
    s.login(email, password)
    print('main.py; login done')
except Exception as e:
    print('main.py; login failed', e)