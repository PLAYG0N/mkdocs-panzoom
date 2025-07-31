from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
from markdown.postprocessors import Postprocessor

import xml.etree.ElementTree as etree
import re


class PanZoomExtension(Extension):
    def __init__(self, **kwargs):
        self.config = {
            'full_screen': [False, 'Enables fullscreen'],
            'always_show_hint': [False, 'Permanently show hint'],
            'key': ['alt', 'Key to press to enable panzoom'],
            'selectors': [[".mermaid", ".d2", "img"], 'Selectors on which to enable panzoom'],
            'hint_location': ['bottom', 'Hint bottom/top'],
        }
        super().__init__(**kwargs)
    
    def extendMarkdown(self, md):
        md.registerExtension(self)
        # self.md = md
        # insert processors and patterns here
        # md.treeprocessors.register(PanZoomTreeprocessor(md = md, selectors = self.getConfig("selectors", [])), "panzoom", -1)
        md.postprocessors.register(PanZoomPostprocessor(md=md,selectors=self.getConfig("selectors", [])), "panzoom", -1)
        # return super().extendMarkdown(md)

class PanZoomTreeprocessor(Treeprocessor):
    def __init__(self, md = None, selectors = []):
        self.selectors = selectors
        super().__init__(md)

    def run(self, root:etree.Element):
        print(etree.tostring(root,"unicode", "html"))
        # print(self.md.htmlStash.rawHtmlBlocks)
        self.containers = self.find_all(root)
        # print(self.containers)
        return super().run(root)

    def find_all(self,root:etree.Element):
        output = []
        for selector in self.selectors:
            if selector.startswith("."):
                _selector = ".//*[@class='%s']" % selector.lstrip(".")
            elif selector.startswith("#"):
                _selector = ".//*[@id='%s']" % selector.lstrip("#")
            else:
                _selector = ".//%s" % selector
            output += root.findall(_selector)
        
        print(output)

        return output

class PanZoomPostprocessor(Postprocessor):
    def __init__(self, md = None, selectors = []):
        self.selectors = selectors
        super().__init__(md)
    
    def run(self, text):
        # print(text)
        for selector in self.selectors:
            if selector.startswith("."):
                _selector =  re.compile(f"<(\w+)[^>]*class\s*=\s*[\"']([^\"']*\b)?{selector.lstrip(".")}(\b[^\"']*)?[\"'][^>]*>")
            elif selector.startswith("#"):
                _selector = ".//*[@id='%s']" % selector.lstrip("#")
            else:
                _selector = ".//%s" % selector
            
            re.search()

        return text
        # return super().run(text)

def makeExtension(**kwargs):
    return PanZoomExtension(**kwargs)