#coding: utf-8
from .. import extypes
import types

# 动态添加的路由

ROUTE_MODULE = 0x10
ROUTE_FUNC   = 0x20
ROUTE_METHOD = 0x40

ARG_NONE = object()


class BaseHandlerDelegate(object):
    __slots__ = ('handler_t', 'func', 'route', 'route_flag')

    def __init__(self, handler_t, func, route, route_flag):
        self.handler_t = handler_t
        self.func = func
        self.route = tuple(route)
        self.route_flag = route_flag


class HandlerAlias(object):
    __slots__ = ('path',)

    def __init__(self, path):
        self.path = path

    def getTarget(self):
        module, name = self.path.rsplit('.', 1)
        return getattr(__import__(module, fromlist=[name]), name)


class Handler(object):
    """
    _template_dir: 见 template_name 的代码
    """

    __slots__ = ('route', 'route_flag')

    APP_GLOBALS = {}
    BACK = '<script>history.go(-1)</script>'


    @classmethod
    def dispatch(cls, request, url):
        """分发请求，根据 pathinfo 调用相应的模块"""
        # 1: app, 2: module, 3: function or class, 4: method
        route = extypes.astr(url).split('/')
        length = len(route)
        settings = cls.settings
        redirect_dir = getattr(settings, 'REDIRECT_DIR', True)

        if length is 1:
            if not url:
                url = 'index'
            if redirect_dir:
                return cls.forward(request, url + '/')

        if not route[-1]:
            route[-1] = 'index'
        elif route[-1].endswith(settings.FILE_EXT):
            # 去掉伪静态后缀
            route[-1] = route[-1][:-len(settings.FILE_EXT)]
        # 调用对应的类或函数
        route_flag = 0
        i = 1
        module = __import__(settings.APP_PREFIX + route[0], fromlist=[route[i]])
        submodule = getattr(module, route[i], None)
        
        # 找到末层子包
        while (isinstance(submodule, types.ModuleType)
            and submodule.__package__ == submodule.__name__):
            i += 1
            if length is i and redirect_dir:
                return cls.forward(request, '/%s/' % url)
            submodule = __import__(submodule.__name__, fromlist=[route[i]])
            submodule = getattr(submodule, route[i], None)

        if isinstance(submodule, types.ModuleType):
            route_flag |= ROUTE_MODULE
            module = submodule

        # 如果路由只有2层，则调用该模块下的index函数处理
        # 3层：调用模块下route[1]同名函数处理，
        # 若未找到，调用模块下default_handler函数处理
        # 4层：调用模块下的类/方法
        lv_module = i + (route_flag & ROUTE_MODULE is not 0) # 模块最低层级
        lv_class  = 1 + lv_module # 类最低层级
        route_flag |= lv_module # lv_module要求小于16

        if length is lv_module and redirect_dir:
            if url.endswith('/'):
                url += 'index'
            return cls.forward(request, '/%s/' % url)

        name = route[lv_module]
        v = lambda n: (n, getattr(module, n)) if hasattr(module, n) else None
        callee = (v(name + settings.HANDLE_FN_SUFFIX) or v(name.title().replace('-', '') + settings.HANDLE_CLASS_SUFFIX)
            or v(settings.HANDLE_FN_DEFAULT) or v(settings.HANDLE_CLASS_DEFAULT))

        if callee:
            name, callee = callee
        else:
            cls.raise404()

        delegate = None

        if isinstance(callee, HandlerAlias):
            callee = callee.getTarget()

        if isinstance(callee, types.FunctionType):
            route_flag |= ROUTE_FUNC
            delegate = cls.HandlerDelegate(None, callee, route, route_flag)
        elif isinstance(callee, type):
            if name == settings.HANDLE_CLASS_DEFAULT:
                lv_class -= 1
            if length <= lv_class and redirect_dir:
                return cls.forward(request, '/%s/' % url)
            action = route[lv_class] # 方法名
            method = getattr(callee, action, None) or getattr(callee, 'default', None)
            if method:
                route_flag |= ROUTE_METHOD
                delegate = cls.HandlerDelegate(callee, method, route, route_flag)
            else:
                cls.raise404('%s不存在%s方法' % (callee, action))
        else:
            cls.raise404()
        if delegate:
            cls.save_route(url, delegate)
            result = delegate(request)
        return result


    def __init__(self, route, route_flag):
        if not isinstance(route, tuple):
            route = tuple(route)
        self.route = route
        self.route_flag = route_flag

        if route[0] not in self.APP_GLOBALS:
            data = self.APP_GLOBALS[route[0]] = {}
            if hasattr(self.settings, 'APP_GLOABLS'):
                for k, v in self.settings.APP_GLOABLS.items():
                    if isinstance(v, types.FunctionType):
                        v = v(self)
                    data[k] = v
            self.oninit_appdata(data)


    # 在url调用其他方法前执行，如果有返回值则直接返回，不调用其他方法
    # 可用于在整个类的验证登录
    def oninit(self):
        pass

    def oninit_appdata(self, data):
        pass

    def url(self, url, start_with_sep=False):
        """
        @会替换成模块名（同一个父级）
        :param start_with_sep: 是否要以/开头
        """
        if not url.startswith('/'):
            url = self.appid + '/' + url
            if start_with_sep:
                url = '/' + url
        elif not start_with_sep:
            url = url[1:]
        if '@' in url:
            url = url.replace('@', (self.route[1] + '/') if len(self.route) > 2 else '')
        return url

    def render(self, tpl=None, **data):
        tpl = (tpl or self.template_name()) + '.html'
        tpl = self.url(tpl)
        data['handler'] = self

        for k, v in self.APP_GLOBALS[self.appid].items():
            data.setdefault(k, v)
        
        return self.rawrender(tpl, data)

    def template_name(self, action=None, tpldir=None):
        if action:
            route = list(self.route)
            route[-1] = action
        else:
            route = self.route
        if tpldir is None and hasattr(self, '_template_dir'):
            tpldir = self._template_dir
        if tpldir:
            return tpldir + '/' + self.route[-1]
        else:
            return '/'.join(route[1:])
            # split = (self.route_flag & 0xF) + 1 # lv_module + 1
            # return '/'.join(route[1:split]) + '-' + '-'.join(route[split:])

    def page_url(self, route, **query):
        """
        生成页面url
        /开头的路由表示跨应用
        """
        url = self.url(route, True)
        if self.settings.FAKE_STATIC:
            url += self.settings.FAKE_STATIC_EXT
        if query:
            query_str = '&'.join(key+'='+extypes.astr(val) for key, val in query.items())
            url += ('&' if '?' in url else '?') + query_str
        return url

    def action(self, name='', level=0):
        """
        生成同级url操作
        :param level: 保留route层数，0为保留至倒数第二层
        """
        route = list(self.route)
        if level:
            del route[level+1:]
        route[-1] = name
        url = '/' + '/'.join(route)
        if name and self.settings.FAKE_STATIC:
            url += self.settings.FAKE_STATIC_EXT
        return url

    def get_arg(self, key, default=ARG_NONE):
        """获取参数，包括get和form"""
        args = self._query_dict
        value = args.get(key, default)
        if value is ARG_NONE:
            raise ValueError('miss arg ' + key)
        return value

    def get_args(self, keys):
        args = self._query_dict
        return extypes.Map({key: args.get(key, '') for key in keys})

    def get_args_adv(self, keys, default=ARG_NONE):
        args = self._query_dict
        data = extypes.Dict({})
        for key in keys:
            if isinstance(key, (list, tuple)):
                if len(key) == 2:
                    key, value_t = key
                else:
                    key, value_t, default = key
                value = args.get(key, default)
                if value is not ARG_NONE:
                    value = value_t(value)
                else:
                    raise ValueError('miss arg ' + key)
            else:
                value = args.get(key, default)
                if value is ARG_NONE:
                    raise ValueError('miss arg ' + key)
            data[key] = value
        return data

    def goback(self):
        refer = self.referer
        if refer:
            return self.redirect(refer)

    def toaction(self, action):
        return self.redirect(self.action(action))

    @staticmethod
    def forward(request, url):
        raise NotImplementedError

    @staticmethod
    def redirect(url):
        raise NotImplementedError

    @classmethod
    def guessUrl(cls, action=None, startRoot=True):
        arr = cls.__module__.split('.')
        if startRoot:
            arr[0] = ''
        else:
            arr.pop(0)
        if cls.__name__ != cls.settings.HANDLE_CLASS_DEFAULT:
            arr.append(arr)
        if action:
            arr.append(action)
        return '/'.join(arr)

    @classmethod
    def guessFnUrl(cls, fn):
        arr = fn.__module__.split('.')
        if startRoot:
            arr[0] = ''
        else:
            arr.pop(0)
        if fn.__name__ != cls.settings.HANDLE_FN_DEFAULT:
            arr.append(arr)
        return '/'.join(arr)

    @property
    def appid(self):
        return self.route[0]

    @property
    def is_get(self):
        return self.request.method == 'GET'

    @property
    def is_post(self):
        return self.request.method == 'POST'

    @property
    def page_name(self):
        return self.route[-1]


class ForceResult(Exception):
    pass
