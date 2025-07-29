#!/usr/bin/env python3
"""Comprehensive test script to verify all button positioning scenarios."""

from bs4 import BeautifulSoup

from mkdocs_panzoom_plugin.panzoom_box import create_panzoom_box


def test_all_scenarios():
    """Test all combinations of always_show_hint and hint_location."""
    soup = BeautifulSoup("<html><head></head><body></body></html>", "html.parser")

    scenarios = [
        # (always_show_hint, hint_location, expected_nav_class, expected_info_class)
        (False, "top", "panzoom-top-nav", "panzoom-info-box-top panzoom-hidden"),
        (False, "bottom", "panzoom-top-nav", "panzoom-info-box panzoom-hidden"),
        (True, "top", "panzoom-nav-infobox-top", "panzoom-info-box-top"),
        (True, "bottom", "panzoom-top-nav", "panzoom-info-box"),
    ]

    print("=== COMPREHENSIVE BUTTON POSITIONING TEST ===\n")

    for i, (always_hint, hint_loc, expected_nav, expected_info) in enumerate(scenarios, 1):
        config = {
            "always_show_hint": always_hint,
            "hint_location": hint_loc,
            "full_screen": True,
            "show_zoom_buttons": True,
            "key": "alt",
        }

        box = create_panzoom_box(soup, config, i)

        # Get actual values
        nav = box.find("nav")
        nav_classes = " ".join(nav.get("class", []))

        info_box = box.find("div", class_=lambda x: x and ("panzoom-info-box" in x))
        info_classes = " ".join(info_box.get("class", [])) if info_box else "None"

        # Check if correct
        nav_correct = nav_classes == expected_nav
        info_correct = info_classes == expected_info

        status = "✅ PASS" if (nav_correct and info_correct) else "❌ FAIL"

        print(f"Test {i}: always_show_hint={always_hint}, hint_location='{hint_loc}'")
        print(f"  Navigation class: {nav_classes} {'✅' if nav_correct else '❌'}")
        print(f"  Expected nav:     {expected_nav}")
        print(f"  Info box class:   {info_classes} {'✅' if info_correct else '❌'}")
        print(f"  Expected info:    {expected_info}")
        print(f"  Result: {status}")
        print()

    print("=== BUTTON POSITIONING EXPLANATION ===")
    print("• panzoom-top-nav (top: 10px) = buttons at top-right corner")
    print("• panzoom-nav-infobox-top (top: 51px) = buttons below the top hint")
    print("• This ensures buttons are always visible and properly positioned")


if __name__ == "__main__":
    test_all_scenarios()
