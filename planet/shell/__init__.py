import planet
import os
import sys

logged_modes = []

def run(template_file, doc, mode='template'):
    """ select a template module based on file extension and execute it """
    log = planet.logger

    if mode == 'template':
        dirs = planet.config.template_directories()
    else:
        dirs = planet.config.filter_directories()
 
    # parse out "extra" options
    if template_file.find('?') < 0:
        extra_options = {}
    else:
        import cgi
        template_file, extra_options = template_file.split('?',1)
        extra_options = dict(cgi.parse_qsl(extra_options))

    # see if the template can be located
    for template_dir in dirs:
        template_resolved = os.path.join(template_dir, template_file)
        if os.path.exists(template_resolved): break
    else:
        log.error("Unable to locate %s %s", mode, template_file)
        if not mode in logged_modes:
            log.info("%s search path:", mode)
            for template_dir in dirs:
                log.info("    %s", os.path.realpath(template_dir))
            logged_modes.append(mode)
        return
    template_resolved = os.path.abspath(template_resolved)

    # Add shell directory to the path, if not already there
    shellpath = os.path.join(sys.path[0],'planet','shell')
    if shellpath not in sys.path:
        sys.path.append(shellpath)

    # Try loading module for processing this template, based on the extension
    base,ext = os.path.splitext(os.path.basename(template_resolved))
    module_name = ext[1:]
    try:
        try:
            module = __import__("_" + module_name)
        except:
            module = __import__(module_name)
    except Exception, inst:
        return log.error("Skipping %s '%s' after failing to load '%s': %s", 
            mode, template_resolved, module_name, inst)

    # Execute the shell module
    options = planet.config.template_options(template_file)
    if module_name == 'plugin': options['__file__'] = template_file
    options.update(extra_options)
    log.debug("Processing %s %s using %s", mode,
        os.path.realpath(template_resolved), module_name)
    if mode == 'filter':
        return module.run(template_resolved, doc, None, options)
    else:
        output_dir = planet.config.output_dir()
        output_file = os.path.join(output_dir, base)
        module.run(template_resolved, doc, output_file, options)
        return output_file
