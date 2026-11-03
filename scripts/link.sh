#!/bin/sh
# Symlink every skill into every Claude profile (~/.claude and ~/.claude-*),
# and project-scoped skills into the checkout projects.txt names.
# The skills step of sync_profiles.py; run that script with no flags to sync
# settings, plugins, MCP servers and profile/home/ files as well.
exec python3 "$(dirname "$0")/sync_profiles.py" --only skills "$@"
