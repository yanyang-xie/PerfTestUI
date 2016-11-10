from django.contrib import admin

from perfui.models import PerfTestResult, PerfTestConfig, Operation

# Register your models here.
admin.site.register(PerfTestResult)
admin.site.register(PerfTestConfig)
admin.site.register(Operation)
