genericclient
-------------

A generic client for RESTful APIs

::

    $ pip install genericclient


Usage
-----

::

    from genericclient import GenericClient

    myclient = GenericClient(api_url)

    myresource = myclient.resources.get(id=1)

    actives = myclients.posts.filter(active=True)

License
-------

Licensed under the MIT License.
