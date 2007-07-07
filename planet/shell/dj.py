import os.path
import urlparse
import datetime

import tmpl
from planet import config

def DjangoPlanetDate(value):
    return datetime.datetime(*value[:6])

# remap PlanetDate to be a datetime, so Django template authors can use 
# the "date" filter on these values
tmpl.PlanetDate = DjangoPlanetDate

def run(script, doc, output_file=None, options={}):
    """process a Django template file"""

    # this is needed to use the Django template system as standalone
    # I need to re-import the settings at every call because I have to 
    # set the TEMPLATE_DIRS variable programmatically
    from django.conf import settings
    try:
        settings.configure(
            DEBUG=True, TEMPLATE_DEBUG=True, 
            TEMPLATE_DIRS=(os.path.dirname(script),)
            )
    except EnvironmentError:
        pass
    from django.template import Context
    from django.template.loader import get_template

    # set up the Django context by using the default htmltmpl 
    # datatype converters
    context = Context()
    context.update(tmpl.template_info(doc))
    context['Config'] = config.planet_options()
    t = get_template(script)

    if output_file:
        reluri = os.path.splitext(os.path.basename(output_file))[0]
        context['url'] = urlparse.urljoin(config.link(),reluri)
        f = open(output_file, 'w')
        ss = t.render(context)
        if isinstance(ss,unicode): ss=ss.encode('utf-8')
        f.write(ss)
        f.close()
    else:
        # @@this is useful for testing purposes, but does it 
        # belong here?
        return t.render(context)
