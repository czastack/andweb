from tornado import web
from ..base.handler import *

class DispatchHandler(web.RequestHandler):
    def get(self, path):
        result = BaseHandler.dispatch(self, path)
        if result is not None:
            self.write(result)

    def post(self, path):
        return self.get()


class HandlerDelegate(BaseHandlerDelegate):
    def __call__(self, request=None):
        try:
            self.request = request
            handler_t = self.handler_t or BaseHandler
            ins = self.handler_t(request.application, request.request,
                delegate=self)
            ins._write_buffer = request._write_buffer
            result = ins.oninit() or self.func(ins)
        except ForceResult as e:
            result = e.args[0]
        if result and not isinstance(result, (str, bytes, dict)):
            result = str(result)
        return result


class QureyDict:
    __slots__ = ('request')

    def __get__(self, obj, cls=None):
        self.request = obj
        return self

    def get(self, name, default=[]):
        return self.request.get_argument(name, default)

    def getlist(self, name, default=[]):
        return self.request.get_arguments(name, default)


class BaseHandler(Handler, web.RequestHandler):
    __slots__ = ()

    STAY = '', 204
    REFRESH = '', 200, {"Refresh": "0"}

    # json = staticmethod(jsonify)
    # redirect = staticmethod(redirect)
    HandlerDelegate = HandlerDelegate

    query_dict = QureyDict()

    def __init__(self, application, request, **kwargs):
        web.RequestHandler.__init__(self, application, request, **kwargs)

    def initialize(self, delegate):
        Handler.__init__(self, delegate.route, delegate.route_flag)
        self.func = delegate.func

    def oninit(self):
        return self.prepare()

    def get(self):
        self.func(self)

    def post(self):
        self.get()

    @staticmethod
    def raise404(*args):
        raise web.HTTPError(404)

    @classmethod
    def save_route(cls, url, delegate):
        handlers = delegate.request.application.handlers[0]
        del delegate.request
        if handlers[0].pattern == '.*$':
            handlers[1].insert(-1, web.URLSpec('/' + url, delegate.handler_t or BaseHandler, {'delegate': delegate}))

    @classmethod
    def classforward(cls, request, url):
        query_string = request.request.query
        if query_string:
            url += '?' + query_string
        return request.redirect(url)

    def rawrender(self, tpl, data):
        return web.RequestHandler.render(self, tpl, **data)

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


allroutes = [
    (r"/(.*)", DispatchHandler)
]