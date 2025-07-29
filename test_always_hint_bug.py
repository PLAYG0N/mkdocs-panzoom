#!/usr/bin/env python3
"""Test script to reproduce the always_show_hint button disappearing bug."""

from bs4 import BeautifulSoup

from mkdocs_panzoom_plugin.panzoom_box import create_panzoom_box


def test_always_hint_top():
    """Test always_show_hint: true with hint_location: top."""
    soup = BeautifulSoup("<html><head></head><body></body></html>", "html.parser")

    config = {
        "always_show_hint": True,
        "hint_location": "top",
        "full_screen": True,
        "show_zoom_buttons": True,
        "key": "alt",
    }

    box = create_panzoom_box(soup, config, 1)

    print("=== always_show_hint: True, hint_location: top ===")
    print(box.prettify())

    # Check navigation class
    nav = box.find("nav")
    print(f"Navigation class: {nav.get('class')}")

    # Check if info box exists and its position
    info_box = box.find("div", class_=lambda x: x and ("panzoom-info-box" in x))
    print(f"Info box class: {info_box.get('class') if info_box else 'None'}")

    # Check if all buttons exist
    buttons = box.find_all("button", class_="panzoom-button")
    button_classes = [btn.get("class") for btn in buttons]
    print(f"Button classes: {button_classes}")

    print("\n")


def test_always_hint_bottom():
    """Test always_show_hint: true with hint_location: bottom."""
    soup = BeautifulSoup("<html><head></head><body></body></html>", "html.parser")

    config = {
        "always_show_hint": True,
        "hint_location": "bottom",
        "full_screen": True,
        "show_zoom_buttons": True,
        "key": "alt",
    }

    box = create_panzoom_box(soup, config, 1)

    print("=== always_show_hint: True, hint_location: bottom ===")
    print(box.prettify())

    # Check navigation class
    nav = box.find("nav")
    print(f"Navigation class: {nav.get('class')}")

    # Check if info box exists and its position
    info_box = box.find("div", class_=lambda x: x and ("panzoom-info-box" in x))
    print(f"Info box class: {info_box.get('class') if info_box else 'None'}")

    # Check if all buttons exist
    buttons = box.find_all("button", class_="panzoom-button")
    button_classes = [btn.get("class") for btn in buttons]
    print(f"Button classes: {button_classes}")

    print("\n")


def test_normal_hint_top():
    """Test always_show_hint: false with hint_location: top."""
    soup = BeautifulSoup("<html><head></head><body></body></html>", "html.parser")

    config = {
        "always_show_hint": False,
        "hint_location": "top",
        "full_screen": True,
        "show_zoom_buttons": True,
        "key": "alt",
    }

    box = create_panzoom_box(soup, config, 1)

    print("=== always_show_hint: False, hint_location: top ===")
    print(box.prettify())

    # Check navigation class
    nav = box.find("nav")
    print(f"Navigation class: {nav.get('class')}")

    # Check if info box exists and its position
    info_box = box.find("div", class_=lambda x: x and ("panzoom-info-box" in x))
    print(f"Info box class: {info_box.get('class') if info_box else 'None'}")

    # Check if all buttons exist
    buttons = box.find_all("button", class_="panzoom-button")
    button_classes = [btn.get("class") for btn in buttons]
    print(f"Button classes: {button_classes}")


if __name__ == "__main__":
    test_always_hint_top()
    test_always_hint_bottom()
    test_normal_hint_top()
