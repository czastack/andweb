from django import forms
from functools import partial

BS_CLASS = 'form-control'


class MyBaseForm:
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        is_update = kwargs.pop('is_update', False)
        super().__init__(*args, **kwargs)

        if is_update:
            if not hasattr(self, '_id_field'):
                self.__class__._id_field = forms.CharField(widget=forms.HiddenInput())
            self.fields['id'] = self._id_field

    @classmethod
    def set_common_attrs(cls, attrs):
        if attrs:
            for field in cls.base_fields.values():
                field.widget.attrs.update(attrs)

    @classmethod
    def set_common_class(cls, classname):
        for field in cls.base_fields.values():
            attrs = field.widget.attrs
            if attrs.get('class', None):
                attrs['class'] += ' ' + classname
            else:
                attrs['class'] = classname

    @classmethod
    def useplaceholder(cls):
        for field in cls.base_fields.values():
            if isinstance(field, forms.CharField):
                field.widget.attrs['placeholder'] = field.label
        return cls


class FormMetaclass(forms.Form.__class__):
    def __new__(cls, name, bases, attrs):
        common_class = attrs.pop('common_class', None)
        common_attrs = attrs.pop('common_attrs', None)
        theclass = super().__new__(cls, name, bases, attrs)

        if common_class:
            theclass.set_common_class(common_class)

        if common_attrs:
            theclass.set_common_attrs(common_attrs)

        return theclass


class MyForm(forms.Form, MyBaseForm, metaclass=FormMetaclass):
    __slots__ = ()


def model_form(model, fields='__all__', exclude=None, common_class=None, common_attrs=None, meta_attrs=None):
    if meta_attrs is None:
        meta_attrs = {}

    meta_attrs['model'] = model

    if exclude:
        meta_attrs['exclude'] = exclude
    else:
        meta_attrs['fields']  = fields

    cls = type(model.__name__ + 'Form', (MyBaseForm, forms.ModelForm), {
        '__slots__' : (),
        'Meta': type('Meta', (), meta_attrs)
    })

    if common_class:
        cls.set_common_class(common_class)

    if common_attrs:
        cls.set_common_attrs(common_attrs)

    return cls


bs_model_form = partial(model_form, common_class=BS_CLASS)