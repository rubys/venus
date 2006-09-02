from ConfigParser import ConfigParser

# input = foaf, output = ConfigParser
def foaf2config(rdf, baseuri, config=None):

    if not config:
        config = ConfigParser()

    try:
        from RDF import Model, NS, Parser, Statement
    except:
        return config

    if hasattr(rdf, 'read'):
        rdf = rdf.read()

    model = Model()
    def handler(code, level, facility, message, line, column, byte, file, uri):
        pass
    Parser().parse_string_into_model(model,rdf,baseuri,handler)

    dc   = NS('http://purl.org/dc/elements/1.1/')
    foaf = NS('http://xmlns.com/foaf/0.1/')
    rdfs = NS('http://www.w3.org/2000/01/rdf-schema#')

    for statement in model.find_statements(Statement(None,foaf.weblog,None)):
        feed = model.get_target(statement.object,rdfs.seeAlso)
        if not feed: continue

        title = model.get_target(statement.subject,foaf.name)
        if not title: title = model.get_target(statement.object,dc.title)
        if not title: continue

        feed = str(feed.uri)
        if not config.has_section(feed):
            config.add_section(feed)
            config.set(feed, 'name', str(title))

    return config

if __name__ == "__main__":
    import sys, urllib
    config = ConfigParser()

    for uri in sys.argv[1:]:
        foaf2config(urllib.urlopen(uri), uri, config)

    config.write(sys.stdout)

if __name__ == "__main__":
    # small main program which converts FOAF into config.ini format
    import sys, urllib
    config = ConfigParser()
    for foaf in sys.argv[1:]:
        foaf2config(urllib.urlopen(foaf), config)
    config.write(sys.stdout)
