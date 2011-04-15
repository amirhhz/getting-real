#!/usr/bin/env python

from BeautifulSoup import BeautifulSoup
from urllib2 import urlopen
import re
import json
from collections import defaultdict
import logging
from logging import DEBUG, INFO

logging.basicConfig(level=DEBUG)

class BookScraper(object):
  def __init__(self, base_url, toc_page=u""):
    self.base_url = base_url
    toc_page = self.get_page_soup(toc_page).find("div", id="Container")
    self.toc = toc_page

  def parse_toc(self):
    book = {}
    chapters = self.toc.findAll("h2")
    for ch in chapters:
      chap_no = ch.a["name"][2:4]
      book[chap_no] = {
          "chapter_title": ch.contents[1].strip(),
          "sections": []
          }
      # Find links to sections of the each chapter
      sections = ch.findNextSibling("ul").findAll(
          "a", href=re.compile("^ch"))

      for sec in sections:
        sec_content = self.get_page_soup(
            sec["href"]).find("div", "content")
        book[chap_no]["sections"].append({
            "href": sec["href"],
            "section_title": sec_content.h1.contents[0],
            "content": str(sec_content)
          })

      self.book = book

  def save_json(self, filename):
    with open(filename, "w") as fn:
      json.dump(self.book, fn, indent=2)

  def get_page_soup(self, page_path):
    return BeautifulSoup(urlopen(
      self.base_url + page_path).read())

  def export_html(self):
    template="""
<html>
<head>
  <title>{ch_no} {chapter} - {section}</title>
</head>
<body>
  {content}
</body>
</html>
"""
    for chapter, ch_cont in self.book.iteritems():
      ch_no = str(chapter).rjust(2, "0")
      for sec in ch_cont["sections"]:
        filename = sec["href"].replace("php", "html")
        with open(filename, "w") as fn:
          to_write = template.format(
              ch_no=ch_no,
              chapter=ch_cont["chapter_title"],
              section=sec["section_title"],
              content=sec["content"])
          fn.write(to_write)
        logging.info("wrote a section!")
      logging.info("wrote a chapter!")

    # Make the index files
    bad_links = self.toc.findAll("a",href=re.compile("^ch"))
    for each in bad_links:
      each["href"] = each["href"].replace("php", "html")
    filename = "index.html"
    with open(filename, "w") as fn:
      to_write = template.format(
          ch_no=None,
          chapter="Getting Real",
          section="Table of Contents",
          content=str(self.toc))
      fn.write(to_write)
    logging.info("wrote index!")


if __name__ == "__main__":
  import sys

  bs = BookScraper("http://gettingreal.37signals.com/", "toc.php")
  if len(sys.argv) > 1 and sys.argv[1] == "export":
    bs.parse_toc()
    bs.export_html()


