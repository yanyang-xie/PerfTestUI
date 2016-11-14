# -*- coding=utf-8 -*-
# author: yanyang.xie@gmail.com
from django.http.response import HttpResponse
from django.shortcuts import render_to_response
from perfui.models import VEXPerfTestOperation

def index(request):
    vex_operation_list = VEXPerfTestOperation.objects.all()
    context = {'vex_operation_list': vex_operation_list}
    
    return render_to_response('perfui/operation.html', context)

def update_perf_config(request):
    print request.POST
    return HttpResponse('ok')
