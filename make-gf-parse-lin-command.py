#! /usr/bin/env python

# Author: Kaarel Kaljurand
# Version: 2013-06-25
#
# Example:
#   $ echo "hallo" | python make_gf_parse_lin_command.py --lang=Ger --cat=Phrase
#   p -lang=Ger -cat=Phrase "hallo" | l -treebank

import sys
import argparse
import re

pattern = re.compile(r'\s+')

def process_lines(lang_in, lang_out, cat, linearize_all):
	flag_cat = ""
	flag_linearize_all = ""
	if cat is not None:
		flag_cat = "-cat=" + cat
	if linearize_all:
		flag_linearize_all = "-all"
	for line in sys.stdin:
		serialize_command(rewrite_lang(lang_in), rewrite_lang(lang_out), flag_cat, flag_linearize_all, line.strip())

# TODO: add escaping
def serialize_command(lang_in, lang_out, flag_cat, flag_linearize_all, line):
	cmd = 'p %s %s "%s" | l %s %s -treebank' % (lang_in, flag_cat, line, lang_out, flag_linearize_all)
	print re.sub(pattern, ' ', cmd)

def rewrite_lang(lang):
	if lang is None:
		return ""
	return "-lang=" + lang.replace(' ', ',')


parser = argparse.ArgumentParser(
	description='Makes a GF parse + linearize command',
	epilog="That's all it does."
)

parser.add_argument('-l', '--lang-in',
	type=str, action='store', dest='lang_in',
	help='3-letter language code, e.g. Eng')

parser.add_argument('--lang-out',
	type=str, action='store', dest='lang_out',
	help='3-letter language code (or a sequence of codes), e.g. Ger,Spa')

parser.add_argument('-c', '--cat',
	type=str, action='store', dest='cat',
	help='start category')

parser.add_argument("--all",
	action="store_true", dest="linearize_all", default=False,
	help="linearize all variants")

parser.add_argument('-v', '--version', action='version', version='%(prog)s v0.1')

args = parser.parse_args()

process_lines(args.lang_in, args.lang_out, args.cat, args.linearize_all)
