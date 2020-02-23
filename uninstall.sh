#!/usr/bin/env sh

if [ "$(id -u)" != "0" ]; then
    rm ~/.local/bin/blihbetter && echo "Script '~/.local/bin/blihbetter' removed"
else
    rm /usr/bin/blihbetter && echo "Script '/usr/bin/blihbetter' removed"
fi