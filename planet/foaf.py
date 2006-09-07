from ConfigParser import ConfigParser

# input = foaf, output = ConfigParser
def foaf2config(rdf, config):

    if not config or not config.sections():
        return

    # there should be only be 1 section
    section = config.sections().pop()

    try:
        from RDF import Model, NS, Parser, Statement
    except:
        return

    if hasattr(rdf, 'read'):
        rdf = rdf.read()

    # account mappings, none by default
    # form: accounts = {url to service homepage (as found in FOAF)}|{URI template}\n*
    # example: http://del.icio.us/|http://del.icio.us/rss/{foaf:accountName}
    accounts = {}
    if(config.has_option(section, 'online_accounts')):
        values = config.get(section, 'online_accounts')
        for account_map in values.split('\n'):
            try:
                homepage, map = account_map.split('|')
                accounts[homepage] = map
            except:
                pass

    model = Model()
    def handler(code, level, facility, message, line, column, byte, file, uri):
        pass
    Parser().parse_string_into_model(model,rdf,section,handler)

    dc   = NS('http://purl.org/dc/elements/1.1/')
    foaf = NS('http://xmlns.com/foaf/0.1/')
    rdfs = NS('http://www.w3.org/2000/01/rdf-schema#')

    for statement in model.find_statements(Statement(None,foaf.weblog,None)):

        # feed owner
        person = statement.subject
        
        feed = model.get_target(statement.object,rdfs.seeAlso)
        if not feed: continue

        title = model.get_target(person,foaf.name)
        if not title: title = model.get_target(statement.object,dc.title)
        if not title: continue

        feed = str(feed.uri)
        if not config.has_section(feed):
            config.add_section(feed)
            config.set(feed, 'name', str(title))

        # if we don't have mappings, we're done
        if not accounts.keys():
            continue

        # now look for OnlineAccounts for the same person
        for statement in model.find_statements(Statement(person,foaf.holdsAccount,None)):
            rdfaccthome = model.get_target(statement.object,foaf.accountServiceHomepage)
            rdfacctname = model.get_target(statement.object,foaf.accountName)

            if not rdfaccthome or not rdfacctname: continue

            if not rdfaccthome.is_resource() or not accounts.has_key(str(rdfaccthome.uri)): continue

            if not rdfacctname.is_literal(): continue

            rdfacctname = rdfacctname.literal_value['string']
            rdfaccthome = str(rdfaccthome.uri)

            # shorten feed title a bit
            try:
                servicetitle = rdfaccthome.replace('http://','').split('/')[0]
            except:
                servicetitle = rdfaccthome

            feed = accounts[rdfaccthome].replace("{foaf:accountName}", rdfacctname)
            if not config.has_section(feed):
                config.add_section(feed)
                config.set(feed, 'name', "%s (%s)" % (title, servicetitle))

    return

if __name__ == "__main__":
    import sys, urllib
    config = ConfigParser()

    for uri in sys.argv[1:]:
        config.add_section(uri)
        foaf2config(urllib.urlopen(uri), config)

    config.write(sys.stdout)
