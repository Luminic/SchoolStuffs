import string
import lsymbols

def operate(lhs, rhs, operator):
    # print("operate", lhs, rhs, operator)
    res = []
    assert len(lhs) == len(rhs), "lhs & rhs must have the same size"
    for i in range(len(lhs)):
        if operator == lsymbols.OR:
            res.append(lhs[i] or rhs[i])
        elif operator == lsymbols.AND:
            res.append(lhs[i] and rhs[i])
        elif operator == lsymbols.COND:
            if lhs[i]:
                res.append(rhs[i])
            else:
                res.append(True)
        elif operator == lsymbols.BICOND:
            res.append(lhs[i] == rhs[i])
        elif operator == lsymbols.XOR:
            res.append(lhs[i] != rhs[i])
        elif operator == lsymbols.NAND:
            res.append(not (lhs[i] and rhs[i]))
        elif operator == lsymbols.NOR:
            res.append(not (lhs[i] or rhs[i]))
        else:
            raise NotImplementedError
    return res

def n_to_b(n):
    if n == '0' or n == 0: return False
    elif n == '1' or n == 1: return True
    else: raise ValueError

def b_to_n(b):
    if b: return '1'
    else: return '0'

def bitwise_evaluate(eq, pretty_return=True):
    lhs = []
    rhs = []
    operator = None
    modifier = None
    i = -1
    while i < len(eq) - 1:
        i += 1

        symbol = eq[i]
        # print(i, symbol)
        if symbol in string.whitespace:
            continue

        elif symbol in "([":
            # print("| parens")
            # find corresponding closing parentheses
            depth = 0
            for j in range(i+1, len(eq)):
                if eq[j] in "([":
                    depth += 1
                elif eq[j] in ")]":
                    depth -= 1
                if depth == -1:
                    break
            # print("| |", eq[i+1:j])
            parens = bitwise_evaluate(eq[i+1:j], pretty_return=False)
            if modifier == lsymbols.NOT:
                parens = [not bit for bit in parens]
            if operator == None: lhs = parens
            else: rhs = parens
            i = j

        elif symbol in lsymbols.lsymbols:
            modifier = None
            if symbol in lsymbols.NOT_EXTRAS:
                modifier = lsymbols.NOT
                continue
            elif operator != None:
                lhs = operate(lhs, rhs, operator)
            operator = lsymbols.standardize(symbol)

        elif symbol in "01":
            mod_symbol = n_to_b(symbol)
            if modifier == lsymbols.NOT: mod_symbol = not mod_symbol
            if operator == None:
                lhs.append(mod_symbol)
            else:
                rhs.append(mod_symbol)

    if len(rhs) == 0:
        res = lhs
    else:
        res = operate(lhs, rhs, operator)
    if pretty_return:
        return "".join([b_to_n(bit) for bit in res])
    else:
        return res