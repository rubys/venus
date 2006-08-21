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
  print config.feeds()

  # planet wide configuration
  print config.name()
  print config.link()

  # per template configuration
  print config.days_per_page('atom.xml.tmpl')
  print config.encoding('index.html.tmpl')

Todo:
  * error handling (example: no planet section)
"""

import os, sys
from ConfigParser import ConfigParser

parser = ConfigParser()

planet_predefined_options = []

def __init__():
    """define the struture of an ini file"""
    import config

    # underlying implementation
    def get(section, option, default):
        if section and parser.has_option(section, option):
            return parser.get(section, option)
        elif parser.has_option('Planet', option):
            return parser.get('Planet', option)
        else:
            return default

    def define_planet(name, default):
        setattr(config, name, lambda default=default: get(None,name,default))
        planet_predefined_options.append(name)

    def define_planet_list(name):
        setattr(config, name, lambda : get(None,name,'').split())
        planet_predefined_options.append(name)

    def define_tmpl(name, default):
        setattr(config, name, lambda section, default=default:
            get(section,name,default))

    def define_tmpl_int(name, default):
        setattr(config, name, lambda section, default=default:
            int(get(section,name,default)))

    # planet wide options
    define_planet('name', "Unconfigured Planet")
    define_planet('link', "Unconfigured Planet")
    define_planet('cache_directory', "cache")
    define_planet('log_level', "WARNING")
    define_planet('feed_timeout', 20)
    define_planet('date_format', "%B %d, %Y %I:%M %p")
    define_planet('generator', 'Venus')
    define_planet('generator_uri', 'http://intertwingly.net/code/venus/')
    define_planet('owner_name', 'Anonymous Coward')
    define_planet('owner_email', '')
    define_planet('output_theme', '')
    define_planet('output_dir', 'output')

    define_planet_list('template_files')
    define_planet_list('bill_of_materials')
    define_planet_list('template_directories')
    define_planet_list('reading_lists')

    # template options
    define_tmpl_int('days_per_page', 0)
    define_tmpl_int('items_per_page', 60)
    define_tmpl('encoding', 'utf-8')

def load(config_file):
    """ initialize and load a configuration"""
    import config, planet
    log = planet.getLogger(config.log_level())

    global parser
    parser = ConfigParser()
    parser.read(config_file)

    # Theme support
    theme = config.output_theme()
    if theme:
        for path in ("", os.path.join(sys.path[0],'themes')):
            theme_dir = os.path.join(path,theme)
            theme_file = os.path.join(theme_dir,'config.ini')
            if os.path.exists(theme_file):
                # initial search list for theme directories
                dirs = config.template_directories() + [theme_dir]

                # read in the theme
                parser = ConfigParser()
                parser.read(theme_file)

                # complete search list for theme directories
                dirs += [os.path.join(theme_dir,dir) for dir in 
                    config.template_directories()]

                # merge configurations, allowing current one to override theme
                parser.read(config_file)
                parser.set('Planet', 'template_directories', ' '.join(dirs))
                break
        else:
            log.error('Unable to find theme %s', theme)

    # Reading list support
    reading_lists = config.reading_lists()
    if reading_lists:
        if not os.path.exists(config.cache_lists_directory()):
            os.makedirs(config.cache_lists_directory())
        from planet.spider import filename
        for list in reading_lists:
            cache_filename = filename(config.cache_lists_directory(), list)
            try:
                import urllib
                data=urllib.urlopen(list).read()
                cache = open(cache_filename, 'w')
                cache.write(data)
                cache.close()
                log.debug("Using %s readinglist", list) 
            except:
                try:
                    cache = open(cache_filename)
                    data = cache.read()
                    cache.close()
                    log.info("Using cached %s readinglist", list)
                except:
                    log.exception("Unable to read %s readinglist", list)
                    continue
        planet.opml.opml2config(data, parser)
        # planet.foaf.foaf2config(data, list, config)

def cache_sources_directory():
    if parser.has_option('Planet', 'cache_sources_directory'):
        parser.get('Planet', 'cache_sources_directory')
    else:
        return os.path.join(cache_directory(), 'sources')

def cache_lists_directory():
    if parser.has_option('Planet', 'cache_lists_directory'):
        parser.get('Planet', 'cache_lists_directory')
    else:
        return os.path.join(cache_directory(), 'lists')

def feeds():
    """ list the feeds defined """
    return filter(lambda feed: feed!='Planet' and feed not in template_files(),
       parser.sections())

def planet_options():
    """ dictionary of planet wide options"""
    return dict(map(lambda opt: (opt, parser.get('Planet',opt)),
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

def write(file=sys.stdout):
    """ write out an updated template """
    print parser.write(file)
