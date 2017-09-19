try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

import requests

from . import exceptions


_version = "0.0.16"
__version__ = VERSION = tuple(map(int, _version.split('.')))


AmbiguousComparison = exceptions.AmbiguousComparison
MultipleResourcesFound = exceptions.MultipleResourcesFound
ResourceNotFound = exceptions.ResourceNotFound
HTTPError = exceptions.HTTPError
NotAuthenticatedError = exceptions.NotAuthenticatedError
BadRequestError = exceptions.BadRequestError


def hydrate_json(response):
    try:
        return response.json()
    except ValueError:
        raise ValueError(
            "Response from server is not valid JSON. Received {}: {}".format(
                response.status_code,
                response.text,
            ),
        )


def _urljoin(base, parts, trail=False):
    _trail = '/' if trail else ''
    url = base
    if not url.endswith('/'):
        url += '/'
    return urljoin(url, *map(str, parts)) + _trail


class Resource(object):
    whitelist = (
        '__class__',
        '_endpoint',
        'payload',
        'save',
        'delete',
        '_urljoin',
    )

    def __init__(self, endpoint, **kwargs):
        self._endpoint = endpoint
        self.payload = kwargs

        super(Resource, self).__init__()

    def __setattr__(self, name, value):
        if name == 'whitelist' or name in self.whitelist:
            return super(Resource, self).__setattr__(name, value)
        if isinstance(value, self.__class__) and hasattr(value, 'pk'):
            value = value.pk
        self.payload[name] = value

    def __getattr__(self, name):
        if name not in self.payload:
            raise AttributeError("Resource on endpoint `{}` has not attribute '{}'".format(
                self._endpoint.name,
                name,
            ))
        return self.payload[name]

    def __repr__(self):
        return '<Resource `{0}` {}: {1}>'.format(self._endpoint.name, self.pk_name, self.pk)

    def __eq__(self, other):
        if self.payload != other.payload and self.pk == other.pk:
            raise AmbiguousComparison(
                "Payloads are different, but {}:{} is the same.".format(
                    self.pk_name, self.pk
                )
            )
        return self.payload == other.payload

    @property
    def pk_name(self):
        pk_name = None
        if 'id' in self.payload:
            pk_name = 'id'
        elif 'uuid' in self.payload:
            pk_name = 'uuid'
        return pk_name

    @property
    def pk(self):
        if self.pk_name is not None:
            return self.payload.get(self.pk_name)
        return None

    def _urljoin(self, *parts):
        return _urljoin(self._endpoint.url, parts, self._endpoint.trail)

    def save(self):
        if self.pk is not None:
            url = self._urljoin(self.pk)
            try:
                response = self._endpoint.request('put', url, json=self.payload)
            except exceptions.BadRequestError:
                response = self._endpoint.request('patch', url, json=self.payload)
            results = hydrate_json(response)
        else:
            response = self._endpoint.request('post', url, json=self.payload)
            results = hydrate_json(response)
        self.payload = results
        return self

    def delete(self):
        url = self._urljoin(self.pk)
        self._endpoint.request('delete', url)


class Endpoint(object):

    def __init__(self, api, name):
        self.api = api
        self.name = name
        self.trail = '/' if self.api.trailing_slash else ''
        self.url = "{}{}{}".format(self.api.url, name, self.trail)

        super(Endpoint, self).__init__()

    def _urljoin(self, *parts):
        return _urljoin(self.url, parts, self.trail)

    def filter(self, **kwargs):
        response = self.request('get', self.url, params=kwargs)
        results = hydrate_json(response)
        return [Resource(self, **result) for result in results]

    def all(self):
        return self.filter()

    def get(self, **kwargs):
        if 'id' in kwargs:
            url = self._urljoin(kwargs['id'])
            response = self.request('get', url)
        elif 'uuid' in kwargs:
            url = self._urljoin(kwargs['uuid'])
            response = self.request('get', url)
        elif 'pk' in kwargs:
            url = self._urljoin(kwargs['pk'])
            response = self.request('get', url)
        elif 'slug' in kwargs:
            url = self._urljoin(kwargs['slug'])
            response = self.request('get', url)
        elif 'username' in kwargs:
            url = self._urljoin(kwargs['username'])
            response = self.request('get', url)
        else:
            url = self.url
            response = self.request('get', url, params=kwargs)

        if response.status_code == 404:
            raise exceptions.ResourceNotFound("No `{}` found for {}".format(self.name, kwargs))

        result = hydrate_json(response)

        if isinstance(result, list):
            if len(result) == 0:
                raise exceptions.ResourceNotFound("No `{}` found for {}".format(self.name, kwargs))
            if len(result) > 1:
                raise exceptions.MultipleResourcesFound("Found {} `{}` for {}".format(len(result), self.name, kwargs))

            return Resource(self, **result[0])

        return Resource(self, **result)

    def create(self, payload):
        response = self.request('post', self.url, json=payload)
        if response.status_code != 201:
            raise exceptions.HTTPError(response)

        result = hydrate_json(response)
        return Resource(self, **result)

    def get_or_create(self, **kwargs):
        defaults = kwargs.pop('defaults', {})
        try:
            resource = self.get(**kwargs)
            return resource
        except ResourceNotFound:
            params = {k: v for k, v in kwargs.items()}
            params.update(defaults)
            return self.create(params)

    def create_or_update(self, payload):
        if 'id' in payload or 'uuid' in payload:
            return Resource(self, **payload).save()

        return self.create(payload)

    def delete(self, pk):
        url = self._urljoin(pk)

        response = self.request('delete', url)

        if response.status_code != 204:
            raise exceptions.HTTPError(response)

        return None

    def request(self, method, *args, **kwargs):
        response = getattr(self.api.session, method)(*args, **kwargs)

        if response.status_code == 403:
            raise exceptions.NotAuthenticatedError(response, "Cannot authenticate user `{}` on the API".format(self.api.session.auth[0]))
        elif response.status_code == 400:
            raise exceptions.BadRequestError(
                response,
                "Bad Request 400: {}".format(response.text)
            )
        return response

    def __repr__(self):
        return "<Endpoint `{}`>".format(self.url)


class GenericClient(object):
    endpoint_class = Endpoint

    MultipleResourcesFound = MultipleResourcesFound
    ResourceNotFound = ResourceNotFound
    HTTPError = HTTPError
    NotAuthenticatedError = NotAuthenticatedError
    BadRequestError = BadRequestError

    def __init__(self, url, auth=None, adapter=None, trailing_slash=False):
        self.session = requests.session()
        self.session.headers.update({'Content-Type': 'application/json'})
        if auth is not None:
            self.session.auth = auth
        if not url.endswith('/'):
            url = '{}/'.format(url)
        self.url = url
        self.trailing_slash = trailing_slash

        if adapter is not None:
            self.session.mount(url, adapter())

        super(GenericClient, self).__init__()

    def __getattr__(self, name):
        return self.endpoint_class(self, name)
