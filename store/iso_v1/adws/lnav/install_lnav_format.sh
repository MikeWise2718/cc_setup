#!/usr/bin/env bash
#
# install_lnav_format.sh - Install ADW execution log format for lnav
#
# Usage:
#   ./install_lnav_format.sh          # Install format
#   ./install_lnav_format.sh --check  # Check if lnav is available
#   ./install_lnav_format.sh --remove # Remove installed format
#
# This script installs the ADW execution log format file so lnav can
# parse and display ADW workflow logs with proper formatting.
#
# For more information about lnav: https://lnav.org/

set -e

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FORMAT_FILE="$SCRIPT_DIR/adw_execution.lnav.json"

# lnav format directories
LNAV_USER_DIR="$HOME/.lnav/formats/installed"
LNAV_SYSTEM_DIR="/etc/lnav/formats"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}!${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

check_lnav() {
    if command -v lnav &> /dev/null; then
        local version
        version=$(lnav -V 2>&1 | head -1)
        print_success "lnav is installed: $version"
        return 0
    else
        print_error "lnav is not installed"
        echo ""
        echo "Install lnav using one of these methods:"
        echo "  macOS:   brew install lnav"
        echo "  Ubuntu:  sudo apt install lnav"
        echo "  Fedora:  sudo dnf install lnav"
        echo "  Arch:    sudo pacman -S lnav"
        echo ""
        echo "Or download from: https://lnav.org/"
        return 1
    fi
}

install_format() {
    echo "Installing ADW execution log format for lnav..."
    echo ""

    # Check if lnav is installed
    if ! check_lnav; then
        echo ""
        print_warning "Continuing with installation anyway..."
        echo ""
    fi

    # Check if format file exists
    if [[ ! -f "$FORMAT_FILE" ]]; then
        print_error "Format file not found: $FORMAT_FILE"
        exit 1
    fi

    # Create user format directory if it doesn't exist
    if [[ ! -d "$LNAV_USER_DIR" ]]; then
        echo "Creating lnav format directory: $LNAV_USER_DIR"
        mkdir -p "$LNAV_USER_DIR"
    fi

    # Copy format file
    echo "Copying format file..."
    cp "$FORMAT_FILE" "$LNAV_USER_DIR/"

    print_success "Format installed to: $LNAV_USER_DIR/adw_execution.lnav.json"
    echo ""
    echo "Usage:"
    echo "  lnav /path/to/adw_execution.log.jsonl"
    echo ""
    echo "Or configure logging directory in ~/.adw/settings.json:"
    echo '  { "logging_directory": "~/logs/adw" }'
}

remove_format() {
    echo "Removing ADW execution log format..."

    local installed_file="$LNAV_USER_DIR/adw_execution.lnav.json"

    if [[ -f "$installed_file" ]]; then
        rm "$installed_file"
        print_success "Format removed from: $installed_file"
    else
        print_warning "Format not found at: $installed_file"
    fi
}

show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Install ADW execution log format for lnav."
    echo ""
    echo "Options:"
    echo "  --check   Check if lnav is installed"
    echo "  --remove  Remove installed format"
    echo "  --help    Show this help message"
    echo ""
    echo "Without options, installs the format to ~/.lnav/formats/installed/"
}

# Main
case "${1:-}" in
    --check)
        check_lnav
        ;;
    --remove)
        remove_format
        ;;
    --help|-h)
        show_help
        ;;
    "")
        install_format
        ;;
    *)
        print_error "Unknown option: $1"
        show_help
        exit 1
        ;;
esac
