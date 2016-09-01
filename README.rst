=============
genericclient
=============

A generic client for RESTful APIs

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

    myclient = GenericClient(url, auth=None, adapter=None, trailing_slash=False)


Arguments:

* ``url``: The root URL of your API
* ``auth``: The auth for your API. You can pass anything that ``requests`` can accept as auth.
* ``adapter``: optional session adapter for ``requests``.
* ``trailing_slash``: You can set this to ``True`` if your API's URLs end with a ``/``

Endpoints
---------

Endpoints are available as properties on the main instance.

``.all()``
~~~~~~~~~~

Retrieves all resources (essentially a simple ``GET`` on the endpoint)::

    myclient.posts.all()  # GET /posts/

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
to create the resource.

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

License
=======

Licensed under the MIT License.
