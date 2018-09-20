=============
genericclient
=============

.. image:: https://travis-ci.org/genericclient/genericclient-requests.svg?branch=master
    :target: https://travis-ci.org/genericclient/genericclient-requests

A generic client for RESTful APIs based on ``requests``.

For an async version based on ``aiohttp``, see `genericclient-aiohttp <https://github.com/genericclient/genericclient-aiohttp>`_ (Python 3.5+ only).

Installation
============

::

    $ pip install genericclient


Quickstart
==========

::

    from genericclient import GenericClient

    myclient = GenericClient(api_url)

    myresource = myclient.resources.get(id=1)

    actives = myclient.posts.filter(active=True)

Usage
=====

Instantiation
-------------

::

    myclient = GenericClient(url, auth=None, session=None, adapter=None, trailing_slash=False, autopaginate=None)


Arguments:

* ``url``: The root URL of your API
* ``auth``: The auth for your API. You can pass anything that ``requests`` can accept as auth.
* ``session``: Pass a session instance to have ``requests`` use that session. If ``None`` (the default), it will instantiate an instance of ``requests.session`` for you.
* ``adapter``: optional session adapter for ``requests``.
* ``trailing_slash``: You can set this to ``True`` if your API's URLs end with a ``/``
* ``autopaginate``: You can set this to a callable to fetch all pages resulting from a request. Currently, the only callable included is ``genericclient.pagination.link_header``, which supports [RFC5988](https://tools.ietf.org/html/rfc5988).

Endpoints
---------

Endpoints are available as properties on the main instance.

``.all()``
~~~~~~~~~~

Retrieves all resources (essentially a simple ``GET`` on the endpoint)::

    myclient.posts.all()  # GET /posts/

``.filter()``
~~~~~~~~~~~~~

``.filter(**kwargs)`` calls a ``GET`` with ``kwargs`` as querystring values::

    myclient.posts.filter(blog=12, status=1)  # GET /posts/?blog=12&status=1

``.get(**kwargs)``
~~~~~~~~~~~~~~~~~~

A special case of ``.filter()``.

If ``kwargs`` contains ``id``, ``pk``, ``slug`` or ``username``, that value will
be used in the URL path, in that order.

Otherwise, it calls a ``GET`` with ``kwargs`` as querystring values.

If the returned list is empty, will raise ``ResourceNotFound``.

If the returned list contains more than 1 resource, will raise ``MultipleResourcesFound``

Note that ``.get()`` will return a ``Resource``, not a list of ``Resource`` s

::

    myclient.posts.filter(blog=12, status=1)  # GET /posts/?blog=12&status=1
    myclient.posts.filter(id=12)  # GET /posts/12/
    myclient.posts.filter(slug='12-ways-clickbait')  # GET /posts/12-ways-clickbait/

``.create(payload)``
~~~~~~~~~~~~~~~~~~~~

Will result in a ``POST``, with ``payload`` (a ``dict``) as the request's body,
returning a new ``Resource``::

    post = myclient.posts.create({'blog': 12, 'status': 1})  # POST /posts/

``.get_or_create(defaults, **kwargs)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Issues a GET to fetch the resource. If the resource is not found, issues a POST
to create the resource::

    # Assuming it doesn't exist
    post = myclient.posts.get_or_update(slug='my-post', defaults={'status': 1})  # GET /posts/my-post/, then POST /posts/


``.create_or_update(payload)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If ``payload`` contains a key called ``'id'``, will issue a ``PUT``. If the
server returns a `400` error, a ``PATCH`` request will be re-issued.
If `payload`` does not contains ``'id'``, it will issue a ``POST``::

    post = myclient.posts.create_or_update({'status': 1})  # POST /posts/
    post = myclient.posts.create_or_update({'id': 1234, 'status': 1})  # PUT /posts/1234/

    post = myclient.posts.create_or_update({'id': 1234})  # PUT /posts/1234/
    # <- server returns 400
    # -> PATCH /posts/1234/

``.delete(pk)``
~~~~~~~~~~~~~~~

Will issue a ``DELETE``, and will use ``pk`` as part of the URL::

    myclient.posts.delete(24)  # DELETE /posts/24/

Resources
---------

All endpoints methods (with the exception of ``.delete()``) return either a
``Resource`` or a list of ``Resource`` s.

A ``Resource`` is just a wrapping class for a ``dict``, where keys can be accessed
as properties.

Additionally, ``Resource`` s have a special property called ``.payload``, which
contains the original payload received from the server.

``Resource`` s have the following methods:

``Resource.delete()`` will result in a ``DELETE``, with ``Resource.id`` as
par of the URL::

    blog = myclient.posts.create({'blog': 12, 'status': 1})  # POST /posts/
    blog.delete()  # DELETE /blog/345/ -- the ID 345 was returned by the server in the previous response

``Resource.save()`` will result in a ``PUT``, with ``Resource.id`` as
par of the URL. If the
server returns a `400` error, a ``PATCH`` request will be re-issued::

    post = myclient.posts.create({'blog': 12, 'status': 1})  # POST /posts/
    post.status = 2
    post.save()  # PUT /posts/345/

    post = Resource(id=345, status=1)
    post.save()  # PUT /posts/345/
    # <- server returns 400
    # -> PATCH /posts/345/

ResourceSets
------------

Whenever a method returns a list of Resources, they list will be wrapped in a ``ResultSet``.

A ResultSet is a just a ``list`` object, with the addition of a ``.response`` containing the original response from the server.

Customizing Endpoints and Resources
-----------------------------------

Resources can be customized by subclassing ``genericclient.Resource``.

The most common reason is specifying the name of the primary key::

    from genericclient import Resource


    class PostResource(Resource):
        pk_name = 'slug'


Endpoints can be customized by subclassing ``genericclient.Endpoint``::

    form genericclient import Endpoint


    class PostEndpoint(Endpoint):
        resource_class = PostResource


You can then subclass ``genericclient.GenericClient`` to tell the client which endpoint classes to use on each endpoint::

    from genericclient import GenericClient

    class Client(GenericClient):
        endpoint_classes = {
            'posts': PostEndpoint,
        }

Routes
------

If your API has some non-RESTful calls within the main endpoints (sometimes referred as ``detail_route`` and ``list_route``), you can use ``genericclient`` to call them::

    myclient.posts(id=123).publish(date=tomorrow)

::

    myclient.blogs().ping() 


Routes http calls use ``POST`` by default, but you can specify something else by using the ``_method`` argument::

    myclient.posts(_method='get', id=123).pingbacks()

::

    myclient.blogs(_method='get').visits()

Note that this calls will return an instance of ``genericclient.ParsedResponse``, instead of instances of ``genericclient.Resource``,

License
=======

Licensed under the MIT License.
