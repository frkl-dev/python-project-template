from datetime import date
from jinja2 import Template, nodes, runtime, pass_context
from jinja2.ext import Extension

class CurrentYearExtension(Extension):
    def __init__(self, environment):
        super().__init__(environment)
        environment.globals["current_year"] = date.today().year

class RenderStringFilter(Extension):
    def __init__(self, environment):
        super().__init__(environment)
        environment.filters['render_template'] = self.render_template

    @pass_context
    def render_template(self, context, template_string):
        """Filter to render a template string with current context"""
        template = self.environment.from_string(template_string)
        print("----")
        print(list(context.keys()))
        print(context.get("copyright_holder"))
        print(context.get("email"))
        # Use the current template's context, which contains all Copier variables
        return template.render(context)
