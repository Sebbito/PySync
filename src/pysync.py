# This file implements functions and ressources for the client side of pysync
import argparse as ap

CONF_PATH = '~/.config/pysync/client'

parser = ap.ArgumentParser(
        prog='pysync',
        description='Client Program for file synchronization with a PySync server instance.'
        )

parser.print_help()
