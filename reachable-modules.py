#! /usr/bin/env python
#
# Lists the modules that are imported in the given files,
# either directly or indirectly.
#
# This script executes:
#
#     echo "dg" | gf --path $path --retain file1 file2 ...
#
# and parses out the module names found in the generated dependency diagram
# (a file with the name _gfdepgraph.dot which is saved into the current directory).
# The STDOUT and STDERR of GF are written into STDOUT.
# (Maybe there is a better way to do this...)

# Author: Kaarel Kaljurand
# Version: 2012-11-02
#
# Examples:
#
import sys
import argparse
import os
from subprocess import Popen, PIPE, STDOUT
import re

gf='gf'

# This file is created into the current directory,
# as a result of the GF dg command.
# TODO: remove it automatically
gfdepgraph='_gfdepgraph.dot'

re_module_name = re.compile('([^ ]+) \[')


# Commandline arguments parsing
parser = argparse.ArgumentParser(description='List the modules that are (transitively) imported from the given modules')

parser.add_argument('src_files', metavar='SRC', type=str, nargs='+',
	help='GF files that constitute the starting nodes of the module hierarchy')

parser.add_argument('-p', '--path', type=str, action='store', dest='path',
	help='GF library search path')

parser.add_argument('-v', '--version', action='version', version='%(prog)s v0.1')

args = parser.parse_args()

cmd = [gf, '--run', '--verbose=0', '--retain']
if args.path is not None:
	cmd.extend(['--path', args.path])
cmd.extend(args.src_files)
#print >> sys.stderr, ' '.join(cmd)
p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
print >> sys.stderr, p.communicate(input='dg')[0]
with open(gfdepgraph, 'r') as f:
	for line in f:
		# match = search only the beginning of the string
		m = re_module_name.match(line.rstrip())
		if m:
			print m.group(1)
