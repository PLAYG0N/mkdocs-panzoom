"""Test for the hint button bug where clicking (?) hides all top-right buttons."""

from unittest.mock import Mock

import pytest
from bs4 import BeautifulSoup

from mkdocs_panzoom_plugin.panzoom_box import create_panzoom_box


@pytest.fixture
def soup():
    """Create a BeautifulSoup instance for testing."""
    return BeautifulSoup("<html><head></head><body></body></html>", "html.parser")


@pytest.fixture
def mock_page():
    """Create a mock page object."""
    page = Mock()
    page.url = "test/"
    return page


@pytest.fixture
def full_config():
    """Create a full configuration with all buttons enabled."""
    return {
        "always_show_hint": False,  # This ensures info button is present
        "full_screen": True,  # This enables max/min buttons
        "show_zoom_buttons": True,  # This enables zoom in/out buttons
        "key": "alt",
        "hint_location": "bottom",
    }


class TestHintButtonBug:
    """Test the hint button bug where clicking (?) affects other buttons."""

    def test_hint_button_exists_with_other_buttons(self, soup, full_config):
        """Test that all buttons exist when configured."""
        box = create_panzoom_box(soup, full_config, 0)

        # Verify info button exists (the ? button)
        info_button = box.find("button", class_="panzoom-info")
        assert info_button is not None, "Info button (?) should exist"

        # Verify other buttons exist
        reset_button = box.find("button", class_="panzoom-reset")
        max_button = box.find("button", class_="panzoom-max")
        min_button = box.find("button", class_="panzoom-min")
        zoom_in_button = box.find("button", class_="panzoom-zoom-in")
        zoom_out_button = box.find("button", class_="panzoom-zoom-out")

        assert reset_button is not None, "Reset button should exist"
        assert max_button is not None, "Max button should exist"
        assert min_button is not None, "Min button should exist"
        assert zoom_in_button is not None, "Zoom in button should exist"
        assert zoom_out_button is not None, "Zoom out button should exist"

    def test_info_box_structure_correct(self, soup, full_config):
        """Test that info box structure is correct and scoped properly."""
        box = create_panzoom_box(soup, full_config, 0)

        # Find the info box
        info_box = box.find("div", class_="panzoom-info-box")
        assert info_box is not None, "Info box should exist"

        # Verify it has the hidden class by default
        assert "panzoom-hidden" in info_box.get("class", []), (
            "Info box should be hidden by default"
        )

        # Verify info box is inside the panzoom box (proper scoping)
        assert info_box.find_parent("div", class_="panzoom-box") is not None, (
            "Info box should be scoped to panzoom box"
        )

    def test_navigation_structure_isolation(self, soup, full_config):
        """Test that navigation structure is properly isolated."""
        box = create_panzoom_box(soup, full_config, 0)

        # Find the navigation container
        nav = box.find("nav", class_="panzoom-top-nav")
        assert nav is not None, "Navigation should exist"

        # Verify navigation contains the buttons
        nav_buttons = nav.find_all("button", class_="panzoom-button")
        assert len(nav_buttons) > 0, "Navigation should contain buttons"

        # Verify navigation is properly scoped within the box
        assert nav.find_parent("div", class_="panzoom-box") is not None, (
            "Navigation should be scoped to panzoom box"
        )

    def test_button_isolation_classes(self, soup, full_config):
        """Test that buttons have proper classes for isolation."""
        box = create_panzoom_box(soup, full_config, 0)

        # Get all buttons
        buttons = box.find_all("button", class_="panzoom-button")

        # Each button should have unique identifying classes
        expected_button_classes = [
            "panzoom-info",
            "panzoom-reset",
            "panzoom-max",
            "panzoom-min",
            "panzoom-zoom-in",
            "panzoom-zoom-out",
        ]

        found_classes = []
        for button in buttons:
            button_classes = button.get("class", [])
            for expected_class in expected_button_classes:
                if expected_class in button_classes:
                    found_classes.append(expected_class)

        # Verify all expected button types are found
        for expected_class in expected_button_classes:
            assert expected_class in found_classes, (
                f"Button with class {expected_class} should exist"
            )

    def test_multiple_panzoom_boxes_isolation(self, soup, full_config):
        """Test that multiple panzoom boxes don't interfere with each other."""
        # Create two separate panzoom boxes
        box1 = create_panzoom_box(soup, full_config, 1)
        box2 = create_panzoom_box(soup, full_config, 2)

        # Verify each box has its own info button and info box
        info_button1 = box1.find("button", class_="panzoom-info")
        info_button2 = box2.find("button", class_="panzoom-info")
        info_box1 = box1.find("div", class_="panzoom-info-box")
        info_box2 = box2.find("div", class_="panzoom-info-box")

        assert info_button1 is not None, "Box1 should have info button"
        assert info_button2 is not None, "Box2 should have info button"
        assert info_box1 is not None, "Box1 should have info box"
        assert info_box2 is not None, "Box2 should have info box"

        # Verify they have the same structure (the reuse is actually expected behavior in this context)
        assert info_button1.get("class") == info_button2.get("class"), (
            "Info buttons should have same classes"
        )
        assert info_box1.get("class") == info_box2.get("class"), (
            "Info boxes should have same classes"
        )

        # Verify the boxes themselves have different IDs for proper scoping
        assert box1.get("id") != box2.get("id"), "Boxes should have different IDs"
        assert box1.get("id") == "panzoom1", "Box1 should have ID panzoom1"
        assert box2.get("id") == "panzoom2", "Box2 should have ID panzoom2"

    def test_hint_button_javascript_integration(self, soup, full_config):
        """Test that hint button JavaScript functionality is properly isolated."""
        box = create_panzoom_box(soup, full_config, 0)

        # Convert to string to simulate how it would appear in HTML
        html_content = str(box)

        # Verify the structure contains proper selectors for JavaScript
        assert 'class="panzoom-info panzoom-button"' in html_content, (
            "Info button should have correct classes"
        )
        assert 'class="panzoom-info-box panzoom-hidden"' in html_content, (
            "Info box should have correct classes"
        )
        assert 'id="panzoom0"' in html_content, "Box should have unique ID for scoping"

        # Verify other buttons have proper classes
        assert 'class="panzoom-reset panzoom-button"' in html_content, (
            "Reset button should have correct classes"
        )
        assert 'class="panzoom-max panzoom-button"' in html_content, (
            "Max button should have correct classes"
        )

    def test_hint_location_top_structure(self, soup, full_config):
        """Test hint location 'top' creates proper structure."""
        config = full_config.copy()
        config["hint_location"] = "top"

        box = create_panzoom_box(soup, config, 0)

        # When always_show_hint is False (from full_config), navigation should use
        # panzoom-top-nav for better UX (buttons at corner)
        nav = box.find("nav", class_="panzoom-top-nav")
        assert nav is not None, "Should use panzoom-top-nav class when always_show_hint is False"

        # Should use different info box class
        info_box = box.find("div", class_="panzoom-info-box-top")
        assert info_box is not None, "Should use panzoom-info-box-top class when hint is at top"
