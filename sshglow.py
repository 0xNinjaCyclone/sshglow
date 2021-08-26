#!/usr/bin/python3

import os
import sys
import pty
import socket
import time
from ipaddress import IPv4Network
from optparse import OptionParser

AUTHOR  = "Abdallah Mohamed Elsharif"
VERSION = "1.0"
DefaultCommandExecution = "whoami"

class Color:
    Red     = "\033[0;31m"
    Yellow  = "\033[0;33m"
    Green   = "\033[0;32m"
    White   = "\033[0;37m"
    Blue    = "\033[0;34m"


def register_options():
    parser = OptionParser(version=VERSION)
    parser.add_option('-t','--targets',dest='targets',
            help='Your Target (one ip or more separated by ,) or cidr or range ex(192.168.1.1-10)')
    parser.add_option("-c","--credentials",dest="creds",
            help="Enter creds on or more separated by , ex(user:pass or user2:pass2,user2:pass2) or file with same expression")
    parser.add_option("-d","--delay",dest="delay",help="delay interval in seconds (default 0.5)",default="0.5")
    parser.add_option("-e","--exec",dest="exec",help="Execute command on all machines which you have access on")
    parser.add_option("-r","--no-replicate",action="store_true",dest="replicate",help="Don't replicate execution using multiple users")
    options , _ = parser.parse_args()
    return options

def banner():
    banner = """
███████╗███████╗██╗  ██╗ ██████╗ ██╗      ██████╗ ██╗    ██╗
██╔════╝██╔════╝██║  ██║██╔════╝ ██║     ██╔═══██╗██║    ██║
███████╗███████╗███████║██║  ███╗██║     ██║   ██║██║ █╗ ██║
╚════██║╚════██║██╔══██║██║   ██║██║     ██║   ██║██║███╗██║
███████║███████║██║  ██║╚██████╔╝███████╗╚██████╔╝╚███╔███╔╝
╚══════╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝ ╚═════╝  ╚══╝╚══╝                                                                
""" 
    print(Color.Red + banner.replace('\n','\n\t\t\t'))
    print(f"\t\t\t{Color.Blue} Author  ->  {AUTHOR}{Color.White},  {Color.Green}Version  ->  {VERSION}{Color.White}\n\n")

def ssh_connector(login,passwd,cmd):
    pid, fd = pty.fork()
    if not pid:
        os.execv("/usr/bin/ssh",["/usr/bin/ssh",login,"-o","StrictHostKeyChecking=no",cmd])
    
    while True:
        try:
            output = os.read(fd, 1024).strip()
        except:
            break

        lower = output.lower()
        if b'password:' in lower:
            os.write(fd, (passwd + '\n').encode("utf-8"))
            break

        elif b'are you sure you want to continue connecting' in lower:
            # Adding key to known_hosts
            os.write(fd, b'yes\n')

    output = []
    while True:
        try:
            data = os.read(fd, 1024).strip()
            failed = False
            if b'Permission denied,' in data or b'password:' in data:
                failed = True
                break

            output.append(data.decode('utf-8'))
        except:
            break
    
    if not failed:
        pid , status = os.waitpid(pid, os.WNOHANG)
        return status,''.join(output)
    else:
        return -1 , ""

def find_ssh_servers(hosts):
    servers = []
    for host in hosts:
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.settimeout(0.1)
        if s.connect_ex((host,22)) == 0:
            servers.append(host)
    
    return servers

def handle_targets(targets):
    if ',' in targets:
        targets = targets.split(',')
        
    elif '-' in targets:
        host , lastoct = targets.split("-")
        firstoct = host.split('.')[-1]
        targets = []
        for oct in range(int(firstoct),int(lastoct)):
            octs = host.split('.')
            targets.append(f"{octs[0]}.{octs[1]}.{octs[2]}.{str(oct)}")

    elif '/' in targets:
        try:
            targets = [str(ip) for ip in IPv4Network(targets)]
        except ValueError as err:
            print(f"{Color.Red}[!]{Color.White} {err}")
            sys.exit(1)

    else:
        targets = [targets]

    return find_ssh_servers(targets)

def handle_credentials(credentials):
    return credentials.split(',') if ',' in credentials else [credentials] if not os.path.isfile(credentials) else [line.strip() for line in open(credentials,'r').readlines()]

def display_ssh_servers(hosts):
    print("SSH SERVERS  :")
    for host in hosts:
        print(f"\t{Color.Green}{host}{Color.White}")

    print()

def run(targets,credentials,delay,no_replicate = False,cmd = None):
    execute = DefaultCommandExecution if not cmd else cmd
    targets = handle_targets(targets)
    credentials = handle_credentials(credentials)
    display_ssh_servers(targets)
    for target in targets:
        time.sleep(delay)
        print(f"\n{target} :")
        print(f"{Color.Blue}\tHostName    :\t",end='')
        try:
            host = f"{Color.Green}{socket.gethostbyaddr(target)[0]}"
        except socket.herror:
            host = f"{Color.Red}UNKNOWN"

        print(f"{host}")
        print(f"\t{Color.Blue}Access      :{Color.White}",end='')
        outputs = {}
        for c in credentials:
            if ':' not in c:
                print(f"\n\t\t{Color.Red}Please enter valid credentials ex(user:password) \"{c}\" is not valid{Color.White}\n")
                return
            
            if no_replicate and len(outputs) > 0:
                execute = DefaultCommandExecution

            user , passwd = c.split(':')
            status , output = ssh_connector(f"{user}@{target}",passwd,execute)
            if status != -1 and not (no_replicate and len(outputs) > 0):
                outputs[c] = output

            elif status != -1:
                outputs[c] = ""

        if len(outputs) == 0 :
            print(f"\t{Color.Red}No Access !!{Color.White}")

        else:
            print(f"{Color.Green}\t{', '.join(outputs.keys())}{Color.White}")
            if cmd:
                for key in outputs:
                    output = outputs.get(key).replace('\n','\n\t\t\t')
                    if len(output) > 0:
                        print(f"\t{Color.Blue}Exec ({key.split(':')[0]} # {Color.Yellow}{cmd}{Color.Blue})   :\n\t\t\t{Color.Green}{output}{Color.White}\n")
            
            outputs.clear()
            execute = cmd

def main():
    banner()
    options = register_options()
    
    if options.targets and options.creds:
        if options.exec:
            run(options.targets,options.creds,float(options.delay),options.replicate,options.exec)

        else:
            run(options.targets,options.creds,float(options.delay),options.replicate)


if __name__ == '__main__':
    main()
    