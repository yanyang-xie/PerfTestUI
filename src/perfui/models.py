# -*- coding: UTF-8 -*-
from django.db import models
from perfui.utility.date_util import get_current_day_start_date

# choices = ['value', 'display name']
CHOICES_PROJECT = [('VEX-Core', 'VEX-Core'), ('VEX-Frontend', 'VEX-Frontend')]
CHOICES_TYPE = [('VOD_T6', 'T6VOD'), ('CDVR_T6', 'CDVR_T6'), ('LINEAR_T6', 'LINEAR_T6')]

class PerfTestResult(models.Model):
    project_name = models.CharField(max_length=100, choices=CHOICES_PROJECT, blank=False, null=False)
    project_version = models.CharField(max_length=100, blank=False, null=False)
    test_type = models.CharField(max_length=100, choices=CHOICES_TYPE, blank=False, null=False)
    test_date = models.DateTimeField(default=get_current_day_start_date())
    test_config = models.TextField(blank=False, null=False)
    index_summary = models.TextField(blank=False, null=False)
    bitrate_summary = models.TextField(blank=False, null=False)
    error_details = models.TextField(blank=True, null=True)
    instance_number = models.IntegerField(default=2, blank=False, null=False)
    
    def __unicode__(self):
        return '[id:{}, project_name:{}, project_version:{}, test_type:{}, test_date:{}, instance_size:{}]'\
                    .format(self.id, self.project_name, self.project_version, self.test_type, self.test_date.strftime('%Y-%m-%d'), self.instance_number)
    
    def as_dict(self):
        return dict(
            id=self.id,
            project_name=self.project_name,
            project_version=self.project_version,
            test_type=self.test_type,
            test_date=self.test_date.strftime('%Y-%m-%d'),
            test_config=self.test_config,
            index_summary=self.index_summary,
            bitrate_summary=self.bitrate_summary,
            error_details=self.error_details,
            instance_number=self.instance_number,
            )
    
    class Meta:
        db_table = 'perf_result'
        ordering = ['-test_date']
        get_latest_by = 'test_date'
        unique_together = ("project_name", "project_version", "test_type", "test_date")

def get_test_type_json_list():
    test_type_list = []
    for choice in CHOICES_TYPE:
        test_type_list.append({"id":choice[0], "name":choice[1]})
    return test_type_list

def get_test_project_json_list():
    test_project_list = []
    for choice in CHOICES_PROJECT:
        test_project_list.append({"id":choice[0], "name":choice[1]})
    return test_project_list

def get_test_version_json_list(test_type, project_name=None):
    if project_name is not None:
        result_list = PerfTestResult.objects.filter(project_name=project_name, test_type=test_type).values_list("project_version").distinct()
    else:
        result_list = PerfTestResult.objects.filter(test_type=test_type).values_list("project_version").distinct()
    return [{"id": str(result[0]), "name":str(result[0])} for result in set(result_list)]

def get_test_date_json_list(test_type, project_name=None, project_version=None):
    test_result_list = PerfTestResult.objects.filter(test_type=test_type)
    if project_name is not None:
        test_result_list = test_result_list.filter(project_name=project_name)
    
    if project_version is not None:
        test_result_list = test_result_list.filter(project_version=project_version)
    
    test_result_list = test_result_list.values("id", "test_date").distinct()
    return [{"id": str(result["id"]), "name":result["test_date"].strftime('%m/%d/%Y')} for result in test_result_list]



#-----------------------------------------------------------------#
class PerfTestConfig(models.Model):
    project_name = models.CharField(max_length=100, choices=CHOICES_PROJECT, blank=False, null=False)
    test_type = models.CharField(max_length=100, choices=CHOICES_TYPE, blank=False, null=False)
    test_config = models.TextField(blank=True, null=True)
    
    content_size = models.IntegerField(blank=False, null=False, default=15000)
    bitrate_number = models.IntegerField(blank=False, null=False, default=2)
    concurrent_session = models.IntegerField(blank=True, null=True, default=0)
    warm_up_minute = models.IntegerField(blank=False, null=False, default=0)
    
    def __unicode__(self):
        return '[id:{}, project_name:{}, test_type:{}, content_size:{}, bitrate_number:{}, concurrent_session:{}, warm_up_minute:{}, ]'\
                    .format(self.id, self.project_name, self.test_type, self.content_size, self.bitrate_number, self.concurrent_session, self.warm_up_minute)
    
    class Meta:
        db_table = 'perf_config'
        ordering = ['project_name', ]
        get_latest_by = 'project_name'
        unique_together = ("project_name", "test_type",)

class Operation(models.Model):
    name = models.CharField(max_length=512, blank=False, null=False)
    start_command = models.CharField(max_length=512, blank=True, null=True)
    stop_command = models.CharField(max_length=512, blank=True, null=True)
    status_command = models.CharField(max_length=512, blank=True, null=True)
    status_info = models.CharField(max_length=20, blank=True, null=True, default='')
    
    class Meta:
        db_table = 'operation'

class VEXPerfTestOperation(Operation):
    perf_config = models.OneToOneField(PerfTestConfig, blank=True, null=True,)
    
    class Meta:
        db_table = 'perf_operation'
