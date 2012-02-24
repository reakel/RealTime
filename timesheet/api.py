from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import DjangoAuthorization, Authorization
from models import *
from django.contrib.auth.models import User
from django.db import models
from tastypie.models import create_api_key

models.signals.post_save.connect(create_api_key, sender=User)

class WebAuthentication(BasicAuthentication):
    def is_authenticated(self, request, **kwargs):
        if request.user.is_authenticated():
            return True

        return super(WebAuthentication, self).is_authenticated(request, **kwargs)

    def get_identifier(self, request):
        if request.user.is_authenticated():
            return request.user.username
        else:
            return super(WebAuthentication, self).get_identifier(request)

class EntryResource(ModelResource):
    class Meta:
        queryset = Entry.objects.all().order_by('id')
        authentication = WebAuthentication()
        authorization = DjangoAuthorization()
        filtering = {
                'billed': ('exact',),
                }

    def apply_authorization_limits(self, request, object_list):
        return object_list.filter(user=request.user)

    def obj_create(self, bundle, request=None, **kwargs):
        return super(EntryResource, self).obj_create(bundle, request, user=request.user)

