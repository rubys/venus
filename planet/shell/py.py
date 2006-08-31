from subprocess import Popen, PIPE

def run(script, doc, output_file=None):
    """ process an Python script """

    if output_file:
        out = open(output_file, 'w')
    else:
        out = PIPE

    proc = Popen(['python', script], stdin=PIPE, stdout=out, stderr=PIPE)
    stdout, stderr = proc.communicate(doc)
    if stderr:
        print stderr

    return stdout
