# Project 5 – Log Analysis $ Incident Response

## Overview

In this project I simulated an SSH brute force attack against my Ubuntu VM and used it as a basis for practising log analysis and incident response. SSH is one of the most common attacks on Linux servers, therefore the goal was to generate realistic attack data and analyse it the way a security analyst would, then configure an automated defence and document the process.

## Lab environment

Analyst machine : Macbook Air M3 running macOS
Target server: ubuntu server 24.04 LTS running on UTM
Network: Isolated host-only network 192.168.64.0/24
Target IP: 192.168.64.2
Attacker IP: 192.168.64.1

## Executive Summary

A simulated brute force attack from my Mac was launched against the Ubuntu VM by running a loop of about 20 SSH connection attempts targeting a non-existent user account. All 20 attempts were recorded in `auth.log` in the `/var/log` directory. After installing and configuring fail2ban, I ran the simulation again and observed how it automatically detected the attack and banned my Mac’s IP address in real time. No successful authentication occurred at any point during the simulation.

## Attack Simulation

To simulate the attack, I executed a loop from my Mac terminal that attempted to SSH into the VM 20 times in a row using fake usernames. This is similar to what automated brute force tools like Hydra do, but on a smaller scale where they circle through username and password combinations rapidly trying to find valid credentials.

**Command used from Mac Terminal:**

```
for i in {1..20}; do ssh fakeuser@192.168.64.2; done
```

All 20 attempts were completed in within 2-3 seconds, the speed is what makes automated brute force dangerous because normal humans would not be able to attempt 20 logins in just 2 seconds, but this script can achieve that effortlessly, not to mention real tools can do thousands per minute.

## Log Analysis

The first thing I did was check auth.log to see what the attack looked like from the server’s perspective. I used grep to filter for the relevant entries.

**Searching for invalid user attempts:** `sudo grep “Invalid user /var/log/auth.log”`

**Output:**

```
2026-03-09T00:44:38.304439+00:00 client sshd[1085]: Invalid user fakeuser from 192.168.64.1 port 49479
2026-03-09T00:44:38.419756+00:00 client sshd[1087]: Invalid user fakeuser from 192.168.64.1 port 49480
2026-03-09T00:44:38.519942+00:00 client sshd[1089]: Invalid user fakeuser from 192.168.64.1 port 49481
```

Each line shows the exact timestamp, the fake username that was tried, the source IP address, and the port the connection came from. One thing I noticed immediately was that each attempt came from a different source port, which is a normal behavior for automated tools and an indicator of scripted activity.

I also noticed that the log says "Invalid user" instead of "Failed password" because SSH rejected the connection before even asking for a password since the username doesn't exist on the system

**Counting attempts per IP:** `sudo grep "Invalid user" auth.log | awk '{print $8}' | sort | uniq -c | sort -rn`

**Output:**

```
20 192.168.64.1
```

20 attempts, all from one IP within 2-3 seconds. In a real attack this would show multiple IPs, as well as, dozens of different usernames.

### Signs of Compromise

| Indicator         | Value                            |
| ----------------- | -------------------------------- |
| Source IP         | 192.168.64.1                     |
| Targeted username | fakeuser                         |
| Total attempts    | 20                               |
| Timeframe         | 2 seconds                        |
| First attempt     | 2026-03-09T00:44:38.304439+00:00 |
| Last attempt      | 2026-03-09T00:44:40.202387+00:00 |
| Method            | SSH brute force - Invalid user   |

### Timeline

| Time     | Event                                                         |
| -------- | ------------------------------------------------------------- |
| 00:44:38 | First SSH brute force attempt detected from 192.168.64.1      |
| 00:44:40 | Final attempt, 20 total attempts recorded in auth.log         |
| 01:43:49 | fail2ban detected threstold exceeded, IP banned automatically |
| 01:43:50 | SSH connection from 192.168.64.1 refused, ban confimed        |
| 01:48:20 | IP manually unbanned via fail2ban-client after verification   |

## Attack Analysis

SSH brute force attacks are one of the most common attacks targeting Linux servers. Attackers tend to use automated tools to rapidly switch between combinations of common usernames, such as root, and admin, then paired with large password wordlists. The main objective is to find valid credentials that allow remote shell access to the server.

I think the key factor that makes this specific type of attack dangerous is the speed. The 20 attempts in this simulation were generated in just 2 seconds, whereas in a real attack, tools like Hydra can attempt thousands of combinations per minute from multiple IP addresses simultaneously. With that being said, without the help of automated detection and response, a server with weak credentials could easily be compromised in a matter of minutes.

In this case, the attack was unsuccessful for two reasons. First, the targeted username did not exist on the system. Second, the server was configured with key-based SSH authentication which means password-based logins are disabled completely. However, the attack can still represents a real threat because the volume of attempts alone can indicate reconnaissance activity, and a misconfigured server with password authentication enabled would definitely be vulnerable.

## Response -fail2ban Configuration

fail2ban was installed and configured to automatically detect and block brute force attempts against SSH. It operates by monitoring auth.log in real time and add firewall rules to block IP addresses that exceed a defined limit of failed attempts.

### Configuration applied in /etc/fail2ban/jail.local:

```
[sshd]
enabled = true
maxretry = 5
findtime = 10m
bantime = 1h
```

### What these settings mean:

- `maxretry= 5` : Ban the IP atfter 5 failed attempts
- `findtime = 10m` : Count failures within a rolling 10 minutes window
- `bantime = 1h` : Keep the IP banned for 1 hour before allowing retry

After restarting fail2ban and re-running the brute force simulation, the source IP was automatically banned after exceeding the threshold. The SSH connection was temrinated mid-session and subsequent connection attempts were refused entirely.

**Jail status confirming the ban:** `sudo fail2ban-client status sshd`

```
Status for the jail: sshd
|- Filter
|- Currently failed: 1
- Total failed: 19
- File list: /var/log/auth. log
- Actions
    |- Currently banned: 1
    |- Total banned: 2
    |- Banned IP list: 192.168.64.1
```

## Remediation

The following measures were confirmed as a result of this incident:

- **fail2ban installed and active**: automated brute force detection and IP banning are now running as a system service
- **Key-based authentication enforced**: password authentication disabled in SSH config which means even a successful username guess would not lead to access without the private key
- **Root login disabled**: direct root SSH access blocked limits the impact of any potential compromise.
- **Default-deny firewall**: ufw configured to block all inbound traffic except SSH and HTTP, reducing the overall attack surface

## Lessons Learned

This exercise has shown me several important principles that apply directly to real-world server security:

- **Log monitoring is essential**: Auth.log recorded every single detail of the attack including source IP, targeted username, exact timestamps, and frequency. Without regular log monitoring, this attack would easily go unnoticed.
- **Automated response matters**: This is the most important take for me because manual log review alone is not sufficient against automated attacks. By the time an analyst reviews a log, thousands of attempts could have already occurred. fail2ban provides an automated defence that detects and responds to threats in real time without human intervention.
- **Layered Security controls is important**: A single security control wouldn't have been able to stop this attack, it's the combination of an invalid username, disabled password authentication, and fail2ban working together that made the attack completely ineffective. This also ensures that no single failure can lead to a compromise.
- **Default configurations are unsafe**: The default Ubuntu Server installation with password-based SSH exposed on port 22 would be the main vulnerability to this type of attack. The system hardening performed in project 2, including key-based auth, disabled root login, firewall rules are the security layers that helped mitigate the risk demonstrated in this brute force SSH attack simulation.
