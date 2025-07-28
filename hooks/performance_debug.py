"""MkDocs hook for performance debugging

The idea behind it is to provide a minimal curated performance log for a `mkdocs build` run.
Of course anyone can use a proper profiler, but the output often contains a lot of non-critical data
that the user has to first filter to get a clearer picture. This hook takes care of this and allows
to quickly see where a bottleneck is occurring. It also has a lower overhead than a proper profiler.

It creates a file in the current working directory, it can be configured easily with variables set
at the bottom of the file. There are also the timing categories included.

It was written using:
- MkDocs==1.6.0
- Jinja2==3.1.3
- Markdown==3.6
The hook will be invalidated if any module modifies the originals for the replaced custom functions.

Example comparison link with tags: https://github.com/mkdocs/mkdocs/compare/1.5.3...1.6.0

TODO:
- Improve summary (display more useful information like avg/median time for template processing).
- Support multi-instance plugins (id() memory unique instances).
- Reconsider the output of FSM mode as it creates 4 entries for templates that only run once, like
  404.html which adds noise to the output, but maybe it's not an issue.

MIT Licence Copyright (c) Kamil Krzyśków (HRY)
"""

import inspect
import logging
import sys
import time
from pathlib import Path
from typing import Callable, Literal, Sequence
from urllib.parse import urljoin

try:
    import jinja2
    import markdown
    import mkdocs
    import yaml
    from mkdocs import plugins, utils
    from mkdocs.commands.build import (
        _build_extra_template,
        _build_theme_template,
        get_context,
        log,
        site_directory_contains_stale_files,
    )
    from mkdocs.config.defaults import MkDocsConfig
    from mkdocs.exceptions import Abort, BuildError
    from mkdocs.livereload import LiveReloadServer
    from mkdocs.structure.files import File, Files, InclusionLevel, get_files, set_exclusions
    from mkdocs.structure.nav import Navigation, get_navigation
    from mkdocs.structure.pages import (
        _ExtractAnchorsTreeprocessor,
        _ExtractTitleTreeprocessor,
        _RawHTMLPreprocessor,
        _RelativePathTreeprocessor,
    )
    from mkdocs.structure.toc import get_toc
except ImportError as e:
    if __name__ != "__main__":
        sys.exit(f"{__name__}\n- {e}")


def main():
    module_compatible = {
        "mkdocs": "1.6.0",
        "jinja2": "3.1.3",
        "markdown": "3.6",
    }
    """Dict with last compatible version of each extended module. Those are also tags on GitHub."""

    print("You're running the Performance Debugger in __main__ mode.")
    print("This mode is intended only to compare functions between versions.")
    print("Last compatible versions are set to:")

    for module, compatible in module_compatible.items():
        print(f"- {module}, {compatible=}")

    choice = input("Would you like to compare the versions with the latest available? [Yes]: ")

    if not choice.lower().startswith(("y", "t", "1")) and choice.strip():
        print("Exiting...")
        sys.exit()

    import requests

    module_latest = {}
    """Dict to store the latest module versions"""

    module_urls = {
        "mkdocs": "https://github.com/mkdocs/mkdocs/raw/{version}/{path}",
        "jinja2": "https://github.com/pallets/jinja/raw/{version}/src/{path}",
        "markdown": "https://github.com/Python-Markdown/markdown/raw/{version}/{path}",
    }
    """Dict with formatted urls to the repository of each extended module"""

    for module, url in module_urls.items():
        print(f"Fetching latest {module} version...", end=" ")
        url = url.split("raw")[0] + "releases/latest"
        response = requests.get(url, allow_redirects=False)
        latest = response.headers.get("location").rsplit("/", 1)[-1]
        module_latest[module] = latest
        print(latest)
        time.sleep(0.1)

    paths_with_functions = {
        "mkdocs/commands/build.py": "def build(",
        "mkdocs/plugins.py": "def run_event(",
        "mkdocs/structure/pages.py": "def render(",
        "markdown/core.py": "def convert(",
        "jinja2/environment.py": "def get_template(",
    }
    """Dict of relative paths to the files containing the extended function definitions"""

    def fetch_function_in_file(file_url, func_def) -> str:
        print(f"Fetching {file_url}...")
        file_response = requests.get(file_url, allow_redirects=True)
        content = file_response.content.decode("utf-8")
        time.sleep(0.1)
        prev_line = ""
        inside_function = False
        definition_depth = -1
        func_lines = []
        for line in content.split("\n"):
            if inside_function:
                if "def " in line:
                    if definition_depth == (len(line) - len(line.lstrip())):
                        break
                func_lines.append(line)
            if not inside_function and func_def in prev_line and "..." not in line:
                inside_function = True
                definition_depth = len(prev_line) - len(prev_line.lstrip())
                func_lines.append(prev_line)
                func_lines.append(line)
            prev_line = line
        return "\n".join(func_lines)

    for module, url in module_urls.items():
        pairs = filter(lambda obj: obj[0].startswith(module), paths_with_functions.items())
        old_version = module_compatible[module]
        new_version = module_latest[module]
        if old_version == new_version:
            print(f"No need to compare {module} as the compatible and latest version are the same")
            continue
        for path, func in pairs:
            old_url = url.format(version=old_version, path=path)
            new_url = url.format(version=new_version, path=path)
            old_func_body = fetch_function_in_file(old_url, func)
            new_func_body = fetch_function_in_file(new_url, func)
            if new_func_body != old_func_body:
                print(f"{func} in {path} differ between {old_version} and {new_version}.")
                print(f"Best to sync them to avoid errors: ", end="")
                print(
                    f"{module_urls[module].split('raw')[0]+'compare'}/{old_version}...{new_version}"
                )
            else:
                print(f"{func} in {path} match in all versions.")

    sys.exit()


if __name__ == "__main__":
    main()


def process_output():

    round_to: int = len(str(TIME_THRESHOLD).split(".")[-1]) + 1

    def endswith_filter(ending: str):
        def entry_filter(entry_obj: tuple[str, float]):
            return entry_obj[0].endswith(ending) and (
                not OMIT_WHEN_THRESHOLD_NOT_REACHED or not entry_obj[1] < TIME_THRESHOLD
            )

        return entry_filter

    summary = {}
    for category, times in ALL.items():

        if category not in summary:
            summary[category] = {}

        handle = summary[category]

        is_acc = False
        filtered_first = None
        filtered_min = None
        filtered_max = None
        filtered_sum = None
        filtered_last = None
        for entry in times:
            # fsm mode
            if entry.endswith("|sum"):
                filtered_first = list(filter(endswith_filter("|first"), times.items()))
                filtered_min = list(filter(endswith_filter("|min"), times.items()))
                filtered_max = list(filter(endswith_filter("|max"), times.items()))
                filtered_sum = list(filter(endswith_filter("|sum"), times.items()))
                break
            # fl mode
            if entry.endswith("|last"):
                filtered_first = filter(endswith_filter("|first"), times.items())
                filtered_last = filter(endswith_filter("|last"), times.items())
                break
        else:
            is_acc = True

        if is_acc:
            handle["total_time"] = round(sum(times.values()), round_to)
            continue

        if filtered_last:
            first_values = map(lambda x: x[1], filtered_first)
            last_values = map(lambda x: x[1], filtered_last)
            handle["total_first"] = round(sum(first_values), round_to)
            handle["total_last"] = round(sum(last_values), round_to)

        if filtered_sum:
            handle["min_of_first"] = min(filtered_first, key=lambda x: x[1])
            handle["max_of_first"] = max(filtered_first, key=lambda x: x[1])
            handle["min_of_min"] = min(filtered_min, key=lambda x: x[1])
            handle["max_of_min"] = max(filtered_min, key=lambda x: x[1])
            handle["min_of_max"] = min(filtered_max, key=lambda x: x[1])
            handle["max_of_max"] = max(filtered_max, key=lambda x: x[1])
            handle["min_of_sum"] = min(filtered_sum, key=lambda x: x[1])
            handle["max_of_sum"] = max(filtered_sum, key=lambda x: x[1])
            for key, value in handle.items():
                handle[key] = {"template": value[0], "time": round(value[1], round_to)}

    # Delete categories omitted by inclusion
    if INCLUDED_CATEGORIES:
        for obj in (summary, ALL, COUNT):
            for category in list(obj):
                if category not in INCLUDED_CATEGORIES:
                    del obj[category]

    # Delete categories omitted by exclusion
    for category in OMITTED_CATEGORIES:
        for obj in (summary, ALL, COUNT):
            try:
                del obj[category]
            except KeyError:
                pass

    # Delete omitted entries and sort values from high to low
    for obj in (ALL, COUNT):
        if obj is ALL:
            filter_threshold = TIME_THRESHOLD
        elif obj is COUNT:
            filter_threshold = COUNT_THRESHOLD
        else:
            raise NotImplementedError
        for category, times in obj.items():
            for entry, value in list(times.items()):
                if OMIT_WHEN_THRESHOLD_NOT_REACHED and value < filter_threshold:
                    del times[entry]
                    continue
                times[entry] = round(value, round_to)
            obj[category] = {
                k: v for k, v in sorted(times.items(), key=lambda x: x[1], reverse=True)
            }

    output = [summary, ALL, COUNT]
    output_settings = {"allow_unicode": True, "indent": 2, "sort_keys": False}

    if SERIALIZE_TIMES_TO_FILE:
        with open(FILE_PATH, "w", encoding="utf8") as file:
            yaml.dump(output, file, **output_settings)
        return

    print()
    print(yaml.dump(output, stream=None, **output_settings))


def custom_run_event(self, name: str, item=None, **kwargs):
    """This function runs in a loop so each time assignment should accumulate previous ones."""

    with Timer(CAT_EVENT, name=f"on_{name}"):
        pass_item = item is not None
        for method in self.events[name]:
            self._current_plugin = self._event_origins.get(method, "<unknown>")
            if log.getEffectiveLevel() <= logging.DEBUG:
                log.debug(f"Running `{name}` event from plugin '{self._current_plugin}'")
            if hasattr(method, "__self__"):
                cls = method.__self__.__class__
                plugin_name = f"{cls.__module__}.{cls.__name__}"
            else:
                plugin_name = "/".join(Path(inspect.getfile(method)).as_posix().split("/")[-2:])
            event_plugin_name = f"on_{name}|{plugin_name}"
            with Timer(CAT_PLUGIN, name=plugin_name), Timer(
                CAT_PLUGIN_EVENT, name=event_plugin_name
            ):
                if pass_item:
                    result = method(item, **kwargs)
                else:
                    result = method(**kwargs)
                # keep item if method returned `None`
                if result is not None:
                    item = result

    if name == "shutdown":
        process_output()

    return item


def custom_build(
    config: MkDocsConfig, *, serve_url: str | None = None, dirty: bool = False
) -> None:
    """Perform a full site build."""

    logger = logging.getLogger("mkdocs")

    # Add CountHandler for strict mode
    warning_counter = utils.CountHandler()
    warning_counter.setLevel(logging.WARNING)
    if config.strict:
        logging.getLogger("mkdocs").addHandler(warning_counter)

    inclusion = InclusionLevel.is_in_serve if serve_url else InclusionLevel.is_included

    try:
        start = time.monotonic()

        # Run `config` plugin events.
        with Timer(CAT_BUILD, name="on_config"):
            config = config.plugins.on_config(config)

        # Run `pre_build` plugin events.
        with Timer(CAT_BUILD, name="on_pre_build"):
            config.plugins.on_pre_build(config=config)

        if not dirty:
            log.info("Cleaning site directory")
            utils.clean_directory(config.site_dir)
        else:  # pragma: no cover
            # Warn user about problems that may occur with --dirty option
            log.warning(
                "A 'dirty' build is being performed, this will likely lead to inaccurate navigation and other"
                " links within your site. This option is designed for site development purposes only."
            )

        if not serve_url:  # pragma: no cover
            log.info(f"Building documentation to directory: {config.site_dir}")
            if dirty and site_directory_contains_stale_files(config.site_dir):
                log.info("The directory contains stale files. Use --clean to remove them.")

        # First gather all data from all files/pages to ensure all data is consistent across all pages.

        with Timer(CAT_BUILD, name="get_files"):
            files = get_files(config)
            env = config.theme.get_env()
            files.add_files_from_theme(env, config)

        # Run `files` plugin events.
        with Timer(CAT_BUILD, name="on_files"):
            files = config.plugins.on_files(files, config=config)

        # If plugins have added files but haven't set their inclusion level, calculate it again.
        set_exclusions(files, config)

        with Timer(CAT_BUILD, name="get_navigation"):
            nav = get_navigation(files, config)

        # Run `nav` plugin events.
        with Timer(CAT_BUILD, name="on_nav"):
            nav = config.plugins.on_nav(nav, config=config, files=files)

        log.debug("Reading markdown pages.")
        excluded = []
        with Timer(CAT_BUILD, name="populate_pages"):
            for file in files.documentation_pages(inclusion=inclusion):
                log.debug(f"Reading: {file.src_uri}")
                with Timer(CAT_PAGE_POPULATION, name="create_page"):
                    if file.page is None and file.inclusion.is_not_in_nav():
                        if serve_url and file.inclusion.is_excluded():
                            excluded.append(urljoin(serve_url, file.url))
                        mkdocs.structure.pages.Page(None, file, config)
                assert file.page is not None
                with Timer(CAT_POPULATED_PAGES, name=file.src_uri):
                    custom_populate_page(file.page, config, files, dirty)
        if excluded:
            log.info(
                "The following pages are being built only for the preview "
                "but will be excluded from `mkdocs build` per `draft_docs` config:\n - "
                + "\n  - ".join(excluded)
            )

        # Run `env` plugin events.
        with Timer(CAT_BUILD, name="on_env"):
            env = config.plugins.on_env(env, config=config, files=files)

        # Start writing files to site_dir now that all data is gathered. Note that order matters. Files
        # with lower precedence get written first so that files with higher precedence can overwrite them.

        log.debug("Copying static assets.")
        with Timer(CAT_BUILD, name="copy_static_files"):
            files.copy_static_files(dirty=dirty, inclusion=inclusion)

        with Timer(CAT_BUILD, name="build_theme_templates"):
            for template in config.theme.static_templates:
                _build_theme_template(template, env, files, config, nav)

        with Timer(CAT_BUILD, name="build_extra_templates"):
            for template in config.extra_templates:
                _build_extra_template(template, files, config, nav)

        log.debug("Building markdown pages.")
        with Timer(CAT_BUILD, name="build_pages"):
            doc_files = files.documentation_pages(inclusion=inclusion)
            for file in doc_files:
                assert file.page is not None
                with Timer(CAT_BUILT_PAGES, name=file.src_uri):
                    custom_build_page(
                        file.page,
                        config,
                        doc_files,
                        nav,
                        env,
                        dirty,
                        excluded=file.inclusion.is_excluded(),
                    )

        with Timer(CAT_BUILD, name="validate_anchor_links"):
            log_level = config.validation.links.anchors
            for file in doc_files:
                assert file.page is not None
                file.page.validate_anchor_links(files=files, log_level=log_level)

        # Run `post_build` plugin events.
        with Timer(CAT_BUILD, name="on_post_build"):
            config.plugins.on_post_build(config=config)

        if counts := warning_counter.get_counts():
            msg = ", ".join(f"{v} {k.lower()}s" for k, v in counts)
            raise Abort(f"Aborted with {msg} in strict mode!")

        log.info(f"Documentation built in {time.monotonic() - start:.2f} seconds")

    except Exception as e:
        # Run `build_error` plugin events.
        config.plugins.on_build_error(error=e)
        if isinstance(e, BuildError):
            log.error(str(e))
            raise Abort("Aborted with a BuildError!")
        raise

    finally:
        logger.removeHandler(warning_counter)


def custom_populate_page(
    page: mkdocs.structure.pages.Page, config: MkDocsConfig, files: Files, dirty: bool = False
) -> None:
    """This function runs in a loop so each time assignment should accumulate previous ones."""

    config._current_page = page
    try:
        # When --dirty is used, only read the page if the file has been modified since the
        # previous build of the output.
        if dirty and not page.file.is_modified():
            return

        # Run the `pre_page` plugin event
        with Timer(CAT_PAGE_POPULATION, name="on_pre_page"):
            page = config.plugins.on_pre_page(page, config=config, files=files)

        with Timer(CAT_PAGE_POPULATION, name="read_source"):
            page.read_source(config)

        assert page.markdown is not None

        # Run `page_markdown` plugin events.
        with Timer(CAT_PAGE_POPULATION, name="on_page_markdown"):
            page.markdown = config.plugins.on_page_markdown(
                page.markdown, page=page, config=config, files=files
            )

        with Timer(CAT_PAGE_POPULATION, name="render"):
            page.render(config, files)

        assert page.content is not None

        # Run `page_content` plugin events.
        with Timer(CAT_PAGE_POPULATION, name="on_page_content"):
            page.content = config.plugins.on_page_content(
                page.content, page=page, config=config, files=files
            )
    except Exception as e:
        message = f"Error reading page '{page.file.src_uri}':"
        # Prevent duplicated the error message because it will be printed immediately afterwards.
        if not isinstance(e, BuildError):
            message += f" {e}"
        log.error(message)
        raise
    finally:
        config._current_page = None


def custom_page_render(self, config: MkDocsConfig, files: Files) -> None:
    """This function runs in a loop so each time assignment should accumulate previous ones."""

    if self.markdown is None:
        raise RuntimeError("`markdown` field hasn't been set (via `read_source`)")

    with Timer(CAT_PAGE_RENDERING, name="create_markdown"):
        md = markdown.Markdown(
            extensions=config["markdown_extensions"], extension_configs=config["mdx_configs"] or {}
        )

        raw_html_ext = _RawHTMLPreprocessor()
        raw_html_ext._register(md)

        extract_anchors_ext = _ExtractAnchorsTreeprocessor(self.file, files, config)
        extract_anchors_ext._register(md)

        relative_path_ext = _RelativePathTreeprocessor(self.file, files, config)
        relative_path_ext._register(md)

        extract_title_ext = _ExtractTitleTreeprocessor()
        extract_title_ext._register(md)

    with Timer(CAT_PAGE_RENDERING, name="convert_markdown"):
        self.content = md.convert(self.markdown)

    with Timer(CAT_PAGE_RENDERING, name="get_toc"):
        self.toc = get_toc(getattr(md, "toc_tokens", []))

    self._title_from_render = extract_title_ext.title
    self.present_anchor_ids = (
        extract_anchors_ext.present_anchor_ids | raw_html_ext.present_anchor_ids
    )
    if log.getEffectiveLevel() > logging.DEBUG:
        self.links_to_anchors = relative_path_ext.links_to_anchors


def custom_markdown_convert(self, source: str) -> str:
    """This function runs in a loop so each time assignment should accumulate previous ones."""

    # Fix up the source text
    if not source.strip():
        return ""  # a blank Unicode string

    try:
        source = str(source)
    except UnicodeDecodeError as e:  # pragma: no cover
        # Customize error message while maintaining original traceback
        e.reason += ". -- Note: Markdown only accepts Unicode input!"
        raise

    # Split into lines and run the line preprocessors.
    with Timer(CAT_MARKDOWN_CONVERT, name="preprocessors"):
        self.lines = source.split("\n")
        for prep in self.preprocessors:
            cls = prep.__class__
            module_name = cls.__module__
            class_name = f"{module_name}.{cls.__name__}"
            with Timer(CAT_MD_MODULE, name=module_name), Timer(CAT_MD_CLASS, name=class_name):
                self.lines = prep.run(self.lines)

    # Parse the high-level elements.
    with Timer(CAT_MARKDOWN_CONVERT, name="parser"):
        root = self.parser.parseDocument(self.lines).getroot()

    # Run the tree-processors
    with Timer(CAT_MARKDOWN_CONVERT, name="tree_processors"):
        for treeprocessor in self.treeprocessors:
            cls = treeprocessor.__class__
            module_name = cls.__module__
            class_name = f"{module_name}.{cls.__name__}"
            with Timer(CAT_MD_MODULE, name=module_name), Timer(CAT_MD_CLASS, name=class_name):
                new_root = treeprocessor.run(root)
                if new_root is not None:
                    root = new_root

    # Serialize _properly_.  Strip top-level tags.
    with Timer(CAT_MARKDOWN_CONVERT, name="serializer"):
        output = self.serializer(root)
        if self.stripTopLevelTags:
            try:
                start = output.index("<%s>" % self.doc_tag) + len(self.doc_tag) + 2
                end = output.rindex("</%s>" % self.doc_tag)
                output = output[start:end].strip()
            except ValueError as e:  # pragma: no cover
                if output.strip().endswith("<%s />" % self.doc_tag):
                    # We have an empty document
                    output = ""
                else:
                    # We have a serious problem
                    raise ValueError(
                        "Markdown failed to strip top-level " "tags. Document=%r" % output.strip()
                    ) from e

    # Run the text post-processors
    with Timer(CAT_MARKDOWN_CONVERT, name="postprocessors"):
        for pp in self.postprocessors:
            cls = pp.__class__
            module_name = cls.__module__
            class_name = f"{module_name}.{cls.__name__}"
            with Timer(CAT_MD_MODULE, name=module_name), Timer(CAT_MD_CLASS, name=class_name):
                output = pp.run(output)

    return output.strip()


def custom_build_page(
    page: mkdocs.structure.pages.Page,
    config: MkDocsConfig,
    doc_files: Sequence[File],
    nav: Navigation,
    env: jinja2.Environment,
    dirty: bool = False,
    excluded: bool = False,
) -> None:
    """This function runs in a loop so each time assignment should accumulate previous ones."""

    config._current_page = page
    try:
        # When --dirty is used, only build the page if the file has been modified since the
        # previous build of the output.
        if dirty and not page.file.is_modified():
            return

        log.debug(f"Building page {page.file.src_uri}")

        # Activate page. Signals to theme that this is the current page.
        page.active = True

        with Timer(CAT_PAGE_BUILDING, name="get_context"):
            context = get_context(nav, doc_files, config, page)

        # Allow 'template:' override in md source files.
        with Timer(CAT_PAGE_BUILDING, name="get_template"):
            template = env.get_template(page.meta.get("template", "main.html"))

        # Run `page_context` plugin events.
        with Timer(CAT_PAGE_BUILDING, name="on_page_context"):
            context = config.plugins.on_page_context(context, page=page, config=config, nav=nav)

        with Timer(CAT_PAGE_BUILDING, name="draft_marker"):
            if excluded:
                page.content = (
                    '<div class="mkdocs-draft-marker" '
                    'title="This page will not be included into the built site.">'
                    "DRAFT"
                    "</div>" + (page.content or "")
                )

        # Render the template.
        with Timer(CAT_PAGE_BUILDING, name="render_template"):
            output = template.render(context)

        # Run `post_page` plugin events.
        with Timer(CAT_PAGE_BUILDING, name="on_post_page"):
            output = config.plugins.on_post_page(output, page=page, config=config)

        # Write the output file.
        with Timer(CAT_PAGE_BUILDING, name="write_file"):
            if output.strip():
                utils.write_file(
                    output.encode("utf-8", errors="xmlcharrefreplace"), page.file.abs_dest_path
                )
            else:
                log.info(f"Page skipped: '{page.file.src_uri}'. Generated empty output.")
    except Exception as e:
        message = f"Error building page '{page.file.src_uri}':"
        # Prevent duplicated the error message because it will be printed immediately afterwards.
        if not isinstance(e, BuildError):
            message += f" {e}"
        log.error(message)
        raise
    finally:
        # Deactivate page
        page.active = False
        config._current_page = None


@jinja2.utils.internalcode
def custom_get_template(self, name, parent=None, globals=None) -> jinja2.Template:

    with Timer(CAT_TEMPLATE_LOAD, name=name, mode="fl"):
        if isinstance(name, jinja2.Template):
            result = name
        else:
            if parent is not None:
                name = self.join_path(name, parent)
            result = self._load_template(name, globals)

    result.root_render_func = template_root_wrapper(result.root_render_func, result.name)

    return result


def template_root_wrapper(func: Callable, name):

    if func.__name__ == "wrapper":
        return func

    def wrapper(*args, **kwargs):
        with Timer(CAT_TEMPLATE_ROOT, name=name, mode="fsm"):
            yield from func(*args, **kwargs)

    return wrapper


@plugins.event_priority(100)
def on_startup(*, command: Literal["build", "gh-deploy", "serve"], **__) -> None:

    if command != "build":
        return

    global MODIFIED_INTERNALS

    if MODIFIED_INTERNALS is False:
        # Reminder comment to put the functions also in main() for comparison
        mkdocs.commands.build.build = custom_build
        mkdocs.plugins.PluginCollection.run_event = custom_run_event
        mkdocs.structure.pages.Page.render = custom_page_render
        markdown.Markdown.convert = custom_markdown_convert
        jinja2.environment.Environment.get_template = custom_get_template
        MODIFIED_INTERNALS = True


class Timer:
    """
    Adapted from:
    https://stackoverflow.com/questions/33987060/python-context-manager-that-measures-time
    """

    accepted_modes: list[str] = [
        "acc",  # Accumulate
        "fl",  # First & Last (used when caching is involved)
        "fsm",  # First & Sum (including First) & MinMax (used when there is huge variability)
    ]

    def __init__(self, category: str, *, name: str = "", mode: str = "acc") -> None:
        self.category: str = category
        self.name: str = name
        if mode in self.accepted_modes:
            self.mode: str = mode
        else:
            raise NotImplementedError(f"Unknown mode '{mode}'")

    def __enter__(self):
        category = COUNT.get(self.category)
        if category is None:
            category = COUNT[self.category] = {}
        category[self.name] = category.get(self.name, 0) + 1
        self.start: float = time.perf_counter()
        return self

    def __exit__(self, *_, **__):
        passed = time.perf_counter() - self.start

        handle = ALL.get(self.category)

        if handle is None:
            handle = ALL[self.category] = {}

        if self.mode == "acc":
            handle[self.name] = handle.get(self.name, 0) + passed
            return

        first = f"{self.name}|first"
        last = f"{self.name}|last"
        sum_ = f"{self.name}|sum"
        min_ = f"{self.name}|min"
        max_ = f"{self.name}|max"

        first_entry = handle.get(first)
        if first_entry is None:
            first_entry = handle[first] = passed

        if self.mode == "fl":
            handle[last] = passed
        elif self.mode == "fsm":
            handle[sum_] = handle.get(sum_, first_entry) + passed
            min_entry = handle.get(min_)
            if min_entry is None or min_entry > passed:
                handle[min_] = passed
            max_entry = handle.get(max_)
            if max_entry is None or max_entry < passed:
                handle[max_] = passed


# CATEGORIES ---------------------------------------------------------------------------------------
CAT_BUILD: str = "WHOLE_BUILD"
"""Most general, should include all below"""

CAT_PAGE_POPULATION: str = "BUILD_POPULATION_STAGE"
"""Accumulates the times related to the page population (includes Markdown)"""

CAT_PAGE_RENDERING: str = "BUILD_RENDERING_STAGE"
"""Accumulates the times related to the page rendering (includes Markdown)"""

CAT_MARKDOWN_CONVERT: str = "BUILD_MARKDOWN_STAGE"
"""Accumulates the times related to the markdown conversion"""

CAT_PAGE_BUILDING: str = "BUILD_MERGE_STAGE"
"""Accumulates the times related to the page building (includes Jinja2 templates)"""

CAT_POPULATED_PAGES: str = "POPULATED_PAGES"
"""Accumulates the times for all populated pages, the src_uri is stored"""

CAT_BUILT_PAGES: str = "BUILT_PAGES"
"""Accumulates the times for all built pages, the src_uri is stored"""

CAT_EVENT: str = "ALL_EVENTS"
"""Accumulates all event times"""

CAT_PLUGIN_EVENT: str = "PLUGINS_PER_EVENTS"
"""Accumulates all event times per plugin"""

CAT_PLUGIN: str = "PLUGINS_PER_NAMES"
"""Accumulates all plugin times"""

CAT_MD_MODULE: str = "MARKDOWN_PER_MODULES"
"""Accumulates Markdown processing time per module"""

CAT_MD_CLASS: str = "MARKDOWN_PER_CLASSES"
"""Accumulates Markdown processing time per class"""

CAT_TEMPLATE_LOAD: str = "LOADED_TEMPLATES"
"""Saves first, and the last time for loading a template"""

CAT_TEMPLATE_ROOT: str = "TEMPLATE_ROOTS"
"""
Saves first, and the sum of all times in processing the root template function.
Includes load times for child templates as well, so keep that in mind.
"""

# MODIFIED INTERNALLY ------------------------------------------------------------------------------

MODIFIED_INTERNALS: bool = False
"""Sanity flag for the instance this hook is run in serve mode"""

ALL: dict[str, dict[str, float]] = {}
"""A global dict to store all times"""

COUNT: dict[str, dict[str, int]] = {}
"""A global dict to store the amount of times a category->step invoked a Timer"""

# MODIFIED BY THE USER -----------------------------------------------------------------------------

SERIALIZE_TIMES_TO_FILE: bool = True
"""Instead of printing to Terminal save file"""

FILE_PATH: str = "performance_debug.yml"
"""File path relative to current working directory"""

TIME_THRESHOLD: float = 0.0001
"""Minimal time value to be shown in the output (affects output rounding)"""

COUNT_THRESHOLD: int = 2
"""Minimal count value to be shown in the output"""

OMIT_WHEN_THRESHOLD_NOT_REACHED: bool = True
"""Only affects the displayed entries at the end, they will be not shown, but will be summed up"""

INCLUDED_CATEGORIES: set[str] = set()
"""Limit the output to these categories, other categories will still be summed up"""

OMITTED_CATEGORIES: set[str] = set()
"""Categories that will be not shown in the output, they will still be summed up"""
