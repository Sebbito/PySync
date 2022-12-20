#!/bin/python3
import os
import tqdm
from pathlib import Path
import socket as s
import generator as gen
import sender
# whenever you see constants, they are from here
from constants import *
import atexit


class Receiver:
    ''' Server like class for receiving files. '''

    def __init__(self, destination = DEFAULT_DESTINATION, server_address = DEFAULT_SERVER, server_port = DEFAULT_PORT):
        self.address = server_address
        self.port = server_port
        self.socket = s.socket(s.AF_INET, s.SOCK_STREAM)
        self.socket.bind((self.address, self.port))
        self.socket.setsockopt(s.SOL_SOCKET, s.SO_REUSEADDR, 1)
        self.destination = destination
        atexit.register(self.exit)

    def __exit__(self, *args):
        self.socket.close()

    def exit(self):
        self.socket.close()

    def receive_forever(self):
        while(True):
            self.receive()
        self.socket.close()

    def receive_once(self):
        self.receive()
        self.socket.close()

    def receive(self):
        file_count, update_flag = receive_msg_start(self.socket)
        print(f"[i] Receiving {file_count} files. Updates: {update_flag}")
        update_flag = update_flag == 'True'

        for _ in range(int(file_count)):
            self.socket.listen(5)
            client_socket, address = self.socket.accept()

            self.handle_server_response(client_socket, update_flag)
            
            client_socket.close()

    def handle_server_response(self, socket, update_flag):
        ''' Currently does like a two in one where it handles all the args and also the response. '''
        filename, filesize, md5, modtime = receive_file_info(socket)

        # type casting
        filepath = Path(self.destination + '/' + filename)
        filesize = int(filesize)

        # create dirs if file didn't exists
        if not filepath.exists():
            if not filepath.parents[0].exists():
                os.makedirs(filepath.parents[0])

            # send ok since the client will be waiting before proceeding
            socket.send(f"{OK}".encode())
            receive_file_contents(socket, filepath, filesize)
            return EXIT_SUCCESS

        if gen.calculate_md5(filepath) == md5:
            # skip transmition since they are the same
            socket.send(f"{SKIP}".encode())
            print(f"[i] Checksums are the same, skipping transmition of file {filepath}.")
            return EXIT_SUCCESS
        else:
            # not the same means updating
            # if our file is newer and client wants to update
            if (os.stat(filename).st_mtime > float(modtime)):
                if update_flag == True:
                    # client wants to receive the updated file contents
                    # inform him of the update
                    print(f"[i] Sending updated file {filepath}")
                    socket.send(f"{UPDATE}".encode())
                    received = socket.recv(BUFFER_SIZE).decode()
                    if received == OK:
                        sender.send_file(socket, filepath)
                    else:
                        print(f"[!] Expected {OK}, received {received} instead. Aborting")
                        exit(EXIT_FAILURE)
                    return EXIT_SUCCESS
                else:
                    socket.send(f"{SKIP}".encode())
                    print(f"[i] Update_flag is {update_flag}. Skipping transmition.")
                    return EXIT_SUCCESS
            else:
                print(f"[i] Getting newer client changes")
                socket.send(f"{OK}".encode())
                receive_file_contents(socket, filepath, filesize)
                return EXIT_SUCCESS

        print("[!] Reached end of handle function. Illegal state. Aborting")
        exit(EXIT_FAILURE)

    # end class Receiver

def receive_msg_start(socket):
    ''' Function to receive the starting information of the transmition.'''
    socket.listen(5)
    client_socket, address = socket.accept()

    received = client_socket.recv(BUFFER_SIZE).decode()
    client_socket.send(f"{OK}".encode())
    client_socket.close()

    return received.split(SEPARATOR)


def receive_file(socket, destination=None):
    ''' Receives and stores the file, no questions asked. '''
    filename, filesize, md5, modtime = receive_file_info(socket)

    if not destination == None:
        filename = Path(destination + '/' + filename)

    socket.send(f"{OK}".encode())

    path = Path(filename)
    receive_file_contents(socket, path, filesize)


def receive_file_info(socket):
    ''' Function to receive the file informations.'''
    # receive the file infos
    received = socket.recv(BUFFER_SIZE).decode()
    return received.split(SEPARATOR)


def receive_file_contents(socket, path, filesize):
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
