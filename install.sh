#!/usr/bin/env sh

if [ "$(id -u)" != "0" ]; then
    cp ./blihbetter.py ~/.local/bin/blihbetter && echo "Script copied in '~/.local/bin/blihbetter'"
else
    cp ./blihbetter.py /usr/bin/blihbetter && echo "Script copied in '/usr/bin/blihbetter'"
fi