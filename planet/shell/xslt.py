import os

def run(script, doc, output_file=None):
    """ process an XSLT stylesheet """

    try:
        # if available, use the python interface to libxslt
        import libxml2
        import libxslt
        dom = libxml2.parseDoc(doc)
        docfile = None
    except:
        # otherwise, use the command line interface
        dom = None
        import warnings
        if hasattr(warnings, 'simplefilter'):
            warnings.simplefilter('ignore', RuntimeWarning)
        docfile = os.tmpnam()
        file = open(docfile,'w')
        file.write(doc)
        file.close()

    # do it
    if dom:
        styledoc = libxml2.parseFile(script)
        style = libxslt.parseStylesheetDoc(styledoc)
        result = style.applyStylesheet(dom, None)
        style.saveResultToFilename(output_file, result, 0)
        style.freeStylesheet()
        result.freeDoc()
    else:
        os.system('xsltproc %s %s > %s' % (script, docfile, output_file))

    if dom: dom.freeDoc()
    if docfile: os.unlink(docfile)
