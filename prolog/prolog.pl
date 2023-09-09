:- discontiguous vertebra/2.
:- discontiguous vertebra_from_top/2.

vertebra(B, l5) :-
    ((is_pelvic(A),
    is_vertebra(B),
    is_closest(A, B))
    ;
    dhash_vertebra(B, l5)
    ;
    from_detail(B, l5)
    ).

vertebra_from_top(B, l5) :-
    (
        (
        is_vertebra(A),
        is_vertebra(B),
        is_adjacent(A, B),
        ((vertebra(A, l4); vertebra_from_top(A, l4)), lower(B, A))
        )
    ;
    dhash_vertebra(B, l5)
    ;
    from_detail(B, l5)
    ).

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

vertebra_from_top(B, l4) :-
    (
        (
        is_vertebra(A),
        is_vertebra(B),
        is_adjacent(A, B),
        ((vertebra(A, l3); vertebra_from_top(A, l3)), lower(B, A))
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

vertebra_from_top(B, l3) :-
    (
        (
        is_vertebra(A),
        is_vertebra(B),
        is_adjacent(A, B),
        ((vertebra(A, l2); vertebra_from_top(A, l2)), lower(B, A))
        )
    ;
    dhash_vertebra(B, l3)
    ).

vertebra(B, l2) :-
    ((is_vertebra(A),
    is_vertebra(B),
    is_adjacent(A, B),
    vertebra(A, l3),
    higher(B, A))
    ;
    dhash_vertebra(B, l2)).

vertebra_from_top(B, l2) :-
    (
        (
        is_vertebra(A),
        is_vertebra(B),
        is_adjacent(A, B),
        ((vertebra(A, l1); vertebra_from_top(A, l1)), lower(B, A))
        )
    ;
    dhash_vertebra(B, l2)
    ).

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
    \+ is_sternum(B),
    lower(B, A).

prior_l1(B, l1) :-
    is_artifact(A),
    is_closest(A, B),
    close_artifact(A, l1).

vertebra(B, l1) :-
    prior_l1(B, l1)
    ;
    (is_vertebra(B),
    (l1_condition_1(B) ; l1_condition_2(B)))
    ;
    dhash_vertebra(B, l1)
    ;
    from_detail(B, l1).

vertebra_from_top(B, l1) :-
    prior_l1(B, l1),
    (
        (
        is_vertebra(A),
        is_vertebra(B),
        is_adjacent(A, B),
        ((vertebra(A, t12); vertebra_from_top(A, t12)), lower(B, A))
        )
    ;
    dhash_vertebra(B, l1)
    ;
    from_detail(B, l1)
    ).

vertebra(B, t12) :-
    (
    is_vertebra(A),
    is_vertebra(B),
    is_adjacent(A, B),
    vertebra(A, l1),
    higher(B, A)
    )
    ;
    from_detail(B, t12).

vertebra_from_top(B, t12) :-
    (
        (
        is_vertebra(A),
        is_vertebra(B),
        is_adjacent(A, B),
        ((vertebra(A, t11); vertebra_from_top(A, t11)), lower(B, A))
        )
    ;
    dhash_vertebra(B, t12)
    ;
    from_detail(B, t12)
    ).

vertebra(B, t11) :-
    is_vertebra(A),
    is_vertebra(B),
    is_adjacent(A, B),
    vertebra(A, t12),
    higher(B, A).

vertebra_from_top(B, t11) :-
    (
        (
        is_vertebra(A),
        is_vertebra(B),
        is_adjacent(A, B),
        ((vertebra(A, t10); vertebra_from_top(A, t10)), lower(B, A))
        )
    ;
    dhash_vertebra(B, t11)
    ).

vertebra(B, t10) :-
    is_vertebra(A),
    is_vertebra(B),
    is_adjacent(A, B),
    vertebra(A, t11),
    higher(B, A).

vertebra_from_top(B, t10) :-
    (
        (
        is_vertebra(A),
        is_vertebra(B),
        is_adjacent(A, B),
        ((vertebra(A, t9); vertebra_from_top(A, t9)), lower(B, A))
        )
    ;
    dhash_vertebra(B, t10)
    ).

vertebra(B, t9) :-
    is_vertebra(A),
    is_vertebra(B),
    is_adjacent(A, B),
    vertebra(A, t10),
    higher(B, A).

vertebra_from_top(B,t9) :-
    (
        (
        is_vertebra(A),
        is_vertebra(B),
        is_adjacent(A, B),
        ((vertebra(A, t8); vertebra_from_top(A, t8)), lower(B, A))
        )
    ;
    dhash_vertebra(B, t9)
    ).
