from unittest import TestCase

import responses

from genericclient import GenericClient
from genericclient_base.pagination import link_header


MOCK_API_URL = 'http://dummy.org'

generic_client = GenericClient(url=MOCK_API_URL, autopaginate=link_header)


class EndpointTestCase(TestCase):
    def test_paginate(self):
        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, MOCK_API_URL + '/users', json=[
                {'id': 1},
            ], headers={
                'link': '<' + MOCK_API_URL + '/users?page=2>; rel=next',
            }, match_querystring=True)
            rsps.add(responses.GET, MOCK_API_URL + '/users?page=2', json=[
                {'id': 2},
            ], headers={
                'link': '<' + MOCK_API_URL + '/users>; rel=previous, <' + MOCK_API_URL + '/users?page=3>; rel=next',
            }, match_querystring=True)
            rsps.add(responses.GET, MOCK_API_URL + '/users?page=3', json=[
                {'id': 3},
            ], headers={
                'link': '<' + MOCK_API_URL + '/users?page=2>; rel=previous',
            }, match_querystring=True)

            users = generic_client.users.all()
            self.assertEqual(len(users), 3)
            self.assertEqual(users[0].id, 1)
            self.assertEqual(users[1].id, 2)
            self.assertEqual(users[2].id, 3)
