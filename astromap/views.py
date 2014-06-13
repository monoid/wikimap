from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def index(request):
    u""" Index page. """
    # Renders template
    return HttpResponse(u'index')


def atom_feed(request):
    u""" An ATOM feed. """
    return HttpResponse(u'atom')


def kml_feed(request):
    u""" A KML feed for Google Earth etc. """
    return HttpResponse(u'kml')


def login(request):
    u""" Login page and login handler, both old and social. """
    return HttpResponse(u'login')


def ajax_handler(request):
    u""" AJAX handling: point creation, modification, etc. """
    return HttpResponse(u'ajax')


# def auth_handler(request):
#     return ''
