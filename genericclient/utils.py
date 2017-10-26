from posixpath import join

from . import exceptions


def urljoin(base, parts, trail=False):
    _trail = '/' if trail else ''
    url = base
    if not url.endswith('/'):
        url += '/'
    return join(url, *map(str, parts)) + _trail


def find_pk(kwargs):
    for key in ('id', 'uuid', 'pk', 'slug', 'username'):
        if key in kwargs:
            return kwargs[key]

    raise exceptions.UnknownPK("Can't find suitable pk in `{!r}`".format(kwargs))
