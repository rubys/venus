from ConfigParser import ConfigParser

inheritable_options = [ 'online_accounts' ]

def load_accounts(config, section):
    accounts = {}
    if(config.has_option(section, 'online_accounts')):
        values = config.get(section, 'online_accounts')
        for account_map in values.split('\n'):
            try:
                homepage, map = account_map.split('|')
                accounts[homepage] = map
            except:
                pass

    return accounts

def load_model(rdf, base_uri):

    if hasattr(rdf, 'find_statements'):
        return rdf

    if hasattr(rdf, 'read'):
        rdf = rdf.read()

    def handler(code, level, facility, message, line, column, byte, file, uri):
        pass

    from RDF import Model, Parser

    model = Model()

    Parser().parse_string_into_model(model,rdf,base_uri,handler)

    return model

# input = foaf, output = ConfigParser
def foaf2config(rdf, config, subject=None, section=None):

    if not config or not config.sections():
        return

    # there should be only be 1 section
    if not section: section = config.sections().pop()

    try:
        from RDF import Model, NS, Parser, Statement
    except:
        return

    # account mappings, none by default
    # form: accounts = {url to service homepage (as found in FOAF)}|{URI template}\n*
    # example: http://del.icio.us/|http://del.icio.us/rss/{foaf:accountName}
    accounts = load_accounts(config, section)

    depth = 0

    if(config.has_option(section, 'depth')):
        depth = config.getint(section, 'depth')

    model = load_model(rdf, section)

    dc   = NS('http://purl.org/dc/elements/1.1/')
    foaf = NS('http://xmlns.com/foaf/0.1/')
    rdfs = NS('http://www.w3.org/2000/01/rdf-schema#')
    rdf = NS('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
    rss = NS('http://purl.org/rss/1.0/')

    for statement in model.find_statements(Statement(subject,foaf.weblog,None)):

        # feed owner
        person = statement.subject

        # title is required (at the moment)
        title = model.get_target(person,foaf.name)
        if not title: title = model.get_target(statement.object,dc.title)
        if not title: 
            continue

        # blog is optional
        feed = model.get_target(statement.object,rdfs.seeAlso)
        if feed and rss.channel == model.get_target(feed, rdf.type):
            feed = str(feed.uri)
            if not config.has_section(feed):
                config.add_section(feed)
                config.set(feed, 'name', str(title))

        # now look for OnlineAccounts for the same person
        if accounts.keys():
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

        if depth > 0:

            # now the fun part, let's go after more friends
            for statement in model.find_statements(Statement(person,foaf.knows,None)):
                friend = statement.object

                # let's be safe
                if friend.is_literal(): continue
                
                seeAlso = model.get_target(friend,rdfs.seeAlso)

                # nothing to see
                if not seeAlso or not seeAlso.is_resource(): continue

                seeAlso = str(seeAlso.uri)

                if not config.has_section(seeAlso):
                    config.add_section(seeAlso)
                    copy_options(config, section, seeAlso, 
                            { 'content_type' : 'foaf', 
                              'depth' : str(depth - 1) })
                try:
                    from planet.config import downloadReadingList
                    downloadReadingList(seeAlso, config,
                        lambda data, subconfig : friend2config(model, friend, seeAlso, subconfig, data), 
                        False)
                except:
                    pass

    return

def copy_options(config, parent_section, child_section, overrides = {}):
    global inheritable_options
    for option in [x for x in config.options(parent_section) if x in inheritable_options]:
        if not overrides.has_key(option):
            config.set(child_section, option, config.get(parent_section, option))

    for option, value in overrides.items():
        config.set(child_section, option, value)


def friend2config(friend_model, friend, seeAlso, subconfig, data):

    try:
        from RDF import Model, NS, Parser, Statement
    except:
        return

    dc   = NS('http://purl.org/dc/elements/1.1/')
    foaf = NS('http://xmlns.com/foaf/0.1/')
    rdf = NS('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
    rdfs = NS('http://www.w3.org/2000/01/rdf-schema#')

    # FOAF InverseFunctionalProperties
    ifps = [foaf.mbox, foaf.mbox_sha1sum, foaf.jabberID, foaf.aimChatID, 
        foaf.icqChatID, foaf.yahooChatID, foaf.msnChatID, foaf.homepage, foaf.weblog]

    model = load_model(data, seeAlso)

    for statement in model.find_statements(Statement(None,rdf.type,foaf.Person)):

        samefriend = statement.subject
        
        # maybe they have the same uri
        if friend.is_resource() and samefriend.is_resource() and friend == samefriend:
            foaf2config(model, subconfig, samefriend)
            return

        for ifp in ifps:
            object = model.get_target(samefriend,ifp)
            if object and object == friend_model.get_target(friend, ifp):
                foaf2config(model, subconfig, samefriend)
                return

if __name__ == "__main__":
    import sys, urllib
    config = ConfigParser()

    for uri in sys.argv[1:]:
        config.add_section(uri)
        foaf2config(urllib.urlopen(uri), config, section=uri)
        config.remove_section(uri)

    config.write(sys.stdout)
