#encoding: utf8

import functools
import locale
import time


KEY_NAME = lambda x: x['name']

def sort_pinyin_init():
    locale.setlocale(locale.LC_COLLATE, 'zh_CN.UTF8')


def sort_pinyin_keyfn(keyfn=None):
    key = locale.strcoll if not keyfn else lambda a, b: locale.strcoll(keyfn(a), keyfn(b))
    return functools.cmp_to_key(key)


def sort_pinyin(a, keyfn=None):
    return sorted(a, key=sort_pinyin_keyfn(keyfn))


def sort_pinyin_name(a):
    return sort_pinyin(a, lambda x: x.name)


def values_group_by(source, key):
    """根据指定属性分组，用于select联动"""
    data = {}
    if hasattr(source, 'objects'):
        source = source.objects
    if hasattr(source, 'values'):
        source = source.values()
    for item in source:
        val = item.pop(key)
        try:
            val = str(val)
        except:
            pass
        if val not in data:
            data[val] = []
        data[val].append(item)
    return data


def cacheproperty(func):
    def _deco(self):
        name = '_' + func.__name__
        val = getattr(self, name, None)
        if val is None:
            val = func(self)
            setattr(self, name, val)
        return val
    return property(_deco)


def cacheclassproperty(func):
    def _deco(self):
        name = '_' + func.__name__
        val = getattr(self.__class__, name, None)
        if val is None:
            val = func(self)
            setattr(self.__class__, name, val)
        return val
    return property(_deco)


def ordered_dict_getitem(items, key):
    """
    用元组或列表第一个元素作为键获取
    """
    for item in items:
        if item[0] == key:
            return item[1]


def timestr(t, show_time=True):
    """ 
    时间戳转日期字符串
    :p show_time: 是否显示时分秒
    """
    ltime=time.localtime(t)
    fmt = "%Y-%m-%d"
    if show_time:
        fmt += " %H:%M:%S"
    return time.strftime(fmt, ltime)