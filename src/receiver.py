#!/bin/python3
import os
import tqdm
from pathlib import Path
import socket as s
# whenever you see constants, they are from here 🠟
from constants import *

class Receiver(object):
    def __init__(self):
        self.address = "0.0.0.0"
        self.port = 8008
        self.socket = s.socket()
        self.socket.bind((self.address, self.port))

    def __exit__(self, *args):
        self.socket.close()

    def receive_all(self):
        self.socket.listen(5)
        client_socket, address = self.socket.accept()
        # print(f"Accepted connection {client_socket} with address {address}")

        file_count = client_socket.recv(BUFFER_SIZE).decode()
        print(f"[i] Receiving {file_count} files")
        for _ in range(int(file_count)):
            self.socket.listen(5)
            client_socket, address = self.socket.accept()
            self._receive_file(client_socket)

        # close the client socket
        client_socket.close()
        # close the server socket
        self.socket.close()


    def _receive_file(self, client_socket):
        # receive the file infos
        # receive using client socket, not server socket
        received = client_socket.recv(BUFFER_SIZE).decode()
        filename, filesize = received.split(SEPARATOR)

        # type casting
        filename = Path(filename)
        filesize = int(filesize)

        # create dirs on the fly
        if not os.path.exists(filename.parents[0]):
            print(f"[i] Creating paths '{filename.parents[0]}' for file '{filename}'")
            os.makedirs(filename.parents[0])

        # send ok since the client will be waiting before proceeding
        client_socket.send(f"{OK}".encode())

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

