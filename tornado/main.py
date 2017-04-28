from tornado import ioloop, web
from .handler import allroutes, BaseHandler
from ..base import settings
from ..extypes import Dict
import os
import sys

BASE_DIR = os.getcwd()

defaultsettings = { 
    "static_path" :   os.path.join(BASE_DIR, "static"), 
    "template_path" : os.path.join(BASE_DIR, "templates"), 
    "gzip" : True, 
    "debug" : True, 
}

def run(settings=settings, routes=None):
    port = int(sys.argv[1]) if len(sys.argv) is 2 else 8000
    thesettings = dict(defaultsettings)

    if routes:
        allroutes[:0] = routes

    if isinstance(settings, dict):
        thesettings.update(settings)
    else:
        for key in dir(settings):
            if not key.startswith('__'):
                thesettings[key] = getattr(settings, key)

    app = web.Application(allroutes, **thesettings)
    BaseHandler.settings = Dict(app.settings)
    app.listen(port)
    ioloop.IOLoop.instance().start()
