#! /usr/bin/env python3

# Parsing using libpgf.
# TODO: does not work
#
# Author: Kaarel Kaljurand
# Version: 2013-06-18
#
# Examples:
#
# echo "hello" | python3 parse-with-libpgf.py -f Phrasebook.pgf -l en_US
#
from pgf.pygf import *
from pgf import *
import pgf.fun as f
import sys
import argparse
import os
import re


def process_strings():
	"""
	"""
	count = 0
	for line in sys.stdin:
		line = line.strip()
		count = count + 1
		expr,*_ = parse(line, lang=args.lang)
		l,*_ = linearize(expr, lang=args.lang)
		print(l)


parser = argparse.ArgumentParser(description='Parser')

parser.add_argument('-f', '--pgf', type=str, action='store', dest='pgf',
	help='path to the PGF-formatted grammar (OBLIGATORY)')

parser.add_argument('-l', '--lang', type=str, action='store', dest='lang',
	default='en_US',
	help='ISO language code (DEFAULT: en_US)')

parser.add_argument('-v', '--version', action='version', version='%(prog)s v0.1')

args = parser.parse_args()

if args.pgf is None:
	print("ERROR: argument -f/--pgf is not specified", file=sys.stderr)
	exit()


import_pgf(args.pgf)

process_strings()
