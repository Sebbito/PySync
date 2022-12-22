#!/bin/python3
# This file implements functions and ressources for the client side of pysync
import argparse as ap
import receiver as r
import sender as s
from constants import *

VERSION="0.0.1"

# CONF_PATH = "~/.config/pysync/client"

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
    # s = sender.Sender(update=args.update)
    s.send(args)
    exit(EXIT_SUCCESS)

def get(args):
    # s = sender.Sender(update=args.update)
    s.get(args)
    exit(EXIT_SUCCESS)

def sync(args):
    # s = sender.Sender(update=args.update)
    s.sync(args)
    exit(EXIT_SUCCESS)

if __name__ == "__main__":
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
    parser_send = subparsers.add_parser("sync", aliases=["sy"], help="Synchronizes all files. Similar to send and get with -uc options.")
    parser_send.add_argument("-c", "--create", action="store_true", help="Create non-existant files and directories.")
    parser_send.set_defaults(func=send)

    # Getting
    parser_send = subparsers.add_parser("get", aliases=["ge"], help="Pulls all files from server. Overwrites local files with the same name on default.")
    parser_send.add_argument("-u", "--update", action="store_true", help="Update local files. Older remote files are skipped.")
    parser_send.add_argument("-c", "--create", action="store_true", help="Create non-existant files and directories.")
    parser_send.set_defaults(func=send)

    # Sending
    parser_send = subparsers.add_parser("send", aliases=["se"], help="Sends files from the given directory to the server. Overwrites local files with the same name on default.")
    parser_send.add_argument("file", nargs="+", help="Files to be sent.")
    parser_send.add_argument("-u", "--update", action="store_true", help="Update remote files. Older local files are skipped.")
    parser_send.add_argument("-c", "--create", action="store_true", help="Create non-existant files and directories.")
    parser_send.set_defaults(func=send)

    # Receiving 
    parser_receive = subparsers.add_parser("receive", aliases=["re"], help="Opens a port and receives incoming files, storing them in the current directory.")
    parser_receive.add_argument("-o", "--once", action="store_true", help="Only do one transaction, then quit, closing the port.")
    parser_receive.add_argument("-c", "--continuos", action="store_true", help="Continuosly receive files, ending only when killed.")
    parser_receive.add_argument("-d", "--destination", help="Chose a different directory for file storage.")
    parser_receive.set_defaults(func=receive)

    args = parser.parse_args()

    if hasattr(args, "func"):
        func = args.func
        options = vars(args).copy()
        options["func"] =  options["func"].__name__# this is not needed for any process
        print(f"{options}")
        args.func(options)
    else:
        parser.print_help()
