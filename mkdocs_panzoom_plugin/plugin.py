import logging
from collections import OrderedDict
import os
import re

from mkdocs import utils
from mkdocs.config import config_options, defaults
from mkdocs.plugins import BasePlugin
from mkdocs.exceptions import ConfigurationError
from mkdocs_panzoom_plugin.exclude import exclude,include
from mkdocs_panzoom_plugin.html_page import create_meta_tags

logger = logging.getLogger("mkdocs.plugin")
base_path = os.path.dirname(os.path.abspath(__file__))

class PanZoomPlugin(BasePlugin):
    config_scheme = (
        ("mermaid", config_options.Type(bool, default=True)),
        ("images", config_options.Type(bool, default=False)),
        ("full_screen", config_options.Type(bool, default=False)),
        ("always_show_hint", config_options.Type(bool, default=False)),
        ("key", config_options.Type(str, default="alt")),
        # ("include", config_options.Type(list, default=["*"])),
        ("exclude", config_options.Type(list, default=[])),
        ("include_selectors", config_options.Type(list, default=[])),
        ("exclude_selectors", config_options.Type(list, default=[])),
        ("hint_location", config_options.Type(str, default="bottom")),
        ("initial_zoom_level", config_options.Type(float, default=1.0)),
    )
    default_selectors = {".mermaid", ".d2"}

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

        config["extra_css"].append("assets/stylesheets/panzoom.css")
        config["extra_javascript"].append("assets/javascripts/panzoom.min.js")
        config["extra_javascript"].append("assets/javascripts/zoompan.js")

        # get final set of selectors
        included_selectors = set(self.config.get("include_selectors", [])) | set()
        excluded_selectors = set(self.config.get("exclude_selectors", [])) | set()
        final_selectors = self.default_selectors.difference(excluded_selectors)
        final_selectors.update(included_selectors) 

        if config.get("images",False):
            final_selectors.add("img")
        if not config.get("mermaid",True):
            final_selectors.remove(".mermaid")

        config.update({"selectors": list(final_selectors)})
        self.config.update({"selectors": list(final_selectors)})
        local_config:dict = self.config

        local_config.pop("mermaid")
        local_config.pop("images")
        local_config.pop("exclude")
        local_config.pop("include_selectors")
        local_config.pop("exclude_selectors")
        mdx_configs: dict = config.get("mdx_configs")
        mdx_configs.update({"panzoom": local_config})

        mdx_extensions = config.get("markdown_extensions")
        mdx_extensions.append("panzoom")

        config.update({"mdx_configs": mdx_configs})
        config.update({"markdown_extensions": mdx_extensions})

        return config

    def on_post_page(self, output: str, /, *, page, config):

        excluded_pages = self.config.get("exclude",[])

        if exclude(page.file.src_path,excluded_pages):
            return

        html_page = re.sub(r"(<\/head>)", f"{create_meta_tags(config)} \\1", output, count=1) 
        return str(html_page)

    def on_post_build(self, *, config):
        """Copy files to the assets"""

        output_base_path = os.path.join(config["site_dir"], "assets")
        css_path = os.path.join(output_base_path, "stylesheets")
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

        # Profiler().print_stats()
