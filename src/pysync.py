#!/bin/python3
# This file implements functions and ressources for the client side of pysync
import argparse as ap
import receiver
import sender 
from constants import *

VERSION='0.0.1'

# CONF_PATH = '~/.config/pysync/client'

def receive(args):
    r = receiver.Receiver()
    if args.once == True:
        r.receive_all()
    elif args.forever == True:
        r.receive_forever()
    else:
        print("Whoops! Could not parse that argument. Please try again with a different argument.")
        exit(EXIT_FAILURE)
    exit(EXIT_SUCCESS)

parser = ap.ArgumentParser(
        prog='pysync',
        description='Program for file synchronization with another machine running PySync.'
        )

parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(VERSION) )
# parser.add_argument('-l', '--list', action=filehelper.list_files(), help='Lists all files that are tracked for syncing.')
# parser.add_argument('-c', '--check', action=filehelper.check_files(), help='Checks if all tracked files are up to date.')
# group = parser.add_mutually_exclusive_group(required=True)
subparsers = parser.add_subparsers(help='pysync {command} --help')
# parser_send = subparser.add_parser('send', help="Send one or more files")
parser.add_argument('-s', '--send', dest='path', nargs='+' ,help='Sends files for the given directory to the server.')


parser_receive = subparsers.add_parser('receive', help="Opens a port and receives incoming files, storing them in the current directory.")
parser_receive.add_argument('-o', '--once', action='store_true', help='Only do one transaction, then quit, closing the port.')
parser_receive.add_argument('-f', '--forever', action='store_true', help='Continuosly receive files, ending only when killed.')
parser_receive.set_defaults(func=receive)

args = parser.parse_args()
print(args)

if hasattr(args, 'func'):
    args.func(args)
elif args.path != None:
    s = sender.Sender()
    s.send(args.path)
    exit(EXIT_SUCCESS)

parser.print_help()
