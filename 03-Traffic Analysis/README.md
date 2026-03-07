# Network Traffic Analysis

## Overview

This project focuses on capturing and analyzing real network traffic using Wireshark. My goal was to observe what different types of traffic look like at the packet level, understand what information is exposed in plain text, and compare unencrypted and encrypted communication. All captures were taken on the bridge100 interface, the virtual network between my Mac and Ubuntu VM.

## Lab Environment

| Component         | Details                             |
| ----------------- | ----------------------------------- |
| Capture Interface | bridge100 (UTM virtual network)     |
| Wireshark Version | Latest stable                       |
| Host Machine      | MacBook Air M3                      |
| Target VM         | Ubuntu Server 24.04 LTS             |
| Host IP           | 192.168.64.1                        |
| VM IP             | 192.168.64.2                        |
| Web Server        | Apache 2.4 (Installed on Ubuntu VM) |

## Capture 1 - TCP 3-way Handshake

### What I did

Generated a TCP connection by sending an HTTP request from Mac to the Apache web server running on the Ubuntu VM using curl:
`curl http://192.168.64.2`

### Filter used

```
tcp.port == 51394
```

### What I observed

Every TCP connection starts with a 3-way handshake before any data is exchanged. I could see all 3 steps clearly in Wireshark

**Packet 1 - SYN (MAC -> Ubuntu):**

```
192.168.64.1 -> 192.168.64.2
51394 -> 80 [SYN]
Seq=0 Win=65535 Len=0 MSS=1460
```

My Mac initiated the connection to Apache on port 80. Port 51394 is the ephemeral port that was automatically assigned by the Mac's OS for this specific session.

**Packet 2 - SYN-ACK (Ubuntu -> Mac):**

```
192.168.64.2 -> 192.168.64.1
80 -> 51394 [SYN-ACK]
Seq=0 Ack=1 Win=65160
```

Ubuntu acknowledged the connection request and gave a signal that it's ready.

**Packet 3 - ACK (Mac -> Ubuntu):**

```
192.168.64.1 -> 192.168.64.2
51394 -> 80 [ACK]
Seq=1 Ack=1 Win=131776
```

Mac acknowledged Ubuntu's response. With the handshake complete, the connection is established. HTTP data exchange will begin after this.

### Key Observation

- The entire handshake completes before a single byte of application data is sent
- The OS handles the handshake automatically
- The ephemeral port 51394 was assigned automatically by the Mac's OS for this specific sesion
- Each new connection gets a different ephemeral port

### Security relevance

The 3-way handshake is the foundation of TCP's reliability. However, it also creates a vulnerability such as SYN flood attacks which can be done by sending thousands of SYN packets without completing the handshake, exhuasting the server's connection table ans causing a denial of service.

## Capture 2 - HTTP Traffic Analysis

### What I did

Installed Apache on the Ubuntu VM and sent HTTP requests from my Mac using both curl and a browser directly to Ubuntu's IP:
`curl http://192.168.64.2`

Also visited http://192.168.64.2 in browser to generate additional HTTP traffic.

### Filter used

```
http
```

### What I observed

HTTP traffic is completely unencrypted. Everything is transmitted in plain text and fully readable in Wireshark

**HTTP GET request (Mac -> Ubuntu):**

```
GET / НTTР/1.1
Host: 192.168.64.2
User-Agent: curl/8.7.1\
Accept: */*
```

**HTTP 200 OK response (Ubuntu -> Mac):**

```
НТTP/1.1 200 0K
Server: Apache/2.4.58 (Ubuntu)
Content-Length: 10671
Content-Type: text/html

(full HTML source code is visible)
```

### Key Observation

- The full HTML source code of the webpage was visible in Wireshark, the content is completely exposed
- The Apache version was visible in the response headers, this information would help attackers identify what software is running and look up known vulnerabilities
- My Mac's browser information was visible in the request headers including User-Agent string
- Any form data, cookies, or login credentials submitted over HTTP would be fully readable by anyone capturing the traffic

### Security relevance

This capture clearly demonstrates why HTTP should never be used for anything sensitive. A basic MITM attack on the same network would expose everything- login credentials, session cookies, personal data.

## Capture 3 - HTTPS vs HTTP Comparison

### What I did

Generated HTTPS traffic from the Ubuntu VM to google.com so the traffic would cross bridge100 and be captured:

```
curl https://google.com
```

### Filter used

```
tls
```

### What I observed

**HTTP packet contents (from capture 2):**

```
Full HTML visible
Request headers readable
Response headers readable
Server version exposed
Complete page content accessible
```

**HTTPS/TLS packet contents:**

```
Enrypted Application Data
[content unreadable]
```

The difference was immediately noticeable. While HTTP showed everything in plain text, HTTPS showed only encrypted bytes that are completely unreadable without the encryption key.

**What is still visible in HTTPS:**
Even with TLS encryption, some information remains visible at the TCP layer:

- Source IP
- Destination IP
- Source Port
- Destination Port
- Packet size
- Timing
- Domain name

### Key Observations

- TLS encrypts the content inside the packet but TCP headers must remain visible for routing to work
- Think of it like a sealed envelope - the address on the outside must be readable for delivery but the letter inside is private
- Metadata is still visible even with HTTPS
- Content is protected

### Security relevance

HTTPS protects content but not metadata, this means ISPs and anyone capturing traffic can still see which websites we're visiting even if they can't read what we're doing there. Now I understand why DNS over HTTPS (DoH) was developed, it's to encrypt the domain name lookups so metadata is also protected.

## Capture 4 - DNS Lookup

### What I did

Ran nslookup from the Ubuntu VM terminal while capturing on bridge100:

```
nslookup google.com
```

### Filter used

```
dns
```

### What I observed

```
DNS Query (Ubuntu -> DNS server):
Transaction ID: 0xcc9d
Type: A record (IPv4 address lookup)
Class: IN (Internet)
Port: 53
Protocol: UDP

DNS Response (DNS server -> Ubuntu):
Transaction ID: 0xcc9d (same ID - matched by OS)
Type: A
Class: IN
Addr: 91.189.92.20
```

### Key Observations

- DNS uses UDP not TCP - no handshake, just send and receive
- DNS runs on port 53
- The entire DNS query is in plain text - completely uncrypted
- Transaction ID matches between query and response - OS uses this to match responses to the correct query
- Anyone capturing traffic can see exactly which domains are being looked up even if the actual website uses HTTPS
- DNS was sent to Google's DNS server (8.8.8.8) which I configured during static IP setup in project 2.

### Security Relevance

DNS is a significant privacy and security concern:

**DNS spoofing**
An attacker who sucessfully intercepts DNS queries can return false IP addresses, redirecting victims to malicious websites. Since DNS has no authentication, devices accept whatever response they receive. The small 16-bit transaction ID makes it possible to guess the correct ID by flooding fake responses.

**DNS surveillance**
Even when we're using HTTPS too access websites, DNS queries can still reveal which sites we're visiting. ISPs and network adminstrators can build a complete picture of browsing activity from DNS alone.

**DNS over HTTPS (DoH):**
This allows DNS queries to be encrypted inside HTTPS so they're unreadable to anyone intercepting the traffic.

## Capture 5 - ARP Traffic

### What I did

Cleared the ARP cache on my Mac to force a fresh ARP exchange, then ran ping to the Ubuntu VM while capturing on bridge100:

```
sudo arp -d 192.168.64.2
ping 192.168.64.2
```

### Filter used

```
arp
```

### What I observed

Before the first ping packet was even sent I saw a complete ARP exchange in Wireshark:

**Packet 1 - ARP Request (broadcast):**

```
12146	5336.989623	86:94:37:bc:7c:64	Broadcast	ARP	42	Who has 192.168.64.2? Tell 192.168.64.1
```

- Source MAC 32:2b:81:18:6d:76 -> Ubuntu VM (confirmed in ip a)
- Destination -> Broadcast (ff:ff:ff:ff:ff:ff) sent to every device on the network
- No ports, no TCP, no UDP - ARP operates at Layer 2 below the transport layer
- Expanding the packet in Wireshark reveals:
  Target MAC: 00:00:00:00:00:00 -> Ubuntu doesn't know Mac's MAC address yet - that's why it's broadcasting

**Packet 2 - ARP Reply (unicast):**

```
12147	5336.990885	32:2b:81:18:6d:76	86:94:37:bc:7c:64	ARP	42	192.168.64.2 is at 32:2b:81:18:6d:76
```

- Source MAC 86:94:37:bc:7c:64 -> Mac responding
- Destination -> 32:2b:81:18:6d:76 (Ubuntu VM)
  Reply is unicast - only the requester needs the answer
- OS immediately updates ARP cache with this mapping
- Ping packets begin flowing after this exchange

**After ARP resolved - ICMP ping packets begin:**

```
12148	5336.990922	192.168.64.1	192.168.64.2	ICMP	98	Echo (ping) request  id=0xf7fb, seq=0/0, ttl=64


12149	5336.992279	192.168.64.2	192.168.64.1	ICMP	98	Echo (ping) reply    id=0xf7fb, seq=0/0, ttl=64 (request in 12148)
```

This sequence demonstrates the dependency between ARP and higher level protocols:

1. ARP request -> "who has 192.168.64.1?"
2. ARP reply -> "192.168.64.1 is at 86:94:37:bc:7c:64"
3. OS updates ARP cache with Mac's MAC address
4. ICMP ping request -> now sent using Mac's real MAC
5. ICMP ping reply -> Mac responds back to Ubuntu

I have noticed that the ping could not begin until ARP resolved the MAC address. This is why ARP happens first - without the MAC address the OS has no way to deliver the packet on the local network regardless of what protocol is being used above it.

### Key Observations

- ARP happens automatically - the OS triggered it before the ping without any manual intervention
- Request is broadcast (ff:ff:ff:ff:ff:ff) -> sent to every device on the network
- Reply is unicast -> sent directly back to requester only
- Target MAC is 00:00:00:00:00:00 in the request -> confirms the OS doesn't know the MAC yet
- ARP has no authentication - any device can claim any IP
- No port numbers in ARP packets - operates at Layer 2 below TCP and UDP
- ARP cache prevents constant broadcasting - only triggered when cache is empty or expired

### Security relevance - ARP Poisoning

ARP's lack of authentication makes it vulnerable to attacks. An attacker on the same network can:

**Wait for a request:**

```
Ubuntu -> "Who has 192.168.64.1?"
Mac -> "192.168.64.1 is at 86:94:37:bc:7c:64" (real)
Attacker -> "192.168.64.1 is at aa:bb:cc:dd:ee:ff" (fake)
Ubuntu -> last reply wins -> cache poisoned
```

**Or send unsolicited gratuitous ARP:**

```
Attacker -> "192.168.64.1 is at aa:bb:cc:dd:ee:ff"
No one requested - but Ubuntu accepts it anyway
Cache updated -> all traffic redirected to attacker
```

Once the traffic is poisoned, everything will flow through the attacker who can read and forward it to the destination they want. Both sides (Mac and Ubuntu) would have no idea because everything still appears to work normally.

In Wireshark ARP poisoning would be seen as:

- Unsolicited ARP replies with no preceding request
- Two different MAC addresses claiming the same IP
- Rapid repeated ARP replies from the same source

## Key Findings

### What is encrypted and what isn't

| Protocol  | Port | Encrypted | What's visible to attacker                |
| --------- | ---- | --------- | ----------------------------------------- |
| HTTP      | 80   | No        | Everything: headers, content, credentials |
| HTTPS/TLS | 443  | Yes       | IP addresses, ports, timing, domain name  |
| DNS       | 53   | No        | Every domain name we look up              |
| ARP       | N/A  | No        | All MAC to IP mappings on network         |

### What an attacker on the same network could see

- Every HTTP request and response in full detail
- Every DNS query
- MAC addresses of all devices through ARP
- Which IP addresses we're connected to even over HTTPS
- Timing and volume of all traffic
- Software versions

### What an attacker cannot see

- Content of HTTPS traffic
- Content of SSH sessions
- Anything inside an encrypted VPN tunnel

## Limitations and Future Improvements

- Only captured traffic on a local virtual network, real world captures on a public network would show significantly more diverse traffic
- Did not capture FTP or Telnet traffic which are also unencrypted and still used in some environments
- Wireshark captures not included in repository due to file size constraints and sensitive background traffic captured during sessions. Screenshots are provided to illustrate key findings.
