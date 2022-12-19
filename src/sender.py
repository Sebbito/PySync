#!/bin/python3
import os
import tqdm
from pathlib import Path
import socket as s
import generator as gen
# whenever you see constants, they are from here 🠟
from constants import *

class Sender:
    def __init__(self, server_address = DEFAULT_SERVER, server_port = DEFAULT_PORT):
        self.port = server_port
        self.address = server_address
        self.socket = s.socket()

    def __exit__(self, *args):
        self.socket.close()

    def send(self, mixed):
        '''
        Sends all files in the given Path 'mixed'. Each file is sent through it's own socket.
        '''
        try:
            file_list = gen.generate_file_list(mixed)
            file_counter = len(file_list)

            print(f"[i] Found {file_counter} files.")
            
            print("[i] Connecting to server")
            self.socket.connect((self.address, self.port))
            print("[+] Connected to server")

            self.socket.send(f"{file_counter}".encode())
            # close the socket
            self.socket.close()
            self.loop_through_and_send(file_list)

            # close the socket
            self.socket.close()
            print("[+] Closed socket")
        except Exception as e:
            print(e)
            raise

    def loop_through_and_send(self, file_list):
        for p in file_list:
            # send the file
            if p.exists() and p.is_file:
                # generate a new socket for each file
                # closing and reconnecting to prevent merged output
                self.socket = s.socket()
                self.socket.connect((self.address, self.port))
                self.send_file(p)
                self.socket.close()
            else:
                print(f"[!] Path '{p}' is not a file or doesn't exists")
                exit()

    def send_file(self, filename):
        filesize = os.path.getsize(filename)
        md5 = gen.calculate_md5(filename)

        # send the filename and filesize
        self.socket.send(f"{filename}{SEPARATOR}{filesize}{SEPARATOR}{md5}".encode())

        received = self.socket.recv(BUFFER_SIZE).decode()

        if received == OK:
            print("[+] Received ok, continuing.")
        elif received == SKIP:
            print("[i] Received skip, file contents are the same, continuing.")
            return EXIT_SUCCESS
        else:
            print("[!] No status signal received. Aborting file transmission!")
            exit()

        # print("[i] Received ok, continuing")

        progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
        with open(filename, "rb") as f:
            while True:
                # read the bytes from the file
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    # file transmitting is done
                    break
                # we use sendall to assure transimission in busy networks
                self.socket.sendall(bytes_read)
                # update the progress bar
                progress.update(len(bytes_read))

