from unittest import TestCase

import responses

from requests_threads import AsyncSession
from twisted.internet.defer import inlineCallbacks
from twisted.internet import threads
from genericclient import GenericClient


MOCK_API_URL = 'http://dummy.org'

session = AsyncSession(n=100)
generic_client = GenericClient(url=MOCK_API_URL, session=session, trailing_slash=True)


# Create your tests here.
class ResourceTestCase(TestCase):

    def test_resource_delete(self):
        @inlineCallbacks
        def f(*args):
            with responses.RequestsMock() as rsps:
                rsps.add(responses.GET, MOCK_API_URL + '/users/1/', json={
                    'id': 1,
                    'username': 'user1',
                    'group': 'watchers',
                })

                user1 = yield generic_client.users.get(id=1)
                self.assertEqual(user1.username, 'user1')

            with responses.RequestsMock() as rsps:
                rsps.add(responses.DELETE, MOCK_API_URL + '/users/1/', status=204)

                yield user1.delete()
        threads.deferToThread(f)

    def test_resource_save(self):
        @inlineCallbacks
        def f(*args):
            with responses.RequestsMock() as rsps:
                rsps.add(responses.GET, MOCK_API_URL + '/users/1/', json={
                    'id': 1,
                    'username': 'user1',
                    'group': 'watchers',
                })

                user1 = yield generic_client.users.get(id=1)
                self.assertEqual(user1.username, 'user1')

            with responses.RequestsMock() as rsps:
                rsps.add(responses.PUT, MOCK_API_URL + '/users/1/', json={
                    'id': 1,
                    'username': 'user1',
                    'group': 'admins',
                })

                user1.group = 'admins'
                yield user1.save()
        threads.deferToThread(f)
