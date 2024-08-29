import logging
from collections import OrderedDict
import os

from mkdocs import plugins
from mkdocs import utils
from mkdocs.config import config_options, defaults
from mkdocs.plugins import BasePlugin
from mkdocs.exceptions import ConfigurationError
from mkdocs_panzoom_plugin.exclude import exclude,include
from mkdocs_panzoom_plugin.html_page import HTMLPage

logger = logging.getLogger("mkdocs.plugin")
base_path = os.path.dirname(os.path.abspath(__file__))

class PanZoomPlugin(BasePlugin):
    config_scheme = (
        ("mermaid", config_options.Type(bool, default=True)),
        ("images", config_options.Type(bool, default=False)),
        ("full_screen", config_options.Type(bool, default=False)),
        ("include", config_options.Type(list, default=["*"])),
        ("exclude", config_options.Type(list, default=[])),
    )

    def on_config(self, config, **kwargs):

        plugins = [*OrderedDict(config["plugins"])]

        def check_position(plugin, plugins):
            if plugin in plugins:
                if plugins.index("panzoom") < plugins.index(plugin):
                    raise ConfigurationError(
                        "[panzoom-plugin] The panzoom-plugin should be defined after " + plugin
                    )

        check_plugins = [
            "mermaid2"
        ]

        for p in check_plugins:
            check_position(p,plugins)

        return config

    def on_post_page(self, output: str, /, *, page, config):

        excluded_pages = self.config.get("exclude",[])

        if exclude(page.file.src_path,excluded_pages):
            return

        #print(page.content)

        html_page = HTMLPage(output,self.config,page)

        html_page.add_panzoom()

        return str(html_page)

    def on_post_build(self, *, config):
        """Copy files to the assets"""

        output_base_path = os.path.join(config["site_dir"], "assets")
        css_path = os.path.join(output_base_path, "stylesheets")
        print(css_path)
        utils.copy_file(
            os.path.join(base_path, "custom", "panzoom.css"),
            os.path.join(css_path, "panzoom.css"),
        )
        js_path = os.path.join(output_base_path, "javascripts")
        utils.copy_file(
            os.path.join(base_path, "custom", "zoompan.js"),
            os.path.join(js_path, "zoompan.js"),
        )
        utils.copy_file(
                    os.path.join(base_path, "panzoom", "panzoom.min.js"),
                    os.path.join(js_path, "panzoom.min.js"),
                )
