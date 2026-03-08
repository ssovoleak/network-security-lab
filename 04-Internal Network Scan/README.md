# Network Reconnaissance - Nmap Scanning

## Overview

After hardening the Ubuntu in project 2, I wanted to see it from the other side- what does an attacker actually see when they scan my server? This project uses Nmap to perform network recconaissance against the Ubuntu VM to understand what information is exposed and whether the hardening I applied actually made a difference.

After running these scans just under 5 minutes I had a complete profile of the target including exact software versions, open ports, host keys, and network topology. It made me understand why hardening matters because every open port and every running service tells an attacker something useful.

## Lab Environment

| Component    | Details                 | Role                   |
| ------------ | ----------------------- | ---------------------- |
| Host Machine | Macbook Air M3          | Running Nmap scans     |
| Target VM    | Ubuntu Server 24.04 LTS | Being scanned          |
| Host IP      | 192.168.64.1            | Scanner                |
| Target IP    | 192.168.64.2            | Target                 |
| Network      | UTM bridge100           | Virtual local network  |
| Tool         | Nmap 7.98               | Installed via Homebrew |

## What is Nmap

Nmap is an open source tool used for network reconnaissance. Attackers use it to discover targets and identify vulnerabilities. Whereas Defenders can use it to audit their own infrastructure and verify their own configuration settings.

I used it here to ansewer one question - if someone got on my local network and scanned my Ubuntu VM, what would they find?

## Scan 1 - Basic Port Scan

### Command

```
nmap 192.168.64.2
```

### Output

```
Host is up (0.0012s latency) .
Not shown: 998 filtered top ports (no-response)
PORT STATE SERVICE
22/tcp open ssh
80/tcp open http
```

### What this scan does

Nmap's default scan checks the top 1000 most common TCP ports. For each port it sends a SYN packet and waits:

- SYN-ACK -> port is open
- RST -> port is closed
- No response -> port is filtered by firewall

### What I found

The first thing I noticed was that 998 out of 1000 ports showed as filtered which is the ufw firewall from project 2 doing its job. Only port 22 (SSH) and port 80 (HTTP) were visible, which is exactly what I configured.

From an attacker's perspective this is not quite helpful because the attack surface is very small. Only 2 ports to work with out of a thousand scanned.

## Scan 2 - OS Detection

### Command

```
sudo nmap -O 192.168.64.2
```

### Output

```
MAC Address: 32:2B:81:18:6D:76 (Unknown)
Device type: general purpose|router|storage-misc
Running (JUST GUESSING): Linux 4.X|5. X|6.X|2.6.X|3.X (97%)
Aggressive OS guesses: Linux 4.15 - 5.19 (97%)
No exact OS matches for host (test conditions non-ideal).
Network Distance: 1 hop
```

### What this scan does

Sends specially crafted packets and analyses how the target responds. Every OS responds slightly differently to unusual packets. Nmap compares responses against a database of known signatures to guess what's running.

### What I found

Nmap detected Linux at 97% confidence but couldn't identify the exact kernel version. The warning "test conditions non-ideal" means the firewall was interfering with the fingerprinting process. The more ports the firewall blocks the harder it is for Nmap to get an accurate OS fingerprint.

My MAC address was fully exposed - `32:2B:81:18:6D:76`. This is unavoidable on a local network since MAC addresses are needed for ARP and local delivery. An attacker would use this to track and identify my specific VM across multiple scans.

The network distance of 1 hop confirms the VM is directly on the local network with no intermediate routers, which is expected for my lab setup.

## Scan 3 - Service Version Detection

### Command

```
nmap -sV 192.168.64.2
```

### Output

```
PORT STATE SERVICE VERSION
22/tcp open ssh   OpenSSH 9.6p1 Ubuntu 3ubuntu13.14 (Ubuntu Linux; protocol 2.0)
80/tcp open http.   Apache httpd 2.4.58 ( (Ubuntu))
Service Info: OS: Linux; CPE: cpe:/0:1inux:linux_kernel
```

### What this scan does

Connects to each open port and grabs the service banner - the message a service sends when we first connect. Most services announce their exact name and version in this banner. Nmap collects and displays all of it.

### What I found

This is where things got interesting. In under 50 seconds Nmap grabbed the exact versions of both services running on my VM - OpenSSH 9.6p1 and Apache 2.4.58. An attacker would take these version numbers straight to CVE databases like NVD or Exploit-DB and search for known vulnerabilities.

The CPE identifier `cpe:/0:1inux:linux_kernel` is a standardised string that's directly searchable in vulnerability database, making the attacker's job even easier.

Ubuntu was confirmed twice - once in the SSH banner and once in the Apache banner. I was basically advertising my OS through two different services simultaneously.

However, both versions are recent so there are fewer known vulnerabilities. Keeping software updated is one of the most effective defences against this type of reconnaissance.

## Scan 4 - Aggressive Scan

### Command

```
sudo nmap -A 192.168.64.2
```

### Output

```
22/tcp open ssh
OpenSSH 9.6p1 Ubuntu 3ubuntu13.14 (Ubuntu Linux; protocol 2.0)
I ssh-hostkey:
256 af: 99:4b:04:75:14:5e:d1: f9:86:1f:f5:70:71:af:73 (ECDSA)
1- 256 54:CC:ba:1d:ec: 77:32:92:30:d5:ba:ff:7f:68:4e:37 (ED25519)
80/tcp open http
Apache httpd 2.4.58 ((Ubuntu))
I_http-title: Apache2 Ubuntu Default Page: It works
I_http-server-header: Apache/2.4.58 (Ubuntu)
MAC Address: 32:2B: 81:18:6D:76 (Unknown)
Aggressive OS guesses: Linux 4.15 - 5.19 (97%), Linux 4.19 (97%), Linux 5.0 - 5.14 (97%), OpenWrt 21.02 (Linux 5.4) (97%), MikroTik RouterOS 7.2 - 7.5 (Linux 5.6.
3) (97%), Linux 6.0 (94%), Linux 5.4 - 5.10 (91%), Linux 2.6.32 (91%), Linux 2.6.32 - 3.13 (91%), Linux 3.10 - 4.11 (91%)
Network Distance: 1 hop
Service Info: OS: Linux; CPE: cpe:/0:linux:linux_kernel
TRACEROUTE
HOP RTT ADDRESS
1 0.76 ms 192.168.64.2
```

### What this scan does

This scan combines version detection, OS detection, script scanning and traceroute. Nmap scripts automatically probe services for additional information beyond just version numbers.

### What I found

This scan revealed more than I expected. The SSH host keys were fully exposed:

```
256 af: 99:4b:04:75:14:5e:d1: f9:86:1f:f5:70:71:af:73 (ECDSA)
1- 256 54:CC:ba:1d:ec: 77:32:92:30:d5:ba:ff:7f:68:4e:37 (ED25519)
```

These are my server's identity fingerprints. An attacker saves these to track the specific server accoss scans. If the fingerprints change unexpectedly, it could possibly indicate a MITM attack or that the server has been rebuilt.

The default Apache page title "It works" was also grabbed

```
I_http-title: Apache2 Ubuntu Default Page: It works
```

This tells an attacker my Apache installation is new and possibly misconfigured. They could start probing for common misconfigurations such as exposed directories, test files, and admin panels. This is the case because I installed Apache for project 3 and left the default page up.

The Apache version was also visible in the HTTP server header

```
I_http-server-header: Apache/2.4.58 (Ubuntu)
```

This is not just visible to Nmap, this header is sent to every single person who visits port 80. This means that anyone with a browser and basic understanding can see my exact Apache version without even running a scan.

The traceroute confirmed the VM is 1 hop away at 0.76ms, which is directly on my local network as expected.

## Scan 5 - Full Port Scan

### Command

```
sudo nmap -p- 192.168.64.2
```

### Output

```
Not shown: 65533 filtered top ports (no-response)
PORT STATE SERVICE
22/tcp open ssh
80/tcp open http
MAC Address: 32:2B:81:18:6D:76 (Unknown)
```

### What this scan does

Scans all 65535 TCP ports instead of default top 1000. Attackers do this to find services running on non-standard ports that basic scans miss.

### What I found

The full scan took much longer than a basic scan. Every filtred port has to wait for a timeout before Nmap moves on, which indicates that the firewall is what's slowing the attacker down.

The result was the same as the basic scan, only ports 22 and 80 open out of 65535. No hidden services, no backdoors, no services running on unsual ports. This shows that the firewall rules I configured in project 2 are consistent across all 65535 ports, not just the top 1000.

This was the most reasuring result. A full port scan is the most thorough thing an attacker can do and it found nothing beyond what I already knew was open.

## Complete Attacker Profile

After running all five scans I had built this complete profile of my own server in just under 5 minutes:

```
Target IP :         192.168.64.2
OS:                 Linux(Ubuntu) - 97% confident
SSH version:        OpenSSH 9.6p1
HTTP version:       Apache 2.4.58
Default page:       fresh Apache install
SSH host keys:      ECDSA and ED25519
MAC address:        32:2B:81:18:6D:76
Open ports:         22 and 80 only
Filtered ports:     65533
Network:            local, 1 hop, 0.76ms
```

## Security Assessment

### What's working

| Control                     | Evidence from scans                        |
| --------------------------- | ------------------------------------------ |
| Firewall active             | 65535 ports filtered across all scans      |
| Minimal attack surface      | Only 2 ports open out of 65535             |
| SSH hardened                | Password auth disabled, key auth only      |
| Recent software versions    | OpenSSH 9.6p1, Apache 2.4.58               |
| OS fingerprinting difficult | No exact OS match found                    |
| Scan speed degraded         | Full scan took 110 seconds due to firewall |

### What needs improvement

| Finding                     | Risk   | Fix                                 |
| --------------------------- | ------ | ----------------------------------- |
| Apache version in headers   | Medium | Set ServerTokens Prod               |
| Default Apache page showing | Low    | Replace or remove                   |
| Port 80 open unnecessarily  | Medium | Disable — only needed for project 3 |
| No IDS running              | Gap    | Install fail2ban for SSH protection |
| No scan detection           | Gap    | Configure log monitoring            |

## Key Takeaways

Running Nmap against my own server changed how I think about security. Before this project I knew the firewall was configured and SSH was hardened, but I didn't fully understand how much information was still available through just the 2 open ports.

## Limitations and Future Improvements

- Only TCP scans performed - a UDP scan would reveal additional services not visible here
- No vulnerability scanning beyond reconnaissance
- No Windows target available to demonstrate Windows specific ports
- Scans went completely undetected, no IDS configured to alert on reconnaissance activity.
