import os.path
import urlparse

from planet import config
from tmpl import template_info

def run(script, doc, output_file=None, options={}):
    """process a Django template file """

    # this is needed to use the Django template system as standalone
    # I need to re-import the settings at every call because I have to 
    # set the TEMPLATE_DIRS variable programmatically
    from django.conf import settings
    settings.configure(
        DEBUG=True, TEMPLATE_DEBUG=True, 
        TEMPLATE_DIRS=(os.path.dirname(script),)
        )
    from django.template import Context
    from django.template.loader import get_template

    context = Context()
    context.update(template_info(doc))

    reluri = os.path.splitext(os.path.basename(output_file))[0]
    context['url'] = urlparse.urljoin(config.link(),reluri)

    t = get_template(script)
    f = open(output_file, 'w')
    f.write(t.render(context))
    f.close()
