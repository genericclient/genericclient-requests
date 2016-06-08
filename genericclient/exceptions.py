class MultipleResourcesFound(ValueError):
    pass


class ResourceNotFound(ValueError):
    pass


class HTTPError(ValueError):
    def __init__(self, response, *args, **kwargs):
        self.response = response
        super(HTTPError, self).__init__(response, *args, **kwargs)


class NotAuthenticatedError(ValueError):
    def __init__(self, response, message=None, *args, **kwargs):
        self.response = response
        super(NotAuthenticatedError, self).__init__(message, *args, **kwargs)
