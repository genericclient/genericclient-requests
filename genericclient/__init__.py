import requests

from . import exceptions


_version = "0.0.2"
__version__ = VERSION = tuple(map(int, _version.split('.')))


class Resource(object):
    whitelist = (
        '__class__',
        '_endpoint',
        'payload',
        'save',
        'delete',
    )

    def __init__(self, endpoint, **kwargs):
        self._endpoint = endpoint
        self.payload = kwargs

        super(Resource, self).__init__()

    def __setattr__(self, name, value):
        if name == 'whitelist' or name in self.whitelist:
            return super(Resource, self).__setattr__(name, value)
        self.payload[name] = value

    def __getattribute__(self, name):
        if name == 'whitelist' or name in self.whitelist:
            return super(Resource, self).__getattribute__(name)
        return self.payload[name]

    def save(self):
        url = self._endpoint.url
        if 'id' in self.payload:
            url += self.payload['id'] + self.endpoint.trail
            response = self._endpoint.request('put', url, json=self.payload)
            results = response.json()
        else:
            response = self._endpoint.request('post', url, json=self.payload)
            results = response.json()
        self.payload = results

    def delete(self):
        url = self._endpoint.url + self.payload['id'] + self.endpoint.trail
        self._endpoint.request('delete', url)

    def __repr__(self):
        try:
            pk = self.id
        except AttributeError:
            pk = None
        return '<Resource `{0}` id: {1}>'.format(self._endpoint.name, pk)


class Endpoint(object):
    def __init__(self, api, name):
        self.api = api
        self.name = name
        self.trail = '/' if self.api.trailing_slash else ''
        self.endpoint = '%s%s' % (name, self.trail)
        self.url = self.api.url + self.endpoint

        super(Endpoint, self).__init__()

    def filter(self, **kwargs):
        response = self.request('get', self.url, params=kwargs)
        results = response.json()
        return [Resource(self, **result) for result in results]

    def all(self):
        return self.filter()

    def get(self, **kwargs):
        if 'id' in kwargs:
            url = "{0}{1}{2}".format(self.url, kwargs['id'], self.trail)
            response = self.request('get', url)
        elif 'pk' in kwargs:
            url = "{0}{1}{2}".format(self.url, kwargs['pk'], self.trail)
            response = self.request('get', url)
        elif 'slug' in kwargs:
            url = "{0}{1}{2}".format(self.url, kwargs['slug'], self.trail)
            response = self.request('get', url)
        elif 'username' in kwargs:
            url = "{0}{1}{2}".format(self.url, kwargs['username'], self.trail)
            response = self.request('get', url)
        else:
            url = self.url
            response = self.request('get', url, params=kwargs)

        if response.status_code == 404:
            raise exceptions.ResourceNotFound("No `{}` found for {}".format(self.name, kwargs))

        result = response.json()

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

        result = response.json()
        return Resource(self, **result)

    def create_or_update(self, payload):
        if 'id' in payload:
            return Resource(self, **payload).save()

        return self.create(payload)

    def delete(self, pk):
        url = "{}{}/".format(self.url, pk)

        response = self.request('delete', url)

        if response.status_code != 204:
            raise exceptions.HTTPError(response)

        return None

    def request(self, method, *args, **kwargs):
        response = getattr(self.api.session, method)(*args, **kwargs)

        if response.status_code == 403:
            raise exceptions.NotAuthenticatedError(response, "Cannot authenticate user `{}` on the API".format(self.api.session.auth[0]))
        return response

    def __repr__(self):
        return "<Endpoint `{}`>".format(self.url)


class GenericClient(object):
    endpoint_class = Endpoint

    def __init__(self, url, auth=None, adapter=None, trailing_slash=False):
        self.session = requests.session()
        self.session.headers.update({'Content-Type': 'application/json'})
        if auth is not None:
            self.session.auth = auth
        if not url.endswith('/'):
            url += '/'
        self.url = url
        self.trailing_slash = trailing_slash

        if adapter is not None:
            self.session.mount(url, adapter())

        super(GenericClient, self).__init__()

    def __getattribute__(self, name):
        if name in ('session', 'url', 'endpoint_class', 'trailing_slash'):
            return super(GenericClient, self).__getattribute__(name)
        return self.endpoint_class(self, name)
