#! /usr/bin/env python

# Downloads files with the given extension from the GF Cloud
# and saves them into the given directory.
# Optionally just lists these files without downloading/saving.
#
# Author: Kaarel Kaljurand
# Version: 2012-10-31
#
import sys
import argparse
import json
import os
import urllib
import urllib2


def get_file_paths(query):
	"""
	Returns the list of file paths that the HTTP query returns
	"""
	req = urllib2.Request(query)
	try:
		res = urllib2.urlopen(req)
		jsonAsStr = res.read()
		return json.loads(jsonAsStr)
	except Exception, e:
		print >> sys.stderr, e


def make_query(params):
	"""
	Returns the query string that contains the given parameters
	"""
	return args.server + "/cloud?" + urllib.urlencode(params)


def download_and_save(f, out):
	"""
	Downloads the given file and saves it into the given directory.
	The directory must exist and be writable.
	"""
	try:
		lineAsArg = urllib.urlencode({ 'file' : f })
		req = urllib2.Request(query_dl + "&" + lineAsArg)
		content = urllib2.urlopen(req).read()
		path = os.path.join(out, f)
		output = open(path, "w")
		output.write(content)
		output.close()
	except Exception, e:
		print >> sys.stderr, e


parser = argparse.ArgumentParser(description='Download files with the given extension')

parser.add_argument('-s', '--server', type=str, action='store', dest='server',
	default='http://localhost:41296',
	help='name of the GF cloud service, default=http://localhost:41296')

parser.add_argument('-d', '--dir', type=str, action='store',
	default='/grammars/',
	dest='dir',
	help='directory on the server where files are stored, default=/grammars/')

parser.add_argument('-o', '--out', type=str, action='store',
	default='.',
	dest='out',
	help='local directory into which the files are saved, default=.')

parser.add_argument('-e', '--ext', type=str, action='store',
	default='.gf',
	dest='ext',
	help='extension of files that will be downloaded, default=gf')

parser.add_argument('-n', '--no-act', action='store_true',
	default=False,
	dest='noact',
	help='just list the files but do not download them, default=False')

parser.add_argument('-v', '--version', action='version', version='%(prog)s v0.1')

args = parser.parse_args()

# The extension can optionally start with a dot
if not args.ext.startswith('.'):
	args.ext = '.' + args.ext

query_ls = make_query({ 'dir' : args.dir, 'command' : 'ls', 'ext' : args.ext })
query_dl = make_query({ 'dir' : args.dir, 'command' : 'download' })

file_paths = get_file_paths(query_ls)

if file_paths is None or len(file_paths) == 0:
	print >> sys.stderr, '{:}'.format("No matching files")
	exit()

count = 0
for f in get_file_paths(query_ls):
	count = count + 1
	print >> sys.stderr, '{:} {:}'.format(count, f)
	if not args.noact:
		download_and_save(f, args.out)
