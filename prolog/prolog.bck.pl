:- discontiguous vertebra/2.

vertebra(B, l5) :-
    ((is_pelvic(A),
    is_vertebra(B),
    is_closest(A, B))
    ;
    dhash_vertebra(B, l5)).

vertebra(B, l4) :-
    (
        (
        is_vertebra(A),
        is_vertebra(B),
        is_adjacent(A, B),
        (vertebra(A, l5), higher(B, A))
        )
    ;
    dhash_vertebra(B, l4)
    ).

vertebra(B, l3) :-
    ((is_vertebra(A),
    is_vertebra(B),
    is_adjacent(A, B),
    vertebra(A, l4),
    higher(B, A))
    ;
    dhash_vertebra(B, l3)).

vertebra(B, l2) :-
    ((is_vertebra(A),
    is_vertebra(B),
    is_adjacent(A, B),
    vertebra(A, l3),
    higher(B, A))
    ;
    dhash_vertebra(B, l2)).

is_sternum(A) :-
    is_vertebra(A),
    is_rib(B),
    is_closest(B, A).

l1_condition_1(B) :-
    is_vertebra(A),
    is_adjacent(A, B),
    vertebra(A, l2),
    higher(B, A).

l1_condition_2(B) :-
    is_vertebra(A),
    is_adjacent(A, B),
    is_sternum(A),
    \+ is_sternum(B).

vertebra(B, l1) :-
    (is_vertebra(B),
    (l1_condition_1(B) ; l1_condition_2(B)))
    ;
    dhash_vertebra(B, l1).

vertebra(B, t12) :-
    is_vertebra(A),
    is_vertebra(B),
    is_adjacent(A, B),
    vertebra(A, l1),
    higher(B, A).

vertebra(B, t11) :-
    is_vertebra(A),
    is_vertebra(B),
    is_adjacent(A, B),
    vertebra(A, t12),
    higher(B, A).

vertebra(B, t10) :-
    is_vertebra(A),
    is_vertebra(B),
    is_adjacent(A, B),
    vertebra(A, t11),
    higher(B, A).

vertebra(B, t9) :-
    is_vertebra(A),
    is_vertebra(B),
    is_adjacent(A, B),
    vertebra(A, t10),
    higher(B, A).

