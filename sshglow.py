#!/usr/bin/python3

import os
import sys
import pty
import socket
import time
from ipaddress import IPv4Network
from optparse import OptionParser


AUTHOR  = "Abdallah Mohamed Elsharif"
VERSION = "1.1"


class Color:
    Red     = "\033[0;31m"
    Yellow  = "\033[0;33m"
    Green   = "\033[0;32m"
    Blue    = "\033[0;34m"
    Bold    = "\033[1m"
    NC      = "\033[0m" # No Color


class Print:

    display = True


    @classmethod
    def normal(cls, text="", endl = "\n", startl = ""):
        if Print.display:
            print(f"{startl}{text}{Color.NC}", end=endl)

    @classmethod
    def special(cls, text="", endl = "\n", startl = ""):
        if Print.display:
            print(f"{startl}{Color.Bold}{text}{Color.NC}", end=endl)

    @classmethod
    def success(cls, text="", endl = "\n", startl = ""):
        if Print.display:
            print(f"{startl}{Color.Green}{text}{Color.NC}", end=endl)

    @classmethod
    def status(cls, text="", endl = "\n", startl = ""):
        if Print.display:
            print(f"{startl}{Color.Blue}{text}{Color.NC}", end=endl)

    @classmethod
    def fail(cls, text="", endl = "\n", startl = ""):
        if Print.display:
            print(f"{startl}{Color.Red}{text}{Color.NC}", end=endl)


def register_options():
    parser = OptionParser(version=VERSION)
    parser.add_option('-t','--targets',dest='targets',
            help='Your Target (one ip or more separated by ,) or cidr or range ex(192.168.1.1-10)')
    parser.add_option("-P","--protocol",dest="proto",help="Enter your target protocol supportd protocols [ssh] default (ssh)", default="ssh")
    parser.add_option("-p","--port",dest="port",help="Enter the port of the protocol",type=int)
    parser.add_option("-c","--credentials",dest="creds",
            help="Enter creds on or more separated by , ex(user:pass or user2:pass2,user2:pass2) or file with same expression")
    parser.add_option("-d","--delay",dest="delay",help="delay interval in seconds (default 0.5)",type=float,default=0.5)
    parser.add_option("-e","--exec",dest="exec",help="Execute command on all machines which you have access on")
    parser.add_option("-r","--no-duplicate",action="store_true",dest="duplicate",help="Don't duplicate execution when using multiple users")
    parser.add_option("-s","--silent",action="store_true",dest="silent",help="No output")
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
    
    Print.fail(banner.replace('\n','\n\t\t\t'))
    Print.status(f"Author  ->  ", startl='\t\t\t', endl='')
    Print.success(AUTHOR, endl=',\t')
    Print.special(f"Version  ->  {VERSION}", endl='\n\n')


class IProto:
    def __init__(self, port) -> None:
        self.port = port

    def connector(self, target, user, passwd, cmd):
        pass


class SSH(IProto):
    def __init__(self, port = 22) -> None:
        IProto.__init__(self, port)

    def connector(self, target, user, passwd, cmd):
        pid, fd = pty.fork()
        if not pid:
            os.execv("/usr/bin/ssh",["/usr/bin/ssh",f"{user}@{target}","-p",str(self.port),"-o","StrictHostKeyChecking=no",cmd])
        
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
            pid, _ = os.waitpid(pid, os.WNOHANG)
            return True, ''.join(output)
        else:
            return False, ''


def find_servers(hosts, port):
    servers = []
    for host in hosts:
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.settimeout(0.1)
        if s.connect_ex((host, port)) == 0:
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
            Print.fail(err)
            sys.exit(1)

    else:
        targets = [targets]

    return targets


def handle_credentials(credentials):
    return credentials.split(',') if ',' in credentials else [credentials] if not os.path.isfile(credentials) else [line.strip() for line in open(credentials,'r').readlines()]


def display_servers(protoname, hosts):
    Print.normal(f"{protoname} SERVERS  :")

    if bool(hosts):
        for host in hosts:
            Print.success(host, startl='\t')

    else:
        Print.fail("No Servers available !!", startl='\t')


def display_hostname(host):
    Print.normal(f"\n{host}  :")
    Print.status("HostName    :", startl='\t', endl='\t')
    
    try:
        Print.success(socket.gethostbyaddr(host)[0])
    except socket.herror:
        Print.fail("UNKNOWN")


def display_access(node):
    Print.status("Access      :", startl='\t', endl='')

    if node["access"]:
        Print.special(startl='\t', endl='')
        for i in node["info"]:
            user = i["user"]
            passwd = i["pass"]
            Print.special(f"{user}:{passwd}", endl='')

            if i != node["info"][-1]:
                Print.special(', ', endl='')
    else:
        Print.fail("No Access !!", startl='\t', endl='')

    Print.special(endl='\n')


def display_exec(info):
    for i in info:
        if i["exec"] and i["output"]:
            user = i["user"]
            cmd = i["cmd"]
            Print.status(f"Exec ({user} # {Color.Yellow}{cmd}{Color.Blue})   :", startl='\n\t')
            Print.success(i["output"], startl='\t\t\t')


def display(access):
    for node in access:
        display_hostname(node["target"])

        display_access(node)

        if node["access"]:
            display_exec(node["info"])
            
        
def get_proto(protoname, port = None):
    pn = protoname.lower()

    if pn == "ssh":
        p = SSH

    else: 
        raise TypeError(f"{protoname} is unexpected !!")

    return p(port) if port else p()


def run(targets, proto, credentials, delay, no_duplicate = False, cmd = None):
    access = list()
    defaultCommand = "whoami"
    hosts = handle_targets(targets)
    targets = find_servers(hosts, proto.port)
    credentials = handle_credentials(credentials)
    display_servers(proto.__class__.__name__, targets)

    for target in targets:
        time.sleep(delay)

        accessInfo = dict()
        accessInfo['target'] = target
        accessInfo['execute'] = cmd != None
        accessInfo['access'] = False
        accessInfo['info'] = list()

        # Use default command in execution if user does not pass any commands
        execute = defaultCommand if not cmd else cmd

        for c in credentials:
            if ':' not in c:
                Print.fail(f"Please enter valid credentials ex(user:password) \"{c}\" is not valid", startl='\n\t')
                continue
            

            # If execution was disabled we should use default command 
            if not accessInfo['execute'] and execute != defaultCommand:
                execute = defaultCommand

            user , passwd = c.split(':')
            valid , output = proto.connector(target, user, passwd, execute)

            # If we get valid access
            if valid:
                accessInfo["access"] = True

                info = {
                    "user": user,
                    "pass": passwd,
                    "exec": accessInfo["execute"],
                }

                if info["exec"]:
                    info["cmd"] = cmd
                    info["output"] = output


                accessInfo["info"].append(info)

                # If no_duplicate option was enabled and we get valid access we should disable execution for the another users
                if no_duplicate:
                    accessInfo["execute"] = False


        access.append(accessInfo)


    display(access)


def main():
    options = register_options()

    if options.silent: # No output
        Print.display = False

    banner()
    
    if options.targets and options.creds:
        try:
            run(options.targets, get_proto(options.proto, options.port), options.creds, options.delay, options.duplicate, options.exec)
        except BaseException as e:
            Print.fail(e)
        


if __name__ == '__main__':
    main()
    