import re
import logging
from bs4 import BeautifulSoup

from mkdocs_panzoom_plugin import panzoom_box
from mkdocs_panzoom_plugin.panzoom_box import *

#from mkdocs_panzoom_plugin.panzoom_box import PanZoomBox

class HTMLPage:
    def __init__(self, content:str, config, page):
        self.soup = BeautifulSoup(content,"html.parser")
        self.config = config
        self.page = page
        self.containers = self._find_elements()


    def __str__(self):
        return str(self.soup)


    def add_panzoom(self):
        for element in self.containers:
            panzoom_box = create_panzoom_box(self.soup,self.config)
            #panzoom_container = self.soup.new_tag("div",**{"class": "panzoom-container"})
            test = element.wrap(panzoom_box)

            panzoom_box.append(create_info_box(self.soup,self.config))

            #test.wrap(panzoom_container)
        #print(self.soup.prettify())

        # Include the css and js in the file
        self.soup.head.append(create_css_link(self.soup,self.page))
        self.soup.body.append(create_js_script(self.soup,self.page))
        self.soup.body.append(create_js_script_plugin(self.soup,self.page))

    def _find_elements(self):
        output = []

        if self.config.get("images",False):

            output += self.soup.findAll("img")

        if self.config.get("mermaid",False):
            output += self.soup.findAll(class_="mermaid")
        return output
