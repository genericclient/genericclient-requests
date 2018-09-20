import requests

from genericclient_base import (
    BaseEndpoint, BaseGenericClient, BaseResource, exceptions, ParsedResponse
)


_version = "1.3.0"
__version__ = VERSION = tuple(map(int, _version.split('.')))


class Resource(BaseResource):
    pass


class Endpoint(BaseEndpoint):
    resource_class = Resource

    def request(self, method, url, *args, **kwargs):
        resp = getattr(self.api.session, method)(url, *args, **kwargs)
        response = ParsedResponse(
            status_code=resp.status_code,
            headers=resp.headers,
            data=self.api.hydrate_data(resp),
        )

        if response.status_code == 403:
            if self.api.session.auth:
                msg = "Failed request to `{}`. Cannot authenticate user `{}` on the API.".format(
                    url, self.api.session.auth[0],
                )
            else:
                msg = "Failed request to `{}`. User is not authenticated.".format(
                    url,
                )

            raise exceptions.NotAuthenticatedError(
                response, msg,
            )
        elif response.status_code == 400:
            raise exceptions.BadRequestError(
                response,
                "Bad Request 400: {}".format(response.data)
            )
        return response


class GenericClient(BaseGenericClient):
    endpoint_class = Endpoint

    def __init__(self, url, auth=None, session=None, adapter=None, trailing_slash=False, autopaginate=None):
        super(GenericClient, self).__init__(url, auth, session, trailing_slash, autopaginate)
        self.adapter = adapter

    def make_session(self):
        session = requests.session()
        if self.auth is not None:
            session.auth = self.auth
        session.headers.update({'Content-Type': 'application/json'})
        if self.adapter is not None:
            session.mount(self.url, self.adapter())
        return session

    def hydrate_data(self, response):
        if not response.text:
            return None
        try:
            return response.json()
        except ValueError:
            raise ValueError(
                "Response from server is not valid JSON. Received {}: {}".format(
                    response.status_code,
                    response.text,
                ),
            )
