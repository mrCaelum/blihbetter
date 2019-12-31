#!/usr/bin/env python

import os
import sys
import subprocess
import json
import hmac
import hashlib
import urllib.request
import urllib.parse
import getpass
import datetime

EIOTA_VERSION = '2.1.0'
USER_IDENTIFIER = 'user'
TOKEN_IDENTIFIER = 'token'
GIT_URL_IDENTIFIER = 'git_url'
BLIH_URL_IDENTIFIER = 'blih_url'
USER_AGENT_IDENTIFIER = 'blih_user_agent'
DEFAULT_CONFIG_FILE = os.path.expanduser("~") + "/.config/epitech/config.json"
DEFAULT_GIT_URL = "git@git.epitech.eu"
DEFAULT_BLIH_URL = "https://blih.epitech.eu/"
DEFAULT_USER_AGENT = 'blih-1.7-win'

def print_logo():
    print('\033[1;36m')
    print('         ________  _________  ')
    print('   ___  /  _/ __ \/_  __/   | ')
    print('  / _ \ / // / / / / / / /| | ')
    print(' /  __// // /_/ / / / / ___ | ')
    print(' \___/___/\____/ /_/ /_/  |_| ')
    print('\033[0m')

def sign_data(user_config, data=None):
    signature = hmac.new(bytes(user_config[TOKEN_IDENTIFIER], 'utf8'), msg=bytes(user_config[USER_IDENTIFIER], 'utf8'), digestmod=hashlib.sha512)
    if data:
        signature.update(bytes(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')), 'utf8'))
    signed_data = {'user' : user_config[USER_IDENTIFIER], 'signature' : signature.hexdigest()}
    if data != None:
        signed_data['data'] = data
    return signed_data

def blih_request(user_config, resource, method='GET', content_type='application/json', data=None, url=None):
    signed_data = sign_data(user_config, data)
    if url:
        req = urllib.request.Request(url=url, method=method, data=bytes(json.dumps(signed_data), 'utf8'))
    else:
        req = urllib.request.Request(url=user_config[BLIH_URL_IDENTIFIER] + resource, method=method, data=bytes(json.dumps(signed_data), 'utf8'))
    req.add_header('Content-Type', content_type)
    req.add_header('User-Agent', user_config[USER_AGENT_IDENTIFIER])
    try:
        f = urllib.request.urlopen(req)
    except urllib.error.HTTPError as e:
        data = json.loads(e.read().decode('utf8'))
        print("\033[37;41m ERROR \033[0m HTTP Error", str(e.code), ":", data['error'])
        sys.exit(e.code)
    if f.status == 200:
        try:
            data = json.loads(f.read().decode('utf8'))
        except:
            print("\033[37;41m ERROR \033[0m Can't decode data, aborting")
            sys.exit(1)
        return (f.status, f.reason, f.info(), data)
    print('\033[37;41m ERROR \033[0m Unknown error')
    sys.exit(1)

def set_user_config(path=DEFAULT_CONFIG_FILE):
    print_logo()
    print('\033[1;33mConfig file generation:\033[0;2m \'' + path + '\'\033[0m', end='\n\n')
    user_config = {}
    try:
        user_config[USER_IDENTIFIER] = input('User: ')
        user_config[TOKEN_IDENTIFIER] = hashlib.sha512(bytes(getpass.getpass(), 'utf8')).hexdigest()
        user_config[GIT_URL_IDENTIFIER] = input('Git url (' + DEFAULT_GIT_URL + '): ')
        user_config[BLIH_URL_IDENTIFIER] = input('Blih url (' + DEFAULT_BLIH_URL + '): ')
        user_config[USER_AGENT_IDENTIFIER] = input('Blih url (' + DEFAULT_USER_AGENT + '): ')
    except:
        print("\n\n\033[37;44m INFO \033[0m Exited")
        exit(0)
    if not user_config[GIT_URL_IDENTIFIER]:
        user_config[GIT_URL_IDENTIFIER] = DEFAULT_GIT_URL
    if not user_config[BLIH_URL_IDENTIFIER]:
        user_config[BLIH_URL_IDENTIFIER] = DEFAULT_BLIH_URL
    if not user_config[USER_AGENT_IDENTIFIER]:
        user_config[USER_AGENT_IDENTIFIER] = DEFAULT_USER_AGENT
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
            if user_config[USER_IDENTIFIER] and user_config[TOKEN_IDENTIFIER] and user_config[GIT_URL_IDENTIFIER] and user_config[BLIH_URL_IDENTIFIER] and user_config[USER_AGENT_IDENTIFIER]:
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
    print('Token registered:', 'Yes' if user_config[TOKEN_IDENTIFIER] else 'No')
    print('Git URL:         ', user_config[GIT_URL_IDENTIFIER])
    print('Blih URL:        ', user_config[BLIH_URL_IDENTIFIER])
    if (user_config[USER_AGENT_IDENTIFIER]):
        print('Blih user agent: ', user_config[USER_AGENT_IDENTIFIER])
    print()

def get_acl(user_config, repo):
    status, reason, headers, data = blih_request(user_config, '/repository/' + repo + '/acls', method='GET')
    max_user_size = 0
    max_acl_size = 0
    for i in data.keys():
        if (len(i) > max_user_size):
            max_user_size = len(i)
        if (len(data[i]) > max_acl_size):
            max_acl_size = len(data[i])
    print((' ' * int(max_user_size / 2)) + ' \033[1;36mUSER\033[0m ' + (' ' * int(max_user_size / 2)) + '\033[1;33m|\033[0m' + (' ' * int(max_acl_size / 2)) + ' \033[1;36mACLs\033[0m ' + (' ' * int(max_acl_size / 2)))
    max_user_part = int(max_user_size / 2) * 2 + 6
    max_acl_part = int(max_acl_size / 2) * 2 + 6
    print('\033[1;33m' + ('‾' * max_user_part) + '|' + ('‾' * max_acl_part) + '\033[0m')
    for i in data.keys():
        print((' ' * int((max_user_part - len(i)) / 2)) + i + (' ' * int((max_user_part - len(i)) / 2 - (len(i) % 2 == 0))) + ' \033[1;33m|\033[0m' + (' ' * int((max_acl_part - len(data[i])) / 2)) + data[i])

def set_acl(user_config, repo, user, acls=''):
    data = {
        'user' : user,
        'acl' : acls
    }
    status, reason, headers, data = blih_request(user_config, '/repository/' + repo + '/acls', method='POST', data=data)
    print('\033[37;44m INFO \033[0m', data['message'])

def ls(user_config, opt=None):
    status, reason, headers, data = blih_request(user_config, '/repositories', method='GET')
    for repository in data['repositories']:
        print(repository)

def clone(user_config, repo):
    print('Cloning from \'' + user_config[GIT_URL_IDENTIFIER] + ':' + user_config[USER_IDENTIFIER] + '\'')
    return os.system('git clone ' + user_config[GIT_URL_IDENTIFIER] + ':' + user_config[USER_IDENTIFIER] + '/' + repo)

def info(user_config, repo, out=True):
    status, reason, headers, data = blih_request(user_config, '/repository/' + repo, method='GET')
    if out:
        print_logo()
        print('\033[1;33mNAME:\033[1;37m', repo, '\n')
        if data['message']['url']:
            print('\033[1;33m          Url:\033[0m', data['message']['url'])
        if data['message']['uuid']:
            print('\033[1;33m         UUID:\033[0m', data['message']['uuid'])
        if data['message']['description']:
            print('\033[1;33m  Description:\033[0m', data['message']['description'])
        if data['message']['public']:
            print('\033[1;33m       Public:\033[0m', data['message']['public'])
        if data['message']['creation_time']:
            print('\033[1;33mCreation date:\033[0m', datetime.datetime.fromtimestamp(int(data['message']['creation_time'])).strftime('%Y-%m-%d %H:%M:%S'))
        print()
        get_acl(user_config, repo)
        print('\n\033[2m© Louis Kleiver (louis.kleiver@gmail.com)\033[0m')
    return data['message']

def create(user_config, repo, description=None):
    data = {
        'name' : repo,
        'type' : 'git'
    }
    if description:
        data['description'] = description
    status, reason, headers, data = blih_request(user_config, '/repositories', method='POST', data=data)
    print('\033[37;44m INFO \033[0m', data['message'])

def delete(user_config, repo):
    status, reason, headers, data = blih_request(user_config, '/repository/' + repo, method='DELETE')
    print('\033[37;44m INFO \033[0m', data['message'])

def sshkey_list(user_config):
    status, reason, headers, data = blih_request(user_config, '/sshkeys', method='GET')
    print()
    for i in data.keys():
        print ('\033[1;33m' + i + '\033[0m')
        print(data[i], end='\n\n')

def sshkey_upload(user_config, filename):
    try:
        file = open(filename, 'r')
    except:
        print("\033[37;41m ERROR \033[0m Can't open file : " + filename)
        sys.exit(1)
    data = {
        'sshkey' : urllib.parse.quote(file.read().strip('\n'))
    }
    file.close()
    status, reason, headers, data = blih_request(user_config, '/sshkeys', method='POST', data=data)
    print('\033[37;44m INFO \033[0m', data['message'])

def sshkey_remove(user_config, sshkey):
    status, reason, headers, data = blih_request(user_config, '/sshkey/' + sshkey, method='DELETE')
    print('\033[37;44m INFO \033[0m', data['message'])

def ping(user_config, to='blih'):
    if to == "blih":
        status, reason, headers, data = blih_request(user_config, '/whoami', method='GET')
        print_logo()
        print('\033[37;42m OK \033[0m Successfuly connected to\033[1m', user_config[BLIH_URL_IDENTIFIER], '\033[0mas\033[1m', data['message'], '\033[0m')
    elif to == "git":
        cmd = subprocess.run(["ssh", user_config[GIT_URL_IDENTIFIER]], check=False, stdout=subprocess.PIPE)
        if cmd.returncode == 128:
            print('\033[37;42m OK \033[0m Successfuly connected to\033[1m', user_config[GIT_URL_IDENTIFIER], '\033[0mas\033[1m', cmd.stdout.decode('utf-8').split(' ')[1].split('!')[0], '\033[0m')
        else:
            print('\033[37;41m ERROR \033[0m Unable to connect (check your ssh key)')
    else:
        print('\033[37;41m ERROR \033[0m Invalid target', to)
        sys.exit(1)

def usage(cmd=None):
    print_logo()
    if cmd in ('acl', 'ACL', 'acls', 'ACLs', 'rights'):
        print('\033[1;33mUSAGE:\033[0m eiota ' + cmd + ' [command] arguments...', end='\n\n')
        print('\033[1;33mCOMMANDS:\033[0m')
        print('    get <repo> <acl>  - Get repository ACLs')
        print('    set <repo> <acl>  - Set repository ACLs')
    elif cmd == 'getacl':
        print('\033[1;33mUSAGE:\033[0m eiota get acl <repo>', end='\n\n')
        print('\033[1;33mDESCRIPTION:\033[0m Get the repository ACLs')
    elif cmd == 'setacl':
        print('\033[1;33mUSAGE:\033[0m eiota set acl <repo> <user> <acl>', end='\n\n')
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
    elif cmd == 'sshkey':
        print('\033[1;33mUSAGE:\033[0m eiota ' + cmd + ' [command] arguments...', end='\n\n')
        print('\033[1;33mCOMMANDS:\033[0m')
        print('    list               - List ssh keys')
        print('    upload <filename>  - Upload ssh key from a file')
        print('    rm <key name>      - Set repository ACLs')
    else:
        print('\033[0;32mv' + EIOTA_VERSION + '\033[0m', end='\n\n')
        print('\033[1;33mUSAGE:\033[0m eiota [command] arguments...', end='\n\n')
        print('\033[1;33mCOMMANDS:\033[0m')
        print('    help               - Display this help message')
        print('    config             - Setup the config file')
        print('    ping               - Ask to blih who you are')
        print('    ls                 - Display every user repository')
        print('    new <name>         - Create a new repository')
        print('    clone <name>       - Clone the repository')
        print('    rm <name>          - Remove the repository')
        print('    info <name>        - Display repository informations')
        print('    acl (get/set)      - Edit the repository ACLs')
        print('    sshkey (add/ls/rm) - Edit the repository ACLs')
        print('\n\033[2m© Louis Kleiver (louis.kleiver@gmail.com)\033[0m')

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
        elif sys.argv[1] == 'ping':
            ping(user_config)
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
        elif sys.argv[1] in ('acl', 'ACL', 'acls', 'ACLs', 'rights'):
            usage('acl')
        elif sys.argv[1] == 'whoami':
            print_logo()
            print('\n\033[1;33mHello\033[1;37m', user_config[USER_IDENTIFIER], '\033[0m')
            print('\033[2mYou can type \'eiota config info\' to get more informations\033[0m')
        else:
            usage()
    elif len(sys.argv) == 3:
        if sys.argv[1] == 'help':
            usage(sys.argv[2])
        elif sys.argv[1] == 'ping':
            ping(user_config, to=sys.argv[2])
        elif sys.argv[1] == 'clone':
            if sys.argv[2] == 'help':
                usage('clone')
            else:
                clone(user_config, sys.argv[2])
        elif sys.argv[1] == 'sshkey' and (sys.argv[2] == 'ls' or sys.argv[2] == 'list'):
            sshkey_list(user_config)
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
        elif sys.argv[1] == 'getacl':
            get_acl(user_config, sys.argv[2])
        else:
            usage()
    elif len(sys.argv) == 4:
        if (sys.argv[1] in ('acl', 'ACL', 'acls', 'ACLs', 'rights') and sys.argv[2] == 'get') or (sys.argv[2] in ('acl', 'ACL', 'acls', 'ACLs', 'rights') and sys.argv[1] == 'get'):
            get_acl(user_config, sys.argv[3])
        elif sys.argv[1] == 'setacl':
            set_acl(user_config, sys.argv[2], sys.argv[3])
        elif sys.argv[1] == 'sshkey' and (sys.argv[2] == 'add' or sys.argv[2] == 'upload'):
            sshkey_upload(user_config, sys.argv[3])
        elif sys.argv[1] == 'sshkey' and (sys.argv[2] == 'rm' or sys.argv[2] == 'remove' or sys.argv[2] == 'delete'):
            sshkey_remove(user_config, sys.argv[3])
        else:
            usage()
    elif len(sys.argv) == 5:
        if (sys.argv[1] in ('acl', 'ACL', 'acls', 'ACLs', 'rights') and sys.argv[2] == 'set') or (sys.argv[2] in ('acl', 'ACL', 'acls', 'ACLs', 'rights') and sys.argv[1] == 'set'):
            set_acl(user_config, sys.argv[3], sys.argv[4])
        elif sys.argv[1] == 'setacl':
            set_acl(user_config, sys.argv[2], sys.argv[3], sys.argv[4])
        else:
            usage()
    elif len(sys.argv) == 6:
        if (sys.argv[1] in ('acl', 'ACL', 'acls', 'ACLs', 'rights') and sys.argv[2] == 'set') or (sys.argv[2] in ('acl', 'ACL', 'acls', 'ACLs', 'rights') and sys.argv[1] == 'set'):
            set_acl(user_config, sys.argv[3], sys.argv[4], sys.argv[5])
        else:
            usage()
    else:
        usage()
