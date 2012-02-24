from django.contrib import admin
from models import *

class EntryAdmin(admin.ModelAdmin):
    model = Entry
    fields = ('date', 'start_time', 'end_time', 'user')
    list_display = ('user', 'date', 'start_time', 'end_time', 'billed')
    list_filter = ('date',)
    search_fields = ('user__username',)
    extra = 10

admin.site.register(Entry,EntryAdmin)
