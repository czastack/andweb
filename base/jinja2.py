from jinja2 import Environment
import os.path as Path


class CustomEnvironment(Environment):

    def join_path(self, name, parent=None, globals=None):
        if './' in name:
            return Path.relpath(Path.join(Path.dirname(parent), name))
        else:
            return Environment.join_path(self, name, parent)