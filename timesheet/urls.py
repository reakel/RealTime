from django.conf.urls.defaults import *
from api import *
from tastypie.api import Api

v1_api = Api(api_name='v1')
v1_api.register(EntryResource())
v1_api.register(TimesheetResource())

urlpatterns = patterns('',
        (r'^api/', include(v1_api.urls)),
        (r'login/', 'django.contrib.auth.views.login'),
        (r'^changepass/$', 'django.contrib.auth.views.password_change'),
        (r'^donechangepass/$', 'django.contrib.auth.views.password_change_done'),
        )
urlpatterns += patterns('timesheet.views',
        (r'^$', 'main_view'),
#        (r'^accounts/profile', 'main_view'),
        (r'^profile/$', 'edit_userprofile'),
        (r'^timesheet/$', 'show_timesheets'),
        (r'^downloadtimesheet/timesheet(\d+)L?.doc$', 'download_timesheet'),
        (r'^maketimesheet/$', 'make_timesheet'),
        (r'^delete_timesheet/(\d+)L?/$', 'delete_timesheet'),
        (r'^logout/$', 'logout_view'),
        )
