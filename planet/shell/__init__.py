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
        template_module_name = os.path.join('planet', 'shell', ext[1:])
        template_module = __import__(template_module_name)
    except ImportError, inst:
        return log.error("Skipping template '%s' after failing to load '%s': %s", template_resolved, template_module_name, inst)
    except Exception, inst:
        return log.error("Unknown exception: %s", inst)

    log.info("Processing template %s from %s", template_resolved, template_module_name)
    output_dir = planet.config.output_dir()
    output_file = os.path.join(output_dir, base)
    template_module.run(template_resolved, doc, output_file)
