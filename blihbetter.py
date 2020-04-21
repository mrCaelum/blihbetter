#!/usr/bin/env python3

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
import curses
from curses.textpad import Textbox, rectangle

BLIHBETTER_VERSION = '2.4.0'
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
    print('   ___  ___ __     ___      __  __         ')
    print('  / _ )/ (_) /    / _ )___ / /_/ /____ ____')
    print(' / _  / / / _ \  / _  / -_) __/ __/ -_) __/')
    print('/____/_/_/_//_/ /____/\__/\__/\__/\__/_/   ')
    print('\033[0m')

def sign_data(user_config, data=None):
    signature = hmac.new(bytes(user_config[TOKEN_IDENTIFIER], 'utf8'), msg=bytes(user_config[USER_IDENTIFIER], 'utf8'), digestmod=hashlib.sha512)
    if data:
        signature.update(bytes(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')), 'utf8'))
    signed_data = {'user' : user_config[USER_IDENTIFIER], 'signature' : signature.hexdigest()}
    if data != None:
        signed_data['data'] = data
    return signed_data

def blih_request(user_config, resource, method='GET', content_type='application/json', data=None, url=None, gui=False):
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
        print(gui)
        print(e.code)
        if gui and e.code == 404 and data['error'] == 'No ACLs':
            return (404, 'No ACLs', 'No ACLs', 'No ACLs')
        if gui:
            gui_exit()
        print("\033[37;41m ERROR \033[0m HTTP Error", str(e.code), ":", data['error'])
        sys.exit(e.code)
    if f.status == 200:
        try:
            data = json.loads(f.read().decode('utf8'))
        except:
            print("\033[37;41m ERROR \033[0m Can't decode data, aborting")
            if gui:
                gui_exit()
            sys.exit(1)
        return (f.status, f.reason, f.info(), data)
    print('\033[37;41m ERROR \033[0m Unknown error')
    if gui:
        gui_exit()
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
        user_config[USER_AGENT_IDENTIFIER] = input('Blih user agent (' + DEFAULT_USER_AGENT + '): ')
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
    print('> \'blihbetter config\' to create a valid config file.')
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

def gui_init():
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_CYAN)
    curses.curs_set(0)
    return (stdscr)

def gui_print_header(stdscr):
    stdscr.addstr(0, 0, '   ___  ___ __     ___      __  __         ', curses.color_pair(1))
    stdscr.addstr(1, 0, '  / _ )/ (_) /    / _ )___ / /_/ /____ ____', curses.color_pair(1))
    stdscr.addstr(2, 0, ' / _  / / / _ \  / _  / -_) __/ __/ -_) __/', curses.color_pair(1))
    stdscr.addstr(3, 0, '/____/_/_/_//_/ /____/\__/\__/\__/\__/_/   ', curses.color_pair(1))

def gui_info(stdscr, message):
    stdscr.clear()
    gui_print_header(stdscr)
    stdscr.addstr(6, 0, ' INFO ', curses.color_pair(4))
    stdscr.addstr(6, 7, message)
    stdscr.refresh()
    stdscr.getch()

def gui_list(stdscr, menu_list, x, y, width=18, heigth=14, pos=0, view_pos=0, loop=True, selection=True, print_only=False):
    return_value = 'quit'
    rectangle(stdscr, y, x, y + heigth, x + width)
    while True:
        for i in range(0, len(menu_list) if len(menu_list) <= heigth - 1 else heigth - 1):
            stdscr.addstr(y + 1 + i, x + 1, menu_list[i + view_pos][0:width-1] + ' ' * ((width - 1) - len(menu_list[i + view_pos])), curses.A_REVERSE if (selection and pos == i + view_pos) else 0)
        stdscr.refresh()
        if print_only:
            return ('', pos, view_pos)
        c = stdscr.getch()
        if not loop:
            return (c, pos, view_pos)
        if c == ord('q') or c == curses.KEY_LEFT or c == 27:
            return_value = 'quit'
            break
        elif c == curses.KEY_UP:
            if pos == 0:
                pos = len(menu_list) - 1
                if len(menu_list) > heigth:
                    view_pos = len(menu_list) - heigth + 1
            else:
                if pos - view_pos == 0:
                    view_pos -= 1
                pos -= 1
        elif c == curses.KEY_DOWN:
            if pos == len(menu_list) - 1:
                pos = 0
                view_pos = 0
            else:
                if pos - view_pos == heigth - 2:
                    view_pos += 1
                pos += 1
        elif c == ord('\n') or c == curses.KEY_RIGHT:
            return (menu_list[pos], pos, view_pos)
    for i in range(y, y + heigth + 1):
        stdscr.addstr(i, x, ' ' * (width + 1))
    return (return_value, pos, view_pos)

def gui_acl_add(user_config, stdscr, repo, buser='', r=False, w=False, a=False, canBeDeleted=False):
    user = buser
    max_select = (6 if canBeDeleted else 5)
    selection = 0
    stdscr.clear()
    gui_print_header(stdscr)
    stdscr.addstr(6, 1, 'USER:', (curses.color_pair(3) | curses.A_BOLD) if selection == 0 else curses.color_pair(3))
    stdscr.addstr(8, 6, ' READ ', (curses.A_BOLD if selection == 1 else curses.A_NORMAL) | (curses.color_pair(4) if r else curses.COLOR_WHITE))
    stdscr.addstr(8, 14, ' WRITE ', (curses.A_BOLD if selection == 2 else curses.A_NORMAL) | (curses.color_pair(4) if w else curses.COLOR_WHITE))
    stdscr.addstr(8, 23, ' ADMIN ', (curses.A_BOLD if selection == 3 else curses.A_NORMAL) | (curses.color_pair(4) if a else curses.COLOR_WHITE))
    stdscr.addstr(10, 4, ' CANCEL ', (curses.color_pair(4) | curses.A_BOLD) if selection == 4 else curses.A_NORMAL)
    stdscr.addstr(10, 16, ' SAVE ' if canBeDeleted else ' ADD ', (curses.color_pair(4) | curses.A_BOLD) if selection == 5 else curses.A_NORMAL)
    if canBeDeleted:
        stdscr.addstr(10, 25, ' REMOVE ', (curses.color_pair(4) | curses.A_BOLD) if selection == 6 else curses.A_NORMAL)
    stdscr.addstr(6, 7, user)
    while True:
        cmd = stdscr.getch()
        if cmd == 27:
            return
        elif cmd == curses.KEY_UP:
            selection = (4 if selection == 0 else (0 if selection < 4 else selection - 3))
            if selection > max_select:
                selection -= 1
        elif cmd == curses.KEY_DOWN:
            selection = (0 if selection > 3 else (1 if selection == 0 else selection + 3))
            if selection > max_select:
                selection -= 1
        elif cmd == curses.KEY_LEFT:
            selection = (max_select if selection == 0 else selection - 1)
        elif cmd == curses.KEY_RIGHT:
            selection = (0 if selection == max_select else selection + 1)
        elif cmd == curses.KEY_ENTER or cmd == 10 or cmd == 13 or cmd == ord(' '):
            if selection == 1:
                r = not r
            elif selection == 2:
                w = not w
            elif selection == 3:
                a = not a
            elif selection == 4 and cmd != ord(' '):
                return
            elif selection == 5 and cmd != ord(' '):
                break
            elif selection == 6 and cmd != ord(' '):
                r = False
                w = False
                a = False
                break
        elif buser == '' and selection == 0 and (str(chr(cmd)).isalnum() or chr(cmd) == '.' or chr(cmd) == '@' or chr(cmd) == '-' or chr(cmd) == '_') and len(user) < 64:
            user += str(chr(cmd))
        elif buser == '' and cmd == ord('\x7f'):
            user = user[:-1]
        stdscr.clear()
        gui_print_header(stdscr)
        stdscr.addstr(6, 1, 'USER:', (curses.color_pair(3) | curses.A_BOLD) if selection == 0 else curses.color_pair(3))
        stdscr.addstr(8, 6, ' READ ', (curses.A_BOLD if selection == 1 else curses.A_NORMAL) | (curses.color_pair(4) if r else curses.COLOR_WHITE))
        stdscr.addstr(8, 14, ' WRITE ', (curses.A_BOLD if selection == 2 else curses.A_NORMAL) | (curses.color_pair(4) if w else curses.COLOR_WHITE))
        stdscr.addstr(8, 23, ' ADMIN ', (curses.A_BOLD if selection == 3 else curses.A_NORMAL) | (curses.color_pair(4) if a else curses.COLOR_WHITE))
        stdscr.addstr(10, 4, ' CANCEL ', (curses.color_pair(4) | curses.A_BOLD) if selection == 4 else curses.A_NORMAL)
        stdscr.addstr(10, 16, ' SAVE ' if canBeDeleted else ' ADD ', (curses.color_pair(4) | curses.A_BOLD) if selection == 5 else curses.A_NORMAL)
        if canBeDeleted:
            stdscr.addstr(10, 24, ' REMOVE ', (curses.color_pair(4) | curses.A_BOLD) if selection == 6 else curses.A_NORMAL)
        stdscr.addstr(6, 7, user)
    acls = '' + ('r' if r else '') + ('w' if w else '') + ('a' if a else '')
    status, reason, headers, data = blih_request(user_config, '/repository/' + repo + '/acls', method='POST', data={'user': user, 'acl': acls}, gui=True)
    gui_info(stdscr, data['message'])

def gui_repo(user_config, stdscr, repo):
    pos = 0
    view_pos = 0
    while True:
        status, reason, headers, data = blih_request(user_config, '/repository/' + repo, method='GET', gui=True)
        repo_data = data['message']
        stdscr.clear()
        gui_print_header(stdscr)
        stdscr.addstr(6, 1, 'NAME:', curses.color_pair(3) | curses.A_BOLD)
        stdscr.addstr(6, 7, repo)
        stdscr.addstr(8, 12, "Url:", curses.color_pair(3) | curses.A_BOLD)
        stdscr.addstr(9, 11, "UUID:", curses.color_pair(3) | curses.A_BOLD)
        stdscr.addstr(10, 4, "Description:", curses.color_pair(3) | curses.A_BOLD)
        stdscr.addstr(11, 9, "Public:", curses.color_pair(3) | curses.A_BOLD)
        stdscr.addstr(12, 2, "Creation date:", curses.color_pair(3) | curses.A_BOLD)
        stdscr.addstr(8, 17, repo_data['url'] if repo_data['url'] else '???')
        stdscr.addstr(9, 17, repo_data['uuid'] if repo_data['uuid'] else '???')
        stdscr.addstr(10, 17, repo_data['description'] if repo_data['description'] else '???')
        stdscr.addstr(11, 17, repo_data['public'] if repo_data['public'] else '???')
        stdscr.addstr(12, 17, datetime.datetime.fromtimestamp(int(repo_data['creation_time'])).strftime('%Y-%m-%d %H:%M:%S') if repo_data['creation_time'] else '???')
        status, reason, headers, data = blih_request(user_config, '/repository/' + repo + '/acls', method='GET', gui=True)
        acl_users = []
        if type(data) != type(""):
            for i in data.keys():
                acl_users.append(i)
        stdscr.addstr(14, 28, 'ACLs:', curses.color_pair(3))
        gui_list(stdscr, acl_users, 26, 15, width=32, heigth=5, selection=False, print_only=True)
        stdscr.refresh()
        cmd, pos, view_pos = gui_list(stdscr, ['add acls', 'edit acls', 'delete repository'], 1, 15, width=19, heigth=5, pos=pos, view_pos=view_pos)
        if cmd == 'quit':
            return ''
        if cmd == 'add acls':
            gui_acl_add(user_config, stdscr, repo)
        elif cmd == 'edit acls':
            acls_pos = 0
            acls_view_pos = 0
            while len(acl_users) > 0:
                stdscr.clear()
                gui_print_header(stdscr)
                stdscr.addstr(6, 1, 'NAME:', curses.color_pair(3) | curses.A_BOLD)
                stdscr.addstr(6, 7, repo)
                stdscr.addstr(8, 12, "Url:", curses.color_pair(3) | curses.A_BOLD)
                stdscr.addstr(9, 11, "UUID:", curses.color_pair(3) | curses.A_BOLD)
                stdscr.addstr(10, 4, "Description:", curses.color_pair(3) | curses.A_BOLD)
                stdscr.addstr(11, 9, "Public:", curses.color_pair(3) | curses.A_BOLD)
                stdscr.addstr(12, 2, "Creation date:", curses.color_pair(3) | curses.A_BOLD)
                stdscr.addstr(8, 17, repo_data['url'] if repo_data['url'] else '???')
                stdscr.addstr(9, 17, repo_data['uuid'] if repo_data['uuid'] else '???')
                stdscr.addstr(10, 17, repo_data['description'] if repo_data['description'] else '???')
                stdscr.addstr(11, 17, repo_data['public'] if repo_data['public'] else '???')
                stdscr.addstr(12, 17, datetime.datetime.fromtimestamp(int(repo_data['creation_time'])).strftime('%Y-%m-%d %H:%M:%S') if repo_data['creation_time'] else '???')
                stdscr.addstr(14, 28, 'ACLs:', curses.color_pair(3))
                gui_list(stdscr, ['add acls', 'edit acls', 'delete repository'], 1, 15, width=19, heigth=5, pos=pos, view_pos=view_pos, print_only=True)
                acls_cmd, acls_pos, acls_view_pos = gui_list(stdscr, acl_users, 26, 15, width=32, heigth=5, pos=acls_pos, view_pos=acls_view_pos, print_only=True)
                r = False
                w = False
                a = False
                for el in data.keys():
                    if acl_users[acls_pos] == el and ('r' in data[el]):
                        r = True
                    if acl_users[acls_pos] == el and ('w' in data[el]):
                        w = True
                    if acl_users[acls_pos] == el and ('a' in data[el]):
                        a = True
                stdscr.addstr(16, 62, ' READ ', (curses.A_BOLD | curses.color_pair(4) if r else curses.A_NORMAL))
                stdscr.addstr(17, 62, ' WRITE ', (curses.A_BOLD | curses.color_pair(4) if w else curses.A_NORMAL))
                stdscr.addstr(18, 62, ' ADMIN ', (curses.A_BOLD | curses.color_pair(4) if a else curses.A_NORMAL))
                stdscr.refresh()
                acls_cmd = stdscr.getch()
                if acls_cmd == ord('q') or acls_cmd == curses.KEY_LEFT or acls_cmd == 27:
                    break
                elif acls_cmd == curses.KEY_UP:
                    if acls_pos == 0:
                        acls_pos = len(acl_users) - 1
                        if len(acl_users) > 5:
                            acls_view_pos = len(acl_users) - 6
                    else:
                        if acls_pos - acls_view_pos == 0:
                            acls_view_pos -= 1
                        acls_pos -= 1
                elif acls_cmd == curses.KEY_DOWN:
                    if acls_pos == len(acl_users) - 1:
                        acls_pos = 0
                        acls_view_pos = 0
                    else:
                        if acls_pos - acls_view_pos == 3:
                            acls_view_pos += 1
                        acls_pos += 1
                else:
                    gui_acl_add(user_config, stdscr, repo, buser=acl_users[acls_pos], r=r, w=w, a=a, canBeDeleted=True)
                    break
        elif cmd == 'delete repository':
            selection = False
            while True:
                stdscr.clear()
                gui_print_header(stdscr)
                stdscr.addstr(8, 2, 'You really want to delete \"' + repo + '\" ?', curses.A_BOLD)
                stdscr.addstr(10, 6, ' NO ', (curses.color_pair(4) | curses.A_BOLD) if not selection else curses.A_NORMAL)
                stdscr.addstr(10, 14, ' YES ', (curses.color_pair(4) | curses.A_BOLD) if selection else curses.A_NORMAL)
                stdscr.refresh()
                cmd = stdscr.getch()
                if cmd == curses.KEY_LEFT or cmd == curses.KEY_RIGHT or cmd == curses.KEY_UP or cmd == curses.KEY_DOWN:
                    selection = not selection
                elif cmd == ord('\n'):
                    if selection:
                        status, reason, headers, data = blih_request(user_config, '/repository/' + repo, method='DELETE', gui=True)
                        gui_info(stdscr, data['message'])
                        return 'quit'
                    else:
                        break
                elif cmd == 27:
                    break

def gui_repo_list(user_config, stdscr):
    cmd = ''
    status, reason, headers, data = blih_request(user_config, '/repositories', method='GET', gui=True)
    repositories = []
    pos = 0
    view_pos = 0
    for repo in data['repositories']:
        repositories.append(repo)
    repositories.sort()
    while cmd != 'quit':
        stdscr.clear()
        gui_print_header(stdscr)
        gui_list(stdscr, ['new repository', 'repositories', 'quit'], 0, 6, pos=1, print_only=True)
        cmd, pos, view_pos = gui_list(stdscr, repositories, 20, 6, 42, pos=pos, view_pos=view_pos)
        if cmd != '' and cmd != 'quit':
            cmd = gui_repo(user_config, stdscr, cmd)

def gui_repo_new(user_config, stdscr):
    name = ''
    selection = 0
    stdscr.clear()
    gui_print_header(stdscr)
    stdscr.addstr(6, 1, 'REPOSITORY NAME:', (curses.color_pair(3) | curses.A_BOLD) if selection < 2 else curses.color_pair(3))
    stdscr.addstr(8, 4, ' CANCEL ', (curses.color_pair(4) | curses.A_BOLD) if selection == 2 else curses.A_NORMAL)
    stdscr.addstr(8, 16, ' CREATE ', (curses.color_pair(4) | curses.A_BOLD) if selection == 3 else curses.A_NORMAL)
    stdscr.addstr(6, 18, name)
    while True:
        cmd = stdscr.getch()
        if cmd == 27:
            return
        elif cmd == curses.KEY_UP or cmd == curses.KEY_DOWN:
            selection += (2 if selection < 2 else -2)
        elif cmd == curses.KEY_LEFT:
            selection = (0 if selection == 2 else (3 if selection < 2 else 2))
        elif cmd == curses.KEY_RIGHT:
            selection = (0 if selection == 3 else (2 if selection < 2 else 3))
        elif cmd == curses.KEY_ENTER or cmd == 10 or cmd == 13:
            if selection < 2:
                selection = 3
            elif selection == 2:
                return
            elif selection == 3:
                break
        elif selection < 2 and (str(chr(cmd)).isalnum() or chr(cmd) == '-' or chr(cmd) == '_') and len(name) < 64:
            name += str(chr(cmd))
        elif cmd == ord('\x7f'):
            name = name[:-1]
        stdscr.clear()
        gui_print_header(stdscr)
        stdscr.addstr(6, 1, 'REPOSITORY NAME:', (curses.color_pair(3) | curses.A_BOLD) if selection < 2 else curses.color_pair(3))
        stdscr.addstr(8, 4, ' CANCEL ', (curses.color_pair(4) | curses.A_BOLD) if selection == 2 else curses.A_NORMAL)
        stdscr.addstr(8, 16, ' CREATE ', (curses.color_pair(4) | curses.A_BOLD) if selection == 3 else curses.A_NORMAL)
        stdscr.addstr(6, 18, name)
    status, reason, headers, data = blih_request(user_config, '/repositories', method='POST', data={'name': name, 'type': 'git'}, gui=True)
    gui_info(stdscr, data['message'])

def gui(user_config):
    stdscr = gui_init()
    gui_print_header(stdscr)
    cmd = ''
    pos = 0
    view_pos = 0
    while cmd != 'quit':
        stdscr.clear()
        gui_print_header(stdscr)
        cmd, pos, view_pos = gui_list(stdscr, ['new repository', 'repositories', 'quit'], 0, 6, pos=pos, view_pos=0)
        if (cmd == 'new repository'):
            gui_repo_new(user_config, stdscr)
        elif (cmd == 'repositories'):
            gui_repo_list(user_config, stdscr)
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()

def gui_exit():
    curses.nocbreak()
    curses.echo()
    curses.endwin()

def usage(cmd=None):
    print_logo()
    if cmd in ('acl', 'ACL', 'acls', 'ACLs', 'rights'):
        print('\033[1;33mUSAGE:\033[0m blihbetter ' + cmd + ' [command] arguments...', end='\n\n')
        print('\033[1;33mCOMMANDS:\033[0m')
        print('    get <repo> <acl>  - Get repository ACLs')
        print('    set <repo> <acl>  - Set repository ACLs')
    elif cmd == 'getacl':
        print('\033[1;33mUSAGE:\033[0m blihbetter get acl <repo>', end='\n\n')
        print('\033[1;33mDESCRIPTION:\033[0m Get the repository ACLs')
    elif cmd == 'setacl':
        print('\033[1;33mUSAGE:\033[0m blihbetter set acl <repo> <user> <acl>', end='\n\n')
        print('\033[1;33mDESCRIPTION:\033[0m Set the repository ACLs')
    elif cmd == 'config':
        print('\033[1;33mUSAGE:\033[0m blihbetter config (<output file>/info)', end='\n\n')
        print('\033[1;33mDESCRIPTION:\033[0m')
        print('    info:           - Display actual configuration.')
        print('    <output file>:  - Create a config in the <output file>.')
        print('                      The <output file> is \033[2m\'' + DEFAULT_CONFIG_FILE + '\'\033[0m by default.')
    elif cmd == 'clone':
        print('\033[1;33mUSAGE:\033[0m blihbetter clone <repo>', end='\n\n')
        print('\033[1;33mDESCRIPTION:\033[0m Clone the defined repository <repo>.')
    elif cmd == 'ls':
        print('\033[1;33mUSAGE:\033[0m blihbetter ls', end='\n\n')
        print('\033[1;33mDESCRIPTION:\033[0m List every repository of the user.')
    elif cmd == 'create':
        print('\033[1;33mUSAGE:\033[0m blihbetter create <repo>', end='\n\n')
        print('\033[1;33mDESCRIPTION:\033[0m Create a new repository <repo>.')
    elif cmd == 'new':
        print('\033[1;33mUSAGE:\033[0m blihbetter new <repo>', end='\n\n')
        print('\033[1;33mDESCRIPTION:\033[0m Create a new repository <repo> with the default Epitech configuration.')
    elif cmd == 'rm':
        print('\033[1;33mUSAGE:\033[0m blihbetter rm <repo>', end='\n\n')
        print('\033[1;33mDESCRIPTION:\033[0m Remove a repository <repo>.')
    elif cmd == 'info':
        print('\033[1;33mUSAGE:\033[0m blihbetter info <repo>', end='\n\n')
        print('\033[1;33mDESCRIPTION:\033[0m Display repository informations.')
    elif cmd == 'sshkey':
        print('\033[1;33mUSAGE:\033[0m blihbetter ' + cmd + ' [command] arguments...', end='\n\n')
        print('\033[1;33mCOMMANDS:\033[0m')
        print('    list               - List ssh keys')
        print('    upload <filename>  - Upload ssh key from a file')
        print('    rm <key name>      - Set repository ACLs')
    else:
        print('\033[0;32mv' + BLIHBETTER_VERSION + '\033[0m', end='\n\n')
        print('\033[1;33mUSAGE:\033[0m blihbetter [command] arguments...', end='\n\n')
        print('\033[1;33mCOMMANDS:\033[0m')
        print('    help               - Display this help message')
        print('    config             - Setup the config file')
        print('    config info        - View the config file')
        print('    ping               - Ask to blih who you are')
        print('    ls                 - Display every user repository')
        print('    create <name>      - Create a new repository')
        print('    new <name>         - Create a new repository with default Epitech config')
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
            gui(get_user_config())
        exit(0)
    if not (len(sys.argv) == 2 and sys.argv[1] == 'config'):
        user_config = get_user_config()
    if len(sys.argv) == 2:
        if sys.argv[1] == 'help':
            usage()
        elif sys.argv[1] == 'ping':
            ping(user_config)
        elif sys.argv[1] == 'clone' or sys.argv[1] == 'new' or sys.argv[1] == 'create' or sys.argv[1] == 'info':
            usage(sys.argv[1])
        elif sys.argv[1] == 'rm' or sys.argv[1] == 'delete' or sys.argv[1] == 'remove':
            usage('rm')
        elif sys.argv[1] == 'ls' or sys.argv[1] == 'list':
            ls(user_config)
        elif sys.argv[1] == 'config':
            set_user_config()
        elif sys.argv[1] in ('acl', 'ACL', 'acls', 'ACLs', 'rights'):
            usage('acl')
        elif sys.argv[1] == 'whoami':
            print_logo()
            print('\n\033[1;33mHello\033[1;37m', user_config[USER_IDENTIFIER], '\033[0m')
            print('\033[2mYou can type \'blihbetter config info\' to get more informations\033[0m')
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
        elif sys.argv[1] == 'create':
            if sys.argv[2] == 'help':
                usage('create')
            else:
                create(user_config, sys.argv[2])
        elif sys.argv[1] == 'new':
            if sys.argv[2] == 'help':
                usage('new')
            else:
                create(user_config, sys.argv[2])
                set_acl(user_config, sys.argv[2], 'ramassage-tek', 'r')
                clone(user_config, sys.argv[2])
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
        elif sys.argv[1] == 'getacl':
            get_acl(user_config, sys.argv[2])
        elif sys.argv[1] == 'setacl' and sys.argv[2] == 'help':
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
