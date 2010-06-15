import os, sys
import urlparse
import pubsubhubbub_publisher as PuSH

def publish(config):
    hub = config.pubsubhubbub_hub()
    link = config.link()
    if hub and link:
        for root, dirs, files in os.walk(config.output_dir()):
            xmlfiles = [urlparse.urljoin(link, f) for f in files if f in ['atom.xml', 'rss10.xml', 'rss20.xml']]
            try:
                PuSH.publish(hub, xmlfiles)
            except PuSH.PublishError, e:
                sys.stderr.write("PubSubHubbub publishing error: %s\n" % e)
            break
