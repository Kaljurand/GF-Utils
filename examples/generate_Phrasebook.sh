# TODO: make it a Makefile

# Location of Phrasebook.pgf
g=${PHRASEBOOK}/Phrasebook.pgf
probs=/dev/null

# Locations of various outputs
out=out
funs=${out}/funs.pl
ptrees=${out}/ptrees.txt
trees=${out}/trees.txt
coverage_ptrees=${out}/coverage_ptrees.txt
coverage_trees=${out}/coverage_trees.txt
lincmd=${out}/lincmd.txt
lin=${out}/lin.txt
lin_lang=${out}/lin_lang.txt

# Generation parameters
lang=DisambPhrasebookEng

# The best depth-parameter is difficult to estimate
# low depth: runs slower (timeout can take effect), smaller coverage (might be because of timeout),
#  smaller size, linearization is faster
# A high depth will not increase coverage because we start
# out with sufficiently deep partial trees so we get good coverage also at lower depths.
# 5: 8/133 (/137/154)
# 6: 9/133 (/137/154)
depth=5

# How many trees to generate
number=1

# How many times to repeat generation
# Values higher than 1 might makse sense is timeout is used.
repeat=1

# Timeout in seconds
timeout=2

mkdir -p ${out}

echo "Making the list of function definitions"
echo "pg -funs" | gf --run ${g} | convert_funs.py > ${funs}

echo "Generating partial trees up to category Phrase"
swipl -g "['${funs}'], [fun_path], fun(Fun, [_|_], _), once(fun_to_tree(Fun, 'Phrase', T)), format_in_gf(T), nl, fail ; true." -t halt -f none > ${ptrees}

echo "Filling in partial trees"
cat ${ptrees} | generate.py --lang=${lang} --depth ${depth} --number ${number} --repeat ${repeat} --timeout=${timeout} --probs ${probs} -g ${g} > ${trees}

echo "Making a GF linearize-command"
cat ${trees} | grep "(" | sed "s/^/l -treebank /" > ${lincmd}

echo "Coverage of partial trees"
cat ${ptrees} | coverage.py -g ${g} > ${coverage_ptrees}

echo "Coverage of final trees"
cat ${trees} | coverage.py -g ${g} > ${coverage_trees}

echo "Linearizing"
cat ${lincmd} | gf --run ${g} > ${lin}

echo "Extracting lang-linearizations"
cat ${lin} | grep "${lang}: " > ${lin_lang}
