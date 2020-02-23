# blihbetter
A simple python script to simplify BLIH usage for Epitech students.

[![License](https://img.shields.io/github/license/mrCaelum/blihbetter)](http://badges.mit-license.org)
[![AUR](https://img.shields.io/aur/version/blihbetter)](https://aur.archlinux.org/packages/blihbetter/)

## Installation

### Archlinux

###### You can install [blihbetter](https://aur.archlinux.org/packages/blihbetter/) from the [AUR](https://aur.archlinux.org/):
```
yay -S blihbetter
```

### Others

###### The install script will copy blihbetter in `~/.local/bin`
```
chmod +x install.sh
./install.sh
```

###### You can also run it as root to copy blihbetter in `/usr/bin`
```
chmod +x install.sh
sudo ./install.sh
```

## Usage

```
blihbetter [command] arguments...
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
