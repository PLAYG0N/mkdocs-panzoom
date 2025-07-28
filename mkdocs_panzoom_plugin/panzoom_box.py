"""Panzoom box creation utilities for the mkdocs-panzoom plugin."""

from typing import Any

from bs4 import BeautifulSoup, Tag
from mkdocs import utils
from mkdocs.structure.pages import Page


def create_info_box(soup: BeautifulSoup, config: dict[str, Any]) -> Tag:
    """Create an information box for pan-zoom hints."""
    always_hint = config.get("always_show_hint", False)
    key = config.get("key", "alt")

    if config.get("hint_location", "bottom") == "top":
        css_class = "panzoom-info-box-top"
    else:
        css_class = "panzoom-info-box"

    if always_hint:
        info_box = soup.new_tag("div", attrs={"class": css_class})
    else:
        info_box = soup.new_tag("div", attrs={"class": css_class + " panzoom-hidden"})

    action_text = " to disable Pan & Zoom (for text selection)"
    key_messages = {
        "alt": f'Press "Alt" / "Option"{action_text}',
        "ctrl": f'Press "Ctrl"{action_text}',
        "shift": f'Press "Shift"{action_text}',
    }

    # Ensure key is a string for the get() call
    key_str = str(key) if key is not None else "alt"
    info_box.string = key_messages.get(
        key_str, f"Press modifier key{action_text}"
    )  # info_box.string = 'Press "Alt" / "Option" to enable Pan & Zoom'

    return info_box


def create_button_info(soup: BeautifulSoup) -> Tag:
    """Create an info button for the panzoom interface."""
    info = soup.new_tag("button", attrs={"class": "panzoom-info panzoom-button"})

    info_svg = soup.new_tag(
        "svg",
        attrs={
            "class": "panzoom-icon",
            "xmlns": "http://www.w3.org/2000/svg",
            "viewBox": "0 0 512 512",
        },
    )

    info_path = soup.new_tag(
        "path",
        attrs={
            "d": "M464 256A208 208 0 1 0 48 256a208 208 0 1 0 416 0zM0 256a256 256 0 1 1 512 0A256 256 0 1 1 0 256zm169.8-90.7c7.9-22.3 29.1-37.3 52.8-37.3l58.3 0c34.9 0 63.1 28.3 63.1 63.1c0 22.6-12.1 43.5-31.7 54.8L280 264.4c-.2 13-10.9 23.6-24 23.6c-13.3 0-24-10.7-24-24l0-13.5c0-8.6 4.6-16.5 12.1-20.8l44.3-25.4c4.7-2.7 7.6-7.7 7.6-13.1c0-8.4-6.8-15.1-15.1-15.1l-58.3 0c-3.4 0-6.4 2.1-7.5 5.3l-.4 1.2c-4.4 12.5-18.2 19-30.6 14.6s-19-18.2-14.6-30.6l.4-1.2zM224 352a32 32 0 1 1 64 0 32 32 0 1 1 -64 0z"
        },
    )

    info_svg.append(info_path)

    info.append(info_svg)

    return info


def create_button_reset(soup: BeautifulSoup) -> Tag:
    """Create a reset button for the panzoom interface."""
    reset = soup.new_tag("button", attrs={"class": "panzoom-reset panzoom-button"})

    reset_svg = soup.new_tag(
        "svg",
        attrs={
            "class": "panzoom-icon",
            "xmlns": "http://www.w3.org/2000/svg",
            "viewBox": "0 0 512 512",
        },
    )

    reset_path = soup.new_tag(
        "path",
        attrs={
            "d": "M125.7 160l50.3 0c17.7 0 32 14.3 32 32s-14.3 32-32 32L48 224c-17.7 0-32-14.3-32-32L16 64c0-17.7 14.3-32 32-32s32 14.3 32 32l0 51.2L97.6 97.6c87.5-87.5 229.3-87.5 316.8 0s87.5 229.3 0 316.8s-229.3 87.5-316.8 0c-12.5-12.5-12.5-32.8 0-45.3s32.8-12.5 45.3 0c62.5 62.5 163.8 62.5 226.3 0s62.5-163.8 0-226.3s-163.8-62.5-226.3 0L125.7 160z"
        },
    )

    reset_svg.append(reset_path)

    reset.append(reset_svg)

    return reset


def create_button_max(soup: BeautifulSoup) -> Tag:
    """Create a maximize/fullscreen button for the panzoom interface."""
    max_button = soup.new_tag("button", attrs={"class": "panzoom-max panzoom-button"})

    max_svg = soup.new_tag(
        "svg",
        attrs={
            "class": "panzoom-icon",
            "xmlns": "http://www.w3.org/2000/svg",
            "viewBox": "0 0 448 512",
        },
    )

    max_path = soup.new_tag(
        "path",
        attrs={
            "d": "M32 32C14.3 32 0 46.3 0 64l0 96c0 17.7 14.3 32 32 32s32-14.3 32-32l0-64 64 0c17.7 0 32-14.3 32-32s-14.3-32-32-32L32 32zM64 352c0-17.7-14.3-32-32-32s-32 14.3-32 32l0 96c0 17.7 14.3 32 32 32l96 0c17.7 0 32-14.3 32-32s-14.3-32-32-32l-64 0 0-64zM320 32c-17.7 0-32 14.3-32 32s14.3 32 32 32l64 0 0 64c0 17.7 14.3 32 32 32s32-14.3 32-32l0-96c0-17.7-14.3-32-32-32l-96 0zM448 352c0-17.7-14.3-32-32-32s-32 14.3-32 32l0 64-64 0c-17.7 0-32 14.3-32 32s14.3 32 32 32l96 0c17.7 0 32-14.3 32-32l0-96z"
        },
    )

    max_svg.append(max_path)

    max_button.append(max_svg)

    return max_button


def create_button_min(soup: BeautifulSoup, hidden: bool = True) -> Tag:
    """Create a minimize button for the panzoom interface."""
    if hidden:
        min_button = soup.new_tag(
            "button", attrs={"class": "panzoom-min panzoom-button panzoom-hidden"}
        )
    else:
        min_button = soup.new_tag("button", attrs={"class": "panzoom-min panzoom-button"})

    min_svg = soup.new_tag(
        "svg",
        attrs={
            "class": "panzoom-icon",
            "xmlns": "http://www.w3.org/2000/svg",
            "viewBox": "0 0 448 512",
        },
    )

    min_path = soup.new_tag(
        "path",
        attrs={
            "d": "M160 64c0-17.7-14.3-32-32-32s-32 14.3-32 32l0 64-64 0c-17.7 0-32 14.3-32 32s14.3 32 32 32l96 0c17.7 0 32-14.3 32-32l0-96zM32 320c-17.7 0-32 14.3-32 32s14.3 32 32 32l64 0 0 64c0 17.7 14.3 32 32 32s32-14.3 32-32l0-96c0-17.7-14.3-32-32-32l-96 0zM352 64c0-17.7-14.3-32-32-32s-32 14.3-32 32l0 96c0 17.7 14.3 32 32 32l96 0c17.7 0 32-14.3 32-32s-14.3-32-32-32l-64 0 0-64zM320 320c-17.7 0-32 14.3-32 32l0 96c0 17.7 14.3 32 32 32s32-14.3 32-32l0-64 64 0c17.7 0 32-14.3 32-32s-14.3-32-32-32l-96 0z"
        },
    )

    min_svg.append(min_path)
    min_button.append(min_svg)

    return min_button


def create_button_zoom_in(soup: BeautifulSoup) -> Tag:
    """Create a zoom in button for the panzoom interface."""
    zoom_in = soup.new_tag("button", attrs={"class": "panzoom-zoom-in panzoom-button"})

    zoom_in_svg = soup.new_tag(
        "svg",
        attrs={
            "class": "panzoom-icon",
            "xmlns": "http://www.w3.org/2000/svg",
            "viewBox": "0 0 448 512",
        },
    )

    zoom_in_path = soup.new_tag(
        "path",
        attrs={
            "d": "M256 80c0-17.7-14.3-32-32-32s-32 14.3-32 32V224H48c-17.7 0-32 14.3-32 32s14.3 32 32 32H192V432c0 17.7 14.3 32 32 32s32-14.3 32-32V288H400c17.7 0 32-14.3 32-32s-14.3-32-32-32H256V80z"
        },
    )

    zoom_in_svg.append(zoom_in_path)
    zoom_in.append(zoom_in_svg)

    return zoom_in


def create_button_zoom_out(soup: BeautifulSoup) -> Tag:
    """Create a zoom out button for the panzoom interface."""
    zoom_out = soup.new_tag("button", attrs={"class": "panzoom-zoom-out panzoom-button"})

    zoom_out_svg = soup.new_tag(
        "svg",
        attrs={
            "class": "panzoom-icon",
            "xmlns": "http://www.w3.org/2000/svg",
            "viewBox": "0 0 448 512",
        },
    )

    zoom_out_path = soup.new_tag(
        "path",
        attrs={
            "d": "M432 256c0 17.7-14.3 32-32 32L48 288c-17.7 0-32-14.3-32-32s14.3-32 32-32l352 0c17.7 0 32 14.3 32 32z"
        },
    )

    zoom_out_svg.append(zoom_out_path)
    zoom_out.append(zoom_out_svg)

    return zoom_out


def create_panzoom_box(soup: BeautifulSoup, config: dict[str, Any], id: int | str) -> Tag:
    """Create the main panzoom container box with all controls."""
    always_hint = config.get("always_show_hint", False)

    panzoom_box = soup.new_tag(
        "div",
        attrs={
            "class": "panzoom-box",
            "id": "panzoom" + str(id),
            "oncontextmenu": "return false;",
        },
    )

    panzoom_box.attrs["data-key"] = config.get("key", "none")

    if config.get("hint_location", "bottom") == "top":
        nav_class = "panzoom-nav-infobox-top"
    else:
        nav_class = "panzoom-top-nav"

    nav = soup.new_tag(
        "nav",
        attrs={
            "class": nav_class,
            # "title": "material-fullscreen"
        },
    )

    info = create_button_info(soup)
    reset = create_button_reset(soup)
    max_button = create_button_max(soup)
    min_button = create_button_min(soup)
    zoom_in = create_button_zoom_in(soup)
    zoom_out = create_button_zoom_out(soup)

    # remove info button on permanent info banner
    if not always_hint:
        nav.append(info)

    nav.append(reset)

    # Add zoom in/out buttons if enabled
    if config.get("show_zoom_buttons", False):
        nav.append(zoom_in)
        nav.append(zoom_out)

    if config.get("full_screen", False):
        nav.append(max_button)
        nav.append(min_button)

    info_box = create_info_box(soup, config)

    if config.get("hint_location", "bottom") == "top":
        panzoom_box.append(info_box)

    panzoom_box.append(nav)

    # CRITICAL FIX: Add info box at bottom if hint_location is "bottom"
    if config.get("hint_location", "bottom") == "bottom":
        panzoom_box.append(info_box)

    return panzoom_box


def create_css_link(soup: BeautifulSoup, page: Page) -> Tag:
    """Create a CSS link tag for the panzoom stylesheet."""
    href = utils.get_relative_url(utils.normalize_url("assets/stylesheets/panzoom.css"), page.url)
    return soup.new_tag("link", attrs={"rel": "stylesheet", "href": href})


def create_js_script(soup: BeautifulSoup, page: Page) -> Tag:
    """Create a script tag for the panzoom JavaScript library."""
    src = utils.get_relative_url(
        utils.normalize_url("assets/javascripts/panzoom.min.js"), page.url
    )
    return soup.new_tag("script", attrs={"src": src})


def create_js_script_plugin(soup: BeautifulSoup, page: Page) -> Tag:
    """Create a script tag for the panzoom plugin JavaScript."""
    src = utils.get_relative_url(utils.normalize_url("assets/javascripts/zoompan.js"), page.url)
    return soup.new_tag("script", attrs={"src": src})


def create_fullscreen_modal(soup: BeautifulSoup, config: dict[str, Any]) -> Tag:
    """Create a fullscreen modal for the panzoom interface."""
    modal = soup.new_tag(
        "div", attrs={"class": "panzoom-fullscreen-modal", "id": "panzoom-fullscreen-modal"}
    )

    nav = soup.new_tag(
        "nav",
        attrs={
            "class": "panzoom-top-nav",
            # "title": "material-fullscreen"
        },
    )

    info = create_button_info(soup)
    reset = create_button_reset(soup)
    min_button = create_button_min(soup, False)
    zoom_in = create_button_zoom_in(soup)
    zoom_out = create_button_zoom_out(soup)

    # remove info button on permanent info banner
    if not config.get("always_show_hint", False):
        nav.append(info)

    nav.append(reset)

    # Add zoom in/out buttons if enabled
    if config.get("show_zoom_buttons", False):
        nav.append(zoom_in)
        nav.append(zoom_out)

    nav.append(min_button)

    modal.append(nav)

    # CRITICAL FIX: Add info box to fullscreen modal if not always showing hint
    if not config.get("always_show_hint", False):
        info_box = create_info_box(soup, config)
        modal.append(info_box)

    return modal
