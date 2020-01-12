#!/usr/bin/env sh

if [ "$(id -u)" != "0" ]; then
    rm ~/.local/bin/eiota && echo "Script '~/.local/bin/eiota' removed"
else
    rm /usr/bin/eiota && echo "Script '/usr/bin/eiota' removed"
fi