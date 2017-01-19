
class VEXPerfTestResult():
    def __init__(self, test_result_info):
        self.test_result_info = test_result_info
        self.test_duration_tag = 'Test Duration'
        self.request_total_tag = 'Request In Total'
        self.request_concurrent_tag = 'Request concurrent'
        self.request_succeed_rate_tag = 'Request Succeed Rate'
        self.response_average_time_tag = 'Response Average Time'
        self.response_failure_tag = 'Response Failure'
        self.response_time_distribution_tag = 'millisecond'
        self.response_time_distribution_metric_sep = '-'
        
        self.test_duration = 1
        self.request_total = 0
        self.request_concurrent = 1
        self.request_succeed_rate = '100.00%'
        self.request_succeed = 0
        self.response_average_time = 1
        self.response_failure = 0
        self.response_time_distribution_list = []
        self.response_time_distribution_percent_list = []
        
        self.parse()
    
    def parse(self):
        for line in self.test_result_info.split('\n'):
            line = line.strip()
            if line == '' or line.find(':') < 0:
                continue
            
            key, value = line.split(':')
            if key.find(self.test_duration_tag) > -1:
                self.test_duration = int(value.strip())
                continue
            
            if key.find(self.request_total_tag) > -1:
                self.request_total = int(value.strip())
                continue
            
            if key.find(self.request_concurrent_tag) > -1:
                self.request_concurrent = int(value.strip())
                continue
            
            if key.find(self.request_succeed_rate_tag) > -1:
                self.request_succeed_rate = value.strip()
                continue
            
            if key.find(self.response_average_time_tag) > -1:
                self.response_average_time = int(value.strip())
                continue
            
            if key.find(self.response_failure_tag) > -1:
                self.response_failure = int(value.strip())
                continue
            
            if key.find(self.response_time_distribution_tag) > -1:
                response_time_distribution = key.replace(self.response_time_distribution_tag,'').strip()
                response_time_distribution_list = response_time_distribution.split(self.response_time_distribution_metric_sep)
                response_time_distribution = '%-6s-%6s' %(str(response_time_distribution_list[0]), str(response_time_distribution_list[1]))
                
                self.response_time_distribution_list.append([response_time_distribution, int(value.strip())])
                continue
        
        for distribution in self.response_time_distribution_list:
            percent = (100 * float('%0.6f' %distribution[1]))/ self.request_total
            self.response_time_distribution_percent_list.append([distribution[0], '%0.4f' %(percent)])
        
        self.request_succeed = int(self.request_total * float(self.request_succeed_rate.replace('%', ''))) / 100
        print self.request_succeed

if __name__ == '__main__':
    result_info = '''
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
    
    r = VEXPerfTestResult(result_info)
    print r.test_duration
    print r.request_total
    print r.request_concurrent
    print r.request_succeed_rate
    print r.response_average_time
    print r.response_failure
    print r.response_time_distribution_list
    print r.response_time_distribution_percent_list
    