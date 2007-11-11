"""
Planet Configuration

This module encapsulates all planet configuration.  This is not a generic
configuration parser, it knows everything about configuring a planet - from
the structure of the ini file, to knowledge of data types, even down to
what are the defaults.

Usage:
  import config
  config.load('config.ini')

  # administrative / structural information
  print config.template_files()
  print config.subscriptions()

  # planet wide configuration
  print config.name()
  print config.link()

  # per template configuration
  print config.days_per_page('atom.xml.tmpl')
  print config.encoding('index.html.tmpl')

Todo:
  * error handling (example: no planet section)
"""

import os, sys, re, urllib
from ConfigParser import ConfigParser
from urlparse import urljoin

parser = ConfigParser()

planet_predefined_options = ['filters']

def __init__():
    """define the struture of an ini file"""
    import config

    # get an option from a section
    def get(section, option, default):
        if section and parser.has_option(section, option):
            return parser.get(section, option)
        elif parser.has_option('Planet', option):
            if option == 'log_format':
                return parser.get('Planet', option, raw=True)
            return parser.get('Planet', option)
        else:
            return default

    # expand %(var) in lists
    def expand(list):
        output = []
        wild = re.compile('^(.*)#{(\w+)}(.*)$')
        for file in list.split():
            match = wild.match(file)
            if match:
                pre,var,post = match.groups()
                for sub in subscriptions():
                    value = feed_options(sub).get(var,None)
                    if value:
                        output.append(pre+value+post)
            else:
                output.append(file)
        return output

    # define a string planet-level variable
    def define_planet(name, default):
        setattr(config, name, lambda default=default: get(None,name,default))
        planet_predefined_options.append(name)

    # define a list planet-level variable
    def define_planet_int(name, default=0):
        setattr(config, name, lambda : int(get(None,name,default)))
        planet_predefined_options.append(name)

    # define a list planet-level variable
    def define_planet_list(name, default=''):
        setattr(config, name, lambda : expand(get(None,name,default)))
        planet_predefined_options.append(name)

    # define a string template-level variable
    def define_tmpl(name, default):
        setattr(config, name, lambda section, default=default:
            get(section,name,default))

    # define an int template-level variable
    def define_tmpl_int(name, default):
        setattr(config, name, lambda section, default=default:
            int(get(section,name,default)))

    # planet wide options
    define_planet('name', "Unconfigured Planet")
    define_planet('link', '')
    define_planet('cache_directory', "cache")
    define_planet('log_level', "WARNING")
    define_planet('log_format', "%(levelname)s:%(name)s:%(message)s")
    define_planet('date_format', "%B %d, %Y %I:%M %p")
    define_planet('new_date_format', "%B %d, %Y")
    define_planet('generator', 'Venus')
    define_planet('generator_uri', 'http://intertwingly.net/code/venus/')
    define_planet('owner_name', 'Anonymous Coward')
    define_planet('owner_email', '')
    define_planet('output_theme', '')
    define_planet('output_dir', 'output')
    define_planet('spider_threads', 0) 

    define_planet_int('new_feed_items', 0) 
    define_planet_int('feed_timeout', 20)
    define_planet_int('cache_keep_entries', 10)

    define_planet_list('template_files')
    define_planet_list('bill_of_materials')
    define_planet_list('template_directories', '.')
    define_planet_list('filter_directories')

    # template options
    define_tmpl_int('days_per_page', 0)
    define_tmpl_int('items_per_page', 60)
    define_tmpl_int('activity_threshold', 0)
    define_tmpl('encoding', 'utf-8')
    define_tmpl('content_type', 'utf-8')
    define_tmpl('ignore_in_feed', '')
    define_tmpl('name_type', '')
    define_tmpl('title_type', '')
    define_tmpl('summary_type', '')
    define_tmpl('content_type', '')
    define_tmpl('future_dates', 'keep')
    define_tmpl('xml_base', '')
    define_tmpl('filter', None) 
    define_tmpl('exclude', None) 

def load(config_file):
    """ initialize and load a configuration"""
    global parser
    parser = ConfigParser()
    parser.read(config_file)

    import config, planet
    from planet import opml, foaf, csv_config
    log = planet.logger
    if not log:
        log = planet.getLogger(config.log_level(),config.log_format())

    # Theme support
    theme = config.output_theme()
    if theme:
        for path in ("", os.path.join(sys.path[0],'themes')):
            theme_dir = os.path.join(path,theme)
            theme_file = os.path.join(theme_dir,'config.ini')
            if os.path.exists(theme_file):
                # initial search list for theme directories
                dirs = config.template_directories()
                if theme_dir not in dirs:
                    dirs.append(theme_dir)
                if os.path.dirname(config_file) not in dirs:
                    dirs.append(os.path.dirname(config_file))

                # read in the theme
                parser = ConfigParser()
                parser.read(theme_file)
                bom = config.bill_of_materials()

                # complete search list for theme directories
                dirs += [os.path.join(theme_dir,dir) for dir in 
                    config.template_directories() if dir not in dirs]

                # merge configurations, allowing current one to override theme
                template_files = config.template_files()
                parser.set('Planet','template_files','')
                parser.read(config_file)
                for file in config.bill_of_materials():
                    if not file in bom: bom.append(file)
                parser.set('Planet', 'bill_of_materials', ' '.join(bom))
                parser.set('Planet', 'template_directories', ' '.join(dirs))
                parser.set('Planet', 'template_files',
                   ' '.join(template_files + config.template_files()))
                break
        else:
            log.error('Unable to find theme %s', theme)

    # Filter support
    dirs = config.filter_directories()
    filter_dir = os.path.join(sys.path[0],'filters')
    if filter_dir not in dirs and os.path.exists(filter_dir):
        parser.set('Planet', 'filter_directories', ' '.join(dirs+[filter_dir]))

    # Reading list support
    reading_lists = config.reading_lists()
    if reading_lists:
        if not os.path.exists(config.cache_lists_directory()):
            os.makedirs(config.cache_lists_directory())

        def data2config(data, cached_config):
            if content_type(list).find('opml')>=0:
                opml.opml2config(data, cached_config)
            elif content_type(list).find('foaf')>=0:
                foaf.foaf2config(data, cached_config)
            elif content_type(list).find('csv')>=0:
                csv_config.csv2config(data, cached_config)
            elif content_type(list).find('config')>=0:
                cached_config.readfp(data)
            else:
                from planet import shell
                import StringIO
                cached_config.readfp(StringIO.StringIO(shell.run(
                    content_type(list), data.getvalue(), mode="filter")))

            if cached_config.sections() in [[], [list]]: 
                raise Exception

        for list in reading_lists:
            downloadReadingList(list, parser, data2config)

def downloadReadingList(list, orig_config, callback, use_cache=True, re_read=True):
    from planet import logger
    import config
    try:

        import urllib2, StringIO
        from planet.spider import filename

        # list cache file name
        cache_filename = filename(config.cache_lists_directory(), list)

        # retrieve list options (e.g., etag, last-modified) from cache
        options = {}

        # add original options
        for key in orig_config.options(list):
            options[key] = orig_config.get(list, key)
            
        try:
            if use_cache:
                cached_config = ConfigParser()
                cached_config.read(cache_filename)
                for option in cached_config.options(list):
                     options[option] = cached_config.get(list,option)
        except:
            pass

        cached_config = ConfigParser()
        cached_config.add_section(list)
        for key, value in options.items():
            cached_config.set(list, key, value)

        # read list
        curdir=getattr(os.path, 'curdir', '.')
        if sys.platform.find('win') < 0:
            base = urljoin('file:', os.path.abspath(curdir))
        else:
            path = os.path.abspath(os.path.curdir)
            base = urljoin('file:///', path.replace(':','|').replace('\\','/'))

        request = urllib2.Request(urljoin(base + '/', list))
        if options.has_key("etag"):
            request.add_header('If-None-Match', options['etag'])
        if options.has_key("last-modified"):
            request.add_header('If-Modified-Since',
                options['last-modified'])
        response = urllib2.urlopen(request)
        if response.headers.has_key('etag'):
            cached_config.set(list, 'etag', response.headers['etag'])
        if response.headers.has_key('last-modified'):
            cached_config.set(list, 'last-modified',
                response.headers['last-modified'])

        # convert to config.ini
        data = StringIO.StringIO(response.read())

        if callback: callback(data, cached_config)

        # write to cache
        if use_cache:
            cache = open(cache_filename, 'w')
            cached_config.write(cache)
            cache.close()

        # re-parse and proceed
        logger.debug("Using %s readinglist", list) 
        if re_read:
            if use_cache:  
                orig_config.read(cache_filename)
            else:
                cdata = StringIO.StringIO()
                cached_config.write(cdata)
                cdata.seek(0)
                orig_config.readfp(cdata)
    except:
        try:
            if re_read:
                if use_cache:  
                    if not orig_config.read(cache_filename): raise Exception()
                else:
                    cdata = StringIO.StringIO()
                    cached_config.write(cdata)
                    cdata.seek(0)
                    orig_config.readfp(cdata)
                logger.info("Using cached %s readinglist", list)
        except:
            logger.exception("Unable to read %s readinglist", list)

def http_cache_directory():
    if parser.has_option('Planet', 'http_cache_directory'):
        os.path.join(cache_directory(), 
            parser.get('Planet', 'http_cache_directory'))
    else:
        return os.path.join(cache_directory(), "cache")

def cache_sources_directory():
    if parser.has_option('Planet', 'cache_sources_directory'):
        return os.path.join(cache_directory(),
            parser.get('Planet', 'cache_sources_directory'))
    else:
        return os.path.join(cache_directory(), 'sources')

def cache_lists_directory():
    if parser.has_option('Planet', 'cache_lists_directory'):
        parser.get('Planet', 'cache_lists_directory')
    else:
        return os.path.join(cache_directory(), 'lists')

def feed():
    if parser.has_option('Planet', 'feed'):
        return parser.get('Planet', 'feed')
    elif link():
        for template_file in template_files():
            name = os.path.splitext(os.path.basename(template_file))[0]
            if name.find('atom')>=0 or name.find('rss')>=0:
                return urljoin(link(), name)

def feedtype():
    if parser.has_option('Planet', 'feedtype'):
        parser.get('Planet', 'feedtype')
    elif feed() and feed().find('atom')>=0:
        return 'atom'
    elif feed() and feed().find('rss')>=0:
        return 'rss'

def subscriptions():
    """ list the feed subscriptions """
    return __builtins__['filter'](lambda feed: feed!='Planet' and 
        feed not in template_files()+filters()+reading_lists(),
        parser.sections())

def reading_lists():
    """ list of lists of feed subscriptions """
    result = []
    for section in parser.sections():
        if parser.has_option(section, 'content_type'):
            type = parser.get(section, 'content_type')
            if type.find('opml')>=0 or type.find('foaf')>=0 or \
               type.find('csv')>=0 or type.find('config')>=0 or \
               type.find('.')>=0:
                result.append(section)
    return result

def filters(section=None):
    filters = []
    if parser.has_option('Planet', 'filters'):
        filters += parser.get('Planet', 'filters').split()
    if filter(section):
        filters.append('regexp_sifter.py?require=' +
            urllib.quote(filter(section)))
    if exclude(section):
        filters.append('regexp_sifter.py?exclude=' +
            urllib.quote(exclude(section)))
    for section in section and [section] or template_files():
        if parser.has_option(section, 'filters'):
            filters += parser.get(section, 'filters').split()
    return filters

def planet_options():
    """ dictionary of planet wide options"""
    return dict(map(lambda opt: (opt,
        parser.get('Planet', opt, raw=(opt=="log_format"))),
        parser.options('Planet')))

def feed_options(section):
    """ dictionary of feed specific options"""
    import config
    options = dict([(key,value) for key,value in planet_options().items()
        if key not in planet_predefined_options])
    if parser.has_section(section):
        options.update(dict(map(lambda opt: (opt, parser.get(section,opt)),
            parser.options(section))))
    return options

def template_options(section):
    """ dictionary of template specific options"""
    return feed_options(section)

def filter_options(section):
    """ dictionary of filter specific options"""
    return feed_options(section)

def write(file=sys.stdout):
    """ write out an updated template """
    print parser.write(file)
