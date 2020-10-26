EPSILON = 0.0001

class VectorIterator:
    def __init__(self, vector):
        self.vector = vector
        self.index = 0

    def __next__(self):
        if self.index < len(self.vector):
            self.index += 1
            return self.vector[self.index-1]
        raise StopIteration


class Vector:
    def __init__(self, data):
        self.data = data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, i):
        return self.data[i]

    def __setitem__(self, i, val):
        self.data[i] = val

    def __iter__(self):
        return VectorIterator(self)

    def __str__(self):
        return "["+", ".join([str(d) for d in self.data])+"]"

    def __repr__(self):
        return f"Vector({str(self)})"

    def __mul__(self, scalar):
        conditional_rounding = lambda x: round(x) if abs(round(x)-x) < EPSILON else x
        
        return Vector([conditional_rounding(n*scalar) for n in self])
    
    def __rmul__(self, scalar):
        return self*scalar
    
    def __truediv__(self, scalar):
        return self * (1 / scalar)
    
    def __rtruediv__(self, scalar):
        return Vector([scalar/v for v in self])

    def __add__(self, other):
        if len(self) != len(other):
            raise ValueError("Cannot add two vectors of different lengths")

        return Vector([self[i] + other[i] for i in range(len(self))])
    
    def __sub__(self, other):
        return self + (other * -1)

    def __neg__(self):
        return self * -1

    def __abs__(self):
        return Vector([abs(n) for n in self.data])

    def __eq__(self, other):
        if type(other) != type(self):
            return False

        return all(self[i] == other[i] for i in range(len(self)))

    def __ne__(self, other):
        return not self == other

    def dot(self, other):
        res = 0
        for i in range(len(self.data)):
            res += self.data[i]*other.data[i]
        return res

    def magnitude(self):
        return sum(n**2 for n in self.data)**(1/2)

    def normalize(self):
        return self / self.magnitude()

    def round(self, dec=0):
        self.data = [round(d, dec) for d in self.data]

    def is_zero(self):
        for n in self.data:
            if n != 0:
                return False
        return True
    
    def index_first_nonzero(self):
        for i in range(len(self.data)):
            if abs(self.data[i]) > EPSILON:
                return i
        return None

    def first_nonzero(self):
        i = self.index_first_nonzero()
        if i == None:
            return None
        else:
            return self.data[i]
    
    def append(self, n):
        self.data.append(n)

    def ortho_proj(self, other):
        return (self.dot(other) / other.dot(other)) * other

    def copy(self):
        return Vector(self.data.copy())


class Matrix:
    """
    n x m row-major matrix
    """
    def __init__(self, vecs):
        size = (len(vecs), len(vecs[0]))
        for i in range(len(vecs)):
            assert len(vecs[i]) == size[1], "All rows must be the same size"
            # Convert lists to vector if necessary
            if type(vecs[i]) == list:
                vecs[i] = Vector(vecs[i])

        self.rows = vecs

    @staticmethod
    def identity(n):
        return Matrix([[int(i==j) for i in range(n)] for j in range(n)])
    
    def __str__(self):
        return str(self.rows)
    
    def __repr__(self):
        return f"Matrix({str(self.as_list())})"

    def __getitem__(self, i):
        return self.rows[i]
    
    def print(self, name=""):
        def conditional_abs(n):
            if "__abs__" in dir(n.__class__): return abs(n)
            return n
        longest = max(max(len(str(conditional_abs(n))) for n in r) for r in self.rows) + 1
        if name:
            print(f"{name}: ", end="")
        print(f"Matrix {len(self.rows)}x{len(self.rows[0])}:")
        for row in self.rows:
            for num in row:
                padded = str(num)
                padding_needed = longest - len(padded)
                if str(num)[0] == '-':
                    padding_needed += 1
                else:
                    padded = " "+padded
                print(padded + "," + " "*padding_needed, end="")
            print()

    def as_list(self):
        return [list(r) for r in self.rows]

    def transpose(self):
        return Matrix([list(row) for row in zip(*self.rows)])

    def __mul__(self, other):
        if type(other) == Matrix:
            assert len(self.rows[0]) == len(other.rows), "Cannot multiply matrices of incompatible sizes"
            res = []
            other = other.transpose()
            for col in other.rows: # cols bc transposed
                new_col = []
                for i in range(len(self.rows)):
                    new_col.append(sum([self.rows[i][j]*col[j] for j in range(len(col))]))
                res.append(new_col)
            return Matrix(res).transpose()

        elif type(other) == Vector:
            assert len(self.rows[0]) == len(other), "Cannot multiply matrix with vector of incompatible size"
            res = []
            for row in self.rows:
                total = 0
                for i in range(len(other)):
                    total += row[i] * other[i]
                res.append(total)
            return Vector(res)

        else:
            return Matrix([[self.rows[i][j] * other for j in range(len(self.rows[i]))] for i in range(len(self.rows))])
    
    def __rmul__(self, other):
        if isinstance(other, Matrix):
            return other.__mul__(self)
        elif isinstance(other, Vector):
            raise ValueError("Cannot left multiply a vector with a matrix!")
        return self.__mul__(other)

    def __truediv__(self, other):
        return self.__mul__(1/other)

    def __add__(self, other):
        if type(other) == Matrix:
            return Matrix([[self.rows[i][j] + other.rows[i][j] for j in range(len(self.rows[i]))] for i in range(len(self.rows))])
        else:
            return Matrix([[self.rows[i][j] + other for j in range(len(self.rows[i]))] for i in range(len(self.rows))])
    
    def __sub__(self, other):
        return self.__add__(other * -1)

    def __neg__(self):
        return self * -1

    def round(self, dec=0):
        for r in range(len(self.rows)):
            for c in range(len(self.rows[r])):
                self.rows[r][c] = round(self.rows[r][c]*pow(10,dec))/pow(10,dec)
    
    def to_echelon_form(self):
        i = 1
        while 1:
            self.rows.sort(key = lambda x: abs(x).data, reverse=True)
            
            if i == len(self.rows):
                break
            elif self.rows[i].is_zero():
                break
            elif self.rows[i].index_first_nonzero() == self.rows[i-1].index_first_nonzero():
                scaling_factor = self.rows[i].first_nonzero() / self.rows[i-1].first_nonzero()
                self.rows[i] -= self.rows[i-1] * scaling_factor
            else:
                i += 1
        for i in range(len(self.rows)):
            first_nonzero = self.rows[i].first_nonzero()
            if first_nonzero != None:
                self.rows[i] /= first_nonzero

    def to_reduced_echelon_form(self, already_echelon_form=False):
        if not already_echelon_form:
            self.to_echelon_form()

        for i in range(len(self.rows)):
            pivot_point = self.rows[i].index_first_nonzero()
            if pivot_point == None:
                break

            for j in range(i-1,-1,-1):
                scaling_factor = self.rows[j][pivot_point] / self.rows[i][pivot_point]
                self.rows[j] -= self.rows[i] * scaling_factor

    def determinant(self, iterating_rows=True, other_index=0):
        if (len(self.rows) == 2 and len(self.rows[0]) == 2):
            return self.rows[0][0] * self.rows[1][1] - self.rows[0][1] * self.rows[1][0]

        result = 0
        if iterating_rows:
            for i in range(len(self.rows)):
                result += self.cofactor(i, other_index) * self[i][other_index]
        else:
            for j in range(len(self.rows[0])):
                result += self.cofactor(other_index, j) * self[other_index][j]
        return result
        
    def excluding(self, i, j):
        """
        Returns a new matrix without row i and column j
        """
        res = []
        for r in range(len(self.rows)):
            if r != i:
                row = []
                for c in range(len(self.rows[r])):
                    if c != j:
                        row.append(self.rows[r][c])
                res.append(row)
        return Matrix(res)

    def cofactor(self, i, j):
        "i & j are zero indexed"
        cf_mat = self.excluding(i, j)
        return cf_mat.determinant() * (-1)**(i+j)

    def add_column(self, col):
        assert len(col) == len(self.rows), "invalid column size"
        for i in range(len(self.rows)):
            self.rows[i].append(col[i])

    def inverse(self):
        m = self.transpose()
        m.rows.extend(Matrix.identity(len(self.rows)))
        m = m.transpose()
        m.to_reduced_echelon_form()
        m = m.transpose()
        m.rows = m.rows[len(self.rows):]
        m = m.transpose()
        return m

# Aliases for shorter code
Vec = Vector
Mat = Matrix

"""
Why spend a couple minutes doing parsing by hand when you can spend hours
making and debugging a program to parse it???
Apparently sometimes the equation ('-' in '-') where both characters are dashes
returns False.
"""
def standard_translation_matrix(variables, transformation):
    variables = variables.replace(" ", "")
    transformation = transformation.replace(" ", "")
    # replace minus (−) and dash (-) with 'm' because sometimes '-' in '-' returns False (wtf python???)
    transformation = transformation.replace("−", "m")
    transformation = transformation.replace("-", "m")
    variables = variables.split(",")
    rows = []
    equations = transformation.split(",")
    # print("variables", variables)
    # print("equations:", equations)
    for eq in equations:
        # print("equation:", eq)
        current_eq = [0 for _ in range(len(variables))]
        current_n = ""
        for char in eq:
            # print("char:", char, "current_n:", current_n, end=" ")
            for var_index in range(len(variables)):
                if char == variables[var_index]:
                    # print("char in variables", end=" ")
                    current_n = current_n.replace("m", "-") # replace m back into a dash(-)
                    if len(current_n) > 0:
                        current_eq[var_index] = int(current_n)

            if char in "m0123456789":
                # print("char in list", end=" ")
                current_n += char
            else:
                current_n = ""
        #     print()
        # print("adding current_eq:", current_eq)
        rows.append(current_eq)
    return Mat(rows)

stm = standard_translation_matrix


def interpolating_polynomial(points, degree=-1):
    """
    Generate a matrix for an interpolating polynomial from point pairs
    By default, degree will be the number of points
    """
    if degree == -1:
        degree = len(points)
    
    vectors = []
    for point in points:
        poly = []
        for n in range(degree):
            poly.append(pow(point[0], n))
        poly.append(point[1])
        vectors.append(Vec(poly))

    return Mat(vectors)

def orthogonalize(basis):
    ortho_basis = []
    for i in range(len(basis)):
        ortho_vector = basis[i]
        for j in range(len(ortho_basis)):
            ortho_vector -= basis[i].ortho_proj(ortho_basis[j])
        ortho_basis.append(ortho_vector)
    return ortho_basis


class Variable:
    def __init__(self, name, coefficient=1, power=1):
        self.name = name
        self.coefficient = coefficient
        self.power = power

    def __neg__(self):
        return Variable(self.name, coefficient=-self.coefficient, power=self.power)

    def __add__(self, other):
        if isinstance(other, Variable):
            if other.name == self.name:
                if other.power == self.power:
                    return Variable(self.name, coefficient=self.coefficient+other.coefficient, power=self.power)
                else:
                    return Equation([self, other])

        elif isinstance(other, Term):
            return other.__add__(self)

        elif isinstance(other, Equation):
            return other.__add__(self)

        # Number or something
        else:
            return Equation(self).__add__(other)
    
    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        return self.__add__(-other)

    def __rsub__(self, other):
        return (-self).__add__(other)

    def __mul__(self, other):
        return Term(self)*other

    def __rmul__(self, other):
        return self.__mul__(other)

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name and self.coefficient == other.coefficient and self.power == other.power

    def __str__(self):
        res = self.name
        if (self.coefficient != 1):
            res = str(self.coefficient) + "*" + res
        if (self.power != 1):
            res += "^" + str(self.power)
        return res

    def copy(self):
        return Variable(self.name, coefficient=self.coefficient, power=self.power)

Var = Variable

class Term:
    def __init__(self, variables, coefficient=1):
        """
        Creates a term where variables are multiplied together
        The variable coefficients will be combined into a single Term coefficient

        variables should be a list. WARNING: It will be shallow copied
        comparing variables == other.variables should tell you if the two terms are compatible (can be added together)
        """

        if "__len__" in dir(variables.__class__):
            self.variables = variables
        else: # So you can create a Term from a single variable more easily
            self.variables = [variables]

        # Move all the variable's coefficients into the term's coefficient
        self.coefficient = coefficient
        for i in range(len(self.variables)):
            self.coefficient *= self.variables[i].coefficient
            self.variables[i].coefficient = 1

    def __neg__(self):
        return Term(self.copy_variables(), coefficient=-self.coefficient)

    def __add__(self, other):
        if isinstance(other, Variable):
            other = Term(other)
        
        if isinstance(other, Term):
            if self.compatible(other.variables):
                return Term(self.copy_variables(), coefficient=self.coefficient+other.coefficient)
            else:
                return Equation([self.copy(), other.copy()])

        elif isinstance(other, Equation):
            return other.__add__(self)

        else: # Should be a plain number
            return Equation(self.copy()).__add__(other)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        return self.__add__(-other)

    def __rsub__(self, other):
        return (-self).__add__(other)

    def __mul__(self, other):
        if isinstance(other, Variable):
            other = Term(other)
        
        if isinstance(other, Term):
            new_vars = self.copy_variables()
            for var in other.variables:
                exists = False
                for i in range(len(new_vars)):
                    if var.name == new_vars[i].name:
                        exists = True
                        new_vars[i].power += var.power
                if not exists:
                    new_vars.append(var)

            new_coefficient = self.coefficient*other.coefficient
            if new_coefficient == 0: return 0
            return Term(new_vars, coefficient=new_coefficient)

        elif isinstance(other, Equation):
            return other.__mul__(self)
        
        elif isinstance(other, Vector) or isinstance(other, Matrix):
            return NotImplemented

        else: # Should be a plain number
            new_coefficient = self.coefficient*other
            if new_coefficient == 0: return 0
            return Term(self.copy_variables(), coefficient=new_coefficient)
    
    def __rmul__(self, other):
        return self.__mul__(other)
    
    def __str__(self):
        res = []
        for v in self.variables:
            res.append(str(v))
        res = " * ".join(res)
        if (self.coefficient != 1):
            res = str(self.coefficient) + " * " + res
        return res

    def copy_variables(self):
        return [v.copy() for v in self.variables]

    def copy(self):
        return Term(self.copy_variables(), coefficient=self.coefficient)

    def compatible(self, variables):
        if len(self.variables) != len(variables): return False
        for var in self.variables:
            in_variables = False
            for other_var in variables:
                if var == other_var:
                    in_variables = True
            if not in_variables:
                return False
        return True


class Equation:
    def __init__(self, terms, constant=0):
        if "__len__" in dir(terms.__class__):
            self.terms = terms
        else: # So you can create an Equation from a single term more easily
            self.terms = [terms]
        
        # Convert to Terms if needed
        if len(self.terms) > 0:
            if not isinstance(self.terms[0], Term):
                self.terms = [Term(t) for t in self.terms]

        self.constant = constant

    def __neg__(self):
        new_equation = Equation([], constant=-self.constant)
        for t in self.terms:
            new_equation.terms.append(-t.copy())
        return new_equation

    def __add__(self, other):
        if isinstance(other, Variable):
            other = Term(other)

        if isinstance(other, Term):
            new_terms = [t.copy() for t in self.terms]
            for i in range(len(new_terms)):
                if new_terms[i].compatible(other.variables):
                    new_terms[i] += other
                    return Equation(new_terms, constant=self.constant)
            new_terms.append(other)
            return Equation(new_terms, constant=self.constant)

        elif isinstance(other, Equation):
            new_equation = self.copy()
            for term in other.terms:
                new_equation += term
            new_equation.constant += other.constant
            return new_equation

        else: # Should be a plain number
            new_equation = self.copy()
            new_equation.constant += other
            return new_equation

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        return self.__add__(-other)

    def __rsub__(self, other):
        return (-self).__add__(other)

    def __mul__(self, other):
        # print("mul w/ other", other)
        if isinstance(other, Variable):
            other = Term(other)

        if isinstance(other, Equation):
            new_equation = self.copy()*other.constant # Shouldn't cause a loop because constant multiplication is handled differently
            for term in other.terms:
                # print("other equation")
                # print("ne", new_equation)
                # print("self", self)
                new_equation += self * term
            return new_equation

        elif isinstance(other, Vector) or isinstance(other, Matrix):
            return NotImplemented
        
        else: # Terms and constants have multiplication handled the same way
            new_equation = Equation([])
            for i in range(len(self.terms)):
                # print("self before", self)
                new_equation += (self.terms[i].copy())*other
                # print("self after", self)
                # print("term or const")
                # print(self.terms[i])
                # self.terms[i].copy().variables[0] = Variable("y", power=10)
                # print("ne", new_equation)
                # print("self", self)
            new_equation += self.constant * other
            return new_equation

    def __rmul__(self, other):
        return self.__mul__(other)

    def __str__(self):
        res = []
        for t in self.terms:
            res.append("("+str(t)+")")
        if self.constant != 0:
            res.append(str(self.constant))
        return " + ".join(res)

    def copy(self):
        new_terms = [t.copy() for t in self.terms]
        return Equation(new_terms, constant=self.constant)

