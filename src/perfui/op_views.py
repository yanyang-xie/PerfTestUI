# -*- coding=utf-8 -*-
# author: yanyang.xie@gmail.com
import json
import logging

from django.http.response import HttpResponse, HttpResponseServerError, HttpResponseBadRequest
from django.shortcuts import render_to_response, get_object_or_404

from perfui.models import VEXPerfTestOperation, Operation

logger = logging.getLogger(__name__)

def index(request):
    vex_operation_list = VEXPerfTestOperation.objects.filter(perf_config__isnull=False)
    operation_list = Operation.objects.all()
    
    # operation list will be separated to 2 tables
    operation_list_1 = operation_list[::2]
    operation_list_2 = operation_list[1::2]
    
    context = {'vex_operation_list': vex_operation_list, 'operation_list':[operation_list_1, operation_list_2]}
    return render_to_response('perfui/operation.html', context)

def operation(request):
    try:
        op_id = request.GET.get('op_id')
        op_tag = request.GET.get('op_tag')
        vex_op = request.GET.get('vex_op')
        logger.debug("Operation:[id:%s, tag:%s, is_vex_op:%s]" %(op_id, op_tag, vex_op))
        
        command, obj = _get_operation_command(op_id, op_tag, vex_op)
        logger.debug("Operation:[id:%s, tag:%s]. Command is [%s]" % (op_id, op_tag, command))
        if command == "":
            raise Exception("Not found command['%s']" %(op_tag))
        
        stdout, stderr = execute_command(command, obj.timeout)
        
        if stderr is not None and len(stderr) > 0:
            logger.error("Failed to execute ['%s'] operation. Reason:[%s]" %(op_tag, str(stderr)))
            json_data = json.dumps({"status_code": 500, "message":"Failed to execute ['%s'] operation. Reason:[%s]" %(op_tag, str(stderr[-1]).replace('\n', ''))})
            logger.error("Failed to execute ['%s'] operation. Reason:[%s]" %(op_tag, str(stderr[-1]).replace('\n', '')))
            return HttpResponse(json_data, content_type="application/json")
        else:
            if vex_op == 'true':
                if op_tag == 'start':
                    status_flag = True
                elif op_tag == 'stop':
                    status_flag = False
                
                if status_flag is not None:
                    obj.status_flag = status_flag
                    obj.save()
                    logger.debug('Save performace test operation status for %s to %s' %(obj.name, status_flag))
        
        logger.info("Operation:[id:%s, tag:%s]. Command is %s, response is '%s'" % (op_id, op_tag, command, stdout))
        # You can dump a lot of structured data into a json object, such as lists and tuples
        json_data = json.dumps({"status_code": 200, "message": "Success to execute %s [%s]" %(op_tag.lower(), obj.name.lower())})
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

def vex_perf_test_status(request):
    status_list = []
    
    vex_operation_list = VEXPerfTestOperation.objects.all()
    for vex_op in vex_operation_list:
        status_command = vex_op.status_command
        if status_command is not None:
            stdout, stderr = execute_command(status_command)
        
            if stderr is None or len(stderr) == 0:
                status_list.append({'id':vex_op.id, 'status': 0})
                vex_op.status_flag=True
                vex_op.save()
            else:
                status_list.append({'id':vex_op.id, 'status': 1})
                vex_op.status_flag=False
                vex_op.save()
        else:
            status_list.append({'id':vex_op.id, 'status': 2})
    
    json_data = json.dumps(status_list)
    logger.debug('VEX operation status: %s' %(json_data))
    return HttpResponse(json_data, content_type="application/json")

def execute_command(command, timeout=30, is_shell=True):
    import subprocess
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=is_shell) 
    stdout, stderr = process.stdout.readlines(), process.stderr.readlines() 
    
    import os, signal
    os.kill(process.pid, signal.SIGKILL)
    return stdout, stderr

def execute_command_older(command, timeout=30, is_shell=True): 
    """call shell-command and either return its output or kill it 
    if it doesn't normally exit within timeout seconds and return None""" 
    import subprocess, datetime, os, time, signal  
    start = datetime.datetime.now()
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=is_shell) 
    while process.poll() is None:
        time.sleep(.5)
        now = datetime.datetime.now()
        if (now - start).seconds> timeout:
            logger.warn("Timeout[%s] to run [%s], return" %(timeout, command))
            os.kill(process.pid, signal.SIGKILL)
            os.waitpid(-1, os.WNOHANG)
            return None,["Timeout[%s]" %(timeout), ]
    return process.stdout.readlines(),process.stderr.readlines()

def _get_operation_command(op_id, op_tag, is_vex_operation):
    if is_vex_operation == 'true':
        obj = get_object_or_404(VEXPerfTestOperation, pk=op_id)
    else:
        obj = get_object_or_404(Operation, pk=op_id)
        
    command = ""
    if op_tag == "start" or op_tag == "run":
        command = obj.start_command
    elif op_tag == "stop":
        command = obj.stop_command
    elif op_tag == "status":
        command = obj.status_command
    elif op_tag == "result":
        command = obj.result_collect_command
    return command, obj