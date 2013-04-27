GF-Utils
========

Various scripts for interacting with GF tools and services


Requirements
------------

Python.

Some scripts require `curl` on the PATH.

Some scripts require `gf` on the PATH.

Some scripts require a running GF Cloud Service (http://cloud.grammaticalframework.org/).
To start it on localhost, execute (bash):

	$ GF_RESTRICTED=yes gf --server=41297 --document-root `pwd`/document-root

(Required GF version 2012-11-14 or newer.)


Documentation
-------------

Look at the source code.


Examples
--------

Note: The following are `bash` command lines.

### Interacting with the GF Cloud Service

In each case you need to specify the directory on the server.
The directory must exist and must have a name of the form "/grammars" or
"/tmp/dir", where `dir` can be any string [TODO: check].

Upload the MOLTO Phrasebook:

	upload-grammar.py --dir /tmp/dir ${GF_SRC}/examples/phrasebook/

Upload a directory full of PGF files:

	upload-grammar.py --dir /tmp/dir --ext "\.pgf" local_pgf_dir/

Compile it for English and German using `Phrase` as start category.
The start category is optional, if specified then optimized compilation is used.

	make-pgf.py --dir /tmp/dir --cat Phrase --langs Eng,Ger Phrasebook

Check for the currently available PGFs and their languages:

	info.py --dir /tmp/dir

List the compiled modules (i.e. files with the extension '.gfo'):

	download.py --dir /tmp/dir --ext "gfo" --no-act

Download the source files (i.e. files with the extension '.gf'):

	download.py --dir /tmp/dir --ext "gf" --out outdir

Parsing:

	echo "hello" | pgf.py --dir /tmp/dir -g Phrasebook -f PhrasebookEng


### Generating GF-grammars

Interpret the given CSV file as a GF grammar and write it out into a
set of GF files.

	csv_to_grammar.py --file Sheet1.csv --name Geograpy --dir outdir

An example of an input file is the output of

	curl -L https://script.google.com/macros/s/AKfycbyMYJxM_qL7vS45r_NJJQC_4seepJk3faIkiw5zDIC3Lr9cGjE/exec


### Other

List the all the modules that are imported starting from 3 Phrasebook toplevel files,
either directly or indirectly.

	reachable-modules.py ${GF_SRC}/examples/phrasebook/Phrasebook{Eng,Ger,Ita}.gf

	reachable-modules.py --path ../../grammars/acewiki_aceowl:../../lib/src/ace:../../lib/src/api Geography{Ace,Ape,Ger,Spa}.gf


Generate trees by GF's `generate_random`.

	generate.py --depth 6 --number 20 --repeat 10 --cat S --probs funs.probs -g App.pgf


List the 10 least used non-lexical functions in the given tree set:

	cat lin.txt | grep "TestAttempto: " | sed "s/.*: //" |\
	python coverage.py -g Simple.pgf |\
	grep "^c" | sort -n -k3 | cut -f2,3 | head -5

	Trees: 73
	Simple functions: 37
	Complex function coverage: 62/98
	a2VP	0
	a2VPQ	0
	andRS	0
	consText	0
	ConsVPS	0
