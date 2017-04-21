from .fields import Field
from ...extypes import Dict

class FormMetaclass(type):
	def __new__(cls, name, bases, attrs):
		# 排除Model类本身:
		if not attrs.get('__abstract__', False):
			# 获取所有的Field
			nofields = '__fields__' not in attrs
			if nofields:
				fields = []
				parentfields = []
				for parent in bases:
					if parent is not Form and issubclass(parent, Form):
						parentfields += parent.__fields__
			getlabel = attrs.pop('__label__', None)
			common_class = attrs.pop('common_class', None)
			common_attrs = attrs.pop('common_attrs', None)

			for name, field in attrs.items():
				if isinstance(field, Field):
					# 根据name获取label
					if hasattr(field.label, '__call__'):
						field.label = field.label(name)
					elif field.label is None and getlabel:
						field.label = getlabel(name)					

					if common_class:
						if field.attrs.get('class', None):
							field.attrs['class'] += ' ' + common_class
						else:
							field.attrs['class'] = common_class

					if common_attrs:
						for item in common_attrs.items():
							field.attrs.setdefault(*item)

					if nofields: fields.append(name)
			if nofields:
				fields.sort(key=lambda x: attrs[x].index)
				if parentfields:
					parentfields += fields
					fields = parentfields
				attrs['__fields__'] = fields
			attrs['__slots__'] = ('data', )
		return type.__new__(cls, name, bases, attrs)

class Form(metaclass=FormMetaclass):
	"""
	表单基类
	成员只有data: 表单的值dict
	__fields__:   决定实际使用的表单项及顺序
	__abstract__: 此为抽象类
	__label__:    根据name获取label的函数
	common_class: 表单控件公共class
	common_attrs: 表单控件公共属性
	"""

	__abstract__ = True

	def __init__(self, data = None):
		"""
		:param data: 数据字典
		"""
		if type(data).__name__ is 'ImmutableMultiDict':
			# 接收request.form
			self.data = Dict({})
			for name in self.__fields__:
				self.data[name] = getattr(self, name).parse_form(data, name)
		else:
			self.data = Dict(data.copy() if data is not None else {})

	def __iter__(self):
		"""
		渲染html时调用
		yield (label, field_html)
		"""
		for name, field in self.iterfields():
			yield name, field.label, field.html(self, name)

	def field_html(self, name):
		return getattr(self, name).html(self, name)

	@classmethod
	def iterfields(cls):
		"""表单项迭代"""
		for name in cls.__fields__:
			yield name, getattr(cls, name)