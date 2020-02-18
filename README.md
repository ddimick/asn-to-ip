## ASN to IP

### What
Queries RADB whois and returns IP netblocks associated with BGP Autonomous System Numbers (ASN). Returns IPv4 results by default, adds IPv6 results as an option. Can operate either on the command line or as a basic web service, and a Docker container is available. The web service is suitable for use with pfSense and OPNsense URL aliases.

### Why
There are a number of publicly available web API interfaces to query for netblocks associated with an ASN, all of which appear to return JSON objects. That's fine and useful, but I needed a plain list of netblocks to plug into my pfSense/OPNsense aliases. Rather than rely on a third-party web API interface for source data, I instead query the RADB whois service directly, as it's the largest Routing Registry mirror site available as well as the official whois service for the IRR.

### Requirements
A standard Python 3 install for CLI mode (tested with 3.7.6). Add Flask if you want to use it in web server mode (`pip install Flask`).

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

$ curl -L "http://localhost:5000?asn=AS15169,AS109&ipv6"
8.8.8.0/24
8.15.202.0/24
8.34.208.0/21
8.34.208.0/23
8.34.208.0/24
...
```

### Docker cli usage:
```
$ docker run --rm -it ddimick/asn-to-ip:latest ./asn-to-ip.py --asn AS15169 --asn AS109 --ipv6
8.8.4.0/24
8.8.8.0/24
8.15.202.0/24
8.34.208.0/21
8.34.208.0/23
...
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
```
