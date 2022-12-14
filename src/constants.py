#!/bin/python3

PYSYNC_LOG_FILE = "~/.pysync/pysync.log"
PYSYNC_CONF_FILE = "~/.pysync/pysync.conf"
LOGGER_NAME = "pysync_logger"

# defaults
DEFAULT_PORT = 40500
DEFAULT_SERVER = "127.0.0.1"
BUFFER_SIZE = 1024
DEFAULT_DESTINATION = './'

# Protocol stuff
SEPARATOR = "[SEP]"
OK = "[OK]"
SKIP = "[SKIP]"
UPDATE = "[UPDATE]"

# exit codes
EXIT_SUCCESS = 0
EXIT_FAILURE = 0
