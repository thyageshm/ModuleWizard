import os
import webapp2
import jinja2

template_dir = os.path.join(os.path.join(os.path.join(os.path.dirname(__file__), '..'), '..'), 'templates')
jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                                       autoescape=True)

CURRENT_YEAR = "2013/2014"
CURRENT_SEM = "2"

class Handler(webapp2.RequestHandler):
    """Handler Class with Utility functions for Templates"""

    def __write__(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def __render_str__(self, template, **params):
        t = jinja_environment.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.__write__(self.__render_str__(template, **kw))
