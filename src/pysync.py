#!/bin/python3
# This file implements functions and ressources for the client side of pysync
import argparse as ap
import receiver
import sender 

VERSION='0.0.1'

# CONF_PATH = '~/.config/pysync/client'

parser = ap.ArgumentParser(
        prog='pysync',
        description='Program for file synchronization with another machine running PySync.'
        )

parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(VERSION) )
# parser.add_argument('-l', '--list', action=filehelper.list_files(), help='Lists all files that are tracked for syncing.')
# parser.add_argument('-c', '--check', action=filehelper.check_files(), help='Checks if all tracked files are up to date.')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-r', '--receive', action='store_true', help='Opens a port and receives incoming files, storing them in the current directory.')
group.add_argument('-s', '--send', dest='path', nargs=1 ,help='Sends files for the given directory to the server.')

args = parser.parse_args()

if args.receive == True:
    r = receiver.Receiver()
    r.receive_all()
elif args.path != None:
    s = sender.Sender()
    s.send(args.path)
else:
    parser.print_help()
