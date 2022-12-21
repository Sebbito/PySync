#!/bin/python3
import os
import tqdm
from pathlib import Path
import socket as s
import generator as gen
import receiver 
# whenever you see constants, they are from here
from constants import *


def send(args):
    '''
    Function to send one or more files to a server.
    args:
        - file
        - options for operation
    '''
    try:
        list, count = gen.get_file_list_and_count(args['file'])

        # send the first message of the communication
        initiate_communication(DEFAULT_SERVER, DEFAULT_PORT, args)

        # send filecount 
        send_file_count(DEFAULT_SERVER, DEFAULT_PORT, count)

        # send all the files in the file list
        loop_through_and_send(DEFAULT_SERVER, DEFAULT_PORT, list)

        print("[+] Closed socket")
    except Exception as e:
        print(f"[!] Fatal error while transmitting. Aborting.")
        raise


def initiate_communication(address, port, args):
    ''' Sends the arguments over to the server to set it up for transmition. '''
    try:
        # remove the file list
        args.pop('file')

        socket = s.socket()
        print(f"[i] Connecting to server {DEFAULT_SERVER}:{DEFAULT_PORT}.")
        socket.connect((address, port))
        print("[+] Connected to server.")
        socket.send(f"{args}".encode())

        rec = socket.recv(BUFFER_SIZE).decode()

        if not rec == OK:
            print(f"[!] Invalid server response '{rec}'. Aborting")
            exit(EXIT_FAILURE)

        print(f"[i] Received ok. Start sending files.")
        # close the socket
        socket.close()
    except ConnectionRefusedError:
        print("[!] Server not found or connection closed.")
        socket.close()
        exit(EXIT_FAILURE)

def send_file_count(address, port, file_count):
    if file_count is None:
        print(f"[!] File list empty. Aborting")
        exit(EXIT_FAILURE)

    socket = s.socket()
    socket.connect((address, port))
    
    print(f"[i] Sending filecount")
    socket.send(f"{file_count}".encode())

    rec = socket.recv(BUFFER_SIZE).decode()

    if not rec == OK:
        print(f"[!] Invalid server response '{rec}'. Aborting")
        exit(EXIT_FAILURE)

    print(f"[i] Received ok")


def loop_through_and_send(address, port, file_list):
    ''' Opens sockets for each file and sends the file contents to the server. '''

    if file_list is None:
        print("[!] Empty file list. Aborting")

    print("[i] Start sending files")
    for path in file_list:
        # send the file
        if path.exists() and path.is_file:
            # generate a new socket for each file
            # closing and reconnecting to prevent merged output
            socket = s.socket()
            socket.connect((address, port))

            send_file(socket, path)
            
            # close the socket
            socket.close()
        else:
            print(f"[!] Path '{path}' is not a file or doesn't exists")
            exit()

    
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
        print("[i] Received skip, file contents are the same, continuing")
    else:
        print("[!] No or illegal status signal received. Aborting file transmission")
        exit(EXIT_FAILURE)


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

