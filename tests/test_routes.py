from unittest import TestCase

import responses

from genericclient import GenericClient


MOCK_API_URL = 'http://dummy.org'

generic_client = GenericClient(url=MOCK_API_URL)


class EndpointTestCase(TestCase):

    def test_endpoint_detail_route(self):
        with responses.RequestsMock() as rsps:
            def request_callback(request):
                return (200, {}, request.body)

            rsps.add_callback(
                responses.POST, MOCK_API_URL + '/users/2/notify',
                callback=request_callback,
                content_type='application/json',
            )

            response = generic_client.users.detail(id=2).notify(unread=3)
            self.assertEqual(response.json(), {'unread': 3})
