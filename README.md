GF-Utils
========

Various scripts for interacting with GF tools and services


Requirements
------------

Python.

Some scripts require `curl`.

Some scripts require a running GF Cloud Service (http://cloud.grammaticalframework.org/).
To start it on localhost, execute (bash):

	GF_RESTRICTED=yes gf -server

(Required GF version 2012-10-23 or later.)


Documentation
-------------

Look at the source code.


Examples of interacting with the GF Cloud Service
-------------------------------------------------

Upload the MOLTO Phrasebook:

	python upload-grammar.py --dir /tmp/gfse.123 ${GF_SRC}/examples/phrasebook/

Compile it for English and German:

	python make-pgf.py --dir /tmp/gfse.123 --langs Eng,Ger Phrasebook

Check for the currently available PGFs and their languages:

	python info.py --dir /tmp/gfse.123

Parsing:

	echo "hello" | python pgf.py --dir /tmp/gfse.123 -g Phrasebook -f PhrasebookEng
