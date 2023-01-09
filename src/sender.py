#!/bin/python3

import os
import tqdm
from pathlib import Path
import socket as s
import logging
import generator as gen
import receiver 
# whenever you see constants, they are from here
from constants import *
# import pdb

log = logging.getLogger(LOGGER_NAME)

def get(args):
    log.debug(f"Called routine to get files")

    server_socket = receiver.get_binded_socket(DEFAULT_SERVER)
    init_socket = s.socket() # only for initial connection

    address = args['address'] if args['address'] != None else DEFAULT_SERVER
    port = args['port'] if args['port'] != None else DEFAULT_PORT 

    log.debug(f"Connecting to server {address}:{port}.")
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
    log.debug("Syncing routine. Calling send and get")
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
    log.debug(f"Called routine to send files")

    address = args['address'] if args['address'] != None else DEFAULT_SERVER
    port = args['port'] if args['port'] != None else DEFAULT_PORT 

    try:
        list, count = gen.get_file_list_and_count(args['file'])

        socket = s.socket()
        log.debug(f"Connecting to server {address}:{port}.")
        socket.connect((address, port))

        # send the first message of the communication
        initiate_communication(socket, args)

        # send filecount 
        send_file_count(socket, count)

        # send all the files in the file list
        loop_through_and_send(socket, list)
    except Exception as e:
        log.error(e)
        raise e


def initiate_communication(socket: s.socket, args=None):
    ''' Sends the arguments over to the server to set it up for transmition. '''
    try:

        log.debug(f"Sending args {args}.")
        socket.send(f"{args}".encode())

        rec = socket.recv(BUFFER_SIZE).decode()

        if rec == OK:
            log.debug(f"Received ok")
        else:
            log.debug(f"Invalid server response '{rec}'. Aborting")
            exit(EXIT_FAILURE)

    except ConnectionRefusedError as e:
        log.error(e)
        raise e


def send_file_count(socket: s.socket, file_count: int):
    if file_count is None:
        e = RuntimeError("Empty file list")
        log.error(e)
        raise e

    
    log.debug(f"Sending filecount '{file_count}' to {socket.getpeername()}")
    socket.send(f"{file_count}".encode())

    rec = socket.recv(BUFFER_SIZE).decode()

    if rec == OK:
        log.debug(f"Received ok")
    else:
        e = RuntimeError(f"Invalid server response '{rec}'")
        log.error(e)
        raise e


def loop_through_and_send(socket: s.socket, file_list):
    ''' Opens sockets for each file and sends the file contents to the server. '''

    if file_list is None:
        log.debug("Empty file list. Aborting")

    log.debug("Start sending files")
    progress = tqdm.tqdm(range(len(file_list)), f"Sending {len(file_list)} files")
    for path in file_list:
        # send the file
        if path.exists() and path.is_file:
            send_file(socket, path)
            # update the progress bar
            progress.update(1)
        else:
            log.debug(f"Path '{path}' is not a file or doesn't exists")
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
    log.debug(f"Sending file info: {file}{SEPARATOR}{filesize}{SEPARATOR}{md5}{SEPARATOR}{modtime} to {socket.getpeername()}")
    socket.send(f"{file}{SEPARATOR}{filesize}{SEPARATOR}{md5}{SEPARATOR}{modtime}".encode())

    # receive server response
    received = socket.recv(BUFFER_SIZE).decode()

    if received == OK:
        log.debug("Received ok, continuing.")
        send_file_contents(socket, file, filesize)
        log.debug("Done sending")
        rec = socket.recv(BUFFER_SIZE).decode()

        if rec == OK:
            log.debug(f"Received ok")
        else:
            log.debug(f"Invalid server response '{rec}'. Aborting")
            exit(EXIT_FAILURE)
    elif received == SKIP:
        log.debug("Received skip, continuing")
    else:
        log.debug("No or illegal status signal received. Aborting file transmission")
        exit(EXIT_FAILURE)


def send_file_contents(socket: s.socket, filename: Path, filesize: int):
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
            total = total + sent

