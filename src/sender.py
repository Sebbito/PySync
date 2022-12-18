#!/bin/python3
import os
import tqdm
from pathlib import Path
import socket as s
from generator import Generator
# whenever you see constants, they are from here 🠟
from constants import *

class Sender:
    def __init__(self, server_address = DEFAULT_SERVER, server_port = DEFAULT_PORT):
        self.port = server_port
        self.address = server_address
        self.socket = s.socket()

    def __exit__(self, *args):
        self.socket.close()

    def send(self, path):
        '''
        Scans path and sends all found files through it's dedicated socket.
        '''
        try:
            p = Path(path)
            file_counter = self.count_files(p)
            print(f"[i] Found {file_counter} files.")
            
            print("[i] Connecting to server")
            self.socket.connect((self.address, self.port))
            print("[+] Connected to server")

            self.socket.send(f"{file_counter}".encode())
            # close the socket
            self.socket.close()
            self.loop_through_and_send(p)

            # close the socket
            self.socket.close()
            print("[+] Closed socket")
        except Exception as e:
            print(e)
            raise

    def loop_through_and_send(self, path):
        p = Path(path)
        # send the file
        if p.exists():
            if p.is_file():
                # generate a new socket for each file
                # closing and reconnecting to prevent merged output
                self.socket = s.socket()
                self.socket.connect((self.address, self.port))
                self.send_file(p)
                self.socket.close()
            # recursion if it is a directory
            elif p.is_dir():
                # count files so we can inform the receiver how many we send
                # send files
                for file in p.iterdir():
                    # print(f"[i] Iterating {file} for dir {p}")
                    self.loop_through_and_send(file)
            else:
                print(f"[!] Path '{p}' is neither file nor directory, aborting.")
                exit()
        else:
            print(f"[!] Path '{p}' doesn't exists")
            exit()

    def send_file(self, filename):
        filesize = os.path.getsize(filename)

        # send the filename and filesize
        self.socket.send(f"{filename}{SEPARATOR}{filesize}".encode())

        received = self.socket.recv(BUFFER_SIZE).decode()
        if (received == OK):
            print("[i] Received ok, continuing")
        else:
            print("[!] No ok signal received. Aborting file transmission!")
            exit()

        progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
        with open(filename, "rb") as f:
            while True:
                # read the bytes from the file
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    # file transmitting is done
                    break
                # we use sendall to assure transimission in 
                # busy networks
                self.socket.sendall(bytes_read)
                # update the progress bar
                progress.update(len(bytes_read))

    def count_files(self, path) -> int:
        ''' Uses recursion to count all files in path. '''
        counter = 0
        p = Path(path)

        if p.is_dir():
            for file in p.iterdir():
                counter += self.count_files(file)
        else:
            counter += 1

        return counter
