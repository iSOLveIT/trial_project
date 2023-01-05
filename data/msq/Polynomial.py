import oneqloud_polynomials
import pickle, warnings
import logging.config
from time import sleep
from azure.quantum.optimization import Term

from logger.logger_config import LOGGING_CONFIG

# Set up logger
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)


def update_storage(func):
    def wrapper(*args):
        args[0]._stored = None
        return func(*args)

    return wrapper


class Polynomial(object):
    """A simple class to allow users to work with binary polynomials of varying degrees"""

    # Used to decide whether to use qbp or bp. This can be modified later, currently set based on a test with 4100 terms (and variables).
    _threshold = 50

    constant_term = property(
        fset=update_storage(
            lambda self, value: setattr(self.bp, "constant_term", value)
        )
    )
    degree = property()
    term_count = property()
    var_count = property()
    var_list = property()

    def __init__(self, terms=[], reduce=False):
        """
        The constructor for Polynomial class.

        Args:
           terms (list): Terms used to construct polynomial.
           reduce (bool): The flag to decide whether or not to reduce the polynomial.
        """
        if isinstance(terms, oneqloud_polynomials.BinaryPolynomial):
            self.bp = terms.clone()
        else:
            self.bp = oneqloud_polynomials.BinaryPolynomial()
            for term in terms:
                self.bp.add_term(term[0], term[1])
        self._stored = None
        self.__reduce = reduce  # Used to decide whether to reduce the given polynomial
        # Used to store the fixed variables to be added to the solution
        self._processed_portion = {}

    def __repr__(self):
        return self.bp.to_string()

    def __getattr__(self, name):
        try:
            return getattr(self.bp, name)
        except AttributeError:
            err_msg = "Polynomial object does not have attribute {}".format(name)
            logger.error(err_msg)
            raise AttributeError(err_msg) from None

    @property
    def var_terms(self):
        logger.debug("()")
        bp_ = self.bp.clone()
        bp_.set_coefficient(0, [])
        return bp_

    def add_terms(self, terms):
        logger.debug("()")
        if len(terms) == 0:
            err_msg = "No Term to add"
            logger.error(err_msg)
            raise Exception(err_msg)
        else:
            for term in terms:
                self.add_term(term[0], term[1])
        logger.debug("- Return")

    @update_storage
    def power(self, exponent):
        # QuadraticBinaryPolynomial()
        logger.debug("()")
        if (
            (self.bp.degree < 2)
            and (exponent <= 2)
            and (self.term_count > Polynomial._threshold)
        ):
            qbp = self.to_qbp()
            qbp.square()
            self.bp = Polynomial.from_qbp(qbp).bp
        # BinaryPolynomial()
        else:
            self.bp.power(exponent)
        logger.debug("- Return")

    @update_storage
    def multiply(self, poly):
        # Will accept polynomial or constant
        # QuadraticBinaryPolynomial()
        logger.debug("()")
        use_qbp = True
        if isinstance(poly, Polynomial):
            mul_obj = poly.bp
            use_qbp = False
        else:
            mul_obj = poly
        if (
            (self.degree <= 2)
            and (use_qbp)
            and (self.term_count > Polynomial._threshold)
        ):
            qbp = self.to_qbp()
            qbp.multiply(mul_obj)
            self.bp = Polynomial.from_qbp(qbp).bp
        # BinaryPolynomial()
        else:
            self.bp.multiply(mul_obj)
        logger.debug("- Return")

    @staticmethod
    def from_qbp(qbp, reduce=False):
        """
        Function to construct a Polynomial object from a QuadraticBinaryPolynomial.

        Args:
           qbp: The QuadraticBinaryPolynomial object used to construct polynomial.
           reduce (bool): The flag to decide whether or not to reduce the polynomial.

        Returns polynomial
        """
        logger.debug("()")
        poly = Polynomial(reduce=reduce)
        poly.bp = oneqloud_polynomials.BinaryPolynomial(qbp)
        logger.debug("- Return")
        return poly

    @staticmethod
    def from_numpy(array, var_list=None, reduce=False):
        """
        Function to construct a Polynomial object from a numpy array or matrix.
        Currently only supports square matrices to create Polynomial of degree<=2.

        If a list of variable indices is provided the resulting polynomial's
        variable indices will be replaced with those in the list. The list must match array dimensions.

        Args:
           array (numpy): The array or matrix used to construct polynomial.
           var_list (list): Variable indices to be used for the polynomial.
           reduce (bool): The flag to decide whether or not to reduce the polynomial.

        Returns polynomial
        """
        logger.debug("()")
        qbp = oneqloud_polynomials.binary_polynomial.qbp_from_numpy(
            array=array, var_list=var_list
        )
        poly = Polynomial.from_qbp(qbp, reduce=reduce)
        logger.debug("- Return")
        return poly

    @staticmethod
    def from_azure_terms(terms):
        """
        Convert a list of Azure Terms to a Qanopy Polynomial.

        Args:
           terms (dict): Terms used to construct polynomial.

        Returns polynomial
        """
        logger.debug("()")
        poly = Polynomial()
        for term in terms:
            poly.add_terms([term.w, term.ids])
        logger.debug("- Return")
        return poly

    @staticmethod
    def from_azure_terms_file(path):
        """Load a problem as a list of azure.quantum.optimization.Term.
        Args:
            path (string): Full path to problem components.
        Returns:
            list: List of azure.quantum.optimization.Term. Note that the
                constant term is included.
        """
        logger.debug("()")
        try:
            poly = Polynomial.from_file(path)
        except RuntimeError:
            with open(path, "rb") as f:
                poly_list = pickle.load(f)
                poly = Polynomial(poly_list)
        logger.debug("- Return")
        return qpoly_to_azure_terms(poly)

    @staticmethod
    def from_dict(terms_dict, reduce=False):
        """
        Function to construct a Polynomial object from a dictionary.
        Currently only supports Polynomial of degree<=2.

        Args:
           terms (dict): Terms used to construct polynomial.
           reduce (bool): The flag to decide whether or not to reduce the polynomial.

        Returns polynomial
        """
        logger.debug("()")
        poly = Polynomial(reduce=reduce)
        for k, v in terms_dict.items():
            if len(k) != 2:
                err_msg = "Key should have two indices. Higher order polynomial are not supported"
                logger.error(err_msg)
                raise Exception(err_msg)
            poly.add_term(v, [k[0], k[1]])
        logger.debug("- Return")
        return poly

    @staticmethod
    def from_file(filename, reduce=False):
        """
        Function to construct a Polynomial object from a serialized QuadraticBinaryPolynomial object.

        Args:
           filename (str): The file containing a serialized QuadraticBinaryPolynomial object.
           reduce (bool): The flag to decide whether or not to reduce the polynomial.

        Returns polynomial
        """
        logger.debug("()")
        pr = oneqloud_polynomials.binary_polynomial.PolynomialReader(filename)
        qbp = pr.load()
        poly = Polynomial.from_qbp(qbp, reduce=reduce)
        logger.debug("- Return")
        return poly

    def to_qbp(self):
        logger.debug("()")
        if self.degree > 2:
            err_msg = "Cannot convert to qbp object. Degree > 2."
            logger.error(err_msg)
            raise Exception(err_msg)
        qubo = oneqloud_polynomials.QuadraticBinaryPolynomial()
        for term in self.bp:
            if len(term.var_list) == 0:
                qubo.add_constant_term(term.coefficient)
            elif len(term.var_list) < 2:
                qubo.add_term(term.coefficient, term.var_list[0])
            else:
                qubo.add_term(term.coefficient, term.var_list[0], term.var_list[1])
        logger.debug("- Return")
        return qubo

    def to_list(self):
        logger.debug("()")
        terms = []
        for term in self.bp:
            terms.append([term.coefficient, term.var_list])
        logger.debug("- Return")
        return terms

    def to_file(self, filename):
        """
        Saves a qbp Polynomial into a file.
        """
        logger.debug("()")
        if self.degree > 2:
            err_msg = "Polynomial should not be greater than degree 2."
            logger.error(err_msg)
            raise Exception("Polynomial should not be greater than degree 2.")
        qbp = self.to_qbp()
        pw = oneqloud_polynomials.binary_polynomial.PolynomialWriter(filename)
        pw.save(qbp)
        logger.debug("- Return")

    def to_numpy(self):
        """
        Returns an upper triangular matrix representation of the qbp polynomial.

        """
        logger.debug("()")
        if self.degree > 2:
            err_msg = "Polynomial should not be greater than degree 2."
            logger.error(err_msg)
            raise Exception("Polynomial should not be greater than degree 2.")
        if self.constant_term != 0:
            err_msg = "Only var_terms() supported. Polynomial entered has a constant."
            logger.error(err_msg)
            raise Exception(err_msg)

        qbp = self.to_qbp()
        qbp.export_array()
        logger.debug("- Return")
        return qbp.export_array()

    def to_azure_terms(
        self,
        rounding=False,
        include_constant_term=True,
    ):
        """Convert a Qanopy Polynomial to a list of Azure Terms."""
        logger.debug("()")
        terms = [
            self.to_azure_term(monomial, rounding=rounding)
            for monomial in sorted(self.bp, key=str)
            if len(monomial.var_list) > 0
        ]

        if include_constant_term is True:
            const_term = self.constant_term
            if rounding:
                const_term = int(round(const_term))

            if const_term != 0:
                terms.append(Term(c=const_term, indices=[]))

        logger.debug("- Return")
        return terms

    def to_azure_term(self, monomial, rounding=False):
        """Convert a single term of a Qanopy Polynomial to an Azure Term."""
        logger.debug("()")
        indices = monomial.var_list
        coefficient = monomial.coefficient
        if rounding:
            coefficient = int(round(coefficient))

        logger.debug("- Return")
        return Term(c=coefficient, indices=indices)

    # All other oneqloud_polynomials BinaryPolynomial attributes and functions are included directly below:
    @update_storage
    def sum(self, Polynomial):
        self.bp.sum(Polynomial.bp)

    def equals(self, Polynomial):
        return self.bp.equals(Polynomial.bp)

    def has_term(self, var_list):
        return self.bp.has_term(var_list)

    @update_storage
    def add_term(self, constant, var_list):
        self.bp.add_term(constant, var_list)

    @update_storage
    def set_coefficient(self, coeff, var_list):
        self.bp.set_coefficient(coeff, var_list)

    def to_string(self):
        return self.bp.to_string()

    def get_coefficient(self, var_list):
        return self.bp.get_coefficient(var_list)

    def get_term(self, var_list):
        return self.bp.get_term(var_list)

    @update_storage
    def remove_term(self, var_list):
        self.bp.remove_term(var_list)

    @update_storage
    def remove_var(self, index):
        self.bp.remove_var(index)

    def __eq__(self, other):
        return self.equals(other)

    def __str__(self):
        return self.to_string()

    def __iter__(self):
        return iter(self.bp)

    def __len__(self):
        return len(self.bp)

    def __add__(self, other):
        poly = Polynomial(self.bp)
        if isinstance(other, Polynomial):
            poly.sum(other)
        else:
            poly.add_constant_term(other)
        return poly

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        return self.__add__(other * -1)

    def __rsub__(self, other):
        return other + (self * -1)

    def __mul__(self, other):
        poly = Polynomial(self.bp)
        poly.multiply(other)
        return poly

    def __rmul__(self, other):
        return self.__mul__(other)

    def __pow__(self, other):
        poly = Polynomial(self.bp)
        poly.power(other)
        return poly

    def _stored_state(self, tag):
        self._stored = tag

    @update_storage
    def _reduce(self):
        """Implementation of an in-place polynomial reduction.
        Will reduce a quadratic polynomial if __reduce attribute is set to True.

        Note:
            Reduces polynomials with degrees in (0,2].
        """
        logger.debug("()")
        if self.__reduce == True:
            if self.degree > 2:
                warnings.warn(
                    "Cannot reduce polynomials of degree > 2. Ignoring this request"
                )
                self.__reduce = False
            elif self.degree == 0:
                warnings.warn(
                    "Cannot reduce polynomials of degree 0. Ignoring this request"
                )
                self.__reduce = False
            else:
                qbp = self.to_qbp()
                oneqloud_polynomials.binary_polynomial.preprocess(qbp)
                if qbp.fixed_vars != {}:
                    self._processed_portion = qbp.fixed_vars
                    new_qbp = oneqloud_polynomials.binary_polynomial.reduce_qbp_by_configuration(
                        qbp, qbp.fixed_vars
                    )
                    self.bp = Polynomial.from_qbp(new_qbp).bp
        logger.debug("- Return")

    def __copy__(self):
        return Polynomial(self.bp)

    def __deepcopy__(self, memo):
        # Shallow and deep are the same
        return self.__copy__()
