# Empire modules
1 - sshglow_enum module : for enumeration
2 - sshglow_exec module : for drop empire agent into accessible machines

# About
the modules will load SSHGlow in victim memory and call SSHGlow Functions 
that perform the tasks
SSHGlowExec module can execute only normal commands and can drop empire agent 
in victim network over python or powershell stagers for that the module can
targeting windows and linux and mac but the machine which load SSHGlow
should be python3 installed already 

## setup and run
```
cp sshglow_enum.yaml [%Empire PATH%]/empire/server/modules/python/situational_awareness/network/
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
│ Creds   │       │ True     │ (Victim)File or                     │
│         │       │          │ user1:pass1,user2:pass2 or only one │
├─────────┼───────┼──────────┼─────────────────────────────────────┤
│ Delay   │ 5     │ True     │ Delay interval in seconds           │
├─────────┼───────┼──────────┼─────────────────────────────────────┤
│ Targets │       │ True     │ CIDR or Range ex(192.168.1.1-10) or │
│         │       │          │ only one                            │
└─────────┴───────┴──────────┴─────────────────────────────────────┘


```