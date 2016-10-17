import logging

from django.shortcuts import render_to_response, render


logger = logging.getLogger(__name__)

def page_not_found(request):
    return render_to_response('404.html')

def page_error(request):
    return render_to_response('500.html')

def index(request):
    return render(request, 'perf_ui/index.html')

def about(request):
    pass
