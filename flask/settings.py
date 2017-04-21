from ..base.settings import *


APP_GLOABLS = {
    'STATIC': lambda h: h.app.static_url_path + '/',
    'APPSTATIC': lambda h: '{}/{}/'.format(h.app.static_url_path, h.appid),
    'APPURL': lambda h: '/' + h.appid + '/',
}