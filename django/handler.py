from django.http import HttpResponse, HttpResponseRedirect, Http404
# from django.template.context_processors import csrf
from django.template.loader import render_to_string
from django.conf.urls import url as url_t
from django.conf import settings
from ..base.handler import *
import json

subpatterns = []

class HandlerDelegate(BaseHandlerDelegate):
    def __call__(self, request):
        try:
            if self.handler_t is None:
                result = self.func(BaseHandler(request, self.route, self.route_flag))
            else:
                ins = self.handler_t(request, self.route, self.route_flag)
                result = ins.oninit() or self.func(ins)
        except ForceResult as e:
            result = e.args[0]

        if not isinstance(result, HttpResponse):
            if not isinstance(result, str):
                result = str(result)
            result = HttpResponse(result)
        return result


class BaseHandler(Handler):
    __slots__ = ('request',)

    STAY = HttpResponse(status=204)
    REFRESH = HttpResponse()
    REFRESH["Refresh"] = "0"
    INDEX = HttpResponseRedirect('index')
    HandlerDelegate = HandlerDelegate

    redirect = staticmethod(HttpResponseRedirect)
    settings = settings

    def __init__(self, request, route, route_flag):
        self.request = request
        super().__init__(route, route_flag)

    @staticmethod
    def raise404(*args):
        raise Http404(*args)

    @staticmethod
    def save_route(url, delegate):
        subpatterns.append(url_t('^%s$' % url, delegate))

    @classmethod
    def classforward(cls, request, url):
        query_string = request.META.get('QUERY_STRING', None)
        if query_string:
            url += '?' + query_string
        return cls.redirect(url)

    def rawrender(self, tpl, data):
        # data.update(csrf(self.request))
        return render_to_string(tpl, data)

    def json(self, obj):
        return HttpResponse(json.dumps(obj), content_type="application/json")

    def get_or_404(self, model, msg='', **query):
        try:
            return model.objects.get(**query)
        except model.DoesNotExist:
            self.raise404(msg)

    @property
    def query_dict(self):
        request = self.request
        return getattr(request, request.method, request.GET)

    @property
    def referer(self):
        return self.request.META.get('HTTP_REFERER', None)

    @property
    def is_ajax(self):
        return self.request.is_ajax()

    @property
    def session(self):
        return self.request.session

    @property
    def user(self):
        return self.request.user


class AssignableHandler(BaseHandler):
    __slots__ = ('variables',)

    def oninit(self):
        super().oninit()
        self.variables = {}

    def render(self, tpl=None, **data):
        for k, v in self.variables.items():
            data.setdefault(k, v)
        return super().render(tpl, **data)

    def assign(self, name, value):
        self.variables[name] = value

    def unassign(self, name):
        return self.variables.pop(name, None)