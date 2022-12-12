#!/bin/python3
import os, sys
import threading

path = os.path.dirname('../src/')

sys.path.append(path)

import sender as sender
import receiver as receiver

r = receiver.Receiver()
s = sender.Sender()

tr = threading.Thread(target=r.receive_file, args=(), kwargs={})
print("[+] Starting thread")
ret = tr.start()
print("[+] Thread started")

s.send_file('../test')


print("[+] Joining thread")
tr.join()
print("[+] Thread joined")
# test if both files are the same


print(ret)
