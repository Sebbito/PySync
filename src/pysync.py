# This file implements functions and ressources for the client side of pysync
import argparse as ap
import sync

VERSION='0.0.1'

CONF_PATH = '~/.config/pysync/client'

parser = ap.ArgumentParser(
        prog='pysync',
        description='Client Program for file synchronization with a PySync server instance.'
        )

parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(VERSION) )
parser.add_argument('-l', '--list', action=sync.list_files(), help='Lists all files that are synced')
# parser.print_help()
args = parser.parse_args()
print(vars(args))
