#!/bin/bash

# Release script for Neuravo SDK
# Usage: ./scripts/release.sh <version> <push>
# Example: ./scripts/release.sh 0.2.0 true

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check arguments
if [ $# -lt 1 ]; then
    echo -e "${RED}Usage: ./scripts/release.sh <version> [push]${NC}"
    echo -e "${YELLOW}Example: ./scripts/release.sh 0.2.0${NC}"
    echo -e "${YELLOW}Example: ./scripts/release.sh 0.2.0 true${NC}"
    exit 1
fi

NEW_VERSION=$1
PUSH_TO_REMOTE=${2:-false}

# Validate version format (semantic versioning)
if ! [[ $NEW_VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo -e "${RED}Invalid version format. Expected: MAJOR.MINOR.PATCH${NC}"
    exit 1
fi

echo -e "${YELLOW}Preparing release for version ${NEW_VERSION}${NC}"

# Check if working directory is clean
if [ ! -z "$(git status --short)" ]; then
    echo -e "${RED}Working directory is not clean. Please commit or stash changes.${NC}"
    exit 1
fi

# Update version in _version.py
echo -e "${GREEN}Updating version in src/neuravo/_version.py${NC}"
python3 << EOF
import re

version_file = 'src/neuravo/_version.py'
with open(version_file, 'r') as f:
    content = f.read()

# Update __version__
content = re.sub(
    r'__version__ = "[^"]+"',
    f'__version__ = "{NEW_VERSION}"',
    content
)

# Update __version_info__
major, minor, patch = NEW_VERSION.split('.')
content = re.sub(
    r'__version_info__ = \([^)]+\)',
    f'__version_info__ = ({major}, {minor}, {patch})',
    content
)

with open(version_file, 'w') as f:
    f.write(content)

print(f"Version updated to {NEW_VERSION}")
EOF

# Update version in pyproject.toml
echo -e "${GREEN}Updating version in pyproject.toml${NC}"
sed -i "s/version = \"[^\"]*\"/version = \"${NEW_VERSION}\"/" pyproject.toml

# Update CHANGELOG.md
echo -e "${GREEN}Updating CHANGELOG.md${NC}"
DATE=$(date +"%Y-%m-%d")
python3 << EOF
import re

changelog_file = 'CHANGELOG.md'
with open(changelog_file, 'r') as f:
    content = f.read()

# Replace [Unreleased] with new version
new_entry = f"## [{NEW_VERSION}] - {DATE}"
content = content.replace("## [Unreleased]", new_entry + "\n\n## [Unreleased]", 1)

with open(changelog_file, 'w') as f:
    f.write(content)

print(f"CHANGELOG.md updated with version {NEW_VERSION}")
EOF

# Run tests
echo -e "${YELLOW}Running tests...${NC}"
python3 -m pytest tests/ -v --tb=short
if [ $? -ne 0 ]; then
    echo -e "${RED}Tests failed. Aborting release.${NC}"
    git checkout src/neuravo/_version.py pyproject.toml CHANGELOG.md
    exit 1
fi

# Check coverage
echo -e "${YELLOW}Checking code coverage...${NC}"
python3 -m pytest tests/ --cov=src/neuravo --cov-fail-under=85 -q
if [ $? -ne 0 ]; then
    echo -e "${RED}Coverage check failed. Aborting release.${NC}"
    git checkout src/neuravo/_version.py pyproject.toml CHANGELOG.md
    exit 1
fi

# Type checking
echo -e "${YELLOW}Running type checking...${NC}"
python3 -m mypy src/neuravo
if [ $? -ne 0 ]; then
    echo -e "${RED}Type checking failed. Aborting release.${NC}"
    git checkout src/neuravo/_version.py pyproject.toml CHANGELOG.md
    exit 1
fi

# Linting
echo -e "${YELLOW}Running linting...${NC}"
python3 -m ruff check src/neuravo
if [ $? -ne 0 ]; then
    echo -e "${RED}Linting failed. Aborting release.${NC}"
    git checkout src/neuravo/_version.py pyproject.toml CHANGELOG.md
    exit 1
fi

# Create commit
echo -e "${GREEN}Creating release commit${NC}"
git add src/neuravo/_version.py pyproject.toml CHANGELOG.md
git commit -m "chore: release v${NEW_VERSION}"

# Create tag
echo -e "${GREEN}Creating git tag v${NEW_VERSION}${NC}"
git tag -a "v${NEW_VERSION}" -m "Release version ${NEW_VERSION}"

# Push to remote (optional)
if [ "$PUSH_TO_REMOTE" = "true" ]; then
    echo -e "${GREEN}Pushing to remote${NC}"
    git push origin main
    git push origin "v${NEW_VERSION}"
    
    # Build distribution
    echo -e "${YELLOW}Building distribution packages${NC}"
    python3 -m pip install build
    python3 -m build
    
    # Upload to PyPI
    echo -e "${YELLOW}Uploading to PyPI${NC}"
    python3 -m pip install twine
    python3 -m twine upload dist/*
    
    echo -e "${GREEN}Release ${NEW_VERSION} published successfully!${NC}"
else
    echo -e "${GREEN}Release ${NEW_VERSION} prepared (not pushed)${NC}"
    echo -e "${YELLOW}To push, run: ./scripts/release.sh ${NEW_VERSION} true${NC}"
fi

echo -e "${GREEN}Done!${NC}"
