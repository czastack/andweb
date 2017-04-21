
def run(app, settings):
    from ..base.jinja2 import CustomEnvironment
    from .taglib import TAGS
    from .filters import FILTERS
    from .handler import BaseHandler
    import sys


    # 加载额外配置
    app.config.update(settings.config)
    app.jinja_env.__class__.join_path = CustomEnvironment.join_path
    BaseHandler.app = app
    BaseHandler.settings = settings

    # 加载自定义标签拓展
    for tag in TAGS:
        app.jinja_env.add_extension(tag)

    # 加载自定义过滤器
    for fn in FILTERS:
        app.add_template_filter(fn)

    @app.route('/<path:url>', methods=('GET', 'POST'))
    def default(url):
        return BaseHandler.dispatch(BaseHandler.request, url)

    @app.route('/')
    def index():
        return default('')

    port = int(sys.argv[1]) if len(sys.argv) is 2 else 5000
    app.run(host='0.0.0.0', debug=True, threaded=True, port=port)