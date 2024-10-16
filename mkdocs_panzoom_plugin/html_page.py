import re
import logging
import json
from bs4 import BeautifulSoup

from mkdocs_panzoom_plugin import panzoom_box
from mkdocs_panzoom_plugin.panzoom_box import *

class HTMLPage:
    def __init__(self, content:str, config, page):
        self.soup = BeautifulSoup(content,"html.parser")
        self.config = config
        self.page = page
        self.default_selectors = {".mermaid", ".d2"}
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

        self._add_data_for_js()

    def _add_data_for_js(self):
        meta_tag = self.soup.new_tag("meta")
        meta_tag["name"] = "panzoom-data"
        meta_tag["content"] = json.dumps({
            "selectors": self.config.get("selectors")
            })
        self.soup.head.append(meta_tag)

    def _find_elements(self):
        output = []
        
        # get final set of selectors
        included_selectors = set(self.config.get("include_selectors", [])) | set()
        excluded_selectors = set(self.config.get("exclude_selectors", [])) | set()

        final_selectors = self.default_selectors.difference(excluded_selectors)
        final_selectors.update(included_selectors) 

        if self.config.get("images",False):
            final_selectors.add("img")


        if not self.config.get("mermaid",False):
            final_selectors.remove(".mermaid")


        self.config.update({"selectors": list(final_selectors)})

        for selector in self.default_selectors:
            if selector.startswith("."):
                output += self.soup.findAll(class_=selector.lstrip("."))
            elif selector.startswith("#"):
                id_element = self.soup.find(id=selector.lstrip("#"))
                if not id_element is None:
                    output.append(id_element)
            else:
                output += self.soup.findAll(selector)

        return output
