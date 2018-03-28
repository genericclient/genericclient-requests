from unittest import TestCase

from genericclient import GenericClient
import responses


MOCK_API_URL = 'http://dummy.org'


class AuthClientTestCase(TestCase):
    def test_403(self):
        generic_client = GenericClient(
            url=MOCK_API_URL,
        )
        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, MOCK_API_URL + '/users', status=403)
            with self.assertRaises(generic_client.NotAuthenticatedError):
                generic_client.users.all()


    def test_403_auth(self):
        generic_client = GenericClient(
            url=MOCK_API_URL,
            auth=('myusername', 'password'),
        )
        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, MOCK_API_URL + '/users', status=403)
            with self.assertRaises(generic_client.NotAuthenticatedError) as excinfo:
                generic_client.users.all()

            assert 'myusername' in str(excinfo.exception)
