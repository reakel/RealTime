# Create your views here.
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.db.models import Max, Min
from django.core.urlresolvers import reverse
from forms import *
import maketimesheet
from models import Entry
import json

loginurl = 'login'
@login_required
def main_view(request):
    ef = EntryForm()
    form = ef.as_table()
    return render_to_response("main.html", { 'entry_form': form, 'user_fullname':request.user.get_full_name() })

@login_required
def make_timesheet(request):
    if not request.method == "GET": return HttpResponse("FU")
    conds = {'timesheet':None, 'user': request.user}
    if request.GET.get("entries"):
        conds["pk__in"] = json.loads(request.GET["entries"])
        print json.loads(request.GET["entries"])
    entries = Entry.objects.filter(**conds)[:27]
    if entries.count() <= 0:
        return redirect(main_view)
    timesheet = Timesheet(user=request.user)
    timesheet.save()
    timesheet.entry_set = entries
    timesheet.save()
    d = { 'jscode': 'window.location = \"%s#!%i\";' % (reverse(show_timesheets),timesheet.id) }
    return render_to_response("runjs.html", d)


@login_required
def download_timesheet(request):
    filename = '/usr/local/wsgi/timeliste/timesheet/timesheet.doc'
    if not request.method == "GET": return HttpResponse("FU")
    conds = { 'user': request.user}
    ts = Timesheet.objects.filter(**conds).get(pk=request.GET["ts"])
    if not ts.is_downloaded:
        ts.is_downloaded = True
        ts.save()
    data = maketimesheet.make_timesheet(filename,ts)
    response = HttpResponse(mimetype="application/doc")
    response["Content-Disposition"] = "attachment; file-name=timesheet.doc"
    response.write(data)
    return response

@login_required
def show_timesheets(request,*args):
    timesheets = Timesheet.objects.filter(user=request.user).order_by('-pk')
    timesheets = timesheets.annotate(first_date=Min('entry__date'),last_date=Max('entry__date'))
    timesheets = timesheets.values('first_date','last_date','id','is_downloaded')
    return render_to_response("show_timesheets.html", { 'timesheets': timesheets })


def logout_view(request):
    logout(request)
    return render_to_response("logout.html")
