def eulers_method(f, h=1, x_n=0, y_n=0, iterations=1, table=False, n_type=float):
    h = n_type(h)
    x_n = n_type(x_n)
    y_n = n_type(y_n)

    if table: res = [(x_n, y_n)]
    for _ in range(iterations):
        y_n += h * f(x_n, y_n)
        x_n += h
        if table: res.append((x_n, y_n))

    if table: return res
    return (x_n, y_n)

def improved_eulers_method(f, h=1, x_n=0, y_n=0, iterations=1, table=False, return_u=False, n_type=float):
    h = n_type(h)
    x_n = n_type(x_n)
    y_n = n_type(y_n)

    if table: 
            if return_u: res = [[x_n, n_type(0), y_n]]
            else: res = [[x_n, y_n]]
    for _ in range(iterations):
        L = f(x_n, y_n)
        u_n = y_n + L * h
        x_n += h
        R = f(x_n, u_n)
        y_n += h*(L+R)/2

        if table: 
            if return_u: res.append([x_n, u_n, y_n])
            else: res.append([x_n, y_n])

    if table: return res
    if return_u: return [x_n, u_n, y_n]
    return [x_n, y_n]

def print_table(data, headers=None, truncate=5):
    longest = [0]*len(data[0])
    for row in data:
        for i, col in enumerate(row):
            longest[i] = max(len(str(col)), longest[i])
            
    for i, v in enumerate(longest):
        longest[i] = min(truncate, v)

    def to_length(s, length):
        if s[0] != '-': s = ' '+s
        if len(s) >= length+1: s = s[:length+1]
        else: s += ' '*(length+1-len(s))
        return s

    if headers != None:
        for c_i, col in enumerate(headers):
            s = to_length(col, longest[c_i])
            print(s, end='')
            if c_i != len(headers)-1: print(' |', end='')
            else: print()

        for i in range(len(headers)):
            s = '-'*(longest[i]+1)
            print(s, end='')
            if i != len(headers)-1: print('-+', end='')
            else: print()
    
    for row in data:
        for c_i, col in enumerate(row):
            s = str(col)

            s = to_length(s, longest[c_i])

            print(s, end='')

            if c_i != len(row)-1: print(' |', end='')
            else: print()