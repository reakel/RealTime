# Create your views here.
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.forms import PasswordChangeForm
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect
from django.db.models import Max, Min
from django.core.urlresolvers import reverse
from django.template import RequestContext, Context
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt
import os
from settings import SITE_ROOT
from forms import *
import maketimesheet
from models import Entry, Timesheet
import json

loginurl = 'login'
@login_required
def main_view(request):
    ef = EntryForm()
    form = ef.as_table()
    c = RequestContext(request,{ 'entry_form': form, 'user':request.user })
    t = get_template('main.html')
    return HttpResponse(t.render(c))

@login_required
@csrf_exempt
def make_timesheet(request):
    if not request.method == "POST": raise Http404
    try:
        indata= json.loads(request.raw_post_data)
        entry_ids = [ int(i) for i in indata["entries"] ]
    except:
        raise Http404
    if len(entry_ids) == 0: raise Http404
    conds = {
            'pk__in': entry_ids,
            'timesheet':None, 
            'user': request.user
            }
    entries = Entry.objects.filter(**conds)[:27]
    if entries.count() <= 0:
        return HttpResponse('{ "success":false, "url":"" }', mimetype="application/json") 
    timesheet = Timesheet(user=request.user)
    timesheet.save()
    timesheet.entry_set = entries
    timesheet.save()
    d = { 'jscode': 'window.location = \"%s#!%i\";' % (reverse(show_timesheets),timesheet.id) }
    return HttpResponse('{ "success":true, "url":"%s#!%i" }' % (reverse(show_timesheets),timesheet.id), mimetype="application/json")


@login_required
def download_timesheet(request):
    filename = os.path.join(SITE_ROOT,'timesheet/timesheet.doc')
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
    #timesheets = timesheets.values('first_date','last_date','id','is_downloaded')
    return render_to_response("show_timesheets.html", { 'timesheets': timesheets, 'user':request.user })


def logout_view(request):
    logout(request)
    return redirect(main_view)

@login_required
def edit_userprofile(request):
    if request.method == "POST":
        uf = UserForm(request.POST, instance=request.user)
        ufp = UserProfileForm(request.POST, instance=request.user.get_profile())
        uf.save()
        ufp.save()
    uf = UserForm(instance=request.user)
    upf = UserProfileForm(instance=request.user.get_profile())
    t = get_template('userprofile.html')
    c = RequestContext(request, { 'user_form': uf, 'user_profile_form': upf })
    return HttpResponse(t.render(c))

@login_required
def change_password(request):
    if request.method == "POST":
        pf = PasswordChangeForm(request.POST, instance=request.user)
        if pf.is_valid():
            pf.save()
            return HttpResponse("OK")
        else:
            return HttpResponse("FU")
    else:
        pf = PasswordChangeForm(request.user)
        c = RequestContext(request, { 'password_form': pf })
        t = get_template("changepass.html")
        return HttpResponse(t.render(c))
