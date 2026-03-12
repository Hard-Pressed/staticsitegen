#!/usr/bin/env bash
set -euo pipefail

# Production build for GitHub Pages-style repo subpath hosting.
python3 src/main.py "/staticsitegen/"
