#!/bin/python3
import os
import tqdm
from pathlib import Path
import socket as s
import generator as gen
# whenever you see constants, they are from here
from constants import *

class Receiver(object):
    def __init__(self, destination = DEFAULT_DESTINATION, server_address = DEFAULT_SERVER, server_port = DEFAULT_PORT):
        self.address = server_address
        self.port = server_port
        self.socket = s.socket(s.AF_INET, s.SOCK_STREAM)
        self.socket.bind((self.address, self.port))
        self.destination = destination

    def __exit__(self, *args):
        self.socket.close()

    def receive_forever(self):
        while(True):
            self.receive_all()


    def receive_all(self):
        self.socket.listen(5)
        client_socket, address = self.socket.accept()
        # print(f"Accepted connection {client_socket} with address {address}")

        file_count = client_socket.recv(BUFFER_SIZE).decode()
        print(f"[i] Receiving {file_count} files")
        client_socket.close()

        for _ in range(int(file_count)):
            self.socket.listen(5)
            client_socket, address = self.socket.accept()
            self.receive_file(client_socket)
            client_socket.close()


    def receive_file(self, client_socket):
        # receive the file infos
        # receive using client socket, not server socket
        received = client_socket.recv(BUFFER_SIZE).decode()
        filename, filesize, md5 = received.split(SEPARATOR)

        # type casting
        filename = Path(self.destination + '/' + filename)
        filesize = int(filesize)

        # parent dirs don't exist (so the file doesn't exist aswell)
        if not os.path.exists(filename.parents[0]):
            print(f"[i] Creating paths '{filename.parents[0]}' for file '{filename}'")
            os.makedirs(filename.parents[0])
        elif filename.exists():
            # file exists. Is it the same?
            if gen.calculate_md5(filename) == md5:
                # skip transmition since they are the same
                client_socket.send(f"{SKIP}".encode())
                print(f"[i] Checksums are the same, skipping transmition of file {filename}.")
                return EXIT_SUCCESS


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

