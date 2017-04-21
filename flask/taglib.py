#encoding: utf8
from jinja2 import nodes
from jinja2.ext import Extension


# 只有一个参数的自闭合标签
class SimSingleTag(Extension):
    __slots__ = ()

    def parse(self, parser):
        # 要先移到下一个
        next(parser.stream)
        # 第一个表达式参数
        args = [nodes.Name('handler', 'load'), parser.parse_expression()]
        if parser.stream.skip_if('comma'):
            args.append(parser.parse_expression())
        return nodes.CallBlock(self.call_method('_run', args), [], [], '')

    def _run(self, handler, *arg, caller):
        return self.run(handler, *arg)


class CSS_JS_Tag(SimSingleTag):
    __slots__ = ()

    def run(self, handler, files, parent = None):
        if parent is True:
            parent = handler.appid
        parent = (parent + '/' + self.TAG) if parent else self.TAG
        url = lambda file: self.static_url(handler, file, parent) + '.' + self.TAG
        if isinstance(files, str):
            files = files.split(',')
        return ''.join(self.TAG_PART.format(url(file.strip())) for file in files)

    # def preprocess(self, source, name, filename=None):
    #   return source

    @staticmethod
    def static_url(handler, filename, parent=''):
        """生成静态资源url"""
        if parent and not parent.endswith('/'):
            parent += '/'
        path = handler.app.static_url_path + '/'
        return path + parent + filename


class CssTag(CSS_JS_Tag):
    __slots__ = ()
    TAG = 'css'
    tags = set([TAG])
    TAG_PART = '<link rel="stylesheet" href="{0}">'


class JsTag(CSS_JS_Tag):
    __slots__ = ()
    TAG = 'js'
    tags = set([TAG])
    TAG_PART = '<script src="{0}"></script>'


# class CssJsTag(SimSingleTag):
#     __slots__ = ()
#     tags = set(['cjs'])
#     def run(self, *args):
#         return CssTag.run(CssTag, *args) + JsTag.run(JsTag, *args)


class LangTag(SimSingleTag):
    __slots__ = ()
    tags = set(['lang'])

    def run(self, handler, is_en):
        return 'lang="%s"' % ('en' if is_en else 'zh-cmn-Hans')


TAGS = (CssTag, JsTag, LangTag)