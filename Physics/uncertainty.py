import numbers

class UncertainNumber(numbers.Number):
    """
    Creates a number with an uncertainty and propagates those uncertainties when performing calculations
    If mixed with non `UncertainNumber` classes in calculations, it assumes the other has infinite precision
    """

    def __init__(self, number, uncertainty=0):
        if isinstance(number, UncertainNumber): # allow `UncertainNumber(UncertainNumber)` to work
            self.n = number.n
            self.u = number.u
        elif isinstance(number, numbers.Number):
            self.n = number
            self.u = abs(uncertainty)

    def percent_error(self):
        if self.n == 0: return 0
        return self.u / self.n

    def __neg__(self):
        return UncertainNumber(-self.n, self.u)

    def __add__(self, other):
        """
        Propagates uncertainty by adding uncertainties
        """
        other = UncertainNumber(other)
        return UncertainNumber(self.n + other.n, self.u + other.u)

    def __radd__(self, other):
        return self + other
    
    def __sub__(self, other):
        """
        Propagates uncertainty by adding uncertainties
        """
        other = UncertainNumber(other)
        return UncertainNumber(self.n - other.n, self.u + other.u)
    
    def __rsub__(self, other):
        return -self + other

    def __mul__(self, other):
        """
        Propagates uncertainty by adding the %error for both values and converting back to error after multiplication
        """
        other = UncertainNumber(other)
        p_err = self.percent_error() + other.percent_error()
        res = self.n * other.n
        return UncertainNumber(res, abs(res*p_err))

    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other):
        """
        Propagates uncertainty by adding the %error for both values and converting back to error after division
        """
        other = UncertainNumber(other)
        p_err = self.percent_error() + other.percent_error()
        res = self.n / other.n
        return UncertainNumber(res, abs(res*p_err))

    def __rtruediv__(self, other):
        return UncertainNumber(1/self.n, self.u) * other

    def __abs__(self):
        """
        Returns the absolute values of the number component of self
        The uncertainty component should always be positive
        """
        return UncertainNumber(abs(self.n), self.u)

    def __pow__(self, exponent):
        """
        Propagates uncertainty using the worst case method
        Warning: Uncertainties can very quickly blow up when using exponents
        """
        exponent = UncertainNumber(exponent)
        res = self.n ** exponent.n
        low = (self.n - self.u) ** (exponent.n - exponent.u)
        high = (self.n + self.u) ** (exponent.n + exponent.u)
        uncertainty = max(abs(res - low), abs(res-high))

        return UncertainNumber(res, uncertainty)

    def __rpow__(self, other):
        other = UncertainNumber(other)
        return other ** self

    def __eq__(self, other):
        """
        Compares the values of two `UncertainNumber`s
        Does not take the uncertainty into account
        """
        other = UncertainNumber(other)
        return self.n == other.n

    def __lt__(self, other):
        other = UncertainNumber(other)
        return self.n < other.n

    def __le__(self, other):
        return not (self > other)
    
    def __gt__(self, other):
        other = UncertainNumber(other)
        return self.n > other.n

    def __ge__(self, other):
        return not (self < other)

    def __repr__(self):
        return f"UncertainNumber({self.n}, {self.u})"

    def __str__(self):
        return str(self.n) + " ±" + str(self.u)
