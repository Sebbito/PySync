#!/bin/python3
# This file implements functions and ressources for the client side of pysync
import argparse as ap
from receiver import Receiver
from sender import Sender

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
group.add_argument('--receive', action='store_true', help='Opens a port and receives incoming files.')
group.add_argument('--send', dest='path', help='Sends files for the given directory.')

args = parser.parse_args()
print(args)

if args.listen:
    r = Receiver()
    r.receive_all()
if args.path:
    s = Sender()
    s.send(args.path)

