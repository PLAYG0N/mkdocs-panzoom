"""MkDocs plugin for adding pan and zoom functionality to images and diagrams."""

import logging
import os
from collections import OrderedDict
from typing import Any

from mkdocs import utils
from mkdocs.config import config_options
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.exceptions import ConfigurationError
from mkdocs.plugins import BasePlugin
from mkdocs.structure.pages import Page

from mkdocs_panzoom_plugin.exclude import exclude
from mkdocs_panzoom_plugin.html_page import HTMLPage


logger = logging.getLogger("mkdocs.plugin")
base_path = os.path.dirname(os.path.abspath(__file__))


class PanZoomPlugin(BasePlugin):
    """MkDocs plugin that adds pan and zoom functionality to images and mermaid diagrams."""

    config_scheme = (
        ("mermaid", config_options.Type(bool, default=True)),
        ("images", config_options.Type(bool, default=False)),
        ("full_screen", config_options.Type(bool, default=False)),
        ("always_show_hint", config_options.Type(bool, default=False)),
        ("show_zoom_buttons", config_options.Type(bool, default=False)),
        ("key", config_options.Type(str, default="alt")),
        ("include", config_options.Type(list, default=["*"])),
        ("exclude", config_options.Type(list, default=[])),
        ("include_selectors", config_options.Type(list, default=[])),
        ("exclude_selectors", config_options.Type(list, default=[])),
        ("hint_location", config_options.Type(str, default="bottom")),
        ("initial_zoom_level", config_options.Type(float, default=1.0)),
        ("zoom_step", config_options.Type(float, default=0.2)),
        ("buttons_size", config_options.Type(str, default="1.25em")),
    )

    def on_config(self, config: MkDocsConfig, **kwargs: Any) -> MkDocsConfig:
        """Configure the plugin and validate settings."""
        # Handle case where plugins might be missing or different types
        if "plugins" not in config:
            return config

        plugins_config = config["plugins"]
        plugins_dict: OrderedDict[str, Any]
        if isinstance(plugins_config, list):
            # Convert list to OrderedDict for processing
            plugins_dict = OrderedDict(
                (p, {}) if isinstance(p, str) else (p, {}) for p in plugins_config
            )
        elif isinstance(plugins_config, dict):
            plugins_dict = OrderedDict(plugins_config)
        else:
            plugins_dict = plugins_config

        plugins = [*plugins_dict]

        def check_position(plugin: str, plugins: list[str]) -> None:
            """Check if the panzoom plugin is positioned correctly relative to other plugins."""
            if plugin in plugins:
                if plugins.index("panzoom") < plugins.index(plugin):
                    raise ConfigurationError(
                        f"[panzoom-plugin] The panzoom-plugin should be defined after {plugin}"
                    )

        check_plugins = ["mermaid2"]

        for p in check_plugins:
            check_position(p, plugins)

        # Validate configuration values
        self._validate_config()

        return config

    def _validate_config(self) -> None:
        """Validate plugin configuration values."""
        # Validate key options
        valid_keys = {"alt", "ctrl", "shift", "none"}
        key = self.config.get("key", "alt")
        if key not in valid_keys:
            logger.warning(
                f"Invalid key '{key}'. Using default 'alt'. Valid options: {valid_keys}"
            )
            self.config["key"] = "alt"

        # Validate hint location
        valid_locations = {"top", "bottom"}
        hint_location = self.config.get("hint_location", "bottom")
        if hint_location not in valid_locations:
            logger.warning(
                f"Invalid hint_location '{hint_location}'. Using default 'bottom'. "
                f"Valid options: {valid_locations}"
            )
            self.config["hint_location"] = "bottom"

        # Validate zoom values
        zoom_step = self.config.get("zoom_step", 0.2)
        if not isinstance(zoom_step, int | float) or zoom_step <= 0:
            logger.warning(f"Invalid zoom_step '{zoom_step}'. Using default 0.2")
            self.config["zoom_step"] = 0.2

        initial_zoom = self.config.get("initial_zoom_level", 1.0)
        if not isinstance(initial_zoom, int | float) or initial_zoom <= 0:
            logger.warning(f"Invalid initial_zoom_level '{initial_zoom}'. Using default 1.0")
            self.config["initial_zoom_level"] = 1.0

    def on_post_page(self, output: str, /, *, page: Page, config: MkDocsConfig) -> str | None:
        """Process page after HTML generation to add pan-zoom functionality."""
        try:
            excluded_pages = self.config.get("exclude", [])

            if exclude(page.file.src_path, excluded_pages):
                return output  # Return original output for excluded pages

            html_page = HTMLPage(output, self.config, page, config)
            html_page.add_panzoom()

            return str(html_page)

        except Exception as e:
            logger.error(f"Error processing page {page.file.src_path}: {e}")
            # Return original output on error to prevent build failure
            return output

    def on_post_build(self, *, config: MkDocsConfig) -> None:
        """Copy plugin assets to the site directory."""
        try:
            output_base_path = os.path.join(config["site_dir"], "assets")

            # Ensure directories exist
            css_path = os.path.join(output_base_path, "stylesheets")
            js_path = os.path.join(output_base_path, "javascripts")

            os.makedirs(css_path, exist_ok=True)
            os.makedirs(js_path, exist_ok=True)

            # Copy CSS file
            utils.copy_file(
                os.path.join(base_path, "custom", "panzoom.css"),
                os.path.join(css_path, "panzoom.css"),
            )

            # Copy JavaScript files
            utils.copy_file(
                os.path.join(base_path, "custom", "zoompan.js"),
                os.path.join(js_path, "zoompan.js"),
            )
            utils.copy_file(
                os.path.join(base_path, "panzoom", "panzoom.min.js"),
                os.path.join(js_path, "panzoom.min.js"),
            )

            logger.debug("Successfully copied panzoom plugin assets")

        except Exception as e:
            logger.error(f"Error copying panzoom plugin assets: {e}")
            raise
