#! /usr/bin/env python
#
# Expects partial trees in STDIN (make these e.g. using fun_path.pl).
# Completes these using the GF commandline client's "generate_random" command.
#
# The long term plan of this humble script is to offer all kinds of generation
# and combinations of different types of generation:
#  - top down
#  - bottom up
#  - probability-guided
#  - exhaustive
#  - look-ahead based
#
# Author: Kaarel Kaljurand
# Version: 2013-04-29
#
# TODO:
#  - implement proper timeout (available in Python v3.3)
#  - large values of 'depth' give stack overflow, handle this somehow
#  - implement iterative deepening, i.e. if "no tree found" then increase depth
#  - don't required the probs file (the /dev/null based default is probably not portable)
#
import sys
import argparse
import os
from subprocess import Popen, PIPE, STDOUT
import re
from string import Template

gf='gf'

template_gf_gr = Template("""gr -lang=${lang} -number=${number} -depth=${depth} -probs=${probs}""")

def exec_cmd(cmd_shell, cmd_gf):
	"""
	Runs a command and returns it STDOUT
	"""
	p = Popen(cmd_shell, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
	return p.communicate(input=cmd_gf)[0]


# Commandline arguments parsing
parser = argparse.ArgumentParser(description='Random generation')

parser.add_argument('-g', '--grammar', type=str, action='store',
	dest='grammar',
	help='full path to the PGF (REQUIRED)')

parser.add_argument('-c', '--cat', type=str, action='store',
	dest='cat',
	help='start category')

# TODO: use a more universal default (e.g. 'some' or 'all' if backend supports)
parser.add_argument('-l', '--lang', type=str, action='store',
	default='Ace',
	dest='lang',
	help='uses only functions that have linearizations in all these languages')

parser.add_argument('-d', '--depth', type=int, action='store',
	default=5,
	dest='depth',
	help='the maximum generation depth')

parser.add_argument('-n', '--number', type=int, action='store',
	default=1,
	dest='number',
	help='number of trees in the output')

parser.add_argument('--probs', type=str, action='store',
	default='/dev/null',
	dest='probs',
	help='path to the probabilities file')

parser.add_argument('-r', '--repeat', type=int, action='store',
	default=1,
	dest='repeat',
	help='number of times to repeat the generation')

#floating point number with an optional suffix:
# `s' for seconds (the default), `m' for minutes, `h' for hours or `d' for days.
parser.add_argument('-t', '--timeout', type=str, action='store',
	dest='timeout',
	help='number of seconds after which the generation should timeout (works only on Linux)')

parser.add_argument('-v', '--version', action='version', version='%(prog)s v0.2')

args = parser.parse_args()

if args.grammar is None:
	print >> sys.stderr, 'ERROR: argument -g/--grammar is not specified'
	exit()

cmd_gf_gr = template_gf_gr.substitute(
	lang = args.lang,
	depth = args.depth,
	number = args.number,
	probs = args.probs
)

if args.cat is not None:
	cmd_gf_gr = cmd_gf_gr + " " + "-cat=" + args.cat

cmd_shell = [gf, '--run', '--verbose=0', args.grammar]

if args.timeout is not None:
	cmd_shell = ['timeout', args.timeout] + cmd_shell

#print >> sys.stderr, cmd_gf_gr
#print >> sys.stderr, ' '.join(cmd_shell)

count_input_tree = 0

for line in sys.stdin:
	tree = line.strip()
	if tree is '':
		continue
	count_input_tree = count_input_tree + 1
	for i in range(1, args.repeat + 1):
		print >> sys.stderr, '{0}/({1}/{2})/{3}'.format(count_input_tree, i, args.repeat, tree)
		cmd = cmd_gf_gr + " " + tree
		#print >> sys.stderr, '{0}'.format(cmd)
		print exec_cmd(cmd_shell, cmd)
