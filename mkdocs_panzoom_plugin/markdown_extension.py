from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
from markdown.postprocessors import Postprocessor
from mkdocs_panzoom_plugin.panzoom_box import create_panzoom_box

import xml.etree.ElementTree as etree
import re

CLASS_PART1 = r"(<(\w+)[^>]*class\s*=\s*[\"']([^\"']*\b)?"
CLASS_PART2 = r"(\b[^\"']*)?[\"'][^>]*>(?:.|\n)*?</\2>)"

ID_PART1 = r"(<(\w+)[^>]*id\s*=\s*[\"']"
ID_PART2 = r"[\"'][^>]*>(?:.|\n)*?<\/\2>)"

def TAG(tag:str):
    return f"((?:<({tag})[^\\/>]*>(?:.|\\n)*?<\\/\\2>)|(?:<({tag})[^>]*\\/>))"

class PanZoomExtension(Extension):
    def __init__(self, **kwargs):
        self.config = {
            'full_screen': [False, 'Enables fullscreen'],
            'always_show_hint': [False, 'Permanently show hint'],
            'key': ['alt', 'Key to hold to enable panzoom'],
            'selectors': [[".mermaid", ".d2", "img"], 'Selectors on which to enable panzoom'],
            'hint_location': ['bottom', 'Hint bottom/top'],
            'initial_zoom_level': [1.0, 'Initial zoom level'],
        }
        super().__init__(**kwargs)
    
    def extendMarkdown(self, md):
        md.registerExtension(self)
        # insert processors and patterns here
        md.postprocessors.register(PanZoomPostprocessor(self.getConfigs(),md=md), "panzoom", -1)
        # return super().extendMarkdown(md)

class PanZoomPostprocessor(Postprocessor):
    def __init__(self, config:dict, md = None, ):
        self.selectors = config.get("selectors", [])
        self.config = config
        super().__init__(md)
    
    def run(self, text):
        # print(text)
        sub = create_panzoom_box(config=self.config, id=0)
        for selector in self.selectors:
            if selector.startswith("."):
                pattern =  re.compile(f"{CLASS_PART1}{selector.lstrip('.')}{CLASS_PART2}")
            elif selector.startswith("#"):
                pattern = re.compile(f"{ID_PART1}{selector.lstrip('#')}{ID_PART2}")
            else:
                pattern = re.compile(TAG(selector))
            text = re.sub(pattern, sub, text, count=0)
            # re.search()

        # print(text)
        return text
        # return super().run(text)

def makeExtension(**kwargs):
    return PanZoomExtension(**kwargs)