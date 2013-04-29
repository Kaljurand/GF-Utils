% Assumes fun/3, consumer/3
%
% Example:
%
% Generate a single tree for each non-lexical function in the grammar.
%
% fun(Fun, [_|_], _), once(fun_to_tree(Fun, 'Text', T)), format_in_gf(T).

%% fun_to_tree(Fun, StartCat, Tree) is nondet.
%
%
fun_to_tree(Fun, StartCat, Tree) :-
	fun(Fun, Args, Cat),
	path(Cat, StartCat, [Fun], Path),
	same_length(Args, Args1),
	path_to_tree(Path, t(Fun, Args1), Tree).


%% path(?Fun, +StartCat, ?Path) is nondet.
%
% Generates a path upwards from the given function to
% the given category.
%
% TODO:
% Optimize for the least number of total arguments, e.g.
% greedily choose functions with least number of arguments.
%
% TODO: add MaxLen input to limit the length of the Path
%
path(Fun, StartCat, Path) :-
	fun(Fun, _Args, Cat),
	path(Cat, StartCat, [Fun], Path).


path(StartCat, StartCat, _Seen, []) :-
	!.

% There exists Fun1 which can embed a fun of category Cat
% at argument position Index
path(Cat, StartCat, Seen, [Fun1-Index | Path]) :-
	select_fun(Cat, Seen, Fun1, Index),
	fun(Fun1, _Args, Cat1),
	path(Cat1, StartCat, [Fun1 | Seen], Path).


%% select_fun(Cat, Seen, Fun, Index) is nondet
%
% Select a function that consumes the given category.
% Preference is given to functions which consume the
% category at a low argument position. In case of several
% functions that match, choose one randomly.
%
% TODO: current version prefers low indexes,
% rather: prefer low number of arguments
%
% TODO: magic number 4
%
select_fun(Cat, Seen, Fun, Index) :-
	between(0, 4, Index),
	findall(F, good_consumer(Cat, Seen, F, Index), Funs),
	random_permutation(Funs, FunsInRandomOrder),
	member(Fun, FunsInRandomOrder).

/*
select_fun(Cat, Seen, Fun, Index) :-
	good_consumer(Cat, Seen, Fun, Index).
*/

% path must contain unique funs
good_consumer(Cat, Seen, Fun, Index) :-
	consumer(Cat, Fun, Index),
	\+ bad_fun(Fun),
	\+ member(Fun, Seen).


%% path_to_tree(+Path, -Tree) is det.
%
% Trace the path from top-to-bottom and build its corresponding tree.
% The tree has open nodes.
%
path_to_tree(Path, Bottom, Tree) :-
	reverse(Path, PathRev),
	path_to_tree_aux(PathRev, Bottom, Tree).

path_to_tree_aux([], Bottom, Bottom).

path_to_tree_aux([Fun-Index | Tail], Bottom, t(Fun, Args1)) :-
	fun(Fun, Args, _),
	same_length(Args, Args1),
	nth0(Index, Args1, TailTree),
	path_to_tree_aux(Tail, Bottom, TailTree).


%% format_in_gf(+Tree) is det.
%
% Serializes the given Tree in the GF tree format, i.e.
%
% t(Name, Args) -> (Name Args) with variables replaced by ?
%
format_in_gf(Var) :-
	var(Var),
	!,
	format("? ").

format_in_gf(t(Name, [])) :-
	!,
	format("~w ", [Name]).

format_in_gf(t(Name, Args)) :-
	format("(~w ", [Name]),
	maplist(format_in_gf, Args),
	format(") ", [Name]).


%% bad_fun(?Fun) is nondet.
%
% Lists functions to be ignored
% TODO: make this configurable
%
bad_fun(bad_fun).
bad_fun(falseS).
bad_fun(orRS).
bad_fun(andRS).
