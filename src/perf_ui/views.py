# -*- coding=utf-8 -*-
# author: yanyang.xie@gmail.com

import logging

from django.shortcuts import render_to_response, render

from perf_ui.model.result_parser import VEXPerfTestResult
from perf_ui.models import LoadTestResult, get_test_type_json_list, \
    get_test_version_json_list, get_test_project_json_list, \
    get_test_date_json_list
from perf_ui.util import get_test_content_number


logger = logging.getLogger(__name__)

def page_not_found(request):
    return render_to_response('404.html')

def page_error(request):
    return render_to_response('500.html')

def index(request):
    return render(request, 'perf_ui/base.html')

def result_vod_t6(request):
    context = _generate_result_context(request, 'VOD_T6')
    logger.debug("Context is: %s", context)
    print context

    return render(request, 'perf_ui/vod-t6-index.html', context=context)

def result_linear_t6(request):
    return render(request, 'perf_ui/linear-t6-index.html')

def result_cdvr_t6(request):
    return render(request, 'perf_ui/cdvr-t6-index.html')

# show load test result for one test type
def _generate_result_context(request, test_type):
    load_test_results = LoadTestResult.objects.filter(test_type=test_type);
    if request.GET.has_key('project_name'):
        project_name = request.GET.get('project_name')
        load_test_results = load_test_results.filter(project_name=project_name)
    
    if request.GET.has_key('project_version'):
        project_version = request.GET.get('project_version')
        load_test_results = load_test_results.filter(project_version=project_version)
    
    test_result = load_test_results[0]
    
    context = {}
    context.update({'test_type': test_type,
               'selected_project_name':test_result.project_name,
               'selected_project_version':test_result.project_name,    
               'selected_result_id':test_result.id,     
               'test_type_list': get_test_type_json_list(),
               'test_project_list': get_test_project_json_list(),
               'test_version_list':get_test_version_json_list(test_type, test_result.project_name),
               'test_date_list': get_test_date_json_list(test_type, test_result.project_name, test_result.project_version),
               })
    context.update(_generate_context(test_result))
    context.update(_get_vod_test_scenario(test_result))
    return context
    
def _generate_context(test_result):
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
                    })
        
    bitrate_perf_result = VEXPerfTestResult(test_result.index_summary)
    response_failure_rate = (100 * float('%0.6f' %bitrate_perf_result.response_failure))/ check_percent/ bitrate_perf_result.request_total
    result_context.update({'bitrate_response_average_response': bitrate_perf_result.response_average_time,
                    'bitrate_request_succeed_rate':bitrate_perf_result.request_succeed_rate,
                    'bitrate_response_failure_rate': ('%0.2f' %(round(100 - response_failure_rate, 2))) + '%'
                    })
    return result_context
    
def _get_vod_test_scenario(test_result):
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
        test_scenario_dict['sap_required'] = test_config_dict.get('test.require.sap')
    else:
        test_scenario_dict['sap_required'] = 'False'
    
    return test_scenario_dict

def _get_linear_test_scenario(test_result):
    return {}

def _get_cdvr_test_scenario(test_result):
    return {}

