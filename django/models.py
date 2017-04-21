from django.db import models
from django.contrib import admin
from django.forms.models import model_to_dict


def register_model(ms):
    todo = []

    for key in ms.__dict__:
        if key.startswith('_'):
            continue

        m = ms.__dict__[key]

        if isinstance(m, type) and issubclass(m, models.Model) and not m._meta.abstract and m not in admin.site._registry:
            todo.append(m)

    admin.site.register(todo)


class BaseModel(models.Model):
    class Meta:
        abstract = True

    @classmethod
    def iter_field(self, fields=None, exclude=None):
        return (field for field in self._meta.fields if not 
            ((exclude and field.name in exclude) or (fields and field.name not in fields)))

    @classmethod
    def iter_label(self, fields=None, exclude=None):
        return ((field.name, field.verbose_name) for field in self.iter_field(fields, exclude))

    def iter_label_value(self, fields=None, exclude=None):
        for field in self.iter_field(fields, exclude):
            if isinstance(field, models.ForeignKey):
                value = str(getattr(self, field.name))
            else:
                value = self._get_FIELD_display(field)
            yield field.name, field.verbose_name, value

    def to_dict(self, *args, **kwargs):
        return model_to_dict(self, *args, **kwargs)