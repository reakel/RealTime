from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from models import *


class EntryAdmin(admin.ModelAdmin):
    model = Entry
    fields = ('date', 'start_time', 'end_time', 'user',)
    list_display = ('user', 'date', 'start_time', 'end_time')
    list_filter = ('date',)
    search_fields = ('user__username',)
    extra = 10

class EntryInline(admin.TabularInline):
    model = Entry
    extra = 10

class TimesheetAdmin(admin.ModelAdmin):
    model = Timesheet
    inlines = [ EntryInline ]

class UserProfileInline(admin.StackedInline):
    model = UserProfile
     
class UserProfileAdmin(UserAdmin):
    inlines = [UserProfileInline]

#Uncomment the two following lines to include userprofile in UserAdmin
#admin.site.unregister(User)
#admin.site.register(User, UserProfileAdmin)

admin.site.register(Entry,EntryAdmin)
admin.site.register(Timesheet, TimesheetAdmin)
