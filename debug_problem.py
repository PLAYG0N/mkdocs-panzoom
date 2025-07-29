#!/usr/bin/env python3
"""Debug the specific problematic case."""

from bs4 import BeautifulSoup

from mkdocs_panzoom_plugin.panzoom_box import create_panzoom_box


def debug_problematic_case():
    """Debug always_show_hint=True, hint_location=bottom case."""
    soup = BeautifulSoup("<html><head></head><body></body></html>", "html.parser")

    config = {
        "always_show_hint": True,
        "hint_location": "bottom",
        "full_screen": True,
        "show_zoom_buttons": True,
        "key": "alt",
    }

    box = create_panzoom_box(soup, config, 1)

    print("=== PROBLEMATIC CASE ANALYSIS ===")
    print("Config: always_show_hint=True, hint_location=bottom")
    print()

    print("Full HTML structure:")
    print(box.prettify())
    print()

    # Analyze structure
    nav = box.find("nav")
    info_box = box.find("div", class_=lambda x: x and ("panzoom-info-box" in x))

    print("Navigation element:")
    print(f"  Classes: {nav.get('class')}")
    print(f"  Position in box: {list(box.children).index(nav)}")
    print()

    print("Info box element:")
    print(f"  Classes: {info_box.get('class')}")
    print(f"  Position in box: {list(box.children).index(info_box)}")
    print()

    # Check all buttons in nav
    buttons = nav.find_all("button", class_="panzoom-button")
    print(f"Buttons in navigation: {len(buttons)}")
    for i, btn in enumerate(buttons):
        classes = btn.get("class", [])
        primary_class = [c for c in classes if c.startswith("panzoom-") and c != "panzoom-button"][
            0
        ]
        print(f"  {i + 1}. {primary_class}: {classes}")

    print()
    print("Child elements order in panzoom-box:")
    for i, child in enumerate(box.children):
        if hasattr(child, "name") and child.name:
            classes = child.get("class", [])
            print(f"  {i + 1}. <{child.name}> classes: {classes}")


if __name__ == "__main__":
    debug_problematic_case()
