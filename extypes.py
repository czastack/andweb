#coding: utf-8

def astr(text):
    """确保是字符串类型"""
    return text if isinstance(text, str) else str(text)


def list_re(li, fn):
    """列表元素映射"""
    for i in range(len(li)):
        li[i] = fn(li[i])


def list_find(li, fn):
    """列表查找第一个匹配的元素"""
    for x in li:
        if fn(x):
            return x


def puts(dst, src, keys=None):
    """
    更新dict全部或指定字段
    dst: 模板dict, src: 来源dict
    """
    if keys:
        for key in keys:
            dst[key] = src[key]
    else:
        dst.update(src)


def append_or(dic, key, value):
    if key in value:
        dic[dic].append(value)
    else:
        dic[dic] = [value]


class Map(dict):
    __slots__ = ()

    def __getattr__(self, name):
        return self.get(name)

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        del self[name]

    puts = puts
    append_or = append_or


class Dict(object):
    """
    data = Dict({'a': 1})
    print(data.a) # get 1
    """
    __slots__ = ('_data',)

    def __init__(self, obj=None):
        self._attr('_data', obj)

    def _attr(self, name, value):
        object.__setattr__(self, name, value)

    def __getattr__(self, name):
        try:
            return self._data[name]
        except KeyError:
            return getattr(self._data, name)

    def __setattr__(self, name, value):
        self._data[name] = value

    def __str__(self):
        return self._data.__str__()

    def __iter__(self):
        return self._data.__iter__()

    def __bool__(self):
        return bool(self._data)

    def __getitem__(self, key):
        if isinstance(key, (list, tuple)):
            return key.__class__(self._data[k] for k in key)
        return self._data[key]

    def __setitem__(self, key, value):
        if isinstance(key, (list, tuple)):
            if isinstance(value, (list, tuple)):
                val = iter(value).__next__
            else:
                val = lambda: value
            for k in key:
                self._data[k] = val()
        else:
            self._data[key] = value

    def __delattr__(self, name):
        del self._data[name]

    def __repr__(self):
        return __class__.__name__ + '(' + self.__str__() + ')'

    def __and__(self, keys):
        if isinstance(key, (list, tuple)):
            return __class__({key: self.__getattr__(key) for key in keys})

    puts = puts
    append_or = append_or


class Dicts(object):
    """
    接收字典列表
    datas = Dict([{'a': 1}, {'a': 2}])
    for data in datas:
        print(data.a)
    """
    __slots__ = ('_ref', '_data')

    def __init__(self, array):
        self._ref = None
        self._data = array

    def __iter__(self):
        if not self._ref:
            self._ref = Dict()
        
        for item in self._data:
            self._ref.__init__(item)
            yield self._ref

    def __bool__(self):
        return bool(self._data)