#!/bin/bash
# source-integrity-check.sh
#
# Pre-commit hook: when source citations change in a data file,
# the corresponding data values must also change.
#
# Prevents the error of swapping source attribution (e.g., from
# Source A to Source B) while keeping Source A's data values.
# Changing attribution without changing data is fabrication.
#
# Install: cp hooks/source-integrity-check.sh .git/hooks/pre-commit
#   or: hooks/install.sh
#
# Configuration: set these to match your project's file paths.
SOURCES_FILE="${SOURCES_FILE:-src/data/sources.ts}"
DATA_FILE="${DATA_FILE:-src/data/rates.ts}"

# Only check if the sources file is staged
if ! git diff --cached --name-only | grep -q "^${SOURCES_FILE}$"; then
  exit 0
fi

# Check if any publisher/source names changed
SOURCE_DIFF=$(git diff --cached -- "$SOURCES_FILE" \
  | grep -E "^\+.*(publisher|source|citation|attribution):" \
  | grep -v "^\+\+\+" || true)

if [ -z "$SOURCE_DIFF" ]; then
  # No source publisher changes, nothing to check
  exit 0
fi

# Source publishers changed. Check if the data file also changed.
if ! git diff --cached --name-only | grep -q "^${DATA_FILE}$"; then
  echo ""
  echo "SOURCE INTEGRITY CHECK FAILED"
  echo "============================="
  echo ""
  echo "Source citations in ${SOURCES_FILE} changed:"
  echo "$SOURCE_DIFF"
  echo ""
  echo "But ${DATA_FILE} (which contains the data values) was NOT modified."
  echo ""
  echo "RULE: If you change which source a data point cites, you must ALSO"
  echo "replace the data values with figures from the new source."
  echo "Changing attribution without changing data is fabrication."
  echo ""
  echo "If this is a legitimate citation-only fix (e.g., correcting a URL),"
  echo "stage both files or use: git commit --no-verify"
  echo ""
  exit 1
fi

# Both files changed: expected pattern
exit 0
