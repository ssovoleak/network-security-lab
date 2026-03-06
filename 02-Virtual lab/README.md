# Virtual Lab Setup

## Overview

This project is bilt using a small home lab on my MacBook using a Ubuntu Server VM. The goal was to get hands on with the administrative and security tasks in real environments, such as, configuring networks, hardening servers, managing users, and controlling access with a firewall.

Everything was done through SSH from my Mac terminal into the Ubuntu VM.

## Lab Environment

Host Machine: Macbook Air M3
Hypervisor: UTM
Target VM: Ubuntu Server 24.04 LTS (ARM64)
Network: UTM virtual bridge (bridge100)
Host IP: 192.168.64.1
VM IP: 192.168.64.2 (static)

## What I did

### 1. Static IP configuration

The first thing I noticed when I checked the network configuration is that the VM was getting its IP address automatically via DHCP. For a server, if the IP changes every reboot, SSH connections would break and firewall rules would stop working.

I modified the Netplan config file to make sure the VM IP is static:

```yaml
network:
  version: 2
  ethernets:
    enp0s1:
      dhcp4: false
      addresses:
        - 192.168.64.2/24
      routes:
        - to: default
          via: 192.168.64.1
      nameservers:
        addresses:
          - 8.8.8.8
          - 8.8.4.4
```

After the modification, I applied the changes without rebooting using `sudo netplan apply`.

### 2. SSH hardening

By default SSH allows password authentication, this means anyone who can reach port 22 can try to brute force their way into the session. The fix here is to switch to SSH key authentication and disable passwords completely.

I realized the important thing here is the order of operation. I have to set up the key and confirm it works before disabling passwords, otherwise I would lock myself out permanently.

Generat key pair on Mac:

- Copy public key to Ubuntu VM
- Test that key login works
- Disable password authentication afterwards

Changes made to sshd_config:

- PermitRootlogin : no | root should never be directly accessible |
- PasswordAuthentication : no | eliminate brute force risk |
- MaxAuthTries : 3 | Limit login attempts to 3 times |
- LoginGraceTime : 30s | reduce the risk of attack window |
- X11Forwarding : no | Unnecessary on a server |
- ClientAliveInterval : 60 | detect and close ghost connections |

One issue I ran into - Ubuntu 24.04 has an extra config file at `/etc/ssh/sshd_config.d/50-cloud-init.conf` that was overriding my changes with `PasswordAuthentication yes`. I had to update both files for the setting to actually take effect.

Verified the hardening worked:

#### password auth blocked

ssh -o PreferredAuthentication=password voleak@192.168.64.2
-> Permission denied (publickey)

#### Root login blocked

ssh root@192.168.64.2
-> Permission denied

### 3. User Management

Created 2 users to practice access control:
| User | Type | Sudo Access |
|------|------|-------------|
| Voleak | Admin | Yes |
| standarduser | Standard | No |

Practicing the principle of least privilege, users should only have access to what they actually need. If an attacker compromises a standard user account, the damage is limited. However, if they compromise an admin account, the issue is much bigger.

Verified that standarduser couldn't run sudo:
su - standarduser
sudo apt update
-> standarduser is not in the sudoers file

### 4. File Permissions

Linux controls access to every file and directory using a permission system. Every file has three sets of permissions - for owners, the group, and everyone else.

-rwxr-xr-x
-rwx : owner (full access)
r-x : group (read and execute)
r-x : others (read and execute)

Permissions translate to numbers:

- r (read) = 4
- w (write) = 2
- x (execute) = 1

So `rwxr-xr-x` = 755

When practiced changing permissions with `chmod` and ownership with `chown`. One interesting thing I noticed is that even if I set a file to `000` (no permission for anyone), the owner can still run `chmod` to store access because ownership and permissions are separate concepts. Moreover, a sudo user can always override with `sudo` regardless.

I have learned the security relevance here is real - misconfigured file permissions are a common privilege escalation vector. Sensitive files with wrong permissions can expose SSH keys, passwords, and configuration files to users who shouldn't have access.

### 5. Firewall Rules

Used ufw to control what traffic is allowed in and out of the VM.

Set the defaults:

- sudo ufw default deny incoming #block everything by default
- sudo ufw allow outgoing #VM can reach internet freely

Allow SSH before enabling the firewall, If the firewall is enabled before SSH, I would get locked out immediately :

- sudo ufw allow 22
- sudo ufw enable

The most interesting thing I learned here is that firewall rules order matters. ufw processes rules from top to bottom and stops at the first match. I tested this by adding a deny rule for my Mac's IP but placing it after the allow rule for port 22 - SSH still worked because the allow rule matched first and the deny rule was never reached.

The fix was to insert the deny rule in the first position so it gets checked first:

sudo ufw insert 1 deny from 192.168.64.1

I have also learned the difference between filtered and and closed ports when testing curl from my Mac:

- Port allowed, no service running -> immediate "connection refused"
- Port blocked by firewall -> request times out after 75 seconds

Additionally, firewall rules only affect new connections, not existing ones. Adding a deny rule while already SSH'd in doesn't lock or kick me out. The session was already established so ufw doesn't have any effect. To disconnect someone who's already in, I'd have to actively kill the session.

## Key Takeaways

A few things that I've fully understood after building this:

The order of operations matters more than I expected. Whether it's setting up SSH keys before disabling passwords, or adding firewall allow rules before enabling the firewall - getting the sequnce wrong can lock you out immediately.

Everything in Linux is a file with a config. Once we know to look in the right place such as /etc/ we can find and understand how almost any service is configured. The pattern is the same everywhere: commented out lines show defaults, uncomment and change to override the defaults.

## Limitations and Future Improvements

- No ban configured to automatically blocked repeated failed SSH login attempts
- Firewall currently allows SSH from anywhere, in a real environment only trusted IPs are allowed
- Single VM setup - a more realistic lab would have multiple VMs on an isolated internal network
- No IDS (Intrusion Detection System) configured to alert on suspicious activity.
- No Windows machine yet - planning to add a Windows VM to demonstrate cross platform administration, Windows Event Viewer log analysis, and Windows specific port scanning in a future update.
