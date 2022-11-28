import socket
import hmac
import hashlib
import pickle

server_IP = '127.0.0.127'
server_port = 6944

host_IP = 'localhost'
host_port = 8025

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((server_IP, server_port))

# create a HMAC object
h = hmac.new(b'key', digestmod=hashlib.sha256)

# serialize the HMAC object
h_bytes = pickle.dumps(h)

# send the HMAC object to the server
s.send(h_bytes)

s.quit()
