from ..html import html_tag
from ...extypes import Dict

class FieldMetaClass(type):
	__slots__ = ()
	def __new__(cls, name, bases, attrs):
		attrs.setdefault('__slots__', ())
		return type.__new__(cls, name, bases, attrs)

class Field(metaclass=FieldMetaClass):
	"""
	Filed基类
	子类要实现的方法：
	__html__(self, name, attrs)
	"""
	__slots__ = ('label', 'attrs', 'index')
	counter = 0

	def __init__(self, label = None, attrs = None):
		self.label = label
		self.attrs = attrs or {}
		self.index = __class__.counter
		__class__.counter += 1

	def html(self, form, name):
		attrs = Dict(self.attrs.copy())
		attrs.setdefault('name', name)

		value = form.data.get(name, None)
		if value is not None:
			attrs.value = value

		return self.__html__(name, attrs)

	def parse_form(self, form, name):
		"""
		:param form: request.form
		:returns 解析得到的值
		"""
		return form.get(name)

class Input(Field):
	input_type = None # 默认为text

	def __html__(self, name, attrs):
		if self.input_type:
			attrs.setdefault('type', self.input_type)

		return html_tag('input', attrs, closed=False)

class Checkbox(Input):
	input_type = 'checkbox'

	def parse_form(self, form, name):
		return form.get(name) is not None

class File(Input):
	input_type = 'file'

class Date(Input):
	input_type = 'date'

class Email(Input):
	input_type = 'email'

class Phone(Input):
	input_type = 'tel'
	pattern    = '^(0|86|17951)?(13[0-9]|15[012356789]|17[0678]|18[0-9]|14[57])[0-9]{8}'

	def __html__(self, name, attrs):
		attrs.setdefault('pattern', self.pattern)
		return Input.__html__(self, name, attrs)

class Hidden(Input):
	input_type = 'hidden'

class Password(Input):
	"""
	For security purposes, this field will not reproduce the value on a form
	submit by default. To have the value filled in, set `hide_value` to `False`.
	"""
	input_type = 'password'
	hide_value = True

	def __html__(self, name, attrs):
		self.hide_value and attrs.pop('value', None)
		return Input.__html__(self, name, attrs)

class Number(Input):
	input_type = 'number'

	def parse_form(self, form, name):
		value = form.get(name)
		if not value:
			value = 0
		elif isinstance(self.attrs.get('step', None), float):
			value = float(value)
		else:
			value = int(value)
		return value

class Submit(Input):
	input_type = 'submit'

	def __html__(self, name, attrs):
		attrs.setdefault('value', '提交')
		return Input.__html__(self, name, attrs)

class ListField(Field):
	"""__choices__: 默认选项"""
	__slots__ = ('choices',)

	def __init__(self, label = None, attrs = None, choices = None):
		Field.__init__(self, label, attrs)
		self.choices = choices or getattr(self, '__choices__', None)

class CheckboxList(ListField):
	def __html__(self, name, attrs):
		items = []
		attrs.type = 'checkbox'
		attrs.pop('required', None)
		checked_value = attrs.pop('value', [])
		if checked_value:
			checked_value = checked_value.split(',')
		for value, text in self.choices:
			# attrs.name = "{0}[{1}]".format(name, value)
			attrs.value = value
			if value in checked_value:
				attrs.checked = True
			else:
				attrs.pop('checked', None)
			input_tag = html_tag('input', attrs, closed=False)
			label_tag = html_tag('label', text=input_tag+text)
			items.append(label_tag)
		return html_tag('div', {'class': 'checkboxlist'}, ' '.join(items))

	def parse_form(self, form, name):
		return form.getlist(name)

class RadioList(ListField):
	def __html__(self, name, attrs):
		items = []
		attrs.type = 'radio'
		attrs.pop('required', None)
		checked_value = attrs.get('value', None)
		for item in self.choices:
			if isinstance(item, str):
				value = item
				text = item
			else:
				value, text = item
			attrs.value = value
			if value == checked_value:
				attrs.checked = True
			else:
				attrs.pop('checked', None)
			input_tag = html_tag('input', attrs, closed=False)
			label_tag = html_tag('label', text=input_tag+text)
			items.append(label_tag)
		return html_tag('div', {'class': 'radiolist'}, ' '.join(items))

class YesNo(RadioList):
	__choices__ = (('true', '是'), ('false', '否'))

	def parse_form(self, form, name):
		value = form.get(name)
		return value == 'true'

class SexChoice(RadioList):
	__choices__ = ('男', '女')

class Select(ListField):
	def __html__(self, name, attrs):
		if self.choices:
			options = []
			option_attrs = Dict({})
			selected_value = attrs.pop('value', None)
			for value, text in self.choices:
				option_attrs.value = value
				if value is selected_value:
					option_attrs.selected = True
				else:
					option_attrs.pop('selected', None)
				options.append(html_tag('option', option_attrs, text))
			options = ''.join(options)
		else:
			options = None
		return html_tag('select', attrs, options)

class MultiSelect(Select):
	def __html__(self, name, attrs):
		attrs.multiple = True
		return Select.__html__(self, name, attrs)

	parse_form = CheckboxList.parse_form

class TextArea(Field):
	def __html__(self, name, attrs):
		text = attrs.pop('value', None)
		return html_tag('textarea', attrs, text)

class AutoCompleteInput(Input):
	"""
	带有自动完成列表的input控件
	choices like: (names, (('this is opt1', 'opt1'), ))
	"""
	__slots__ = ListField.__slots__
	__init__  = ListField.__init__

	def __html__(self, name, attrs):
		if self.choices:
			listid, choices = self.choices
			attrs.list = listid
			options = []
			option_attrs = Dict({})
			for item in choices:
				if isinstance(item, str):
					value = item
					label = None
				else:
					value, label = item
				option_attrs.value = value
				option_attrs.label = label
				options.append(html_tag('option', option_attrs, closed = False))
			options = ''.join(options)
			datalist = html_tag('datalist', {'id': listid}, text = options)
		else:
			datalist = ''
		tag = Input.__html__(self, name, attrs)
		return tag + datalist