"""
Sample tests

"""

from django.test import SimpleTestCase

from app import calc


class CalcTests(SimpleTestCase):

    def test_add_numbers(self):
        res = calc.add(1,2)

        self.assertEqual(res,3)

    def test_sub_numbers(self):
        res = calc.sub(15,10)

        self.assertEqual(res, 5)


