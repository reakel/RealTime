from django.contrib import admin
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

admin.site.register(Entry,EntryAdmin)
admin.site.register(Timesheet, TimesheetAdmin)
