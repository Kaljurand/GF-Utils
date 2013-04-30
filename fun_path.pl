% Assumes fun/3, consumer/3
%
% TODO:
%  - cleanup generic tree exclusion
%
% Example:
%
% Generate a single tree for each non-lexical function in the grammar.
%
% fun(Fun, [_|_], _), once(fun_to_tree(Fun, 'Text', T)), format_in_gf(T).

find_filter_and_format_trees(N, Cat) :-
	findall_trees(N, Cat, Trees),
	exclude_generic_trees(Trees, SpecificTrees),
	format_trees(SpecificTrees).


format_trees(Trees) :-
	maplist(format_in_gf(nl), Trees).


findall_trees(N, Cat, Trees) :-
	findall(
		T,
		(
			fun(Fun, [_|_], _),
			call_n_times(N, fun_to_tree(Fun, Cat, T))
		),
		Trees
	).


% TODO: slow
exclude_generic_trees(Trees, SpecificTrees) :-
	exclude(is_generic_tree(Trees), Trees, SpecificTrees).

is_generic_tree(Trees, Generic) :-
	member(Specific, Trees),
	\+ subsumes_term(Specific, Generic),
	subsumes_term(Generic, Specific),
	!.


%% call_n_times(+N:integer, +Goal)
call_n_times(N, Goal) :-
	nb_setval(counter, 0),
	call(Goal),
	inc_counter(counter, NewValue),
	(
		NewValue =< N
	->
		true
	;
		!, fail
	).

inc_counter(Name, ValueNew) :-
	nb_getval(Name, Value),
	ValueNew is Value + 1,
	nb_setval(Name, ValueNew).


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
	select_fun(Cat, Seen, Fun1, Index, _),
	fun(Fun1, _Args, Cat1),
	path(Cat1, StartCat, [Fun1 | Seen], Path).


%% select_fun(Cat, Seen, Fun, Index, Key) is nondet.
%
% Select a function that consumes the given category.
%
select_fun(Cat, Seen, Fun, Index, Key) :-
	findall(f(F, I), good_consumer(Cat, Seen, F, I), Funs),
	maplist(assign_key, Funs, FunsWithKeys),
	keysort(FunsWithKeys, FunsWithKeysSorted),
	member(Key-f(Fun, Index), FunsWithKeysSorted).


% path must contain unique funs
good_consumer(Cat, Seen, Fun, Index) :-
	consumer(Cat, Fun, Index),
	\+ bad_fun(Fun),
	\+ member(Fun, Seen).


%% assign_key(Term, Key-Term) is det.
%
% Assign a sort key to the function.
% The sort key prefers functions that have few arguments,
% breaking ties by the position of the category (to more left the better),
% breaking ties randomly.
%
% TODO: remove hack: functions with long names are penalized
% TODO: magic numbers 10^n
assign_key(f(Fun, Index), Key-f(Fun, Index)) :-
	fun(Fun, Args, _),
	length(Args, Len),
	atom_length(Fun, NameLen),
	random(1, 100, Random),
	Key is (Len * 100000000) + (Index * 1000000) + (NameLen * 1000) + Random.


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
format_in_gf(Goal, Tree) :-
	format_in_gf(Tree),
	call(Goal).


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
/*
bad_fun(falseS).
bad_fun(orRS).
bad_fun(andRS).
*/
bad_fun(for_everyS).
bad_fun('ConsVPS').
bad_fun('ConsVPSQ').
bad_fun('BaseVPS').
bad_fun('BaseVPSQ').
