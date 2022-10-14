from http import HTTPStatus
from django.shortcuts import render


def page_not_found(request, exception):
    return render(request,
                  'core/404.html',
                  {'path': request.path},
                  status=HTTPStatus.NOT_FOUND.value
                  )


def csrf_failure(request, reason=''):
    return render(request,
                  'core/403csrf.html',
                  status=HTTPStatus.FORBIDDEN.value
                  )


def server_error(request):
    return render(request,
                  'core/500.html',
                  status=HTTPStatus.INTERNAL_SERVER_ERROR.value
                  )
