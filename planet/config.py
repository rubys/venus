"""
Planet Configuration

This module encapsulates all planet configuration.  This is not a generic
configuration parser, it knows everything about configuring a planet - from
the structure of the ini file, to knowledge of data types, even down to
what are the defaults.

Usage:
  from planet import config
  config.load('config.ini')

  # administrative / structural information
  print config.templates()
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

import sys
from ConfigParser import ConfigParser

parser = ConfigParser()

planet_predefined_options = []

def __init__():
    """define the struture of an ini file"""
    from planet import config

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

    # template options
    define_tmpl_int('days_per_page', 0)
    define_tmpl_int('items_per_page', 60)
    define_tmpl('encoding', 'utf-8')

    # prevent re-initialization
    setattr(config, '__init__', lambda: None)

def load(file):
    """ initialize and load a configuration"""
    __init__()
    global parser
    parser = ConfigParser()
    parser.read(file)

def template_files():
    """ list the templates defined """
    return parser.get('Planet','template_files').split(' ')

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
    from planet import config
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
