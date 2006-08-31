import planet
import os
import sys

def run(template_file, doc, mode='template'):
    """ select a template module based on file extension and execute it """
    log = planet.getLogger(planet.config.log_level())

    if mode == 'template':
        dirs = planet.config.template_directories()
    else:
        dirs = planet.config.filter_directories()
 
    # see if the template can be located
    for template_dir in dirs:
        template_resolved = os.path.join(template_dir, template_file)
        if os.path.exists(template_resolved): break
    else:
        return log.error("Unable to locate %s %s", mode, template_file)

    # Add shell directory to the path, if not already there
    shellpath = os.path.join(sys.path[0],'planet','shell')
    if shellpath not in sys.path:
        sys.path.append(shellpath)

    # Try loading module for processing this template, based on the extension
    base,ext = os.path.splitext(os.path.basename(template_resolved))
    module_name = ext[1:]
    try:
        module = __import__(module_name)
    except Exception, inst:
        print module_name
        return log.error("Skipping %s '%s' after failing to load '%s': %s", 
            mode, template_resolved, module_name, inst)

    # Execute the shell module
    if mode == 'filter':
        log.debug("Processing filer %s using %s", template_resolved,
            module_name)
        return module.run(template_resolved, doc, None)
    else:
        log.info("Processing template %s using %s", template_resolved,
            module_name)
        output_dir = planet.config.output_dir()
        output_file = os.path.join(output_dir, base)
        module.run(template_resolved, doc, output_file)
