#! /usr/bin/env python

# Compiles a PGF on the GF cloud
# Author: Kaarel Kaljurand
# Version: 2012-10-25
#
# Examples:
#
# python make-pgf.py --dir /tmp/gfse.123 --langs Eng,Ger Phrasebook
#
import sys
import argparse
import os
import json
import subprocess
import re

curl='curl'
EXT='.gf'

# Commandline arguments parsing
parser = argparse.ArgumentParser(description='Compiles a PGF on the GF cloud')

parser.add_argument('name', metavar=('NAME'), type=str,
	help='name of the grammar (i.e. abstract syntax)')

parser.add_argument('-d', '--dir', type=str, action='store', dest='dir',
	help='GF webservice directory (OBLIGATORY)')

parser.add_argument('-s', '--server', type=str, action='store', dest='server',
	default='http://localhost:41296',
	help='name of the GF cloud service, default=http://localhost:41296')

parser.add_argument('-l', '--langs', type=str, action='store', dest='langs',
	help='comma-separated list of 3-letter language codes, e.g. Eng,Ger,Spa (OBLIGATORY)')

parser.add_argument('--verbosity', type=int, action='store', dest='verbosity',
	default='1',
	help='amount of output to produce')

parser.add_argument('-v', '--version', action='version', version='%(prog)s v0.1')

args = parser.parse_args()

if args.dir is None:
	print >> sys.stderr, 'ERROR: argument -d/--dir is not specified'
	exit()

if args.langs is None:
	print >> sys.stderr, 'ERROR: argument -l/--langs is not specified'
	exit()

name = args.name
langs = args.langs.split(',')
params = [ '-d' + name + x + EXT + '=' for x in langs ]
cmd = [curl, '-d', 'dir=' + args.dir, '-d', 'command=remake']
cmd.extend(params)
cmd.append(args.server + "/cloud")

if args.verbosity > 1:
	print >> sys.stderr, ' '.join(cmd)

p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out,err = p.communicate()
result = json.loads(out)

if args.verbosity > 1:
	print json.dumps(result, indent=4)

if args.verbosity > 0:
	if result["errorcode"] == "OK":
		print "OK"
	else:
		print result["output"]
