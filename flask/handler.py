from flask import render_template as render, redirect, jsonify, abort
from werkzeug import Response
from ..base.handler import *


class HandlerDelegate(BaseHandlerDelegate):
    def __call__(self, request=None):
        try:
            if self.handler_t is None:
                result = self.func(BaseHandler(self.route, self.route_flag))
            else:
                ins = self.handler_t(self.route, self.route_flag)
                result = ins.oninit() or self.func(ins)
        except ForceResult as e:
            result = e.args[0]
        if not isinstance(result, (str, tuple, Response)):
            result = str(result)
        return result


class BaseHandler(Handler):
    __slots__ = ()

    STAY = '', 204
    REFRESH = '', 200, {"Refresh": "0"}

    from flask import request, session
    json = staticmethod(jsonify)
    redirect = staticmethod(redirect)
    HandlerDelegate = HandlerDelegate

    @staticmethod
    def raise404(*args):
        abort(404)

    @classmethod
    def save_route(cls, url, delegate):
        app = cls.app
        endpoint = hex(id(delegate))
        rule = app.url_rule_class('/' + url, methods={'GET', 'POST'}, endpoint=endpoint)
        app.url_map.add(rule)
        app.view_functions[endpoint] = delegate

    @classmethod
    def classforward(cls, request, url):
        query_string = request.query_string
        if query_string:
            url += '?' + str(query_string)
        return cls.redirect(url)

    def rawrender(self, tpl, data):
        return render(tpl, **data)

    @property
    def _query_dict(self):
        return self.request.values

    @property
    def referer(self):
        return self.request.headers.get('referer', None)

    @property
    def is_ajax(self):
        return self.request.is_xhr



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