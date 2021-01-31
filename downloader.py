#!/usr/bin/env python3

from sec_edgar_downloader import Downloader
import os, re, shutil

def find_filename(path, date, form):
    ret = os.path.join(path, "%s_%s.html" % (form, date))
    if not os.path.isfile(ret):
        return ret

    for i in range(10):
        ret = os.path.join(path, os.path.join(path, "%s_%d.html" % (form, date, i)))
        if not os.path.isfile(ret):
            return ret

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
        os.rename(htmlFname, find_filename(path, date, form))
        shutil.rmtree(os.path.join(path, filingDir))


def main(path, tickers):
    # do_download(path, tickers, "10-K")
    # do_download(path, tickers, "10-Q")
    # do_download(path, tickers, "20-F")
    do_download(path, tickers, "8-K")
    # do_download(path, tickers, "6-K")

if __name__ == '__main__':
    import sys
    path = sys.argv[1]
    tickers = sys.argv[2]
    main(path, tickers)