# coding=utf-8
from subprocess import PIPE, Popen


def run(script, doc, output_file=None, options={}):
    """ process an Python script """

    if output_file:
        out = open(output_file, 'w')
    else:
        out = PIPE

    proc = Popen(['sed', '-f', script],
                 stdin=PIPE, stdout=out, stderr=PIPE)

    stdout, stderr = proc.communicate(doc)
    if stderr:
        import planet
        planet.logger.error(stderr)

    return stdout
