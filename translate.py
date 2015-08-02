#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Translates from source language to target language, e.g.
#
#     cat in.txt | translate.py --pgf Translate2.pgf --tokenize --source TranslateEng --target TranslateEst > out.tsv
#
# or linearizes existing trees, e.g.
#
#     cat gold.tsv | translate.py --pgf Translate2.pgf --source TranslateEng --target TranslateEst --type=gold > out.tsv
#
# where gold.tsv and out.tsv are in the same 4-column format:
#
#     source string, target string, probability of parsing source (-1 if no parse), parse tree of source string
#
# If n-best > 1 then multiple parse trees / translations can result, output on separate lines.
#
# For the PGF API see: http://www.grammaticalframework.org/doc/python-api.html
#
# @author Kaarel Kaljurand
# @version 2015-07-29

from __future__ import division, unicode_literals, print_function
import sys
import re
import argparse
import pgf
from collections import *

def get_args():
    p = argparse.ArgumentParser(description='')
    p.add_argument('--pgf', type=str, action='store', dest='pgf', required=True, help='grammar in PGF format')
    p.add_argument('-s', '--source', type=str, action='store', dest='source', required=True, help='source language')
    p.add_argument('-t', '--target', type=str, action='store', dest='target', required=True, help='target language')
    p.add_argument('--type', type=str, action='store', default='plain', help='input type, one of {plain (default), gold}. plain = strings to be translated, one per line; gold = 4-column format that is generated by this program, in this case only trees are linearized')
    p.add_argument('--cat', type=str, action='store', help='start category for parsing')
    p.add_argument('--n-best', type=int, action='store', dest='n_best', default=1, help='number of parses to be generated')
    p.add_argument('--tokenize', action='store_true', help='tokenize input string (only if type=plain)')
    p.add_argument('-v', '--version', action='version', version='%(prog)s v0.2.0')
    return p.parse_args()

def print_utf8(s, file=sys.stdout):
    print(s.encode('utf8'), file=file)

def lowercase_first(s):
    if s == '' or s[0:4] == 'John' or s[0:4] == 'Mary':
        return s
    return s[:1].lower() + s[1:]

def tokenize(s):
    s1 = lowercase_first(s)
    s2 = re.sub('([.,!?])', r' \1 ', s1)
    return s2

def gen_translations(args, lang_source, lang_target, line):
    if args.type == 'gold':
        fields = line.split('\t')
        if fields[2] == '-1':
            yield fields[0],fields[1],fields[2],fields[3]
        else:
            tree = pgf.readExpr(fields[3])
            utt_target = lang_target.linearize(tree).decode('utf8')
            yield fields[0],utt_target,fields[2],fields[3]
    else:
        if args.tokenize:
            utt_source = tokenize(line)
        else:
            utt_source = line
        if args.cat:
            for prob,tree in lang_source.parse(utt_source, n=args.n_best, cat=args.cat):
                utt_target = lang_target.linearize(tree).decode('utf8')
                yield utt_source,utt_target,prob,tree
        else:
            for prob,tree in lang_source.parse(utt_source, n=args.n_best):
                utt_target = lang_target.linearize(tree).decode('utf8')
                yield utt_source,utt_target,prob,tree

def main():
    args = get_args()
    gr = pgf.readPGF(args.pgf)
    try:
        lang_source = gr.languages[args.source]
        lang_target = gr.languages[args.target]
    except KeyError as e:
        print_utf8('Error: no such language: {0}'.format(e), file=sys.stderr)
        exit(1)
    for raw_line in sys.stdin:
        line = raw_line.decode('utf8').strip()
        try:
            for utt_source,utt_target,prob,tree in gen_translations(args, lang_source, lang_target, line):
                print_utf8("{0}\t{1}\t{2}\t{3}".format(utt_source, utt_target, prob, tree))
        except pgf.ParseError as e:
            print_utf8('{0}\t{1}\t{2}\t{3}'.format(line, '', -1, e))

if __name__ == "__main__":
    main()
