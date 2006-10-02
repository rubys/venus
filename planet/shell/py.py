from subprocess import Popen, PIPE
import sys 

def run(script, doc, output_file=None, options={}):
    """ process an Python script """

    if output_file:
        out = open(output_file, 'w')
    else:
        out = PIPE

    options = sum([['--'+key, value] for key,value in options.items()], [])

    proc = Popen([sys.executable, script] + options,
        stdin=PIPE, stdout=out, stderr=PIPE)

    stdout, stderr = proc.communicate(doc)
    if stderr:
        import planet
        planet.logger.error(stderr)

    return stdout
