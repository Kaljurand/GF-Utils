g=${ACE_IN_GF}/Words300.pgf
#probs=${ACE_IN_GF}/probs/combined.probs
probs=${ACE_IN_GF}/probs/empty.probs
out=out

funs=${out}/funs.pl
ptrees=${out}/ptrees.txt
trees=${out}/trees.txt
coverage=${out}/coverage.txt
lincmd=${out}/lincmd.txt
lin=${out}/lin.txt

number=1

# 4, 6
depth=2

repeat=1

# TODO:
# increase coverage
# decrease length (measure it with the coverage script)
# decrease repetition

mkdir -p ${out}

echo "pg -funs" | gf --run ${g} | convert_funs.py > ${funs}
swipl -g "['${funs}'], [fun_path], fun(Fun, [_|_], _), once(fun_to_tree(Fun, 'Sentence', T)), format_in_gf(T), nl, fail ; true." -t halt -f none > ${ptrees}
swipl -g "['${funs}'], [fun_path], fun(Fun, [_|_], _), once(fun_to_tree(Fun, 'Question', T)), format_in_gf(T), nl, fail ; true." -t halt -f none >> ${ptrees}
cat ${ptrees} | generate.py --depth ${depth} --number ${number} --repeat ${repeat} --probs ${probs} -g ${g} > ${trees}
cat ${trees} | coverage.py -g ${g} > ${coverage}
cat ${trees} | grep "(" | sed "s/^/l -treebank /" > ${lincmd}
cat ${lincmd} | gf --run ${g} > ${lin}
cat ${lin} | grep "Ace: "
