#!/usr/bin/env python3

"""
curlgen.py: cURL configuration generator

Reads URLs from stdin and writes a cURL configuration script to stdout.
"""

import os
import socket
import argparse
from sys import stdin, stderr
from urllib.parse import urlsplit

parser = argparse.ArgumentParser(description='cURL configuration generator')
parser.add_argument('--overwrite', action='store_true',
                    help='overwrite files which already exist')
parser.add_argument('-v', '--verbose', action='store_true',
                    help='generate informative comments')
parser.add_argument('-s', '--silent', action='store_true',
                    help='silence error messages')
parser.add_argument('-d', '--base-directory', default='.',
                    help='the directory relative to which files will be saved')
parser.add_argument('--infer', action='store_true',
                    help='infer save path from URL')
parser.add_argument('-i', '--index', type=int, default=0,
                    help='index into the path component for path inference')
parser.add_argument('-b', '--blacklist', nargs='*', default=[],
                    help='blacklisted filetypes')
parser.add_argument('-e', '--extra', nargs='*', default=[],
                    help='user-supplied cURL options')

args = parser.parse_args()
args.base_directory = os.path.expanduser(args.base_directory)
if not os.path.exists(args.base_directory):
    os.makedirs(args.directory)

def print_c(msg):
    if args.verbose:
        print('# {}'.format(msg))

def print_e(msg):
    if not args.silent:
        print('# {}'.format(msg), file=stderr)

def get_path(url, base, infer, index):
    usp = urlsplit(url)
    if usp.netloc == '':
        usp = urlsplit('//' + url)
    upath = usp.path
    spath = upath.split('/')

    path = base
    name = spath[-1] if spath[-1] != '' else 'index'

    if infer:
        if index < len(spath):
            if index != 0:
                path = os.path.join(base, spath[index])
            else:
                path = os.path.join(base, *spath[:-1])
        else:
            print_e('failed to infer save path for {}'.format(url))

    return path, name

while True:
    line = stdin.readline().strip()
    if line == '': break;

    if line.split('.')[-1] in args.blacklist:
        print_c('Skipping "{}": blacklisted'.format(line))
        continue

    path, name = get_path(line, args.base_directory, args.infer, args.index)
    if not os.path.exists(path):
        os.makedirs(path)

    save_path = os.path.join(path, name)
    if not args.overwrite and os.path.exists(save_path):
        print_c('Skipping "{}": file already exists'.format(save_path))
        continue

    print_c('curl -o {} --url {} ...'.format(save_path, line))
    print('url = "{}"'.format(line))
    print('output = "{}"'.format(save_path))

    if args.extra != []:
        print_c('user-supplied options...')
        for opt in args.extra:
            print(opt)
    print()

