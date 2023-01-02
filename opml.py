#!/usr/bin/env python3

# This script does not require third-patry packages

import argparse
import sys
import urllib.request
from xml.sax.saxutils import quoteattr
from pathlib import Path
from io import StringIO


def check(rssurl):
    req = urllib.request.Request(rssurl)
    req.add_header("User-Agent", "RSS OPML Generator")
    urllib.request.urlopen(req).read().decode("utf-8")


def main(args):
    # 0. Open output file
    # We should open the output file in binary mode to prevent Windows converting LF to CRLF
    with open(args.output, "wb") as output:
        # Mimic the print function to binary file
        def oprint(*args, **kwargs):
            # Output to a string first
            s = StringIO()
            print(*args, **kwargs, file=s)
            # Then get it to the actual binary file
            s = s.getvalue().encode("utf-8")
            output.write(s)

        contents = []
        # 1. Parse README.md and get the list of links
        with open("./README.md", encoding="utf-8") as f:
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
        oprint("<opml version='2.0'>")
        oprint("<head>")
        oprint("<title>USTCLUG Blogs</title>")
        oprint("</head>")
        oprint("<body>")

        for name, url, rssurl in contents:
            skip = False
            if args.ignore_unavailable_rss:
                try:
                    check(rssurl)
                except:
                    oprint(
                        "<!-- {}: {} is not available, http site = {} -->".format(
                            name, rssurl, url
                        )
                    )
                    oprint(
                        "name: {}, url: {}, rssurl: {} not available".format(
                            name, url, rssurl
                        ),
                        file=sys.stderr,
                    )
                    skip = True
            if not skip:
                if args.thunderbird:
                    oprint("<outline title={}>".format(name))
                oprint(
                    "<outline type='rss' text={} xmlUrl={} htmlUrl={}/>".format(
                        name, quoteattr(rssurl), quoteattr(url)
                    )
                )
                if args.thunderbird:
                    oprint("</outline>")

        oprint("</body>")
        oprint("</opml>")


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
    # UTF-8 support of Windows Console is completely a mess
    # And some apps like Thunderbird requires a UTF-8 opml file
    # So I have to do output within the script instead of using shell redirection
    # See https://github.com/ustclug/blogs/issues/5 for more detailss
    parser.add_argument(
        "--output", type=Path, help="Output opml file path", default="ustclug.opml"
    )
    args = parser.parse_args()
    main(args)
