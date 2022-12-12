#!/bin/python3
import tqdm
from pathlib import Path
import socket as s
import os

class Sender:
    def __init__(self):
        self.port = 8008
        self.address = "0.0.0.0"
        self.socket = s.socket()
        self.BUFFER_SIZE = 4096
        self.SEPARATOR = "[SEP]"

    def send(self, path):
        try:
            p = Path(path)
            if p.is_file():
                self.send_file(p.name)
            else:
                print("[!] Sending whole dirs is not supportet yet")
                raise
        except Exception as e:
            print(e)
            raise

    def send_file(self, filename):
        filesize = os.path.getsize(filename)
        BUFFER_SIZE = self.BUFFER_SIZE
        SEPARATOR= self.SEPARATOR

        print("[I] Connecting to socket")
        self.socket.connect((self.address, self.port))
        print("[+] Connected to socket")

        # send the filename and filesize
        self.socket.send(f"{filename}{SEPARATOR}{filesize}".encode())

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
        # close the socket
        self.socket.close()
