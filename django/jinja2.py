from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse
from ..base.jinja2 import CustomEnvironment


def environment(**options):
    env = CustomEnvironment(**options)
    env.globals.update({
        'static': staticfiles_storage.url,
        'url': reverse,
    })
    return env