import math

def permutations(n:int) -> float:
    """
    Equivalent to `n!`

    The number of ways a set of n elements can be arranged (ordered)
    """
    return math.factorial(n)

def r_combinations(n:int, r:int) -> float:
    """
    r-combinations of n elements aka `n! / (n-r)!`.

    The number of ways to choose a set of r elements from a set of n elements
    without repetition but order does matter.

    This function optimizes the calculation a bit to avoid calculating the full n!.
    It might be a little slower for small n but will be significantly faster for large n.
    """
    res = 1
    for i in range((n-r)+1, n+1):
        res *= i
    return res

def choose(n:int, r:int) -> float:
    """
    `n choose r` aka `n! / (r!(n-r)!)`.

    The number of ways to choose a set of r elements from a set of n elements
    without repetition and if order doesn't matter.

    This function optimizes the calculation a bit to avoid calculating the full n!.
    It might be a little slower for small n but will be significantly faster for large n.
    """
    res = 1
    r = max(r, n-r)
    for i in range(r+1, n+1):
        res *= i
    res //= math.factorial(n-r)
    return res


def r_combinations_fac(n:int, r:int) -> float:
    """
    Same as `r_combinations(...)` but without the optimizations
    """
    return math.factorial(n) // math.factorial(n-r)

def choose_fac(n:int, r:int) -> float:
    """
    Same as `choose(...)` but without the optimizations
    """
    return math.factorial(n) // (math.factorial(r) * math.factorial(n-r))


def probability_exactly_m_of_n_events(n:int, m:int, prob_T:float) -> float:
    """
    Given `n` events that can be either True or False, this function gives the
    probability there will be exactly `m` True events.
    """
    return prob_T**m * (1-prob_T)**(n-m) * choose(n, m)

def probability_at_least_m_of_n_events(n:int, m:int, prob_T:float) -> float:
    """
    Given `n` events that can be either True or False, this function gives the
    probability there will be at least `m` A events.
    """
    total = 0
    for exact in range(m, n+1):
        total += probability_exactly_m_of_n_events(n, exact, prob_T)
    return total

def probability_table_for_n_events(n:int, prob_T:float) -> list[float]:
    """
    Given `n` events that can be either True or False, this function returns a list
    where the probability there will be exactly `i` True events is `returned_list[i]`
    """
    res = []
    for m in range(n+1):
        res.append(probability_exactly_m_of_n_events(n, m, prob_T))
    return res


def expected_value_of_a_die(sides:int=6)->float:
    return sides*(sides+1)/2 /sides