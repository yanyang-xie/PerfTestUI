from django.conf.urls import url, patterns

handler404 = 'perf_ui.views.page_not_found'
handler500 = 'perf_ui.views.page_error'

urlpatterns = patterns('perf_ui.views',
    url(r'^$', 'index', name='home'),
)

urlpatterns += patterns('perf_ui.views',
    url(r'^about', 'about', name='about'),
)
