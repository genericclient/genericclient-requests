from unittest import TestCase

from genericclient import utils


class UtilsTestCase(TestCase):

    def test_urljoin(self):
        url = utils.urljoin(
            'http://example.com',
            ['users', 2],
            trail=True
        )
        self.assertEqual(url, 'http://example.com/users/2/')

        url = utils.urljoin(
            'http://example.com',
            ['users', 2],
            trail=False
        )
        self.assertEqual(url, 'http://example.com/users/2')

        url = utils.urljoin(
            'http://example.com/',
            ['users', 2],
            trail=True
        )
        self.assertEqual(url, 'http://example.com/users/2/')

        url = utils.urljoin(
            'http://example.com/users',
            [2, 'notify'],
            trail=True
        )
        self.assertEqual(url, 'http://example.com/users/2/notify/')
