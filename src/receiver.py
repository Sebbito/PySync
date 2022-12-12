#!/bin/python3
import os
import tqdm
import socket as s
# import socketserver as ss

class Receiver(object):
    def __init__(self):
        self.address = "0.0.0.0"
        self.port = 8008
        self.socket = s.socket()
        self.socket.bind((self.address, self.port))
        self.SEPARATOR = "[SEP]"
        self.BUFFER_SIZE = 4096

    def __exit__(self, *args):
        self.socket.close()

    def receive_file(self):
        SEPARATOR= self.SEPARATOR
        BUFFER_SIZE = self.BUFFER_SIZE
        
        self.socket.listen(5)
        client_socket, address = self.socket.accept()

        # receive the file infos
        # receive using client socket, not server socket
        received = client_socket.recv(BUFFER_SIZE).decode()
        filename, filesize = received.split(SEPARATOR)
        # remove absolute path if there is
        filename = os.path.basename(filename)
        # convert to integer
        filesize = int(filesize)

        # start receiving the file from the socket
        # and writing to the file stream
        progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
        with open(filename, "wb") as f:
            while True:
                # read 1024 bytes from the socket (receive)
                bytes_read = client_socket.recv(BUFFER_SIZE)
                if not bytes_read:    
                    # nothing is received
                    # file transmitting is done
                    break
                # write to the file the bytes we just received
                f.write(bytes_read)
                # update the progress bar
                progress.update(len(bytes_read))

        # close the client socket
        client_socket.close()
        # close the server socket
        self.socket.close()
        return filename
