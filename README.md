## ASN to IP

Queries whois and returns IP netblocks associated with BGP Autonomous System Numbers (ASN). Returns IPv4 results by default, adds IPv6 results as an option. Can operate either CLI or as a basic web service.

#### Command-Line Usage:

```
asn-to-ip.py [-h] (-a ASN | -d) [-p PORT] [-6]

optional arguments:  
  -h, --help            show this help message and exit  
  -a ASN, --asn ASN     BGP Autonomous System Number (ASN)  
  -d, --daemon          Run as a web sever  
  -p PORT, --port PORT  Port for web server (default: 5000)  
  -6, --ipv6            Also include ipv6 network blocks (default: false)  
```

### Web Server Usage:

```
usage: http://127.0.0.1:5000/asn/X or http://127.0.0.1:5000/ipv6/asn/X, where X is a BGP Autonomous System Number. Multiple ASNs may be specified by separating them with commas, like http://127.0.0.1:5000/asn/X,X,X.
```

### Example docker-compose.yaml:

```
version: "3.7"

services:
  asn-to-ip:
    container_name: asn-to-ip
    image: ddimick/asn-to-ip
    restart: always

    ports:
      - 5000:5000/tcp

    command: --daemon --port 5000
```
