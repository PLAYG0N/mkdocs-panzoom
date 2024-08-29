
from bs4 import BeautifulSoup
from mkdocs import utils
#from bs4.element import BeautifulSoup

def create_panzoom_box(soup,config):
    panzoom_box = soup.new_tag("div",**{"class": "panzoom-box"})
    nav = soup.new_tag("nav", **{
        "class": "panzoom-top-nav",
        #"title": "material-fullscreen"
    })

    reset = soup.new_tag("button", **{
        "class": "panzoom-reset panzoom-button"
    })

    reset_svg = soup.new_tag("svg", **{
        "class": "panzoom-icon",
        "xmlns": "http://www.w3.org/2000/svg",
        "viewBox": "0 0 512 512"
    })

    reset_path = soup.new_tag("path", **{
        "d": "M125.7 160l50.3 0c17.7 0 32 14.3 32 32s-14.3 32-32 32L48 224c-17.7 0-32-14.3-32-32L16 64c0-17.7 14.3-32 32-32s32 14.3 32 32l0 51.2L97.6 97.6c87.5-87.5 229.3-87.5 316.8 0s87.5 229.3 0 316.8s-229.3 87.5-316.8 0c-12.5-12.5-12.5-32.8 0-45.3s32.8-12.5 45.3 0c62.5 62.5 163.8 62.5 226.3 0s62.5-163.8 0-226.3s-163.8-62.5-226.3 0L125.7 160z"
    })

    reset_svg.append(reset_path)

    reset.append(reset_svg)



    max = soup.new_tag("button", **{
        "class": "panzoom-max panzoom-button"
    })

    max_svg = soup.new_tag("svg", **{
        "class": "panzoom-icon",
        "xmlns": "http://www.w3.org/2000/svg",
        "viewBox": "0 0 448 512"
    })

    max_path = soup.new_tag("path", **{
        "d": "M32 32C14.3 32 0 46.3 0 64l0 96c0 17.7 14.3 32 32 32s32-14.3 32-32l0-64 64 0c17.7 0 32-14.3 32-32s-14.3-32-32-32L32 32zM64 352c0-17.7-14.3-32-32-32s-32 14.3-32 32l0 96c0 17.7 14.3 32 32 32l96 0c17.7 0 32-14.3 32-32s-14.3-32-32-32l-64 0 0-64zM320 32c-17.7 0-32 14.3-32 32s14.3 32 32 32l64 0 0 64c0 17.7 14.3 32 32 32s32-14.3 32-32l0-96c0-17.7-14.3-32-32-32l-96 0zM448 352c0-17.7-14.3-32-32-32s-32 14.3-32 32l0 64-64 0c-17.7 0-32 14.3-32 32s14.3 32 32 32l96 0c17.7 0 32-14.3 32-32l0-96z"
    })

    max_svg.append(max_path)

    max.append(max_svg)

    min = soup.new_tag("button", **{
        "class": "panzoom-min panzoom-button panzoom-hidden"
    })

    min_svg = soup.new_tag("svg", **{
        "class": "panzoom-icon",
        "xmlns": "http://www.w3.org/2000/svg",
        "viewBox": "0 0 448 512"
    })

    min_path = soup.new_tag("path", **{
        "d": "M160 64c0-17.7-14.3-32-32-32s-32 14.3-32 32l0 64-64 0c-17.7 0-32 14.3-32 32s14.3 32 32 32l96 0c17.7 0 32-14.3 32-32l0-96zM32 320c-17.7 0-32 14.3-32 32s14.3 32 32 32l64 0 0 64c0 17.7 14.3 32 32 32s32-14.3 32-32l0-96c0-17.7-14.3-32-32-32l-96 0zM352 64c0-17.7-14.3-32-32-32s-32 14.3-32 32l0 96c0 17.7 14.3 32 32 32l96 0c17.7 0 32-14.3 32-32s-14.3-32-32-32l-64 0 0-64zM320 320c-17.7 0-32 14.3-32 32l0 96c0 17.7 14.3 32 32 32s32-14.3 32-32l0-64 64 0c17.7 0 32-14.3 32-32s-14.3-32-32-32l-96 0z"
    })

    min_svg.append(min_path)
    min.append(min_svg)

    nav.append(reset)
    if config.get("full_screen",False)==True:
        nav.append(max)
        nav.append(min)

    panzoom_box.append(nav)

    return panzoom_box

def create_css_link(soup,page):
    href= utils.get_relative_url(utils.normalize_url("assets/stylesheets/panzoom.css"),page.url)
    return soup.new_tag("link", rel="stylesheet", href=href)

def create_js_script(soup,page):
    src= utils.get_relative_url(utils.normalize_url("assets/javascripts/panzoom.min.js"),page.url)
    return soup.new_tag("script", src=src)

def create_js_script_plugin(soup,page):
    src= utils.get_relative_url(utils.normalize_url("assets/javascripts/zoompan.js"),page.url)
    return soup.new_tag("script", src=src)
