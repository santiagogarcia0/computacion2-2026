import socket

with socket.create_connection(('localhost', 8080)) as s:
    s.sendall(b'hola mundo\n')
    while True:
        pedazo = s.recv(4)          # de a 4 bytes a propósito
        if not pedazo:
            break
        print(f'recv devolvió: {pedazo!r}')