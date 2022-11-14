class HttpPatchParsingMiddleware():
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'PATCH' and not request.content_type == 'application/json':
            if hasattr(request, '_post'):
                del request._post
                del request._files

            try:
                request.method = 'POST'
                request._load_post_and_files()
                request.method = 'PATCH'
            except AttributeError as error:
                request.META['REQUEST_METHOD'] = 'POST'
                request._load_post_and_files()
                request.META['REQUEST_METHOD'] = 'PATCH'
            request.PATCH = request.POST

        response = self.get_response(request)
        return response

