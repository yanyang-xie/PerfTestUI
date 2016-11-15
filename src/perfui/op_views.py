# -*- coding=utf-8 -*-
# author: yanyang.xie@gmail.com
import logging

from django.http.response import HttpResponse, HttpResponseServerError, HttpResponseBadRequest
from django.shortcuts import render_to_response, get_object_or_404
from perfui.models import VEXPerfTestOperation

logger = logging.getLogger(__name__)

def index(request):
    all_operation_list = VEXPerfTestOperation.objects.all()
    vex_operation_list = all_operation_list.filter(perf_config__isnull=False)
    operation_list = all_operation_list.filter(perf_config__isnull=True)
    
    # operation list will be separated to 3 tables
    operation_list_1 = operation_list[::3]
    operation_list_2 = operation_list[1::3]
    operation_list_3 = operation_list[2::3]
    
    context = {'vex_operation_list': vex_operation_list, 'operation_list':[operation_list_1, operation_list_2, operation_list_3]}
    
    return render_to_response('perfui/operation.html', context)

def update_perf_config(request):
    try:
        #print request.POST.items()
        pk = request.POST.get('pk')
        name = request.POST.get('name')
        value = int(request.POST.get('value'))
        logger.debug('Update: pk:%s, name:%s, value:%s' %(pk, name , value))
        vex_op_object = get_object_or_404(VEXPerfTestOperation, pk=pk)
        perf_config = vex_op_object.perf_config
        
        if name == 'content_size': perf_config.content_size=value
        if name == 'bitrate_number': perf_config.bitrate_number=value
        if name == 'session_number': perf_config.session_number=value
        if name == 'warm_up_minute': perf_config.warm_up_minute=value
        
        perf_config.save()
        return HttpResponse('Saved')
    except ValueError, e:
        logger.error('Value of %s must be int. %s' %(name, e))
        response = HttpResponseBadRequest('Value of %s must be int' %(name))
        return response
    except Exception, e:
        logger.error('Failed to save the change. %s' %e)
        response = HttpResponseServerError('Server ERROR')
        return response