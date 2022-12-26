#!/bin/python3
import os
import tqdm
from pathlib import Path
import socket as s
import generator as gen
import sender
# whenever you see constants, they are from here
from constants import *


def receive_forever(args):
    server_socket = get_binded_socket(DEFAULT_SERVER)

    try:
        while(True):
            receive(server_socket)
    except KeyboardInterrupt:
        server_socket.close()
        print(f"[!] Aborted receiving")
    

def receive_once(args, address=DEFAULT_SERVER, port=DEFAULT_PORT):
    server_socket = get_binded_socket(DEFAULT_SERVER)

    try:
        receive(server_socket)
    except KeyboardInterrupt:
        print(f"[!] Aborted receiving")
        server_socket.close()
        print(f"[i] Closed Socket")

def receive(server_socket: s.socket):
    args, address, client_socket = receive_msg_start(server_socket)

    # start according routine
    if args['func'] == 'send':
        # client wants to send files to us
        receive_files(client_socket, args)
    elif args['func'] == 'get':
        # IMPORTANT: change the function or else we enter an endless loop
        args['func'] = 'send'
        sender.send(args)
    else:
        print(f"[!] Illegal option {args['func']}. Aborting")
        exit(EXIT_FAILURE)
    client_socket.close()


def receive_msg_start(socket: s.socket):
    ''' Function to receive the starting information of the transmition.'''
    socket.listen(1)
    client_socket, address = socket.accept()

    try:
        received = eval(client_socket.recv(BUFFER_SIZE).decode())
        print(f"[i] Received {received} from {address}")
        client_socket.send(f"{OK}".encode())
        print("[i] Sending ok")
    except SyntaxError:
        print(f"[!] Could not parse received message. Aborting")
        exit(EXIT_FAILURE)

    return received, address, client_socket

def receive_files(socket: s.socket, args: dict):
    file_count = receive_file_count(socket)

    for _ in range(file_count):
        file, filesize, md5, modtime = receive_file_info(socket)

        # deciding what to do with file
        if  args['update'] == True and update_option_handler(file, md5, modtime) == False or\
            args['create'] == True and create_option_handler(file) == False or\
            not file.exists():
            # none of the options triggered
            print("[i] Skipping transmition")
            socket.send(f"{SKIP}".encode())
        else:
            print("[i] Sending ok")
            socket.send(f"{OK}".encode())
            receive_file_contents(socket, file, filesize)
            print("[i] Done receiving, sending ok")
            socket.send(f"{OK}".encode())


def update_option_handler(file: Path, md5: str, modtime: float) -> bool:
    ''' Handles the update case.
        Invoking this function implies args['update'] == True.
        Return:
            True - Receive the file
            False - Skip the file
    '''
    ret = True
    if file.exists():
        # we can skip if our file is the same or older
            if gen.calculate_md5(file) == md5 or os.stat(file).st_mtime < modtime:
                ret = False
                print("[i] Update true but out file is newer, skipping")
    return ret

def create_option_handler(file: Path) -> bool:
    ''' Handles the create case.
        Invoking this function implies args['create'] == True '''
    ret = True
    if not file.exists():
        if not file.parents[0].exists():
            os.makedirs(file.parents[0])
        file.touch()
        ret = True
        print(f"[i] New file {file} created")

    return ret

def receive_file_count(socket: s.socket):
    ''' Receives file count and sends ok back. '''
    file_count = 0

    try:
        file_count = int(socket.recv(BUFFER_SIZE).decode())
        print(f"[i] Receiving {file_count} files")
        socket.send(f"{OK}".encode())
        print("[i] Sending ok")
    except:
        raise

    return file_count


def receive_file_info(socket: s.socket):
    ''' Function to receive the file informations.'''
    # receive the file infos
    received = socket.recv(BUFFER_SIZE).decode()
    file, filesize, md5, modtime = received.split(SEPARATOR)

    # casting
    try:
        file = Path(file)
        filesize = int(filesize)
        # md5 is a string already
        modtime = float(modtime)
        print(f"[i] Received file info: {file}, {filesize}, {md5}, {modtime}")
    except:
        print(f"[!] Could not parse received message on receive_files. Aborting")
        exit(EXIT_FAILURE)
    return file, filesize, md5, modtime


def receive_file_contents(socket: s.socket, filename: Path, filesize: int):
    # start receiving the file from the socket
    # and writing to the file stream
    progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "wb") as f:
        bytes_received = 0
        while bytes_received < filesize:
            # read 1024 bytes from the socket (receive)
            bytes_read = socket.recv(BUFFER_SIZE)
            if bytes_read == b'':
                raise RuntimeError("socket connection broken")
            # write to the file the bytes we just received
            f.write(bytes_read)
            # update the progress bar
            progress.update(len(bytes_read))
            bytes_received = bytes_received + len(bytes_read)



def get_binded_socket(address: str):
    ''' Will open a socket and bind it to a free port. 
        Loops from the default until it finds a free one.'''
    socket = s.socket(s.AF_INET, s.SOCK_STREAM)
    socket.setsockopt(s.SOL_SOCKET, s.SO_REUSEADDR, 1)
    port = int(DEFAULT_PORT)

    while(True):
        try:
            socket.bind((address, port))
            break
        except:
            port += 1
            continue

    opts = socket.getsockname()
    print(f"[i] Opened up server at {opts}")

    return socket
