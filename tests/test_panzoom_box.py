"""Test the panzoom_box module functionality."""

import pytest
from bs4 import BeautifulSoup

from mkdocs_panzoom_plugin.panzoom_box import (
    create_button_info,
    create_button_max,
    create_button_min,
    create_button_reset,
    create_button_zoom_in,
    create_button_zoom_out,
    create_css_link,
    create_fullscreen_modal,
    create_info_box,
    create_js_script,
    create_js_script_plugin,
    create_panzoom_box,
)


@pytest.fixture
def soup():
    """Create a BeautifulSoup instance for testing."""
    return BeautifulSoup("<html><head></head><body></body></html>", "html.parser")


@pytest.fixture
def mock_page():
    """Create a mock page object for testing."""
    from unittest.mock import Mock

    page = Mock()
    page.url = "test/"
    return page


@pytest.fixture
def basic_config():
    """Create a basic configuration for testing."""
    return {
        "key": "alt",
        "always_show_hint": False,
        "full_screen": False,
        "show_zoom_buttons": False,
        "hint_location": "bottom",
        "buttons_size": "1.25em",
    }


class TestInfoBox:
    """Test info box creation functionality."""

    def test_create_info_box_bottom(self, soup, basic_config):
        """Test creating info box at bottom."""
        info_box = create_info_box(soup, basic_config)

        assert info_box.name == "div"
        assert "panzoom-info-box" in info_box.get("class")
        assert "panzoom-hidden" in info_box.get("class")
        assert 'Press "Alt"' in info_box.string

    def test_create_info_box_top(self, soup, basic_config):
        """Test creating info box at top."""
        config = basic_config.copy()
        config["hint_location"] = "top"

        info_box = create_info_box(soup, config)

        assert "panzoom-info-box-top" in info_box.get("class")

    def test_create_info_box_always_show(self, soup, basic_config):
        """Test creating info box that's always visible."""
        config = basic_config.copy()
        config["always_show_hint"] = True

        info_box = create_info_box(soup, config)

        assert "panzoom-hidden" not in info_box.get("class")

    def test_create_info_box_different_keys(self, soup, basic_config):
        """Test info box with different key configurations."""
        keys_and_messages = [
            ("ctrl", 'Press "Ctrl"'),
            ("shift", 'Press "Shift"'),
            ("none", "Press modifier key"),
        ]

        for key, expected_text in keys_and_messages:
            config = basic_config.copy()
            config["key"] = key

            info_box = create_info_box(soup, config)
            assert expected_text in info_box.string


class TestButtons:
    """Test button creation functionality."""

    def test_create_button_info(self, soup):
        """Test creating info button."""
        button = create_button_info(soup)

        assert button.name == "button"
        assert "panzoom-info" in button.get("class")
        assert "panzoom-button" in button.get("class")

        # Check SVG icon
        svg = button.find("svg")
        assert svg is not None
        assert svg.get("viewBox") == "0 0 512 512"

    def test_create_button_reset(self, soup):
        """Test creating reset button."""
        button = create_button_reset(soup)

        assert button.name == "button"
        assert "panzoom-reset" in button.get("class")
        assert "panzoom-button" in button.get("class")

    def test_create_button_max(self, soup):
        """Test creating maximize button."""
        button = create_button_max(soup)

        assert button.name == "button"
        assert "panzoom-max" in button.get("class")
        assert "panzoom-button" in button.get("class")

    def test_create_button_min_hidden(self, soup):
        """Test creating minimize button (hidden by default)."""
        button = create_button_min(soup)

        assert button.name == "button"
        assert "panzoom-min" in button.get("class")
        assert "panzoom-button" in button.get("class")
        assert "panzoom-hidden" in button.get("class")

    def test_create_button_min_visible(self, soup):
        """Test creating minimize button (visible)."""
        button = create_button_min(soup, hidden=False)

        assert "panzoom-hidden" not in button.get("class")

    def test_create_button_zoom_in(self, soup):
        """Test creating zoom in button."""
        button = create_button_zoom_in(soup)

        assert button.name == "button"
        assert "panzoom-zoom-in" in button.get("class")
        assert "panzoom-button" in button.get("class")

    def test_create_button_zoom_out(self, soup):
        """Test creating zoom out button."""
        button = create_button_zoom_out(soup)

        assert button.name == "button"
        assert "panzoom-zoom-out" in button.get("class")
        assert "panzoom-button" in button.get("class")


class TestPanzoomBox:
    """Test main panzoom box creation."""

    def test_create_panzoom_box_basic(self, soup, basic_config):
        """Test creating basic panzoom box."""
        box = create_panzoom_box(soup, basic_config, 1)

        assert box.name == "div"
        assert "panzoom-box" in box.get("class")
        assert box.get("id") == "panzoom1"
        assert box.get("data-key") == "alt"

        # Check navigation
        nav = box.find("nav")
        assert nav is not None
        assert "panzoom-top-nav" in nav.get("class")

    def test_create_panzoom_box_with_fullscreen(self, soup, basic_config):
        """Test creating panzoom box with fullscreen enabled."""
        config = basic_config.copy()
        config["full_screen"] = True

        box = create_panzoom_box(soup, config, 1)

        # Should have max and min buttons
        max_button = box.find("button", class_="panzoom-max")
        min_button = box.find("button", class_="panzoom-min")

        assert max_button is not None
        assert min_button is not None

    def test_create_panzoom_box_with_zoom_buttons(self, soup, basic_config):
        """Test creating panzoom box with zoom buttons enabled."""
        config = basic_config.copy()
        config["show_zoom_buttons"] = True

        box = create_panzoom_box(soup, config, 1)

        # Should have zoom in/out buttons
        zoom_in = box.find("button", class_="panzoom-zoom-in")
        zoom_out = box.find("button", class_="panzoom-zoom-out")

        assert zoom_in is not None
        assert zoom_out is not None

    def test_create_panzoom_box_always_show_hint(self, soup, basic_config):
        """Test creating panzoom box with always visible hint."""
        config = basic_config.copy()
        config["always_show_hint"] = True

        box = create_panzoom_box(soup, config, 1)

        # Should not have info button when hint is always shown
        info_button = box.find("button", class_="panzoom-info")
        assert info_button is None

    def test_create_panzoom_box_hint_location_top(self, soup, basic_config):
        """Test creating panzoom box with hint at top."""
        config = basic_config.copy()
        config["hint_location"] = "top"

        box = create_panzoom_box(soup, config, 1)

        # When always_show_hint is False (default), navigation should use
        # panzoom-top-nav regardless of hint_location for better UX
        nav = box.find("nav")
        assert "panzoom-top-nav" in nav.get("class")

    def test_create_panzoom_box_hint_location_top_always_show(self, soup, basic_config):
        """Test creating panzoom box with hint at top and always visible."""
        config = basic_config.copy()
        config["hint_location"] = "top"
        config["always_show_hint"] = True

        box = create_panzoom_box(soup, config, 1)

        # When always_show_hint is True and hint_location is top,
        # navigation should use panzoom-nav-infobox-top to avoid overlap
        nav = box.find("nav")
        assert "panzoom-nav-infobox-top" in nav.get("class")

        # Info box should be visible (no hidden class)
        info_box = box.find("div", class_="panzoom-info-box-top")
        assert info_box is not None
        assert "panzoom-hidden" not in info_box.get("class", [])

    def test_create_panzoom_box_hint_location_bottom_always_show(self, soup, basic_config):
        """Test creating panzoom box with hint at bottom and always visible."""
        config = basic_config.copy()
        config["hint_location"] = "bottom"
        config["always_show_hint"] = True

        box = create_panzoom_box(soup, config, 1)

        # When always_show_hint is True and hint_location is bottom,
        # navigation should use panzoom-top-nav (buttons at corner)
        nav = box.find("nav")
        assert "panzoom-top-nav" in nav.get("class")

        # Info box should be visible (no hidden class)
        info_box = box.find("div", class_="panzoom-info-box")
        assert info_box is not None
        assert "panzoom-hidden" not in info_box.get("class", [])

    def test_create_panzoom_box_navigation_structure(self, soup, basic_config):
        """Test that navigation buttons are properly structured and contained."""
        config = basic_config.copy()
        config["full_screen"] = True
        config["show_zoom_buttons"] = True

        box = create_panzoom_box(soup, config, 1)

        # Check navigation container exists
        nav = box.find("nav", class_="panzoom-top-nav")
        assert nav is not None

        # Check that all buttons are within the navigation
        buttons_in_nav = nav.find_all("button", class_="panzoom-button")
        assert len(buttons_in_nav) >= 4  # info, reset, max, zoom_in, zoom_out

        # Check specific buttons exist in navigation
        info_button = nav.find("button", class_="panzoom-info")
        reset_button = nav.find("button", class_="panzoom-reset")
        max_button = nav.find("button", class_="panzoom-max")
        zoom_in_button = nav.find("button", class_="panzoom-zoom-in")
        zoom_out_button = nav.find("button", class_="panzoom-zoom-out")

        assert info_button is not None
        assert reset_button is not None
        assert max_button is not None
        assert zoom_in_button is not None
        assert zoom_out_button is not None

        # Ensure min button exists but is hidden initially
        min_button = nav.find("button", class_="panzoom-min")
        assert min_button is not None
        assert "panzoom-hidden" in min_button.get("class")

    def test_info_button_click_isolation(self, soup, basic_config):
        """Test that info button functionality doesn't affect other buttons."""
        config = basic_config.copy()
        config["full_screen"] = True  # Enable fullscreen to get max button

        box = create_panzoom_box(soup, config, 1)

        # Ensure info button has proper click isolation structure
        info_button = box.find("button", class_="panzoom-info")
        assert info_button is not None

        # Check that other buttons remain visible when box is created
        reset_button = box.find("button", class_="panzoom-reset")
        max_button = box.find("button", class_="panzoom-max")

        assert reset_button is not None
        assert max_button is not None

        # Ensure no unexpected hidden classes on navigation buttons
        assert "panzoom-hidden" not in reset_button.get("class", [])
        assert "panzoom-hidden" not in max_button.get("class", [])
        assert "panzoom-hidden" not in info_button.get("class", [])


class TestAssetCreation:
    """Test asset link/script creation."""

    def test_create_css_link(self, soup, mock_page):
        """Test creating CSS link tag."""
        link = create_css_link(soup, mock_page)

        assert link.name == "link"
        rel_attr = link.get("rel")
        if isinstance(rel_attr, list):
            assert "stylesheet" in rel_attr
        else:
            assert rel_attr == "stylesheet"
        assert "panzoom.css" in link.get("href")

    def test_create_js_script(self, soup, mock_page):
        """Test creating JavaScript script tag."""
        script = create_js_script(soup, mock_page)

        assert script.name == "script"
        assert "panzoom.min.js" in script.get("src")

    def test_create_js_script_plugin(self, soup, mock_page):
        """Test creating plugin JavaScript script tag."""
        script = create_js_script_plugin(soup, mock_page)

        assert script.name == "script"
        assert "zoompan.js" in script.get("src")


class TestFullscreenModal:
    """Test fullscreen modal creation."""

    def test_create_fullscreen_modal_basic(self, soup, basic_config):
        """Test creating basic fullscreen modal."""
        modal = create_fullscreen_modal(soup, basic_config)

        assert modal.name == "div"
        assert "panzoom-fullscreen-modal" in modal.get("class")
        assert modal.get("id") == "panzoom-fullscreen-modal"

        # Should have navigation
        nav = modal.find("nav")
        assert nav is not None

    def test_create_fullscreen_modal_with_zoom_buttons(self, soup, basic_config):
        """Test creating fullscreen modal with zoom buttons."""
        config = basic_config.copy()
        config["show_zoom_buttons"] = True

        modal = create_fullscreen_modal(soup, config)

        # Should have zoom buttons
        zoom_in = modal.find("button", class_="panzoom-zoom-in")
        zoom_out = modal.find("button", class_="panzoom-zoom-out")

        assert zoom_in is not None
        assert zoom_out is not None

    def test_create_fullscreen_modal_without_info_button(self, soup, basic_config):
        """Test fullscreen modal without info button when hint always shown."""
        config = basic_config.copy()
        config["always_show_hint"] = True

        modal = create_fullscreen_modal(soup, config)

        # Should not have info button
        info_button = modal.find("button", class_="panzoom-info")
        assert info_button is None

    def test_create_fullscreen_modal_with_info_box(self, soup, basic_config):
        """Test fullscreen modal includes info box when hint not always shown."""
        modal = create_fullscreen_modal(soup, basic_config)

        # Should have info box appended
        info_box = modal.find("div", class_="panzoom-info-box")
        assert info_box is not None


class TestInfoBoxJavaScriptCompatibility:
    """Test that generated HTML is compatible with JavaScript selectors."""

    def test_panzoom_box_has_correct_info_box_selectors(self, soup, basic_config):
        """Test that panzoom box generates info boxes with correct classes for JS selection."""
        # Test bottom hint location (default)
        box_bottom = create_panzoom_box(soup, basic_config, 0)
        info_box_bottom = box_bottom.find("div", class_="panzoom-info-box")
        assert info_box_bottom is not None

        # Test top hint location
        config_top = basic_config.copy()
        config_top["hint_location"] = "top"
        box_top = create_panzoom_box(soup, config_top, 1)
        info_box_top = box_top.find("div", class_="panzoom-info-box-top")
        assert info_box_top is not None

    def test_info_button_exists_when_not_always_showing_hint(self, soup, basic_config):
        """Test that info button is generated when hint is not always shown."""
        basic_config["always_show_hint"] = False
        box = create_panzoom_box(soup, basic_config, 0)

        info_button = box.find("button", class_="panzoom-info")
        assert info_button is not None

        # Verify the button has the correct structure for JavaScript to attach events
        svg = info_button.find("svg")
        assert svg is not None

    def test_info_button_missing_when_always_showing_hint(self, soup, basic_config):
        """Test that info button is not generated when hint is always shown."""
        basic_config["always_show_hint"] = True
        box = create_panzoom_box(soup, basic_config, 0)

        info_button = box.find("button", class_="panzoom-info")
        assert info_button is None
