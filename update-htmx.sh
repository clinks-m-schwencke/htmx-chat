#!/usr/bin/env bash

set -euo pipefail

HTMX_URL="https://cdn.jsdelivr.net/npm/htmx.org@next/dist/htmx.min.js"

# Curl the 'next' head for htmx, to check version
# "x-jsd-version"
LATEST_VERSION=$(curl -I "$HTMX_URL" | grep "x-jsd-version:" | awk '{print $2}')

# Check against the version in '.htmx-version'
# Create file if it doesn't exist
[ ! -f ".htmx-version" ] && touch ".htmx-version"
CURRENT_VERSION=$(cat ".htmx-version")

# If different, download the new htmx into './chat/static/chat/htmx.min.js'
echo "Latest version: $LATEST_VERSION"
echo "Current version: $CURRENT_VERSION"

if [ "$LATEST_VERSION" != "$CURRENT_VERSION" ]; then
    # Delete old version
    rm ./chat/static/chat/htmx.min.js
    # Download new version
    (cd chat/static/chat && curl -O "$HTMX_URL")
    echo "Downloaded HTMX version: $LATEST_VERSION"
    echo "$LATEST_VERSION" > .htmx-version
else
    echo "Already up to date!"
fi
