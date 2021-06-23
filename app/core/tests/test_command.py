from unittest.mock import patch

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import TestCase

# Mocking is used to isolate the specific code to be tested and to avoid unintended consequences of running your unit tests
class CommandTests(TestCase):

    # creating Mock Test_Case to wait for DB
    def test_wait_for_db_ready(self):
        """Test waiting for db When db is available"""

        # Our management command is going to basically try and retrieve the database connection from Django and it's
        # going to check if when we try and retrieve it it retrieves an operational error or not.
        # So if it retrieves an operational error then the database is not available.
        # If an operational error is not thrown, then the database is available and the command will continue.
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:  # overriding ConnectionHandler and return 'True' every time it calls and connect without error
            gi.return_value = True
            call_command('wait_for_db')
            self.assertEqual(gi.call_count, 1)

    def test_wait_for_db(self):
        """Test waiting for db"""
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            gi.side_effect = [OperationalError] * 5 + [True]
            call_command('wait_for_db')
            self.assertEqual(gi.call_count, 6)
