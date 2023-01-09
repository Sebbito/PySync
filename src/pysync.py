#!/bin/python3
import os
from pathlib import Path
import argparse as ap
import logging
import receiver as r
import sender as s
from constants import *

VERSION="0.0.1"

def receive(args):

    if args['once'] == True:
        r.receive_once(args)
    elif args['continuos'] == True:
        r.receive_forever(args)
    else:
        print("Whoops! Could not parse that argument. Please try again with a different argument.")
        exit(EXIT_FAILURE)
    exit(EXIT_SUCCESS)

def send(args):
    s.send(args)
    exit(EXIT_SUCCESS)

def get(args):
    s.get(args)
    exit(EXIT_SUCCESS)

def sync(args):
    s.sync(args)
    exit(EXIT_SUCCESS)

def init_logger():
    log_path = Path(PYSYNC_LOG_FILE).expanduser()

    if log_path.is_file():
        pass
    elif not log_path.exists():
        try:
            os.makedirs(log_path.parents[0])
            log_path.touch()
        except FileExistsError:
            pass
        except Exception as e:
            raise e
        pass
    else:
        print(f"Log file doesn't exist, isn't readble or could not be created. Please make sure that the log file ({log_path}) is a regular file and read/writable")
        exit()

    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
    file_handler = logging.FileHandler(log_path, mode='w', encoding='utf-8')
    stream_handler = logging.StreamHandler()


    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.INFO)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

def init_argparse():
    parser = ap.ArgumentParser(
        prog="pysync",
        description="Program for file synchronization with another machine running PySync."
        )

    parser.add_argument("-v", "--version", action="version", version="%(prog)s {}".format(VERSION) )
    # parser.add_argument("-l", "--list", action=filehelper.list_files(), help="Lists all files that are tracked for syncing.")
    # parser.add_argument("-c", "--check", action=filehelper.check_files(), help="Checks if all tracked files are up to date.")
    # group = parser.add_mutually_exclusive_group(required=True)
    subparsers = parser.add_subparsers(help="pysync {command} --help")

    # Syncing
    parser_sync = subparsers.add_parser("sync", aliases=["sy"], help="Synchronizes all files. Similar to send and get with -uc options.")
    parser_sync.add_argument("file", nargs="+", help="Files to be sent by the server.")
    parser_sync.add_argument("-c", "--create", action="store_true", help="Create non-existant files and directories.")
    parser_sync.add_argument("--address", help="Address of the server.")
    parser_sync.add_argument("--port", help="Port of the server.")
    parser_sync.set_defaults(func=sync)

    # Getting
    parser_get = subparsers.add_parser("get", aliases=["ge"], help="Pulls all files from server. Overwrites local files with the same name on default.")
    parser_get.add_argument("file", nargs="+", help="Files to be sent by the server.")
    parser_get.add_argument("-u", "--update", action="store_true", help="Update local files. Older remote files are skipped.")
    parser_get.add_argument("-c", "--create", action="store_true", help="Create non-existant files and directories.")
    parser_get.add_argument("--address", help="Address of the server.")
    parser_get.add_argument("--port", help="Port of the server.")
    parser_get.set_defaults(func=get)

    # Sending
    parser_send = subparsers.add_parser("send", aliases=["se"], help="Sends files from the given directory to the server. Overwrites local files with the same name on default.")
    parser_send.add_argument("file", nargs="+", help="Files to be sent.")
    parser_send.add_argument("-u", "--update", action="store_true", help="Update remote files. Older local files are skipped.")
    parser_send.add_argument("-c", "--create", action="store_true", help="Create non-existant files and directories.")
    parser_send.add_argument("--address", help="Address of the server.")
    parser_send.add_argument("--port", help="Port of the server.")
    parser_send.set_defaults(func=send)

    # Receiving 
    parser_receive = subparsers.add_parser("receive", aliases=["re"], help="Opens a port and receives incoming files, storing them in the current directory.")
    parser_receive.add_argument("-o", "--once", action="store_true", help="Only do one transaction, then quit, closing the port.")
    parser_receive.add_argument("-c", "--continuos", action="store_true", help="Continuosly receive files, ending only when killed.")
    parser_receive.add_argument("-d", "--destination", help="Chose a different directory for file storage.")
    parser_receive.set_defaults(func=receive)

    return parser


if __name__ == "__main__":
    parser = init_argparse()
    init_logger()
    args = parser.parse_args()

    log = logging.getLogger(LOGGER_NAME)

    log.debug(f"Started with args {args}")

    if hasattr(args, "func"):
        func = args.func
        options = vars(args).copy()
        options["func"] =  options["func"].__name__ # transform function to prettier name
        try:
            args.func(options)
        except Exception as e:
            print(e)
    else:
        parser.print_help()

    log.debug(f"Closing program")
