#
# Shows the differences in two PGF files (using a general purpose diff)
#
diff=vimdiff
gf="gf --run"

if [ $# -ne 2 ]
then
	echo "Usage: bash diff-pgf.bash <pgf1> <pgf2>"
	exit
fi

pgf1=$1
pgf2=$2

$diff <(echo "pg" | $gf $pgf1) <(echo "pg" | $gf $pgf2)
