import os, sys
import urlparse
import planet
import pubsubhubbub_publisher as PuSH

def publish(config):
    log = planet.logger
    hub = config.pubsubhubbub_hub()
    link = config.link()

    # identify feeds
    feeds = []
    if hub and link:
        for root, dirs, files in os.walk(config.output_dir()):
            for file in files:
                 if file in config.pubsubhubbub_feeds():
                     feeds.append(urlparse.urljoin(link, file))

    # publish feeds
    if feeds:
        try:
            PuSH.publish(hub, feeds)
            for feed in feeds:
                log.info("Published %s to %s\n" % (feed, hub))
        except PuSH.PublishError, e:
            log.error("PubSubHubbub publishing error: %s\n" % e)
