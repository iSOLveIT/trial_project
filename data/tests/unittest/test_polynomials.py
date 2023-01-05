# ugly code, not mine for whoever git blames this in the future
# TODO need to refactor
from azure.quantum.optimization import Term
from unittest import TestCase
from msq.Polynomial import Polynomial
import numpy as np
import os

terms_bp = [[1, [2, 3, 4]], [2, []], [3, [1]]]
terms_qubo = [[2, [1, 3]], [10, []], [2, [1]]]
terms_reduce = [[-2, [2, 3]], [1, [4]]]
terms_linear1 = [[2, [1]], [5, []]]
terms_linear2 = [[3, [2]], [6, []]]
terms_degree_zero = [[2, []]]
term_1 = [5, [1, 2]]
empty_term = []


Terms_and_known_solution = {"Terms": [[2, [0]]], "Processed": {0: False}}

data_path = "tests/unittest/data/"

# large_poly
terms = []
for i in range(52):
    var = []
    var.append(i)
    terms.append([i, var])
large_poly = Polynomial(terms)

client_poly1 = Polynomial(terms_bp)


def isAnagram(s1, s2):
    if sorted(s1) == sorted(s2):
        return True
    else:
        return False


class testPolynomials(TestCase):
    def test_constructor(self):
        self.assertEqual(client_poly1.constant_term, 2)
        self.assertEqual(client_poly1.degree, 3)
        self.assertEqual(client_poly1.term_count, 3)
        self.assertEqual(client_poly1.var_count, 4)
        self.assertEqual(client_poly1.var_list, [1, 2, 3, 4])
        self.assertEqual(client_poly1._stored, None)

    def test_repr(self):
        self.assertEqual(repr(Polynomial()), "0")

    def test_invalid_attribute(self):
        with self.assertRaises(Exception):
            arbitrary_attribute = client_poly1.arbitrary

    def test_var_terms(self):
        self.assertTrue(
            isAnagram(client_poly1.var_terms.to_string(), "3 x_1 + x_2 x_3 x_4")
        )

    def test_add_terms(self):
        client_poly = Polynomial()
        with self.assertRaises(Exception):
            client_poly.add_terms(empty_term)
        # ## single term:
        client_poly = Polynomial()
        client_poly.add_terms([term_1])
        self.assertTrue(isAnagram(client_poly.to_string(), "5 x_1 x_2"))
        # ## multiple terms:
        client_poly = Polynomial()
        client_poly.add_terms(terms_linear1)
        self.assertTrue(isAnagram(client_poly.to_string(), "5 + 2 x_1"))

    def test_from_numpy(self):
        # var_list None
        nump = np.array([[-3, 0, 2], [0, 1, 0], [0, 0, 1]])
        poly = Polynomial().from_numpy(array=nump)
        self.assertTrue(isAnagram(poly.to_string(), "x_2 + x_1 + 2 x_0 x_2 - 3 x_0"))
        # var_list not None
        poly2 = Polynomial().from_numpy(array=nump, var_list=[0, 5, 6])
        self.assertTrue(isAnagram(poly2.to_string(), "x_6 + 2 x_0 x_6 + x_5 - 3 x_0"))

    def test_from_file(self):
        poly_from_file = Polynomial.from_file(data_path + "pwexample.out")
        self.assertEqual(type(poly_from_file), Polynomial)

    def test_from_dict(self):
        terms_dict = {(0, 0): 0, (0, 1): 1, (1, 0): 2, (1, 1): 3}
        poly_from_dict = Polynomial.from_dict(terms_dict)
        self.assertEqual(type(poly_from_dict), Polynomial)

        terms_dict[(0, 1, 2)] = 4
        with self.assertRaises(Exception):
            invalid_poly = Polynomial.from_dict(terms_dict)

    def test_to_qbp(self):
        client_poly_qbp = Polynomial(terms_qubo)
        qbp = client_poly_qbp.to_qbp()
        self.assertIsNotNone(qbp)

        # Throws for degree>2
        with self.assertRaises(Exception):
            qbp = client_poly1.to_qbp()

    def test_to_list(self):
        term_list = client_poly1.to_list()
        self.assertEqual(term_list, [[1.0, [2, 3, 4]], [3.0, [1]], [2.0, []]])

    def test_to_numpy(self):
        poly_qbp = Polynomial(terms_reduce)  # valid qubo
        qbp_numpy = poly_qbp.to_numpy()
        self.assertTrue(isinstance(qbp_numpy, np.ndarray))

        poly_qbp = Polynomial(terms_qubo)  # with constant, invalid
        with self.assertRaises(Exception):
            qbp_numpy = poly_qbp.to_numpy()

        poly_bp = Polynomial(terms_bp)  # higher order, invalid
        with self.assertRaises(Exception):
            bp_numpy = poly_bp.to_numpy()

    def test_to_file(self):
        # # Test to_file(filename)
        poly_to_file = Polynomial(terms_qubo)
        poly_to_file.to_file(data_path + "test_poly.out")
        self.assertTrue(os.path.isfile(data_path + "test_poly.out"))

        invalid_to_file = Polynomial(terms_bp)
        with self.assertRaises(Exception):
            invalid_to_file.to_file(data_path + "test_poly_invalid.out")

    def test_to_azure_terms(self):
        poly_to_azure_terms = Polynomial(terms_bp)
        azure_terms = poly_to_azure_terms.to_azure_terms()

        expected_terms = [
            Term(c=3.0, indices=[1]),
            Term(c=1.0, indices=[2, 3, 4]),
            Term(c=2.0, indices=[]),
        ]

        self.assertEqual(azure_terms, expected_terms)

    def test_to_azure_terms_constant(self):
        poly_to_azure_terms = Polynomial(terms_degree_zero)
        azure_terms = poly_to_azure_terms.to_azure_terms()

        expected_terms = [Term(c=2.0, indices=[])]

        self.assertEqual(azure_terms, expected_terms)

    def test_to_azure_terms_constant_false(self):
        poly_to_azure_terms = Polynomial(terms_degree_zero)
        azure_terms = poly_to_azure_terms.to_azure_terms(include_constant_term=False)

        expected_terms = []

        self.assertEqual(azure_terms, expected_terms)

    def test_to_azure_terms_constant_rounding_up(self):
        constant_rounding_terms = [[3.5, [1, 2]]]

        poly_to_azure_terms = Polynomial(constant_rounding_terms)
        azure_terms = poly_to_azure_terms.to_azure_terms(rounding=True)

        expected_terms = [Term(c=4.0, indices=[1, 2])]

        self.assertEqual(azure_terms, expected_terms)

    def test_to_azure_terms_constant_rounding_down(self):
        constant_rounding_terms = [[2.5, [1, 2]]]

        poly_to_azure_terms = Polynomial(constant_rounding_terms)
        azure_terms = poly_to_azure_terms.to_azure_terms(rounding=True)

        # Rounding values of 0.5 will round to nearest even integer
        expected_terms = [Term(c=2.0, indices=[1, 2])]

        self.assertEqual(azure_terms, expected_terms)

    def test_to_azure_terms_empty(self):
        poly_to_azure_terms = Polynomial(empty_term)
        azure_terms = poly_to_azure_terms.to_azure_terms()

        expected_terms = []

        self.assertEqual(azure_terms, expected_terms)

    def test_to_azure_term(self):
        class TestMonomial:
            var_list = [1, 2]
            coefficient = 2

        monomial = TestMonomial()
        poly = Polynomial(empty_term)
        single_term = poly.to_azure_term(monomial)

        expected_term = Term(c=2.0, indices=[1, 2])

        self.assertEqual(single_term, expected_term)

    def test_to_azure_term_rounding_down(self):
        class TestMonomial:
            var_list = [1, 2]
            coefficient = 2.5

        monomial = TestMonomial()
        poly = Polynomial(empty_term)
        single_term = poly.to_azure_term(monomial, rounding=True)

        # Rounding values of 0.5 will round to nearest even integer
        expected_term = Term(c=2.0, indices=[1, 2])

        self.assertEqual(single_term, expected_term)

    def test_to_azure_term_rounding_up(self):
        class TestMonomial:
            var_list = [1, 2]
            coefficient = 3.5

        monomial = TestMonomial()
        poly = Polynomial(empty_term)
        single_term = poly.to_azure_term(monomial, rounding=True)

        expected_term = Term(c=4.0, indices=[1, 2])

        self.assertEqual(single_term, expected_term)

    def test_power(self):
        # squaring large linear poly
        large_poly.power(2)
        self.assertEqual(large_poly.degree, 2)

        # squaring qubo gives bp
        terms_qubo2 = [[2, [1, 3]], [10, []], [2, [4]]]
        client_poly = Polynomial(terms_qubo2)
        self.assertEqual(client_poly.degree, 2)
        client_poly.power(2)  # 8 x_1 x_3 x_4 + 44 x_1 x_3 + 100 + 44 x_4
        self.assertTrue(
            isAnagram(
                client_poly.to_string(), "8 x_1 x_3 x_4 + 44 x_1 x_3 + 100 + 44 x_4"
            )
        )
        self.assertEqual(client_poly.degree, 3)

    def test_multiply_poly(self):
        # oneqloud polynomials required conversion of qubo to bp to perform this
        client_poly_linear1 = Polynomial(terms_linear1)
        client_poly_linear2 = Polynomial(terms_linear2)
        client_poly_linear1.multiply(client_poly_linear2)
        self.assertTrue(
            isAnagram(
                client_poly_linear1.to_string(), "30 + 12 x_1 + 15 x_2 + 6 x_1 x_2"
            )
        )
        self.assertEqual(client_poly_linear1.degree, 2)

    def test_multiply_constant(self):
        # internally uses qbp or bp depending on degree and threshold
        ## qbp
        large_poly.multiply(10)
        self.assertEqual(large_poly.degree, 1)
        ## bp
        client_poly1 = Polynomial(terms_bp)  #  3 x_1 + 2 + x_2 x_3 x_4
        client_poly1.multiply(10)
        self.assertTrue(
            isAnagram(client_poly1.to_string(), "30 x_1 + 20 + 10 x_2 x_3 x_4")
        )
        self.assertEqual(client_poly1.degree, 3)

    def test_reduce_true(self):
        poly = Polynomial(Terms_and_known_solution["Terms"])
        poly1 = Polynomial(Terms_and_known_solution["Terms"], reduce=True)
        poly1._reduce()
        self.assertEqual(
            poly1._processed_portion, Terms_and_known_solution["Processed"]
        )

    def test_reduce_false(self):
        poly = Polynomial(terms=terms_reduce)
        poly2 = Polynomial(terms=terms_reduce)  # reduce = False by default
        poly2._reduce()
        self.assertEqual(poly, poly2)
        self.assertEqual(len(poly2._processed_portion), 0)

    def test_reduce_warn(self):
        poly = Polynomial(terms=terms_bp)
        poly1 = Polynomial(terms=terms_bp, reduce=True)
        with self.assertWarns(UserWarning):
            poly1._reduce()
        self.assertEqual(poly, poly1)
        self.assertEqual(len(poly1._processed_portion), 0)

        poly_0 = Polynomial(terms=terms_degree_zero)
        poly2 = Polynomial(terms=terms_degree_zero, reduce=True)
        with self.assertWarns(UserWarning):
            poly2._reduce()

    def test_stored_state(self):
        poly = Polynomial(terms=terms_bp)
        poly._stored_state("test_tag")
        self.assertEqual(poly._stored, "test_tag")

        poly_to_add = Polynomial(terms=terms_bp)
        poly.sum(poly_to_add)
        self.assertEqual(poly._stored, None)

    def test_python_internal(self):
        poly = Polynomial(terms=terms_bp)
        poly_constant = Polynomial(terms=terms_degree_zero)
        poly_to_add = Polynomial(terms=terms_bp)
        new_poly = poly + poly_to_add
        mul_poly = poly_to_add * 2
        constant_added_poly = new_poly + 2
        subtracted_poly = new_poly - 2
        power_poly = poly_constant**3

        self.assertEqual(poly, poly_to_add)
        self.assertEqual(new_poly.constant_term, 4)
        self.assertEqual(constant_added_poly.constant_term, 6)
        self.assertEqual(subtracted_poly.constant_term, 2)
        self.assertEqual(power_poly.constant_term, 8)

    def test_reduce_true(self):
        poly = Polynomial(terms=terms_reduce)
        poly1 = Polynomial(terms=terms_reduce, reduce=True)
        poly1._reduce()
        self.assertTrue(poly != poly1)
        self.assertTrue(len(poly1._processed_portion) != 0)

    def test_reduce_false(self):
        poly = Polynomial(terms=terms_reduce)
        poly2 = Polynomial(terms=terms_reduce)  # reduce = False by default
        poly2._reduce()
        self.assertTrue(poly == poly2)
        self.assertTrue(len(poly2._processed_portion) == 0)
