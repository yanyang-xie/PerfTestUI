from django.contrib import admin

from perfui.models import PerfTestResult, PerfTestConfig, Operation, \
    VEXPerfTestOperation, OperationGroup, VEXVersion


# Register your models here.
admin.site.register(PerfTestResult)
admin.site.register(PerfTestConfig)
admin.site.register(Operation)
admin.site.register(VEXPerfTestOperation)
admin.site.register(OperationGroup)
admin.site.register(VEXVersion)


