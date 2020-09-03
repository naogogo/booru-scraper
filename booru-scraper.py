#!/usr/bin/env python3

import argparse
import datetime
import hashlib
import logging
import os
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree

DEFAULT_BOORU = "http://localhost"
DEFAULT_LIMIT = 100
DEFAULT_PAGE = 1
DEFAULT_USERAGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0"

class BooruPost(object):

        REQUIRED_ATTRIBUTES = [
                "created_at",
                "file_url",
                "id",
        ]

        def __init__(self, post):
                self.logger = logging.getLogger(self.__class__.__name__)

                self.post = post
                for attribute in self.REQUIRED_ATTRIBUTES:
                        setattr(self, attribute, self.post.attrib[attribute])
                self.filename = os.path.basename(self.file_url)

        def checksum(self):
                return os.path.splitext(self.filename)[0]

        def headers(self):
                url = urllib.parse.urlparse(self.file_url)
                booru = "{url.scheme}://{url.netloc}".format(url=url)
                return {
                        "User-Agent": DEFAULT_USERAGENT,
                        "Referer": "{0}/post/show/{1}".format(booru, self.id),
                }

        def mtime(self):
                timeformat = "%a %b %d %H:%M:%S %z %Y"
                timestamp = datetime.datetime.strptime(self.created_at, timeformat)
                mtime = time.mktime(timestamp.timetuple())
                return (mtime, mtime)

        def fetch(self, directory):
                filepath = "{0}/{1}".format(directory, self.filename)

                if not os.path.isdir(directory):
                        os.mkdir(directory)

                if os.path.isfile(filepath):
                        with open(filepath, "rb") as f:
                                checksum = hashlib.md5(f.read()).hexdigest()

                        if not checksum == self.checksum():
                                self.logger.warn("Checksum mismatch: expected %s, got %s", self.checksum(), checksum)
                                os.unlink(filepath)

                if not os.path.isfile(filepath):
                        request = urllib.request.Request(self.file_url, headers=self.headers())

                        with urllib.request.urlopen(request) as r, open(filepath, "wb") as f:
                                f.write(r.read())

                        os.utime(filepath, self.mtime())

                        self.logger.info("Successfully fetched %s", self.filename)
                else:
                        self.logger.info("%s exists and matches checksum", self.filename)

class BooruList(object):

        def __init__(self, booru, limit, page, tags):
                self.logger = logging.getLogger(self.__class__.__name__)

                self.booru = booru
                self.limit = limit
                self.page = page
                self.tags = tags

        def headers(self):
                return {
                        "User-Agent": DEFAULT_USERAGENT,
                }

        def fetch(self):
                url = "{0}/post/index.xml?limit={1}&page={2}&tags={3}".format(
                        self.booru, self.limit, self.page, "+".join(self.tags)
                )

                request = urllib.request.Request(url, headers=self.headers())
                response = urllib.request.urlopen(request).read().decode("utf8")

                self.posts = response

        @property
        def posts(self):
                return self._posts

        @posts.setter
        def posts(self, xmlstring):
                self._posts = xml.etree.ElementTree.fromstring(xmlstring)

if __name__ == "__main__":

        logging.basicConfig(level=logging.INFO)

        parser = argparse.ArgumentParser(description="Scrapes a booru for posts")
        parser.add_argument("--booru", type=str,
                help="URL of the booru to use (default: {0})".format(DEFAULT_BOORU), default=DEFAULT_BOORU)
        parser.add_argument("--limit", type=int,
                help="Number of posts to get from the page (default: {0})".format(DEFAULT_LIMIT), default=DEFAULT_LIMIT)
        parser.add_argument("--page", type=int,
                help="Page number to start the search from (default: {0})".format(DEFAULT_PAGE), default=DEFAULT_PAGE)
        parser.add_argument("directory", metavar="DIRECTORY", type=str,
                help="Where to fetch the posts to")
        parser.add_argument("tags", metavar="TAG", type=str, nargs="*",
                help="Any number of tags to search, searches across all tags if none specified")
        args = parser.parse_args()

        joinedtags = "+".join(args.tags)

        boorulist = BooruList(args.booru, args.limit, args.page, args.tags)
        boorulist.fetch()
        for post in boorulist.posts:
                boorupost = BooruPost(post)
                boorupost.fetch("{0}/{1}".format(args.directory, joinedtags))
