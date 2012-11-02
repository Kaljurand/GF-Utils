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

	GF_RESTRICTED=yes gf -server

(Required GF version 2012-10-23 or later.)


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

	python upload-grammar.py --dir /tmp/dir ${GF_SRC}/examples/phrasebook/

Compile it for English and German:

	python make-pgf.py --dir /tmp/dir --langs Eng,Ger Phrasebook

Check for the currently available PGFs and their languages:

	python info.py --dir /tmp/dir

List the compiled modules (i.e. files with the extension '.gfo'):

	python download.py --dir /tmp/dir --ext "gfo" --no-act

Download the source files (i.e. files with the extension '.gf'):

	python download.py --dir /tmp/dir --ext "gf" --out outdir

Parsing:

	echo "hello" | python pgf.py --dir /tmp/dir -g Phrasebook -f PhrasebookEng


# Other

List the all the modules that are imported starting from 3 Phrasebook toplevel files,
either directly or indirectly.

	python reachable-modules.py ${GF_SRC}/examples/phrasebook/Phrasebook{Eng,Ger,Ita}.gf
