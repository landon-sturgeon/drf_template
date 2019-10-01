from django.test import TestCase

from .calc import add, subtract


class CalcTests(TestCase):
    """Generic test class for testing the calculators methods."""

    def test_add_numbers(self):
        """Test that two numbers are added together.

        :return: None
        :raises AssertionError: exception if addition results are wrong
        """
        self.assertEqual(add(3, 8), 11)

    def test_subtract_numbers(self):
        """Test that two numbers are subtracted from each other.

        :return: None
        :raises AssertionError: exception if subtraction is wrong
        """
        self.assertEqual(subtract(8, 3), 5)
