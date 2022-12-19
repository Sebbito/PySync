#!/bin/python3
# This file implements functions and ressources for the client side of pysync
import argparse as ap
import receiver
import sender 
from constants import *

VERSION='0.0.1'

# CONF_PATH = '~/.config/pysync/client'

def receive(args):
    if args.destination:
        r = receiver.Receiver(destination = args.destination)
    else:
        r = receiver.Receiver()

    if args.once == True:
        r.receive_all()
    elif args.continuos == True:
        r.receive_forever()
    else:
        print("Whoops! Could not parse that argument. Please try again with a different argument.")
        exit(EXIT_FAILURE)
    exit(EXIT_SUCCESS)

def send(args):
    s = sender.Sender()
    if args.file:
        s.send(args.file)
    exit(EXIT_SUCCESS)

if __name__ == "__main__":
    parser = ap.ArgumentParser(
            prog='pysync',
            description='Program for file synchronization with another machine running PySync.'
            )

    parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(VERSION) )
    # parser.add_argument('-l', '--list', action=filehelper.list_files(), help='Lists all files that are tracked for syncing.')
    # parser.add_argument('-c', '--check', action=filehelper.check_files(), help='Checks if all tracked files are up to date.')
    # group = parser.add_mutually_exclusive_group(required=True)
    subparsers = parser.add_subparsers(help='pysync {command} --help')

    # Sending
    parser_send = subparsers.add_parser('send', aliases=['s'], help='Sends files from the given directory to the server.')
    parser_send.add_argument('file', nargs='+', help='Files to be sent.')
    # parser_send.add_argument('-u', '--update', action='store_true', help='Only update files.')
    parser_send.set_defaults(func=send)

    # Receiving 
    parser_receive = subparsers.add_parser('receive', aliases=['r'], help="Opens a port and receives incoming files, storing them in the current directory.")
    parser_receive.add_argument('-o', '--once', action='store_true', help='Only do one transaction, then quit, closing the port.')
    parser_receive.add_argument('-c', '--continuos', action='store_true', help='Continuosly receive files, ending only when killed.')
    parser_receive.add_argument('-d', '--destination', help='Directory where the files should be stored.')
    parser_receive.set_defaults(func=receive)

    args = parser.parse_args()
    print(args)

    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()
