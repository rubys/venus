import planet
import os

def run(template_file, doc):
    """ select a template module based on file extension and execute it """
    log = planet.getLogger(planet.config.log_level())

    for template_dir in planet.config.template_directories():
        template_resolved = os.path.join(template_dir, template_file)
        if os.path.exists(template_resolved): break
    else:
        return log.error("Unable to locate template %s", template_file)

    base,ext = os.path.splitext(os.path.basename(template_resolved))
    try:
        module = __import__('planet/shell/' + ext[1:])
    except:
        return log.error("Skipping template %s", template_resolved)

    log.info("Processing template %s", template_resolved)
    output_dir = planet.config.output_dir()
    output_file = os.path.join(output_dir, base)
    module.run(template_resolved, doc, output_file)
