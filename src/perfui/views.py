# -*- coding=utf-8 -*-
# author: yanyang.xie@thistech.com

import logging

from django.db.models.query_utils import Q
from django.shortcuts import render_to_response, render

from perfui.model.armchart import generate_vex_am_serial_chart_info
from perfui.model.result_parser import VEXPerfTestResult
from perfui.models import PerfTestResult, get_test_type_json_list, \
    get_test_version_json_list, get_test_project_json_list, \
    get_test_date_json_list
from perfui.utility.common_util import get_test_content_number


logger = logging.getLogger(__name__)

def page_not_found(request):
    return render_to_response('404.html')

def page_error(request):
    return render_to_response('500.html')

def index(request):
    return render(request, 'perfui/base.html')

# show load test result for one test type
def show_perf_result(request, test_type):
    context = _get_result_context(request, test_type)
    logger.debug("Context is: %s", context)
    return render(request, 'perfui/perf_result.html', context=context)

def _get_result_context(request, test_type):
    load_test_results = PerfTestResult.objects.filter(~Q(index_summary=u''),test_type=test_type);
    context = {'test_type': test_type,
               'test_type_list': get_test_type_json_list(),
               'test_project_list': get_test_project_json_list(),
               }

    if request.GET.has_key('project_name'):
        project_name = request.GET.get('project_name')
        context.update({'selected_project_name': project_name,})
        load_test_results = load_test_results.filter(project_name=project_name)
    
    if request.GET.has_key('project_version'):
        project_version = request.GET.get('project_version')
        context.update({'selected_project_version': project_version,})
        load_test_results = load_test_results.filter(project_version=project_version)
    
    if load_test_results.count() > 0:
        if request.GET.has_key('test_result_id'):
            test_result = PerfTestResult.objects.get(id=int(request.GET.get('test_result_id')));
        else:
            test_result = load_test_results[-1]
        context.update(
                {
                'no_result': False,
                'selected_project_name':test_result.project_name,
                'selected_project_version':test_result.project_version,   
                'selected_result_id':test_result.id,     
                'test_version_list':get_test_version_json_list(test_type, test_result.project_name),
                'test_date_list': get_test_date_json_list(test_type, test_result.project_name, test_result.project_version),
                })
        context.update(_get_result_summary_context(test_result))
        context.update(_get_test_scenario_context(test_result))
        context.update(_get_result_error_details_context(test_result))
        
        if test_type.find('VOD') < 0:
            context['client_number'] = context['request_total']
        
        if test_type.find('CDVR') > -1:
            context['asset_number'] = context['client_number']
    else:
        context.update({'no_result': True, })
    return context
    
def _get_result_summary_context(test_result):
    result_context = {}
    result_context.update(test_result.as_dict())
    
    test_config_dict = eval(test_result.test_config)
    check_percent = 1.00 
    if test_config_dict.has_key('client.response.check.percent'):
        check_percent = float(test_config_dict.get('client.response.check.percent'))
        
    index_perf_result = VEXPerfTestResult(test_result.index_summary)
    result_context['request_concurrent'] = (index_perf_result.request_concurrent + 1 ) / test_result.instance_number
    result_context.update({'index_response_average_response': index_perf_result.response_average_time,
                    'index_request_succeed_rate':index_perf_result.request_succeed_rate,
                    'request_total':index_perf_result.request_total,
                    'test_duration':index_perf_result.test_duration,
                    })
        
    bitrate_perf_result = VEXPerfTestResult(test_result.bitrate_summary)
    if bitrate_perf_result.request_total !=0:
        response_failure_rate = (100 * float('%0.6f' %bitrate_perf_result.response_failure))/ check_percent/ bitrate_perf_result.request_total
    else:
        response_failure_rate = 0
    
    result_context.update({'bitrate_response_average_response': bitrate_perf_result.response_average_time,
                    'bitrate_request_succeed_rate':bitrate_perf_result.request_succeed_rate,
                    'bitrate_response_success_rate': ('%0.2f' %(round(100 - response_failure_rate, 2))) + '%',
                    'bitrate_response_error_details': test_result.error_details.strip(),
                    })
    
    index_am_chart_info, index_am_chart_defination = generate_vex_am_serial_chart_info(index_perf_result.response_time_distribution_list, "Index")
    bitrate_am_chart_info, bitrate_am_chart_defination = generate_vex_am_serial_chart_info(bitrate_perf_result.response_time_distribution_list, "Bitrate")
    
    result_context.update(index_am_chart_defination)
    result_context.update(bitrate_am_chart_defination)
    result_context.update({'index_am_data': index_am_chart_info, 'bitrate_am_data': bitrate_am_chart_info,})
    
    return result_context

def _get_result_error_details_context(test_result):
    errors = test_result.error_details
    
    error_dict = {}
    for error_info in errors.split('\n'):
        if error_info.strip() == '':
            continue
        
        error_info = str(error_info).replace('str:', '')
        print error_info
        sep_position = error_info.find(':')
        ip = error_info[:sep_position]
        error_msg = str(error_info[sep_position + 1:].strip())
        error_list = error_msg.split('\t')
        
        error_dict[str(ip.strip())] = error_list
        
        if len(error_dict) >= 10:
            break
    
    return {'error_dict': error_dict}

def _get_test_scenario_context(test_result):
    test_config_dict = eval(test_result.test_config)
    
    test_scenario_dict = {}
    if test_config_dict.has_key('test.case.content.names'):
        content_names = test_config_dict.get('test.case.content.names').split('_')[-1]
        test_scenario_dict['asset_number'] = get_test_content_number(content_names)
    else:
        test_scenario_dict['asset_number'] = 0
    
    if test_config_dict.has_key('test.bitrate.request.number'):
        test_scenario_dict['media_request_number'] = test_config_dict.get('test.bitrate.request.number')
    else:
        test_scenario_dict['media_request_number'] = 2
    
    if test_config_dict.has_key('test.index.asset.content.size'):
        test_scenario_dict['master_content_size'] = test_config_dict.get('test.index.asset.content.size')
    else:
        test_scenario_dict['master_content_size'] = '10k'
    
    if test_config_dict.has_key('test.bitrate.asset.content.size'):
        test_scenario_dict['media_playlist_content_size'] = test_config_dict.get('test.bitrate.asset.content.size')
    else:
        test_scenario_dict['media_playlist_content_size'] = '150k'
    
    if test_config_dict.has_key('test.bitrate.asset.content.size.merged'):
        test_scenario_dict['merged_media_playlist_content_size'] = test_config_dict.get('test.bitrate.asset.content.size.merged')
    else:
        test_scenario_dict['merged_media_playlist_content_size'] = '300k'
    
    if test_config_dict.has_key('test.require.sap'):
        test_scenario_dict['sap_required'] = 'Yes' if test_config_dict.get('test.require.sap') == 'True' else 'No'
    else:
        test_scenario_dict['sap_required'] = 'No'
    
    # for hot cdvr and linear
    if test_config_dict.has_key('test.case.client.number'):
        test_scenario_dict['client_number'] = test_config_dict.get('test.case.client.number')
    
    return test_scenario_dict
