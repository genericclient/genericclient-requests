from unittest import TestCase

import responses

from genericclient import GenericClient


MOCK_API_URL = 'http://dummy.org'

generic_client = GenericClient(url=MOCK_API_URL, trailing_slash=True)


# Create your tests here.
class EndpointTestCase(TestCase):

    def test_endpoint_all(self):
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

            users = generic_client.users.all()
            self.assertEqual(len(users), 3)

    def test_endpoint_filter(self):
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

            users = generic_client.users.filter(group="watchers")
            self.assertEqual(len(users), 2)

        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, MOCK_API_URL + '/users/?group__in=watchers&group__in=contributors', json=[
                {
                    'id': 1,
                    'username': 'user1',
                    'group': 'watchers',
                },
                {
                    'id': 2,
                    'username': 'user2',
                    'group': 'contributors',
                },
            ], match_querystring=True)

            users = generic_client.users.filter(group__in=["watchers", "contributors"])
            self.assertEqual(len(users), 2)

    def test_endpoint_links(self):
        with responses.RequestsMock() as rsps:
            rsps.add('GET', MOCK_API_URL + '/users/?page=2', json=[
                {
                    'id': 3,
                    'username': 'user1',
                    'group': 'watchers',
                },
                {
                    'id': 4,
                    'username': 'user2',
                    'group': 'watchers',
                },
            ], match_querystring=True, headers={
                'Link': '<http://example.com/users/?page=3>; rel=next,<http://example.com/users/?page=1>; rel=previous'
            })

            users = generic_client.users.filter(page=2)
            self.assertEqual(users.response.links, {
                'next': {'url': 'http://example.com/users/?page=3', 'rel': 'next'},
                'previous': {'url': 'http://example.com/users/?page=1', 'rel': 'previous'}
            })

    def test_endpoint_get_id(self):
        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, MOCK_API_URL + '/users/2/', json={
                'id': 2,
                'username': 'user2',
                'group': 'watchers',
            })

            user2 = generic_client.users.get(id=2)
            self.assertEqual(user2.username, 'user2')

        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, MOCK_API_URL + '/users/9999/', status=404)

            self.assertRaises(generic_client.ResourceNotFound, generic_client.users.get, id=9999)

    def test_endpoint_get_params(self):
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

            admin = generic_client.users.get(role='admin')
            self.assertEqual(admin.username, 'user3')
