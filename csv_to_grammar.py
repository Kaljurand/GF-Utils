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
#  3. lin operation or simple string in language 1
#  4. lin operation or simple string in language 2
#  ...
#
# The grammar name is the name of the input file.
# The language names must be provided in the first row.

# Author: Kaarel Kaljurand
# Version: 2013-02-22
#
# Examples:
#
# ./csv_to_grammar.py --file Sheet1.csv --name Geograpy --dir outdir
#
# TODO:
#  - use underscores in ACE entries
#  - cleanup (especially string building)
#  - add: --url <url of CSV-formatted data>
#
import sys
import argparse
import os
import re
import csv
from string import Template

#path_directive = "--# -path=.:present\n"
path_directive = ""

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
	word = strip_cell(word)
	if word == "":
		raise Exception("empty function name")
	word = unicode_to_gfcode(word)
	return word + "_" + cat

def make_cat(cat, default_cat):
	cat = strip_cell(cat)
	if cat == "":
		return default_cat
	return cat

def strip_cell(cell):
	"""
	Remove [comment text], normalize whitespace, remove padding space
	"""
	cell = re.sub(r'\[[^]]*\]', '', cell)
	cell = re.sub(r'\s+', ' ', cell)
	cell = cell.strip()
	return cell

def make_lin(cell, cat, col_id, cell0):
	"""
	If the lin cell contains a bare string (e.g. '"capital" feminine')
	i.e. no operator call (e.g. 'mkV2 "ask"', 'mkV2 L.ask_V'),
	then create a call to a smart paradigm.
	The whitespace is trimmed.
	If there are not spaces then put the string into quotes.
	TODO: rewrite the ACE-specific code in a general way
	"""
	is_ace_col = (col_id == first_lang_col)

	cell = strip_cell(cell)

	# If the cell is empty then we return None,
	# unless we are in a the ACE-column in which case
	# we'll try to use the function name as the ACE entry.
	if cell == "":
		if is_ace_col and cell0 != "":
			cell = cell0
		else:
			return None


	# if there are no existing quotes
	# and it is not an entry like 'mkV2 (I.contener_V)'
	if cell.find('"') == -1 and not re.search('[A-Z]\.', cell):
		cell = '"' + cell + '"'

	if cat == "CN":
		if not has_prefix_some(cell, ['mkCN', 'aceN']):
			if is_ace_col:
				return 'aceN {0}'.format(cell)
			return 'mkCN (mkN {0})'.format(cell)
	elif cat == "V2":
		if not has_prefix_some(cell, ['mkV2', 'prepV2', 'aceV2']):
			if is_ace_col:
				return 'aceV2 {0}'.format(cell)
			return 'mkV2 (mkV {0})'.format(cell)
	else:
		if not has_prefix_some(cell, ['mk' + cat, 'ace' + cat]):
			if is_ace_col:
				return 'ace{0} {1}'.format(cat, cell)
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

def unicode_to_gfcode(u):
	"""
	"""
	u1 = u.decode("utf8")
	u2 = u1.encode('ascii', 'xmlcharrefreplace')
	u3 = re.sub(r'[^A-Za-z0-9\']', '_', u2)
	return u3

def make_name2(u):
	"""
	Remove all whitespace and lowercase the result.
	"""
	return re.sub(r'\s+', '', u).lower()


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
funs2 = {}
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
		try:
			if len(row) < 2:
				raise Exception("less than 2 fields")
			cat = make_cat(row[1], "PN")
			funname = make_fun_name(row[0], cat)
			funname2 = make_name2(funname)
			if funname in funs:
				raise Exception("duplicate function name: '" + funname + "'")
			if funname2 in funs2:
				raise Exception("similar function name: '" + funname + "'")
			funs[funname] = cat
			funs2[funname2] = cat
			i = first_lang_col
			for cell in row[first_lang_col:]:
				if i not in lins:
					lins[i] = {}
				lin = make_lin(cell, cat, i, strip_cell(row[0]))
				if lin != None:
					lins[i][funname] = lin
				i = i + 1
			print >> sys.stderr, 'Reading: ' + '  |  '.join(row)
		except Exception as e:
			print >> sys.stderr, 'Error: {:}: {:}'.format(e.message, '  |  '.join(row))

# Put the abstract syntax into a string
abstract = path_directive
abstract += Template(module_header[1]).substitute(name = args.name) + " {\nfun\n"
for funname in sorted(funs, key=str.lower):
	abstract = abstract + funname + " : " + funs[funname] + " ;\n"
abstract = abstract + "}"

# ... and write it into a file.
write_file(args.dir, args.name + ".gf", abstract)

# Put each concrete syntax into a string
for l in lins:
	try:
		lang_name = strip_cell(header[l])
		if lang_name == "":
			raise Exception("bad language name: '" + header[l] + "'")
		concrete = path_directive
		concrete += Template(module_header[l]).substitute(name = args.name, lang = lang_name) + " {\n"
		concrete += "flags coding=utf8 ;\nlin\n"
		for funname in sorted(lins[l], key=str.lower):
			concrete = concrete + funname + " = " + lins[l][funname] + " ;\n"
		concrete = concrete + "}"
		# ... and write it into a file.
		write_file(args.dir, args.name + lang_name + ".gf", concrete)
	except Exception as e:
		print >> sys.stderr, 'Error: {:}'.format(e.message)
