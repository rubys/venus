import planet
import os
import sys

def run(template_file, doc):
    """ select a template module based on file extension and execute it """
    log = planet.getLogger(planet.config.log_level())

    # see if the template can be located
    for template_dir in planet.config.template_directories():
        template_resolved = os.path.join(template_dir, template_file)
        if os.path.exists(template_resolved): break
    else:
        return log.error("Unable to locate template %s", template_file)

    # Add shell directory to the path, if not already there
    shellpath = os.path.join(sys.path[0],'planet','shell')
    if shellpath not in sys.path:
        sys.path.append(shellpath)

    # Try loading module for processing this template, based on the extension
    base,ext = os.path.splitext(os.path.basename(template_resolved))
    template_module_name = ext[1:]
    try:
        template_module = __import__(template_module_name)
    except Exception, inst:
        return log.error("Skipping template '%s' after failing to load '%s':" +
            " %s", template_resolved, template_module_name, inst)

    # Execute the shell module
    log.info("Processing template %s using %s", template_resolved,
        template_module_name)
    output_dir = planet.config.output_dir()
    output_file = os.path.join(output_dir, base)
    template_module.run(template_resolved, doc, output_file)
