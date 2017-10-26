from unittest import TestCase

from genericclient import GenericClient


class EndpointTestCase(TestCase):

    def test_host(self):
        client = GenericClient(url='http://dummy.org')
        self.assertEqual(client.host, 'dummy.org')

        client = GenericClient(url='http://dummy.org:8000')
        self.assertEqual(client.host, 'dummy.org:8000')

        client = GenericClient(url='http://dummy.org:8000/api')
        self.assertEqual(client.host, 'dummy.org:8000')

        client = GenericClient(url='http://dummy.org/api')
        self.assertEqual(client.host, 'dummy.org')
