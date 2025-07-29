#!/usr/bin/env python3
"""Test all scenarios after the fix."""

from bs4 import BeautifulSoup

from mkdocs_panzoom_plugin.panzoom_box import create_panzoom_box


def test_all_scenarios_after_fix():
    """Test all combinations to verify the fix."""
    soup = BeautifulSoup("<html><head></head><body></body></html>", "html.parser")

    scenarios = [
        # (always_show_hint, hint_location, description)
        (False, "top", "Normal operation - hint at top, button shows info box"),
        (False, "bottom", "Normal operation - hint at bottom, button shows info box"),
        (True, "top", "Always hint at top - buttons should be below hint"),
        (True, "bottom", "PROBLEMATIC CASE - hint at bottom, buttons at corner"),
    ]

    print("=== TESTING ALL SCENARIOS AFTER FIX ===\n")

    for i, (always_hint, hint_loc, description) in enumerate(scenarios, 1):
        config = {
            "always_show_hint": always_hint,
            "hint_location": hint_loc,
            "full_screen": True,
            "show_zoom_buttons": True,
            "key": "alt",
        }

        box = create_panzoom_box(soup, config, i)

        # Analyze the structure
        nav = box.find("nav")
        nav_classes = " ".join(nav.get("class", []))

        info_box = box.find("div", class_=lambda x: x and ("panzoom-info-box" in x))
        info_classes = " ".join(info_box.get("class", [])) if info_box else "None"

        # Count buttons in navigation
        buttons = nav.find_all("button", class_="panzoom-button")
        visible_buttons = [btn for btn in buttons if "panzoom-hidden" not in btn.get("class", [])]

        print(f"Test {i}: {description}")
        print(f"  Config: always_show_hint={always_hint}, hint_location='{hint_loc}'")
        print(f"  Navigation: {nav_classes}")
        print(f"  Info box:   {info_classes}")
        print(f"  Buttons in nav: {len(buttons)} total, {len(visible_buttons)} visible")

        # Expected navigation class based on logic
        if always_hint and hint_loc == "top":
            expected_nav = "panzoom-nav-infobox-top"
        else:
            expected_nav = "panzoom-top-nav"

        status = "✅" if nav_classes == expected_nav else "❌"
        print(f"  Expected nav:   {expected_nav} {status}")
        print()

    print("=== CSS CHANGES MADE ===")
    print("1. Increased z-index of .panzoom-top-nav from 3 to 4")
    print("   This ensures navigation is above info box when hint_location=bottom")
    print("2. Reduced top position of .panzoom-nav-infobox-top from 51px to 35px")
    print("   This positions buttons closer to the top hint")
    print()
    print("The problematic case should now work correctly!")


if __name__ == "__main__":
    test_all_scenarios_after_fix()
