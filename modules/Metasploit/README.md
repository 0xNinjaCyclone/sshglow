# Metasploit modules
1 - sshglow_enum module : for enumeration
2 - sshglow_exec module : for drop metasploit payloads into accessible machines

# About
the modules will load SSHGlow in memory and call SSHGlow Functions 
that perform the tasks 
SSHGlowExec module can execute only normal commands and can drop metasploit payloads 
in victim network over python or powershell or HTA stagers for that the module can
targeting windows and linux and mac but python3 should be installed already 

## setup and run
```
cp sshglow_enum.rb /usr/share/metasploit-framework/modules/auxiliary/scanner/ssh/
cp sshglow_exec.rb /usr/share/metasploit-framework/modules/exploits/multi/ssh/
```

```
msf6 > use auxiliary/scanner/ssh/py_sshglow_enum
msf6 auxiliary(scanner/ssh/py_sshglow_enum) > info 

       Name: SSHGlowEnum
     Module: auxiliary/scanner/ssh/py_sshglow_enum
    License: Metasploit Framework License (BSD)
       Rank: Normal

Provided by:
  Abdallah Mohamed Elsharif

Check supported:
  No

Basic options:
  Name    Current Setting  Required  Description
  ----    ---------------  --------  -----------
  Creds                    yes       File or user1:pass1,user2:pass2 or single
  DELAY   5                yes       Delay interval in seconds
  RHOSTS                   yes       The target host(s), range CIDR identifier, or hosts file with syntax 'file:<path>'

Description:
  This module will find our access in network.

```