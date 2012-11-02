#! /usr/bin/env python

# Uploads GF grammar modules to the GF cloud.
# Note that there can be multiple source directories, however,
# all the files are copied to a single directory
# on the server so make sure that no filenames clash.

# Author: Kaarel Kaljurand
# Version: 2012-10-25
#
# Examples:
#
# python upload-grammar.py --dir /tmp/dir g1 g2
#
import sys
import argparse
import os
import subprocess
import re

curl='curl'
# We want to upload only gf files.
ext_pattern='^\.gf$'
# In some cases precompiled gfo-files would also make sense,
# i.e. TODO: make ext_pattern part of the commandline.
#ext_pattern='^\.(gf|gfo)$'

def gf_file_generator(src_dirs, includes):
	"""
	Generates relative pathnames that correspond to
	files with the extension $ext_pattern in the given directories.
	"""
	for top in src_dirs:
		for root, dirs, files in os.walk(top, topdown=False, followlinks=False):
			for name in files:
				path = os.path.join(root, name)
				basename, extension = os.path.splitext(path)
				if re.match(ext_pattern, extension):
					if includes is None:
						yield [root, name]
					elif name in includes:
						yield [root, name]


def upload_files(dir, files):
	for [root, name] in files:
		print '{:} {:}'.format(name, root)
		upload(dir, root, name)


def upload(dir, root, name):
	"""
	Uploads the given files using Curl
	"""
	path = os.path.join(root, name)
	cmd = [curl,
		'-d', "dir=" + dir,
		'-d', 'command=upload',
		'--data-urlencode', name + "@" + path,
		args.server + "/cloud"]
	#print >> sys.stderr, ' '.join(cmd)
	subprocess.call(cmd)


# Commandline arguments parsing
parser = argparse.ArgumentParser(description='Uploads GF files to the GF cloud')

parser.add_argument('src_dirs', metavar='SRC', type=str, nargs='+',
	help='local directories to be copied to the server')

parser.add_argument('--includes', type=str, action='store', dest='includes',
	help='every uploaded file must be in this list (if specified) by its local name')

parser.add_argument('-d', '--dir', type=str, action='store', dest='dir',
	help='GF webservice directory (OBLIGATORY)')

parser.add_argument('-s', '--server', type=str, action='store', dest='server',
	default='http://localhost:41296',
	help='name of the GF cloud service, default=http://localhost:41296')

parser.add_argument('-v', '--version', action='version', version='%(prog)s v0.1')

args = parser.parse_args()

if args.dir is None:
	print >> sys.stderr, 'ERROR: argument -d/--dir is not specified'
	print >> sys.stderr, 'You can generate a new directory on the server by: curl ' + args.server + '/new'
	exit()

includes = None
if args.includes is not None:
	with open(args.includes) as f:
		includes = f.read().splitlines()

g = gf_file_generator(args.src_dirs, includes)
upload_files(args.dir, g)
