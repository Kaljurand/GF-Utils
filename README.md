GF-Utils
========

Various scripts for interacting with GF tools and services


Requirements
------------

Various scripts have various requirements but all are listed below.

Python.

GHC.

Some scripts require one or more of the following on the PATH:

  - `curl`
  - `gf`
  - `swipl`

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


### Analyzing GF-grammars

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

Bottom-up generation of tree queries. First step: convert the function definitions into a Prolog-based format.
Second step: for each non-lexical function map it to a single tree (there can be more but the others are not generated
by `once/1`), such that:

  - the tree embeds the function,
  - the tree corresponds to the category 'Sentence',
  - all arguments in the tree are unspecified ('?').

	echo "pg -funs" | gf --run Grammar.pgf | convert_funs.py > funs.pl
	swipl -g "[funs], [fun_path], fun(Fun, [_|_], _), once(fun_to_tree(Fun, 'Sentence', T)), format_in_gf(T), nl, fail ; true." -t halt -f none

#### Analyzing ambiguity

Roundtripper highlights some forms of ambiguity present in the grammar by linearizing the
given trees and then parsing the obtained linearizations.

  1. compile [Roundtripper.hs](Roundtripper.hs) using `make Roundtripper`
  2. generate some trees using the methods described above
  3. run Roundtripper and analyze the results

Here is an example that lists the most ambiguous languages in the MOLTO Phrasebook.

	cat trees.txt | ./Roundtripper -f Phrasebook.pgf -l DisambPhrasebookEng > out.txt
	cat out.txt | grep DIFF | cut -f2 | sort | uniq -c | sort -nr
	    566 PhrasebookUrd
	    467 PhrasebookTha
	    427 PhrasebookHin
	    381 PhrasebookPes
	    360 PhrasebookEng
	    322 PhrasebookRus
	    249 PhrasebookSwe
	    ...

For more documentation see the source of [Roundtripper.hs](Roundtripper.hs).
