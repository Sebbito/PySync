#!/usr/bin/python3
import hashlib
from pathlib import Path
from constants import *

def generate_file_list(mixed):
    ''' Generates a list of path objects from the mixed object.
        mixed could be a single file or multiple directories
        Will return a list of all files found'''
    
    if mixed == None:
        print("[!] File list is empty. Aborting")
        exit()
    
    file_list = []

    for path in mixed:
        fetch_files(path, file_list)

    return file_list

def get_file_list_and_count(files):
    file_list = generate_file_list(files)
    file_count = len(file_list)

    print(f"[i] Found {file_count} files.")
    return file_list, file_count


def fetch_files(path, list):
    ''' Uses recursion to add all files in path to the list.'''

    p = Path(path)
    if p.exists():
        if p.is_dir():
            for file in p.iterdir():
                fetch_files(file, list)
        elif p.is_file():
            list.append(p)
        else:
            print("[!] Path {p} is not viable. Aborting")
            exit(EXIT_FAILURE)
    else:
        print("[!] Path {p} is not viable. Aborting")
        exit(EXIT_FAILURE)

def calculate_md5(file):
    ''' Calculates the md5 sum for the file. '''
    hash_md5 = hashlib.md5()
    with open(file, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
