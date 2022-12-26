# PySync
An experimental python tool for syncing files with another machine.

# Warning
This tool is intended as a learning project for myself. It is nowhere near finished and not tested at all and is not secure.
If you wish to sync your files with a good tool, use rsync.
Use at your own risk.

# Basic Usage
For information about the use of the program refer to the help pages
```bash
pysync -h
pysync send -h
pysync receive -h
pysync get -h
pysync sync -h
```

Pysync will look for a connection on the provided address/port or if none are specified it will look on 127.0.0.:40500.
Connections can be set up with `pysync receive`.

It will send the arguments, receive an ok and then depending on the function used (send, get, sync):
- Send: The client will send file information and then the file contents to the server
- Get: The client opens up a receiving port and send the port number to the server. The server will then start the sending routine and send information to the client.
- Sync: The client will first send and then get file information.

Pysync will not create files on default and overwrite any existing file unless the update option is set.
