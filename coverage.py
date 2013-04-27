#! /usr/bin/env python
#
# Shows the coverage with respect to the functions defined in the grammar.
#
# Author: Kaarel Kaljurand
# Version: 2013-04-26
#
import sys
import argparse
import os
from subprocess import Popen, PIPE, STDOUT
import re
from string import Template

gf='gf'

template_gf_pg_funs = Template("""
pg -funs
""")

def exec_cmd(cmd_shell, cmd_gf):
	"""
	Runs a GF command and returns its STDOUT
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
	if tree in trees:
		trees[tree] = trees[tree] + 1
	else:
		trees[tree] = 1
	funs = get_funs(tree)
	#print >> sys.stderr, 'Funs: {0}'.format(funs)
	for fun in funs:
		if fun in funs_complex:
			funs_complex[fun] = funs_complex[fun] + 1
		else:
			if fun in funs_simple:
				funs_simple[fun] = funs_simple[fun] + 1
			else:
				funs_simple[fun] = 1

parser = argparse.ArgumentParser(description='Shows how many functions of the given grammar are present in the trees given in STDIN.')

parser.add_argument('-g', '--grammar', type=str, action='store',
	dest='grammar',
	help='full path to the PGF (REQUIRED)')

parser.add_argument('-v', '--version', action='version', version='%(prog)s v0.1')

args = parser.parse_args()

if args.grammar is None:
	print >> sys.stderr, 'ERROR: argument -g/--grammar is not specified'
	exit()

cmd_shell = [gf, '--run', '--verbose=0', args.grammar]
cmd_gf_pg_funs = template_gf_pg_funs.substitute()

out_gf_pg_funs = exec_cmd(cmd_shell, cmd_gf_pg_funs)

trees = {}
funs_simple = {}
funs_complex = dict( (name,0)
	for name,typ in (line.split(' : ')
		for line in out_gf_pg_funs.splitlines() if '->' in line) )


count_trees = 0
for line in sys.stdin:
	tree = line.strip()
	if tree is not '':
		register_tree(tree)
		count_trees = count_trees + 1


count = sum(1 for fun in funs_complex if funs_complex[fun] > 0)
print >> sys.stderr, 'Trees: {0}'.format(count_trees)
print >> sys.stderr, 'Unique trees: {0}'.format(len(trees))
print >> sys.stderr, 'Simple functions: {0}'.format(len(funs_simple))
print >> sys.stderr, 'Complex function coverage: {0}/{1}'.format(count, len(funs_complex))

for key in sorted(funs_simple.iterkeys()):
	print 's\t{0}\t{1}'.format(key, funs_simple[key])

for key in sorted(funs_complex.iterkeys()):
	print 'c\t{0}\t{1}'.format(key, funs_complex[key])
