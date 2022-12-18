#!/usr/bin/python3
from pathlib import Path

READ_BUF = 512

class Generator(object):
    # def __init__(self):

    # def __exit__(self, *args):

    def generate_file_list(self, mixed):
        ''' Generates a list of files from the mixed object.
            mixed could be a single file or multiple directories
            We will return a list of all files found'''
        
        if mixed == None:
            print("[!] File list is empty. Aborting")
            exit()
        
        file_list = []

        for path in mixed:
            self.fetch_files(path, file_list)

        return file_list

    def fetch_files(self, path, list):
        ''' Uses recursion to add all files in path to the list.'''

        p = Path(path)
        if p.exists():
            if p.is_dir():
                for file in p.iterdir():
                    self.fetch_files(file, list)
            elif p.is_file():
                list.append(p)
            else:
                print("[!] Path {p} is not viable. Aborting")
                exit()
        else:
            print("[!] Path {p} is not viable. Aborting")
            exit()

