## ASN to IP

Queries whois and returns IP netblocks associated with BGP Autonomous System Numbers (ASN). Returns IPv4 results by default, adds IPv6 results as an option. Can operate either CLI or as a basic web service.

#### Command-Line Usage:

```
usage: asn-to-ip.py [-h] (-a ASN | -d) [-i IP] [-p PORT] [-6] [--debug]

optional arguments:
  -h, --help            show this help message and exit
  -a ASN, --asn ASN     BGP Autonomous System Number (ASN), may use this parameter multiple times
  -d, --daemon          Run as a web sever (requires Flask)
  -i IP, --ip IP        Host IP to attach the web server (default 127.0.0.1, use 0.0.0.0 for all interfaces)
  -p PORT, --port PORT  Port for web server (default: 5000)
  -6, --ipv6            Also include ipv6 network blocks (default: false)
  --debug               Enable debug mode for Flask server
```

### Web Server Usage:

```
usage: http://127.0.0.1:5000/?asn=X, where X is one or more BGP Autonomous System Numbers separated by commas.
Returns IPv4 results by default. Add &ipv6 to also include IPv6 results, like http://127.0.0.1:5000/?asn=X&ipv6.
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

    command: --daemon --port 5000 --ip 0.0.0.0
```
