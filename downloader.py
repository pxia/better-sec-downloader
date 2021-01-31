#!/usr/bin/env python3

from bs4 import BeautifulSoup
from sec_edgar_downloader import Downloader
import os, re, shutil

BASE_HTML = """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>title</title>
  </head>
  <body>
  </body>
</html>
"""


def find_filename(path, ticker, form, date):
    form = form.replace("-", "")
    ret = os.path.join(path, "%s_%s_%s.html" % (ticker, form, date))
    if not os.path.isfile(ret):
        return ret

    for i in range(10):
        ret = os.path.join(
            path, os.path.join(path, "%s_%s_%s_%d.html" % (ticker, form, date, i))
        )
        if not os.path.isfile(ret):
            return ret


def url_rewrite(fromfname, tofname):
    with open(fromfname, "r") as f:
        source = BeautifulSoup(f, features="lxml")
        dest = BeautifulSoup(BASE_HTML, features="lxml")
        dest.head.title.string.replace_with(tofname)
        links = source.findAll("a")
        for link in links:
            try:
                link["href"] = "#" + link["href"].split("#", 1)[1]
            except:
                pass
        dest.body.replace_with(source.findAll("body")[0])
        with open(tofname, "w") as f:
            f.write(str(dest))


def do_download(path, ticker, form):
    dl = Downloader(path)
    dl.get(form, ticker, after="2015-01-01")
    path = os.path.join(path, "sec-edgar-filings", ticker, form)

    if not os.path.isdir(path):
        return

    pattern = re.compile("([0-9]+)")
    for filingDir in os.listdir(path):
        fullSubmissionFname = os.path.join(path, filingDir, "full-submission.txt")
        htmlFname = os.path.join(path, filingDir, "filing-details.html")
        if not os.path.isfile(fullSubmissionFname):
            print("skipping ", fullSubmissionFname)
            continue
        found = False
        with open(fullSubmissionFname) as f:
            for line in f:
                if line.startswith("FILED AS OF DATE"):
                    date = re.search(pattern, line).group(0)
                    found = True
        if not found:
            print("skipping ", filingDir)
            continue
        url_rewrite(htmlFname, find_filename(path, ticker, form, date))
        shutil.rmtree(os.path.join(path, filingDir))


def main(path, tickers):
    for ticker in tickers:
        print("downloading", ticker)
        do_download(path, ticker, "10-K")
        do_download(path, ticker, "10-Q")
        do_download(path, ticker, "20-F")
        do_download(path, ticker, "8-K")
        do_download(path, ticker, "6-K")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("""Usage: %s <dir> ticker [tickers...]""" % (sys.argv[0]))
        exit(1)
    path = sys.argv[1]
    tickers = sys.argv[2:]
    main(path, tickers)
