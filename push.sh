#!/bin/bash
# Quick push - run after rebuilding the public pages
# Usage: bash push.sh "commit message"

MSG="${1:-Update CT.gov Hiddenness Atlas public site}"

git add -A
git commit -m "$MSG"
git push origin master 2>/dev/null || git push origin main 2>/dev/null

echo ""
echo "Pushed to GitHub. View at:"
echo "  https://github.com/mahmood726-cyber/ctgov-hiddenness-atlas"
echo "  https://mahmood726-cyber.github.io/ctgov-hiddenness-atlas/"
