from unittest import TestCase

import responses

from genericclient import GenericClient


class RequestClientTestCase(TestCase):

    def test_host(self):
        client = GenericClient(url='http://dummy.org')
        self.assertEqual(client.host, 'dummy.org')

        client = GenericClient(url='http://dummy.org:8000')
        self.assertEqual(client.host, 'dummy.org:8000')

        client = GenericClient(url='http://dummy.org:8000/api')
        self.assertEqual(client.host, 'dummy.org:8000')

        client = GenericClient(url='http://dummy.org/api')
        self.assertEqual(client.host, 'dummy.org')

    def test_session(self):
        client = GenericClient(url='http://dummy.org', auth=('username', 'password'))
        self.assertEqual(client.session.auth[0], 'username')

    def test_invalid_data(self):
        client = GenericClient(url='http://dummy.org')
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                'http://dummy.org/users',
                body='[not json]',
                headers={'Content-Type': 'application/json'},
            )

            with self.assertRaises(ValueError) as excinfo:
                client.users.all()

            assert '[not json]' in str(excinfo.exception)
