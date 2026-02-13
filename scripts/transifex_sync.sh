#!/bin/bash
# Transifex sync script for LinguaEdit
# Usage: ./scripts/transifex_sync.sh [push|pull|both]
#
# Requires: brew install transifex-cli
# API token stored in macOS Keychain: transifex/api_token

set -e
cd "$(dirname "$0")/.."

export TX_TOKEN=$(security find-generic-password -s "transifex/api_token" -w 2>/dev/null)
if [ -z "$TX_TOKEN" ]; then
    echo "Error: Transifex API token not found in Keychain"
    echo "Store it: security add-generic-password -a transifex -s transifex/api_token -w YOUR_TOKEN -U login.keychain-db"
    exit 1
fi

ACTION="${1:-both}"

case "$ACTION" in
    push)
        echo "==> Pushing source strings to Transifex..."
        tx push --source --force
        echo "==> Pushing Swedish translations..."
        tx push --translation --languages sv_SE --force
        ;;
    pull)
        echo "==> Pulling translations from Transifex..."
        tx pull --all --force
        echo "==> Rebuilding .qm files..."
        for ts in src/linguaedit/translations/linguaedit_*.ts; do
            lang=$(basename "$ts" .ts | sed 's/linguaedit_//')
            echo "  Compiling $lang..."
            pyside6-lrelease "$ts" -qm "src/linguaedit/translations/linguaedit_${lang}.qm" 2>/dev/null
        done
        echo "Done! Don't forget to commit new translations."
        ;;
    both)
        $0 push
        $0 pull
        ;;
    *)
        echo "Usage: $0 [push|pull|both]"
        exit 1
        ;;
esac
