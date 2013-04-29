# TODO: make it a Makefile

# Location of ACE-in-GF
g=${ACE_IN_GF}/Words300.pgf
probs=${ACE_IN_GF}/probs/Words300.probs

# Locations of various outputs
out=out
funs=${out}/funs.pl
ptrees=${out}/ptrees.txt
trees=${out}/trees.txt
coverage_ptrees=${out}/coverage_ptrees.txt
coverage_trees=${out}/coverage_trees.txt
coverage_trees_sorted=${out}/coverage_trees_sorted.txt
coverage_ptrees_info=${out}/coverage_ptrees_info.txt
coverage_trees_info=${out}/coverage_trees_info.txt
lincmd=${out}/lincmd.txt
lin=${out}/lin.txt
lin_lang=${out}/lin_lang.txt

# Generation parameters
lang=Ace

# The best depth-parameter is difficult to estimate
# low depth: runs slower (timeout can take effect), smaller coverage (might be because of timeout),
#  smaller size, linearization is faster
# A high depth will not increase coverage because we start
# out with sufficiently deep partial trees so we get good coverage also at lower depths.
#
# Some reference results specific to a specific version of ACE-in-GF.
# Note that the coverage on partial trees is 82.
# 2: 17/54 (avg. tree size vs coverage)
# 3: 23/71 -> 17/74
# 4: 28/77
# 5: 36/77
# 6: 43/79
# 7: 51/79 (linearization took forever)
depth=3

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

echo "Generating partial trees up to category Sentence"
swipl -g "['${funs}'], [fun_path], fun(Fun, [_|_], _), once(fun_to_tree(Fun, 'Sentence', T)), format_in_gf(T), nl, fail ; true." -t halt -f none > ${ptrees}

echo "Generating partial trees up to category Question"
swipl -g "['${funs}'], [fun_path], fun(Fun, [_|_], _), once(fun_to_tree(Fun, 'Question', T)), format_in_gf(T), nl, fail ; true." -t halt -f none >> ${ptrees}

echo "Filling in partial trees"
cat ${ptrees} | generate.py --lang=${lang} --depth ${depth} --number ${number} --repeat ${repeat} --timeout=${timeout} --probs ${probs} -g ${g} > ${trees}

echo "Making a GF linearize-command"
cat ${trees} | grep "(" | sed "s/^/l -treebank /" > ${lincmd}

echo "Coverage of partial and final trees"
cat ${ptrees} | coverage.py -g ${g} > ${coverage_ptrees} 2> ${coverage_ptrees_info}
cat ${trees} | coverage.py -g ${g} > ${coverage_trees} 2> ${coverage_trees_info}
cat ${coverage_ptrees_info} ${coverage_trees_info}

cat ${coverage_trees} | sort -nr -k3 > ${coverage_trees_sorted}

echo "Linearizing"
cat ${lincmd} | gf --run ${g} > ${lin}

echo "Extracting ACE-linearizations"
cat ${lin} | grep "${lang}: " > ${lin_lang}
