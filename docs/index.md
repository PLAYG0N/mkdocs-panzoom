# Home

This plugin makes use of the [panzoom](https://github.com/anvaka/panzoom) library by [Andrei Kashcha](https://github.com/anvaka)

## Setup

`pip install mkdocs-panzoom-plugin`

Add it to your `mkdocs.yaml`:

```yaml
plugins:
  - search
  - panzoom

```

!!! warning

    Make sure to define the `site_url` otherwise it won't work!

    **Example**:

    ```yaml
    site_url: https://playg0n.github.io/mkdocs-panzoom/
    ```

## Usage

Examples and usage are available in the [docs](https://playg0n.github.io/mkdocs-panzoom/).

## Config

### Mermaid

This enables panzoom on mermaid diagrams.

```yaml
plugins:
  - panzoom:
      mermaid: true # default true
```

### Images

This enables panzoom on images.

```yaml
plugins:
  - panzoom:
      images: true # default true
```

### Always show hint

This makes the hint on how to use it permanently visible.

```yaml
plugins:
  - panzoom:
      always_show_hint: true # default false
```

### Exclude Pages

```yaml
plugins:
  - panzoom:
      exclude:
        - Path/to/page.md
```

### Enable Fullscreen

!!! warning

    This is still in development!

```yaml
plugins:
  - panzoom:
      full_screen: True # default False
```

## Credits

The structure and some parts are from the [enumerate-headings-plugin](https://github.com/timvink/mkdocs-enumerate-headings-plugin)
