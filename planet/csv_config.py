# coding=utf-8
import csv
import sys
import urllib
from ConfigParser import ConfigParser


# input = csv, output = ConfigParser
def csv2config(input_, config=None):
    if not hasattr(input_, 'read'):
        input_ = csv.StringIO(input_)

    if config is None:
        config = ConfigParser()

    reader = csv.DictReader(input_)
    for row in reader:
        section = row[reader.fieldnames[0]]
        if not config.has_section(section):
            config.add_section(section)
        for name, value in row.items():
            if value and name != reader.fieldnames[0]:
                config.set(section, name, value)

    return config


if __name__ == "__main__":
    # small main program which converts CSV into config.ini format
    config = ConfigParser()
    for addr in sys.argv[1:]:
        csv2config(urllib.urlopen(addr), config)
    config.write(sys.stdout)
