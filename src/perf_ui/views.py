import logging
import string

from django.shortcuts import render_to_response, render

from perf_ui.models import LoadTestResult, get_test_type_json_list, \
    get_test_version_json_list, get_test_project_json_list


logger = logging.getLogger(__name__)

def page_not_found(request):
    return render_to_response('404.html')

def page_error(request):
    return render_to_response('500.html')

def index(request):
    return render(request, 'perf_ui/base.html')

def result_vod_t6(request):
    return render(request, 'perf_ui/vod-t6-index.html')

def result_linear_t6(request):
    return render(request, 'perf_ui/linear-t6-index.html')

def result_cdvr_t6(request):
    return render(request, 'perf_ui/cdvr-t6-index.html')

# show load test result for one test type
def show_latest_test_results(request, test_type, max=10):
    context = {'selected_test_type': test_type, 'test_type_list': get_test_type_json_list(), 'test_project_list': get_test_project_json_list(),}
    
    load_test_results = LoadTestResult.objects.filter(test_type=test_type);
    if len(load_test_results) == 0:
        return render(request, 'loadtest/testResults.html', context)
    
    context.update({'test_version_list': get_test_version_json_list(test_type),})
    latest_test_result = load_test_results[0]
    
    
    
    '''
    if len(load_test_results) > 0:
        latest_load_test_result = load_test_results[0]
        index_results = _get_armcharts_column_list(latest_load_test_result.test_result_index)
        bitrate_results = _get_armcharts_column_list(latest_load_test_result.test_result_bitrate)
        
        index_benchmark_summary = _get_benchmark_number(latest_load_test_result.test_result_index, '_index')
        bitrate_benchmark_summary = _get_benchmark_number(latest_load_test_result.test_result_bitrate, '_bitrate')
        
        context.update({'load_test_results':load_test_results,
                        'selected_test_id': latest_load_test_result.id,
                        'selected_test_module':latest_load_test_result.test_module,
                        'selected_test_version':latest_load_test_result.test_version,
                       'index_result_json': json.dumps(index_results),
                       'bitrate_result_json': json.dumps(bitrate_results),
                       })
        context.update(latest_load_test_result.as_dict())
        context.update(index_benchmark_summary)
        context.update(bitrate_benchmark_summary)
        
    logger.debug("Context is: %s", context)
    return render(request, 'loadtest/testResults.html', context)
    '''

# 
def _get_armcharts_column_list(benchmark_result):
    color_list = ['#CD0D74', '#8A0CCF', ]
    
    time_distribute_tmp_dict = {}
    time_distribute_armchart_info_dict = {}
    
    for line in benchmark_result.split('\n'):
        if string.strip(line) == '':
            continue
        
        if line.find('millisecond') < 0:
            continue
        
        time_tag, client_number = line.split(':')
        time_tag = time_tag.replace('millisecond', '').strip()
        client_number = client_number.replace('\r', ' ').strip()
        
        time_distribute_key = int(time_tag.split('-')[0].strip())
        time_distribute_tmp_dict[time_distribute_key] = time_tag
        
        converted_dict = {}
        converted_dict['ResponseTime'] = time_tag
        converted_dict['Client']=client_number
        time_distribute_armchart_info_dict[time_tag]=converted_dict
    
    keys = time_distribute_tmp_dict.keys()
    keys.sort()
    convert_column_list = []
    for i, key in enumerate(keys):
        armchart_info_dict = time_distribute_armchart_info_dict.get(time_distribute_tmp_dict.get(key))
        armchart_info_dict['color'] = color_list[i%len(color_list)]
        convert_column_list.append(armchart_info_dict)
        
    return convert_column_list


if __name__ == '__main__':
    t = '''
    Index response summary
      Test Duration (second): 300
      Request concurrent    : 95
      Request In Total      : 28635
      Request Succeed       : 28635
      Request Failure       : 0
      Request Succeed Rate  : 100.00%
      Response Average Time : 27
      Response Failure      : 0
      Response Time Distribution
          0-200      millisecond: 28587
          200-500    millisecond: 0
          500-1000   millisecond: 48
          1000-2000  millisecond: 0
          2000-3000  millisecond: 0
          3000-6000  millisecond: 0
          6000-12000 millisecond: 0
    '''
    
    print _get_armcharts_column_list(t)
