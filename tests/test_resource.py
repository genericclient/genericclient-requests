from unittest import TestCase

import responses

from genericclient import GenericClient


MOCK_API_URL = 'http://dummy.org'

generic_client = GenericClient(url=MOCK_API_URL)


# Create your tests here.
class ResourceTestCase(TestCase):

    def test_resource_delete(self):
        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, MOCK_API_URL + '/users/1', json={
                'id': 1,
                'username': 'user1',
                'group': 'watchers',
            })

            user1 = generic_client.users.get(id=1)
            self.assertEqual(user1.username, 'user1')

        with responses.RequestsMock() as rsps:
            rsps.add(responses.DELETE, MOCK_API_URL + '/users/1', status=204)

            user1.delete()

    def test_resource_delete_uuid(self):
        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, MOCK_API_URL + '/users/1', json={
                'uuid': 1,
                'username': 'user1',
                'group': 'watchers',
            })

            user1 = generic_client.users.get(uuid=1)
            self.assertEqual(user1.username, 'user1')

        with responses.RequestsMock() as rsps:
            rsps.add(responses.DELETE, MOCK_API_URL + '/users/1', status=204)

            user1.delete()

    def test_resource_save(self):
        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, MOCK_API_URL + '/users/1', json={
                'id': 1,
                'username': 'user1',
                'group': 'watchers',
            })

            user1 = generic_client.users.get(id=1)
            self.assertEqual(user1.username, 'user1')

        with responses.RequestsMock() as rsps:
            rsps.add(responses.PUT, MOCK_API_URL + '/users/1', json={
                'id': 1,
                'username': 'user1',
                'group': 'admins',
            })

            user1.group = 'admins'
            user1.save()

    def test_resource_save_uuid(self):
        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, MOCK_API_URL + '/users/1', json={
                'uuid': 1,
                'username': 'user1',
                'group': 'watchers',
            })

            user1 = generic_client.users.get(uuid=1)
            self.assertEqual(user1.username, 'user1')

        with responses.RequestsMock() as rsps:
            rsps.add(responses.PUT, MOCK_API_URL + '/users/1', json={
                'uuid': 1,
                'username': 'user1',
                'group': 'admins',
            })

            user1.group = 'admins'
            user1.save()
