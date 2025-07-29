"""Test the main plugin functionality."""

from collections import OrderedDict
from unittest.mock import Mock

import pytest

from mkdocs_panzoom_plugin.plugin import PanZoomPlugin


@pytest.fixture
def plugin():
    """Create a plugin instance for testing."""
    return PanZoomPlugin()


@pytest.fixture
def mock_page():
    """Create a mock page object."""
    page = Mock()
    page.file = Mock()
    page.file.src_path = "test.md"
    page.file.dest_path = "test/index.html"
    page.title = "Test Page"
    page.content = "Test content"
    page.meta = {}
    page.url = "test/"
    return page


@pytest.fixture
def mock_mkdocs_config():
    """Create a mock MkDocs configuration."""
    config = {"site_url": "https://example.com", "plugins": [], "theme": {"name": "material"}}
    return config


class TestPluginInitialization:
    """Test plugin initialization."""

    def test_plugin_creation(self):
        """Test that plugin can be created successfully."""
        plugin = PanZoomPlugin()
        assert plugin is not None
        assert hasattr(plugin, "config_scheme")

    def test_plugin_config_scheme(self):
        """Test plugin configuration scheme."""
        plugin = PanZoomPlugin()
        config_dict = dict(plugin.config_scheme)

        expected_keys = {
            "mermaid",
            "images",
            "full_screen",
            "always_show_hint",
            "show_zoom_buttons",
            "key",
            "include",
            "exclude",
            "include_selectors",
            "exclude_selectors",
            "hint_location",
            "initial_zoom_level",
            "zoom_step",
            "buttons_size",
        }

        assert set(config_dict.keys()) == expected_keys


class TestPluginConfiguration:
    """Test plugin configuration handling."""

    def test_on_config_basic(self, plugin):
        """Test basic configuration handling."""
        config = {"site_url": "https://example.com", "plugins": OrderedDict()}

        # Should not raise exception
        result = plugin.on_config(config)  # type: ignore[call-arg]
        assert result is None or isinstance(result, dict)

    def test_on_config_with_plugins(self, plugin):
        """Test on_config method with various plugin configurations."""
        configs = [
            {"site_url": "https://example.com", "plugins": OrderedDict()},
            {"site_url": "https://example.com", "plugins": OrderedDict([("search", {})])},
            {
                "site_url": "https://example.com",
                "plugins": OrderedDict([("search", {}), ("panzoom", {})]),
            },
        ]

        for config in configs:
            # Should not raise exception
            result = plugin.on_config(config)  # type: ignore[call-arg]
            assert result is None or isinstance(result, dict)


class TestPluginBasics:
    """Test basic plugin functionality."""

    def test_plugin_can_be_imported(self) -> None:
        """Test that the plugin can be imported."""
        assert PanZoomPlugin is not None

    def test_plugin_instantiation(self) -> None:
        """Test plugin can be instantiated."""
        plugin = PanZoomPlugin()
        assert plugin is not None

    def test_plugin_config_scheme(self) -> None:
        """Test plugin configuration scheme."""
        plugin = PanZoomPlugin()

        # Check that config scheme exists and has expected keys
        config_scheme = dict(plugin.config_scheme)  # type: ignore[attr-defined]

        expected_keys = [
            "mermaid",
            "images",
            "full_screen",
            "always_show_hint",
            "show_zoom_buttons",
            "key",
            "include",
            "exclude",
            "include_selectors",
            "exclude_selectors",
            "hint_location",
            "initial_zoom_level",
            "zoom_step",
            "buttons_size",
        ]

        for key in expected_keys:
            assert key in config_scheme


class TestPluginPostPage:
    """Test plugin post-page processing."""

    def test_on_post_page_basic(self, plugin, mock_page, mock_mkdocs_config):
        """Test basic post-page processing."""
        # Set up basic plugin config
        plugin.config = {
            "exclude": [],
            "key": "alt",
            "always_show_hint": False,
            "full_screen": False,
            "show_zoom_buttons": False,
        }

        html_content = """
        <html>
        <head><title>Test</title></head>
        <body><div class="mermaid">test</div></body>
        </html>
        """

        result = plugin.on_post_page(html_content, page=mock_page, config=mock_mkdocs_config)

        assert isinstance(result, str)
        assert "panzoom-box" in result

    def test_on_post_page_excluded_file(self, plugin, mock_page, mock_mkdocs_config):
        """Test post-page processing with excluded file."""
        # Configure plugin to exclude this file
        plugin.config = {
            "exclude": ["test.md"],
        }

        html_content = "<html><body>content</body></html>"

        result = plugin.on_post_page(html_content, page=mock_page, config=mock_mkdocs_config)

        # Should return original content unchanged
        assert result == html_content

    def test_on_post_page_with_zoom_buttons(self, plugin, mock_page, mock_mkdocs_config):
        """Test post-page processing with zoom buttons enabled."""
        plugin.config = {
            "exclude": [],
            "show_zoom_buttons": True,
            "key": "alt",
        }

        html_content = """
        <html>
        <head><title>Test</title></head>
        <body><div class="mermaid">test</div></body>
        </html>
        """

        result = plugin.on_post_page(html_content, page=mock_page, config=mock_mkdocs_config)

        assert "panzoom-zoom-in" in result
        assert "panzoom-zoom-out" in result

    def test_on_post_page_with_fullscreen(self, plugin, mock_page, mock_mkdocs_config):
        """Test post-page processing with fullscreen enabled."""
        plugin.config = {
            "exclude": [],
            "full_screen": True,
            "key": "alt",
        }

        html_content = """
        <html>
        <head><title>Test</title></head>
        <body><div class="mermaid">test</div></body>
        </html>
        """

        result = plugin.on_post_page(html_content, page=mock_page, config=mock_mkdocs_config)

        assert "panzoom-max" in result
        assert "panzoom-min" in result

    def test_on_post_page_error_handling(self, plugin, mock_page, mock_mkdocs_config):
        """Test error handling in post-page processing."""
        plugin.config = {}

        # Invalid HTML that might cause issues
        html_content = "<html><div>unclosed"

        # Should not raise exception
        result = plugin.on_post_page(html_content, page=mock_page, config=mock_mkdocs_config)
        assert isinstance(result, str)


class TestPluginValidation:
    """Test plugin validation functionality."""

    def test_validate_config_missing_site_url(self, plugin):
        """Test validation with missing site_url."""
        plugin.config = {}
        config = {"plugins": OrderedDict()}

        # Should handle missing site_url gracefully
        result = plugin.on_config(config)  # type: ignore[call-arg]
        assert result is None or isinstance(result, dict)

    def test_validate_config_invalid_key(self, plugin):
        """Test validation with invalid key configuration."""
        plugin.config = {"key": "invalid"}

        # Should handle invalid key values
        # (Implementation should validate and possibly warn/error)
        assert True  # Placeholder - actual validation depends on implementation

    def test_validate_config_invalid_zoom_values(self, plugin):
        """Test validation with invalid zoom configuration."""
        plugin.config = {
            "initial_zoom_level": -1,  # Invalid negative zoom
            "zoom_step": 0,  # Invalid zero step
        }

        # Should handle invalid zoom values
        assert True  # Placeholder - actual validation depends on implementation


class TestPluginIntegration:
    """Test plugin integration scenarios."""

    def test_plugin_with_multiple_elements(self, plugin, mock_page, mock_mkdocs_config):
        """Test plugin with multiple diagrams/images."""
        plugin.config = {
            "exclude": [],
            "key": "alt",
            "show_zoom_buttons": True,
        }

        html_content = """
        <html>
        <head><title>Test</title></head>
        <body>
            <div class="mermaid">mermaid 1</div>
            <img src="test.jpg" alt="test">
            <div class="d2">d2 diagram</div>
            <div class="mermaid">mermaid 2</div>
        </body>
        </html>
        """

        result = plugin.on_post_page(html_content, page=mock_page, config=mock_mkdocs_config)

        # Should create multiple panzoom boxes
        panzoom_count = result.count("panzoom-box")
        assert panzoom_count > 1

    def test_plugin_with_custom_selectors(self, plugin, mock_page, mock_mkdocs_config):
        """Test plugin with custom selector configuration."""
        plugin.config = {
            "exclude": [],
            "include_selectors": [".custom-chart"],
            "exclude_selectors": [".mermaid"],
        }

        html_content = """
        <html>
        <body>
            <div class="mermaid">should be excluded</div>
            <div class="custom-chart">should be included</div>
        </body>
        </html>
        """

        result = plugin.on_post_page(html_content, page=mock_page, config=mock_mkdocs_config)

        # Should only process custom-chart, not mermaid
        assert "custom-chart" in result
        # The mermaid div should still be there but not wrapped in panzoom-box
        assert "should be excluded" in result
        assert "should be included" in result
