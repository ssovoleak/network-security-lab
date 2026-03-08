# Network Security Lab

A personal home lab built to develop practical cybersecurity skills through hands-on projects. It starts with TCP/UDP socket programming to understand how data is transmitted at the protocol level – knowledge that directly translates to analysing real packet behaviour in Wireshark. From there the lab moves into system hardening, network traffic analysis, network reconnaissance, and incident response – all done in a controlled virtual environment on my own machine.

## Lab Environment

- **Attacker/ Analyst machine**: Macbook Air running macOS
- **Target server**: Ubuntu Server 24.04 LTS running on UTM (ARM virtualisation)
- **Network**: Isolated host-only network between Mac and VM

## Projects

| Project                          | Description                                                                                           | Tools                   |
| -------------------------------- | ----------------------------------------------------------------------------------------------------- | ----------------------- |
| TCP/UDP socket Programming       | Built a multi-client TCP chat server and UDP messaging system to understand transport layer protocols | Python                  |
| Linux Server Hardening           | Configured and hardened an Ubuntu Server with SSH, firewall, and user privilege controls              | ufw, OpenSSH, Linux CLI |
| Network Traffic Analysis         | Captured and analysed live network traffic across multiple protocols                                  | Wireshark               |
| Network Reconnaissance           | Performed port scanning and service enumeration against the hardened VM                               | Nmap                    |
| Log Analysis & Incident Response | Simulated brute force attacks and documented incident response procedures                             | fail2ban, auth.log      |
