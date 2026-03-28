#!/bin/bash
# Install the source integrity check as a git pre-commit hook.
#
# Usage: ./hooks/install.sh

HOOK_DIR="$(git rev-parse --git-dir)/hooks"
HOOK_FILE="$HOOK_DIR/pre-commit"

if [ -f "$HOOK_FILE" ]; then
  echo "A pre-commit hook already exists at $HOOK_FILE"
  echo "To append, add this line to your existing hook:"
  echo "  ./hooks/source-integrity-check.sh"
  exit 1
fi

cp hooks/source-integrity-check.sh "$HOOK_FILE"
chmod +x "$HOOK_FILE"
echo "Installed source-integrity-check.sh as pre-commit hook"
