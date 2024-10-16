# Panzoom for MkDocs

This plugin makes use of the [panzoom](https://github.com/anvaka/panzoom) ([LICENCE](./mkdocs_panzoom_plugin/panzoom/LICENCE)) library by [Andrei Kashcha](https://github.com/anvaka)

> [Live Demo](https://playg0n.github.io/mkdocs-panzoom/)

## Setup

`pip install mkdocs-panzoom-plugin`

Add it to your `mkdocs.yml`:

```yml
plugins:
  - search
  - panzoom

```

> [!WARNING]
>Make sure to define the `site_url` otherwise it won't work!
>
>**Example**:
>
>```yaml
>site_url: https://playg0n.github.io/mkdocs-panzoom/
>```

## Usage

Examples and usage are available in the [docs](https://playg0n.github.io/mkdocs-panzoom/).

## Config

### Selectors

Mermaid and D2 are included by default, but you can add any arbitrary selector or exclude the default ones.
To enable images add the `img` tag like below.

```yaml
plugins:
  - panzoom:
      include_selectors:
        - .myClass # class in html
        - "#myId" # id in html
        - "img" # tag in html
      exclude_selectors:
        - ".mermaid"
        - ".d2"
```

### Exclude Pages

```yml
plugins:
  - panzoom:
      exclude:
        - Path/to/page.md
```

### Enable Fullscreen

> [!WARNING]
>This is still in development!

```yml
plugins:
  - panzoom:
      full_screen: True # default False
```

## Credits

The structure and some parts are from the [enumerate-headings-plugin](https://github.com/timvink/mkdocs-enumerate-headings-plugin) ([LICENCE](./licences/enumerate-headings-plugin))
