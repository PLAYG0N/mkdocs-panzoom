# Contributing

## Contributor Setup

Clone the project locally. You may want to git clone using the official [GitHub CLI](https://cli.github.com/)
to avoid issues with SSH keys.

```sh
gh repo clone ...
```

## Contributor Setup - Automated

Simply run `make setup`

Then `source .venv/bin/activate`

## Contributor Setup - Manual

If `make setup` didn't work on your system you can do the setup manually, step by step:

1. Install uv `curl -LsSf https://astral.sh/uv/install.sh | sh`.
1. Ensure pre-commit is installed, or install with: `uv tool install pre-commit`
1. Create a virtual environment with the Python version from [.python-version](./.python-version): `uv venv --python $(cat .python-version) .venv`
1. Activate the virtual environment with `source .venv/bin/activate`
1. Install dependencies with `uv sync --locked` (the `--locked` flag avoids updating uv.lock, similar to CI/CD mode)
1. Run `make check`

## Running all hooks checks locally

Run `make check`

## Running all hooks plus tests

Run `make check tests`

## Working on the docs

Run `make serve`

### How to Docker build locally with Nexus dependencies

In order to run a local Docker build:

1. Set up the [impersonating-proxy](https://github.bus.zalan.do/automata/impersonating-reverse-proxy)
2. Run the following command:

```sh
DOCKER_BUILDKIT=0 docker build . --network nexus --build-arg SKIP_CERTIFICATE_VALIDATION=true
```

## Additional Development Notes

* Always run `make check` before committing changes
* Use `make check tests` to run the full test suite
* The project uses `uv` for dependency management - avoid using pip directly
* Pre-commit hooks are automatically installed and will run on each commit
