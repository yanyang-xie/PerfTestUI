from django.conf.urls import url, patterns

handler404 = 'perf_ui.views.page_not_found'
handler500 = 'perf_ui.views.page_error'

urlpatterns = patterns('perf_ui.views',
    url(r'^$', 'index', name='home'),
    url(r'^result/t6vod$', 'result_vod_t6', name='result_vod_t6_index'),
    url(r'^result/t6linear$', 'result_linear_t6', name='result_linear_t6_index'),
    url(r'^result/t6cdvr$', 'result_cdvr_t6', name='result_cdvr_t6_index'),
)

urlpatterns += patterns('perf_ui.views',
    url(r'^about', 'about', name='about'),
)
