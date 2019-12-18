#!/bin/python3

import os
import sys
import subprocess
import json
import hashlib
import getpass
import datetime

USER_IDENTIFIER = 'user'
TOKEN_IDENTIFIER = 'token'
GIT_URL_IDENTIFIER = 'git_url'
BLIH_URL_IDENTIFIER = 'blih_url'
DEFAULT_CONFIG_FILE = os.path.expanduser("~") + "/.config/epitech/config.json"
DEFAULT_GIT_URL = "git@git.epitech.eu"
DEFAULT_BLIH_URL = "https://blih.epitech.eu/"

def print_logo():
    print('\033[1;36m')
    print('         ________  _________  ')
    print('   ___  /  _/ __ \/_  __/   | ')
    print('  / _ \ / // / / / / / / /| | ')
    print(' /  __// // /_/ / / / / ___ | ')
    print(' \___/___/\____/ /_/ /_/  |_| ')
    print('\033[0m')

def set_user_config(path=DEFAULT_CONFIG_FILE):
    print_logo()
    print('\033[1;33mConfig file generation:\033[0;2m \'' + path + '\'\033[0m', end='\n\n')
    user_config = {}
    try:
        user_config[USER_IDENTIFIER] = input('User: ')
        user_config[TOKEN_IDENTIFIER] = hashlib.sha512(bytes(getpass.getpass(), 'utf8')).hexdigest()
        user_config[GIT_URL_IDENTIFIER] = input('Git url (' + DEFAULT_GIT_URL + '): ')
        user_config[BLIH_URL_IDENTIFIER] = input('Blih url (' + DEFAULT_BLIH_URL + '): ')
    except:
        print("\n\n\033[37;44m INFO \033[0m Exited")
        exit(0)
    if not user_config[GIT_URL_IDENTIFIER]:
        user_config[GIT_URL_IDENTIFIER] = DEFAULT_GIT_URL
    if not user_config[BLIH_URL_IDENTIFIER]:
        user_config[BLIH_URL_IDENTIFIER] = DEFAULT_BLIH_URL
    if not os.path.exists(os.path.dirname(path)):
        try:
            os.makedirs(os.path.dirname(path))
        except:
            print("\033[37;41m ERROR \033[0m Unable to create config file")
            exit(1)
    try:
        with open(path, 'w') as file:
            json.dump(user_config, file)
            print("\033[37;44m INFO \033[0m Config file successfuly created in '" + path + "'")
    except:
        print("\033[37;41m ERROR \033[0m Unable to create config file")
        exit(1)

def get_user_config(path=DEFAULT_CONFIG_FILE):
    try:
        with open(path, 'r') as file:
            user_config = json.load(file)
            if user_config[USER_IDENTIFIER] and user_config[TOKEN_IDENTIFIER] and user_config[GIT_URL_IDENTIFIER] and user_config[BLIH_URL_IDENTIFIER]:
                return user_config
    except:
        pass
    print('\033[37;41m ERROR \033[0m Invalid config file \'' + path + '\'')
    print('> \'eiota config\' to create a valid config file.')
    exit(1)

def user_config_info(user_config):
    print_logo()
    print('\033[1;33mCONFIGURATION:\033[0m', end='\n\n')
    print('User:            ', user_config[USER_IDENTIFIER])
    print('Token registered:', 'Yes' if user_config[USER_IDENTIFIER] else 'No')
    print('Git URL:         ', user_config[GIT_URL_IDENTIFIER])
    print('Blih URL:        ', user_config[BLIH_URL_IDENTIFIER], end='\n\n')

def blih_cmd(user_config, cmd):
    return 'blih -u ' + user_config[USER_IDENTIFIER] + ' -t ' + user_config[TOKEN_IDENTIFIER] + ' ' + cmd

def get_acl(user_config, repo):
    try:
        infos = str(subprocess.check_output(blih_cmd(user_config, 'repository getacl ' + repo), shell=True), 'utf-8')
    except:
        print('\033[37;44m INFO \033[0m Invalid repository or no ACLs')
        return
    infos = infos.split('\n')
    infos.pop()
    max_user_size = 0
    max_acl_size = 0
    for i in range(len(infos)):
        infos[i] = infos[i].split(':')
        if (len(infos[i][0]) > max_user_size):
            max_user_size = len(infos[i][0])
        if (len(infos[i][1]) > max_acl_size):
            max_acl_size = len(infos[i][1])
    print((' ' * int(max_user_size / 2)) + ' \033[1;36mUSER\033[0m ' + (' ' * int(max_user_size / 2)) + '\033[1;33m|\033[0m' + (' ' * int(max_acl_size / 2)) + ' \033[1;36mACLs\033[0m ' + (' ' * int(max_acl_size / 2)))
    max_user_part = int(max_user_size / 2) * 2 + 6
    max_acl_part = int(max_acl_size / 2) * 2 + 6
    print('\033[1;33m' + ('‾' * max_user_part) + '|' + ('‾' * max_acl_part) + '\033[0m')
    for element in infos:
        print((' ' * int((max_user_part - len(element[0])) / 2)) + element[0] + (' ' * int((max_user_part - len(element[0])) / 2 - (len(element[0]) % 2 == 0))) + ' \033[1;33m|\033[0m' + (' ' * int((max_acl_part - len(element[1])) / 2)) + element[1])

def set_acl(user_config, repo, acls):
    return os.system(blih_cmd(user_config, 'repository setacl ' + repo + ' ' + acls))

def ls(user_config, opt=None):
    repo_list = str(subprocess.check_output(blih_cmd(user_config, 'repository list'), shell=True), 'utf-8')
    repo_list = repo_list[:-1].split('\n')
    for repo in repo_list:
        print(repo)

def clone(user_config, repo):
    print('Cloning from \'' + user_config[GIT_URL_IDENTIFIER] + ':' + user_config[USER_IDENTIFIER] + '\'')
    return os.system('git clone ' + user_config[GIT_URL_IDENTIFIER] + ':' + user_config[USER_IDENTIFIER] + '/' + repo)

def info(user_config, repo, out=True):
    try:
        raw_output = subprocess.check_output(blih_cmd(user_config, 'repository info ' + repo), shell=True)
    except:
        print('\033[37;41m ERROR \033[0m Invalid repository \'' + repo + '\'')
        return
    infos = json.loads(str(raw_output, 'utf-8').replace("\'", "\""))
    if out:
        print_logo()
        print('\033[1;33mNAME:\033[1;37m', repo, '\n')
        if infos['url']:
            print('\033[1;33m          Url:\033[0m', infos['url'])
        if infos['uuid']:
            print('\033[1;33m         UUID:\033[0m', infos['uuid'])
        if infos['description']:
            print('\033[1;33m  Description:\033[0m', infos['description'])
        if infos['public']:
            print('\033[1;33m       Public:\033[0m', infos['public'])
        if infos['creation_time']:
            print('\033[1;33mCreation date:\033[0m', datetime.datetime.fromtimestamp(int(infos['creation_time'])).strftime('%Y-%m-%d %H:%M:%S'))
        print()
        get_acl(user_config, repo)
        print('\n\033[2m© Louis Kleiver (louis.kleiver@epitech.eu)\033[0m')
    return infos

def create(user_config, repo):
    try:
        raw_output = subprocess.check_output(blih_cmd(user_config, 'repository create ' + repo), shell=True)
    except:
        print('\033[37;41m ERROR \033[0m Unable to create \'' + repo + '\'')
        exit(1)
    print('\033[37;44m INFO \033[0m', str(raw_output, 'utf-8'), end='')

def delete(user_config, repo):
    try:
        raw_output = subprocess.check_output(blih_cmd(user_config, 'repository delete ' + repo), shell=True)
    except:
        print('\033[37;41m ERROR \033[0m Invalid repository \'' + repo + '\'')
        exit(1)
    print('\033[37;44m INFO \033[0m', str(raw_output, 'utf-8'), end='')

def usage(cmd=None):
    print_logo()
    if cmd in ('acl', 'ACL', 'acls', 'ACLs', 'rights'):
        print('\033[1;33mUSAGE:\033[0m eiota ' + cmd + ' [command] arguments...', end='\n\n')
        print('\033[1;33mCOMMANDS:\033[0m')
        print('    get <repo> <acl>  - Get repository ACLs')
        print('    set <repo> <acl>  - Set repository ACLs')
    elif cmd == 'getacl':
        print('\033[1;33mUSAGE:\033[0m eiota get acl <repo> <acl>', end='\n\n')
        print('\033[1;33mDESCRIPTION:\033[0m Get the repository ACLs')
    elif cmd == 'setacl':
        print('\033[1;33mUSAGE:\033[0m eiota set acl <repo> <acl>', end='\n\n')
        print('\033[1;33mDESCRIPTION:\033[0m Set the repository ACLs')
    elif cmd == 'config':
        print('\033[1;33mUSAGE:\033[0m eiota config (<output file>/info)', end='\n\n')
        print('\033[1;33mDESCRIPTION:\033[0m')
        print('    info:           - Display actual configuration.')
        print('    <output file>:  - Create a config in the <output file>.')
        print('                      The <output file> is \033[2m\'' + DEFAULT_CONFIG_FILE + '\'\033[0m by default.')
    elif cmd == 'clone':
        print('\033[1;33mUSAGE:\033[0m eiota clone <repo>', end='\n\n')
        print('\033[1;33mDESCRIPTION:\033[0m Clone the defined repository <repo>.')
    elif cmd == 'ls':
        print('\033[1;33mUSAGE:\033[0m eiota ls', end='\n\n')
        print('\033[1;33mDESCRIPTION:\033[0m List every repository of the user.')
    elif cmd == 'new':
        print('\033[1;33mUSAGE:\033[0m eiota new <repo>', end='\n\n')
        print('\033[1;33mDESCRIPTION:\033[0m Create a new repository created <repo>.')
    elif cmd == 'rm':
        print('\033[1;33mUSAGE:\033[0m eiota rm <repo>', end='\n\n')
        print('\033[1;33mDESCRIPTION:\033[0m Remove a repository <repo>.')
    elif cmd == 'info':
        print('\033[1;33mUSAGE:\033[0m eiota info <repo>', end='\n\n')
        print('\033[1;33mDESCRIPTION:\033[0m Display repository informations.')
    else:
        print('\033[1;33mUSAGE:\033[0m eiota [command] arguments...', end='\n\n')
        print('\033[1;33mCOMMANDS:\033[0m')
        print('    help              - Display this help message')
        print('    config            - Setup the config file')
        print('    ls                - Display every user repository')
        print('    new <name>        - Create a new repository')
        print('    clone <name>      - Clone the repository')
        print('    rm <name>         - Remove the repository')
        print('    info <name>       - Display repository informations')
        print('    acl (get/set)     - Edit the repository ACLs')
    print('\n\033[2m© Louis Kleiver (louis.kleiver@epitech.eu)\033[0m')

if __name__ == "__main__":
    if len(sys.argv) == 1:
        if not os.path.exists(DEFAULT_CONFIG_FILE):
            set_user_config()
        else:
            usage()
        exit(0)
    if not (len(sys.argv) == 2 and sys.argv[1] == 'config'):
        user_config = get_user_config()
    if len(sys.argv) == 2:
        if sys.argv[1] == 'help':
            usage()
        elif sys.argv[1] == 'clone':
            usage('clone')
        elif sys.argv[1] == 'new' or sys.argv[1] == 'create':
            usage('new')
        elif sys.argv[1] == 'new' or sys.argv[1] == 'create' or sys.argv[1] == 'delete':
            usage('rm')
        elif sys.argv[1] == 'info':
            usage('info')
        elif sys.argv[1] == 'ls' or sys.argv[1] == 'list':
            ls(user_config)
        elif sys.argv[1] == 'config':
            set_user_config()
        elif sys.argv[1] == 'getacl':
            usage('getacl')
        elif sys.argv[1] == 'setacl':
            usage('setacl')
        elif sys.argv[1] == 'whoami':
            print_logo()
            print('\n\033[1;33mHello\033[1;37m', user_config[USER_IDENTIFIER], '\033[0m')
            print('\033[2mYou can type \'eiota config info\' to get more informations\033[0m\n')
        else:
            usage()
    elif len(sys.argv) == 3:
        if sys.argv[1] == 'help':
            usage(sys.argv[2])
        elif sys.argv[1] == 'clone':
            if sys.argv[2] == 'help':
                usage('clone')
            else:
                clone(user_config, sys.argv[2])
        elif (sys.argv[1] == 'ls' or sys.argv[1] == 'list') and sys.argv[2] == 'help':
            usage('ls')
        elif sys.argv[1] == 'new' or sys.argv[1] == 'create':
            if sys.argv[2] == 'help':
                usage('new')
            else:
                create(user_config, sys.argv[2])
        elif sys.argv[1] == 'rm' or sys.argv[1] == 'delete' or sys.argv[1] == 'remove':
            if sys.argv[2] == 'help':
                usage('rm')
            else:
                delete(user_config, sys.argv[2])
        elif sys.argv[1] == 'info':
            if sys.argv[2] == 'help':
                usage('info')
            else:
                info(user_config, sys.argv[2])
        elif sys.argv[1] == 'config':
            if sys.argv[2] == 'help':
                usage('config')
            if sys.argv[2] == 'info':
                user_config_info(user_config)
            else:
                set_user_config(sys.argv[2])
        elif sys.argv[1] == 'getacl' or sys.argv[2] == 'help':
            usage('getacl')
        elif sys.argv[1] == 'setacl' or sys.argv[2] == 'help':
            usage('setacl')
        elif (sys.argv[1] in ('acl', 'ACL', 'acls', 'ACLs', 'rights') and sys.argv[2] == 'get') or (sys.argv[2] in ('acl', 'ACL', 'acls', 'ACLs', 'rights') and sys.argv[1] == 'get'):
            usage('getacl')
        elif (sys.argv[1] in ('acl', 'ACL', 'acls', 'ACLs', 'rights') and sys.argv[2] == 'set') or (sys.argv[2] in ('acl', 'ACL', 'acls', 'ACLs', 'rights') and sys.argv[1] == 'set'):
            usage('setacl')
        elif sys.argv[1] in ('acl', 'ACL', 'acls', 'ACLs', 'rights'):
            get_acl(user_config ,sys.argv[2])
        else:
            usage()
    elif len(sys.argv) == 4:
        if ((sys.argv[1] in ('acl', 'ACL', 'acls', 'ACLs', 'rights') and sys.argv[2] == 'get') or sys.argv[2] in ('acl', 'ACL', 'acls', 'ACLs', 'rights') and sys.argv[1] == 'get'):
            get_acl(user_config, sys.argv[3])
        else:
            usage()
    elif len(sys.argv) == 5:
        if ((sys.argv[1] in ('acl', 'ACL', 'acls', 'ACLs', 'rights') and sys.argv[2] == 'set') or sys.argv[2] in ('acl', 'ACL', 'acls', 'ACLs', 'rights') and sys.argv[1] == 'set'):
            set_acl(user_config, sys.argv[3], sys.argv[4])
        else:
            usage()
    else:
        usage()
