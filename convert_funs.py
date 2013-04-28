#! /usr/bin/env python
#
# Input format:
#   Z_Var : Var ;
#   a2VP : A2 -> NP -> VP ;
#
# Example:
#
#   echo "pg -funs" | gf --run Grammar.pgf | convert_funs.py
#
# Author: Kaarel Kaljurand
# Version: 2013-04-28
#
import sys
import argparse
import os
import re
from string import Template

gf='gf'

re_fun = re.compile('(.+) : (.+) ;')

consumer = {}

def escape_prolog(atom):
	"""
	TODO: don't add quotes if not needed
	TODO: handle token-internal quotes
	"""
	return "'" + atom + "'"

def escape_prolog_list(atom_list):
	return [escape_prolog(x) for x in atom_list]

def format_prolog_fun(fun, args, value):
	print 'fun({0}, [{1}], {2}).'.format(
		escape_prolog(fun),
		', '.join(escape_prolog_list(args)),
		escape_prolog(value))

def format_prolog_consumer(cat, fun, dim):
	print 'consumer({0}, {1}, {2}).'.format(
		escape_prolog(cat),
		escape_prolog(fun),
		dim)

def add_consumer(cat, fun, dim):
	if cat not in consumer:
		consumer[cat] = {}
	consumer[cat][fun] = dim


parser = argparse.ArgumentParser(description='Formats GF function declarations in Prolog')

parser.add_argument('-t', '--to', type=str, action='store',
	default='prolog',
	dest='to',
	help='output format (default: prolog)')

parser.add_argument('-v', '--version', action='version', version='%(prog)s v0.1')

args = parser.parse_args()

for line in sys.stdin:
	m = re_fun.match(line)
	if m:
		fun = m.group(1)
		cats = m.group(2).split(' -> ')
		lastpos = len(cats) - 1
		args = cats[0 : lastpos]
		value = cats[lastpos]
		dim = lastpos
		format_prolog_fun(fun, args, value)
		pos = 0
		for arg in args:
			add_consumer(arg, fun, pos)
			pos = pos + 1
	else:
		print >> sys.stderr, 'Warning: ignored: {0}'.format(line)

# TODO: currently sorted by the position index,
# could be sorted by the number of arguments of the function
for cat in consumer:
	funs = consumer[cat]
	for fun in sorted(funs, key=funs.get, reverse=False):
		dim = funs[fun]
		format_prolog_consumer(cat, fun, dim)
