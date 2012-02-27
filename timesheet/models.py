from django.db import models
from django.contrib.auth.models import User
from datetime import time
from django.core.exceptions import ValidationError

def timediff(t1,t2):
    diff = (t1.hour-t2.hour)*60+t1.minute-t2.minute
    if (diff<0):
        diff += 24*60
    return diff/60.0
# Create your models here.
class Timesheet(models.Model):
    user = models.ForeignKey(User)

class Entry(models.Model):
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    user = models.ForeignKey(User)
    timesheet = models.ForeignKey(Timesheet, null=True, blank=True)

    def get_timediff(self):
        return timediff(self.end_time,self.start_time)

    def get_timediffstring(self):
        diff = self.get_timediff()
        return "% 2.2f" % diff
    def get_shortdatestring(self):
        return "%02i.%02i" % (self.date.day, self.date.month)
    def get_weeknumber(self):
        return self.date.isocalendar()[1]
    def save(self, *args, **kwargs):
        if (self.start_time>=self.end_time): raise ValidationError("Requirement: start time < end time")
        c = Entry.objects.filter(
                user=self.user, 
                date=self.date,
                start_time__lte=self.start_time,
                end_time__gt=self.start_time
                ).count()
        if c > 0 and not self.id: raise ValidationError("Cannot create multiple entries in the same time interval")
        c = Entry.objects.filter(
                user=self.user, 
                date=self.date,
                start_time__lt=self.end_time,
                end_time__gte=self.end_time
                ).count()
        if c > 0 and not self.id: raise ValidationError("Cannot create multiple entries in the same time interval")
        c = Entry.objects.filter(user=self.user, timesheet=None).count()
        if c > 27: raise ValidationError("Limit reached. Please bill current entries before adding more")
        super(Entry,self).save(args, kwargs)

