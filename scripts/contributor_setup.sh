#!/usr/bin/env bash
# ==============================================================================
# Development Environment Setup and Contributor Bootstrap Script
# ==============================================================================
#
# PURPOSE:
#   Idempotently validates and installs required development tools for Slurm
#   cluster management project contributors. Ensures consistent development
#   environment across platforms with Python, UV package manager, Git, Docker,
#   and pre-commit hooks for code quality and collaboration.
#
# EXECUTION CONTEXTS:
#   Interactive Usage:
#     - ./contributor_setup.sh
#     - Used by new contributors to set up development environment
#     - Run when updating development dependencies or tools
#
#   Automated Execution:
#     - CI/CD pipeline environment preparation
#     - Container build processes for development images
#     - Automated testing environment setup
#
# DEPENDENCIES:
#   - Bash shell with standard utilities (curl, wget, tar, etc.)
#   - Platform package managers: Homebrew (macOS), apt/dnf (Linux)
#   - Network connectivity: For downloading packages and tools
#   - Administrative privileges: For system package installation
#
# FAILURE SCENARIOS:
#   - Missing package managers → Manual installation required
#   - Network connectivity issues → Tool downloads fail
#   - Permission errors → System package installation blocked
#   - Platform incompatibility → Unsupported OS/architecture
#
# AWS PERMISSIONS:
#   - No AWS permissions required (local development setup only)
#   - Operates entirely on local development environment
#   - No cloud service interactions or API calls
#
# SUPPORTED PLATFORMS:
#   ┌─────────────────────────────────────────────────────────────────┐
#   │                    Platform Compatibility Matrix                │
#   ├─────────────────┬───────────────────────────────────────────────┤
#   │ Linux           │ Ubuntu 24.04+, Debian 12+, CentOS 8+          │
#   │                 │ Package management via apt, dnf, yum           │
#   ├─────────────────┼───────────────────────────────────────────────┤
#   │ macOS           │ macOS Sequoia 15.5+, Apple Silicon + Intel     │
#   │                 │ Package management via Homebrew preferred      │
#   └─────────────────┴───────────────────────────────────────────────┘
#
# TOOLS INSTALLED:
#   - Python 3.11+: Core runtime for project development
#   - UV Package Manager: Fast Python package and project management
#   - Git: Version control with pre-commit hook integration
#   - Docker: Container runtime for testing and development
#   - SSH Client: Required for cluster access and development
#   - Pre-commit: Code quality hooks and formatting enforcement
#   - Linting Tools: mypy, ruff, black for code quality
#
# INTEGRATION POINTS:
#   1. UV Package Management:
#      - Replaces pip for faster dependency resolution
#      - Manages virtual environments and Python versions
#      - Integrates with pyproject.toml for project configuration
#
#   2. Pre-commit Framework:
#      - Automated code formatting and linting before commits
#      - CloudFormation template validation hooks
#      - License header management and consistency checks
#
#   3. Docker Integration:
#      - Local container development and testing
#      - CI/CD pipeline compatibility verification
#      - Cross-platform build and test environment

# Development environment setup script for Slurm cluster project contributors

# set -e: Exit immediately if any command exits with a non-zero status
set -e

# set -o pipefail: Don't mask errors from a command piped into another command
set -o pipefail

# set -x: prints all lines before running debug (debugging)
[ -n "${DEBUG}" ] && set -x

#-----------------------------------#
#--- Platform Support Validation ---#
#-----------------------------------#
## Validate that the script is running on a supported platform
## This prevents repeating the same check throughout the script
function validate_supported_platform() {
    local device
    device=$(uname)

    if [ "$device" != 'Darwin' ] && [ "$device" != 'Linux' ]; then
        printf "❌ ERROR: Unsupported operating system: %s\n" "$device" >&2
        printf "   This script only supports Linux and macOS (Darwin).\n" >&2
        printf "   Please run this script on a supported platform.\n" >&2
        exit 1
    fi
}

# Validate platform before proceeding
validate_supported_platform

#----------------------------#
#--- OSX vs Linux tooling ---#
#----------------------------#
# We need to set this up before the helpers, so they can use the aliases
if [ "$(uname)" == 'Darwin' ]; then
    # Check if GNU coreutils are available, prefer them but fall back to system versions
    if command -v gtee &>/dev/null; then
        export _tee='gtee'
    else
        export _tee='tee'
    fi

    if command -v gcut &>/dev/null; then
        export _cut='gcut'
    else
        export _cut='cut'
    fi

    if command -v gsed &>/dev/null; then
        export _sed='gsed'
    else
        export _sed='sed'
    fi

    if command -v gtail &>/dev/null; then
        export _tail='gtail'
    else
        export _tail='tail'
    fi

    if command -v gdate &>/dev/null; then
        export _date='gdate'
    else
        export _date='date'
    fi

    if command -v gtimeout &>/dev/null; then
        export _timeout='gtimeout'
    else
        export _timeout='timeout'
    fi

    if command -v gawk &>/dev/null; then
        export _awk='gawk'
    else
        export _awk='awk'
    fi
elif [ "$(uname)" == 'Linux' ]; then
    export _tee='tee'
    export _cut='cut'
    export _sed='sed'
    export _tail='tail'
    export _date='date'
    export _timeout='timeout'
    export _awk='awk'
fi

#------------------------#
#--- Helper Functions ---#
#------------------------#
## Output to standard error
function util.log.error() {
    printf "❌ ERROR $(${_date} "${_date_format:-+%H:%M:%S:%N}") %s\n" "$*" >&2
}

## Output a warning to standard output
function util.log.warn() {
    printf "⚠️ WARN $(${_date} "${_date_format:-+%H:%M:%S:%N}") %s\n" "$*" >&2
}

## Output an info standard output
function util.log.info() {
    printf "INFO $(${_date} "${_date_format:-+%H:%M:%S:%N}") %s\n" "$*" >&1
}

## Output a new line break to stdout
function util.log.newline() {
    printf "\n" >&1
}

## Print an error and exit, failing
function util.die() {
    util.log.error "$1"
    # if $2 is defined AND NOT EMPTY, use $2; otherwise, set the exit code to: 150
    errnum=${2-150}
    exit "${errnum}"
}

## Ask for user confirmation before proceeding with an action
function util.ask_confirmation() {
    local message="$1"
    local default_response="${2:-n}"  # Default to 'no' if not specified

    # In CI/CD environments, automatically answer "yes" to avoid blocking
    if is_non_interactive_environment; then
        util.log.info "Non-interactive environment detected, automatically answering 'yes' to: $message"
        return 0
    fi

    printf "%s [y/N]: " "$message"
    read -r response

    # If no response, use default
    if [ -z "$response" ]; then
        response="$default_response"
    fi

    # Convert to lowercase for comparison
    response=$(echo "$response" | tr '[:upper:]' '[:lower:]')

    case "$response" in
        y|yes)
            return 0  # Success - user confirmed
            ;;
        n|no)
            return 1  # Failure - user declined
            ;;
        *)
            util.log.error "Invalid response. Please answer y/yes or n/no."
            util.ask_confirmation "$message" "$default_response"
            ;;
    esac
}

#-------------------------------------#
#--- Ensure OS has core util items ---#
#-------------------------------------#
## Necessary for correct error line logging and awk (nawk vs gawk) implementation on macOS
function ensure_system_helpers() {
    if ! command grep --version 1>/dev/null 2>&1; then
        util.die "❌ it seems grep is not installed, please install it."
    fi

    # Check if the date command supports nanoseconds (for better timestamp precision)
    if ! $_date "+%H:%M:%S:%N" &>/dev/null; then
        if [ "$(uname)" == 'Darwin' ]; then
            util.log.error "❌ Your date command doesn't support nanoseconds. Consider installing GNU coreutils:"
            util.log.error "MacOS: brew install coreutils"
            util.log.error "This will provide gdate, gcut, gsed, and other GNU tools with better compatibility."
            util.log.error "Falling back to seconds precision for timestamps..."

            # Override the date format to use seconds instead of nanoseconds
            export _date_format="+%H:%M:%S"
        else
            util.log.error "❌ Your date command doesn't support nanoseconds."
            export _date_format="+%H:%M:%S"
        fi
    else
        export _date_format="+%H:%M:%S:%N"
    fi

    # Test awk version compatibility
    # On macOS, system awk doesn't support -W version, so we'll use a different approach
    if [ "$(uname)" == 'Darwin' ] && [ "$_awk" = "awk" ]; then
        # Using system awk on macOS, check if it's working with a simple test
        if ! echo "test" | $_awk "{print \$1}" >/dev/null 2>&1; then
            util.log.error "❌ Your awk command is not working properly."
            util.log.error "Consider installing gawk: brew install gawk"
        fi
    elif ! $_awk -W version 1>/dev/null 2>&1; then
        if [ "$(uname)" == 'Darwin' ]; then
            util.log.error "❌ Your awk version might not be fully compatible. Consider installing gawk:"
            util.log.error "MacOS: brew install gawk"
            util.log.error "Continuing with system awk..."
        else
            util.log.error "❌ awk version check failed, but continuing..."
        fi
    fi
}

ensure_system_helpers

#------------------------------------------#
#--- Non-Interactive Environment Helper ---#
#------------------------------------------#
## Detect if the script is running in a non-interactive environment
## This includes CI/CD systems and automated/headless installations
function is_non_interactive_environment() {
    # Check for common CI/CD environment variables
    [ -n "${CI}" ] ||                      # Generic CI flag (used by many CI systems)
    [ -n "${GITHUB_ACTIONS}" ] ||          # GitHub Actions
    [ -n "${GITLAB_CI}" ] ||               # GitLab CI
    [ -n "${JENKINS_URL}" ] ||             # Jenkins
    [ -n "${BAMBOO_BUILD_NUMBER}" ] ||     # Atlassian Bamboo
    [ -n "${TEAMCITY_VERSION}" ] ||        # TeamCity
    [ -n "${TF_BUILD}" ] ||                # Azure DevOps
    [ -n "${CIRCLECI}" ] ||                # CircleCI
    [ -n "${TRAVIS}" ] ||                  # Travis CI
    [ -n "${BUILDKITE}" ] ||               # Buildkite
    [ -n "${DRONE}" ] ||                   # Drone CI
    [ -n "${CODEBUILD_BUILD_ID}" ] ||      # AWS CodeBuild
    [ -n "${BUILD_ID}" ] ||                # Generic build ID (used by various CI systems)
    [ -n "${BUILD_NUMBER}" ] ||            # Generic build number (used by various CI systems)
    # Check for non-interactive package manager environments
    [ "${DEBIAN_FRONTEND}" = "noninteractive" ] ||  # Debian/Ubuntu non-interactive mode
    [ "${NEEDRESTART_MODE}" = "a" ] ||     # Ubuntu automatic restart mode
    [ "${APT_LISTCHANGES_FRONTEND}" = "none" ] ||   # APT non-interactive mode
    [ -n "${TERM}" ] && [ "${TERM}" = "dumb" ]      # Dumb terminal (often used in automated environments)
}

#--------------------------------#
#--- Ensure Homebrew on macOS ---#
#--------------------------------#
## Check if Homebrew is available on macOS
function has_homebrew() {
    command -v brew &>/dev/null
}

## Recommend Homebrew installation on macOS for better package management
function ensure_homebrew_if_macos() {
    if [ "$(uname)" == 'Darwin' ]; then
        if ! has_homebrew; then
            util.log.warn "Homebrew is not installed on macOS."
            util.log.warn "While not strictly required, Homebrew is highly recommended for installing tools on macOS."
            util.log.warn "Install Homebrew by running:"
            util.log.warn "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            util.log.warn "Visit https://brew.sh for more information."
            util.log.warn ""
            util.log.warn "Continuing with alternative installation methods..."
        else
            util.log.info "✅ Homebrew is available: $(brew --version | head -n1)"

            # Suggest installing GNU coreutils for better compatibility
            if ! command -v gdate &>/dev/null; then
                util.log.info "💡 For better compatibility, consider installing GNU coreutils:"
                util.log.info "  brew install coreutils"
                util.log.info "This provides gdate, gcut, gsed, and other GNU tools."
            fi
        fi
    fi
}

ensure_homebrew_if_macos

#-----------#
#--- Git ---#
#-----------#
## Git clone each dependency repo.
function checkout() {
    [ -d "$2" ] || git clone --depth 1 "$1" "$2" || util.die "Failed to git clone $1"
}

## Ensure git client is installed.
function ensure_git() {
    if ! command -v git &>/dev/null; then
        util.die "❌ Git is not installed, can't continue. git command not found in path"
    fi
}

ensure_git

#----------------------#
#--- Git Submodules ---#
#----------------------#
## Ensure git client is installed.
function ensure_git_submodules() {
    if [ -f ".gitmodules" ]; then
        git submodule update --init
    fi
}

ensure_git_submodules

#--------------#
#--- Docker ---#
#--------------#
## Ensure docker client is installed and that doesn't require sudo.
function ensure_runtime() {
    if command -v docker --version 1>/dev/null; then
        runtime=docker
        util.log.info "✅ Using Docker as container runtime"
    elif command -v podman &>/dev/null; then
        runtime=podman
        util.log.info "✅ Using Podman as container runtime"
    else
        util.log.error "❌ No container runtime is installed, please install one first."
        if [ "$(uname)" == 'Darwin' ]; then
            util.log.error "  macOS: brew install colima && brew install docker (recommended)"
            util.log.error "  Alternative: brew install --cask docker"
            util.log.error "  Or: brew install podman"
        else
            util.log.error "  Linux: sudo apt install docker.io (Ubuntu/Debian)"
            util.log.error "  Or: sudo apt install podman"
        fi
        exit 30
    fi

    if [ "$runtime" == "docker" ] && (! docker ps --last=1 1>/dev/null 2>&1); then
        util.log.error "❌ Docker is installed but it requires sudo or is not running."
        if [ "$(uname)" == 'Darwin' ]; then
            util.log.error "If using Colima, start it with: colima start"
            util.log.error "If using Docker Desktop, make sure it's running."
        else
            util.log.error "Fix this by adding your user to the docker group:"
            util.log.error "  sudo usermod -aG docker \$USER"
            util.log.error "  newgrp docker"
            util.log.error "Or start the Docker service:"
            util.log.error "  sudo systemctl start docker"
        fi
        exit 31
    fi
}

ensure_runtime

#------------------------------------#
#--- SSH client and other tooling ---#
#------------------------------------#
## Ensure ssh client is installed.
function ensure_ssh_client() {
    local missing_tools=()

    if ! command -v ssh &>/dev/null; then
        missing_tools+=("ssh")
    fi
    if ! command -v ssh-keygen &>/dev/null; then
        missing_tools+=("ssh-keygen")
    fi
    if ! command -v ssh-copy-id &>/dev/null; then
        missing_tools+=("ssh-copy-id")
    fi
    if ! command -v sftp &>/dev/null; then
        missing_tools+=("sftp")
    fi

    if [ ${#missing_tools[@]} -gt 0 ]; then
        util.log.error "❌ Missing SSH tools: ${missing_tools[*]}"
        if [ "$(uname)" == 'Darwin' ]; then
            util.log.error "SSH tools should be pre-installed on macOS."
            util.log.error "If missing, install with: brew install openssh"
        else
            util.log.error "Install with: sudo apt install openssh-client (Ubuntu/Debian)"
            util.log.error "Or: sudo yum install openssh-clients (RHEL/CentOS)"
        fi
        exit 32
    else
        util.log.info "✅ SSH client tools are available"
    fi
}

ensure_ssh_client

#------------------------------#
#--- Ensure UV is available ---#
#------------------------------#
## Install UV if not available - prefer Homebrew on macOS
function install_uv() {
    local install_message
    if [ "$(uname)" == 'Darwin' ] && has_homebrew; then
        install_message="Install uv using Homebrew (brew install uv)?"
    else
        install_message="Install uv using the official installer (curl -LsSf https://astral.sh/uv/install.sh | sh)?"
    fi

    if ! util.ask_confirmation "$install_message"; then
        util.die "❌ uv installation declined by user. Cannot continue without uv."
    fi

    if [ "$(uname)" == 'Darwin' ] && has_homebrew; then
        util.log.info "⏳ Installing uv using Homebrew (recommended for macOS)..."
        if ! brew install uv; then
            util.die "❌ Failed to install uv using Homebrew. Please check your Homebrew installation."
        fi
        util.log.info "✅ uv installed successfully via Homebrew"
    else
        util.log.info "⏳ Installing uv using the official installer..."
        if command -v curl &>/dev/null; then
            curl -LsSf https://astral.sh/uv/install.sh | sh
        elif command -v wget &>/dev/null; then
            wget -qO- https://astral.sh/uv/install.sh | sh
        else
            util.die "❌ Neither curl nor wget is available. Please install one of them or install uv manually."
        fi

        # Add uv to PATH for current session
        export PATH="$HOME/.cargo/bin:$PATH"
        util.log.info "✅ uv installed successfully via official installer"
    fi
}

## Ensure uv is available
function ensure_uv() {
    if ! command -v uv &>/dev/null; then
        util.log.info "⏳ uv is not installed, installing it..."
        install_uv

        # Verify installation
        if ! command -v uv &>/dev/null; then
            if [ "$(uname)" == 'Darwin' ]; then
                util.die "❌ Failed to install uv. Please install it manually: brew install uv (or curl -LsSf https://astral.sh/uv/install.sh | sh)"
            else
                util.die "❌ Failed to install uv. Please install it manually: curl -LsSf https://astral.sh/uv/install.sh | sh"
            fi
        fi
    else
        util.log.info "✅ uv is already installed: $(uv --version)"
    fi
}

ensure_uv

#-----------------------------#
#--- Ensure Python version ---#
#-----------------------------#
## Get required Python version from .python-version file
function get_required_python_version() {
    if [ ! -f ".python-version" ]; then
        util.die "❌ Please create a file named .python-version before proceeding."
    fi
    cat .python-version
}

## Ensure the required Python version and create virtual environment with uv
function ensure_python_and_venv() {
    local required_python_version
    required_python_version=$(get_required_python_version)

    util.log.info "✅ Required Python version: ${required_python_version}"

    # Remove existing venv if it exists and was created with different tools
    if [ -d ".venv" ] && [ ! -f ".venv/pyvenv.cfg" ]; then
        util.log.warn "Removing existing .venv directory (appears to be from different tool)"
        rm -rf ".venv"
    fi

    # Create virtual environment with specific Python version using uv
    if [ ! -d ".venv" ]; then
        util.log.info "⏳ Creating virtual environment with Python ${required_python_version}..."
        if ! uv venv --python "${required_python_version}" .venv; then
            util.log.warn "Python ${required_python_version} not found locally."
            if ! util.ask_confirmation "Install Python ${required_python_version} using uv (uv python install ${required_python_version})?"; then
                util.die "❌ Python ${required_python_version} installation declined by user. Cannot continue without required Python version."
            fi

            util.log.info "⏳ Running: uv python install ${required_python_version}"
            if ! uv python install "${required_python_version}"; then
                util.die "❌ Failed to install Python ${required_python_version} with uv. Please check your network connection or install it manually."
            fi
            util.log.info "✅ Python ${required_python_version} installed successfully"

            # Try creating the virtual environment again
            if ! uv venv --python "${required_python_version}" .venv; then
                util.die "❌ Failed to create virtual environment with Python ${required_python_version} even after installing it."
            fi
        fi
    else
        util.log.info "✅ Virtual environment already exists at .venv"

        # Verify the Python version in existing venv matches requirements
        if [ -f ".venv/bin/python" ]; then
            local current_version
            current_version=$(.venv/bin/python --version 2>&1 | cut -d' ' -f2)
            if [[ ! "$current_version" =~ ^"${required_python_version}" ]]; then
                util.log.warn "Existing venv has Python ${current_version}, but ${required_python_version} is required. Recreating..."
                rm -rf ".venv"

                # Check if required Python version is available, install if not
                if ! uv venv --python "${required_python_version}" .venv; then
                    util.log.warn "Python ${required_python_version} not found locally."
                    if ! util.ask_confirmation "Install Python ${required_python_version} using uv (uv python install ${required_python_version})?"; then
                        util.die "❌ Python ${required_python_version} installation declined by user. Cannot continue without required Python version."
                    fi

                    util.log.info "⏳ Running: uv python install ${required_python_version}"
                    if ! uv python install "${required_python_version}"; then
                        util.die "❌ Failed to install Python ${required_python_version} with uv. Please check your network connection or install it manually."
                    fi
                    util.log.info "✅ Python ${required_python_version} installed successfully"

                    # Try creating the virtual environment again
                    if ! uv venv --python "${required_python_version}" .venv; then
                        util.die "❌ Failed to recreate virtual environment with Python ${required_python_version} even after installing it."
                    fi
                fi
            fi
        fi
    fi
}

# Deactivate any active virtual environment, suppressing errors if not active.
type deactivate &>/dev/null && deactivate

ensure_python_and_venv

# Activate the virtual environment
# shellcheck source=/dev/null
source ".venv/bin/activate" || util.die "❌ Failed to activate the virtual environment"

#----------------------#
#--- Ensure UV sync ---#
#----------------------#
## Install dependencies using uv
function ensure_uv_sync() {
    # Check if we have a pyproject.toml file
    if [ -f "pyproject.toml" ]; then
        if is_non_interactive_environment; then
            util.log.info "⏳ Dealing with uv errors in non-interactive environment..."

            # Unset environment variables that might force UV into locked mode
            # This prevents CI/CD environments from automatically using --locked
            util.log.info "⏳ Unsetting UV environment variables that might force locked mode..."

            # Debug: Show UV-related environment variables if DEBUG is set
            if [ -n "${DEBUG}" ]; then
                util.log.info "Debug: Current UV-related environment variables:"
                env | grep -i uv || true
                env | grep -E '^(CI|GITHUB_ACTIONS|GITLAB_CI|JENKINS_URL|BAMBOO_BUILD_NUMBER|TEAMCITY_VERSION|TF_BUILD|CIRCLECI|TRAVIS|BUILDKITE|DRONE|CODEBUILD_BUILD_ID|BUILD_ID|BUILD_NUMBER)=' || true
            fi

            unset UV_LOCKED
            unset UV_LOCK_OPTIONS
            unset UV_FROZEN
            export UV_NO_SYNC_LOCKED=1
        fi

        util.log.info "⏳ Installing dependencies with uv sync..."
        if ! uv sync; then
            util.die "❌ Failed to install dependencies with uv sync. Please check your pyproject.toml file."
        fi
        util.log.info "✅ Dependencies installed successfully with uv sync"
    elif [ -f "requirements.txt" ]; then
        util.log.info "⏳ Installing dependencies from requirements.txt..."
        if ! uv pip install -r requirements.txt; then
            util.die "❌ Failed to install dependencies from requirements.txt"
        fi
        util.log.info "✅ Dependencies installed from requirements.txt"
    else
        util.log.warn "No pyproject.toml or requirements.txt found, skipping dependency installation"
    fi
}

ensure_uv_sync

#-------------------------#
#--- Ensure pre-commit ---#
#-------------------------#
## Install pre-commit using uv tool if not available, upgrade if already installed
function install_pre_commit() {
    if ! util.ask_confirmation "Install pre-commit using uv tool (uv tool install pre-commit)?"; then
        util.die "❌ pre-commit installation declined by user. Cannot continue without pre-commit."
    fi

    util.log.info "⏳ Installing pre-commit using uv tool..."

    # Check if uv tool command is available
    if ! uv tool --help >/dev/null 2>&1; then
        util.die "❌ uv tool command is not available. Please update uv to a version that supports 'uv tool' command."
    fi

    if ! uv tool install pre-commit; then
        util.die "❌ Failed to install pre-commit using uv tool. Please check your uv installation and network connectivity."
    fi
    util.log.info "✅ Pre-commit installed successfully via uv tool"
}

## Upgrade pre-commit if already installed via uv tool
function upgrade_pre_commit() {
    # Skip upgrade in non-interactive environments to avoid unnecessary warnings
    if is_non_interactive_environment; then
        util.log.info "✅ Skipping pre-commit upgrade in non-interactive environment"
        return 0
    fi

    # Check if pre-commit is installed via uv tool by listing uv tools
    if uv tool list 2>/dev/null | grep -q "pre-commit"; then
        util.log.info "⏳ Upgrading pre-commit using uv tool..."
        if ! uv tool upgrade pre-commit; then
            util.log.warn "Failed to upgrade pre-commit via uv tool, it might already be up to date"
            return 0
        fi
        util.log.info "✅ Pre-commit upgraded successfully"
    else
        util.log.info "✅ pre-commit is installed via system package manager, skipping uv tool upgrade"
    fi
}

## Ensure pre-commit is available and up to date
function ensure_pre_commit() {
    if ! command -v pre-commit &>/dev/null; then
        util.log.info "⏳ pre-commit is not installed, installing it..."
        install_pre_commit

        # Verify installation
        if ! command -v pre-commit &>/dev/null; then
            util.die "❌ Failed to install pre-commit. Please install it manually: uv tool install pre-commit"
        fi
        util.log.info "✅ Pre-commit installation verified"
    else
        local pre_commit_version
        pre_commit_version=$(pre-commit --version 2>/dev/null || echo "unknown")
        util.log.info "✅ pre-commit is already installed: ${pre_commit_version}"

        # Try to upgrade if it's already installed
        upgrade_pre_commit
    fi

    # Install pre-commit hooks for the project
    util.log.info "⏳ Installing pre-commit hooks for the project..."
    if ! pre-commit install; then
        util.die "❌ Failed to install pre-commit hooks. Please check your .pre-commit-config.yaml file."
    fi

    util.log.info "✅ Pre-commit hooks installed successfully"
    util.log.info "✅ Pre-commit setup completed successfully!"
}

ensure_pre_commit

#--------------------------------#
#--- Ensure Bash/Shell linter ---#
#--------------------------------#
## https://github.com/koalaman/shellcheck
function ensure_shellcheck_if_needed() {
    if [ -n "$(find . -maxdepth 3 -name '*.sh' -print -quit)" ]; then
        if ! command -v shellcheck --version &>/dev/null; then
            if ! util.ask_confirmation "Shell/Bash scripts found. Install shellcheck-py using uv tool (uv tool install shellcheck-py)?"; then
                util.log.warn "⚠️ shellcheck installation declined. Shell scripts will not be linted."
                return 0
            fi

            util.log.info "⏳ Shell/Bash found on this project but shellcheck is not installed, installing shellcheck-py..."
            if ! uv tool install shellcheck-py; then
                util.log.error "❌ Failed to install shellcheck-py using uv tool."
                util.log.error "  https://github.com/koalaman/shellcheck"
                if [ "$(uname)" == 'Darwin' ]; then
                    util.log.error "  macOS: brew install shellcheck (recommended)"
                else
                    util.log.error "  Linux: snap install --channel=edge shellcheck"
                    util.log.error "  Linux: sudo apt install shellcheck"
                fi
                exit 35
            fi
            util.log.info "✅ shellcheck-py installed successfully via uv tool"

            # Verify installation
            if ! command -v shellcheck --version &>/dev/null; then
                util.die "❌ Failed to verify shellcheck installation after installing shellcheck-py"
            fi
        else
            util.log.info "✅ shellcheck is already available"
        fi
    else
        util.log.info "This project doesn't seem to be using Bash/Shell files."
    fi
}

ensure_shellcheck_if_needed

#--------------------------------#
#--- Ensure Dockerfile linter ---#
#--------------------------------#
## https://github.com/hadolint/hadolint
function ensure_hadolint_if_needed() {
    if [ -n "$(find . -maxdepth 3 -name 'Dockerfile*' -print -quit)" ]; then
        if ! command -v hadolint --version &>/dev/null; then
            local install_method
            if [ "$(uname)" == 'Darwin' ] && has_homebrew; then
                install_method="Homebrew (brew install hadolint)"
            else
                install_method="direct download from GitHub releases"
            fi

            if ! util.ask_confirmation "Dockerfile(s) found. Install hadolint using ${install_method}?"; then
                util.log.warn "⚠️ hadolint installation declined. Dockerfiles will not be linted."
                return 0
            fi

            util.log.info "⏳ Dockerfile(s) found on this project but hadolint is not installed, installing hadolint..."

            # Try to install hadolint using different methods based on OS
            if [ "$(uname)" == 'Darwin' ] && has_homebrew; then
                util.log.info "⏳ Installing hadolint using Homebrew..."
                if ! brew install hadolint; then
                    util.log.error "❌ Failed to install hadolint using Homebrew."
                    util.log.error "  https://github.com/hadolint/hadolint#install"
                    exit 40
                fi
                util.log.info "✅ hadolint installed successfully via Homebrew"
            else
                # ...existing Linux installation code...
                local hadolint_version="v2.12.0"  # You can update this to latest version
                local hadolint_url="https://github.com/hadolint/hadolint/releases/download/${hadolint_version}/hadolint-Linux-x86_64"
                local install_dir="$HOME/.local/bin"

                # Create local bin directory if it doesn't exist
                mkdir -p "$install_dir"

                if command -v curl &>/dev/null; then
                    if ! curl -L "$hadolint_url" -o "$install_dir/hadolint"; then
                        util.log.error "❌ Failed to download hadolint."
                        util.log.error "  https://github.com/hadolint/hadolint#install"
                        exit 40
                    fi
                elif command -v wget &>/dev/null; then
                    if ! wget "$hadolint_url" -O "$install_dir/hadolint"; then
                        util.log.error "❌ Failed to download hadolint."
                        util.log.error "  https://github.com/hadolint/hadolint#install"
                        exit 40
                    fi
                else
                    util.log.error "❌ Neither curl nor wget is available to download hadolint."
                    util.log.error "  Please install hadolint manually: https://github.com/hadolint/hadolint#install"
                    exit 40
                fi

                # Make it executable
                chmod +x "$install_dir/hadolint"

                # Add to PATH for current session if not already there
                if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
                    export PATH="$HOME/.local/bin:$PATH"
                fi

                util.log.info "✅ hadolint installed successfully to $install_dir/hadolint"
            fi

            # Verify installation
            if ! command -v hadolint --version &>/dev/null; then
                util.die "❌ Failed to verify hadolint installation"
            fi
        else
            util.log.info "✅ hadolint is already available"
        fi
    else
        util.log.info "This project doesn't seem to be using Dockerfile(s)."
    fi
}

ensure_hadolint_if_needed

#--------------------------------#
#--- Ensure Kubernetes linter ---#
#--------------------------------#
## https://github.com/stackrox/kube-linter
function ensure_kube_linter_if_needed() {
    # If there are yaml files containing both `apiVersion:` and `kind:` then is very likely this project contains K8s manifests
    if [ -n "$(find . -name '*.yaml' -type f -exec grep -qlm1 'apiVersion:' {} \; -exec grep -lm1 -H 'kind:' {} \; -a -quit)" ]; then
        if ! command -v kube-linter version &>/dev/null; then
            local install_method
            if [ "$(uname)" == 'Darwin' ] && has_homebrew; then
                install_method="Homebrew (brew install kube-linter)"
            else
                install_method="direct download from GitHub releases"
            fi

            if ! util.ask_confirmation "Kubernetes manifest(s) found. Install kube-linter using ${install_method}?"; then
                util.log.warn "⚠️ kube-linter installation declined. Kubernetes manifests will not be linted."
                return 0
            fi

            util.log.info "⏳ Kubernetes manifest(s) found on this project but kube-linter is not installed, installing kube-linter..."

            # Try to install kube-linter using different methods based on OS
            if [ "$(uname)" == 'Darwin' ] && has_homebrew; then
                util.log.info "⏳ Installing kube-linter using Homebrew..."
                if ! brew install kube-linter; then
                    util.log.error "❌ Failed to install kube-linter using Homebrew."
                    util.log.error "  https://github.com/stackrox/kube-linter#installing-kubelinter"
                    exit 42
                fi
                util.log.info "✅ kube-linter installed successfully via Homebrew"
            else
                # ...existing Linux installation code...
                local kube_linter_version
                util.log.info "⏳ Fetching latest kube-linter version from GitHub API..."
                if command -v curl &>/dev/null; then
                    kube_linter_version=$(curl -s https://api.github.com/repos/stackrox/kube-linter/releases/latest | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')
                elif command -v wget &>/dev/null; then
                    kube_linter_version=$(wget -qO- https://api.github.com/repos/stackrox/kube-linter/releases/latest | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')
                else
                    util.log.warn "Neither curl nor wget available to fetch latest version, using fallback version v0.6.8"
                    kube_linter_version="v0.6.8"
                fi

                # Fallback to a known working version if API call failed
                if [ -z "$kube_linter_version" ] || [ "$kube_linter_version" = "null" ]; then
                    util.log.warn "Failed to fetch latest version from GitHub API, using fallback version v0.6.8"
                    kube_linter_version="v0.6.8"
                fi

                util.log.info "Using kube-linter version: $kube_linter_version"
                local kube_linter_url="https://github.com/stackrox/kube-linter/releases/download/${kube_linter_version}/kube-linter-linux.tar.gz"
                local install_dir="$HOME/.local/bin"
                local temp_dir
                temp_dir=$(mktemp -d)

                # Create local bin directory if it doesn't exist
                mkdir -p "$install_dir"

                if command -v curl &>/dev/null; then
                    if ! curl -L "$kube_linter_url" -o "$temp_dir/kube-linter.tar.gz"; then
                        util.log.error "❌ Failed to download kube-linter."
                        util.log.error "  https://github.com/stackrox/kube-linter#installing-kubelinter"
                        rm -rf "$temp_dir"
                        exit 42
                    fi
                elif command -v wget &>/dev/null; then
                    if ! wget "$kube_linter_url" -O "$temp_dir/kube-linter.tar.gz"; then
                        util.log.error "❌ Failed to download kube-linter."
                        util.log.error "  https://github.com/stackrox/kube-linter#installing-kubelinter"
                        rm -rf "$temp_dir"
                        exit 42
                    fi
                else
                    util.log.error "❌ Neither curl nor wget is available to download kube-linter."
                    util.log.error "  Please install kube-linter manually: https://github.com/stackrox/kube-linter#installing-kubelinter"
                    rm -rf "$temp_dir"
                    exit 42
                fi

                # Extract the binary
                if ! tar -xzf "$temp_dir/kube-linter.tar.gz" -C "$temp_dir"; then
                    util.log.error "❌ Failed to extract kube-linter archive."
                    rm -rf "$temp_dir"
                    exit 42
                fi

                # Move the binary to install directory
                if ! mv "$temp_dir/kube-linter" "$install_dir/kube-linter"; then
                    util.log.error "❌ Failed to move kube-linter to install directory."
                    rm -rf "$temp_dir"
                    exit 42
                fi

                # Make it executable
                chmod +x "$install_dir/kube-linter"

                # Clean up temp directory
                rm -rf "$temp_dir"

                # Add to PATH for current session if not already there
                if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
                    export PATH="$HOME/.local/bin:$PATH"
                fi

                util.log.info "✅ kube-linter installed successfully to $install_dir/kube-linter"
            fi

            # Verify installation
            if ! command -v kube-linter version &>/dev/null; then
                util.die "❌ Failed to verify kube-linter installation"
            fi
        else
            util.log.info "✅ kube-linter is already available"
        fi
    else
        util.log.info "This project doesn't seem to be using Kubernetes manifests."
    fi
}

ensure_kube_linter_if_needed

#------------------------------------#
#--- Ensure CloudFormation linter ---#
#------------------------------------#
## https://github.com/aws-cloudformation/cfn-lint
function ensure_cfn_lint_if_needed() {
    # If there are yaml files containing `AWSTemplateFormatVersion` then is very likely this project contains CloudFormation templates
    if [ -n "$(find . -name '*.yaml' -type f -exec grep -qlm1 'AWSTemplateFormatVersion' {} \; -print -quit)" ]; then
        if ! cfn-lint --help &>/dev/null; then
            if ! util.ask_confirmation "CloudFormation template(s) found. Install cfn-lint using uv tool (uv tool install \"cfn-lint[full]\")?"; then
                util.log.warn "⚠️ cfn-lint installation declined. CloudFormation templates will not be linted."
                return 0
            fi

            util.log.info "⏳ CloudFormation template(s) found on this project but cfn-lint is not installed, installing cfn-lint..."
            if ! uv tool install "cfn-lint[full]" --force; then
                util.log.error "❌ Failed to install cfn-lint using uv tool."
                util.log.error "  https://github.com/aws-cloudformation/cfn-lint"
                exit 44
            fi
            util.log.info "✅ cfn-lint installed successfully via uv tool"

            # Verify installation
            if ! cfn-lint --help &>/dev/null; then
                util.die "❌ Failed to verify cfn-lint installation"
            fi
        else
            util.log.info "✅ cfn-lint is already available"
        fi
    else
        util.log.info "This project doesn't seem to be using CloudFormation templates."
    fi
}

ensure_cfn_lint_if_needed

#----------------------------------------#
#--- Ensure PyInvoke and invoke tests ---#
#----------------------------------------#
## https://github.com/pyinvoke/invoke
function ensure_pyinvoke_if_needed() {
    if [ -f "tasks.py" ] || [ -f "invoke.yaml" ]; then
        # let's make sure invoke works since the .venv is activated
        if ! invoke setup; then
            util.die "Failed to invoke setup"
        fi
        if ! invoke hooks; then
            util.die "Failed to run hooks"
        fi
        if [ -d 'tests' ] && ! invoke tests; then
            util.die "Failed to run tests"
        fi
    else
        util.log.info "This project doesn't seem to be using pyinvoke."
    fi
}

ensure_pyinvoke_if_needed

#-----------------------------------------#
#--- Ensure NodeJS for MkDocs JS needs ---#
#-----------------------------------------#
## https://github.com/DavidAnson/markdownlint
function ensure_nodejs_if_needed() {
    if [ -f "mkdocs.yml" ] || [ -f "docs/robots.txt" ]; then
        if ! command -v node &>/dev/null; then
            local install_method
            if [ "$(uname)" == 'Darwin' ] && has_homebrew; then
                install_method="Homebrew (brew install node)"
            else
                install_method="nvm (Node Version Manager)"
            fi

            if ! util.ask_confirmation "NodeJS is required for this project. Install NodeJS using ${install_method}?"; then
                util.log.warn "⚠️ NodeJS installation declined. Some project features may not work."
                return 0
            fi

            util.log.info "⏳ NodeJS is required for this project but not installed, installing it..."

            if [ "$(uname)" == 'Darwin' ] && has_homebrew; then
                util.log.info "⏳ Installing NodeJS using Homebrew..."
                if ! brew install node; then
                    util.log.error "❌ Failed to install NodeJS using Homebrew."
                    util.log.error "  Alternative: Download from https://nodejs.org/"
                    exit 54
                fi
                util.log.info "✅ NodeJS installed successfully via Homebrew"
            else
                # ...existing Linux nvm installation code...
                util.log.info "⏳ Installing NodeJS for Linux using nvm..."
                if command -v curl &>/dev/null; then
                    # Download and install nvm
                    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
                elif command -v wget &>/dev/null; then
                    wget -qO- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
                else
                    util.die "❌ Neither curl nor wget is available. Please install one of them or install nvm manually."
                fi

                # Source nvm for the current script session
                export NVM_DIR="$HOME/.nvm"
                # shellcheck source=/dev/null
                [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

                # Install Node.js version 24
                if ! nvm install 24; then
                    util.log.error "❌ Failed to install NodeJS version 24 using nvm."
                    util.log.error "  Please check your network connection or nvm installation."
                    exit 54
                fi
                util.log.info "✅ NodeJS installed successfully via nvm"
            fi

            # Verify NodeJS installation
            # Refresh command cache after installation
            hash -r 2>/dev/null || true

            if ! command -v node &>/dev/null; then
                util.log.error "❌ Failed to verify NodeJS installation after installing via nvm."
                util.die "  Please run 'source ~/.bashrc' or restart your shell and try again."
            fi
        else
            util.log.info "✅ NodeJS is already available: $(node --version)"
        fi

        if ! command -v npm &>/dev/null; then
            util.log.warn "npm command not found, but it should have been installed with Node.js via nvm."
            util.log.warn "This might indicate a PATH issue. Trying to proceed..."
        else
            util.log.info "✅ npm is already available: $(npm --version)"
        fi

        util.log.info "✅ NodeJS and npm are available"
    else
        util.log.info "This project doesn't seem to need NodeJS."
    fi
}

ensure_nodejs_if_needed

#--------------#
#--- AWS CLI ---#
#--------------#
## Helper function to install AWS CLI v2 depending on OS and architecture
function install_aws_cli() {
    local device
    local arch
    device=$(uname)
    arch=$(uname -m)

    util.log.info "⏳ Installing AWS CLI v2..."

    if [[ $device == *"Darwin"* ]]; then
        util.log.info "⏳ Installing AWS CLI v2 for macOS..."
        if command -v curl &>/dev/null; then
            if ! curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"; then
                util.die "❌ Failed to download AWS CLI v2 installer for macOS"
            fi
            if ! sudo installer -pkg AWSCLIV2.pkg -target /; then
                util.die "❌ Failed to install AWS CLI v2 for macOS"
            fi
            rm -f AWSCLIV2.pkg
            util.log.info "✅ AWS CLI v2 installed successfully for macOS"
        else
            util.die "❌ curl is required to download AWS CLI v2 installer"
        fi
    elif [[ $device == *"Linux"* ]]; then
        util.log.info "⏳ Installing AWS CLI v2 for Linux ($arch)..."
        local aws_url
        if [[ $arch == *"x86_64"* ]]; then
            aws_url="https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip"
        elif [[ $arch == *"aarch64"* ]]; then
            aws_url="https://awscli.amazonaws.com/awscli-exe-linux-aarch64.zip"
        else
            util.die "❌ Unsupported Linux architecture: $arch. Please check https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html to install manually"
        fi

        # Check for required tools
        if ! command -v curl &>/dev/null; then
            util.die "❌ curl is required to download AWS CLI v2 installer"
        fi
        if ! command -v unzip &>/dev/null; then
            util.die "❌ unzip is required to extract AWS CLI v2 installer"
        fi

        # Download and install
        if ! curl "$aws_url" -o "awscliv2.zip"; then
            util.die "❌ Failed to download AWS CLI v2 installer for Linux"
        fi
        if ! unzip awscliv2.zip; then
            rm -f awscliv2.zip
            util.die "❌ Failed to extract AWS CLI v2 installer"
        fi
        if ! sudo ./aws/install --update; then
            rm -rf aws awscliv2.zip
            util.die "❌ Failed to install AWS CLI v2 for Linux"
        fi
        rm -rf aws awscliv2.zip
        util.log.info "✅ AWS CLI v2 installed successfully for Linux"
    fi
}

## Ensure AWS CLI v2 is available
function ensure_aws_cli() {
    if ! command -v aws &>/dev/null; then
        util.log.info "⏳ AWS CLI is not installed, installing it..."

        if ! util.ask_confirmation "Install AWS CLI v2?"; then
            util.die "❌ AWS CLI installation declined by user. Cannot continue without AWS CLI for this project."
        fi

        install_aws_cli

        # Verify installation
        if ! command -v aws &>/dev/null; then
            util.die "❌ Failed to install AWS CLI v2. Please install it manually: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
        fi
    else
        # Check if it's AWS CLI v2
        local aws_version
        aws_version=$(aws --version 2>&1 | head -n1)
        if [[ "$aws_version" =~ aws-cli/2\. ]]; then
            util.log.info "✅ AWS CLI v2 is already installed: $aws_version"
        elif [[ "$aws_version" =~ aws-cli/1\. ]]; then
            util.log.warn "⚠️ AWS CLI v1 detected: $aws_version"
            util.log.warn "This project requires AWS CLI v2. AWS CLI v1 is deprecated."

            if util.ask_confirmation "Upgrade to AWS CLI v2?"; then
                install_aws_cli

                # Verify the upgrade
                aws_version=$(aws --version 2>&1 | head -n1)
                if [[ "$aws_version" =~ aws-cli/2\. ]]; then
                    util.log.info "✅ Successfully upgraded to AWS CLI v2: $aws_version"
                else
                    util.die "❌ Failed to upgrade to AWS CLI v2"
                fi
            else
                util.log.warn "⚠️ Continuing with AWS CLI v1, but some features may not work correctly"
            fi
        else
            util.log.info "✅ AWS CLI is available: $aws_version"
        fi
    fi
}

ensure_aws_cli

#------------#
#--- DONE ---#
#------------#
util.log.info ""
util.log.info "#-------------------------------------------------------------#"
util.log.info "# SUCCESS! Environment setup completed successfully!          #"
util.log.info "#                                                             #"
util.log.info "# Your environment is now ready with:                         #"
util.log.info "# - Python virtual environment (.venv)                        #"
util.log.info "# - Dependencies installed via uv sync                        #"
util.log.info "# - Pre-commit hooks installed and configured                 #"
util.log.info "#                                                             #"
util.log.info "# The virtual environment is already activated.               #"
util.log.info "# If you need to reactivate it later, use:                    #"
util.log.info "#     source .venv/bin/activate                               #"
util.log.info "#-------------------------------------------------------------#"
