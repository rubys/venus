from subprocess import Popen, PIPE
import os

def run(script, doc, output_file=None, options={}):
    """ process an Python script """

    if output_file:
        out = open(output_file, 'w')
    else:
        out = PIPE

    options = sum([['--'+key, value] for key,value in options.items()], [])

    python = os.environ.get('_', 'python')
    proc = Popen([python, script] + options,
        stdin=PIPE, stdout=out, stderr=PIPE)

    stdout, stderr = proc.communicate(doc)
    if stderr:
        import planet
        planet.logger.error(stderr)

    return stdout
