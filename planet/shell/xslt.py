import os

def quote(string, apos):
    """ quote a string so that it can be passed as a parameter """
    if type(string) == unicode:
        string=string.encode('utf-8')
    if apos.startswith("\\"): string.replace('\\','\\\\')

    if string.find("'")<0:
        return "'" + string + "'"
    elif string.find('"')<0:
        return '"' + string + '"'
    else:
        # unclear how to quote strings with both types of quotes for libxslt
        return "'" + string.replace("'",apos) + "'"

def run(script, doc, output_file=None, options={}):
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

    # do it
    result = None
    if dom:
        styledoc = libxml2.parseFile(script)
        style = libxslt.parseStylesheetDoc(styledoc)
        for key in options.keys():
            options[key] = quote(options[key], apos="\xe2\x80\x99")
        output = style.applyStylesheet(dom, options)
        if output_file:
            style.saveResultToFilename(output_file, output, 0)
        else:
            result = output.serialize('utf-8')
        style.freeStylesheet()
        output.freeDoc()
    elif output_file:
        import warnings
        if hasattr(warnings, 'simplefilter'):
            warnings.simplefilter('ignore', RuntimeWarning)
        docfile = os.tmpnam()
        file = open(docfile,'w')
        file.write(doc)
        file.close()

        cmdopts = []
        for key,value in options.items():
           if value.find("'")>=0 and value.find('"')>=0: continue
           cmdopts += ['--stringparam', key, quote(value, apos=r"\'")]

        os.system('xsltproc %s %s %s > %s' %
            (' '.join(cmdopts), script, docfile, output_file))
        os.unlink(docfile)
    else:
        import sys
        from subprocess import Popen, PIPE

        options = sum([['--stringparam', key, value]
            for key,value in options.items()], [])

        proc = Popen(['xsltproc'] + options + [script, '-'],
            stdin=PIPE, stdout=PIPE, stderr=PIPE)

        result, stderr = proc.communicate(doc)
        if stderr:
            import planet
            planet.logger.error(stderr)

    if dom: dom.freeDoc()

    return result
