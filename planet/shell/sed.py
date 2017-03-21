# coding=utf-8
from subprocess import PIPE, Popen

import planet


def run(script, doc, output_file=None, options=None):
    """ process an Python script """

    if options is None:
        options = {}

    if output_file:
        out = open(output_file, 'w')
    else:
        out = PIPE

    proc = Popen(['sed', '-f', script],
                 stdin=PIPE, stdout=out, stderr=PIPE)

    stdout, stderr = proc.communicate(doc)
    if stderr:
        planet.logger.error(stderr)

    return stdout
