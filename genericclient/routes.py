from . import utils


class Action(object):

    def __init__(self, _endpoint, name, **lookup):
        self.name = name
        self.lookup = lookup
        self._endpoint = _endpoint
        self.trail = self._endpoint.trail
        self.url = utils.urljoin(self._endpoint.url, [self.pk, name], self.trail)
        super(Action, self).__init__()

    @property
    def pk(self):
        return utils.find_pk(self.lookup)

    def __call__(self, **kwargs):
        return self._endpoint.request('post', self.url, json=kwargs)

    def __repr__(self):
        return '<{0} `{1}` on {2} with lookup `{3!r}`>'.format(
            self.__class__.__name__, self.name, self.url, self.pk,
        )

    def _urljoin(self, *parts):
        return utils.urljoin(self._endpoint.url, parts, self.trail)


class DetailRoute(object):
    action_class = Action
    whitelist = (
        'action_class',
        '__class__',
        '_endpoint',
        'lookup',
    )

    def __init__(self, endpoint, **kwargs):
        self._endpoint = endpoint
        self.lookup = kwargs

        super(DetailRoute, self).__init__()

    def __setattr__(self, name, value):
        if name == 'whitelist' or name in self.whitelist:
            return super(DetailRoute, self).__setattr__(name, value)
        self.lookup[name] = value

    def __getattr__(self, name):
        return self.action_class(self._endpoint, name, **self.lookup)

    def __repr__(self):
        return '<{0} on `{}` with lookup `{1!r}`>'.format(
            self.__class__.__name__, self._endpoint.url, self.lookup,
        )
