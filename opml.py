#!/usr/bin/env python3

# This script does not require third-patry packages

import argparse
import sys
import urllib.request
from xml.sax.saxutils import quoteattr


def check(rssurl):
    req = urllib.request.Request(rssurl)
    req.add_header("User-Agent", "RSS OPML Generator")
    urllib.request.urlopen(req).read().decode("utf-8")


def main(args):
    contents = []
    # 1. Parse README.md and get the list of links
    with open("./README.md") as f:
        for line in f:
            if line.startswith("|"):
                try:
                    name, url, rssurl = line.split("|")[1:4]
                    name = name.strip()
                    url = url.strip()
                    rssurl = rssurl.strip()
                    # is rssurl valid?
                    if not rssurl.lower().startswith("http"):
                        continue
                    name = quoteattr(name)
                    contents.append((name, url, rssurl))
                except ValueError:
                    pass
    # 2. Generate OPML
    print("<opml version='2.0'>")
    print("<head>")
    print("<title>USTCLUG Blogs</title>")
    print("</head>")
    print("<body>")

    for name, url, rssurl in contents:
        skip = False
        if args.ignore_unavailable_rss:
            try:
                check(rssurl)
            except:
                print("<!-- {}: {} is not available, http site = {} -->".format(name, rssurl, url))
                print("name: {}, url: {}, rssurl: {} not available".format(name, url, rssurl), file=sys.stderr)
                skip = True
        if not skip:
            if args.thunderbird:
                print("<outline title={}>".format(name))
            print(
                "<outline type='rss' text={} xmlUrl={} htmlUrl={}/>".format(
                    name, quoteattr(rssurl), quoteattr(url)
                )
            )
            if args.thunderbird:
                print("</outline>")

    print("</body>")
    print("</opml>")


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Blogs OPML Generator")
    parser.add_argument(
        "--ignore-unavailable-rss",
        action="store_true",
        help="Ignore unavailable RSS feeds",
    )
    parser.add_argument(
        "--thunderbird",
        action="store_true",
        help="Generate Thunderbird-compatible OPML",
    )
    args = parser.parse_args()
    main(args)
