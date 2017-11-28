import requests

from genericclient_base import BaseEndpoint, BaseGenericClient, BaseResource, exceptions


_version = "0.0.23"
__version__ = VERSION = tuple(map(int, _version.split('.')))


class Resource(BaseResource):
    def save(self):
        if self.pk is not None:
            url = self._urljoin(self.pk)
            try:
                response = self._endpoint.request('put', url, json=self.payload)
            except exceptions.BadRequestError:
                response = self._endpoint.request('patch', url, json=self.payload)
            results = self._endpoint.api.hydrate_json(response)
        else:
            response = self._endpoint.request('post', url, json=self.payload)
            results = self._endpoint.api.hydrate_json(response)
        self.payload = results
        return self

    def delete(self):
        url = self._urljoin(self.pk)
        self._endpoint.request('delete', url)


class Endpoint(BaseEndpoint):
    resource_class = Resource

    def request(self, method, url, *args, **kwargs):
        response = getattr(self.api.session, method)(url, *args, **kwargs)

        if self.status_code(response) == 403:
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
        elif self.status_code(response) == 400:
            raise exceptions.BadRequestError(
                response,
                "Bad Request 400: {}".format(response.text)
            )
        return response


class GenericClient(BaseGenericClient):
    endpoint_class = Endpoint

    def __init__(self, url, auth=None, session=None, adapter=None, trailing_slash=False):
        super(GenericClient, self).__init__(url, auth, session, trailing_slash)

        if adapter is not None:
            self.session.mount(url, adapter())

    def set_session(self, session, auth):
        if session is None:
            session = requests.session()
        if auth is not None:
            session.auth = auth
        session.headers.update({'Content-Type': 'application/json'})
        return session

    def hydrate_json(self, response):
        try:
            return response.json()
        except ValueError:
            raise ValueError(
                "Response from server is not valid JSON. Received {}: {}".format(
                    response.status_code,
                    response.text,
                ),
            )
