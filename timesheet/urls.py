from django.conf.urls.defaults import *
from api import *
from tastypie.api import Api

v1_api = Api(api_name='v1')
v1_api.register(EntryResource())

urlpatterns = patterns('',
        (r'^api/', include(v1_api.urls)),
        (r'login', 'django.contrib.auth.views.login'),
        )
urlpatterns += patterns('timesheet.views',
        (r'^$', 'main_view'),
        (r'^accounts/profile', 'main_view'),
        (r'^timesheet', 'download_timesheet'),
        (r'^logout', 'logout_view'),
        )
