# -*- coding=utf-8 -*-
# author: yanyang.xie@thistech.com
import json
import logging

from django.http.response import HttpResponse, HttpResponseServerError, HttpResponseBadRequest
from django.shortcuts import render_to_response, get_object_or_404
import requests
from requests.exceptions import ConnectionError, Timeout

from perfui.models import VEXPerfTestOperation, Operation, STATUS_TYPE,\
    OperationGroup


logger = logging.getLogger(__name__)

def perf_op_index(request):
    vex_operation_list = VEXPerfTestOperation.objects.filter(perf_config__isnull=False)
    
    context = {'vex_operation_list': vex_operation_list,}
    logger.debug('perf_op_index context: %s' %(context))
    return render_to_response('perfui/perf_operation.html', context)

def basic_op_index(request):
    groups = OperationGroup.objects.values_list('id')
    
    operation_list = []
    for group in groups:
        ops = Operation.objects.filter(group__id=group[0])
        if ops.count() > 0:
            operation_list.append(ops)
    context = {'operation_list': operation_list}
    
    '''
    operation_list = Operation.objects.all()
    # operation list will be separated to 2 tables
    operation_list_1 = operation_list[::2]
    operation_list_2 = operation_list[1::2]
    
    context = {'operation_list':[operation_list_1, operation_list_2]}
    '''
    logger.debug('basic_op_index context: %s' %(context))
    return render_to_response('perfui/basic_operation.html', context)

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
        
        stdout, stderr, ex = _execute_command(command, obj.timeout, True)
        if stderr is not None and len(stderr) > 0 and stderr.strip()!="":
            logger.error("Failed to execute ['%s'] operation. Reason:[%s]" %(op_tag, str(stderr)))
            json_data = json.dumps({"status_code": 500, "message":"Failed to execute ['%s'] operation. Reason:[%s]" %(op_tag, str(stderr[-1]).replace('\n', ''))})
            logger.error("Failed to execute ['%s'] operation. Reason:[%s]" %(op_tag, str(stderr[-1]).replace('\n', '')))
            return HttpResponse(json_data, content_type="application/json")
        elif ex is not None:
            logger.error("Failed to execute ['%s'] operation. Reason:[%s]" %(op_tag, str(ex)))
            json_data = json.dumps({"status_code": 500, "message":"Failed to execute ['%s'] operation. Reason:[%s]" %(op_tag, str(ex).replace('\n', ''))})
            return HttpResponse(json_data, content_type="application/json")
        else:
            if vex_op == 'true':
                status_flag = None
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
        
        if name.find('content_size')>-1: perf_config.content_size=value
        if name.find('bitrate_number')>-1: perf_config.bitrate_number=value
        if name.find('session_number')>-1: perf_config.session_number=value
        if name.find('warm_up_minute')>-1: perf_config.warm_up_minute=value
        
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

def basic_compontent_status(request):
    return _check_status(request, False)

def vex_perf_test_status(request):
    return _check_status(request, True)

def _check_status(request, is_vex_op):
    status_list = []
    
    operation_list = VEXPerfTestOperation.objects.all() if is_vex_op is True else Operation.objects.all()
    for op in operation_list:
        status_command = op.status_command
        if status_command is not None and status_command.strip() != '':
            stdout, stderr, ex = None, None,None
            if op.status_command_type == STATUS_TYPE[0][0]:
                stdout, stderr, ex = _execute_command(status_command, op.timeout, True)
            else:
                stdout, stderr, ex = _execute_command(status_command, op.timeout, False)
                try:
                    # to vex component, save version into short description
                    data = json.loads(stdout)
                    version = data['AppVersion'].lower()
                    op.short_description = version
                except:
                    pass
            
            #0-running, 1-stopped, 2, exception
            if ex is not None:
                logger.error(type(ex))
                if isinstance(ex, (ConnectionError, Timeout)):
                    status_list.append({'id':op.id, 'name':op.name, 'status': 1})
                    op.status_flag=False
                    op.save()
                else:
                    status_list.append({'id':op.id, 'name':op.name, 'status': 2})
            elif stderr is None or len(stderr) == 0:
                status_list.append({'id':op.id, 'name':op.name, 'status': 0})
                op.status_flag=True
                op.save()
            else:
                status_list.append({'id':op.id, 'name':op.name, 'status': 1})
                op.status_flag=False
                op.save()
        else:
            status_list.append({'id':op.id, 'name':op.name, 'status': 2})
    
    json_data = json.dumps(status_list)
    logger.info('VEX operation status: %s' %(json_data))
    return HttpResponse(json_data, content_type="application/json")

def _execute_command(cmd, timeout=30, is_shell=True):
    try:
        if is_shell is True:
            import subprocess
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=is_shell) 
            stdout, stderr = process.stdout.readlines(), process.stderr.readlines() 
            
            #import os, signal
            #os.kill(process.pid, signal.SIGKILL)
            return stdout, stderr, None
        else:
            #do_http
            r = requests.get(cmd, timeout=timeout)
            if r.status_code != 200 and r.status_code != 204:
                logger.debug('Service is not running. Cmd is %s, response status code is %s' %(cmd, r.status_code))
                return None, 'Service is not running', None
            else:
                return r.text, None, None
    except Exception, e:
        logger.error('Execute command error. Cmd is %s. Error is %s' %(cmd, e))
        return None, None, e

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
    elif op_tag == "deploy":
        command = obj.deploy_command
    return command, obj