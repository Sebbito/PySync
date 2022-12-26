#!/bin/python3
import os
import tqdm
from pathlib import Path
import socket as s
import generator as gen
import receiver 
# whenever you see constants, they are from here
from constants import *
# import pdb

def get(args):
    print(f"[i] Called routine to get files")

    server_socket = receiver.get_binded_socket(DEFAULT_SERVER)
    init_socket = s.socket() # only for initial connection

    address = args['address'] if args['address'] != None else DEFAULT_SERVER
    port = args['port'] if args['port'] != None else DEFAULT_PORT 

    print(f"[i] Connecting to server {address}:{port}.")
    init_socket.connect((address, port))

    args['address'] = server_socket.getsockname()[0] # port number
    args['port'] = server_socket.getsockname()[1] # port number

    # send the first message of the communication
    initiate_communication(init_socket, args)
    
    # close the throwaway socket
    init_socket.close()

    receiver.receive(server_socket)
    server_socket.close()

def sync(args):
    # we will only update the files
    print("[i] Syncing routine. Calling send and get")
    args['update'] = True
    args['func'] = 'send'
    send(args)
    args['func'] = 'get'
    get(args)
    exit(EXIT_SUCCESS)

def send(args):
    '''
    Function to send one or more files to a server.
    args:
        - file
        - options for operation
    '''
    print(f"[i] Called routine to send files")

    address = args['address'] if args['address'] != None else DEFAULT_SERVER
    port = args['port'] if args['port'] != None else DEFAULT_PORT 

    try:
        list, count = gen.get_file_list_and_count(args['file'])

        socket = s.socket()
        print(f"[i] Connecting to server {address}:{port}.")
        socket.connect((address, port))

        # send the first message of the communication
        initiate_communication(socket, args)

        # send filecount 
        send_file_count(socket, count)

        # send all the files in the file list
        loop_through_and_send(socket, list)
    except:
        print(f"[!] Fatal error while transmitting. Aborting.")
        raise


def initiate_communication(socket: s.socket, args=None):
    ''' Sends the arguments over to the server to set it up for transmition. '''
    try:

        print(f"[+] Sending args {args}.")
        socket.send(f"{args}".encode())

        rec = socket.recv(BUFFER_SIZE).decode()

        if rec == OK:
            print(f"[i] Received ok")
        else:
            print(f"[!] Invalid server response '{rec}'. Aborting")
            exit(EXIT_FAILURE)

    except ConnectionRefusedError:
        print("[!] Server not found or connection closed.")
        exit(EXIT_FAILURE)


def send_file_count(socket: s.socket, file_count: int):
    if file_count is None:
        print(f"[!] File list empty. Aborting")
        exit(EXIT_FAILURE)

    
    print(f"[i] Sending filecount '{file_count}' to {socket.getpeername()}")
    socket.send(f"{file_count}".encode())

    rec = socket.recv(BUFFER_SIZE).decode()

    if rec == OK:
        print(f"[i] Received ok")
    else:
        print(f"[!] Invalid server response '{rec}'. Aborting")
        exit(EXIT_FAILURE)



def loop_through_and_send(socket: s.socket, file_list):
    ''' Opens sockets for each file and sends the file contents to the server. '''

    if file_list is None:
        print("[!] Empty file list. Aborting")

    print("[i] Start sending files")
    for path in file_list:
        # send the file
        if path.exists() and path.is_file:
            send_file(socket, path)
        else:
            print(f"[!] Path '{path}' is not a file or doesn't exists")
            socket.close()
            exit()
    # close the socket
    socket.close()

    
def send_file(socket: s.socket, file: Path):
    # prepare first info pack
    filesize = os.path.getsize(file)
    md5 = gen.calculate_md5(file)
    modtime = os.stat(file).st_mtime

    # send the filename and filesize
    print(f"Sending file info: {file}{SEPARATOR}{filesize}{SEPARATOR}{md5}{SEPARATOR}{modtime} to {socket.getpeername()}")
    socket.send(f"{file}{SEPARATOR}{filesize}{SEPARATOR}{md5}{SEPARATOR}{modtime}".encode())

    # receive server response
    received = socket.recv(BUFFER_SIZE).decode()

    if received == OK:
        print("[+] Received ok, continuing.")
        send_file_contents(socket, file, filesize)
        print("[i] Done sending")
        rec = socket.recv(BUFFER_SIZE).decode()

        if rec == OK:
            print(f"[i] Received ok")
        else:
            print(f"[!] Invalid server response '{rec}'. Aborting")
            exit(EXIT_FAILURE)
    elif received == SKIP:
        print("[i] Received skip, continuing")
    else:
        print("[!] No or illegal status signal received. Aborting file transmission")
        exit(EXIT_FAILURE)


def send_file_contents(socket: s.socket, filename: Path, filesize: int):
    progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "rb") as f:
        total = 0
        while total < filesize:
            # read the bytes from the file
            bytes_read = f.read(BUFFER_SIZE)
            if bytes_read == b'':
                raise RuntimeError("socket connection broken")
            # we use sendall to assure transimission in busy networks
            sent = socket.send(bytes_read)
            if sent == 0:
                raise RuntimeError("socket connection broken")
            # update the progress bar
            progress.update(len(bytes_read))
            total = total + sent

