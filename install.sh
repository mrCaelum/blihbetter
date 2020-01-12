#!/usr/bin/env sh

if [ "$(id -u)" != "0" ]; then
    cp ./eiota.py ~/.local/bin/eiota && echo "Script copied in '~/.local/bin/eiota'"
else
    cp ./eiota.py /usr/bin/eiota && echo "Script copied in '/usr/bin/eiota'"
fi