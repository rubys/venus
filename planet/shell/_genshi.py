from StringIO import StringIO

from genshi.input import XMLParser
from genshi.template import Context, MarkupTemplate

def run(script, doc, output_file=None, options={}):
    """ process an Genshi template """

    context = Context(**options)

    tmpl_fileobj = open(script)
    tmpl = MarkupTemplate(tmpl_fileobj, script)
    tmpl_fileobj.close()

    context.push({'input':XMLParser(StringIO(doc))})
    output=tmpl.generate(context).render('xml')

    if output_file:
        out_file = open(output_file,'w')
        out_file.write(output)
        out_file.close()
    else:
        return output
