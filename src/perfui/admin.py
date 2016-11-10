from django.contrib import admin

from perfui.models import PerfTestResult, PerfTestConfig, Operation, \
    VEXPerfTestOperation


# Register your models here.
admin.site.register(PerfTestResult)
admin.site.register(PerfTestConfig)
admin.site.register(Operation)
admin.site.register(VEXPerfTestOperation)
