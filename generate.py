#! /usr/bin/env python
#
# Generates trees using the GF commandline client's "generate_random" command.
# Shows the coverage with respect to the functions defined in the grammar.
#
# Author: Kaarel Kaljurand
# Version: 2013-04-25
#
# Examples:
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
from pprint import pformat

gf='gf'

template_gf_gr = Template("""
gr -cat=${cat} -number=${number} -depth=${depth} -probs=${probs} | l -treebank -bind
""")

template_gf_pg_funs = Template("""
pg -funs
""")

def exec_cmd(cmd_shell, cmd_gf):
	"""
	Runs a command and returns it STDOUT
	"""
	p = Popen(cmd_shell, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
	return p.communicate(input=cmd_gf)[0]

def get_funs(tree):
	"""
	Returns the list of function names mentioned in the tree.
	Note: filtering by None removes empty strings
	"""
	return filter(None, re.split('[ ()]+', tree))

def register_tree(tree):
	"""
	Registers the names of the functions that make up the given tree
	"""
	funs = get_funs(tree)
	#print >> sys.stderr, 'Funs: {0}'.format(funs)
	for fun in funs:
		if fun in all_funs:
			all_funs[fun] = all_funs[fun] + 1
		else:
			if fun in other_funs:
				other_funs[fun] = other_funs[fun] + 1
			else:
				other_funs[fun] = 1

def gather_stat(gf_out):
	"""
	Looks for the generated tree in the GF output
	and registers it.
	"""
	for line in gf_out.splitlines():
		m = re_abstract_line.match(line)
		if m:
			register_tree(m.group(1))

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

parser.add_argument('-v', '--version', action='version', version='%(prog)s v0.1')

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

cmd_gf_pg_funs = template_gf_pg_funs.substitute()
cmd_gf_gr = template_gf_gr.substitute(
	cat = args.cat,
	depth = args.depth,
	number = args.number,
	probs = args.probs
)


cmd_shell = [gf, '--run', '--verbose=0', args.grammar]

#print >> sys.stderr, cmd_gf_pg_funs
#print >> sys.stderr, cmd_gf_gr
#print >> sys.stderr, ' '.join(cmd_shell)

out_gf_pg_funs = exec_cmd(cmd_shell, cmd_gf_pg_funs)
#print >> sys.stderr, '{0}'.format(out_gf_pg_funs)

all_funs = dict( (name,0)
	for name,typ in (line.split(' : ')
		for line in out_gf_pg_funs.splitlines() if '->' in line) )
other_funs = {}

for i in range(1, args.repeat + 1):
	print >> sys.stderr, '{0}/{1}'.format(i, args.repeat)
	# TODO: run with timeout
	out = exec_cmd(cmd_shell, cmd_gf_gr)
	gather_stat(out)
	print out


print >> sys.stderr, 'Simple functions\n{0}'.format(pformat(other_funs))

print >> sys.stderr, 'Complex functions\n{0}'.format(pformat(all_funs))

count = sum(1 for fun in all_funs if all_funs[fun] > 0)
print >> sys.stderr, 'Coverage: {0}/{1}'.format(count, len(all_funs))
