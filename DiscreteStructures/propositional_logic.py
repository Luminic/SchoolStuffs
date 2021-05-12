import string
import copy
from setsnstuff import *

class Variable:
    def __init__(self, name, value=None):
        self.name = name
        self.value = value
    
    def get_value_or(self, if_none):
        if self.value == None:
            return if_none
        return self.value
    
    def __repr__(self):
        if self.value == None:
            return f"Variable(\"{self.name}\")"
        return f"Variable(\"{self.name}\", {self.value})"
    
    def __str__(self):
        return self.name
    
    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
    
    def __ne__(self, other):
        return not (self == other)

def standardize_logic_symbol(symbol):
    if symbol in "∧^ᴧ":
        return '^'
    elif symbol in "∨v":
        return 'v'
    elif symbol in "⟹→":
        return '→'
    elif symbol in "∼~¬!":
        return "~"
    elif symbol in "↑|":
        return "↑"
    else:
        return symbol

class Equation:
    def __init__(self, as_str="", modifiers=[]):
        self.modifiers = copy.deepcopy(modifiers)
        self.equation = []
        i = 0
        current_modifiers = []
        while i < len(as_str):
            s = standardize_logic_symbol(as_str[i])

            if as_str[i] in string.whitespace:
                pass

            elif as_str[i] in '([':
                # find corresponding parentheses
                depth = 0
                j = i + 1
                while j < len(as_str):
                    if as_str[j] in "([":
                        depth += 1
                    elif as_str[j] in ")]":
                        if depth == 0:
                            break
                        else:
                            depth -= 1
                    j += 1
                    assert j != len(as_str), "No corresponding parentheses could be found in Equation"

                self.equation.append(Equation(as_str[i+1:j], current_modifiers))
                current_modifiers.clear()
                # move index past the parentheses
                i = j
            
            elif s in "v^→↔≡⊕↑↓":
                self.equation.append(s)
            
            elif s == "~":
                current_modifiers.append(s)

            # Variable
            else:
                self.equation.append(Equation("", current_modifiers))
                self.equation[-1].equation.append(Variable(as_str[i]))
                current_modifiers.clear()

            i += 1
    
    def __repr__(self):
        return f"Equation({repr(self.modifiers)}, {repr(self.equation)})"

    def __str__(self):
        if len(self.equation) == 1:
            as_str = str(self.equation[0])
        elif len(self.equation) < 1:
            print("Warning: invalid equation")
            return "<inv>"
        else:
            as_str = "".join(str(e) for e in self.equation)
            as_str = f"({as_str})"
        if self.modifiers:
            modifiers = "".join(str(m) for m in self.modifiers)
            as_str = modifiers + as_str
        return as_str

    def evaluate(self, tmp_vals=dict(), if_none=None):
        """
        A somewhat naive evaluation of the equation

        `tmp_vals` gives variables a temporary value for this evaluation.
        It will override even a variable with a value.

        If a variable is not in `tmp_vals` and doesn't have a value, it
        will temporarily be given the value `if_none`.
        """

        running_result = None
        current_operation = None
        for i, e in enumerate(self.equation):
            current_value = None
            if isinstance(e, Variable):
                if e in tmp_vals:
                    current_value = tmp_vals[e]
                else:
                    current_value = e.get_value_or(if_none)

            elif isinstance(e, Equation):
                current_value = e.evaluate(tmp_vals, if_none)

            else:
                # e is some kind of combining logic operator
                assert current_operation == None, "Multiple operators next to each other"
                assert i != 0, "Logic operator with with no equation/variable preceding it"
                current_operation = e
                continue

            if i == 0:
                running_result = current_value

            elif current_operation == 'v':
                if running_result == True or current_value == True: 
                    running_result = True # Universal Bound Law 
                elif running_result == False and current_value == False:
                    running_result = False # Idempotent Law (I know its unnecessary but it makes my intentions clear)
                else:
                    running_result = None # It cannot be decided what `running_result` should be
            
            elif current_operation == '^':
                if running_result == False or current_value == False:
                    running_result = False # Universal Bound Law
                elif running_result == True and current_value == True:
                    running_result = True # Idempotent Law
                else:
                    running_result = None # It cannot be decided what `running_result` should be

            elif current_operation == '→':
                # p → q is logically equivalent to (p^q) v ~p
                # I am fully aware this impl. is about as inefficient as you get
                p = Variable('p')
                q = Variable('q')
                eq = Equation("(p^q)v~p")
                res = eq.evaluate({p:running_result, q:current_value})
                running_result = res

            elif current_operation == '↔':
                # p ↔ q is logically equivalent to (p→q)^(q→p)
                p = Variable('p')
                q = Variable('q')
                eq = Equation("(p→q)^(q→p)")
                res = eq.evaluate({p:running_result, q:current_value})
                running_result = res
            
            elif current_operation == '⊕':
                # p ⊕ q is logically equivalent to (p v q) ^ ~(p ^ q)
                p = Variable('p')
                q = Variable('q')
                eq = Equation("(p v q) ^ ~(p ^ q)")
                res = eq.evaluate({p:running_result, q:current_value})
                running_result = res

            elif current_operation == '≡':
                if running_result == None or current_value == None:
                    running_result = None # It cannot be decided what `running_result` should be
                else:
                    running_result = running_result == current_value

            elif current_operation == '↑':
                if running_result == False or current_value == False:
                    running_result = True
                elif running_result == None or current_value == None:
                    running_result = None # It cannot be decided what `running_result` should be
                else:
                    running_result = False
            
            elif current_operation == '↓':
                if running_result == True or current_value == True:
                    running_result = False
                elif running_result == False and current_value == False:
                    running_result = True
                else:
                    running_result = None # It cannot be decided what `running_result` should be

            else:
                print(current_operation)
                print(i, e)
                assert False, "Variables/Equations next to each other with no valid combining logical operator"

            # operation was used so now it is `None` again
            current_operation = None

        if running_result == None:
            return running_result

        nots = self.modifiers.count("~")
        if nots % 2 == 0:
            return running_result
        else:
            return not running_result

        
    def get_variables(self, output):
        for e in self.equation:
            if isinstance(e, Variable):
                output.add(e)
            elif isinstance(e, Equation):
                e.get_variables(output)

    def get_logic_table(self, variables=None, print_res=True):
        if variables == None:
            tmp = set()
            self.get_variables(tmp)
            variables = list(tmp)

        if len(variables) == 0:
            return
        elif isinstance(variables[0], Variable):
            pass
        else:
            variables = [Variable(v) for v in variables]

        all_tmp_vals = cartesian_product([{True, False}] * len(variables))

        results = []
        for current_tmp_vals in all_tmp_vals:
            tmp_vals = dict()
            for i in range(len(variables)):
                tmp_vals[variables[i]] = current_tmp_vals[i]

            assert len(variables) == len(current_tmp_vals)

            results.append((tmp_vals, self.evaluate(tmp_vals)))

        if print_res:
            print_logic_table(results)

        return results

def print_logic_table(table, order=None, reverse_scores=False):
    if order == None:
        order = list(table[0][0].keys())
    if not isinstance(order[0], Variable):
        order = [Variable(v) for v in order]

    def row_position(row):
        pos = 0
        for i, var in enumerate(order):
            if row[0][var] == True:
                if reverse_scores:
                    pos += 2**(i+1)
                else:
                    pos += 2**(len(order) - i - 1)
        return pos

    table.sort(key=row_position, reverse=True)

    print('{' + ", ".join(v.name for v in order) + "}, result")
    print('-'*20)
    for row in table:
        var_values = []
        for var in order:
            var_values.append('T' if row[0][var] else 'F')
        var_values = ", ".join(var_values)
        print('{' + var_values + '}' + f", {row[1]}")
