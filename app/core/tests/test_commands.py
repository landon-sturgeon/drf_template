"""Package containing the tests for the django manager commands."""

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import TestCase
from unittest.mock import patch


class CommandTests(TestCase):
    """Test class for testing the python manager commands."""

    def test_wait_for_db_read(self):
        """Test waiting for db when db is available.

        :return: None
        :raises AssertionError: connection call exceeds more than one
        """
        with patch("django.db.utils.ConnectionHandler.__getitem__") as gi:
            gi.return_value = True
            call_command("wait_for_db")

            self.assertEqual(gi.call_count, 1)

    @patch("time.sleep", return_value=True)
    def test_wait_for_db(self, ts):
        """Test waiting for db.

        The patch decorator just removes the actual time we have for waiting
        until the next connection attempt, making the unittest run faster.

        The patch decorator basically creates a variable within the scope of
        this function who's value is set equal to 'True'.

        :param ts: (not used) mocked time delay for the wait time in db connect
        :return: None
        :raises AssertionError: db wait time doesn't match test delay time
        :raises OperationError: known error for when the db can't connect
        """
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            # purely for linting...
            side_effect_list = [OperationalError] * 5
            side_effect_list += [True]

            gi.side_effect = side_effect_list
            call_command('wait_for_db')
            self.assertEqual(gi.call_count, 6)
