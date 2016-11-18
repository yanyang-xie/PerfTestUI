from django.conf.urls import url, patterns

handler404 = 'perfui.views.page_not_found'
handler500 = 'perfui.views.page_error'

urlpatterns = patterns('perfui.views',
    url(r'^$', 'index', name='home'),
    url(r'^result/(?P<test_type>.+)', 'show_perf_result', name='perf_result'),
)

urlpatterns += patterns('perfui.op_views',
    url(r'^op$', 'index', name='op-home'),
    url(r'^op/update$', 'update_operation_config', name='update_operation_config'),
    url(r'^op/execute$', 'operation', name='operation'),
)

#urlpatterns += patterns('perfui.views',
#    url(r'^about', 'about', name='about'),
#)
