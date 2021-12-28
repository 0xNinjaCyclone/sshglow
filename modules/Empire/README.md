# Empire modules
- sshglow_enum module : For enumeration
- sshglow_exec module : To drop empire agent into accessible machines

# About
the modules will load SSHGlow in victim memory and call SSHGlow Functions 
that perform the tasks\
SSHGlowExec module can execute only normal commands and can drop empire agent 
into victim's network via python or powershell stagers therefore the module can
targeting windows and linux and mac but the machine which load SSHGlow
should be python3 installed already 

## setup and run
```
cp sshglow_enum.* [%Empire PATH%]/empire/server/modules/python/situational_awareness/network/
cp sshglow_exec.* [%Empire PATH%]/empire/server/modules/python/lateral_movement/multi/
```

```
(Empire) > usemodule python/situational_awareness/network/sshglow_enum

 Author       @abdallah_elsharif                                
 Background   True                                              
 Comments     https://github.com/abdallah-elsharif/sshglow      
 Description  This module will find our access in network.      
 Language     python                                            
 Name         python/situational_awareness/network/sshglow_enum 
 NeedsAdmin   False                                             
 OpsecSafe    True                                              
 Techniques   http://attack.mitre.org/techniques/T1021          


┌Record Options───┬──────────┬─────────────────────────────────────┐
│ Name    │ Value │ Required │ Description                         │
├─────────┼───────┼──────────┼─────────────────────────────────────┤
│ Agent   │       │ True     │ Agent to use ssh from.              │
├─────────┼───────┼──────────┼─────────────────────────────────────┤
│ Creds   │       │ True     │ (Attacker)File or                   │
│         │       │          │ user1:pass1,user2:pass2 or only one │
├─────────┼───────┼──────────┼─────────────────────────────────────┤
│ Delay   │ 5     │ True     │ Delay interval in seconds           │
├─────────┼───────┼──────────┼─────────────────────────────────────┤
│ Targets │       │ True     │ target to scan in single or Range   │
│         │       │          │ ex(192.168.1.1-10) or CIDR format   │
│         │       │          │ or (Attacker)File                   │
└─────────┴───────┴──────────┴─────────────────────────────────────┘


```