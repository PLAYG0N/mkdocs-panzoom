import re
import logging
from bs4 import BeautifulSoup

from mkdocs_panzoom_plugin import panzoom_box
from mkdocs_panzoom_plugin.panzoom_box import *

#from mkdocs_panzoom_plugin.panzoom_box import PanZoomBox

class HTMLPage:
    def __init__(self, content:str, config):
        self.soup = BeautifulSoup(content,"html.parser")
        self.config = config
        self.containers = self._find_elements()


    def __str__(self):
        return str(self.soup)


    def add_panzoom(self):
        for element in self.containers:
            panzoom_box = create_panzoom_box(self.soup,self.config)
            #panzoom_box = PanZoomBox.PANZOOM_BOX

            element.wrap(panzoom_box)

        #print(self.soup.prettify())

        # Include the css and js in the file
        self.soup.head.append(create_css_link(self.soup))
        self.soup.body.append(create_js_script(self.soup))
        self.soup.body.append(create_js_script_plugin(self.soup))

    def _find_elements(self):

        return self.soup.findAll(class_="mermaid")
