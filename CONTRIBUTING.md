# Contributing to mkdocs-panzoom

Welcome! This document provides comprehensive guidelines for contributing to the mkdocs-panzoom project.

## 🚀 Quick Start

The fastest way to get started:

```bash
git clone https://github.com/elgalu/mkdocs-panzoom.git
cd mkdocs-panzoom
make setup
source .venv/bin/activate
make check
```

## 📋 Prerequisites

- **Python 3.10+** (check [.python-version](./.python-version) for the exact version)
- **uv** package manager - [Installation guide](https://docs.astral.sh/uv/getting-started/installation/)
- **Git** for version control
- **make** for running commands

## 🛠️ Development Setup

### Option 1: Automated Setup (Recommended)

```bash
make setup
source .venv/bin/activate
```

This will:

- Install `uv` if not present
- Install `pre-commit` as a global tool
- Create a virtual environment with the correct Python version
- Install all dependencies (including dev dependencies)
- Set up pre-commit hooks

### Option 2: Manual Setup

If the automated setup doesn't work, follow these steps:

1. **Install uv**:

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Install pre-commit globally**:

   ```bash
   uv tool install pre-commit
   ```

3. **Create virtual environment**:

   ```bash
   uv venv --python $(cat .python-version) .venv
   ```

4. **Activate virtual environment**:

   ```bash
   source .venv/bin/activate  # Linux/macOS
   # or
   .venv\Scripts\activate     # Windows
   ```

5. **Install dependencies**:

   ```bash
   uv sync --locked  # Installs exact versions from uv.lock
   ```

6. **Install pre-commit hooks**:

   ```bash
   pre-commit install
   ```

7. **Verify setup**:

   ```bash
   make check
   ```

## 🔍 Development Workflow

### Before Making Changes

1. **Create a feature branch**:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Verify environment**:

   ```bash
   make env  # Shows environment information
   ```

### During Development

1. **Run quality checks**:

   ```bash
   make check          # Run all pre-commit hooks
   make check tests    # Run hooks + full test suite
   ```

2. **Run tests specifically**:

   ```bash
   uv run pytest                    # Run all tests
   uv run pytest tests/test_plugin.py  # Run specific test file
   uv run pytest -v                 # Verbose output
   uv run pytest --cov              # With coverage report
   ```

3. **Work on documentation**:

   ```bash
   make serve    # Start live-reload docs server at http://127.0.0.1:8000
   make build    # Build static documentation
   ```

### Code Quality Standards

This project enforces high code quality standards:

- **Type hints**: All functions must have type annotations
- **Docstrings**: All public functions and classes must have docstrings
- **Formatting**: Code is auto-formatted with `ruff format`
- **Linting**: Code must pass `ruff` linting checks
- **Testing**: New features should include tests
- **Documentation**: User-facing features need documentation

## 📦 Building and Testing

### Building the Package

1. **Build wheel and source distribution**:

   ```bash
   uv build
   ```

   This creates files in the `dist/` directory:

   + `mkdocs_panzoom_plugin-X.Y.Z-py3-none-any.whl` (wheel)
   + `mkdocs_panzoom_plugin-X.Y.Z.tar.gz` (source distribution)

2. **Build wheel only**:

   ```bash
   uv build --wheel
   ```

3. **Build source distribution only**:

   ```bash
   uv build --sdist
   ```

### Testing the Built Package

1. **Test in a clean environment**:

   ```bash
   # Create a test environment
   uv venv test-env
   source test-env/bin/activate

   # Install the built wheel
   pip install dist/mkdocs_panzoom_plugin-*.whl

   # Test basic functionality
   python -c "from mkdocs_panzoom_plugin.plugin import PanZoomPlugin; print('✅ Import successful')"

   # Cleanup
   deactivate
   rm -rf test-env
   ```

2. **Test with a sample MkDocs project**:

   ```bash
   # Create a test MkDocs project
   mkdir test-mkdocs
   cd test-mkdocs

   # Create basic mkdocs.yml
   cat > mkdocs.yml << EOF
   site_name: Test Site
   plugins:
     - panzoom
   EOF

   # Create sample content
   mkdir docs
   echo "# Test\n![Test](https://via.placeholder.com/800x600)" > docs/index.md

   # Test the plugin
   uv run mkdocs build
   uv run mkdocs serve  # Check at http://127.0.0.1:8000

   # Cleanup
   cd ..
   rm -rf test-mkdocs
   ```

### Local Testing with pip install -e

For development, you can install the package in editable mode:

```bash
# Install in editable mode
pip install -e .

# Now changes to the source code are immediately reflected
# Test your changes without rebuilding
```

## 🚀 Publishing (Maintainers Only)

### Automated Publishing (Recommended)

The project uses GitHub Actions for automated publishing:

1. **Create and push a git tag**:

   ```bash
   # Update version in pyproject.toml first
   git add pyproject.toml
   git commit -m "bump: version 0.2.3"

   # Create and push tag
   git tag v0.2.3
   git push origin main --tags
   ```

2. **GitHub Actions will automatically**:

   + Build the package
   + Run all tests
   + Publish to PyPI (using trusted publishing)
   + Create a GitHub release
   + Sign artifacts with Sigstore

### Manual Publishing (Emergency Only)

If automated publishing fails:

1. **Build the package**:

   ```bash
   uv build
   ```

2. **Check the build**:

   ```bash
   uv run twine check dist/*
   ```

3. **Test upload to TestPyPI**:

   ```bash
   uv run twine upload --repository testpypi dist/*
   ```

4. **Upload to PyPI**:

   ```bash
   uv run twine upload dist/*
   ```

**Note**: Manual publishing requires PyPI API tokens configured in `~/.pypirc`.

## 🧪 Testing Guidelines

### Writing Tests

1. **Test file naming**: `test_*.py` or `*_test.py`
2. **Test function naming**: `test_descriptive_name()`
3. **Use fixtures** for common setup
4. **Test both success and failure cases**

### Running Tests

```bash
# All tests
uv run pytest

# With coverage
uv run pytest --cov=mkdocs_panzoom_plugin --cov-report=html

# Specific test
uv run pytest tests/test_plugin.py::test_plugin_config

# Verbose output
uv run pytest -v -s
```

### Test Coverage

Aim for high test coverage:

- View coverage report: `open htmlcov/index.html`
- Coverage is reported in CI/CD
- New features should include comprehensive tests

## 📚 Documentation Guidelines

### Writing Documentation

1. **User documentation**: Add to `docs/` directory
2. **API documentation**: Use comprehensive docstrings
3. **Examples**: Include practical examples
4. **Screenshots**: Use for UI features

### Building Documentation

```bash
# Development server (live reload)
make serve

# Build static site
make build

# Documentation is built to site/ directory
```

## 🤝 Contribution Process

### Before You Start

1. **Check existing issues**: Look for related work
2. **Create an issue**: For new features or bugs
3. **Discuss your approach**: Get feedback before coding

### Making Changes

1. **Fork and clone** the repository
2. **Create a feature branch** from `main`
3. **Make your changes** following the guidelines
4. **Add tests** for new functionality
5. **Update documentation** if needed
6. **Run quality checks**: `make check tests`

### Submitting Changes

1. **Commit your changes**:

   ```bash
   git add .
   git commit -m "feat: add new zoom feature"
   ```

2. **Push to your fork**:

   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create a Pull Request**:

   + Use a descriptive title
   + Explain what and why
   + Link related issues
   + Include screenshots for UI changes

### Commit Message Format

Use conventional commits:

- `feat:` new features
- `fix:` bug fixes
- `docs:` documentation changes
- `refactor:` code refactoring
- `test:` adding/updating tests
- `chore:` maintenance tasks

## 🛠️ Troubleshooting

### Common Issues

1. **`uv` not found**:

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   source ~/.bashrc  # or restart terminal
   ```

2. **Python version mismatch**:

   ```bash
   uv python install $(cat .python-version)
   uv venv --python $(cat .python-version) .venv
   ```

3. **Pre-commit hooks failing**:

   ```bash
   pre-commit run --all-files  # Fix all files
   pre-commit autoupdate       # Update hook versions
   ```

4. **Permission issues**:

   ```bash
   chmod +x scripts/contributor_setup.sh
   ```

### Getting Help

- **Create an issue**: For bugs or feature requests
- **Start a discussion**: For questions or ideas
- **Check existing docs**: Search the documentation
- **Review code**: Look at similar implementations

## 🧹 Cleanup

Remove development artifacts:

```bash
make clean  # Removes build artifacts, caches, etc.
```

## 🎯 Quality Standards

This project maintains high quality standards:

- ✅ **100% type coverage** with mypy
- ✅ **Comprehensive test suite** with pytest
- ✅ **Code formatting** with ruff
- ✅ **Documentation** for all public APIs
- ✅ **Pre-commit hooks** for quality assurance
- ✅ **Continuous integration** with GitHub Actions

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/elgalu/mkdocs-panzoom/issues)
- **Discussions**: [GitHub Discussions](https://github.com/elgalu/mkdocs-panzoom/discussions)
- **Documentation**: [Project Docs](https://playg0n.github.io/mkdocs-panzoom/)

Thank you for contributing to mkdocs-panzoom! 🎉
