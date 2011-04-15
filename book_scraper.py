#!/usr/bin/env python

from BeautifulSoup import BeautifulSoup
from urllib2 import urlopen
import re
from collections import defaultdict
import logging
from logging import DEBUG, INFO

logging.basicConfig(level=DEBUG)

class BookScraper(object):
  def __init__(self, base_url, toc_page=u""):
    self.base_url = base_url
    toc_page = self.get_page_soup(toc_page).find("div", id="Container")
    self.toc_page = toc_page

  def parse_toc(self):
    links = self.toc_page.findAll("a", href=re.compile("^ch"))
    self.links = []
    for i in links:
      content = self.get_page_soup(i["href"]).find("div", "content")
      self.links.append({"href": i["href"], "content": content})
    return self.links

  def get_page_soup(self, page_path):
    return BeautifulSoup(urlopen(
      self.base_url + page_path).read())


