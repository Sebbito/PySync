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
    socket = s.socket(s.AF_INET, s.SOCK_STREAM)
    socket.setsockopt(s.SOL_SOCKET, s.SO_REUSEADDR, 1)
    socket.bind((DEFAULT_SERVER, DEFAULT_PORT))

    try:
        while(True):
            receive(socket)
    except KeyboardInterrupt:
        socket.close()
        print(f"[!] Aborted receiving")
    

def receive_once(args, address=DEFAULT_SERVER, port=DEFAULT_PORT):
    socket = s.socket(s.AF_INET, s.SOCK_STREAM)
    socket.setsockopt(s.SOL_SOCKET, s.SO_REUSEADDR, 1)
    socket.bind((address, port))

    try:
        receive(socket)
    except KeyboardInterrupt:
        socket.close()
        print(f"[!] Aborted receiving")

def receive(socket):
    args, address = receive_msg_start(socket)

    # start according routine
    if args['func'] == 'send':
        receive_files(socket, args)
    elif args['func'] == 'get':
        try:
            list, count = gen.get_file_list_and_count(args['file'])
            # send filecount 
            sender.send_file_count(address, DEFAULT_PORT, count)

            # send all the files in the file list
            sender.loop_through_and_send(address, DEFAULT_PORT, list)

            print("[+] Closed socket")
        except:
            print(f"[!] Fatal error while transmitting. Aborting.")
        raise
    # elif args['func'] is 'sync':
    #     receive_files(args, socket)
    #     sender.send(args)
    else:
        print(f"[!] Illegal option {args['func']}. Aborting")
        exit(EXIT_FAILURE)


def receive_msg_start(socket):
    ''' Function to receive the starting information of the transmition.'''
    socket.listen(5)
    client_socket, address = socket.accept()

    try:
        received = eval(client_socket.recv(BUFFER_SIZE).decode())
        print(f"[i] Received {received}")
        client_socket.send(f"{OK}".encode())
        print("[i] Sending ok")
    except SyntaxError:
        print(f"[!] Could not parse received message. Aborting")
        exit(EXIT_FAILURE)
    finally:
        client_socket.close()
        print("[i] Closing socket")

    return received, address

def receive_files(socket: s.socket, args: dict):
    file_count = receive_file_count(socket)

    for _ in range(file_count):
        socket.listen(5)
        client_socket, address = socket.accept()

        file, filesize, md5, modtime = receive_file_info(client_socket)

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

        # deciding what to do with file
        if  args['update'] == True and update_option_handler(file, md5, modtime) == False or\
            args['create'] == True and create_option_handler(file) == False or\
            not file.exists():
            # none of the options triggered
            print("[i] Skipping transmition")
            client_socket.send(f"{SKIP}".encode())
        else:
            print("[i] Sending ok")
            client_socket.send(f"{OK}".encode())
            receive_file_contents(client_socket, file, filesize)

        print("[i] Closing socket")
        client_socket.close()

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

    socket.listen(5)
    client_socket, address = socket.accept()

    file_count = 0

    try:
        file_count = int(client_socket.recv(BUFFER_SIZE).decode())
        print(f"[i] Receiving {file_count} files")
        client_socket.send(f"{OK}".encode())
        print("[i] Sending ok")
    except:
        raise

    return file_count


def receive_file_info(socket: s.socket):
    ''' Function to receive the file informations.'''
    # receive the file infos
    received = socket.recv(BUFFER_SIZE).decode()
    return received.split(SEPARATOR)


def receive_file_contents(socket: s.socket, path: Path, filesize: int):
    # type casting
    filename = Path(path)
    filesize = int(filesize)

    # start receiving the file from the socket
    # and writing to the file stream
    progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "wb") as f:
        while True:
            # read 1024 bytes from the socket (receive)
            bytes_read = socket.recv(BUFFER_SIZE)
            if not bytes_read:    
                # nothing is received
                # file transmitting is done
                break
            # write to the file the bytes we just received
            f.write(bytes_read)
            # update the progress bar
            progress.update(len(bytes_read))

