# coding=utf-8
import os
import urlparse

import pubsubhubbub_publish

import planet


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
            pubsubhubbub_publish.publish(hub, feeds)
            for feed in feeds:
                log.info("Published %s to %s\n" % (feed, hub))
        except pubsubhubbub_publish.PublishError as e:
            log.error("PubSubHubbub publishing error: %s\n" % e)
