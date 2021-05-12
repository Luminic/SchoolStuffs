from typing import Any

def is_symmetric(relation: set[tuple[Any, Any]]) -> bool:  
    """
    O(n) time
    """  
    for pair in relation:
        if not (pair[1], pair[0],) in relation:
            return False

    return True

def is_antisymmetric(relation: set[tuple[Any, Any]]) -> bool: 
    """
    Warning: NOT the same as `not is_symmetric(...)`
    O(n) time
    """   
    for pair in relation:
        if (pair[1], pair[0],) in relation:
            return False

    return True

def is_transitive(relation: set[tuple[Any, Any]]) -> bool:
    """
    O(n^2) time
    """
    for pair in relation:
        for pair2 in relation:
            if pair2[0] == pair[1]:
                if not (pair[0], pair2[1],) in relation:
                    return False

    return True

def is_reflexive(relation: set[tuple[Any, Any]], domain: set[Any]) -> bool:
    """
    O(n) time
    """
    for d in domain:
        if not (d, d,) in relation:
            return False

    return True

def is_irreflexive(relation: set[tuple[Any, Any]], domain: set[Any]) -> bool:
    """
    Warning: NOT the same as `not is_reflexive(...)`
    O(n) time
    """
    for d in domain:
        if (d, d,) in relation:
            return False

    return True

def create_transitive_closure(relation: set[tuple[Any, Any]]) -> bool:
    """
    `relation` will be modified (and returned)
    Unknown time complexity
    """
    while 1:
        queue: set[tuple[Any, Any]] = set()

        for pair in relation:
            for pair2 in relation:
                if pair2[0] == pair[1]:
                    transitive_connection = (pair[0], pair2[1],)
                    if not transitive_connection in relation:
                        queue.add(transitive_connection)

        if queue:
            relation.update(queue)
        else:
            return relation
