# About sshglow
ssh glow is an enumeration and lateral movement tool in linux environments to find the servers which
we access on , and execute command on if we want 

# Main Features
- handle cidr or range separated by - or particular targets separated by , or one target
- handle file of credentials or more than account sperated by , or only one account
- sshglow uses built-in tools and libraries 

# Enumerate
`./sshglow.py -t TARGETS -c CREDS`
![](./preview1.jpg)

# Exec commands
`./sshglow.py -t TARGETS -c CREDS --no-replicate -e COMMAND`
![](./preview2.jpg)

