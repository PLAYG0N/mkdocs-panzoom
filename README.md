# Panzoom for MkDocs

This plugin makes use of the [panzoom](https://github.com/anvaka/panzoom) ([LICENCE](./mkdocs_panzoom_plugin/panzoom/LICENCE)) library by [Andrei Kashcha](https://github.com/anvaka)

## Setup

`pip install mkdocs-panzoom-plugin`

Add it to your `mkdocs.yml`:

```yml
plugins:
  - search
  - panzoom

```

## Usage

Examples and usage are available in the [docs](https://playg0n.github.io/mkdocs-panzoom/).

## Config

### Mermaid

This enables panzoom on mermaid diagrams.

```yml
plugins:
  mermaid: true # default true
```

### Images

This enables panzoom on images.

```yml
plugins:
  images: true # default true
```
### Exclude Pages

```yml
plugins:
  - panzoom:
      exclude:
        - Path/to/page.md
```

### Enable Fullscreen

!!! warning

    This is still in development!

```yml
plugins:
  - panzoom:
      full_screen: True # default False
```

## Credits

The structure and some parts are from the [enumerate-headings-plugin](https://github.com/timvink/mkdocs-enumerate-headings-plugin) ([LICENCE](./licences/enumerate-headings-plugin))
