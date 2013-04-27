#! /usr/bin/env python
#
# Generates trees using the GF commandline client's "generate_random" command.
#
# Author: Kaarel Kaljurand
# Version: 2013-04-27
#
# TODO:
#  - support -lang
#  - large values of 'depth' give stack overflow, handle this somehow
#  - what is the GF default value for 'depth'?
#  - implement iterative deepening
#  - support partial trees as input
#  - don't require the -cat argument to be specified
#
import sys
import argparse
import os
from subprocess import Popen, PIPE, STDOUT
import re
from string import Template

gf='gf'

template_gf_gr = Template("""
gr -cat=${cat} -number=${number} -depth=${depth} -probs=${probs}
""")

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

parser.add_argument('--name', type=str, action='store',
	dest='name',
	help='name of the grammar (guessed on the basis of the grammar path if missing)')

parser.add_argument('-c', '--cat', type=str, action='store',
	dest='cat',
	help='start category (REQUIRED)')

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

parser.add_argument('-t', '--timeout', type=int, action='store',
	dest='timeout',
	help='number of seconds after which the generation should timeout (NOT IMPLEMENTED)')

parser.add_argument('-v', '--version', action='version', version='%(prog)s v0.2')

args = parser.parse_args()

if args.grammar is None:
	print >> sys.stderr, 'ERROR: argument -g/--grammar is not specified'
	exit()

if args.cat is None:
	print >> sys.stderr, 'ERROR: argument -c/--cat is not specified'
	exit()

# If the name of the grammar is not given then guess it from the name of the PGF
if args.name is None:
	rawname = re.sub("^.*/", "", args.grammar)
	args.name = re.sub("\.pgf$", "", rawname)

re_abstract_line = re.compile(args.name + ': (.+)')

cmd_gf_gr = template_gf_gr.substitute(
	cat = args.cat,
	depth = args.depth,
	number = args.number,
	probs = args.probs
)


cmd_shell = [gf, '--run', '--verbose=0', args.grammar]

#print >> sys.stderr, cmd_gf_gr
#print >> sys.stderr, ' '.join(cmd_shell)

for i in range(1, args.repeat + 1):
	print >> sys.stderr, '{0}/{1}'.format(i, args.repeat)
	# TODO: run with timeout
	print exec_cmd(cmd_shell, cmd_gf_gr)
