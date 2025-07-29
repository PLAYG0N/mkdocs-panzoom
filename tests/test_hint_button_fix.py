"""Test hint button bug fix."""

import pytest
from bs4 import BeautifulSoup

from mkdocs_panzoom_plugin.panzoom_box import create_panzoom_box


class TestHintButtonFix:
    """Test that the hint button fix works correctly."""

    @pytest.fixture
    def soup(self):
        """Create a BeautifulSoup instance for testing."""
        return BeautifulSoup("", "html.parser")

    @pytest.fixture
    def basic_config(self):
        """Return basic configuration for testing."""
        return {
            "always_show_hint": False,
            "hint_location": "bottom",
            "full_screen": True,
            "show_zoom_buttons": True,
        }

    def test_info_box_scoping_isolation(self, soup, basic_config):
        """Test that info box manipulation doesn't affect other buttons."""
        box = create_panzoom_box(soup, basic_config, 1)

        # Verify all expected buttons exist
        info_button = box.find("button", class_="panzoom-info")
        reset_button = box.find("button", class_="panzoom-reset")
        max_button = box.find("button", class_="panzoom-max")
        zoom_in_button = box.find("button", class_="panzoom-zoom-in")
        zoom_out_button = box.find("button", class_="panzoom-zoom-out")

        assert info_button is not None
        assert reset_button is not None
        assert max_button is not None
        assert zoom_in_button is not None
        assert zoom_out_button is not None

        # Verify info box exists and has the correct initial state
        info_box = box.find("div", class_=lambda x: x and ("panzoom-info-box" in x))
        assert info_box is not None

        # Info box should start hidden if always_show_hint is False
        assert "panzoom-hidden" in info_box.get("class", [])

        # Ensure no other buttons have the hidden class
        assert "panzoom-hidden" not in reset_button.get("class", [])
        assert "panzoom-hidden" not in max_button.get("class", [])
        assert "panzoom-hidden" not in zoom_in_button.get("class", [])
        assert "panzoom-hidden" not in zoom_out_button.get("class", [])

    def test_info_box_toggle_state_independence(self, soup, basic_config):
        """Test that info box state changes don't affect navigation buttons."""
        box = create_panzoom_box(soup, basic_config, 1)

        # Get the info box
        info_box = box.find("div", class_=lambda x: x and ("panzoom-info-box" in x))
        assert info_box is not None

        # Simulate showing the info box (removing hidden class)
        if "panzoom-hidden" in info_box.get("class", []):
            classes = info_box.get("class", [])
            classes.remove("panzoom-hidden")
            info_box["class"] = classes

        # Verify other buttons are still not hidden
        reset_button = box.find("button", class_="panzoom-reset")
        max_button = box.find("button", class_="panzoom-max")
        zoom_in_button = box.find("button", class_="panzoom-zoom-in")

        assert "panzoom-hidden" not in reset_button.get("class", [])
        assert "panzoom-hidden" not in max_button.get("class", [])
        assert "panzoom-hidden" not in zoom_in_button.get("class", [])

        # Simulate hiding the info box again (adding hidden class)
        classes = info_box.get("class", [])
        if "panzoom-hidden" not in classes:
            classes.append("panzoom-hidden")
            info_box["class"] = classes

        # Verify other buttons are still not hidden
        assert "panzoom-hidden" not in reset_button.get("class", [])
        assert "panzoom-hidden" not in max_button.get("class", [])
        assert "panzoom-hidden" not in zoom_in_button.get("class", [])

    def test_info_box_selector_specificity(self, soup, basic_config):
        """Test that the info box selector is specific enough."""
        box = create_panzoom_box(soup, basic_config, 1)

        # Test both possible info box classes
        info_box_bottom = box.find("div", class_="panzoom-info-box")
        info_box_top = box.find("div", class_="panzoom-info-box-top")

        # One of them should exist (depending on hint_location)
        assert (info_box_bottom is not None) or (info_box_top is not None)

        # Verify that the nav container doesn't have info box classes
        nav = box.find("nav")
        assert nav is not None
        nav_classes = nav.get("class", [])
        assert "panzoom-info-box" not in nav_classes
        assert "panzoom-info-box-top" not in nav_classes

    def test_multiple_panzoom_boxes_isolation(self, soup, basic_config):
        """Test that multiple panzoom boxes don't interfere with each other."""
        # Create two separate panzoom boxes
        box1 = create_panzoom_box(soup, basic_config, 1)
        box2 = create_panzoom_box(soup, basic_config, 2)

        # Verify each has its own info box
        info_box1 = box1.find("div", class_=lambda x: x and ("panzoom-info-box" in x))
        info_box2 = box2.find("div", class_=lambda x: x and ("panzoom-info-box" in x))

        assert info_box1 is not None
        assert info_box2 is not None
        # Verify info boxes are in different containers (different parents)
        assert info_box1.parent != info_box2.parent

        # Verify each has its own set of buttons
        buttons1 = box1.find_all("button", class_="panzoom-button")
        buttons2 = box2.find_all("button", class_="panzoom-button")

        assert len(buttons1) > 0
        assert len(buttons2) > 0

        # Buttons should be different objects (verify they have different parent containers)
        assert box1 != box2
