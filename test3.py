import socket

# Define the server and port
server = '127.0.0.1'
port = 80

# Create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
s.connect((server, port))

# Send the HTTP request
request = 'GET / HTTP/1.1\r\nHost: {}\r\n\r\n'.format(server)
s.sendall(request.encode())

# Receive the response
response = s.recv(4096)

# Print the response
print(response.decode())

# Close the socket
s.close()