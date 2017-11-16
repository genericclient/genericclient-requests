from genericclient_base import utils


class Action(object):

    def __init__(self, endpoint, method, name):
        self.name = name
        self.endpoint = endpoint
        self.method = method
        self.trail = self.endpoint.trail
        self.url = utils.urljoin(self.endpoint.url, [name], self.trail)
        super(Action, self).__init__()

    def __call__(self, **kwargs):
        return self.endpoint.request(self.method, self.url, json=kwargs)

    def __repr__(self):
        return '<{0} `{1}` on {2}`>'.format(
            self.__class__.__name__, self.name, self.url,
        )

    def _urljoin(self, *parts):
        return utils.urljoin(self.endpoint.url, parts, self.trail)


class ListAction(Action):
    pass


class DetailAction(Action):

    def __init__(self, endpoint, method, name, **lookup):
        super(DetailAction, self).__init__(endpoint, method, name)
        self.lookup = lookup
        self.url = utils.urljoin(self.endpoint.url, [self.pk, name], self.trail)

    @property
    def pk(self):
        return utils.find_pk(self.lookup)

    def __repr__(self):
        return '<{0} `{1}` on {2} with lookup `{3!r}`>'.format(
            self.__class__.__name__, self.name, self.url, self.lookup,
        )


class Route(object):
    whitelist = (
        'action_class',
        '__class__',
        '_endpoint',
        '_lookup',
        '_method',
    )

    def __init__(self, endpoint, method):
        self._method = method
        self._endpoint = endpoint
        super(Route, self).__init__()

    def __setattr__(self, name, value):
        if name == 'whitelist' or name in self.whitelist:
            return super(Route, self).__setattr__(name, value)

    def __getattr__(self, name):
        return self.action_class(self._endpoint, self._method, name)

    def __repr__(self):
        return '<{0} on `{}`>'.format(
            self.__class__.__name__, self._endpoint.url,
        )


class ListRoute(Route):
    action_class = ListAction


class DetailRoute(Route):
    action_class = DetailAction

    def __init__(self, endpoint, method, **kwargs):
        super(DetailRoute, self).__init__(endpoint, method)
        self._lookup = kwargs

    def __getattr__(self, name):
        return self.action_class(self._endpoint, self._method, name, **self._lookup)

    def __repr__(self):
        return '<{0} on `{}` with lookup `{1!r}`>'.format(
            self.__class__.__name__, self._endpoint.url, self._lookup,
        )
