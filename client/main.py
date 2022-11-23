import socket 


proxy_IP = '127.0.0.127'
proxy_port = 6942

# connect to the proxy
c_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
c_socket.connect((proxy_IP, proxy_port))

# receive the thank you message from the proxy
msg = c_socket.recv(1024).decode()
print(f'Proxy says {msg}')

# send the OK msg to the proxy
c_socket.send('OK'.encode())

# receive fwding msg from the proxy
msg = c_socket.recv(1024).decode()
print(f'Proxy says: {msg}')

# send the s_message to the proxy
c_socket.send('This is a secret message from the client'.encode())

# receive the s_message from the proxy
msg = c_socket.recv(1024).decode()
print(f'Server says {msg}')

