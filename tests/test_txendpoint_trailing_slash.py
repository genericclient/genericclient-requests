from unittest import TestCase

import responses

from requests_threads import AsyncSession
from twisted.internet.defer import inlineCallbacks
from twisted.internet import threads

from genericclient import GenericClient


MOCK_API_URL = 'http://dummy.org'

session = AsyncSession(n=100)
generic_client = GenericClient(url=MOCK_API_URL, trailing_slash=True, session=session)


# Create your tests here.
class EndpointTestCase(TestCase):

    def test_endpoint_all(self):
        @inlineCallbacks
        def f(*args):
            with responses.RequestsMock() as rsps:
                rsps.add(responses.GET, MOCK_API_URL + '/users/', json=[
                    {
                        'id': 1,
                        'username': 'user1',
                        'group': 'watchers',
                    },
                    {
                        'id': 2,
                        'username': 'user2',
                        'group': 'watchers',
                    },
                    {
                        'id': 3,
                        'username': 'user3',
                        'group': 'admin',
                    },
                ])

                users = yield generic_client.users.all()
                self.assertEqual(len(users), 3)
        threads.deferToThread(f)

    def test_endpoint_filter(self):
        @inlineCallbacks
        def f(*args):
            with responses.RequestsMock() as rsps:
                rsps.add(responses.GET, MOCK_API_URL + '/users/', json=[
                    {
                        'id': 1,
                        'username': 'user1',
                        'group': 'watchers',
                    },
                    {
                        'id': 2,
                        'username': 'user2',
                        'group': 'watchers',
                    },
                ])

                users = yield generic_client.users.filter(group="watchers")
                self.assertEqual(len(users), 2)
        threads.deferToThread(f)

    def test_endpoint_get_id(self):
        @inlineCallbacks
        def f(*args):
            with responses.RequestsMock() as rsps:
                rsps.add(responses.GET, MOCK_API_URL + '/users/2/', json={
                    'id': 2,
                    'username': 'user2',
                    'group': 'watchers',
                })

                user2 = yield generic_client.users.get(id=2)
                self.assertEqual(user2.username, 'user2')

            with responses.RequestsMock() as rsps:
                rsps.add(responses.GET, MOCK_API_URL + '/users/9999/', status=404)

                self.assertRaises(generic_client.ResourceNotFound, generic_client.users.get, id=9999)
        threads.deferToThread(f)

    def test_endpoint_get_params(self):
        @inlineCallbacks
        def f(*args):
            with responses.RequestsMock() as rsps:
                rsps.add(responses.GET, MOCK_API_URL + '/users/', json=[
                    {
                        'id': 1,
                        'username': 'user1',
                        'group': 'watchers',
                    },
                    {
                        'id': 2,
                        'username': 'user2',
                        'group': 'watchers',
                    },
                ])

                self.assertRaises(generic_client.MultipleResourcesFound, generic_client.users.get, group='watchers')

            with responses.RequestsMock() as rsps:
                rsps.add(responses.GET, MOCK_API_URL + '/users/', body='[]')

                self.assertRaises(generic_client.ResourceNotFound, generic_client.users.get, group='cookie_monster')

            with responses.RequestsMock() as rsps:
                rsps.add(responses.GET, MOCK_API_URL + '/users/', json=[
                    {
                        'id': 3,
                        'username': 'user3',
                        'group': 'admin',
                    },
                ])

                admin = yield generic_client.users.get(role='admin')
                self.assertEqual(admin.username, 'user3')
        threads.deferToThread(f)
