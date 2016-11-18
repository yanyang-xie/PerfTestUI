# -*- coding=utf-8 -*-
# author: yanyang.xie@gmail.com
import os
import json
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

def operation(request):
    try:
        op_id = request.GET.get('op_id')
        op_tag = request.GET.get('op_tag')
        logger.debug("Operation:[id:%s, tag:%s]" %(op_id, op_tag))
        
        command = _get_operation_command(op_id, op_tag)
        logger.debug("Operation:[id:%s, tag:%s]. Command is %s" % (op_id, op_tag, command))
        if command == "":
            raise Exception("Not found command['%s']" %(op_tag))
        
        stdout, stderr = execute_command(command, 20)
        if stdout is None:
            logger.error("Timeout to execute ['%s'] operation." %(op_tag))
            json_data = json.dumps({"status_code": 500, "message":"Timeout to execute ['%s'] operation." %(op_tag)})
            return HttpResponse(json_data, content_type="application/json")
        
        if len(stderr) > 0:
            logger.error("Failed to execute ['%s'] operation. Reason:[%s]" %(op_tag, str(stderr)))
            json_data = json.dumps({"status_code": 500, "message":"Failed to execute ['%s'] operation. Reason:[%s]" %(op_tag, str(stderr[-1]).replace('\n', ''))})
            return HttpResponse(json_data, content_type="application/json")
        
        logger.debug("Operation:[id:%s, tag:%s]. Command is %s, response is '%s'" % (op_id, op_tag, command, stdout))
        # You can dump a lot of structured data into a json object, such as lists and tuples
        json_data = json.dumps({"status_code": 200, "message":"ok"})
        return HttpResponse(json_data, content_type="application/json")
    except Exception, e:
        logger.error("Internal Server ERROR. Failed to execute [%s] operation. %s" %(op_tag, e))
        json_data = json.dumps({"status_code": 500, "message":"Internal Server ERROR"})
        return HttpResponse(json_data, content_type="application/json")

def update_operation_config(request):
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

def execute_command(command, timeout=30, is_shell=True):  
    """call shell-command and either return its output or kill it 
    if it doesn't normally exit within timeout seconds and return None""" 
    import subprocess, datetime, os, time, signal  
    start = datetime.datetime.now()
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=is_shell)  
    while process.poll() is None:  
        time.sleep(0.2)  
        now = datetime.datetime.now()  
        if (now - start).seconds> timeout:  
            os.kill(process.pid, signal.SIGKILL)  
            os.waitpid(-1, os.WNOHANG)  
            return None,None
    return process.stdout.readlines(),process.stderr.readlines()

def _get_operation_command(op_id, op_tag):
    vex_op_object = get_object_or_404(VEXPerfTestOperation, pk=op_id)
    command = ""
    if op_tag == "start":
        command = vex_op_object.start_command
    elif op_tag == "stop":
        command = vex_op_object.stop_command
    elif op_tag == "status":
        command = vex_op_object.status_command
    elif op_tag == "result":
        command = vex_op_object.result_collect_command
    return command