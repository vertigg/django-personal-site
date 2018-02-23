from django.http import HttpResponse, Http404
from django import get_version
from django.shortcuts import render
import datetime

def show_datetime(request):
    now = datetime.datetime.now()
    return render(request, 'current_date.html', {"current_date":now})

def hours_ahead(request, offset):
    try:
        offset = int(offset)
    except ValueError:
        raise Http404()
    dt = datetime.datetime.now() + datetime.timedelta(hours=offset)
    html = '<html><body><h1>After {0} hour(s), it will be {1} </body></html>'.format(offset, dt)
    return HttpResponse(html)
