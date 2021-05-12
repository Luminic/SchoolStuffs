def priv_cartesian_product(my_sets, index=0):
    if index < len(my_sets) - 1:
        other = priv_cartesian_product(my_sets, index+1)
    else:
        return [[e] for e in my_sets[index]]

    res = []
    for element in my_sets[index]:
        for group in other:
            # print(element, other)
            # tmp = other[:]
            res.append([element] + group)
    return res

def print_without_quotes(obj):
    return str(obj).replace("'", "")
    
def cartesian_product(inp_sets, print_res=True):
    res = priv_cartesian_product(inp_sets)
    res = {tuple(e) for e in res}
    if print_res:
        print_without_quotes(res)
    return res
    

def get_result(my_set):
    return None

