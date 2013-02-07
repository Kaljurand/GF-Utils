#! /usr/bin/env python

# Creates a GF grammar on the basis of a CSV file.
# The idea is to manage multilingual vocabularies in a spreadsheet
# (collaboratively) and automatically convert it into GF.
#
# Rows:
#  1. Languge names
#  2. Modules headers (interpreted as Python templates, with slots 'name', 'lang')
#  3-n. data
#
# Columns:
#  1. English word (lemma form), should be reasonably long and unambiguous
#  2. GF (RGL) category
#  3. lin operation in language 1
#  4. lin operation in language 2
#  ...
#
# The grammar name is the name of the input file.
# The language names must be provided in the first row.

# Author: Kaarel Kaljurand
# Version: 2013-02-07
#
# Examples:
#
# ./csv_to_grammar.py --file Sheet1.csv --name Geograpy --dir outdir
#
# TODO:
#  - cleanup (especially string building)
#  - allow simple string instead of "lin operation" and fill in the lin operation
#    automatically, this would allow us to use Google Drive's translation function
#    =GoogleTranslate(A3, "en", "it")
#  - get the input directly from Google Drive (using API)
#
import sys
import argparse
import os
import re
import csv
from string import Template


def write_file(dir, filename, content):
	"""
	"""
	path = os.path.join(dir, filename)
	print >> sys.stderr, 'Creating: ' + path
	f = open(path, 'w')
	f.write(content)
	f.close()

def make_grammar_name(filename):
	"""
	TODO: better regexp for generating legal GF grammar names
	"""
	nodir = re.sub(r'.*\/', '', filename)
	noext = re.sub(r'\..*', '', nodir)
	return re.sub(r'[^A-Za-z0-9]', '_', noext)

def make_fun_name(word, cat):
	"""
	TODO: better regexp for generating legal GF fun names
	"""
	return re.sub(r'[^A-Za-z0-9]', '_', word) + "_" + cat

def make_lin(cell, cat):
	"""
	If the lin cell contains a bare string (e.g. '"capital" feminine')
	i.e. no operator call (e.g. 'mkV2 "ask"', 'mkV2 L.ask_V'),
	then create a call to a smart paradigm.
	The whitespace is trimmed.
	If there are not spaces then put the string into quotes.
	"""
	cell = cell.strip()
	if cell == "":
		cell = "TODO"

	# if there are no existing quotes
	# and it is not an entry like 'mkV2 (I.contener_V)'
	if cell.find('"') == -1 and not re.search('[A-Z]\.', cell):
		cell = '"' + cell + '"'

	if cat == "CN":
		if not has_prefix_some(cell, ['mkCN', 'aceN']):
			return 'mkCN (mkN {0})'.format(cell)
	elif cat == "V2":
		if not has_prefix_some(cell, ['mkV2', 'prepV2', 'aceV2']):
			return 'mkV2 (mkV {0})'.format(cell)
	else:
		if not has_prefix_some(cell, ['mk' + cat, 'ace' + cat]):
			return 'mk{0} {1}'.format(cat, cell)
	return cell

def has_prefix_some(s, prefix_set):
	"""
	True if the given string has a prefix
	that is in the given set.
	"""
	for prefix in prefix_set:
		if s.find(prefix, 0) != -1:
			return True
	return False


# Commandline arguments parsing
parser = argparse.ArgumentParser(description='Generates 2 GF modules for a given language')

parser.add_argument('-f', '--file', type=str, action='store', dest='csv_file',
                   help='name of the CSV file (OBLIGATORY)')

parser.add_argument('-n', '--name', type=str, action='store', dest='name',
                   help='name of the grammar, e.g. Phrasebook (OBLIGATORY)')

parser.add_argument('-d', '--dir', type=str, action='store', dest='dir',
                   default='.',
                   help='output directory')

parser.add_argument('-v', '--version', action='version', version='%(prog)s v0.1')

args = parser.parse_args()

if args.csv_file is None:
	print >> sys.stderr, 'ERROR: argument -f/--file is not specified'
	exit()

if args.name is None:
	args.name = make_grammar_name(args.csv_file)

funs = {}
lins = {}
header = []
first_lang_col = 2
with open(args.csv_file, 'rb') as csvfile:
	#dialect = csv.Sniffer().sniff(csvfile.read(1024))
	#csvfile.seek(0)
	#reader = csv.reader(csvfile, dialect)
	# TODO: we assume Google Drive's CSV conventions
	# as sniffing didn't seem to get these right.
	reader = csv.reader(csvfile, delimiter=',', quotechar='"')
	header = next(reader)
	module_header = next(reader)
	for row in reader:
		cat = row[1]
		funname = make_fun_name(row[0], cat)
		funs[funname] = cat
		i = first_lang_col
		for lin in row[first_lang_col:]:
			if i not in lins:
				lins[i] = {}
			lins[i][funname] = make_lin(lin, cat)
			i = i + 1
		print >> sys.stderr, 'Reading: ' + '  |  '.join(row)

# Put the abstract syntax into a string
abstract = "--# -path=.:present\n"
abstract += Template(module_header[1]).substitute(name = args.name) + " {\nfun\n"
for funname in sorted(funs, key=str.lower):
	abstract = abstract + funname + " : " + funs[funname] + " ;\n"
abstract = abstract + "}"

# ... and write it into a file.
write_file(args.dir, args.name + ".gf", abstract)

# Put each concrete syntax into a string
for l in lins:
	lang_name = header[l]
	concrete = "--# -path=.:present\n"
	concrete += Template(module_header[l]).substitute(name = args.name, lang = lang_name) + " {\n"
	concrete += "flags coding=utf8 ;\nlin\n"
	for funname in sorted(lins[l], key=str.lower):
		concrete = concrete + funname + " = " + lins[l][funname] + " ;\n"
	concrete = concrete + "}"
	# ... and write it into a file.
	write_file(args.dir, args.name + lang_name + ".gf", concrete)
