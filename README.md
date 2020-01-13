# eIOTA
A simple python script to simplify BLIH usage for Epitech students.

[![License](https://img.shields.io/github/license/mrCaelum/eiota)](http://badges.mit-license.org)
[![AUR](https://img.shields.io/aur/version/eiota)](https://aur.archlinux.org/packages/eiota/)

## Installation

### Archlinux

###### You can install [eiota](https://aur.archlinux.org/packages/eiota/) from the [AUR](https://aur.archlinux.org/):
```
yay -S eiota
```

### Others

###### The install script will copy eiota in `~/.local/bin`
```
chmod +x install.sh
./install.sh
```

###### You can also run it as root to copy eiota in `/usr/bin`
```
chmod +x install.sh
sudo ./install.sh
```

## Usage

```
eiota [command] arguments...
```

#### COMMANDS:
- `help`               - Display this help message
- `config`              - Setup the config file
- `ping`               - Ask to blih who you are
- `ls`                 - Display every user repository
- `create <name>`      - Create a new repository
- `new <name>`         - Create a new repository with default Epitech config
- `clone <name>`       - Clone the repository
- `rm <name>`          - Remove the repository
- `info <name>`        - Display repository informations
- `acl (get/set)`      - Edit the repository ACLs
- `sshkey (add/ls/rm)` - Edit the repository ACLs

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)
