# coding=utf-8
import imp
import os
import sys
from StringIO import StringIO

import planet
import traceback

log = planet.logger


def run(script, doc, output_file=None, options=None):
    """ process an Python script using imp """
    if options is None:
        options = {}

    save_sys = (sys.stdin, sys.stdout, sys.stderr, sys.argv)
    plugin_stdout = StringIO()
    plugin_stderr = StringIO()

    try:
        # redirect stdin
        sys.stdin = StringIO(doc)

        # redirect stdout
        if output_file:
            sys.stdout = open(output_file, 'w')
        else:
            sys.stdout = plugin_stdout

        # redirect stderr
        sys.stderr = plugin_stderr

        # determine __file__ value
        if "__file__" in options.keys():
            plugin_file = options["__file__"]
            del options["__file__"]
        else:
            plugin_file = script

        # set sys.argv
        options = sum([['--' + key, value] for key, value in options.items()], [])
        sys.argv = [plugin_file] + options

        # import script
        handle = open(script, 'r')
        cwd = os.getcwd()
        try:
            try:
                try:
                    description = ('.plugin', 'rb', imp.PY_SOURCE)
                    imp.load_module('__main__', handle, plugin_file, description)
                except SystemExit as e:
                    if e.code:
                        log.error('%s exit rc=%d', (plugin_file, e.code))
            except Exception as e:
                type_, value, tb = sys.exc_info()
                plugin_stderr.write(''.join(
                    traceback.format_exception_only(type_, value) +
                    traceback.format_tb(tb)))
        finally:
            handle.close()
            if cwd != os.getcwd():
                os.chdir(cwd)

    finally:
        # restore system state
        sys.stdin, sys.stdout, sys.stderr, sys.argv = save_sys

    # log anything sent to stderr
    if plugin_stderr.getvalue():
        planet.logger.error(plugin_stderr.getvalue())

    # return stdout
    return plugin_stdout.getvalue()
