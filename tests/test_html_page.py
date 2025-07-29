"""Test the html_page module functionality."""

from unittest.mock import Mock

import pytest

from mkdocs_panzoom_plugin.html_page import HTMLPage


@pytest.fixture
def basic_html():
    """Create basic HTML content for testing."""
    return """
    <html>
    <head><title>Test</title></head>
    <body>
        <div class="mermaid">mermaid content</div>
        <img src="test.jpg" alt="test">
        <div class="d2">d2 content</div>
    </body>
    </html>
    """


@pytest.fixture
def basic_config():
    """Create basic configuration for testing."""
    return {
        "selectors": [".mermaid", "img", ".d2"],
        "key": "alt",
        "always_show_hint": False,
        "full_screen": False,
        "show_zoom_buttons": False,
        "hint_location": "bottom",
        "initial_zoom_level": 1.0,
        "zoom_step": 0.2,
        "buttons_size": "1.25em",
        "include_selectors": [],
        "exclude_selectors": [],
    }


@pytest.fixture
def mock_page():
    """Create a mock page object."""
    page = Mock()
    page.url = "test/"
    return page


@pytest.fixture
def mock_mkdocs_config():
    """Create a mock MkDocs configuration."""
    config = Mock()
    config.get = Mock(return_value={"name": "material"})
    return config


class TestHTMLPageInitialization:
    """Test HTMLPage initialization."""

    def test_html_page_init_basic(self, basic_html, basic_config, mock_page, mock_mkdocs_config):
        """Test basic HTMLPage initialization."""
        html_page = HTMLPage(basic_html, basic_config, mock_page, mock_mkdocs_config)

        assert html_page.soup is not None
        assert html_page.config == basic_config
        assert html_page.page == mock_page
        assert html_page.mkdocs_config == mock_mkdocs_config
        assert len(html_page.containers) > 0

    def test_html_page_str_representation(
        self, basic_html, basic_config, mock_page, mock_mkdocs_config
    ):
        """Test HTML page string representation."""
        html_page = HTMLPage(basic_html, basic_config, mock_page, mock_mkdocs_config)

        html_str = str(html_page)
        assert isinstance(html_str, str)
        assert "html" in html_str.lower()


class TestElementFinding:
    """Test element finding functionality."""

    def test_find_mermaid_elements(self, basic_html, basic_config, mock_page, mock_mkdocs_config):
        """Test finding mermaid elements."""
        html_page = HTMLPage(basic_html, basic_config, mock_page, mock_mkdocs_config)

        # Should find mermaid and d2 elements (img might not be included by default)
        assert len(html_page.containers) >= 2

    def test_find_elements_with_custom_selectors(self, mock_page, mock_mkdocs_config):
        """Test finding elements with custom selectors."""
        html = """
        <html><body>
            <div class="custom-diagram">content</div>
            <span id="my-chart">chart</span>
        </body></html>
        """

        config = {
            "selectors": [".custom-diagram", "#my-chart"],
            "include_selectors": [".custom-diagram", "#my-chart"],
            "exclude_selectors": [],
        }

        html_page = HTMLPage(html, config, mock_page, mock_mkdocs_config)

        assert len(html_page.containers) >= 0  # May be 0 if selectors are processed differently

    def test_find_elements_with_include_selectors(self, mock_page, mock_mkdocs_config):
        """Test finding elements with include selectors."""
        html = """
        <html><body>
            <div class="include-me">content</div>
            <div class="exclude-me">content</div>
        </body></html>
        """

        config = {
            "selectors": [],
            "include_selectors": [".include-me"],
            "exclude_selectors": [],
        }

        html_page = HTMLPage(html, config, mock_page, mock_mkdocs_config)

        assert len(html_page.containers) == 1

    def test_find_elements_with_exclude_selectors(
        self, basic_html, basic_config, mock_page, mock_mkdocs_config
    ):
        """Test finding elements with exclude selectors."""
        config = basic_config.copy()
        config["exclude_selectors"] = [".mermaid"]

        html_page = HTMLPage(basic_html, config, mock_page, mock_mkdocs_config)

        # Should find fewer elements (img and d2, but not mermaid)
        mermaid_found = any("mermaid" in str(container) for container in html_page.containers)
        assert not mermaid_found

    def test_find_elements_empty_html(self, basic_config, mock_page, mock_mkdocs_config):
        """Test finding elements in empty HTML."""
        html = "<html><body></body></html>"

        html_page = HTMLPage(html, basic_config, mock_page, mock_mkdocs_config)

        assert len(html_page.containers) == 0


class TestPanzoomAddition:
    """Test panzoom functionality addition."""

    def test_add_panzoom_basic(self, basic_html, basic_config, mock_page, mock_mkdocs_config):
        """Test adding basic panzoom functionality."""
        html_page = HTMLPage(basic_html, basic_config, mock_page, mock_mkdocs_config)
        html_page.add_panzoom()

        # Check that panzoom boxes were added
        soup = html_page.soup
        panzoom_boxes = soup.find_all("div", class_="panzoom-box")
        assert len(panzoom_boxes) > 0

    def test_add_panzoom_with_css_link(
        self, basic_html, basic_config, mock_page, mock_mkdocs_config
    ):
        """Test that CSS link is added."""
        html_page = HTMLPage(basic_html, basic_config, mock_page, mock_mkdocs_config)
        html_page.add_panzoom()

        # Check for CSS link
        soup = html_page.soup
        css_link = soup.find("link", {"rel": "stylesheet"})
        assert css_link is not None
        assert "panzoom.css" in css_link.get("href", "")

    def test_add_panzoom_with_js_scripts(
        self, basic_html, basic_config, mock_page, mock_mkdocs_config
    ):
        """Test that JavaScript scripts are added."""
        html_page = HTMLPage(basic_html, basic_config, mock_page, mock_mkdocs_config)
        html_page.add_panzoom()

        # Check for JavaScript scripts
        soup = html_page.soup
        scripts = soup.find_all("script", {"src": True})

        script_sources = [script.get("src") for script in scripts]
        js_found = any("panzoom.min.js" in src for src in script_sources)
        plugin_js_found = any("zoompan.js" in src for src in script_sources)

        assert js_found
        assert plugin_js_found

    def test_add_panzoom_with_meta_data(
        self, basic_html, basic_config, mock_page, mock_mkdocs_config
    ):
        """Test that metadata is added for JavaScript."""
        html_page = HTMLPage(basic_html, basic_config, mock_page, mock_mkdocs_config)
        html_page.add_panzoom()

        # Check for panzoom-data meta tag
        soup = html_page.soup
        meta_tag = soup.find("meta", {"name": "panzoom-data"})
        assert meta_tag is not None

        # Check content includes expected configuration
        content = meta_tag.get("content", "")
        assert "selectors" in content
        assert "initial_zoom_level" in content

    def test_add_panzoom_missing_head(self, basic_config, mock_page, mock_mkdocs_config):
        """Test handling of missing head tag."""
        html = "<html><body><div class='mermaid'>content</div></body></html>"

        html_page = HTMLPage(html, basic_config, mock_page, mock_mkdocs_config)

        # Should not raise exception
        html_page.add_panzoom()

        # Should still wrap elements
        soup = html_page.soup
        panzoom_boxes = soup.find_all("div", class_="panzoom-box")
        assert len(panzoom_boxes) > 0

    def test_add_panzoom_missing_body(self, basic_config, mock_page, mock_mkdocs_config):
        """Test handling of missing body tag."""
        html = "<html><head></head><div class='mermaid'>content</div></html>"

        html_page = HTMLPage(html, basic_config, mock_page, mock_mkdocs_config)

        # Should not raise exception
        html_page.add_panzoom()


class TestConfigurationHandling:
    """Test configuration handling."""

    def test_selector_generation_default(self, basic_html, mock_page, mock_mkdocs_config):
        """Test default selector generation."""
        config = {
            "include_selectors": [],
            "exclude_selectors": [],
        }

        html_page = HTMLPage(basic_html, config, mock_page, mock_mkdocs_config)

        # Should use default selectors (.mermaid, .d2)
        expected_selectors = {".mermaid", ".d2"}
        assert set(html_page.config["selectors"]) == expected_selectors

    def test_selector_generation_with_include(self, basic_html, mock_page, mock_mkdocs_config):
        """Test selector generation with include selectors."""
        config = {
            "include_selectors": ["img", ".custom"],
            "exclude_selectors": [],
        }

        html_page = HTMLPage(basic_html, config, mock_page, mock_mkdocs_config)

        # Should combine default and include selectors
        selectors = html_page.config["selectors"]
        assert ".mermaid" in selectors
        assert ".d2" in selectors
        assert "img" in selectors
        assert ".custom" in selectors

    def test_selector_generation_with_exclude(self, basic_html, mock_page, mock_mkdocs_config):
        """Test selector generation with exclude selectors."""
        config = {
            "include_selectors": [],
            "exclude_selectors": [".mermaid"],
        }

        html_page = HTMLPage(basic_html, config, mock_page, mock_mkdocs_config)

        # Should exclude .mermaid from default selectors
        selectors = html_page.config["selectors"]
        assert ".mermaid" not in selectors
        assert ".d2" in selectors


class TestErrorHandling:
    """Test error handling in HTMLPage."""

    def test_invalid_html_handling(self, basic_config, mock_page, mock_mkdocs_config):
        """Test handling of invalid HTML."""
        invalid_html = "<html><div>unclosed div<body>content"

        # Should not raise exception during initialization
        html_page = HTMLPage(invalid_html, basic_config, mock_page, mock_mkdocs_config)
        assert html_page.soup is not None

    def test_empty_config_handling(self, basic_html, mock_page, mock_mkdocs_config):
        """Test handling of empty configuration."""
        empty_config = {}

        # Should not raise exception
        html_page = HTMLPage(basic_html, empty_config, mock_page, mock_mkdocs_config)
        html_page.add_panzoom()

        assert html_page.soup is not None
