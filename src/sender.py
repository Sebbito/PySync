#!/bin/python3
import os
import tqdm
from pathlib import Path
import socket as s
import generator as gen
import receiver 
# whenever you see constants, they are from here
from constants import *

class Sender:
    def __init__(self, server_address = DEFAULT_SERVER, server_port = DEFAULT_PORT, update = False):
        self.port = server_port
        self.address = server_address
        self.socket = None
        self.update = update

    def __exit__(self, *args):
        self.socket.close()

    def send(self, mixed):
        '''
        Sends all files in the given Path 'mixed'. Each file is sent through it's own socket.
        '''
        try:
            file_list = gen.generate_file_list(mixed)
            file_count = len(file_list)

            print(f"[i] Found {file_count} files.")
            
            initiate_communication(address=self.address, port=self.port, update=self.update, file_count=file_count)

            # send all the files in the file list
            self.loop_through_and_send(file_list)

            print("[+] Closed socket")
        except Exception as e:
            print(e)
            raise

    def loop_through_and_send(self, file_list):
        for path in file_list:
            # send the file
            if path.exists() and path.is_file:
                # generate a new socket for each file
                # closing and reconnecting to prevent merged output
                self.socket = s.socket()
                self.socket.connect((self.address, self.port))
                
                send_file(self.socket, path)
                
                self.socket.close()
            else:
                print(f"[!] Path '{p}' is not a file or doesn't exists")
                exit()

def initiate_communication(address, port, update=False, file_count=0, intention='send'):
    if intention == 'send':
        try:
            socket = s.socket()
            print(f"[i] Connecting to server {address}:{port}.")
            socket.connect((address, port))
            print("[+] Connected to server.")

            socket.send(f"{file_count}{SEPARATOR}{update}".encode())

            rec = socket.recv(BUFFER_SIZE).decode()

            if not rec == OK:
                print(f"[!] Invalid server response '{rec}'. Aborting")
                exit(EXIT_FAILURE)

            print(f"[i] Received ok. Start sending files.")
            # close the socket
            socket.close()
        except Exception as e:
            print("[!] Server not found.")
            raise e

    else:
        print(f"[!] Invalid intention. Aborting")
        exit(EXIT_FAILURE)
    
def send_file(socket, file):
    # prepare first info pack
    filesize = os.path.getsize(file)
    md5 = gen.calculate_md5(file)
    modtime = os.stat(file).st_mtime

    # send the filename and filesize
    socket.send(f"{file}{SEPARATOR}{filesize}{SEPARATOR}{md5}{SEPARATOR}{modtime}".encode())

    # receive server response
    received = socket.recv(BUFFER_SIZE).decode()

    if received == OK:
        print("[+] Received ok, continuing.")
        send_file_contents(socket, file)
    elif received == SKIP:
        print("[i] Received skip, file contents are the same, continuing.")
    elif received == UPDATE:
        print("[i] Received update, server has newer files, continuing.")
        socket.send(f"{OK}".encode())
        receiver.receive_file(socket)
    else:
        print("[!] No status signal received. Aborting file transmission!")
        exit()

def send_file_contents(socket, filename):
    filesize = os.path.getsize(filename)

    progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "rb") as f:
        while True:
            # read the bytes from the file
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                # file transmitting is done
                break
            # we use sendall to assure transimission in busy networks
            socket.sendall(bytes_read)
            # update the progress bar
            progress.update(len(bytes_read))

