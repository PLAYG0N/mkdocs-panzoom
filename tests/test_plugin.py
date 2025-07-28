"""Test the main plugin functionality."""

from typing import Any

from mkdocs_panzoom_plugin.plugin import PanZoomPlugin


def test_plugin_can_be_imported() -> None:
    """Test that the plugin can be imported."""
    assert PanZoomPlugin is not None


def test_plugin_instantiation() -> None:
    """Test plugin can be instantiated."""
    plugin = PanZoomPlugin()
    assert plugin is not None


def test_plugin_config_scheme() -> None:
    """Test plugin configuration scheme."""
    plugin = PanZoomPlugin()

    # Check that config scheme exists and has expected keys
    config_scheme = dict(plugin.config_scheme)  # type: ignore[attr-defined]

    expected_keys = [
        "mermaid",
        "images",
        "full_screen",
        "always_show_hint",
        "show_zoom_buttons",
        "key",
        "include",
        "exclude",
        "include_selectors",
        "exclude_selectors",
        "hint_location",
        "initial_zoom_level",
        "zoom_step",
        "buttons_size",
    ]

    for key in expected_keys:
        assert key in config_scheme


def test_plugin_on_config() -> None:
    """Test plugin on_config method."""
    plugin = PanZoomPlugin()
    config: dict[str, Any] = {"site_url": "https://example.com", "plugins": []}

    # This should not raise an exception
    result = plugin.on_config(config)  # type: ignore[call-arg]
    assert result is None or isinstance(result, dict)
